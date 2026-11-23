#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""save-my-tokens：coding agent 配置体检的取证脚本和备份回滚脚本。

只用 Python 标准库。
  scan      只读。扫 Claude Code / Codex 的配置和近 N 天会话日志，输出证据。
  backup    改动之前，把要动的路径原样存一份。
  set       改 JSON / TOML 里的一个键（文件必须已在备份里）。
  move      搬一个文件或目录（两头都必须已在备份里）。
  seal      改完后记下结果，供回滚时判断文件有没有被别人再动过。
  rollback  还原到备份时的样子，逐项校验 sha256。
  list      列出备份。
  status    对比上次 scan，列出变过但没有备份覆盖的文件。
  selftest  在系统临时目录里造假 HOME，自检 backup → set → seal → rollback。Windows 上 backup 前会自动跑。
  skills    一次改很多个 skill 的状态（整组或点名），只写 skillOverrides，skill 文件不动。
  show      从 scan 的 json 里取一组 skill 的完整名单，不用重扫。
  compare   改之前、改之后各一份 scan 的 json，对比新开会话第一次请求的实测用量。

除 scan 外，写入只发生在 HOME 和 backup 时用 --root 声明的目录里。
"""
import argparse
import copy
import datetime
import difflib
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import time
from collections import Counter, defaultdict

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

VERSION = "0.2.0"
STORE = ".save-my-tokens"
HERE = os.path.dirname(os.path.abspath(__file__))
SWITCHES = os.path.join(os.path.dirname(HERE), "references", "switches.json")

SECRET_RE = re.compile(
    r"(token|secret|passw|credential|cookie|bearer|api[_-]?key|auth|account|(^|_)key$)", re.I)
RARE_RE = re.compile(
    r"(release|rollback|roll-back|deploy|migrat|incident|hotfix|backup|restore|recover|disaster|"
    r"发版|回滚|部署|迁移|事故|应急|备份|恢复|故障)", re.I)
IGNORE_NAMES = {".DS_Store"}
# /doctor prompt-audit 背后的官方说明文件（anthropics/skills 仓库）
PROMPT_AUDIT_URL = "https://raw.githubusercontent.com/anthropics/skills/main/skills/claude-api/shared/prompt-audit.md"
MISSING = object()


def die(msg, code=2):
    print("错误：" + msg, file=sys.stderr)
    sys.exit(code)


def is_windows():
    """真 Windows，或为了在别的系统上测 Windows 分支而设了 SAVE_MY_TOKENS_TREAT_AS_WINDOWS=1。"""
    return os.name == "nt" or os.environ.get("SAVE_MY_TOKENS_TREAT_AS_WINDOWS") == "1"


def utf8_console():
    """报告里有 ⚠、→ 这类字符；Windows 中文系统默认 GBK，输出编码统一成 UTF-8，写不了的字符替换掉而不是报错。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


# 没显式给 --home 时，由环境变量 CLAUDE_CONFIG_DIR / CODEX_HOME 指定的配置目录；None 表示用默认的 ~/.claude、~/.codex
CONF = {"claude": None, "codex": None}


def claude_dir(home):
    return CONF["claude"] or os.path.join(home, ".claude")


def codex_dir(home):
    return CONF["codex"] or os.path.join(home, ".codex")


def claude_json_path(home):
    """设了 CLAUDE_CONFIG_DIR 后 .claude.json 在哪，文档快照里查不到，宁可不读。"""
    return None if CONF["claude"] else os.path.join(home, ".claude.json")


# ---------------------------------------------------------------- 基础工具

def expand(p, home):
    if p == "~":
        return home
    if p.startswith("~/") or p.startswith("~" + os.sep):
        return os.path.join(home, p[2:])
    return os.path.abspath(p)


def show(p, home):
    if p == home:
        return "~"
    if p.startswith(home + os.sep):
        return "~" + p[len(home):]
    return p


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(p, limit=None):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit) if limit else f.read()
    except OSError:
        return ""


def load_json_file(p):
    try:
        with open(p, "r", encoding="utf-8-sig") as f:  # -sig：Windows 记事本存的文件可能带 BOM
            return json.load(f), None
    except FileNotFoundError:
        return None, "absent"
    except (OSError, ValueError) as e:
        return None, str(e)


def ver_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:3])


def iso_utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def parse_now(s):
    if not s:
        return time.time()
    s = s.replace("Z", "+00:00")
    d = datetime.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.timestamp()


def iso_to_ts(s):
    try:
        return parse_now(s[:19] + "+00:00")
    except ValueError:
        return None


# ---------------------------------------------------------------- TOML（读）

def _split_key(s):
    parts = []
    for m in re.finditer(r'\s*(?:"((?:[^"\\]|\\.)*)"|\'([^\']*)\'|([A-Za-z0-9_-]+))\s*(?:\.|$)', s):
        parts.append(next(g for g in m.groups() if g is not None))
    return parts


def _mini_value(s):
    s = s.strip()
    if not s:
        return None
    if s[0] == '"':
        m = re.match(r'"((?:[^"\\]|\\.)*)"', s)
        if m:
            try:
                return json.loads(m.group(0))
            except ValueError:
                return m.group(1)
    if s[0] == "'":
        m = re.match(r"'([^']*)'", s)
        return m.group(1) if m else None
    if s[0] == "[":
        end = s.rfind("]")
        if end < 0:
            return None
        parts = re.findall(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'|[^,\s]+', s[1:end])
        return [_mini_value(x) for x in parts]
    s = s.split("#")[0].strip()
    if s in ("true", "false"):
        return s == "true"
    try:
        return int(s.replace("_", ""))
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


HEADER_RE = re.compile(r"^\s*(\[\[?)\s*([^\[\]]+?)\s*(\]\]?)\s*(#.*)?$")


def mini_toml(text):
    """没有 tomllib 时的降级解析：只认表头和单行的标量 / 标量数组。"""
    root = {}
    cur = root
    for line in text.split("\n"):
        m = HEADER_RE.match(line)
        if m:
            parts = _split_key(m.group(2))
            cur = root
            for i, k in enumerate(parts):
                last = i == len(parts) - 1
                if last and m.group(1) == "[[":
                    cur = cur.setdefault(k, [])
                    if isinstance(cur, list):
                        cur.append({})
                        cur = cur[-1]
                else:
                    nxt = cur.setdefault(k, {})
                    cur = nxt[-1] if isinstance(nxt, list) and nxt else nxt
                if not isinstance(cur, dict):
                    cur = {}
            continue
        m = re.match(r'^\s*("(?:[^"\\]|\\.)*"|[A-Za-z0-9_-]+)\s*=\s*(.*)$', line)
        if m and isinstance(cur, dict):
            key = _split_key(m.group(1))
            if key:
                cur[key[0]] = _mini_value(m.group(2))
    return root


def load_toml_file(p):
    """返回 (数据, 是否降级解析, 错误)。"""
    try:
        with open(p, "rb") as f:
            raw = f.read().decode("utf-8", "replace")
    except FileNotFoundError:
        return None, False, "absent"
    except OSError as e:
        return None, False, str(e)
    if tomllib:
        try:
            return tomllib.loads(raw), False, None
        except Exception as e:  # tomllib.TOMLDecodeError
            return None, False, str(e)
    return mini_toml(raw), True, None


# ---------------------------------------------------------------- 清单：skill / agent / MCP

