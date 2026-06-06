(function () {
  const report = window.SKILL_MANAGER_REPORT || null;

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  const state = {
    query: "",
    status: "needs-action"
  };

  const statusMeta = {
    linked: { label: "软链共享", className: "is-ok" },
    identical: { label: "实体重复", className: "is-warn" },
    conflict: { label: "同名冲突", className: "is-danger" },
    unique: { label: "单独存在", className: "is-info" }
  };

  const actionMeta = {
    conflict: { label: "冲突", className: "is-danger" },
    identical: { label: "重复", className: "is-warn" },
    "broken-symlink": { label: "坏链", className: "is-danger" },
    "codex-only": { label: "Codex Only", className: "is-warn" },
    "claude-only": { label: "Claude Only", className: "is-warn" },
    mismatch: { label: "不一致", className: "is-danger" }
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatNumber(value) {
    return Number(value || 0).toLocaleString("zh-CN");
  }

  function formatDate(value) {
    if (!value) return "未生成扫描数据";
    return new Intl.DateTimeFormat("zh-CN", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    }).format(new Date(value));
  }

  function pill(label, className = "is-info") {
    return `<span class="pill ${className}">${escapeHtml(label)}</span>`;
  }

  function statusPill(status) {
    const meta = statusMeta[status] || statusMeta.unique;
    return pill(meta.label, meta.className);
  }

  function actionPill(type) {
    const meta = actionMeta[type] || { label: type, className: "is-info" };
    return pill(meta.label, meta.className);
  }

  function recommendation(group) {
    if (group.status === "linked") return "正常共享，无需处理";
    if (group.status === "identical") return "保留一个实体，其余入口改软链";
    if (group.status === "conflict") return "先 diff，再决定主版本";
    return "已纳入库存，可按需共享";
  }

  function copyText(text) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text);
  }

  function renderHero() {
    const health = report.health || {};
    const sync = health.codexClaudeSync || {};
    const isHealthy = health.status === "healthy";
    const title = isHealthy ? "同步健康" : "需要处理";
    const detail = isHealthy
      ? "Codex 与 Claude 技能集一致，watcher 已接管后续同步。"
      : "存在需要处理的同步、冲突或链接问题。";

    $("#healthHero").innerHTML = `
      <div class="hero-copy">
        <p class="eyebrow">Skill Health</p>
        <h2>${title}</h2>
        <p>${detail}</p>
      </div>
      <div class="hero-score ${isHealthy ? "is-healthy" : "is-attention"}">
        <span>${isHealthy ? "OK" : "FIX"}</span>
        <strong>${formatNumber(health.actionCount)}</strong>
        <small>待处理项</small>
      </div>
    `;

    $("#generatedAt").textContent = `扫描：${formatDate(report.generatedAt)}`;
    $("#syncLine").innerHTML = `
      Codex ${formatNumber(sync.leftNames)} / Claude ${formatNumber(sync.rightNames)}
      <span>差异 ${formatNumber((sync.leftOnly || []).length + (sync.rightOnly || []).length)}</span>
      <span>内容不一致 ${formatNumber((sync.mismatched || []).length)}</span>
    `;
  }

  function renderMetrics() {
    const summary = report.summary;
    const health = report.health || {};
    const sync = health.codexClaudeSync || {};
    const items = [
      { label: "唯一技能", value: summary.uniqueNames, tone: "neutral" },
      { label: "同步共享", value: summary.linkedNames, tone: "ok" },
      { label: "实体重复", value: summary.physicalDuplicateNames, tone: summary.physicalDuplicateNames ? "warn" : "ok" },
      { label: "坏软链", value: (health.brokenSymlinks || []).length, tone: (health.brokenSymlinks || []).length ? "danger" : "ok" },
      { label: "Codex-only", value: (sync.leftOnly || []).length, tone: (sync.leftOnly || []).length ? "warn" : "ok" },
      { label: "Claude-only", value: (sync.rightOnly || []).length, tone: (sync.rightOnly || []).length ? "warn" : "ok" }
    ];

    $("#metricGrid").innerHTML = items
      .map((item) => `
        <article class="metric is-${item.tone}">
          <p class="label">${escapeHtml(item.label)}</p>
          <p class="value">${formatNumber(item.value)}</p>
        </article>
      `)
      .join("");
  }

  function renderChecks() {
    const checks = report.health?.checks || [];
    $("#checkList").innerHTML = checks
      .map((check) => `
        <article class="check-item ${check.ok ? "is-ok-check" : "is-bad-check"}">
          <span class="check-dot">${check.ok ? "✓" : "!"}</span>
          <div>
            <strong>${escapeHtml(check.label)}</strong>
            <p>${check.ok ? "正常" : "需要处理"}</p>
          </div>
        </article>
      `)
      .join("");
  }

  function renderRoots() {
    $("#rootGrid").innerHTML = report.roots
      .map((root) => {
        const real = Math.max(0, root.total - root.symlinks);
        return `
          <article class="root-row">
            <div>
              <strong>${escapeHtml(root.label)}</strong>
              <p>${formatNumber(root.total)} 入口 · ${formatNumber(root.symlinks)} 软链 · ${formatNumber(real)} 实体</p>
            </div>
            <code>${escapeHtml(root.path)}</code>
          </article>
        `;
      })
      .join("");
  }

  function renderActions() {
    const actions = report.health?.actionItems || [];
    $("#actionCount").textContent = `${formatNumber(actions.length)} 项`;
    $("#actionList").innerHTML = actions.length
      ? actions.slice(0, 32).map((item) => `
          <article class="action-item">
            <div>
              ${actionPill(item.type)}
              <strong>${escapeHtml(item.title)}</strong>
            </div>
            <p>${escapeHtml(item.detail)}</p>
          </article>
        `).join("")
      : `
        <article class="empty-state">
          <strong>没有待处理项</strong>
          <p>当前没有冲突、实体重复、坏链或 Codex / Claude 差异。</p>
        </article>
      `;
  }

  function renderWatcher() {
    const watcher = report.health?.watcher || {};
    const ok = watcher.installed && watcher.loaded && watcher.watching && watcher.lastExitCode === 0;
    $("#watcherPanel").innerHTML = `
      <article class="watcher-card ${ok ? "is-ready" : "is-warning"}">
        <div>
          <p class="eyebrow">Auto Sync</p>
          <h3>${ok ? "watcher 正常运行" : "watcher 需要检查"}</h3>
          <p class="muted">${escapeHtml(watcher.lastLogLine || "暂无运行日志")}</p>
        </div>
        <div class="watcher-grid">
          <span>${pill(watcher.installed ? "已安装" : "未安装", watcher.installed ? "is-ok" : "is-danger")}</span>
          <span>${pill(watcher.loaded ? "已加载" : "未加载", watcher.loaded ? "is-ok" : "is-warn")}</span>
          <span>${pill(watcher.watching ? "监听中" : "未监听", watcher.watching ? "is-ok" : "is-warn")}</span>
          <span>${pill(`退出码 ${watcher.lastExitCode ?? "未知"}`, watcher.lastExitCode === 0 ? "is-ok" : "is-warn")}</span>
        </div>
        <code>${escapeHtml(watcher.plistPath || "")}</code>
      </article>
    `;
  }

  function renderSyncMatrix() {
    const sync = report.health?.codexClaudeSync || {};
    const columns = [
      ["Codex-only", sync.leftOnly || []],
      ["Claude-only", sync.rightOnly || []],
      ["Hash 不一致", sync.mismatched || []]
    ];
    $("#syncMatrix").innerHTML = columns
      .map(([title, items]) => `
        <article class="sync-column ${items.length ? "has-items" : ""}">
          <div class="sync-head">
            <strong>${escapeHtml(title)}</strong>
            ${pill(`${formatNumber(items.length)} 项`, items.length ? "is-warn" : "is-ok")}
          </div>
          <div class="mini-list">
            ${items.length ? items.slice(0, 16).map((item) => `<span>${escapeHtml(item)}</span>`).join("") : "<p>无差异</p>"}
          </div>
        </article>
      `)
      .join("");
  }

  function filteredGroups() {
    const q = state.query.trim().toLowerCase();
    return report.groups.filter((group) => {
      const needsAction = group.status === "conflict" || group.status === "identical";
      const matchesStatus =
        state.status === "all" ||
        (state.status === "needs-action" && needsAction) ||
        group.status === state.status;
      const haystack = [
        group.name,
        group.status,
        recommendation(group),
        ...group.locations.flatMap((item) => [item.path, item.relativePath, item.realFolderPath, item.description])
      ].join(" ").toLowerCase();
      return matchesStatus && (!q || haystack.includes(q));
    });
  }

  function renderTable() {
    const rows = filteredGroups();
    $("#resultCount").textContent = `${formatNumber(rows.length)} 项`;
    if (!rows.length) {
      $("#skillTable").innerHTML = `
        <tr>
          <td colspan="5">
            <div class="table-empty">
              <strong>当前筛选没有项目</strong>
              <p>如果要查看全部技能，请切换到“全部”或“软链共享”。</p>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    $("#skillTable").innerHTML = rows
      .map((group) => {
        const primary = group.locations[0];
        return `
          <tr>
            <td>
              <div class="skill-name">${escapeHtml(group.name)}</div>
              <div class="muted">${group.locations.length} 个入口 · ${group.realFolderPaths.length} 个实体 · ${group.hashes.length} 个版本</div>
            </td>
            <td>${statusPill(group.status)}</td>
            <td>
              <div class="agent-badges">
                ${group.locations.map((item) => `<span>${escapeHtml(item.root)}</span>`).join("")}
              </div>
            </td>
            <td>${escapeHtml(recommendation(group))}</td>
            <td>
              <details class="path-details">
                <summary>路径</summary>
                <div class="path-list">
                  ${group.locations.map((item) => `
                    <button type="button" data-copy="${escapeHtml(item.path)}">
                      <strong>${escapeHtml(item.root)}</strong>
                      <span>${escapeHtml(item.relativePath)}</span>
                    </button>
                  `).join("")}
                  <button type="button" data-copy="${escapeHtml(primary.realFolderPath)}">
                    <strong>real</strong>
                    <span>${escapeHtml(primary.realFolderPath)}</span>
                  </button>
                </div>
              </details>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function bindFilters() {
    $("#skillSearch").addEventListener("input", (event) => {
      state.query = event.target.value;
      renderTable();
    });

    $$(".filter-chip").forEach((button) => {
      button.addEventListener("click", () => {
        state.status = button.dataset.status;
        $$(".filter-chip").forEach((item) => item.classList.toggle("is-active", item === button));
        renderTable();
      });
    });

    document.addEventListener("click", (event) => {
      const copyButton = event.target.closest("[data-copy]");
      if (!copyButton) return;
      copyText(copyButton.dataset.copy);
      copyButton.classList.add("is-copied");
      setTimeout(() => copyButton.classList.remove("is-copied"), 800);
    });
  }

  function setNavState() {
    const links = $$(".nav-link");
    const sections = links.map((link) => document.querySelector(link.getAttribute("href")));
    const active = sections.findLast((section) => section && section.getBoundingClientRect().top < 160);
    links.forEach((link) => {
      link.classList.toggle("is-active", active && link.getAttribute("href") === `#${active.id}`);
    });
  }

  function initDialog() {
    const dialog = $("#hintDialog");
    $("#refreshHint").addEventListener("click", () => dialog.showModal());
    $("#closeDialog").addEventListener("click", () => dialog.close());
  }

  function boot() {
    initDialog();

    if (!report) {
      $("#healthHero").innerHTML = `
        <div class="hero-copy">
          <p class="eyebrow">No Data</p>
          <h2>缺少扫描数据</h2>
          <p>请先运行 scan.mjs 生成 data/report.js。</p>
        </div>
      `;
      return;
    }

    renderHero();
    renderMetrics();
    renderChecks();
    renderRoots();
    renderActions();
    renderWatcher();
    renderSyncMatrix();
    renderTable();
    bindFilters();

    document.addEventListener("scroll", setNavState, { passive: true });
    setNavState();
  }

  boot();
})();