def frontmatter(text):
    if not text.startswith("---"):
        return {}
    out, key = {}, None
    for ln in text.split("\n")[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if m:
            key, v = m.group(1), m.group(2).strip()
            if v in (">", "|", ">-", "|-", ">+", "|+"):
                v = ""
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            out[key] = v
        elif key and ln.strip() and ln[:1] in (" ", "\t"):
            out[key] = (out[key] + " " + ln.strip()).strip()
    return out


def list_skills(base, scope):
    items = []
    if not os.path.isdir(base):
        return items
    for d in sorted(os.listdir(base)):
        if d.startswith("."):
            continue
        p = os.path.join(base, d)
        md = os.path.join(p, "SKILL.md")
        if not os.path.isfile(md):
            continue
        fm = frontmatter(read_text(md, 20000))
        st = os.lstat(p)
        born = min(getattr(st, "st_birthtime", st.st_mtime), st.st_mtime)
        link = os.path.islink(p)
        items.append({
            "name": fm.get("name") or d, "dir": d, "path": p, "md": md, "scope": scope,
            "symlink": link, "target": os.readlink(p) if link else None,
            "desc_chars": len(fm.get("description", "")),
            "desc": fm.get("description", "")[:200],
            "manual_only": fm.get("disable-model-invocation", "").lower() == "true",
            "installed_ts": born,
        })
    return items


def list_agents(base, scope):
    items = []
    if not os.path.isdir(base):
        return items
    for f in sorted(os.listdir(base)):
        if f.startswith(".") or not f.endswith(".md"):
            continue
        p = os.path.join(base, f)
        fm = frontmatter(read_text(p, 20000))
        items.append({"name": fm.get("name") or f[:-3], "path": p, "scope": scope})
    return items


def norm_server(name):
    return re.sub(r"[^A-Za-z0-9]", "_", name or "").lower()


def mcp_brief(name, cfg, scope):
    cfg = cfg if isinstance(cfg, dict) else {}
    kind = cfg.get("type") or ("http" if cfg.get("url") else "stdio")
    return {"name": name, "scope": scope, "transport": kind,
            "alwaysLoad": bool(cfg.get("alwaysLoad")),
            "enabled": cfg.get("enabled", True) is not False,
            "enabled_tools": cfg.get("enabled_tools") if isinstance(cfg.get("enabled_tools"), list) else None,
            "disabled_tools": cfg.get("disabled_tools") if isinstance(cfg.get("disabled_tools"), list) else None}


# ---------------------------------------------------------------- 日志扫描

def new_use():
    return {"n": 0, "last": "", "cwds": Counter()}


def bump(d, key, ts, cwd=None):
    u = d.setdefault(key, new_use())
    u["n"] += 1
    if ts and ts > u["last"]:
        u["last"] = ts
    if cwd:
        u["cwds"][cwd] += 1


CWD_RE = re.compile(rb'"cwd":\s*"((?:[^"\\]|\\.)*)"')
VER_RE = re.compile(rb'"version":\s*"(\d+\.\d+\.\d+)"')
CMD_RE = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
CC_NEEDLES = (b'"Skill"', b'"Agent"', b'"Task"', b'"mcp__')


TS_RE = re.compile(rb'"timestamp":\s*"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)')
USAGE_RE = re.compile(rb'"usage":\s*\{')
U_IN_RE = re.compile(rb'"input_tokens":\s*(\d+)')
U_CC_RE = re.compile(rb'"cache_creation_input_tokens":\s*(\d+)')
U_CR_RE = re.compile(rb'"cache_read_input_tokens":\s*(\d+)')
MODEL_RE = re.compile(rb'"model":\s*"([^"]+)"')
MSGID_RE = re.compile(rb'"id":\s*"(msg_[^"]+)"')
CTX_BIN = 100000          # 请求大小按 10 万 token 一档统计
BIG_REWRITE = 100000      # 多大的历史没命中缓存算「整段重算」


def str_chars(o, depth=0):
    """一个对象里所有字符串值的总长度（最多往下三层）。用来量日志里各种附带信息的大小。"""
    if isinstance(o, str):
        return len(o)
    if depth >= 3:
        return 0
    if isinstance(o, dict):
        return sum(str_chars(v, depth + 1) for k, v in o.items() if k != "type")
    if isinstance(o, list):
        return sum(str_chars(v, depth + 1) for v in o)
    return 0


def note_head(head, line):
    """新开会话时，Claude Code 会把这次请求带了什么记进日志：规则文件、skill 清单、工具说明……
    这里只量每一块的字符数，不保留内容。"""
    if len(line) > 4000000:
        return
    try:
        rec = json.loads(line)
    except ValueError:
        return
    if not isinstance(rec, dict):
        return
    parts = head["parts"]
    if rec.get("type") == "api-request-shape":
        shape = rec.get("shape") if isinstance(rec.get("shape"), dict) else {}
        if head["tools"] is not None:
            return          # 只看第一份：后面的是会话中途工具变了之后的
        parts["system"] = str_chars(shape.get("system"))
        tools = {"builtin": {"n": 0, "chars": 0}, "mcp": {}}
        for t in shape.get("tools") or []:
            if not isinstance(t, dict):
                continue
            size = len(json.dumps(t, ensure_ascii=False))
            name = str(t.get("name") or "")
            if name.startswith("mcp__") and name.count("__") >= 2:
                srv = tools["mcp"].setdefault(name.split("__", 2)[1], {"n": 0, "chars": 0})
            else:
                srv = tools["builtin"]
            srv["n"] += 1
            srv["chars"] += size
        head["tools"] = tools
        parts["builtin_tools"] = tools["builtin"]["chars"]
        parts["mcp_tools"] = sum(v["chars"] for v in tools["mcp"].values())
        return
    a = rec.get("attachment")
    if rec.get("type") != "attachment" or not isinstance(a, dict):
        return
    kind = a.get("type")
    if kind == "skill_listing":
        if a.get("isInitial") and isinstance(a.get("content"), str):
            head["listing"] = True
            parts["skills"] = len(a["content"])
            head["skill_count"] = a.get("skillCount") or len(a.get("names") or [])
    elif kind == "instructions":
        for f in a.get("files") or []:
            if isinstance(f, dict) and isinstance(f.get("content"), str):
                head["files"].append({"path": str(f.get("path") or ""), "kind": str(f.get("type") or ""),
                                      "chars": len(f["content"])})
        parts["rules"] = sum(f["chars"] for f in head["files"])
    elif kind == "mcp_instructions_delta":
        parts["mcp_notes"] = parts.get("mcp_notes", 0) + str_chars(a.get("addedBlocks"))
    elif kind == "deferred_tools_delta":
        parts["deferred"] = parts.get("deferred", 0) + str_chars(a.get("addedLines"))
        head["deferred_n"] = head.get("deferred_n", 0) + len(a.get("addedNames") or [])
    elif kind == "agent_listing_delta":
        parts["agents"] = parts.get("agents", 0) + str_chars(a.get("addedLines"))
    elif kind == "hook_success":
        if a.get("hookEvent") == "SessionStart" and isinstance(a.get("content"), str):
            parts["hooks"] = parts.get("hooks", 0) + len(a["content"])
    elif kind != "prompt_snapshot":
        parts["other"] = parts.get("other", 0) + str_chars(a)


def open_log(path):
    """打开一个会话日志。Codex 会把旧会话压成 .jsonl.zst：Python 3.14+ 用标准库解，
    否则试系统里的 zstd 命令，都没有就返回 None（调用方会记一笔「读不了」）。"""
    if not path.endswith(".zst"):
        return open(path, "rb")
    try:
        from compression import zstd
        return zstd.open(path, "rb")
    except ImportError:
        pass
    exe = shutil.which("zstd")
    if exe:
        import subprocess
        return subprocess.Popen([exe, "-dcq", path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    return None


def note_first_ts(r, line, cutoff_iso):
    """记下每个文件第一条带时间的记录，用来判断日志往前覆盖到哪天。"""
    m = TS_RE.search(line)
    if not m:
        return False
    t = m.group(1).decode()
    if t < cutoff_iso:
        r["older_evidence"] = True
    elif not r["earliest"] or t < r["earliest"]:
        r["earliest"] = t
    return True


def iter_jsonl(root, cutoff):
    """产出 (路径, mtime, 大小, 是否在时间窗内)。窗外的文件只用来判断日志覆盖了多久。"""
    for dp, _dn, fn in os.walk(root):
        for f in fn:
            if not (f.endswith(".jsonl") or f.endswith(".jsonl.zst")):
                continue
            p = os.path.join(dp, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            yield p, st.st_mtime, st.st_size, st.st_mtime >= cutoff


def scan_claude_logs(home, cutoff):
    root = os.path.join(claude_dir(home), "projects")
    cutoff_iso = iso_utc(cutoff)
    r = {"present": os.path.isdir(root), "files": 0, "bytes": 0, "older_evidence": False, "earliest": "",
         "unreadable": 0, "version": None, "cwds": Counter(), "skill_model": {}, "skill_user": {},
         "agents": {}, "mcp": {}, "listings": [],
         # 下面几样都是从日志里的用量数字直接数出来的
         "starts": [],                                   # 每个新会话的第一次请求
         "req": {"main": {}, "sub": {}},                 # 请求数和输入 token，按模型
         "bins": Counter(), "bin_tokens": Counter(),     # 主会话请求按大小分档
         "peaks": [],                                    # 每个会话文件里最大的一次请求
         "rewrites": {},                                 # 没命中缓存、整段重算的请求
         "agent_model": Counter()}                       # 派子代理时指定了什么模型
    if not r["present"]:
        return r
    seen = set()
    seen_msg = set()
    for p, mtime, size, inwin in iter_jsonl(root, cutoff):
        if not inwin:
            r["older_evidence"] = True
            continue
        is_sub = (os.sep + "subagents" + os.sep) in p
        file_cwd = None
        head = None if is_sub else {"parts": {}, "files": [], "tools": None, "listing": False, "lines": 0}
        prev_ts, prev_model, peak, copied, file_msgs = None, None, 0, False, set()
        try:
            fh = open_log(p)
        except OSError:
            fh = None
        if fh is None:
            r["unreadable"] += 1
            continue
        r["files"] += 1
        r["bytes"] += size
        got_ts = False
        with fh:
            for line in fh:
                if not got_ts and b'"timestamp"' in line:
                    got_ts = note_first_ts(r, line, cutoff_iso)
                if file_cwd is None and b'"cwd"' in line:
                    m = CWD_RE.search(line)
                    if m:
                        try:
                            file_cwd = json.loads(b'"' + m.group(1) + b'"')
                        except ValueError:
                            file_cwd = ""
                        if file_cwd and not is_sub:
                            r["cwds"][file_cwd] += 1
                        v = VER_RE.search(line)
                        if v:
                            vs = v.group(1).decode()
                            if ver_tuple(vs) > ver_tuple(r["version"]):
                                r["version"] = vs
                if head is not None:
                    head["lines"] += 1
                    if head["lines"] > 400:
                        head = None
                    elif b'"attachment"' in line or b'"api-request-shape"' in line:
                        note_head(head, line)
                # 每次请求的用量：输入 = 新输入 + 写入缓存 + 读缓存，就是这次请求带的全部上下文
                if b'"usage"' in line and b'"assistant"' in line:
                    um = USAGE_RE.search(line)
                    mi = MSGID_RE.search(line)
                    mid = mi.group(1) if mi else None
                    if um and mid and mid in file_msgs:
                        pass                             # 同一次回复被拆成几条记录，用量是同一份
                    elif um and mid and mid in seen_msg:
                        copied = True                    # 续接会话时抄过来的旧记录，数过了
                    elif um:
                        if mid:
                            seen_msg.add(mid)
                            file_msgs.add(mid)
                        at = um.end()
                        a, b_, c_ = U_IN_RE.search(line, at), U_CC_RE.search(line, at), U_CR_RE.search(line, at)
                        cc, cr = (int(b_.group(1)) if b_ else 0), (int(c_.group(1)) if c_ else 0)
                        ctx = (int(a.group(1)) if a else 0) + cc + cr
                        tss = TS_RE.findall(line)
                        uts = tss[-1].decode() if tss else ""
                        mm = MODEL_RE.search(line)
                        model = mm.group(1).decode("utf-8", "replace") if mm else "?"
                        side = is_sub or b'"isSidechain":true' in line or b'"isSidechain": true' in line
                        inwin_req = not uts or uts >= cutoff_iso
                        if ctx and model != "<synthetic>":
                            if inwin_req:
                                slot = r["req"]["sub" if side else "main"].setdefault(model, {"n": 0, "tokens": 0})
                                slot["n"] += 1
                                slot["tokens"] += ctx
                            if not side:
                                if inwin_req:
                                    b = min(ctx // CTX_BIN, 10)
                                    r["bins"][b] += 1
                                    r["bin_tokens"][b] += ctx
                                    peak = max(peak, ctx)
                                    if prev_ts is None:
                                        if head is not None and head["listing"] and not copied:
                                            r["starts"].append({
                                                "ts": uts, "cwd": file_cwd or "", "tokens": ctx, "model": model,
                                                "parts": head["parts"], "files": head["files"], "tools": head["tools"],
                                                "skill_count": head.get("skill_count"), "deferred_n": head.get("deferred_n")})
                                    elif ctx >= BIG_REWRITE and cr < ctx * 0.1:
                                        gap = iso_to_ts(uts) - iso_to_ts(prev_ts) if uts and prev_ts else 0
                                        why = ("换了模型" if model != prev_model else "隔了 1 小时以上" if gap > 3600
                                               else "隔了 5 分钟到 1 小时" if gap > 300 else "其他原因")
                                        w = r["rewrites"].setdefault(why, {"n": 0, "tokens": 0})
                                        w["n"] += 1
                                        w["tokens"] += ctx
                                prev_ts, prev_model = uts or prev_ts or "", model
                                head = None
                # Claude Code 新开会话时会把发给模型的 skill 清单记进日志：这是实测值，不是我们算的
                if not is_sub and b'"skill_listing"' in line and len(line) < 400000:
                    try:
                        att = json.loads(line)
                    except ValueError:
                        att = None
                    a = att.get("attachment") if isinstance(att, dict) else None
                    if (isinstance(a, dict) and a.get("type") == "skill_listing" and a.get("isInitial")
                            and isinstance(a.get("content"), str)):
                        lts = (att.get("timestamp") or "")[:19]
                        if lts >= cutoff_iso:
                            names = a.get("names") if isinstance(a.get("names"), list) else []
                            r["listings"].append({"ts": lts, "count": a.get("skillCount") or len(names),
                                                  "chars": len(a["content"]), "cwd": att.get("cwd") or file_cwd or ""})
                    continue
                is_tool = b'"tool_use"' in line and any(n in line for n in CC_NEEDLES)
                is_cmd = (not is_tool) and b"<command-name>" in line
                if not (is_tool or is_cmd):
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                ts = (rec.get("timestamp") or "")[:19]
                if ts and ts < cutoff_iso:
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content")
                cwd = rec.get("cwd") or file_cwd
                if rec.get("type") == "assistant" and isinstance(content, list):
                    for b in content:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        bid = b.get("id")
                        if bid:
                            if bid in seen:
                                continue
                            seen.add(bid)
                        name = b.get("name") or ""
                        inp = b.get("input") if isinstance(b.get("input"), dict) else {}
                        if name == "Skill" and inp.get("skill"):
                            bump(r["skill_model"], str(inp["skill"]), ts, cwd)
                        elif name in ("Agent", "Task"):
                            r["agent_model"][str(inp.get("model") or "")] += 1
                            if inp.get("subagent_type"):
                                bump(r["agents"], str(inp["subagent_type"]), ts, cwd)
                        elif name.startswith("mcp__"):
                            parts = name.split("__", 2)
                            if len(parts) == 3:
                                u = r["mcp"].setdefault(parts[1], {"n": 0, "last": "", "tools": Counter()})
                                u["n"] += 1
                                u["tools"][parts[2]] += 1
                                if ts > u["last"]:
                                    u["last"] = ts
                elif rec.get("type") == "user":
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        text = "\n".join(b.get("text", "") for b in content
                                         if isinstance(b, dict) and b.get("type") == "text")
                    else:
                        text = ""
                    names = CMD_RE.findall(text)
                    if not names:
                        continue
                    uid = rec.get("uuid")
                    if uid:
                        if uid in seen:
                            continue
                        seen.add(uid)
                    for n in names:
                        bump(r["skill_user"], n, ts, cwd)
        if peak:
            r["peaks"].append(peak)
    return r


CODEX_MCP_RE = re.compile(r"tools\.mcp__([A-Za-z0-9_]+?)__([A-Za-z0-9_]+)")
CODEX_SKILL_RE = re.compile(r"(?:(\.claude|\.codex|\.agents)/)?skills/([A-Za-z0-9_.-]+)/SKILL\.md")
CODEX_VER_RE = re.compile(rb'"cli_version":\s*"(\d+\.\d+\.\d+)"')


def scan_codex_logs(home, cutoff):
    base = codex_dir(home)
    cutoff_iso = iso_utc(cutoff)
    r = {"present": False, "files": 0, "bytes": 0, "older_evidence": False, "earliest": "", "unreadable": 0,
         "version": None, "cwds": Counter(), "mcp": {}, "skill_reads": {}}
    seen = set()
    for sub in ("sessions", "archived_sessions"):
        root = os.path.join(base, sub)
        if not os.path.isdir(root):
            continue
        r["present"] = True
        for p, mtime, size, inwin in iter_jsonl(root, cutoff):
            if not inwin:
                r["older_evidence"] = True
                continue
            file_cwd = None
            try:
                fh = open_log(p)
            except OSError:
                fh = None
            if fh is None:
                r["unreadable"] += 1
                continue
            r["files"] += 1
            r["bytes"] += size
            got_ts = False
            with fh:
                for line in fh:
                    if not got_ts and b'"timestamp"' in line:
                        got_ts = note_first_ts(r, line, cutoff_iso)
                    if file_cwd is None and b'"session_meta"' in line:
                        m = CWD_RE.search(line)
                        if m:
                            try:
                                file_cwd = json.loads(b'"' + m.group(1) + b'"')
                            except ValueError:
                                file_cwd = ""
                            if file_cwd:
                                r["cwds"][file_cwd] += 1
                        v = CODEX_VER_RE.search(line)
                        if v and ver_tuple(v.group(1).decode()) > ver_tuple(r["version"]):
                            r["version"] = v.group(1).decode()
                        continue
                    if b'"custom_tool_call"' not in line and b'"function_call"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    pl = rec.get("payload")
                    if not isinstance(pl, dict) or pl.get("type") not in ("custom_tool_call", "function_call"):
                        continue
                    ts = (rec.get("timestamp") or "")[:19]
                    if ts and ts < cutoff_iso:
                        continue
                    cid = pl.get("call_id") or pl.get("id")
                    if cid:
                        if cid in seen:
                            continue
                        seen.add(cid)
                    text = pl.get("input") if pl.get("type") == "custom_tool_call" else pl.get("arguments")
                    text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
                    calls = [(m.group(1), m.group(2)) for m in CODEX_MCP_RE.finditer(text)]
                    ns = pl.get("namespace") or ""
                    if pl.get("type") == "function_call" and ns.startswith("mcp__"):
                        calls.append((ns[5:], pl.get("name") or "?"))
                    for server, tool in calls:
                        u = r["mcp"].setdefault(server, {"n": 0, "last": "", "tools": Counter()})
                        u["n"] += 1
                        u["tools"][tool] += 1
                        if ts > u["last"]:
                            u["last"] = ts
                    for name in {m.group(2) for m in CODEX_SKILL_RE.finditer(text)}:
                        bump(r["skill_reads"], name, ts, file_cwd)
    return r


# ---------------------------------------------------------------- 规则文件与重复

CLAUDE_NAMES = ("CLAUDE.md", "CLAUDE.local.md", os.path.join(".claude", "CLAUDE.md"))
IMPORT_RE = re.compile(r"(?:^|(?<=[\s(（:：]))@((?:\\ |[^\s`\"'()（）,，。;；])+)")


def ancestors(cwd, home):
    out, d = [], cwd
    for _ in range(14):
        out.append(d)
        parent = os.path.dirname(d)
        if d == home or parent == d:
            break
        d = parent
    return out


def git_root(cwd, home):
    for d in ancestors(cwd, home):
        if os.path.exists(os.path.join(d, ".git")):
            return d
    return cwd


def broken_links(base):
    """skills 目录下指向不存在位置的软链：skill 已经用不了，入口还留着。"""
    out = []
    if not os.path.isdir(base):
        return out
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.islink(p) and not os.path.exists(p):
            out.append({"path": p, "target": os.readlink(p)})
    return out


def missing_imports(path, home):
    """规则文件里写了 @路径、但那个文件不存在的。只认带扩展名的，避免把 @某人、@scope/包名 算进来。"""
    out = []
    base = os.path.dirname(path)
    for m in IMPORT_RE.finditer(strip_code(read_text(path))):
        raw = m.group(1).replace("\\ ", " ")
        cands = (raw, raw.rstrip(".,;:!?)]}"))
        if not re.search(r"\.[A-Za-z0-9]{1,5}$", cands[1]) or "@" in raw or "://" in raw:
            continue
        ok = False
        for cand in cands:
            p = expand(cand, home) if cand.startswith("~") else os.path.normpath(os.path.join(base, cand))
            if os.path.exists(p):
                ok = True
                break
        if not ok and cands[1] not in out:
            out.append(cands[1])
    return out


def strip_code(text):
    out, fence = [], False
    for ln in text.split("\n"):
        s = ln.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence
            out.append("")
            continue
        out.append("" if fence else re.sub(r"`[^`]*`", " ", ln))
    return "\n".join(out)


def imports_of(path, home, depth=0, seen=None):
    seen = seen if seen is not None else set()
    found = []
    if depth >= 4:
        return found
    base = os.path.dirname(path)
    for m in IMPORT_RE.finditer(strip_code(read_text(path))):
        raw = m.group(1).replace("\\ ", " ")
        for cand in (raw, raw.rstrip(".")):
            p = expand(cand, home) if cand.startswith("~") else os.path.normpath(os.path.join(base, cand))
            if os.path.isfile(p):
                rp = os.path.realpath(p)
                if rp not in seen:
                    seen.add(rp)
                    found.append(p)
                    found.extend(imports_of(p, home, depth + 1, seen))
                break
    return found


def rules_in(d, rd=None):
    out = []
    rd = rd or os.path.join(d, ".claude", "rules")
    if os.path.isdir(rd):
        for dp, _dn, fn in os.walk(rd):
            for f in sorted(fn):
                if f.endswith(".md"):
                    out.append(os.path.join(dp, f))
    return out


def claude_global(home):
    files = []
    g = os.path.join(claude_dir(home), "CLAUDE.md")
    if os.path.isfile(g):
        files.append(g)
    files.extend(rules_in(home, os.path.join(claude_dir(home), "rules")))
    for f in list(files):
        files.extend(imports_of(f, home))
    return files


def claude_chain(cwd, home, excludes):
    files, has_claude = [], False
    for d in ancestors(cwd, home):
        for n in CLAUDE_NAMES:
            if d == home and n.startswith(".claude"):
                continue  # 用户级文件单算
            p = os.path.join(d, n)
            if os.path.isfile(p):
                files.append(p)
                has_claude = True
        if d != home:
            files.extend(rules_in(d))
    if not has_claude:
        for d in ancestors(cwd, home):
            p = os.path.join(d, "AGENTS.md")
            if os.path.isfile(p):
                files.append(p)
    # 先按 claudeMdExcludes 排除，再展开 @import：被排除的文件，它 import 的内容也不会加载
    files = [f for f in files if not any(fnmatch.fnmatch(f, pat) for pat in excludes)]
    for f in list(files):
        files.extend(imports_of(f, home))
    return files


def claude_excluded(cwd, home, excludes):
    """这个目录往上，哪些规则文件被 settings.json 的 claudeMdExcludes 排除了。"""
    out = []
    for d in ancestors(cwd, home):
        for n in CLAUDE_NAMES + ("AGENTS.md",):
            p = os.path.join(d, n)
            if os.path.isfile(p) and any(fnmatch.fnmatch(p, pat) for pat in excludes):
                out.append(p)
    return out


def codex_chain(cwd, home):
    root = git_root(cwd, home)
    files = []
    for d in ancestors(cwd, home):
        p = os.path.join(d, "AGENTS.md")
        if os.path.isfile(p):
            files.append(p)
        if d == root:
            break
    return files


def norm_rule(s):
    s = re.sub(r"^\s*([-*+>]|\d+[.)、])\s+", "", s)
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE).lower()


def weight(s):
    return sum(2 if ord(c) > 0x2E80 else 1 for c in s)


def units_of(path):
    out, fence = [], False
    for i, ln in enumerate(read_text(path).split("\n"), 1):
        s = ln.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence
            continue
        if fence or not s or s.startswith("#"):
            continue
        if re.fullmatch(r"@\S+", s) or re.fullmatch(r"[|\s:-]+", s):
            continue
        n = norm_rule(s)
        if weight(n) < 16:
            continue
        out.append((i, s, n))
        if len(out) >= 600:
            break
    return out


def compare_units(ua, ub):
    exact, near = [], []
    index = {}
    for b in ub:
        index.setdefault(b[2], b)
    for a in ua:
        if a[2] in index:
            exact.append((a, index[a[2]]))
            continue
        best = None
        for b in ub:
            la, lb = len(a[2]), len(b[2])
            if min(la, lb) / max(la, lb) < 0.6:
                continue
            sm = difflib.SequenceMatcher(None, a[2], b[2], autojunk=False)
            if sm.real_quick_ratio() < 0.75 or sm.quick_ratio() < 0.75:
                continue
            ratio = sm.ratio()
            if ratio >= 0.75 and (best is None or ratio > best[0]):
                best = (ratio, b)
        if best:
            near.append((a, best[1], round(best[0], 2)))
    return exact, near


# ---------------------------------------------------------------- scan 主流程

def clip(s, n=110):
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"


def ref_patterns(name):
    e = re.escape(name)
    return re.compile(r"(?:(?<![\w/-])/%s(?![\w-])|`%s`|skills/%s(?![\w-])|「%s」|%s\s*skill)" % (e, e, e, e, e))


def quantile(xs, q):
    """xs 已排序。取分位数，不插值。"""
    return xs[min(len(xs) - 1, int(len(xs) * q))] if xs else 0


HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")


def sections_of(path):
    """按一、二、三级标题把规则文件切成几节，量每节多少字符。代码块里的 # 不算标题。"""
    out, cur, fence = [], None, False
    for i, ln in enumerate(read_text(path).split("\n"), 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else HEADING_RE.match(ln)
        if m:
            cur = {"title": clip(m.group(2), 40), "level": len(m.group(1)), "line": i, "chars": 0}
            out.append(cur)
        if cur is not None:
            cur["chars"] += len(ln) + 1
    return out


SKILL_GROUPS = (
    ("A", "一次没用，也找不到留着的理由", "可以关掉，或只留手动"),
    ("B", "一次没用，但有理由先留着", "逐个看 ⚠ 再定，默认保留"),
    ("C", "只有你手敲过，模型没主动调过", "适合改成「只能手动调」"),
    ("D", "模型只主动调过一两次", "名字说得清的可以「只留名字」"),
    ("E", "在用", "不动"),
)


def skill_group(s):
    if s["total"] == 0:
        return "B" if s["flags"] else "A"
    if s["model_calls"] == 0 and s["codex_reads"] == 0:
        return "C"
    if s["model_calls"] <= 2 and s["codex_reads"] == 0:
        return "D"
    return "E"


def startup_summary(starts, now):
    """新开会话第一次请求的实测。只留统计和最近一次的明细，不把每个会话都写进 json。"""
    if not starts:
        return None
    starts = sorted(starts, key=lambda s: s["ts"])
    toks = sorted(s["tokens"] for s in starts)
    week = iso_utc(now - 7 * 86400)
    recent = sorted(s["tokens"] for s in starts if s["ts"] >= week)
    by_cwd = defaultdict(list)
    for s in starts:
        by_cwd[s["cwd"]].append(s)
    rows = []
    for cwd, ss in sorted(by_cwd.items(), key=lambda kv: -len(kv[1]))[:6]:
        t = sorted(x["tokens"] for x in ss)
        rows.append({"cwd": cwd, "n": len(ss), "median": quantile(t, 0.5), "latest": ss[-1]["tokens"],
                     "latest_ts": ss[-1]["ts"], "latest_parts": ss[-1]["parts"]})
    # 拿哪一次来看明细：最近 7 天新开会话最多的那个目录里最近的一次，最能代表用户平时的开局
    pool = [s for s in starts if s["ts"] >= week] or starts
    busiest = Counter(s["cwd"] for s in pool).most_common(1)[0][0]
    focus = [s for s in pool if s["cwd"] == busiest][-1]
    return {"n": len(starts), "median": quantile(toks, 0.5), "p25": quantile(toks, 0.25), "p75": quantile(toks, 0.75),
            "p90": quantile(toks, 0.9), "min": toks[0], "max": toks[-1],
            "recent7": {"n": len(recent), "median": quantile(recent, 0.5)} if recent else None,
            "latest": starts[-1], "focus": focus, "by_cwd": rows,
            "has_shape": any(s.get("tools") is not None for s in starts)}


def context_summary(cl):
    bins = cl.get("bins") or Counter()
    n = sum(bins.values())
    if not n:
        return None
    tok = cl["bin_tokens"]
    total = sum(tok.values())
    over = {}
    for label, b0 in (("200k", 2), ("400k", 4), ("500k", 5)):
        over[label] = {"requests": sum(v for b, v in bins.items() if b >= b0),
                       "tokens": sum(v for b, v in tok.items() if b >= b0)}
    peaks = sorted(cl.get("peaks") or [])
    rw = cl.get("rewrites") or {}
    return {"requests": n, "tokens": total, "bins": {str(b): bins[b] for b in sorted(bins)},
            "bin_tokens": {str(b): tok[b] for b in sorted(tok)}, "over": over,
            "sessions": len(peaks), "peak_median": quantile(peaks, 0.5), "peak_p90": quantile(peaks, 0.9),
            "peak_max": peaks[-1] if peaks else 0,
            "sessions_over": {"400k": sum(1 for p in peaks if p >= 400000), "500k": sum(1 for p in peaks if p >= 500000)},
            "rewrites": {"n": sum(v["n"] for v in rw.values()), "tokens": sum(v["tokens"] for v in rw.values()), "by": rw}}


def auto_memory(c_dir, settings, env, cwds):
    """Claude Code 自带的自动记忆：每个项目一份 MEMORY.md，开头 200 行或 25KB 每个会话都加载。"""
    files = []
    by_slug = {re.sub(r"[^A-Za-z0-9]", "-", c): c for c in cwds}      # 目录名是路径换掉符号得来的，对得上的还原成路径
    for p in glob.glob(os.path.join(c_dir, "projects", "*", "memory", "MEMORY.md")):
        try:
            size = os.path.getsize(p)
        except OSError:
            continue
        lines = read_text(p).count("\n") + 1
        slug = os.path.basename(os.path.dirname(os.path.dirname(p)))
        files.append({"path": p, "project": by_slug.get(slug), "bytes": size, "lines": lines,
                      "over_limit": lines > 200 or size > 25000})
    files.sort(key=lambda f: -f["bytes"])
    off = settings.get("autoMemoryEnabled") is False or str(env.get("CLAUDE_CODE_DISABLE_AUTO_MEMORY")) == "1"
    return {"enabled": not off, "count": len(files), "files": files[:8]}


def do_scan(args, home):
    now = parse_now(args.now)
    cutoff = now - args.days * 86400
    ev = {"tool": "save-my-tokens", "version": VERSION, "home": home, "days": args.days,
          "now": iso_utc(now), "window_start": iso_utc(cutoff), "files": {}}

    def track(p):
        if p and os.path.isfile(p):
            try:
                ev["files"][p] = sha256_file(p)
            except OSError:
                pass

    c_dir, x_dir = claude_dir(home), codex_dir(home)
    has_claude, has_codex = os.path.isdir(c_dir), os.path.isdir(x_dir)
    cl = scan_claude_logs(home, cutoff) if has_claude else {"present": False, "cwds": Counter(), "files": 0}
    cx = scan_codex_logs(home, cutoff) if has_codex else {"present": False, "cwds": Counter(), "files": 0}

    # ---- Claude Code 配置
    settings_p = os.path.join(c_dir, "settings.json")
    settings, s_err = load_json_file(settings_p)
    settings = settings if isinstance(settings, dict) else {}
    local, _ = load_json_file(os.path.join(c_dir, "settings.local.json"))
    local = local if isinstance(local, dict) else {}
    env = settings.get("env") if isinstance(settings.get("env"), dict) else {}
    track(settings_p)
    track(os.path.join(c_dir, "settings.local.json"))
    overrides = {}
    for src in (settings, local):
        if isinstance(src.get("skillOverrides"), dict):
            overrides.update(src["skillOverrides"])
    cc_version = args.cc_version or cl.get("version")

    claude = {"present": has_claude, "version": cc_version,
              "version_source": "参数" if args.cc_version else ("日志" if cc_version else None),
              "settings_error": None if s_err in (None, "absent") else s_err,
              "log_files": cl.get("files", 0), "log_bytes": cl.get("bytes", 0)}

    # ---- 项目：取近 N 天实际开过会话的目录
    cwd_all = Counter()
    for c, n in cl["cwds"].items():
        cwd_all[c] += n
    for c, n in cx["cwds"].items():
        cwd_all[c] += n
    excludes = [expand(x, home) for x in settings.get("claudeMdExcludes", []) if isinstance(x, str)]
    # 同一个仓库常有多个 worktree：规则文件内容完全相同的并成一组；
    # 目录名相同但内容有出入的最多留 3 个，且不占「前几个项目」的名额。
    projects, seen_sig = [], {}
    explicit = [os.path.realpath(expand(p, home)) for p in (args.project or [])]
    cands = explicit + [c for c, _ in cwd_all.most_common(400) if c not in explicit]
    names, per_name = set(), Counter()
    for cwd in cands:
        if cwd == home or not os.path.isdir(cwd):
            continue
        cfiles = claude_chain(cwd, home, excludes) if has_claude else []
        xfiles = codex_chain(cwd, home) if has_codex else []
        if not cfiles and not xfiles and not os.path.isdir(os.path.join(cwd, ".claude")):
            continue
        sig = tuple(sorted(sha256_file(f) for f in set(cfiles + xfiles)))
        if sig in seen_sig and sig:
            seen_sig[sig]["same_as"].append(cwd)
            seen_sig[sig]["sessions"] += cwd_all.get(cwd, 0)
            continue
        name = os.path.basename(cwd)
        if cwd not in explicit:
            if per_name[name] >= 3 or (name not in names and len(names) >= args.max_projects):
                continue
            names.add(name)
            per_name[name] += 1
        proj = {"cwd": cwd, "sessions": cwd_all.get(cwd, 0), "claude_files": cfiles,
                "codex_files": xfiles, "same_as": [],
                "excluded": claude_excluded(cwd, home, excludes) if has_claude and excludes else []}
        seen_sig[sig] = proj
        projects.append(proj)
    ev["projects"] = projects

    # ---- skill
    skills = list_skills(os.path.join(c_dir, "skills"), "user") if has_claude else []
    user_md = {}
    for s in skills:
        s["also_in"] = []
        user_md[s["dir"]] = sha256_file(s["md"])
    seen_ps = {}
    for pr in projects:
        if not has_claude:
            break
        found = []
        for cwd in [pr["cwd"]] + pr["same_as"][:12]:   # 规则文件相同的 worktree 也看一眼
            found += list_skills(os.path.join(cwd, ".claude", "skills"), "project:" + cwd)
        for s in found:
            h = sha256_file(s["md"])
            if (s["dir"], h) in seen_ps:      # 另一个 worktree 里一模一样的同一个 skill
                seen_ps[(s["dir"], h)]["also_in"].append(s["scope"].split(":", 1)[1])
                continue
            s["also_in"] = []
            if s["dir"] in user_md:           # 用户级已经有一个同名的
                s["twin"] = "内容相同" if user_md[s["dir"]] == h else "内容不同"
            seen_ps[(s["dir"], h)] = s
            skills.append(s)
    # ~/.claude.json 只读其中三样：skillUsage、mcpServers、projects[*].mcpServers
    cj = claude_json_path(home)
    usage_cc, _ = load_json_file(cj) if has_claude and cj else (None, None)
    usage_cc = usage_cc if isinstance(usage_cc, dict) else {}
    skill_usage = {}
    for k, v in (usage_cc.get("skillUsage") or {}).items():
        if isinstance(v, dict) and v.get("lastUsedAt"):
            n = k.rsplit(":", 1)[-1]
            skill_usage[n] = max(skill_usage.get(n, 0), v["lastUsedAt"] / 1000.0)

    def by_last_seg(d):
        out = {}
        for k, u in d.items():
            n = k.rsplit(":", 1)[-1]
            o = out.setdefault(n, new_use())
            o["n"] += u["n"]
            o["last"] = max(o["last"], u["last"])
            o["cwds"].update(u["cwds"])
        return out

    sm, su = by_last_seg(cl.get("skill_model", {})), by_last_seg(cl.get("skill_user", {}))
    sr = cx.get("skill_reads", {})

    # 引用语料：规则文件、其他 skill、subagent 定义、hooks
    agents = (list_agents(os.path.join(c_dir, "agents"), "user") if has_claude else [])
    for pr in projects:
        agents += list_agents(os.path.join(pr["cwd"], ".claude", "agents"), "project:" + pr["cwd"])
    global_claude = claude_global(home) if has_claude else []
    global_codex = [p for p in [os.path.join(x_dir, "AGENTS.md")] if os.path.isfile(p)]
    corpus = []
    for f in set(global_claude + global_codex + [f for pr in projects for f in pr["claude_files"] + pr["codex_files"]]):
        corpus.append((f, read_text(f)))
        track(f)
    for a in agents:
        corpus.append((a["path"], read_text(a["path"])))
        track(a["path"])
    if settings.get("hooks"):
        corpus.append((settings_p + "（hooks）", json.dumps(settings["hooks"], ensure_ascii=False)))
    skill_texts = {s["path"]: (s["dir"], read_text(s["md"])) for s in skills}

    known = set()
    for s in skills:
        track(s["md"])
        names = {s["name"], s["dir"]}
        known |= names
        state = overrides.get(s["name"], overrides.get(s["dir"], "on"))
        if state == "on" and s["manual_only"]:
            state = "user-invocable-only"
        s["state"] = state
        s["model_calls"] = sum(sm.get(n, new_use())["n"] for n in names)
        s["user_calls"] = sum(su.get(n, new_use())["n"] for n in names)
        s["codex_reads"] = sum(sr.get(n, new_use())["n"] for n in names)
        s["last"] = max([sm.get(n, new_use())["last"] for n in names] +
                        [su.get(n, new_use())["last"] for n in names] +
                        [sr.get(n, new_use())["last"] for n in names])
        cw = Counter()
        for n in names:
            cw.update(sm.get(n, new_use())["cwds"])
            cw.update(su.get(n, new_use())["cwds"])
        s["cwds"] = dict(cw.most_common(3))
        s["total"] = s["model_calls"] + s["user_calls"] + s["codex_reads"]
        flags = []
        if s["total"] == 0:
            pat = ref_patterns(s["dir"])
            refs = [f for f, t in corpus if pat.search(t)]
            refs += [p for p, (d, t) in skill_texts.items() if d != s["dir"] and pat.search(t)]
            if refs:
                s["referenced_by"] = sorted(set(refs))[:6]
                flags.append("被点名引用")
            if RARE_RE.search(s["dir"] + " " + s["desc"]):
                flags.append("像低频保命项")
            age = (now - s["installed_ts"]) / 86400
            lu = max(skill_usage.get(n, 0) for n in names)
            if age < args.days and not (lu and lu < s["installed_ts"]):
                # skillUsage 里有更早的使用记录时，说明只是文件被重建过，不算新装
                flags.append("装了才 %d 天" % max(age, 0))
            if lu and lu >= cutoff:
                flags.append("skillUsage 记着 %s 用过，日志里没数到" % iso_utc(lu)[:10])
            elif lu:
                s["last_ever"] = iso_utc(lu)[:10]
        s["flags"] = flags
    claude["skills"] = skills
    listings = sorted(cl.get("listings") or [], key=lambda d: d["ts"])
    claude["listing"] = ({"latest": listings[-1], "samples": len(listings),
                          "min": min(d["count"] for d in listings), "max": max(d["count"] for d in listings)}
                         if listings else None)
    claude["broken_skill_links"] = broken_links(os.path.join(c_dir, "skills")) if has_claude else []
    claude["other_skill_calls"] = {k: v["n"] for k, v in sm.items() if k not in known}
    claude["skill_usage_source"] = bool(skill_usage)
    # 用户级、模型看得见的 skill 按用法分成几组：几百个的时候不用一个个过
    groups_sum = {g: {"n": 0, "desc_chars": 0} for g, _t, _a in SKILL_GROUPS}
    for s in skills:
        if s["scope"] == "user" and s["state"] in ("on", "name-only"):
            s["group"] = skill_group(s)
            groups_sum[s["group"]]["n"] += 1
            groups_sum[s["group"]]["desc_chars"] += s["desc_chars"] if s["state"] == "on" else 0
    claude["skill_groups"] = groups_sum

    # ---- 实测：开局带了多少、会话长到多大、哪个模型在跑
    claude["startup"] = startup_summary(cl.get("starts") or [], now)
    claude["context"] = context_summary(cl)
    claude["requests_by_model"] = cl.get("req") or {"main": {}, "sub": {}}
    am = cl.get("agent_model") or Counter()
    claude["agent_calls"] = {"total": sum(am.values()), "no_model": am.get("", 0),
                             "by_model": {k: v for k, v in am.most_common() if k}}
    claude["auto_memory"] = auto_memory(c_dir, settings, env, list(cl["cwds"])) if has_claude else None
    ms = settings.get("modelSettings") if isinstance(settings.get("modelSettings"), dict) else {}
    claude["compact_window"] = {
        "env": env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW"), "settings": settings.get("autoCompactWindow"),
        "per_model": {k: v.get("autoCompactWindow") for k, v in ms.items()
                      if isinstance(v, dict) and v.get("autoCompactWindow") is not None},
        "disabled": settings.get("autoCompactEnabled") is False or str(env.get("DISABLE_AUTO_COMPACT")) == "1"}

    # ---- subagent
    known_agents = set()
    for a in agents:
        known_agents.add(a["name"])
        u = cl.get("agents", {}).get(a["name"], new_use())
        a["calls"], a["last"] = u["n"], u["last"]
    claude["agents"] = agents
    claude["builtin_agent_calls"] = {k: v["n"] for k, v in cl.get("agents", {}).items() if k not in known_agents}

    # ---- MCP（Claude Code）
    mcps = []
    for name, cfg in (usage_cc.get("mcpServers") or {}).items():
        mcps.append(mcp_brief(name, cfg, "user（~/.claude.json）"))
    for pr in projects:
        pj = (usage_cc.get("projects") or {}).get(pr["cwd"]) or {}
        for name, cfg in (pj.get("mcpServers") or {}).items():
            mcps.append(mcp_brief(name, cfg, "local:" + pr["cwd"]))
        mj, _ = load_json_file(os.path.join(pr["cwd"], ".mcp.json"))
        for name, cfg in ((mj or {}).get("mcpServers") or {}).items():
            mcps.append(mcp_brief(name, cfg, "project:" + pr["cwd"]))
    used = {norm_server(k): v for k, v in cl.get("mcp", {}).items()}
    matched = set()
    for m in mcps:
        u = used.get(norm_server(m["name"]))
        matched.add(norm_server(m["name"]))
        m["calls"] = u["n"] if u else 0
        m["last"] = u["last"] if u else ""
        m["tools_used"] = dict(u["tools"].most_common(12)) if u else {}
    claude["mcp"] = mcps
    claude["other_mcp_calls"] = {k: v["n"] for k, v in cl.get("mcp", {}).items() if norm_server(k) not in matched}
    claude["plugins_enabled"] = sorted(k for k, v in (settings.get("enabledPlugins") or {}).items() if v)

    # ---- 开关与确定性问题（Claude Code）
    sw, _ = load_json_file(SWITCHES)
    sw = sw or {"claude": [], "codex": []}
    rows, problems = [], []
    for item in sw.get("claude", []):
        src = env if item["where"] == "env" else settings
        val = src.get(item["key"], MISSING)
        rows.append({"key": item["key"], "where": item["where"],
                     "value": None if val is MISSING else val, "set": val is not MISSING,
                     "default": item["default"], "what": item["what"], "ask": item.get("ask"),
                     "source": item["source"]})
    vt = ver_tuple(cc_version)
    dam = settings.get("disableAutoMode", MISSING)
    if dam is not MISSING and dam != "disable":
        problems.append("disableAutoMode 当前值是 %s，官方文档写的类型是字符串 \"disable\"，这样写可能不生效。" % json.dumps(dam))
    envw = env.get("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if isinstance(envw, str) and re.search(r"[kKmM]$", envw) and vt and vt < (2, 1, 304):
        problems.append("环境变量 CLAUDE_CODE_AUTO_COMPACT_WINDOW=%s 带后缀，v2.1.304 之前不认（当前 %s），改成纯数字。" % (envw, cc_version))
    acw = settings.get("autoCompactWindow")
    if envw is not None and acw is not None and str(acw) != str(envw):
        problems.append("autoCompactWindow=%s 和环境变量 CLAUDE_CODE_AUTO_COMPACT_WINDOW=%s 都设了且不一样，生效的是环境变量。" % (acw, envw))
    for label, v in (("autoCompactWindow", acw), ("CLAUDE_CODE_AUTO_COMPACT_WINDOW", envw)):
        try:
            iv = int(str(v))
        except (TypeError, ValueError):
            continue
        if not 100000 <= iv <= 1000000:
            problems.append("%s=%s 超出官方范围 100000–1000000。" % (label, v))
    boc = settings.get("bashOutputMaxChars")
    if isinstance(boc, int) and not 4000 <= boc <= 128000:
        problems.append("bashOutputMaxChars=%s 超出 4000–128000，会被夹到范围内。" % boc)
    notes = []   # 影响常驻上下文的设置：是取舍，不是错误
    if str(env.get("ENABLE_TOOL_SEARCH", "")).lower() == "false":
        notes.append("ENABLE_TOOL_SEARCH=false：工具说明（MCP 的，和一部分内置的）每轮都常驻上下文，不走「用到才加载」。删掉这个环境变量就回到默认。")
    gateway = bool(env.get("ANTHROPIC_BASE_URL")) and "anthropic.com" not in str(env.get("ANTHROPIC_BASE_URL"))
    if gateway and vt and vt < (2, 1, 181) and str(env.get("CLAUDE_CODE_ATTRIBUTION_HEADER")) != "0":
        problems.append("走自定义网关且版本低于 2.1.181：系统提示词开头带每次请求都变的标记，会破坏网关侧缓存。升级，或设 CLAUDE_CODE_ATTRIBUTION_HEADER=0。")
    for m in mcps:
        if m["alwaysLoad"]:
            notes.append("MCP %s 设了 alwaysLoad：它的工具说明每轮常驻，不走延迟加载（近 %d 天调用 %d 次）。" % (m["name"], args.days, m["calls"]))
    claude["switches"], claude["problems"], claude["gateway"], claude["notes"] = rows, problems, gateway, notes

    # ---- /doctor prompt-audit 能不能调
    pa = {"checks": [], "available": None}
    if has_claude:
        ok = True
        if not vt:
            pa["checks"].append("版本未知（没有日志）。先跑 claude --version，要 2.1.283 以上。")
            ok = None
        elif vt < (2, 1, 283):
            pa["checks"].append("版本 %s 低于 2.1.283：先升级 Claude Code。" % cc_version)
            ok = False
        else:
            pa["checks"].append("版本 %s，够（要 2.1.283 以上）。" % cc_version)
        if settings.get("disableBundledSkills") is True or str(env.get("CLAUDE_CODE_DISABLE_BUNDLED_SKILLS")) == "1":
            pa["checks"].append("disableBundledSkills 开着：内置 skill 全关，prompt-audit 用不了。")
            ok = False
        for n in ("claude-api", "doctor"):
            st = overrides.get(n)
            if st and st != "on":
                pa["checks"].append("skillOverrides 里 %s 是 %s：prompt-audit 要靠它，得先改回 on。" % (n, json.dumps(st)))
                ok = False
        if str(env.get("DISABLE_DOCTOR_COMMAND")) == "1":
            pa["checks"].append("DISABLE_DOCTOR_COMMAND=1：/doctor 被隐藏。")
            ok = False
        pa["available"] = ok
    # 调不了时的退路：官方那份说明文件本身。本机的插件市场克隆或插件缓存里常有一份。
    pa["official_url"] = PROMPT_AUDIT_URL
    copies = []
    plug = os.path.join(c_dir, "plugins")
    for pat in (("marketplaces", "*"), ("cache", "*", "*", "*")):
        copies += glob.glob(os.path.join(plug, *pat, "skills", "claude-api", "shared", "prompt-audit.md"))
    copies = [p for p in copies if os.path.isfile(p)]
    if copies:
        best = max(copies, key=os.path.getmtime)
        pa["official_file"] = {"path": best, "date": iso_utc(os.path.getmtime(best))[:10]}
    else:
        pa["official_file"] = None
    claude["prompt_audit"] = pa
    ev["claude"] = claude

    # ---- Codex
    codex = {"present": has_codex, "version": cx.get("version"), "log_files": cx.get("files", 0),
             "log_bytes": cx.get("bytes", 0)}
    if has_codex:
        cfg_p = os.path.join(x_dir, "config.toml")
        cfg, degraded, c_err = load_toml_file(cfg_p)
        track(cfg_p)
        codex["config_error"] = None if c_err in (None, "absent") else c_err
        codex["toml_degraded"] = degraded
        cfg = cfg if isinstance(cfg, dict) else {}
        codex["switches"] = [{"key": i["key"], "value": cfg.get(i["key"]), "set": i["key"] in cfg,
                              "default": i["default"], "what": i["what"], "source": i["source"]}
                             for i in sw.get("codex", [])]
        xp = []
        pct = cfg.get("model_post_turn_compact_threshold_percent")
        if isinstance(pct, (int, float)) and not 0 <= pct <= 100:
            xp.append("model_post_turn_compact_threshold_percent=%s 超出 0–100。" % pct)
        limit = cfg.get("project_doc_max_bytes", 32768)
        over = {}
        for pr in projects:
            total = sum(os.path.getsize(f) for f in pr["codex_files"])
            if isinstance(limit, int) and total > limit:
                key = tuple(sorted(sha256_file(f) for f in pr["codex_files"]))
                if key in over:
                    over[key][1] += 1 + len(pr["same_as"])
                else:
                    over[key] = ["%s 的 AGENTS.md 合计 %d 字节，超过 project_doc_max_bytes=%d。按官方 schema 的说明，超出部分 Codex 读不到。" % (show(pr["cwd"], home), total, limit), len(pr["same_as"])]
        for text, more in over.values():
            xp.append(text + ("（另有 %d 个目录情况相同）" % more if more else ""))
        g = os.path.join(x_dir, "AGENTS.md")
        codex["global_agents_bytes"] = os.path.getsize(g) if os.path.isfile(g) else None
        used_x = {norm_server(k): v for k, v in cx.get("mcp", {}).items()}
        xm, matched = [], set()
        for name, c in (cfg.get("mcp_servers") or {}).items():
            b = mcp_brief(name, c, "config.toml")
            u = used_x.get(norm_server(name))
            matched.add(norm_server(name))
            b["calls"], b["last"] = (u["n"], u["last"]) if u else (0, "")
            b["tools_used"] = dict(u["tools"].most_common(12)) if u else {}
            xm.append(b)
        codex["mcp"] = xm
        codex["other_mcp_calls"] = {k: v["n"] for k, v in cx.get("mcp", {}).items() if norm_server(k) not in matched}
        sk_cfg = (cfg.get("skills") or {}).get("config") if isinstance(cfg.get("skills"), dict) else None
        disabled = set()
        for e in sk_cfg or []:
            if isinstance(e, dict) and e.get("enabled") is False:
                disabled.add(e.get("path") or e.get("name"))
        xs = list_skills(os.path.join(x_dir, "skills"), "codex")
        for s in xs:
            track(s["md"])
            u = sr.get(s["dir"], sr.get(s["name"], new_use()))
            s["reads"], s["last"] = u["n"], u["last"]
            s["enabled"] = not (s["md"] in disabled or s["path"] in disabled or s["name"] in disabled)
            flags = []
            if s["reads"] == 0:
                if RARE_RE.search(s["dir"] + " " + s["desc"]):
                    flags.append("像低频保命项")
                if (now - s["installed_ts"]) / 86400 < args.days:
                    flags.append("装了才 %d 天" % max((now - s["installed_ts"]) / 86400, 0))
            s["flags"] = flags
        codex["skills"] = xs
        codex["skills_shared_with_claude"] = bool(
            has_claude and os.path.isdir(os.path.join(c_dir, "skills"))
            and os.path.realpath(os.path.join(x_dir, "skills")) == os.path.realpath(os.path.join(c_dir, "skills")))
        codex["problems"] = xp
        ad = os.path.join(x_dir, "agents")
        codex["agents"] = sorted(f[:-5] for f in os.listdir(ad) if f.endswith(".toml")) if os.path.isdir(ad) else []
    ev["codex"] = codex

    # ---- 重复规则
    groups = {}
    for pr in projects:
        if has_claude:
            groups["claude@" + pr["cwd"]] = set(os.path.realpath(f) for f in global_claude + pr["claude_files"])
        if has_codex:
            groups["codex@" + pr["cwd"]] = set(os.path.realpath(f) for f in global_codex + pr["codex_files"])
    if not projects:
        if has_claude and global_claude:
            groups["claude@~"] = set(os.path.realpath(f) for f in global_claude)
        if has_codex and global_codex:
            groups["codex@~"] = set(os.path.realpath(f) for f in global_codex)
    all_files = sorted(set().union(*groups.values())) if groups else []
    file_groups = defaultdict(set)
    for gname, fs in groups.items():
        for f in fs:
            file_groups[f].add(gname)
    units = {f: units_of(f) for f in all_files}
    hashes = {f: sha256_file(f) for f in all_files}
    is_global = set(os.path.realpath(f) for f in global_claude + global_codex)
    dups = []
    for i, a in enumerate(all_files):
        for b in all_files[i + 1:]:
            ga, gb = file_groups[a], file_groups[b]
            if ga & gb:
                rel = "same_session"
            elif (a in is_global) == (b in is_global) and any(
                    x.split("@", 1)[1] == y.split("@", 1)[1] and x.split("@", 1)[0] != y.split("@", 1)[0]
                    for x in ga for y in gb):
                # 对应的两份：全局对全局，或同一个项目里的 CLAUDE.md 对 AGENTS.md
                rel = "cross_agent"
            else:
                continue              # 不同项目、或一端全局一端项目的，不比
            if hashes[a] == hashes[b]:
                if not units[a]:
                    continue          # 两个都只是一行 @import 之类的指针文件，没有规则可重复
                dups.append({"a": a, "b": b, "relation": rel, "identical_file": True, "exact": [], "near": []})
                continue
            exact, near = compare_units(units[a], units[b])
            if not exact and not near:
                continue
            dups.append({
                "a": a, "b": b, "relation": rel, "identical_file": False,
                "exact": [{"a_line": x[0], "b_line": y[0], "text": clip(x[1])} for x, y in exact],
                "near": [{"a_line": x[0], "b_line": y[0], "a_text": clip(x[1]), "b_text": clip(y[1]), "ratio": r_}
                         for x, y, r_ in near]})
    ev["duplicates"] = dups
    ev["instruction_files"] = [{"path": f, "bytes": os.path.getsize(f), "rules": len(units[f]), "sha256": hashes[f],
                                "chars": len(read_text(f)),
                                "lines": read_text(f).count("\n") + 1, "missing_imports": missing_imports(f, home),
                                "every_session": f in is_global,
                                "sections": sorted(sections_of(f), key=lambda s: -s["chars"])[:6],
                                "loaded_by": sorted(file_groups[f])} for f in all_files]

    # ---- 日志覆盖
    cov = {}
    for label, r in (("claude", cl), ("codex", cx)):
        if r.get("present") and (r.get("earliest") or r.get("older_evidence")):
            first = iso_to_ts(r["earliest"]) if r.get("earliest") else cutoff
            cov[label] = {"earliest_in_window": (r.get("earliest") or "")[:10],
                          "full_window": bool(r.get("older_evidence")),
                          "days_covered": int(min((now - first) / 86400, args.days)),
                          "unreadable_compressed": r.get("unreadable", 0)}
    ev["coverage"] = cov
    ev["backups"] = [{"id": m["id"], "note": m.get("note"), "state": backup_state(m)} for m in all_manifests(home)]

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(ev, f, ensure_ascii=False, indent=1, default=lambda o: dict(o) if isinstance(o, Counter) else str(o))
    print(render(ev, home, args.all))


def md(ts):
    """日志里的时间是 UTC，报给用户的日期按这台电脑的本地时间。"""
    if not ts:
        return "—"
    t = iso_to_ts(ts)
    return time.strftime("%m-%d", time.localtime(t)) if t else ts[5:10]


def render(ev, home, show_all):
    L = []
    cap = 10 ** 6 if show_all else 25
    c, x = ev["claude"], ev["codex"]
    days = ev["days"]
    L.append("save-my-tokens 扫描（只读，没有改任何文件）")
    L.append("范围：%s   窗口：近 %d 天（%s 起）" % (show(home, home), days, ev["window_start"][:10]))
    L.append("Claude Code：%s   Codex：%s" % (
        ("有，版本 %s，窗口内 %d 个会话文件" % (c["version"] or "未知", c["log_files"])) if c["present"] else "没有",
        ("有，版本 %s，窗口内 %d 个会话文件" % (x["version"] or "未知", x["log_files"])) if x["present"] else "没有"))
    for label, name in (("claude", "Claude Code"), ("codex", "Codex")):
        cv = ev["coverage"].get(label)
        if cv and not cv["full_window"]:
            L.append("注意：%s 的日志最早只到 %s，实际只覆盖 %d 天。下面的「0 次」只代表这 %d 天。" % (name, cv["earliest_in_window"], cv["days_covered"], cv["days_covered"]))
        if cv and cv["unreadable_compressed"]:
            L.append("注意：%s 有 %d 个压缩的会话文件（.jsonl.zst）读不了：要 Python 3.14 以上，或系统里装了 zstd 命令。这部分没数进去，次数偏少。" % (name, cv["unreadable_compressed"]))
    for label, obj in (("Claude Code", c), ("Codex", x)):
        if obj.get("present") and not obj.get("log_files"):
            L.append("注意：%s 窗口内没有会话日志，调用次数全部是 0，不能据此判断用没用。" % label)
    if c.get("settings_error"):
        L.append("注意：~/.claude/settings.json 解析失败（%s），开关和 skill 状态读不到。" % c["settings_error"])
    if x.get("config_error"):
        L.append("注意：~/.codex/config.toml 解析失败（%s）。" % x["config_error"])
    if x.get("toml_degraded"):
        L.append("注意：这个 Python 没有 tomllib（3.11 以上才有），config.toml 用简化解析，复杂写法可能读漏；set 改不了 TOML。")

    if c["present"]:
        render_startup(L, c, home, days)
        L.append("")
        L.append("######## 清理：每次请求都带着、可以拿掉的东西 ########")

        sk = c["skills"]
        usr = [s for s in sk if s["scope"] == "user"]
        prj = [s for s in sk if s["scope"] != "user"]
        st_count = Counter(s["state"] for s in usr)
        visible = [s for s in usr if s["state"] in ("on", "name-only")]
        L.append("")
        L.append("== Skill（Claude Code）==")
        L.append("用户级 %d 个（%s）。其中模型每轮能看到 %d 个，描述合计 %d 字符。" % (
            len(usr), "、".join("%s %d" % kv for kv in sorted(st_count.items())) or "无",
            len(visible), sum(s["desc_chars"] for s in visible if s["state"] == "on")))
        if prj:
            L.append("项目级 %d 个（只在各自项目里加载，来自近期用过的 %d 组项目目录）。" % (len(prj), len(ev["projects"])))
        ls = c.get("listing")
        if ls:
            la = ls["latest"]
            L.append("日志实记：最近一次新开会话（%s，%s）发给模型的 skill 清单是 %d 个、%d 字符；窗口内 %d 次新开会话，最少 %d 个、最多 %d 个。" % (
                md(la["ts"]), show(la["cwd"], home) if la["cwd"] else "目录未知", la["count"], la["chars"],
                ls["samples"], ls["min"], ls["max"]))
            L.append("  这个数是 Claude Code 自己记的：内置、插件和当前项目的 skill 也算在里面，字符数里除了描述还有每个 skill 的名字。改完配置后新开一个会话再扫，用它核对。")
        for b in c.get("broken_skill_links") or []:
            L.append("⚠ 软链断了：%s → %s（目标不存在，这个入口已经用不了）" % (show(b["path"], home), b["target"]))
        hidden = [s for s in usr if s["state"] not in ("on", "name-only")]
        if hidden:
            L.append("模型看不见的 %d 个：%s" % (len(hidden), "、".join("%s（%s）" % (s["dir"], "仅手动" if s["state"] == "user-invocable-only" else s["state"]) for s in hidden[:12]) + ("…（完整名单在 json 里）" if len(hidden) > 12 else "")))
        L.append("次数怎么数的：「模型调」是模型用 Skill 工具调用，「手敲」是用户输入 /名字，「Codex 读」是 Codex 按路径读了这个 skill 的 SKILL.md。")

        def where(s):
            if s["scope"] == "user":
                return ""
            w = "项目 " + show(s["scope"].split(":", 1)[1], home)
            return w + ("，另有 %d 个目录有同一份" % len(s["also_in"]) if s["also_in"] else "") + "，"

        def idle_line(s):
            extra = []
            if s["flags"]:
                extra.append("⚠ " + "；".join(s["flags"]))
            if s.get("referenced_by"):
                extra.append("引用它的：" + "、".join(show(p, home) for p in s["referenced_by"][:2]))
            if s.get("last_ever"):
                extra.append("skillUsage 记着最后一次是 " + s["last_ever"])
            if s["symlink"]:
                extra.append("软链 → " + show(s["target"], home))
            return "  - %s [%s%s，描述 %d 字符] %s" % (s["dir"], where(s), s["state"], s["desc_chars"], "  ".join(extra))

        idle = sorted([s for s in visible if s["total"] == 0], key=lambda s: -s["desc_chars"])
        L.append("用户级里近 %d 天 0 次调用、还对模型可见的：%d 个（候选，不是结论）" % (days, len(idle)))
        gs = c.get("skill_groups") or {}
        gcap = cap if show_all else 8
        L.append("模型看得见的 %d 个，按近 %d 天的用法分组（组里的完整名单：slim show --scan <json> --group 字母）：" % (len(visible), days))
        for g, title, advice in SKILL_GROUPS:
            members = sorted([s for s in visible if s.get("group") == g], key=lambda s: (-s["desc_chars"], s["dir"]))
            if not members:
                continue
            L.append("  %s 组 %d 个，描述合计 %d 字符：%s → %s" % (g, len(members), gs.get(g, {}).get("desc_chars", 0), title, advice))
            if g == "E":
                continue                      # 在用的在下面「用过的」里列
            if g in ("A", "B"):
                L.extend("  " + idle_line(s) for s in members[:gcap])
            else:
                L.extend("    - %s [描述 %d 字符]：手敲 %d，模型调 %d，最近 %s" % (
                    s["dir"], s["desc_chars"], s["user_calls"], s["model_calls"], md(s["last"])) for s in members[:gcap])
            if len(members) > gcap:
                L.append("      …还有 %d 个" % (len(members) - gcap))
        idle_p = sorted([s for s in prj if s["total"] == 0 and s["state"] in ("on", "name-only")], key=lambda s: -s["desc_chars"])
        if idle_p:
            L.append("项目级里 0 次调用的：%d 个" % len(idle_p))
            L.extend(idle_line(s) for s in idle_p[:cap])
            if len(idle_p) > cap:
                L.append("  …还有 %d 个，加 --all 看全部" % (len(idle_p) - cap))
        twins = [s for s in prj if s.get("twin")]
        if twins:
            L.append("同名 skill 在用户级和项目级各装了一份（日志分不出用的是哪份，次数是合在一起的）：")
            for s in twins[:cap]:
                L.append("  - %s：%s也有，%s" % (s["dir"], where(s).rstrip("，").replace("项目 ", ""), s["twin"]))

        def busy_line(s):
            note = "  （当前状态 %s）" % s["state"] if s["state"] != "on" else ""
            only = ""
            if s["scope"] == "user" and len(s["cwds"]) == 1 and s["model_calls"] + s["user_calls"] >= 3 and not s["codex_reads"]:
                only = "  只在 %s 用过" % show(list(s["cwds"])[0], home)
            return (note or only), "  - %s%s：模型调 %d，手敲 %d，Codex 读 %d，最近 %s%s%s" % (
                s["dir"], "（项目级）" if s["scope"] != "user" else "", s["model_calls"], s["user_calls"], s["codex_reads"], md(s["last"]), note, only)

        # 和用户级同名的项目级 skill 次数是合在一起的，只列用户级那一行，免得看成两份各用了这么多次
        busy = sorted([s for s in sk if s["total"] > 0 and not s.get("twin")], key=lambda s: -s["total"])
        many = len(busy) > 40      # 用过的很多时只列几个，名单在 json 里；重点留给上面的分组
        top = 10 ** 6 if show_all else (6 if many else 12)
        shown = 0
        L.append("用过的：%d 个（下面列调用最多的，以及状态或用法值得一提的）" % len(busy))
        for i, s in enumerate(busy):
            notable, text = busy_line(s)
            if i < top or (notable and shown < top + (cap if show_all else (2 if many else 6))):
                L.append(text)
                shown += 1
        if len(busy) > shown:
            L.append("  …还有 %d 个，加 --all 看全部" % (len(busy) - shown))
        if c["other_skill_calls"]:
            top = sorted(c["other_skill_calls"].items(), key=lambda kv: -kv[1])[:8]
            L.append("不在上面清单里的 skill 调用（内置、插件带的或已删除的）：" + "、".join("%s %d" % kv for kv in top))
        if not c["skill_usage_source"]:
            L.append("（没有 ~/.claude.json 的 skillUsage 可供交叉核对）")

        L.append("")
        L.append("== MCP（Claude Code）==")
        if not c["mcp"]:
            L.append("没有配置 MCP server。")
        for m in sorted(c["mcp"], key=lambda m: m["calls"]):
            tools = "；用到的工具：" + "、".join("%s %d" % kv for kv in list(m["tools_used"].items())[:6]) if m["tools_used"] else ""
            L.append("  - %s [%s，%s%s]：近 %d 天调用 %d 次，最近 %s%s" % (m["name"], m["scope"].split(":")[0], m["transport"], "，alwaysLoad" if m["alwaysLoad"] else "", days, m["calls"], md(m["last"]), tools))
        if c["other_mcp_calls"]:
            L.append("日志里出现、但不在上面配置里的 MCP（插件带的、别的项目的或已移除的）：" + "、".join("%s %d" % kv for kv in sorted(c["other_mcp_calls"].items(), key=lambda kv: -kv[1])[:8]))
        if c["plugins_enabled"]:
            L.append("启用的插件（它们带的 skill / MCP 归插件管理器管，这里不动）：" + "、".join(c["plugins_enabled"]))

        L.append("")
        L.append("== Subagent（Claude Code）==")
        if not c["agents"]:
            L.append("没有自定义 subagent。")
        for a in sorted(c["agents"], key=lambda a: a["calls"]):
            L.append("  - %s [%s]：近 %d 天调用 %d 次，最近 %s" % (a["name"], a["scope"].split(":")[0], days, a["calls"], md(a["last"])))
        if c["builtin_agent_calls"]:
            L.append("内置或插件 subagent 的调用：" + "、".join("%s %d" % kv for kv in sorted(c["builtin_agent_calls"].items(), key=lambda kv: -kv[1])[:8]))

    if x["present"]:
        L.append("")
        L.append("== Codex ==")
        if x.get("global_agents_bytes") is not None:
            L.append("全局 ~/.codex/AGENTS.md：%d 字节（每个 Codex 会话都加载）。" % x["global_agents_bytes"])
        if x.get("mcp"):
            L.append("MCP：")
            for m in sorted(x["mcp"], key=lambda m: m["calls"]):
                tools = "；用到的工具：" + "、".join("%s %d" % kv for kv in list(m["tools_used"].items())[:6]) if m["tools_used"] else ""
                lim = "，已设 enabled_tools" if m["enabled_tools"] is not None else ""
                L.append("  - %s [%s%s]：近 %d 天调用 %d 次，最近 %s%s" % (m["name"], "启用" if m["enabled"] else "已停用", lim, days, m["calls"], md(m["last"]), tools))
        if x.get("other_mcp_calls"):
            L.append("日志里出现、但不在 config.toml 里的 MCP：" + "、".join("%s %d" % kv for kv in sorted(x["other_mcp_calls"].items(), key=lambda kv: -kv[1])[:8]))
        xs = x.get("skills") or []
        if x.get("skills_shared_with_claude"):
            L.append("~/.codex/skills 就是 ~/.claude/skills（软链）：两端共用同一批 skill 文件。搬动或改名会同时影响两端；只想对一端停用，Claude Code 用 skillOverrides，Codex 用 skills.config。")
        if xs:
            idle = [s for s in xs if s["reads"] == 0 and s["enabled"]]
            L.append("Skill（~/.codex/skills，共 %d 个，停用 %d 个）：近 %d 天没被读过且启用着的 %d 个（候选）" % (len(xs), sum(1 for s in xs if not s["enabled"]), days, len(idle)))
            for s in idle[:cap]:
                L.append("  - %s [描述 %d 字符]%s%s" % (s["dir"], s["desc_chars"], "  ⚠ " + "；".join(s["flags"]) if s["flags"] else "", "  软链 → " + show(s["target"], home) if s["symlink"] else ""))
            read = sorted([s for s in xs if s["reads"]], key=lambda s: -s["reads"])
            top = 10 ** 6 if show_all else 12
            if read:
                L.append("读过的 %d 个，最多的：" % len(read) + "、".join("%s %d" % (s["dir"], s["reads"]) for s in read[:top]))
            L.append("（Codex 的次数是「工具调用里读了这个 SKILL.md」的次数，是推断，不是官方计数。）")
        if x.get("agents"):
            L.append("自定义 agent：%s（v1 不统计 Codex agent 的调用次数）" % "、".join(x["agents"]))

    L.append("")
    L.append("== 规则文件 ==")
    L.append("规则文件（CLAUDE.md、AGENTS.md、rules/ 下的文件）在会话一开始就整份加载，之后每次请求都带着。越大的越值得先看。")
    if ev["instruction_files"]:
        L.append("查了这些规则文件（从大到小；内容完全相同的只列一次）：")
        by_hash = {}
        for f in ev["instruction_files"]:
            by_hash.setdefault(f["sha256"], []).append(f)
        rows = [fs for fs in by_hash.values() if fs[0]["rules"]]     # 只有一行 @import 的指针文件不列
        rows.sort(key=lambda fs: -fs[0]["bytes"])
        for i, fs in enumerate(rows[:cap]):
            f = fs[0]
            L.append("  - %s（%d 字符，%d 字节，%d 行，%d 条）%s%s%s" % (
                show(f["path"], home), f.get("chars", 0), f["bytes"], f.get("lines", 0), f["rules"],
                ("  每个会话都加载" if f.get("every_session") else "") + ("  Codex 读的" if os.path.basename(f["path"]).startswith("AGENTS") else ""),
                "，另有 %d 份相同" % (len(fs) - 1) if len(fs) > 1 else "",
                "  超过官方建议的 200 行" if f.get("lines", 0) > 200 and os.path.basename(f["path"]).startswith("CLAUDE") else ""))
            secs = [s for s in f.get("sections") or [] if s["chars"] >= 800][:4]
            if f.get("chars", 0) >= 4000 and secs and (i < 5 or f.get("every_session") or show_all):
                L.append("      最大的几节：" + "；".join("「%s」%d 字符（第 %d 行起）" % (s["title"], s["chars"], s["line"]) for s in secs))
        if len(rows) > cap:
            L.append("  …还有 %d 个，加 --all 或看 --json" % (len(rows) - cap))
    mem = c.get("auto_memory") if c["present"] else None
    if mem and mem["count"]:
        L.append("Claude Code 自带的自动记忆：%s，%d 个项目有 MEMORY.md。它的开头 200 行或 25KB 在那个项目的每个会话里都加载，上面开局账单的「规则文件」一行不含它。最大的几份：" % (
            "开着" if mem["enabled"] else "已关", mem["count"]))
        for f in mem["files"][:4]:
            L.append("  - %s（%d 字节，%d 行）%s" % (
                "项目 %s 的 MEMORY.md" % show(f["project"], home) if f.get("project") else show(f["path"], home), f["bytes"], f["lines"],
                                               "  超过 200 行或 25KB，后面的部分开局读不到" if f["over_limit"] else ""))
    elif mem:
        L.append("Claude Code 自带的自动记忆：%s，还没有记下任何 MEMORY.md。" % ("开着" if mem["enabled"] else "已关"))
    L.append("")
    L.append("== 重复规则 ==")
    if ev["instruction_files"]:
        dead = [(f["path"], t) for f in ev["instruction_files"] for t in f.get("missing_imports") or []]
        if dead:
            L.append("写了 @引用、但文件不存在的（候选，先确认是不是引用）：")
            for pth, t in dead[:cap]:
                L.append("  - %s 里的 @%s" % (show(pth, home), t))

    def repo_key(d):   # 同一个仓库的不同 worktree：目录名和文件名都一样
        return tuple((os.path.basename(os.path.dirname(p)), os.path.basename(p)) for p in (d["a"], d["b"])) + (d["relation"],)

    seen_keys, kept, folded = set(), [], Counter()
    for d in ev["duplicates"]:
        k = repo_key(d)
        if k in seen_keys:
            folded[k] += 1
        else:
            seen_keys.add(k)
            kept.append(d)
    same = [d for d in kept if d["relation"] == "same_session"]
    cross = [d for d in kept if d["relation"] == "cross_agent"]
    if not same:
        L.append("同一个会话里会一起加载的文件之间：没发现逐条相同或高度相似的规则。")
    for d in same:
        L.append("【同一会话重复加载】%s × %s%s" % (show(d["a"], home), show(d["b"], home), "（另有 %d 个同名目录情况类似）" % folded[repo_key(d)] if folded[repo_key(d)] else ""))
        if d["identical_file"]:
            L.append("  两个文件内容完全相同。")
        for e in d["exact"][:8]:
            L.append("  = 第 %d 行 / 第 %d 行：%s" % (e["a_line"], e["b_line"], e["text"]))
        if len(d["exact"]) > 8:
            L.append("  …逐条相同的共 %d 条" % len(d["exact"]))
        for e in d["near"][:8]:
            L.append("  ≈ 第 %d 行：%s" % (e["a_line"], e["a_text"]))
            L.append("    第 %d 行：%s" % (e["b_line"], e["b_text"]))
    for d in cross:
        L.append("【两个 agent 各一份，不是重复付费】%s × %s" % (show(d["a"], home), show(d["b"], home)))
        if d["identical_file"]:
            L.append("  两个文件内容完全相同（可以考虑让 CLAUDE.md 只写一行 @AGENTS.md）。")
            continue
        L.append("  逐条相同 %d 条；相似但有出入 %d 条%s" % (len(d["exact"]), len(d["near"]), "，有出入的是：" if d["near"] else "。"))
        for e in d["near"][:8]:
            L.append("  ≈ 第 %d 行：%s" % (e["a_line"], e["a_text"]))
            L.append("    第 %d 行：%s" % (e["b_line"], e["b_text"]))
    L.append("（脚本只能找逐条相同和措辞相近的。意思相同、写法不同的重复，要读上面这些文件自己判断。）")
    for f in sorted({f for p in ev["projects"] for f in p.get("excluded", [])}):
        L.append("（%s 被 settings.json 的 claudeMdExcludes 排除：Claude Code 不加载它，它 @import 的文件也不算在同一会话里。）" % show(f, home))
    grouped = [p for p in ev["projects"] if p["same_as"]]
    if grouped:
        L.append("（有 %d 组项目目录的规则文件内容完全相同，多半是同一个仓库的 worktree，共 %d 个目录，每组只算一次。）" % (len(grouped), sum(len(p["same_as"]) + 1 for p in grouped)))

    L.append("")
    L.append("######## 配置：不删东西，只改几个设置 ########")
    if c["present"]:
        render_config(L, c, days)
    L.append("")
    L.append("== 开关 ==")
    probs = (c.get("problems") or []) + (x.get("problems") or [])
    if probs:
        L.append("确定写错或不生效的：")
        for p in probs:
            L.append("  ! " + p)
    else:
        L.append("没发现写错或不生效的配置。")
    if c.get("notes"):
        L.append("影响常驻上下文的设置（是取舍，不是错误）：")
        for p in c["notes"]:
            L.append("  · " + p)
    if c["present"]:
        walk = [r for r in c["switches"] if r.get("ask")]
        if walk:
            L.append("值得和用户过一遍的几个（每个都是取舍，讲清楚再由他定）：")
            for r in walk:
                L.append("  ? %s，现在是 %s，默认 %s" % (
                    r["key"], json.dumps(r["value"], ensure_ascii=False) if r["set"] else "没设", r["default"]))
                L.append("      " + r["ask"])
    L.append("下面是取舍项，只列事实，不代表建议改：")
    unset = []
    if c["present"]:
        if c.get("gateway"):
            L.append("  （Claude Code 走的是自定义网关。）")
        for r in c["switches"]:
            name = ("env." if r["where"] == "env" else "") + r["key"]
            if r["set"]:
                L.append("  - %s = %s（默认：%s）" % (name, json.dumps(r["value"], ensure_ascii=False), r["default"]))
            else:
                unset.append(name)
    if x["present"]:
        for r in x.get("switches", []):
            if r["set"]:
                L.append("  - codex.%s = %s（默认：%s）" % (r["key"], json.dumps(r["value"], ensure_ascii=False), r["default"]))
            else:
                unset.append("codex." + r["key"])
    if unset:
        L.append("  没设、用默认值的：" + "、".join(unset))
    L.append("每个键管什么、默认是什么、出处在哪：%s" % SWITCHES)

    if c["present"]:
        pa = c["prompt_audit"]
        L.append("")
        L.append("== 官方 /doctor prompt-audit（查旧模型写法、失效路径、互相矛盾的规则）==")
        L.append("能不能调：%s" % {True: "能", False: "现在不能", None: "不确定"}[pa["available"]])
        for ck in pa["checks"]:
            L.append("  - " + ck)
        if pa["available"] is not True:
            of = pa.get("official_file")
            L.append("调不了也能做：直接读官方那份说明文件照着做，不用为此改设置。")
            if of:
                L.append("  本机副本：%s（文件日期 %s）" % (show(of["path"], home), of["date"]))
            L.append("  原文：%s" % pa["official_url"])

    if ev["backups"]:
        L.append("")
        L.append("== 之前的备份 ==")
        for b in ev["backups"][-5:]:
            L.append("  - %s [%s] %s" % (b["id"], b["state"], b["note"] or ""))
    return "\n".join(L)


def num(n):
    return "{:,}".format(int(n))


def wan(n):
    """token 数用「万」说：82,300 → 8.2 万。"""
    n = int(n)
    if n >= 100000000:
        return "%.1f 亿" % (n / 100000000.0)
    if n >= 10000:
        return "%.1f 万" % (n / 10000.0)
    return num(n)


def pct(part, whole):
    v = part * 100.0 / max(whole, 1)
    return "不到 0.1%" if 0 < v < 0.05 else "占 %.1f%%" % v


PART_NAMES = (
    ("rules", "规则文件"), ("skills", "skill 清单"), ("mcp_tools", "MCP 工具说明"), ("builtin_tools", "内置工具说明"),
    ("system", "系统提示"), ("hooks", "会话开始时 hook 塞进来的内容"), ("mcp_notes", "MCP 自带的使用说明"),
    ("deferred", "延迟加载的工具名单"), ("agents", "subagent 名单"), ("other", "其他附带信息（环境、沙箱说明等）"),
)
PART_CAN = {
    "rules": "能瘦：见下面「规则文件」", "skills": "能减：见下面「Skill」", "mcp_tools": "能减：停掉不用的 MCP；想留着的，看「开关」里 ENABLE_TOOL_SEARCH 是不是被设成了 false",
    "builtin_tools": "基本是固定的", "system": "固定的", "hooks": "看 hook 是不是还需要", "mcp_notes": "停掉不用的 MCP 就没了",
    "deferred": "停掉不用的 MCP 会变短", "agents": "删掉不用的 subagent 会变短", "other": "基本是固定的",
}


def render_startup(L, c, home, days):
    st = c.get("startup")
    L.append("")
    L.append("######## 开局：新会话的第一次请求带了多少 token ########")
    if not st:
        L.append("日志里没找到新开会话的记录（Claude Code 版本太旧，或窗口内没有新会话），这一块量不出来。")
        L.append("替代办法：让用户新开一个会话，什么都不说，直接输入 /context，把结果贴过来。")
        return
    if st["n"] < 5:
        # 样本太少时不报中位数和分位数，免得一个数被说三遍
        L.append("实测（Claude Code 自己记在日志里的用量，不是估的）：近 %d 天日志里只有 %d 个新会话，第一次请求的输入在 %s 到 %s token 之间。" % (
            days, st["n"], num(st["min"]), num(st["max"])) if st["min"] != st["max"] else
            "实测（Claude Code 自己记在日志里的用量，不是估的）：近 %d 天日志里只有 %d 个新会话。" % (days, st["n"]))
    else:
        L.append("实测（Claude Code 自己记在日志里的用量，不是估的）：近 %d 天 %d 个新会话，第一次请求的输入中位数 %s token，最少 %s，九成在 %s 以内。" % (
            days, st["n"], num(st["median"]), num(st["min"]), num(st.get("p90", st["max"]))))
    if st.get("recent7") and st["n"] >= 5:
        L.append("最近 7 天：%d 个新会话，中位数 %s token。" % (st["recent7"]["n"], num(st["recent7"]["median"])))
    if len(st["by_cwd"]) > 1:
        L.append("按目录（开局大小跟着项目的规则文件、项目级 skill 和 MCP 变）：")
        for r in st["by_cwd"]:
            L.append("  - %s：%d 个新会话，中位数 %s，最近一次 %s（%s）" % (
                show(r["cwd"], home) if r["cwd"] else "目录未知", r["n"], num(r["median"]), num(r["latest"]), md(r["latest_ts"])))
    la = st.get("focus") or st["latest"]
    parts = la.get("parts") or {}
    total = sum(parts.values())
    L.append("拿最近常用的目录里最近一次新开会话来看（%s，%s，%s）：第一次请求 %s token。" % (
        md(la["ts"]), show(la["cwd"], home) if la["cwd"] else "目录未知", la["model"], num(la["tokens"])))
    if not total:
        L.append("  这个版本的日志没有记这次请求里各部分的大小，分不出明细。")
    else:
        L.append("  这次请求里各部分的大小（字符数，从大到小；占比按字符算，中文和英文折成 token 的比例不同，只用来排先后）：")
        for key, v in sorted(parts.items(), key=lambda kv: -kv[1]):
            if not v:
                continue
            name = dict(PART_NAMES).get(key, key)
            extra = ""
            if key == "skills" and la.get("skill_count"):
                extra = " %d 个" % la["skill_count"]
            elif key == "rules":
                extra = " %d 个" % len(la.get("files") or [])
            elif key == "builtin_tools" and la.get("tools"):
                extra = " %d 个" % la["tools"]["builtin"]["n"]
            elif key == "mcp_tools" and la.get("tools"):
                extra = " %d 个" % sum(v_["n"] for v_ in la["tools"]["mcp"].values())
            elif key == "deferred" and la.get("deferred_n"):
                extra = " %d 个" % la["deferred_n"]
            can = PART_CAN.get(key, "")
            if key == "builtin_tools" and not la.get("deferred_n") and any("ENABLE_TOOL_SEARCH=false" in str(x) for x in c.get("notes") or []):
                # 实测（2.1.321）：这个开关设成 false 时，本来「用到才加载」的那部分内置工具也整份带上
                can = "能减：ENABLE_TOOL_SEARCH 被设成了 false，所有工具的说明都整份带上了；改回默认后一部分工具用到才加载"
            L.append("  %5.1f%%  %8s 字符  %s%s  —— %s" % (v * 100.0 / total, num(v), name, extra, can))
            if key == "rules":
                for f in sorted(la.get("files") or [], key=lambda f: -f["chars"])[:6]:
                    L.append("             · %s 字符  %s" % (num(f["chars"]), show(f["path"], home)))
            if key == "mcp_tools" and la.get("tools"):
                for srv, v_ in sorted(la["tools"]["mcp"].items(), key=lambda kv: -kv[1]["chars"])[:6]:
                    L.append("             · %s 字符  %s（%d 个工具）" % (num(v_["chars"]), srv, v_["n"]))
        if la.get("tools") is None:
            L.append("  （这个版本的日志没记系统提示和工具说明的大小，上面只有其余部分。）")
    L.append("怎么用这一块：先砍排在前面、而且「能瘦」「能减」的。改完后新开一个会话说一句话，再扫一次，对比这里的第一次请求 token。")


def render_config(L, c, days):
    cx = c.get("context")
    cw = c.get("compact_window") or {}
    L.append("")
    L.append("== 自动压缩窗口（会话长到多大就自动压缩）==")
    if cw.get("disabled"):
        cur = "自动压缩被关掉了（autoCompactEnabled=false 或 DISABLE_AUTO_COMPACT=1）"
    elif cw.get("env") is not None:
        cur = "环境变量 CLAUDE_CODE_AUTO_COMPACT_WINDOW=%s" % cw["env"]
    elif cw.get("settings") is not None:
        cur = "autoCompactWindow=%s" % cw["settings"]
    else:
        cur = "没设，Claude Code 按模型自己定"
    if cw.get("per_model"):
        cur += "；另外 /autocompact 给这些模型单独设过：" + "、".join("%s=%s" % kv for kv in cw["per_model"].items())
    L.append("现在的设置：%s。" % cur)
    if cx:
        L.append("实测：近 %d 天主会话 %s 次请求，一共带了 %s token 的上下文（每次请求都把当时的整段历史带一遍）。" % (
            days, num(cx["requests"]), wan(cx["tokens"])))
        for label, name in (("200k", "20 万"), ("400k", "40 万"), ("500k", "50 万")):
            o = cx["over"][label]
            if o["requests"]:
                L.append("  上下文超过 %s的请求：%s 次（%s），带了 %s token（%s）" % (
                    name, num(o["requests"]), pct(o["requests"], cx["requests"]), wan(o["tokens"]), pct(o["tokens"], cx["tokens"])))
        L.append("  %d 个会话里，最长的那次请求：中位数 %s，九成在 %s 以内，最大 %s；超过 40 万的会话 %d 个，超过 50 万的 %d 个。" % (
            cx["sessions"], wan(cx["peak_median"]), wan(cx["peak_p90"]), wan(cx["peak_max"]),
            cx["sessions_over"]["400k"], cx["sessions_over"]["500k"]))
        L.append("  怎么读：窗口设成 40 万或 50 万，上面「超过」的那些请求就不会再带那么长的历史；代价是压缩得更早，压缩后模型手里只有摘要。")
    else:
        L.append("日志里没有用量记录，量不出会话实际长到多大。")
    L.append("")
    L.append("== 缓存：放着不动再回来 ==")
    rw = (cx or {}).get("rewrites") or {"n": 0}
    if rw["n"]:
        L.append("实测：近 %d 天有 %s 次请求没命中缓存，把 10 万 token 以上的历史整段重算了一遍，合计 %s token。" % (days, num(rw["n"]), wan(rw["tokens"])))
        for why, v in sorted(rw["by"].items(), key=lambda kv: -kv[1]["tokens"]):
            L.append("  - %s：%s 次，%s token" % (why, num(v["n"]), wan(v["tokens"])))
        L.append("  怎么读：缓存有时效（订阅用户的主会话 1 小时，其余 5 分钟）。隔久了再回来，第一句话要把整段历史按全价重算。离开前先 /compact，或者回来时新开会话，这一笔就小得多。")
    elif cx:
        L.append("近 %d 天没看到「10 万 token 以上的历史整段重算」的请求。" % days)
    L.append("")
    L.append("== 子代理用什么模型 ==")
    rq = c.get("requests_by_model") or {}
    for kind, name in (("main", "主会话"), ("sub", "子代理")):
        rows = sorted((rq.get(kind) or {}).items(), key=lambda kv: -kv[1]["tokens"])
        if rows:
            L.append("%s：%s" % (name, "；".join("%s %s 次、%s token" % (m, num(v["n"]), wan(v["tokens"])) for m, v in rows[:5])))
    ac = c.get("agent_calls") or {}
    if ac.get("total"):
        L.append("派子代理 %s 次：其中 %s 次没指定模型（跟主会话用同一个）%s。" % (
            num(ac["total"]), num(ac["no_model"]),
            "，指定了的：" + "、".join("%s %d" % kv for kv in list(ac["by_model"].items())[:5]) if ac["by_model"] else ""))
        L.append("  怎么读：查资料、搜文件、读日志这类活用便宜的模型就够。没指定模型的子代理会用主会话那个最贵的。")
    elif not (rq.get("sub")):
        L.append("近 %d 天没有派过子代理。" % days)


# ---------------------------------------------------------------- 备份 / 回滚

def store_root(home):
    return os.path.join(home, STORE, "backups")


def manifest_path(home, bid):
    return os.path.join(store_root(home), bid, "manifest.json")


def all_manifests(home):
    root = store_root(home)
    out = []
    if os.path.isdir(root):
        for d in sorted(os.listdir(root)):
            m, _ = load_json_file(os.path.join(root, d, "manifest.json"))
            if isinstance(m, dict):
                out.append(m)
    return out


def backup_state(m):
    if m.get("rolled_back"):
        return "已回滚"
    return "已封存" if m.get("sealed") else "进行中"


def load_manifest(home, bid):
    m, err = load_json_file(manifest_path(home, bid))
    if not isinstance(m, dict):
        die("找不到备份 %s（%s）。用 list 看有哪些。" % (bid, err))
    return m


def save_manifest(home, m):
    p = manifest_path(home, m["id"])
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o600)
    os.replace(tmp, p)


def walk_tree(root):
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for name in sorted(dn + fn):
            if name in IGNORE_NAMES:
                continue
            p = os.path.join(dp, name)
            st = os.lstat(p)
            rel = os.path.relpath(p, root)
            if stat.S_ISLNK(st.st_mode):
                yield rel, "symlink", 0, os.readlink(p)
            elif stat.S_ISDIR(st.st_mode):
                yield rel, "dir", stat.S_IMODE(st.st_mode), ""
            elif stat.S_ISREG(st.st_mode):
                yield rel, "file", stat.S_IMODE(st.st_mode), sha256_file(p)
        # os.walk 默认不跟软链目录，符合预期


def fingerprint(path):
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return {"kind": "absent"}
    if stat.S_ISLNK(st.st_mode):
        return {"kind": "symlink", "target": os.readlink(path)}
    if stat.S_ISDIR(st.st_mode):
        h, n = hashlib.sha256(), 0
        for rel, kind, mode, val in walk_tree(path):
            h.update(("%s\0%s\0%o\0%s\n" % (rel, kind, mode, val)).encode("utf-8", "surrogateescape"))
            n += 1
        return {"kind": "dir", "mode": stat.S_IMODE(st.st_mode), "tree": h.hexdigest(), "count": n}
    if stat.S_ISREG(st.st_mode):
        return {"kind": "file", "mode": stat.S_IMODE(st.st_mode), "sha256": sha256_file(path)}
    return {"kind": "other"}


def inside(p, root):
    # normcase：Windows 上路径不分大小写、/ 和 \ 混用；mac / Linux 上它什么也不做
    p, root = os.path.normcase(p), os.path.normcase(root)
    return p == root or p.startswith(root.rstrip(os.sep) + os.sep)


def forbidden(path):
    b = os.path.basename(path).lower()
    return (b.startswith(".credentials") or b in ("auth.json", ".claude.json", ".env") or b.endswith(".env")
            or "oauth" in b)


def resolve_target(path, roots, home):
    """返回规范化后的路径（父目录解析软链，自身不解析）。不在允许范围内就退出。"""
    parent = os.path.realpath(os.path.dirname(path))
    full = os.path.join(parent, os.path.basename(path))
    if not any(inside(full, r) for r in roots):
        die("%s 不在允许写的范围内（HOME 或 backup 时用 --root 声明的目录）。" % path)
    if inside(full, os.path.join(os.path.realpath(home), STORE)):
        die("不能对备份目录自己做操作。")
    if forbidden(full):
        die("%s 是凭据或运行状态文件，这个工具不碰。" % show(full, home))
    return full


def is_reparse(p):
    """软链，或 Windows 的目录联接等重解析点（Python 3.12 以前 islink 认不出 junction）。"""
    try:
        st = os.lstat(p)
    except OSError:
        return False
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_file_attributes", 0) & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT


def windows_link_inside(p):
    """p 本身或它目录里面有没有软链 / 联接。返回第一个找到的，没有返回 None。"""
    if is_reparse(p):
        return p
    if os.path.isdir(p):
        for dp, dn, fn in os.walk(p):
            for n in dn + fn:
                q = os.path.join(dp, n)
                if is_reparse(q):
                    return q
            dn[:] = [d for d in dn if not is_reparse(os.path.join(dp, d))]
    return None


def entry_for(m, path):
    for i, e in enumerate(m["entries"]):
        if os.path.normcase(e["path"]) == os.path.normcase(path):
            return i, e
    return None, None


def require_open(m):
    if m.get("rolled_back"):
        die("备份 %s 已经回滚过，不能再往里加改动。新开一个 backup。" % m["id"])
    if m.get("sealed"):
        die("备份 %s 已封存。要继续改，新开一个 backup。" % m["id"])


def cmd_backup(args, home):
    rhome = os.path.realpath(home)
    roots = [rhome] + [os.path.realpath(expand(r, home)) for r in (args.root or [])]
    roots += [os.path.realpath(d) for d in (CONF["claude"], CONF["codex"]) if d and not any(inside(os.path.realpath(d), r) for r in roots)]
    paths = []
    for p in args.paths:
        full = resolve_target(expand(p, home), roots, home)
        if full not in paths:
            paths.append(full)
    if is_windows():
        for p in paths:
            q = windows_link_inside(p)
            if q:
                die("%s 是软链或目录联接（或者里面有）。Windows 上备份、回滚这类东西的行为没有验证过，"
                    "回滚可能把联接变成一份普通拷贝，已拒绝。只备份里面的普通文件，或手动改。" % show(q, home))
    # 软链指向的真实文件：在允许范围内就一并备份
    extra, notes = [], []
    for p in paths:
        if os.path.islink(p):
            real = os.path.realpath(p)
            if any(inside(real, r) for r in roots) and os.path.isfile(real) and not forbidden(real):
                if real not in paths and real not in extra:
                    extra.append(real)
                notes.append("%s 是软链，真实文件 %s 也一并备份了；要改内容请改真实文件。" % (show(p, home), show(real, home)))
            else:
                notes.append("%s 是软链，指向 %s，在允许范围之外。这个工具不改它指向的内容。" % (show(p, home), os.readlink(p)))
    paths += extra
    for a in paths:
        for b in paths:
            if a != b and inside(a, b):
                die("%s 在 %s 里面，两个不能同时列。只列外层那个。" % (show(a, home), show(b, home)))

    root = store_root(home)
    os.makedirs(root, mode=0o700, exist_ok=True)
    os.chmod(os.path.join(home, STORE), 0o700)
    os.chmod(root, 0o700)
    base = time.strftime("%Y%m%d-%H%M%S")
    bid, n = base, 1
    while True:
        try:
            os.makedirs(os.path.join(root, bid), mode=0o700)
            break
        except FileExistsError:
            n += 1
            bid = "%s-%d" % (base, n)
    bdir = os.path.join(root, bid)
    entries = []
    for i, p in enumerate(paths):
        fp = fingerprint(p)
        if fp["kind"] == "other":
            die("%s 不是普通文件、目录或软链。" % p)
        dst = os.path.join(bdir, "pre", str(i))
        if fp["kind"] == "file":
            os.makedirs(dst, mode=0o700)
            shutil.copy2(p, os.path.join(dst, "blob"))
        elif fp["kind"] == "dir":
            os.makedirs(dst, mode=0o700)
            shutil.copytree(p, os.path.join(dst, "tree"), symlinks=True)
        entries.append({"path": p, "pre": fp})
    m = {"id": bid, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "note": args.note or "",
         "home": rhome, "roots": roots, "entries": entries, "created_dirs": [], "ops": [],
         "sealed": None, "rolled_back": None, "tool_version": VERSION}
    save_manifest(home, m)
    print("备份 %s 已建好：%s" % (bid, show(bdir, home)))
    for e in entries:
        print("  - %s [%s]" % (show(e["path"], home), {"file": "文件", "dir": "目录", "symlink": "软链", "absent": "现在不存在，回滚时会移走新建的"}[e["pre"]["kind"]]))
    for nline in notes:
        print("注意：" + nline)
    print("备份里是原样拷贝，可能含凭据，目录权限 0700。不要提交或同步出去。")
    print("回滚：python3 %s rollback --backup %s" % (os.path.abspath(__file__), bid))


def struct_get(obj, path):
    cur = obj
    for k in path:
        if isinstance(k, dict):
            if not isinstance(cur, list):
                return MISSING
            hit = [x for x in cur if isinstance(x, dict) and all(x.get(a) == b for a, b in k.items())]
            if not hit:
                return MISSING
            cur = hit[0]
        else:
            if not isinstance(cur, dict) or k not in cur:
                return MISSING
            cur = cur[k]
    return cur


def struct_apply(obj, path, value, delete):
    cur = obj
    for idx, k in enumerate(path[:-1]):
        nxt = path[idx + 1]
        if isinstance(k, dict):
            hit = [x for x in cur if isinstance(x, dict) and all(x.get(a) == b for a, b in k.items())]
            if hit:
                cur = hit[0]
            elif delete:
                return
            else:
                new = dict(k)
                cur.append(new)
                cur = new
        else:
            if k not in cur:
                if delete:
                    return
                cur[k] = [] if isinstance(nxt, dict) else {}
            cur = cur[k]
            want = list if isinstance(nxt, dict) else dict
            if not isinstance(cur, want):
                die("路径 %s 处的现有值类型对不上，没有改。" % json.dumps(path[:idx + 1], ensure_ascii=False))
    if delete:
        cur.pop(path[-1], None)
    else:
        cur[path[-1]] = value


def split_newlines(text, kind):
    """返回 (原文的换行符, 换行统一成 \\n 的文本)。改完再换回去，CRLF 文件不会变成 LF。
    CRLF 和 LF 混用、或有单独的 \\r 的，判断不了该用哪种，拒绝。"""
    crlf = text.count("\r\n")
    if (crlf and crlf != text.count("\n")) or "\r" in text.replace("\r\n", ""):
        die("这个 %s 文件里 CRLF 和 LF 换行混用，脚本改完没法保证其余字节不变，没有改。请手动改，改动仍在备份保护内。" % kind)
    return ("\r\n" if crlf else "\n"), (text.replace("\r\n", "\n") if crlf else text)


def json_edit(text, path, value, delete):
    if any(isinstance(k, dict) for k in path[-1:]):
        die("--path 的最后一项必须是键名。")
    nl, text = split_newlines(text, "JSON")
    try:
        obj = json.loads(text) if text.strip() else {}
    except ValueError as e:
        die("这个 JSON 文件解析不了（%s），没有改。可能带注释，请手动改。" % e)
    if not isinstance(obj, dict):
        die("JSON 顶层不是对象，没有改。")
    old = struct_get(obj, path)
    expected = copy.deepcopy(obj)
    struct_apply(expected, path, value, delete)
    m = re.search(r'\n([ \t]+)"', text)
    indent = m.group(1) if m else "  "
    indent = "\t" if indent.startswith("\t") else len(indent)
    ascii_only = bool(text) and all(ord(ch) < 128 for ch in text)
    tail = "\n" if text.endswith("\n") or not text else ""
    # 整份重写，只有原文本来就是这个格式时，目标键以外的字节才不会变；不是就不改
    if text.strip() and json.dumps(obj, indent=indent, ensure_ascii=ascii_only) + tail != text:
        die("这个 JSON 文件的排版和脚本写出的格式不一样（比如手工排的版），改一个键会连带改动别处，没有改。"
            "请手动改，改动仍在备份保护内。")
    new = json.dumps(expected, indent=indent, ensure_ascii=ascii_only) + tail
    if json.loads(new) != expected:
        die("写出的 JSON 校验没过，没有改。")
    return new.replace("\n", nl), old


def toml_literal(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list) and all(not isinstance(i, (dict, list)) for i in v):
        return "[" + ", ".join(toml_literal(i) for i in v) + "]"
    die("TOML 只支持写入标量和标量数组。")


def toml_key(k):
    return k if re.fullmatch(r"[A-Za-z0-9_-]+", k) else json.dumps(k, ensure_ascii=False)


def toml_edit(text, path, value, delete):
    if tomllib is None:
        die("这个 Python 没有 tomllib（要 3.11 以上），改不了 TOML。请手动改，改动仍在备份保护内。")
    sel_at = [i for i, k in enumerate(path) if isinstance(k, dict)]
    if len(sel_at) > 1 or (sel_at and sel_at[0] != len(path) - 2) or isinstance(path[-1], dict):
        die("TOML 的 --path 只支持：表路径 + 键名，或 表路径 + {选择条件} + 键名。")
    table = path[:sel_at[0]] if sel_at else path[:-1]
    sel = path[sel_at[0]] if sel_at else None
    key = path[-1]
    nl, text = split_newlines(text, "TOML")
    try:
        old_obj = tomllib.loads(text)
    except Exception as e:
        die("这个 TOML 文件解析不了（%s），没有改。" % e)
    old = struct_get(old_obj, path)
    expected = copy.deepcopy(old_obj)
    struct_apply(expected, path, value, delete)

    lines = text.split("\n")
    heads = []
    for i, ln in enumerate(lines):
        m = HEADER_RE.match(ln)
        if m and len(m.group(1)) == len(m.group(3)):
            heads.append((i, m.group(1) == "[[", _split_key(m.group(2))))
    bounds = [h[0] for h in heads] + [len(lines)]

    def kv(line):
        try:
            return tomllib.loads(line)
        except Exception:
            return None

    seg = None
    if not table and sel is None:
        seg = (0, bounds[0], None)
    else:
        for n, (i, is_arr, parts) in enumerate(heads):
            if parts != table or is_arr != (sel is not None):
                continue
            start, end = i + 1, bounds[n + 1]
            if sel is not None:
                body = {}
                for ln in lines[start:end]:
                    d = kv(ln)
                    if d:
                        body.update(d)
                if not all(body.get(a) == b for a, b in sel.items()):
                    continue
            seg = (start, end, i)
            break

    newline = "%s = %s" % (toml_key(key), None if delete else toml_literal(value))
    if seg is None:
        if delete:
            return text.replace("\n", nl), old
        head = ".".join(toml_key(p) for p in table)
        block = ["[[%s]]" % head if sel is not None else "[%s]" % head]
        for a, b in (sel or {}).items():
            block.append("%s = %s" % (toml_key(a), toml_literal(b)))
        block.append(newline)
        body = text if text.endswith("\n") or not text else text + "\n"
        new = body + ("\n" if body.strip() else "") + "\n".join(block) + "\n"
    else:
        start, end, _h = seg
        hit = None
        for j in range(start, end):
            d = kv(lines[j])
            if d is not None and list(d.keys()) == [key]:
                hit = j
                break
            if re.match(r"^\s*(%s|%s)\s*=" % (re.escape(key), re.escape(json.dumps(key))), lines[j]) and d is None:
                die("%s 现在的值跨多行，脚本不改这种，请手动改。" % key)
        if delete:
            if hit is None:
                return text.replace("\n", nl), old
            del lines[hit]
        elif hit is not None:
            lines[hit] = re.match(r"^\s*", lines[hit]).group(0) + newline
        else:
            at = start
            if _h is None:  # 顶层：插在顶层键的最后一行后面
                at = start
                for j in range(start, end):
                    if lines[j].strip():
                        at = j + 1
            lines.insert(at, newline)
        new = "\n".join(lines)
    try:
        got = tomllib.loads(new)
    except Exception as e:
        die("改完的 TOML 解析不了（%s），文件没动。请手动改。" % e)
    if got != expected:
        die("改完的 TOML 和预期不一致，文件没动。请手动改。")
    return new.replace("\n", nl), old


def track_makedirs(m, d):
    made = []
    while d and not os.path.isdir(d):
        made.append(d)
        d = os.path.dirname(d)
    for p in reversed(made):
        os.mkdir(p)
        m["created_dirs"].append(p)


def atomic_write(path, text, mode):
    # 先写临时文件再整体替换：任何一步失败，原文件都还是原样，临时文件删掉，不留半截
    tmp = path + ".save-my-tokens-tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        if isinstance(e, PermissionError):
            die("写 %s 被拒绝（%s）。Windows 上多半是文件正被别的程序占用（Claude Code、Codex、编辑器、杀毒软件），"
                "或者文件是只读的。原文件没动。关掉占用它的程序后再试。" % (path, e))
        die("写 %s 失败（%s），原文件没动。" % (path, e))


def redacted(path, v):
    if v is MISSING:
        return "（无）"
    if any(isinstance(k, str) and SECRET_RE.search(k) for k in path):
        return "<已遮掉>"
    return clip(json.dumps(v, ensure_ascii=False), 80)


def check_path(path):
    if not isinstance(path, list) or not path or not all(isinstance(k, (str, dict)) for k in path):
        die("--path 要写成 JSON 数组，元素是键名（字符串）或选择条件（对象）。")


def cmd_set(args, home):
    many = getattr(args, "many", None)
    if many:
        args.many = many
        if args.path or args.value is not None or args.delete:
            die("--many 和 --path / --value / --delete 不能一起用。")
        try:
            with open(args.many, "r", encoding="utf-8-sig") as f:
                items = json.load(f)
        except (OSError, ValueError) as e:
            die("--many 的文件读不了或不是 JSON：%s" % e)
        if not isinstance(items, list) or not items:
            die("--many 的文件要是一个 JSON 数组，每项形如 {\"path\": [...], \"value\": ...} 或 {\"path\": [...], \"delete\": true}。")
        edits = []
        for it in items:
            if not isinstance(it, dict) or ("value" in it) == bool(it.get("delete")):
                die("--many 里每一项要有 path，再加 value 或 \"delete\": true 其中一个。")
            check_path(it.get("path"))
            edits.append((it["path"], it.get("value"), bool(it.get("delete"))))
        return apply_edits(home, args.backup, args.file, edits)
    if not args.path:
        die("要给 --path（改一个键），或 --many（一次改很多个键）。")
    try:
        path = json.loads(args.path)
    except ValueError:
        die("--path 要写成 JSON 数组，例如 '[\"skillOverrides\",\"deploy\"]'。")
    check_path(path)
    if args.delete == (args.value is not None):
        die("--value 和 --delete 二选一。")
    value = None
    if not args.delete:
        try:
            value = json.loads(args.value)
        except ValueError:
            die("--value 要写成 JSON，例如 '\"off\"'、false、350000。")
    apply_edits(home, args.backup, args.file, [(path, value, bool(args.delete))])


SKILL_STATES = {"off": "off", "关掉": "off", "manual": "user-invocable-only", "user-invocable-only": "user-invocable-only",
                "只能手动调": "user-invocable-only", "name": "name-only", "name-only": "name-only", "只留名字": "name-only",
                "on": "on", "保留": "on"}


def group_members(scan_path, group):
    ev, err = load_json_file(scan_path)
    if not isinstance(ev, dict) or "claude" not in ev:
        die("%s 不是 scan --json 写出的文件（%s）。" % (scan_path, err or "格式不对"))
    return [s for s in ev["claude"].get("skills") or [] if s.get("group") == group.upper()], ev


def cmd_skills(args, home):
    """一次改很多个 skill 的状态：整组，或点名的几个。只动 settings.json 的 skillOverrides，skill 文件不碰。"""
    state = SKILL_STATES.get(args.state)
    if not state:
        die("--state 取 off（关掉）、manual（只能手动调）、name（只留名字）、on（保留）之一。")
    names = list(args.names or [])
    # 点名的名字先核对一遍：拼错的名字写进 skillOverrides 不会报错，只会悄悄不生效
    known = None
    if args.scan:
        ev0, err = load_json_file(args.scan)
        if not isinstance(ev0, dict) or "claude" not in ev0:
            die("%s 不是 scan --json 写出的文件（%s）。" % (args.scan, err or "格式不对"))
        known = set(s["name"] for s in ev0["claude"].get("skills") or [])
    else:
        sd = os.path.join(claude_dir(home), "skills")
        if os.path.isdir(sd):
            known = set(os.listdir(sd))
            cur, _e = load_json_file(os.path.join(claude_dir(home), "settings.json"))
            if isinstance(cur, dict) and isinstance(cur.get("skillOverrides"), dict):
                known |= set(cur["skillOverrides"])
    if known is not None:
        bad = [n for n in names if n not in known]
        if bad:
            die("找不到这些 skill：%s。没有改。检查拼写；项目级、插件里的 skill 加 --scan <json> 按扫描到的名单核对；Claude Code 内置的 skill 用 slim set 改 skillOverrides。" % "、".join(bad))
    if args.group:
        if not args.scan:
            die("用 --group 要同时给 --scan <scan --json 写出的文件>。")
        if args.group.upper() not in ("A", "B", "C", "D"):
            die("--group 取 A、B、C、D 之一。E 组是在用的，不整组改；要改其中某个就点名。")
        members, _ev = group_members(args.scan, args.group)
        names += [s["name"] for s in members]
    skip = set(args.exclude or [])
    stray = [n for n in skip if n not in names]
    if stray:
        die("--exclude 里的 %s 不在这次要改的名单里（是不是拼错了）。没有改。" % "、".join(sorted(stray)))
    names = [n for i, n in enumerate(names) if n not in skip and n not in names[:i]]
    if not names:
        die("没有要改的 skill：给名字，或给 --scan 加 --group。")
    edits = [(["skillOverrides", n], state, False) for n in names]
    apply_edits(home, args.backup, os.path.join(claude_dir(home), "settings.json"), edits,
                summary="%d 个 skill 改成 %s" % (len(names), state))


def cmd_show(args, home):
    """从上次 scan 的 json 里取一组 skill 的完整名单，不用重扫。"""
    members, ev = group_members(args.scan, args.group)
    title = dict((g, t) for g, t, _a in SKILL_GROUPS).get(args.group.upper())
    if not title:
        die("--group 取 A、B、C、D、E 之一。")
    members.sort(key=lambda s: (-s["desc_chars"], s["dir"]))
    if args.names:
        print(" ".join(s["name"] for s in members))
        return
    print("%s 组 %d 个：%s（近 %d 天）" % (args.group.upper(), len(members), title, ev.get("days", 30)))
    for s in members:
        bits = ["描述 %d 字符" % s["desc_chars"], "手敲 %d" % s["user_calls"], "模型调 %d" % s["model_calls"]]
        if s.get("codex_reads"):
            bits.append("Codex 读 %d" % s["codex_reads"])
        if s.get("flags"):
            bits.append("⚠ " + "；".join(s["flags"]))
        if s.get("referenced_by"):
            bits.append("引用它的：" + "、".join(show(p, home) for p in s["referenced_by"][:2]))
        print("  - %s [%s]" % (s["name"], "，".join(bits)))


def apply_edits(home, backup_id, file_arg, edits, summary=None):
    """对同一个 JSON / TOML 文件做一批改动，全部成功才写回一次；任何一项被拒，文件不动。"""
    for path, value, delete in edits:
        if path == ["autoCompactWindow"] and not delete and not (isinstance(value, int) and not isinstance(value, bool) and 100000 <= value <= 1000000):
            die("autoCompactWindow 要是 100000 到 1000000 之间的整数，收到的是 %s。没有改。" % json.dumps(value, ensure_ascii=False))
    m = load_manifest(home, backup_id)
    require_open(m)
    full = resolve_target(expand(file_arg, home), m["roots"], home)
    _i, e = entry_for(m, full)
    if e is None:
        die("%s 不在备份 %s 里。先把它加进一个新的 backup 再改。" % (show(full, home), m["id"]))
    if os.path.islink(full):
        die("%s 是软链。要改就改它指向的真实文件（并确保真实文件在备份里）。" % show(full, home))
    if e["pre"]["kind"] not in ("file", "absent"):
        die("%s 不是文件。" % show(full, home))
    exists = os.path.isfile(full)
    text = ""
    if exists:
        try:
            # newline=""：原样读进 CRLF，改完原样写回
            with open(full, "r", encoding="utf-8", newline="") as f:
                text = f.read()
        except UnicodeDecodeError:
            die("%s 不是 UTF-8 编码（可能是 GBK），脚本不改，请手动改。" % show(full, home))
    bom = chr(0xFEFF) if text.startswith(chr(0xFEFF)) else ""   # Windows 记事本可能加 BOM，原样保留
    body = text[len(bom):]
    if not (full.endswith(".toml") or full.endswith(".json")):
        die("set 只改 .json 和 .toml。别的文件请直接编辑，改动仍在备份保护内。")
    edit = toml_edit if full.endswith(".toml") else json_edit
    done = []
    for path, value, delete in edits:
        before = body
        body, old = edit(body, path, value, delete)
        label = ".".join(k if isinstance(k, str) else json.dumps(k, ensure_ascii=False) for k in path)
        if body != before:
            done.append((path, label, old, value, delete))
    if not done:
        print("没有变化：%s 里%s已经是这个值。" % (show(full, home), " " + label + " " if len(edits) == 1 else "这 %d 项" % len(edits)))
        return
    mode = stat.S_IMODE(os.lstat(full).st_mode) if exists else 0o600
    track_makedirs(m, os.path.dirname(full))
    atomic_write(full, bom + body, mode)
    for path, label, old, value, delete in done:
        m["ops"].append({"op": "set", "file": full, "path": path, "delete": bool(delete),
                         "old": redacted(path, old), "new": "（删除）" if delete else redacted(path, value)})
    save_manifest(home, m)
    if len(edits) == 1:
        path, label, old, value, delete = done[0]
        print("已改 %s：%s  %s → %s" % (show(full, home), label, redacted(path, old), "（删除）" if delete else redacted(path, value)))
        return
    same = len(edits) - len(done)
    print("已改 %s：%s%s，一次写回。" % (show(full, home), summary or "%d 项" % len(edits),
                                  "，其中 %d 项本来就是这个值，实际变了 %d 项" % (same, len(done)) if same else ""))
    for path, label, old, value, delete in done[:12]:
        print("  %s  %s → %s" % (label, redacted(path, old), "（删除）" if delete else redacted(path, value)))
    if len(done) > 12:
        print("  …还有 %d 项，完整清单看 slim list" % (len(done) - 12))


def cmd_move(args, home):
    m = load_manifest(home, args.backup)
    require_open(m)
    src = resolve_target(expand(args.src, home), m["roots"], home)
    dst = resolve_target(expand(args.dst, home), m["roots"], home)
    _i, es = entry_for(m, src)
    _j, ed = entry_for(m, dst)
    if es is None or ed is None:
        die("src 和 dst 都要先列进 backup 的 --paths（dst 现在不存在也要列）。dst 要写搬过去之后的完整路径，含最后那一级名字，不是它的上级目录。")
    if not os.path.lexists(src):
        die("%s 不存在。" % show(src, home))
    if os.path.lexists(dst):
        die("%s 已经存在，不覆盖。" % show(dst, home))
    track_makedirs(m, os.path.dirname(dst))
    try:
        os.rename(src, dst)
    except OSError:
        shutil.move(src, dst)
    m["ops"].append({"op": "move", "src": src, "dst": dst})
    save_manifest(home, m)
    print("已搬 %s → %s" % (show(src, home), show(dst, home)))


def describe(pre, cur):
    if pre == cur:
        return "没变"
    if pre["kind"] == "absent":
        return "新建"
    if cur["kind"] == "absent":
        return "已移走"
    return "已改"


def cmd_seal(args, home):
    m = load_manifest(home, args.backup)
    require_open(m)
    post, changed = [], 0
    print("备份 %s 封存，改动结果：" % m["id"])
    for e in m["entries"]:
        cur = fingerprint(e["path"])
        post.append(cur)
        d = describe(e["pre"], cur)
        changed += d != "没变"
        print("  - %s：%s" % (show(e["path"], home), d))
    m["sealed"] = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "post": post}
    save_manifest(home, m)
    if not changed:
        print("没有任何改动。")
    print("改动在新开的会话里生效；已经开着的会话不会变。")
    print("回滚：python3 %s rollback --backup %s" % (os.path.abspath(__file__), m["id"]))


def set_aside(path, aside_dir, idx):
    """把现在占着位置的东西挪进备份目录，不删除。"""
    if not os.path.lexists(path):
        return
    dst = os.path.join(aside_dir, str(idx))
    os.makedirs(dst, mode=0o700, exist_ok=True)
    shutil.move(path, os.path.join(dst, os.path.basename(path)))


def restore_one(p, pre, src, aside, i):
    set_aside(p, aside, i)
    if pre["kind"] == "file":
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copy2(os.path.join(src, "blob"), p)
        os.chmod(p, pre["mode"])
    elif pre["kind"] == "dir":
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copytree(os.path.join(src, "tree"), p, symlinks=True)
        os.chmod(p, pre["mode"])
    elif pre["kind"] == "symlink":
        os.makedirs(os.path.dirname(p), exist_ok=True)
        os.symlink(pre["target"], p)


def cmd_rollback(args, home):
    manifests = all_manifests(home)
    if args.backup:
        m = load_manifest(home, args.backup)
    else:
        live = [x for x in manifests if not x.get("rolled_back")]
        if not live:
            die("没有可回滚的备份。")
        m = live[-1]
    if m.get("rolled_back"):
        die("备份 %s 已经回滚过（%s）。" % (m["id"], m["rolled_back"]))
    rhome = os.path.realpath(home)
    if m.get("home") != rhome:
        die("这个备份是在 %s 下建的，现在的 HOME 是 %s，不回滚。" % (m.get("home"), rhome))
    bdir = os.path.join(store_root(home), m["id"])
    # 回滚点之后有没有被别人动过
    drift = []
    if m.get("sealed"):
        for e, post in zip(m["entries"], m["sealed"]["post"]):
            cur = fingerprint(e["path"])
            if cur != post and cur != e["pre"]:
                drift.append(e["path"])
    if drift and not args.force:
        print("停：下面这些在这次改动之后又变过，直接还原会冲掉后来的改动：")
        for p in drift:
            print("  - " + show(p, home))
            i, e = entry_for(m, p)
            if e["pre"]["kind"] == "file" and p.endswith((".md", ".markdown", ".txt")) and os.path.isfile(p):
                old = read_text(os.path.join(bdir, "pre", str(i), "blob")).splitlines()
                diff = list(difflib.unified_diff(old, read_text(p).splitlines(), "备份时", "现在", lineterm="", n=1))
                print("    从备份时到现在的全部差异（我们的改动和之后别人的改动都在里面）：")
                for ln in diff[:40]:
                    print("    " + ln)
                if len(diff) > 40:
                    print("    …共 %d 行差异" % len(diff))
        print("配置文件（json / toml）可能含凭据，这里不显示内容。")
        print("先看看后来改了什么。确认要覆盖就加 --force（被替换下来的版本会存进备份目录，不会丢）。")
        sys.exit(3)
    if not m.get("sealed"):
        print("注意：这个备份没有封存（改到一半），无法判断文件之后有没有被别人动过，按原样还原。")
    aside = os.path.join(bdir, "displaced", time.strftime("%Y%m%d-%H%M%S"))
    restored = 0
    for i in reversed(range(len(m["entries"]))):
        e = m["entries"][i]
        p, pre = e["path"], e["pre"]
        if fingerprint(p) == pre:
            continue
        try:
            restore_one(p, pre, os.path.join(bdir, "pre", str(i)), aside, i)
        except PermissionError as err:
            die("还原 %s 时被拒绝（%s）。Windows 上多半是文件正被别的程序占用（Claude Code、Codex、编辑器）。"
                "已经还原到一半，被替换下来的版本在 %s，不会丢。关掉占用它的程序后再跑一次同样的 rollback 接着还原；"
                "如果它说文件「又变过」，那是这次还原到一半造成的，加 --force。"
                % (show(p, home), err, show(aside, home)), 5)
        restored += 1
    for d in sorted(m.get("created_dirs", []), key=len, reverse=True):
        try:
            for junk in IGNORE_NAMES:
                jp = os.path.join(d, junk)
                if os.path.isfile(jp) and os.listdir(d) == [junk]:
                    set_aside(jp, aside, "dirs")
            os.rmdir(d)  # 只删这次自己建的空目录
        except OSError:
            pass
    bad = [e["path"] for e in m["entries"] if fingerprint(e["path"]) != e["pre"]]
    m["rolled_back"] = time.strftime("%Y-%m-%d %H:%M:%S")
    m["rollback_verified"] = not bad
    save_manifest(home, m)
    if bad:
        print("回滚后校验没过，下面这些和备份时不一致：")
        for p in bad:
            print("  - " + show(p, home))
        sys.exit(4)
    print("已回滚备份 %s：还原 %d 项，%d 项本来就没变。逐项校验 sha256 一致。" % (m["id"], restored, len(m["entries"]) - restored))
    if os.path.isdir(aside):
        print("被替换下来的版本存在：%s" % show(aside, home))


def cmd_list(args, home):
    ms = all_manifests(home)
    if not ms:
        print("还没有备份。")
        return
    for m in ms:
        print("%s [%s] %s  %s" % (m["id"], backup_state(m), m["created"], m.get("note") or ""))
        for e in m["entries"]:
            print("    %s" % show(e["path"], home))
        for op in m.get("ops", []):
            if op["op"] == "set":
                print("    · set %s %s：%s → %s" % (show(op["file"], home), json.dumps(op["path"], ensure_ascii=False), op["old"], op["new"]))
            else:
                print("    · move %s → %s" % (show(op["src"], home), show(op["dst"], home)))


def cmd_status(args, home):
    ev, err = load_json_file(args.scan)
    if not isinstance(ev, dict) or "files" not in ev:
        die("读不了 scan 的 JSON（%s）。先跑 scan --json 文件。" % err)
    covered = []
    for m in all_manifests(home):
        if not m.get("rolled_back"):
            covered += [e["path"] for e in m["entries"]]
    changed = 0
    for p, h in sorted(ev["files"].items()):
        cur = sha256_file(p) if os.path.isfile(p) else None
        if cur == h:
            continue
        changed += 1
        rp = os.path.join(os.path.realpath(os.path.dirname(p)), os.path.basename(p))
        ok = any(inside(rp, c) or inside(os.path.realpath(p), c) for c in covered)
        print("  %s %s（%s）" % ("✓" if ok else "✗", show(p, home), ("已不在原位" if cur is None else "内容变了") + ("，有备份" if ok else "，没有备份覆盖！")))
    if not changed:
        print("自上次扫描以来，扫描过的配置和规则文件都没变。")


def cmd_compare(args, home):
    """改之前和改之后各一份 scan 的 json，对比新开会话第一次请求的实测用量。只读。"""
    evs = []
    for p in (args.before, args.after):
        ev, err = load_json_file(p)
        if not isinstance(ev, dict) or "claude" not in ev:
            die("读不了 scan 的 JSON（%s：%s）。" % (p, err))
        evs.append(ev)
    sb, sa = [(e.get("claude") or {}).get("startup") for e in evs]
    if not sb or not sa:
        die("%s那份扫描里没有新开会话的记录，比不了。新开一个会话说一句话，再 scan --json 一次。" % ("改之前" if not sb else "改之后"))
    a = sa["latest"]
    b = sb["latest"]
    if a["cwd"] != b["cwd"]:
        row = [r for r in sb.get("by_cwd") or [] if r["cwd"] == a["cwd"]]
        if row:
            b = {"ts": row[0]["latest_ts"], "cwd": a["cwd"], "tokens": row[0]["latest"], "parts": row[0]["latest_parts"], "model": None}
    if a["ts"] <= b["ts"]:
        die("改之后那份扫描里，最近一次新开会话还是改之前的那一次（%s）。改动只在新开的会话里生效：新开一个会话说一句话，再 scan --json 一次。" % md(a["ts"]))
    L = ["前后对比：新开一个会话，第一次请求带了多少（Claude Code 自己记在日志里的用量，不是估的）", ""]
    L.append("  改之前  %s token   （%s，%s%s）" % (num(b["tokens"]).rjust(9), md(b["ts"]), show(b["cwd"], home), "，" + b["model"] if b.get("model") else ""))
    L.append("  改之后  %s token   （%s，%s%s）" % (num(a["tokens"]).rjust(9), md(a["ts"]), show(a["cwd"], home), "，" + a["model"] if a.get("model") else ""))
    d = b["tokens"] - a["tokens"]
    if d > 0:
        L.append("  少了    %s token   （现在是原来的 %.0f%%）" % (num(d).rjust(9), 100.0 * a["tokens"] / b["tokens"]))
    elif d < 0:
        L.append("  多了    %s token" % num(-d).rjust(9))
    else:
        L.append("  没变")
    if a["cwd"] != b["cwd"]:
        L.append("  注意：两次不在同一个目录，项目级的规则和 skill 不一样，数字只能粗看。在同一个目录新开会话再比才准。")
    if a.get("model") and b.get("model") and a["model"] != b["model"]:
        L.append("  注意：两次用的模型不一样，同样的内容折出来的 token 数会有出入。")
    L.append("")
    L.append("各部分的大小（字符数）：")
    L.append("  %s  %s  %s" % ("改之前".rjust(8), "改之后".rjust(8), ""))
    pb, pa = b.get("parts") or {}, a.get("parts") or {}
    for key, name in PART_NAMES:
        x, y = pb.get(key, 0), pa.get(key, 0)
        if not x and not y:
            continue
        extra = ""
        if key == "skills" and b.get("skill_count") is not None and a.get("skill_count") is not None:
            extra = "（%d 个 → %d 个）" % (b["skill_count"], a["skill_count"])
        elif key == "rules" and b.get("files") is not None and a.get("files") is not None and len(b["files"]) != len(a["files"]):
            extra = "（%d 个文件 → %d 个文件）" % (len(b["files"]), len(a["files"]))
        L.append("  %s  %s  %s%s%s" % (num(x).rjust(10), num(y).rjust(10), name, extra, "" if x != y else "  没变"))
    L.append("")
    L.append("这是各一次新开会话的实测。会话越往后上下文越长，这个数只说明开局。")
    print("\n".join(L))


SELFTEST_FILES = {
    # LF、CRLF 各一份带中文的 settings.json；CRLF 的 config.toml；CRLF 的规则文件；一个 skill 目录
    ".claude/settings.json": '{\n  "env": {\n    "说明": "中文内容 ⚠ → 自检"\n  },\n  "skillOverrides": {\n    "部署": "on"\n  }\n}\n',
    ".claude/settings.local.json": '{\r\n  "env": {\r\n    "说明": "中文内容，CRLF 换行"\r\n  },\r\n  "skillOverrides": {\r\n    "部署": "on"\r\n  }\r\n}\r\n',
    ".codex/config.toml": '# 中文注释\r\nmodel = "gpt"\r\n\r\n[mcp_servers.demo]\r\ncommand = "npx"\r\nnote = "演示"\r\nenabled = true\r\n',
    ".claude/CLAUDE.md": "# 规则\r\n\r\n- 用中文回答\r\n",
    ".claude/skills/演示/SKILL.md": "---\nname: 演示\ndescription: 自检用\n---\n正文\n",
}


def selftest(out=None):
    """在系统临时目录里造一个假 HOME，用本脚本自己的 backup → set → seal → rollback 走一遍，
    校验回滚后每个文件的 sha256 和改前一样。逐步打印，返回是否全部通过。不碰真实 HOME。"""
    import contextlib
    import io
    import tempfile
    out = out or sys.stdout
    saved = dict(CONF)
    CONF.update(claude=None, codex=None)
    results = []

    def step(name, ok, detail=""):
        results.append(bool(ok))
        print("  %s  %s%s" % ("通过" if ok else "失败", name, "：" + detail if detail and not ok else ""), file=out)
        return ok

    def call(fn, home, **kw):
        o, e = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            try:
                fn(argparse.Namespace(**kw), home)
            except SystemExit as x:
                code = x.code if isinstance(x.code, int) else 1
        return code, (o.getvalue() + e.getvalue()).strip()

    def raw(p):
        with open(p, "rb") as f:
            return f.read().decode("utf-8")

    def one_line_changed(a, b, nl):
        la, lb = a.split(nl), b.split(nl)
        if nl == "\r\n" and any("\n" in x or "\r" in x for x in lb):
            return False
        if nl == "\n" and "\r" in b:
            return False
        return len(la) == len(lb) and sum(x != y for x, y in zip(la, lb)) == 1

    print("自检：在临时目录里造假 HOME，走一遍 backup → set → seal → rollback（Python %s，%s）" % (
        sys.version.split()[0], "Windows" if is_windows() else os.name), file=out)
    try:
        tmp = tempfile.mkdtemp(prefix="save-my-tokens-selftest-")
    except OSError as e:
        CONF.update(saved)
        step("在系统临时目录里建目录", False, str(e))
        print("自检没通过。", file=out)
        return False
    try:
        home = os.path.join(tmp, "home")
        for rel, text in SELFTEST_FILES.items():
            p = os.path.join(home, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(text.encode("utf-8"))
        home = os.path.realpath(home)
        P = lambda rel: os.path.join(home, *rel.split("/"))
        before = {rel: sha256_file(P(rel)) for rel in SELFTEST_FILES}
        skill_dir = P(".claude/skills/演示")
        skill_fp = fingerprint(skill_dir)
        targets = [P(".claude/settings.json"), P(".claude/settings.local.json"), P(".codex/config.toml"),
                   P(".claude/CLAUDE.md"), skill_dir]
        code, msg = call(cmd_backup, home, paths=targets, root=None, note="selftest")
        ms = all_manifests(home)
        if not step("backup 建好备份", code == 0 and len(ms) == 1, msg):
            return False
        bid = ms[0]["id"]
        for rel, nl in ((".claude/settings.json", "\n"), (".claude/settings.local.json", "\r\n")):
            pre = raw(P(rel))
            code, msg = call(cmd_set, home, backup=bid, file=P(rel), path='["skillOverrides","部署"]', value='"off"', delete=False)
            post = raw(P(rel)) if code == 0 else pre
            ok = code == 0 and json.loads(post)["skillOverrides"]["部署"] == "off" and one_line_changed(pre, post, nl)
            step("set 改 %s（%s 换行）：只变目标键那一行，换行风格不变" % (rel, "CRLF" if nl == "\r\n" else "LF"), ok, msg or "其余字节变了")
        if tomllib:
            rel = ".codex/config.toml"
            pre = raw(P(rel))
            code, msg = call(cmd_set, home, backup=bid, file=P(rel), path='["mcp_servers","demo","enabled"]', value="false", delete=False)
            post = raw(P(rel)) if code == 0 else pre
            ok = code == 0 and tomllib.loads(post)["mcp_servers"]["demo"]["enabled"] is False and one_line_changed(pre, post, "\r\n")
            step("set 改 %s（CRLF 换行）：只变目标键那一行，换行风格不变" % rel, ok, msg or "其余字节变了")
        else:
            print("  跳过  set 改 config.toml：这个 Python 没有 tomllib，TOML 修改本来就会拒绝", file=out)
        with open(P(".claude/CLAUDE.md"), "ab") as f:
            f.write("- 自检加的一行\r\n".encode("utf-8"))
        with open(os.path.join(skill_dir, "SKILL.md"), "ab") as f:
            f.write("自检加的一行\n".encode("utf-8"))
        code, msg = call(cmd_seal, home, backup=bid)
        step("seal 封存", code == 0, msg)
        changed = [rel for rel in SELFTEST_FILES if sha256_file(P(rel)) != before[rel]]
        step("改动确实落到了文件上", len(changed) == len(SELFTEST_FILES) - (0 if tomllib else 1), "只变了 %s" % changed)
        code, msg = call(cmd_rollback, home, backup=bid, force=False)
        step("rollback 回滚", code == 0, msg)
        bad = [rel for rel in SELFTEST_FILES if not os.path.isfile(P(rel)) or sha256_file(P(rel)) != before[rel]]
        step("回滚后每个文件的 sha256 和改前一致", not bad, "不一致：%s" % bad)
        step("回滚后 skill 目录和改前一致", fingerprint(skill_dir) == skill_fp)
        left = [os.path.join(dp, f) for dp, _d, fn in os.walk(home) for f in fn if f.endswith(".save-my-tokens-tmp")]
        step("没有留下半截的临时文件", not left, "%s" % left)
    except Exception as e:  # 自检本身出意外也算没通过，不往外抛
        step("自检过程", False, "%s: %s" % (type(e).__name__, e))
    finally:
        CONF.update(saved)
        shutil.rmtree(tmp, ignore_errors=True)
        step("清理临时目录", not os.path.exists(tmp), tmp)
    ok = bool(results) and all(results)
    print("自检%s。" % ("全部通过" if ok else "没通过"), file=out)
    return ok


def resolve_home(args):
    """返回 HOME。没显式给 --home 时，按 CLAUDE_CONFIG_DIR / CODEX_HOME 定配置目录。"""
    if args.home:
        return args.home
    home = os.environ.get("HOME")
    if is_windows():
        # 官方文档：Windows 上 ~/.claude 指 %USERPROFILE%\.claude
        up = os.environ.get("USERPROFILE")
        if up:
            if home and os.path.normcase(os.path.abspath(home)) != os.path.normcase(os.path.abspath(up)):
                print("注意：HOME（%s）和 USERPROFILE（%s）不一样，按 USERPROFILE 算；不对就用 --home 指定。" % (home, up), file=sys.stderr)
            home = up
    for key, var in (("claude", "CLAUDE_CONFIG_DIR"), ("codex", "CODEX_HOME")):
        v = os.environ.get(var)
        if not v:
            continue
        if not os.path.isabs(v):
            die("环境变量 %s=%r 不是绝对路径，判断不了它实际指哪个目录。改成绝对路径，或用 --home 指定。" % (var, v))
        CONF[key] = os.path.abspath(v)
        print("注意：按环境变量 %s 读写配置目录 %s。" % (var, CONF[key]), file=sys.stderr)
    if CONF["claude"]:
        print("注意：设了 CLAUDE_CONFIG_DIR 后 .claude.json 放在哪，官方文档没写清，这次不读它（skillUsage 和用户级 MCP 不核对）。", file=sys.stderr)
    elif home:
        s, _ = load_json_file(os.path.join(home, ".claude", "settings.json"))
        if isinstance(s, dict) and isinstance(s.get("env"), dict) and s["env"].get("CLAUDE_CONFIG_DIR"):
            print("注意：~/.claude/settings.json 的 env 里设了 CLAUDE_CONFIG_DIR，但当前环境变量里没有；"
                  "Claude Code 实际用的配置目录可能不是 ~/.claude，这次仍按 ~/.claude 算。", file=sys.stderr)
    return home


def main():
    utf8_console()
    ap = argparse.ArgumentParser(prog="slim.py", description="coding agent 配置体检：取证、备份、回滚。")
    ap.add_argument("--home", help="把哪个目录当 HOME（默认用环境变量 HOME）")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("scan", help="只读扫描")
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--project", action="append", help="额外要查的项目目录，可重复")
    s.add_argument("--max-projects", type=int, default=8, help="按近期会话数自动取前几个项目")
    s.add_argument("--json", help="把完整证据写到这个文件")
    s.add_argument("--now", help="把哪个时刻当作现在（ISO 格式，测试用）")
    s.add_argument("--cc-version", help="Claude Code 版本（默认从日志里取）")
    s.add_argument("--all", action="store_true", help="列表不截断")
    b = sub.add_parser("backup", help="改之前先备份")
    b.add_argument("--paths", nargs="+", required=True)
    b.add_argument("--root", action="append", help="HOME 之外允许动的项目目录，可重复")
    b.add_argument("--note")
    t = sub.add_parser("set", help="改 JSON / TOML 的一个键")
    t.add_argument("--backup", required=True)
    t.add_argument("--file", required=True)
    t.add_argument("--path", help="JSON 数组")
    t.add_argument("--value", help="JSON 值")
    t.add_argument("--delete", action="store_true")
    t.add_argument("--many", help="一次改很多个键：一个 JSON 文件，内容是 [{\"path\": [...], \"value\": ...}, ...]")
    sk = sub.add_parser("skills", help="一次改很多个 skill 的状态（只写 skillOverrides，skill 文件不动）")
    sk.add_argument("--backup", required=True)
    sk.add_argument("--state", required=True, help="off 关掉 / manual 只能手动调 / name 只留名字 / on 保留")
    sk.add_argument("names", nargs="*", help="skill 名字")
    sk.add_argument("--scan", help="scan --json 写出的文件，配合 --group 用")
    sk.add_argument("--group", help="整组一起改：A、B、C、D")
    sk.add_argument("--exclude", nargs="*", help="组里要跳过的 skill")
    sh = sub.add_parser("show", help="从 scan 的 json 里取一组 skill 的完整名单")
    sh.add_argument("--scan", required=True)
    sh.add_argument("--group", required=True)
    sh.add_argument("--names", action="store_true", help="只打印名字")
    mv = sub.add_parser("move", help="搬文件或目录")
    mv.add_argument("--backup", required=True)
    mv.add_argument("--src", required=True)
    mv.add_argument("--dst", required=True)
    se = sub.add_parser("seal", help="改完后封存")
    se.add_argument("--backup", required=True)
    rb = sub.add_parser("rollback", help="还原")
    rb.add_argument("--backup", help="不给就回滚最近一个还没回滚的")
    rb.add_argument("--force", action="store_true")
    sub.add_parser("list", help="列出备份")
    stt = sub.add_parser("status", help="对比上次 scan")
    stt.add_argument("--scan", required=True)
    cp = sub.add_parser("compare", help="两份 scan 的 json 对比开局用量")
    cp.add_argument("--before", required=True)
    cp.add_argument("--after", required=True)
    sub.add_parser("selftest", help="在临时目录里自检 backup → set → seal → rollback，不碰真实配置")
    args = ap.parse_args()
    if args.cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    if is_windows() and args.cmd == "move":
        die("Windows 上不支持 move：目录联接（junction）和软链在 Windows 上搬动、回滚的行为没有验证过，"
            "可能搬走或还原错东西。需要搬的请手动操作，或只用 scan 看报告。")
    home = resolve_home(args)
    if not home or not os.path.isdir(home):
        die("HOME 无效：%r" % home)
    home = os.path.abspath(home)
    if is_windows() and args.cmd == "backup":
        print("Windows：备份前先在这台机器上自检一遍。", file=sys.stderr)
        if not selftest(out=sys.stderr):
            die("自检没通过，这台机器上 backup / set / rollback 不安全，已拒绝。只用 scan 看报告，改动请手动做。")
    fn = {"scan": do_scan, "backup": cmd_backup, "set": cmd_set, "move": cmd_move, "seal": cmd_seal,
          "rollback": cmd_rollback, "list": cmd_list, "status": cmd_status,
          "skills": cmd_skills, "show": cmd_show, "compare": cmd_compare}.get(args.cmd)
    if not fn:
        ap.print_help()
        sys.exit(1)
    fn(args, home)


if __name__ == "__main__":
    main()
