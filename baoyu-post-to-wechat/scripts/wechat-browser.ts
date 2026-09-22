import fs from 'node:fs';
import { readdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

import {
  CdpConnection,
  findChromeExecutable,
  getDefaultProfileDir,
  getAccountProfileDir,
  findExistingChromeDebugPort,
  launchChrome,
  sleep,
  tryConnectExisting,
} from './cdp.ts';
import { loadWechatExtendConfig, resolveAccount } from './wechat-extend-config.ts';
import { ACCOUNT_ID_EXPRESSION, assertBackendAccount } from './wechat-account-guard.ts';

const WECHAT_URL = 'https://mp.weixin.qq.com/';

interface MarkdownMeta {
  title: string;
  author: string;
  content: string;
}

function parseMarkdownFile(filePath: string): MarkdownMeta {
  const text = fs.readFileSync(filePath, 'utf-8');
  let title = '';
  let author = '';
  let content = '';

  const fmMatch = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (fmMatch) {
    const fm = fmMatch[1]!;
    const titleMatch = fm.match(/^title:\s*(.+)$/m);
    if (titleMatch) title = titleMatch[1]!.trim().replace(/^["']|["']$/g, '');
    const authorMatch = fm.match(/^author:\s*(.+)$/m);
    if (authorMatch) author = authorMatch[1]!.trim().replace(/^["']|["']$/g, '');
  }

  const bodyText = fmMatch ? text.slice(fmMatch[0].length) : text;

  if (!title) {
    const h1Match = bodyText.match(/^#\s+(.+)$/m);
    if (h1Match) title = h1Match[1]!.trim();
  }

  const lines = bodyText.split('\n');
  const paragraphs: string[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith('#')) continue;
    if (trimmed.startsWith('![')) continue;
    if (trimmed.startsWith('---')) continue;
    paragraphs.push(trimmed);

  }
  content = paragraphs.join('\n');

  return { title, author, content };
}

export function compressTitle(title: string, maxLen = 20): string {
  if (title.length > maxLen) throw new Error(`Photo title exceeds ${maxLen} characters; supply an approved shorter version`);
  return title;
}

export function compressContent(content: string, maxLen = 1000): string {
  if (content.length > maxLen) throw new Error(`Photo content exceeds ${maxLen} characters; supply an approved shorter version`);
  return content;
}

async function loadImagesFromDir(dir: string): Promise<string[]> {
  const entries = await readdir(dir);
  const images = entries
    .filter(f => /\.(png|jpg|jpeg|gif|webp)$/i.test(f))
    .sort((a, b) => a.localeCompare(b, 'en', { numeric: true }))
    .map(f => path.join(dir, f));
  return images;
}

interface WeChatBrowserOptions {
  title?: string;
  content?: string;
  images?: string[];
  imagesDir?: string;
  markdownFile?: string;
  submit?: boolean;
  expectedAccountId?: string;
  timeoutMs?: number;
  profileDir?: string;
  chromePath?: string;
  draftId?: string;
  cover?: string;
}

export function assertSaveClicked(result: string): void {
  if (!result.startsWith('clicked:')) throw new Error('Save button not found; draft not saved');
}
export function assertSaveConfirmed(messages: string[], previous: string[] = []): void {
  if (messages.some(m => /失败|错误|fail|error/i.test(m)) || !messages.some(m => !previous.includes(m) && /保存成功|已保存|saved successfully/i.test(m))) throw new Error('Draft save unconfirmed; inspect draft list before retrying');
}

async function waitForDomCondition(cdp: CdpConnection, sessionId: string, expression: string, timeoutMs = 15_000): Promise<boolean> {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const result = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
      expression: `Boolean(${expression})`, returnByValue: true,
    }, { sessionId });
    if (result.result.value) return true;
    await sleep(250);
  }
  return false;
}

async function clickVisibleButton(cdp: CdpConnection, sessionId: string, text: string): Promise<void> {
  const result = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
    expression: `(function() {
      const button = Array.from(document.querySelectorAll('.weui-desktop-dialog button'))
        .find(node => node.textContent?.trim().includes(${JSON.stringify(text)}));
      if (!button) return false;
      button.click();
      return true;
    })()`,
    returnByValue: true,
    userGesture: true,
  }, { sessionId });
  if (!result.result.value) throw new Error(`Visible cover dialog button not found: ${text}`);
}

async function setPhotoCover(cdp: CdpConnection, sessionId: string, coverPath: string): Promise<void> {
  const absolutePath = path.isAbsolute(coverPath) ? coverPath : path.resolve(process.cwd(), coverPath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Photo cover image not found: ${absolutePath}`);
  const filename = path.basename(absolutePath);
  const opened = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
    expression: `(function() {
      const button = document.querySelector('#js_cover_null .js_imagedialog') || document.querySelector('.first_appmsg_cover .js_imagedialog');
      if (!button) return false;
      button.click();
      return true;
    })()`, returnByValue: true, userGesture: true,
  }, { sessionId });
  if (!opened.result.value) throw new Error('Photo cover image library control not found');
  const dialogReady = await waitForDomCondition(cdp, sessionId, `document.querySelector('.weui-desktop-dialog input[type="file"][accept*="image/bmp"]')`, 10_000);
  if (!dialogReady) throw new Error('Photo cover upload dialog did not open');
  const previousCount = await cdp.send<{ result: { value: number } }>('Runtime.evaluate', {
    expression: `Array.from(document.querySelectorAll('.weui-desktop-img-picker__img-title')).filter(node => node.textContent?.trim() === ${JSON.stringify(filename)}).length`,
    returnByValue: true,
  }, { sessionId });
  const documentNode = await cdp.send<{ root: { nodeId: number } }>('DOM.getDocument', { depth: -1, pierce: true }, { sessionId });
  const input = await cdp.send<{ nodeId: number }>('DOM.querySelector', {
    nodeId: documentNode.root.nodeId,
    selector: '.weui-desktop-dialog input[type="file"][accept*="image/bmp"]',
  }, { sessionId });
  if (!input.nodeId) throw new Error('Photo cover upload input not found');
  await cdp.send('DOM.setFileInputFiles', { nodeId: input.nodeId, files: [absolutePath] }, { sessionId });
  const uploaded = await waitForDomCondition(cdp, sessionId, `Array.from(document.querySelectorAll('.weui-desktop-img-picker__img-title')).filter(node => node.textContent?.trim() === ${JSON.stringify(filename)}).length > ${previousCount.result.value}`, 30_000);
  if (!uploaded) throw new Error('Photo cover did not appear in image library');
  const selected = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
    expression: `(function() {
      const title = Array.from(document.querySelectorAll('.weui-desktop-img-picker__img-title')).find(node => node.textContent?.trim() === ${JSON.stringify(filename)});
      if (!title) return false;
      title.parentElement?.click();
      return true;
    })()`, returnByValue: true, userGesture: true,
  }, { sessionId });
  if (!selected.result.value) throw new Error('Uploaded photo cover could not be selected');
  await clickVisibleButton(cdp, sessionId, '下一步');
  const cropReady = await waitForDomCondition(cdp, sessionId, `Array.from(document.querySelectorAll('.weui-desktop-dialog')).some(dialog => dialog.offsetParent !== null && dialog.textContent?.includes('编辑封面'))`, 10_000);
  if (!cropReady) throw new Error('Photo cover crop dialog did not open');
  await clickVisibleButton(cdp, sessionId, '确认');
  const applied = await waitForDomCondition(cdp, sessionId, `(function() {
    const preview = document.querySelector('.first_appmsg_cover');
    const background = preview?.style?.backgroundImage || '';
    return background.includes('url(') && !document.body.innerText.includes('封面规格异常');
  })()`, 15_000);
  if (!applied) throw new Error('Photo cover crop was not applied cleanly');
  console.log('[wechat-browser] Photo cover verified in editor.');
}

export async function postToWeChat(options: WeChatBrowserOptions): Promise<void> {
  const { submit = false, timeoutMs = 120_000, profileDir = getDefaultProfileDir() } = options;

  let title = options.title || '';
  let content = options.content || '';
  let images = options.images || [];

  if (options.markdownFile) {
    const absPath = path.isAbsolute(options.markdownFile) ? options.markdownFile : path.resolve(process.cwd(), options.markdownFile);
    if (!fs.existsSync(absPath)) throw new Error(`Markdown file not found: ${absPath}`);
    const meta = parseMarkdownFile(absPath);
    if (!title) title = meta.title;
    if (!content) content = meta.content;
    console.log(`[wechat-browser] Parsed markdown: title="${meta.title}", content=${meta.content.length} chars`);
  }

  if (options.imagesDir) {
    const absDir = path.isAbsolute(options.imagesDir) ? options.imagesDir : path.resolve(process.cwd(), options.imagesDir);
    if (!fs.existsSync(absDir)) throw new Error(`Images directory not found: ${absDir}`);
    images = await loadImagesFromDir(absDir);
    console.log(`[wechat-browser] Image order (directory natural filename order): ${JSON.stringify(images)}`);
    console.log(`[wechat-browser] Found ${images.length} images in ${absDir}`);
  }

  title = compressTitle(title, 20);
  content = compressContent(content, 1000);

  if (!title) throw new Error('Title is required (use --title or --markdown)');
  if (!content) throw new Error('Content is required (use --content or --markdown)');
  if (images.length === 0) throw new Error('At least one image is required (use --image or --images)');

  for (const img of images) {
    if (!fs.existsSync(img)) throw new Error(`Image not found: ${img}`);
  }

  const chromePath = findChromeExecutable(options.chromePath);
  if (!chromePath) throw new Error('Chrome not found. Set WECHAT_BROWSER_CHROME_PATH env var.');

  let cdp: CdpConnection | null = null;

  try {
    const existingPort = await findExistingChromeDebugPort(profileDir);
    if (existingPort) {
      cdp = await tryConnectExisting(existingPort);
      if (cdp) console.log(`[wechat-browser] Connected to existing Chrome on port ${existingPort}`);
    }
    if (!cdp) {
      console.log(`[wechat-browser] Launching Chrome (profile: ${profileDir})`);
      cdp = (await launchChrome(WECHAT_URL, profileDir, chromePath)).cdp;
    }

    const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    let pageTarget = targets.targetInfos.find((t) => t.type === 'page' && t.url.includes('mp.weixin.qq.com'));

    if (!pageTarget) {
      const { targetId } = await cdp.send<{ targetId: string }>('Target.createTarget', { url: WECHAT_URL });
      pageTarget = { targetId, url: WECHAT_URL, type: 'page' };
    }

    let { sessionId } = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: pageTarget.targetId, flatten: true });

    await cdp.send('Page.enable', {}, { sessionId });
    await cdp.send('Runtime.enable', {}, { sessionId });
    await cdp.send('DOM.enable', {}, { sessionId });

    console.log('[wechat-browser] Waiting for page load...');
    await sleep(3000);

    const checkLoginStatus = async (): Promise<boolean> => {
      const result = await cdp!.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: `window.location.href`,
        returnByValue: true,
      }, { sessionId });
      return result.result.value.includes('/cgi-bin/');
    };

    const waitForLogin = async (): Promise<boolean> => {
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        if (await checkLoginStatus()) return true;
        await sleep(2000);
      }
      return false;
    };

    let isLoggedIn = await checkLoginStatus();
    if (!isLoggedIn) {
      console.log('[wechat-browser] Not logged in. Please scan QR code to log in...');
      isLoggedIn = await waitForLogin();
      if (!isLoggedIn) throw new Error('Timed out waiting for login. Please log in first.');
    }
    console.log('[wechat-browser] Logged in.');

    const currentUrl = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `window.location.href`, returnByValue: true,
    }, { sessionId });
    if (!currentUrl.result.value.includes('/cgi-bin/home')) {
      const activeUrl = new URL(currentUrl.result.value);
      const token = activeUrl.searchParams.get('token');
      if (!token) throw new Error('Logged-in WeChat page has no token; cannot navigate safely.');
      const homeUrl = `${WECHAT_URL}cgi-bin/home?t=home/index&token=${encodeURIComponent(token)}&lang=zh_CN`;
      await cdp.send('Runtime.evaluate', {
        expression: `window.location.href = ${JSON.stringify(homeUrl)}`,
      }, { sessionId });
      await sleep(5000);
    }
    const accountProof = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: ACCOUNT_ID_EXPRESSION, returnByValue: true,
    }, { sessionId });
    assertBackendAccount(options.expectedAccountId, accountProof.result.value);

    let editorInfo: { targetId: string; isNewTab: boolean } | null = null;
    if (options.draftId) {
      const homeLocation = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: 'window.location.href', returnByValue: true,
      }, { sessionId });
      const token = new URL(homeLocation.result.value).searchParams.get('token');
      if (!token) throw new Error('Cannot resume photo draft: backend token is unavailable');
      const editUrl = `${WECHAT_URL}cgi-bin/appmsg?t=media/appmsg_edit&action=edit&reprint_confirm=0&type=77&appmsgid=${encodeURIComponent(options.draftId)}&token=${encodeURIComponent(token)}&lang=zh_CN`;
      const created = await cdp.send<{ targetId: string }>('Target.createTarget', { url: editUrl });
      editorInfo = { targetId: created.targetId, isNewTab: true };
      console.log(`[wechat-browser] Resuming photo draft: ${options.draftId}`);
    }

    if (!editorInfo) {
      await sleep(2000);

    console.log('[wechat-browser] Looking for "贴图" menu...');
    const menuResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `
        const menuItems = document.querySelectorAll('.new-creation__menu .new-creation__menu-item');
        const count = menuItems.length;
        const texts = Array.from(menuItems).map(m => m.querySelector('.new-creation__menu-title')?.textContent?.trim() || m.textContent?.trim() || '');
        JSON.stringify({ count, texts });
      `,
      returnByValue: true,
    }, { sessionId });
    console.log(`[wechat-browser] Menu items: ${menuResult.result.value}`);

    const getTargets = async () => {
      return await cdp!.send<{ targetInfos: Array<{ targetId: string; url: string; type: string }> }>('Target.getTargets');
    };

    const initialTargets = await getTargets();
    const initialIds = new Set(initialTargets.targetInfos.map(t => t.targetId));
    console.log(`[wechat-browser] Initial targets count: ${initialTargets.targetInfos.length}`);

    console.log('[wechat-browser] Finding "贴图" menu position...');
    const menuPos = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `
        (function() {
          const menuItems = document.querySelectorAll('.new-creation__menu .new-creation__menu-item');
          console.log('Found menu items:', menuItems.length);
          for (const item of menuItems) {
            const title = item.querySelector('.new-creation__menu-title');
            const text = title?.textContent?.trim() || '';
            console.log('Menu item text:', text);
            if (text === '图文' || text === '贴图') {
              item.scrollIntoView({ block: 'center', behavior: 'instant' });
              const rect = item.getBoundingClientRect();
              console.log('Found 贴图，rect:', JSON.stringify(rect));
              return JSON.stringify({ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2, width: rect.width, height: rect.height });
            }
          }
          return 'null';
        })()
      `,
      returnByValue: true,
    }, { sessionId });
    console.log(`[wechat-browser] Menu position: ${menuPos.result.value}`);

    const pos = menuPos.result.value !== 'null' ? JSON.parse(menuPos.result.value) : null;
    if (!pos) throw new Error('贴图 menu not found or not visible');

    console.log('[wechat-browser] Clicking "贴图" menu with mouse events...');
    await cdp.send('Input.dispatchMouseEvent', {
      type: 'mousePressed',
      x: pos.x,
      y: pos.y,
      button: 'left',
      clickCount: 1,
    }, { sessionId });
    await sleep(100);
    await cdp.send('Input.dispatchMouseEvent', {
      type: 'mouseReleased',
      x: pos.x,
      y: pos.y,
      button: 'left',
      clickCount: 1,
    }, { sessionId });

    console.log('[wechat-browser] Waiting for editor...');
    await sleep(3000);

    const waitForEditor = async (): Promise<{ targetId: string; isNewTab: boolean } | null> => {
      const start = Date.now();

      while (Date.now() - start < 30_000) {
        const targets = await getTargets();
        const pageTargets = targets.targetInfos.filter(t => t.type === 'page');

        for (const t of pageTargets) {
          console.log(`[wechat-browser] Target: ${t.url}`);
        }

        const newTab = pageTargets.find(t => !initialIds.has(t.targetId) && t.url.includes('mp.weixin.qq.com'));
        if (newTab) {
          console.log(`[wechat-browser] Found new tab: ${newTab.url}`);
          return { targetId: newTab.targetId, isNewTab: true };
        }

        const editorTab = pageTargets.find(t => t.url.includes('appmsg'));
        if (editorTab) {
          console.log(`[wechat-browser] Found editor tab: ${editorTab.url}`);
          return { targetId: editorTab.targetId, isNewTab: !initialIds.has(editorTab.targetId) };
        }

        const currentUrl = await cdp!.send<{ result: { value: string } }>('Runtime.evaluate', {
          expression: `window.location.href`,
          returnByValue: true,
        }, { sessionId });
        console.log(`[wechat-browser] Current page URL: ${currentUrl.result.value}`);

        if (currentUrl.result.value.includes('appmsg')) {
          console.log(`[wechat-browser] Current page navigated to editor`);
          return { targetId: pageTarget!.targetId, isNewTab: false };
        }

        await sleep(1000);
      }
      return null;
    };

      editorInfo = await waitForEditor();
    }
    if (!editorInfo) {
      const finalTargets = await getTargets();
      console.log(`[wechat-browser] Final targets: ${finalTargets.targetInfos.filter(t => t.type === 'page').map(t => t.url).join(', ')}`);
      throw new Error('Editor not found.');
    }

    if (editorInfo.isNewTab) {
      console.log('[wechat-browser] Switching to editor tab...');
      const editorSession = await cdp.send<{ sessionId: string }>('Target.attachToTarget', { targetId: editorInfo.targetId, flatten: true });
      sessionId = editorSession.sessionId;

      await cdp.send('Page.enable', {}, { sessionId });
      await cdp.send('Runtime.enable', {}, { sessionId });
      await cdp.send('DOM.enable', {}, { sessionId });
    } else {
      console.log('[wechat-browser] Editor opened in current page');
    }

    await cdp.send('Page.enable', {}, { sessionId });
    await cdp.send('Runtime.enable', {}, { sessionId });
    await cdp.send('DOM.enable', {}, { sessionId });

    let uploadInputReady = false;
    for (let i = 0; i < 30; i++) {
      const ready = await cdp.send<{ result: { value: boolean } }>('Runtime.evaluate', {
        expression: `Boolean(document.querySelector('.js_upload_btn_container input[type=file], input[type=file][multiple][accept*="image"]'))`,
        returnByValue: true,
      }, { sessionId });
      if (ready.result.value) {
        uploadInputReady = true;
        break;
      }
      await sleep(500);
    }
    if (!uploadInputReady) throw new Error('Photo editor did not finish loading its image uploader');

    console.log('[wechat-browser] Uploading all images at once...');
    const absolutePaths = images.map(p => path.isAbsolute(p) ? p : path.resolve(process.cwd(), p));
    console.log(`[wechat-browser] Images: ${absolutePaths.join(', ')}`);
    if (options.draftId) {
      await waitForDomCondition(cdp, sessionId, `document.querySelectorAll('.image-selector__bottom-list-item').length > 0`, 10_000);
      await sleep(500);
    }

    // --- PRIMARY approach: intercept file chooser dialog ---
    const existingRemoteCount = await cdp.send<{ result: { value: number } }>('Runtime.evaluate', {
      expression: `(function() {
        const remote = new Set();
        document.querySelectorAll('.image-selector__bottom-list-item').forEach((el) => {
          const bg = getComputedStyle(el).backgroundImage || '';
          if (/mmbiz|qpic\\.cn/.test(bg)) remote.add(bg);
        });
        return remote.size;
      })()`,
      returnByValue: true,
    }, { sessionId });
    let uploadSuccess = existingRemoteCount.result.value === absolutePaths.length;
    if (uploadSuccess) {
      console.log(`[wechat-browser] Existing draft already contains ${absolutePaths.length} remote images; keeping them.`);
    }
    try {
      if (uploadSuccess) throw new Error('__SKIP_ALREADY_UPLOADED__');
      console.log('[wechat-browser] [primary] Enabling file chooser interception...');
      await cdp.send('Page.setInterceptFileChooserDialog', { enabled: true }, { sessionId });

      // Set up listener for file chooser opened event BEFORE clicking
      const fileChooserPromise = new Promise<{ backendNodeId: number; mode: string }>((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('File chooser dialog not opened within 10s')), 10_000);
        cdp!.on('Page.fileChooserOpened', (params: unknown) => {
          clearTimeout(timeout);
          const p = params as { backendNodeId: number; mode: string };
          console.log(`[wechat-browser] [primary] File chooser opened: backendNodeId=${p.backendNodeId}, mode=${p.mode}`);
          resolve(p);
        });
      });

      // Trigger file chooser by calling .click() on the file input with userGesture
      const fileInputSelectors = [
        '.js_upload_btn_container input[type=file]',
        'input[type=file][multiple][accept*="image"]',
        'input[type=file][accept*="image"]',
        'input[type=file][multiple]',
        'input[type=file]',
      ];

      console.log('[wechat-browser] [primary] Clicking file input via JS .click() with userGesture...');
      const clickResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: `
          (function() {
            const selectors = ${JSON.stringify(fileInputSelectors)};
            for (const sel of selectors) {
              const el = document.querySelector(sel);
              if (el) {
                el.click();
                return JSON.stringify({ clicked: sel });
              }
            }
            const debug = [];
            document.querySelectorAll('input[type=file]').forEach((inp, i) => {
              debug.push({ i, accept: inp.accept, multiple: inp.multiple, parentClass: inp.parentElement?.className?.slice(0, 60) });
            });
            return JSON.stringify({ error: 'no file input found', fileInputs: debug });
          })()
        `,
        returnByValue: true,
        userGesture: true,
      }, { sessionId });
      console.log(`[wechat-browser] [primary] Click result: ${clickResult.result.value}`);

      const clickStatus = JSON.parse(clickResult.result.value);
      if (clickStatus.error) {
        throw new Error(`File input not found: ${clickStatus.error}`);
      }

      // Wait for the file chooser event
      console.log('[wechat-browser] [primary] Waiting for file chooser dialog...');
      const chooser = await fileChooserPromise;

      console.log(`[wechat-browser] [primary] Setting files via backendNodeId=${chooser.backendNodeId}...`);
      await cdp.send('DOM.setFileInputFiles', {
        files: absolutePaths,
        backendNodeId: chooser.backendNodeId,
      }, { sessionId });
      const resolvedInput = await cdp.send<{ object: { objectId?: string } }>('DOM.resolveNode', {
        backendNodeId: chooser.backendNodeId,
      }, { sessionId });
      if (!resolvedInput.object.objectId) throw new Error('Selected file input could not be resolved');
      const dispatchResult = await cdp.send<{ result: { value: string } }>('Runtime.callFunctionOn', {
        objectId: resolvedInput.object.objectId,
        functionDeclaration: `function() {
          const fileCount = this.files ? this.files.length : 0;
          this.dispatchEvent(new Event('input', { bubbles: true }));
          this.dispatchEvent(new Event('change', { bubbles: true }));
          return JSON.stringify({ files: fileCount });
        }`,
        returnByValue: true,
      }, { sessionId });
      const dispatchStatus = JSON.parse(dispatchResult.result.value || '{}');
      console.log(`[wechat-browser] [primary] Change event dispatched: ${dispatchResult.result.value}`);
      if (dispatchStatus.files !== absolutePaths.length) {
        throw new Error(`File input did not retain selected files (${dispatchStatus.files || 0}/${absolutePaths.length})`);
      }
      console.log('[wechat-browser] [primary] Files set successfully via file chooser interception');
      uploadSuccess = true;
    } catch (primaryErr) {
      if (!(primaryErr instanceof Error && primaryErr.message === '__SKIP_ALREADY_UPLOADED__')) {
        console.log(`[wechat-browser] [primary] File chooser approach failed: ${primaryErr instanceof Error ? primaryErr.message : String(primaryErr)}`);
      }
      // Disable interception before falling back
      try { await cdp.send('Page.setInterceptFileChooserDialog', { enabled: false }, { sessionId }); } catch {}
    }

    // --- FALLBACK approach: direct DOM.setFileInputFiles on nodeId ---
    if (!uploadSuccess) {
      console.log('[wechat-browser] [fallback] Trying direct DOM.setFileInputFiles...');
      const { root } = await cdp.send<{ root: { nodeId: number } }>('DOM.getDocument', {}, { sessionId });

      const fileInputSelectors = [
        '.js_upload_btn_container input[type=file]',
        'input[type=file][multiple][accept*="image"]',
        'input[type=file][accept*="image"]',
        'input[type=file][multiple]',
        'input[type=file]',
      ];

      let nodeId = 0;
      for (const sel of fileInputSelectors) {
        const result = await cdp.send<{ nodeId: number }>('DOM.querySelector', { nodeId: root.nodeId, selector: sel }, { sessionId });
        if (result.nodeId) {
          console.log(`[wechat-browser] [fallback] Found file input with selector: ${sel}`);
          nodeId = result.nodeId;
          break;
        }
      }

      if (!nodeId) throw new Error('File input not found with any selector');

      await cdp.send('DOM.setFileInputFiles', { nodeId, files: absolutePaths }, { sessionId });
      console.log('[wechat-browser] [fallback] Files set via nodeId');

      // Dispatch change event
      await cdp.send('Runtime.evaluate', {
        expression: `
          (function() {
            const selectors = ${JSON.stringify(fileInputSelectors)};
            for (const sel of selectors) {
              const el = document.querySelector(sel);
              if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
                return 'dispatched on ' + sel;
              }
            }
            return 'no input found for event dispatch';
          })()
        `,
        returnByValue: true,
      }, { sessionId });
      console.log('[wechat-browser] [fallback] Change event dispatched');
    }

    // Wait for images to upload
    console.log('[wechat-browser] Waiting for images to upload...');
    const targetCount = absolutePaths.length;
    let uploadedCount = 0;
    for (let i = 0; i < 30; i++) {
      await sleep(2000);
      const uploadCheck = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: `
          (function() {
            const remote = new Set();
            document.querySelectorAll('.image-selector img').forEach((img) => {
              if (/mmbiz|qpic\.cn/.test(img.src || '')) remote.add(img.src);
            });
            document.querySelectorAll('.image-selector *').forEach((el) => {
              const bg = getComputedStyle(el).backgroundImage || '';
              if (/mmbiz|qpic\.cn/.test(bg)) remote.add(bg);
            });
            return JSON.stringify({
            uploaded: remote.size,
            remote: Array.from(remote),
            loading: document.querySelectorAll('[class*="upload_loading"], [class*="uploading"], .weui-desktop-upload__loading').length
            });
          })()
        `,
        returnByValue: true,
      }, { sessionId });
      const status = JSON.parse(uploadCheck.result.value);
      uploadedCount = status.uploaded;
      console.log(`[wechat-browser] Upload progress: ${status.uploaded}/${targetCount} (loading: ${status.loading})`);
      if (status.uploaded >= targetCount) break;
    }
    if (uploadedCount < targetCount) {
      throw new Error(`Image upload was not verified (${uploadedCount}/${targetCount}); draft was not saved`);
    }

    console.log('[wechat-browser] Filling title...');
    const titleResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `
        (function() {
          const visibleTitle = document.querySelector('.ProseMirror[contenteditable=true][data-placeholder="请在这里输入标题"]');
          if (!visibleTitle) return 'title_editor_not_found';
          visibleTitle.textContent = ${JSON.stringify(title)};
          visibleTitle.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: ${JSON.stringify(title)} }));
          return visibleTitle.textContent || '';
        })()
      `,
      returnByValue: true,
    }, { sessionId });
    if (titleResult.result.value !== title) throw new Error('Visible photo title was not written exactly');
    await sleep(500);

    console.log('[wechat-browser] Filling content...');
    // Try ProseMirror editor first (new WeChat UI), then fallback to old editor
    const contentResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
      expression: `
        (function() {
          const contentHtml = ${JSON.stringify('<p>' + content.split('\n').filter(l => l.trim()).join('</p><p>') + '</p>')};

          // New UI: ProseMirror contenteditable
          const pm = Array.from(document.querySelectorAll('.ProseMirror[contenteditable=true]')).find(el =>
            !el.hasAttribute('data-placeholder') &&
            !el.textContent?.includes('从这里开始写正文') &&
            !el.classList.contains('original_primary_tips_input')
          );
          if (pm) {
            pm.innerHTML = contentHtml;
            pm.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: ${JSON.stringify(content)} }));
            return 'ProseMirror: content set, length=' + pm.textContent.length;
          }

          // Old UI: .js_pmEditorArea
          const oldEditor = document.querySelector('.js_pmEditorArea');
          if (oldEditor) {
            return JSON.stringify({ type: 'old', x: oldEditor.getBoundingClientRect().x + 50, y: oldEditor.getBoundingClientRect().y + 20 });
          }

          return 'editor_not_found';
        })()
      `,
      returnByValue: true,
    }, { sessionId });

    const contentStatus = contentResult.result.value;
    console.log(`[wechat-browser] Content result: ${contentStatus}`);

    if (contentStatus === 'editor_not_found') {
      throw new Error('Content editor not found');
    }

    // Fallback: old editor uses keyboard simulation
    if (contentStatus.startsWith('{')) {
      const editorClickPos = JSON.parse(contentStatus);
      if (editorClickPos.type === 'old') {
        console.log('[wechat-browser] Using old editor with keyboard simulation...');
        await cdp.send('Input.dispatchMouseEvent', {
          type: 'mousePressed',
          x: editorClickPos.x,
          y: editorClickPos.y,
          button: 'left',
          clickCount: 1,
        }, { sessionId });
        await sleep(50);
        await cdp.send('Input.dispatchMouseEvent', {
          type: 'mouseReleased',
          x: editorClickPos.x,
          y: editorClickPos.y,
          button: 'left',
          clickCount: 1,
        }, { sessionId });
        await sleep(300);

        await cdp.send('Input.dispatchKeyEvent', {
          type: 'keyDown', key: 'a', code: 'KeyA', modifiers: process.platform === 'darwin' ? 4 : 2,
        }, { sessionId });
        await cdp.send('Input.dispatchKeyEvent', {
          type: 'keyUp', key: 'a', code: 'KeyA', modifiers: process.platform === 'darwin' ? 4 : 2,
        }, { sessionId });
        await cdp.send('Input.dispatchKeyEvent', {
          type: 'keyDown', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8,
        }, { sessionId });
        await cdp.send('Input.dispatchKeyEvent', {
          type: 'keyUp', key: 'Backspace', code: 'Backspace', windowsVirtualKeyCode: 8,
        }, { sessionId });

        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          if (line!.length > 0) {
            await cdp.send('Input.insertText', { text: line }, { sessionId });
          }
          if (i < lines.length - 1) {
            await cdp.send('Input.dispatchKeyEvent', {
              type: 'keyDown',
              key: 'Enter',
              code: 'Enter',
              windowsVirtualKeyCode: 13,
            }, { sessionId });
            await cdp.send('Input.dispatchKeyEvent', {
              type: 'keyUp',
              key: 'Enter',
              code: 'Enter',
              windowsVirtualKeyCode: 13,
            }, { sessionId });
          }
          await sleep(50);
        }
        console.log('[wechat-browser] Content typed via keyboard.');
      }
    }
    await sleep(500);

    await setPhotoCover(cdp, sessionId, options.cover || absolutePaths[0]!);

    if (submit) {
      const beforeSave = await cdp.send<{ result: { value: string[] } }>('Runtime.evaluate', {
        expression: `Array.from(document.querySelectorAll('.weui-desktop-toast, [class*=toast]')).map(t => t.textContent?.trim()).filter(Boolean)`, returnByValue: true,
      }, { sessionId });
      console.log('[wechat-browser] Saving as draft...');
      const submitResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: `
          (function() {
            // Try new UI: find button by text
            const allBtns = document.querySelectorAll('button');
            for (const btn of allBtns) {
              const text = btn.textContent?.trim();
              if (text === '保存为草稿') {
                btn.click();
                return 'clicked:保存为草稿';
              }
            }
            // Fallback: old UI selector
            const oldBtn = document.querySelector('#js_submit');
            if (oldBtn) {
              oldBtn.click();
              return 'clicked:#js_submit';
            }
            // List available buttons for debugging
            const btnTexts = [];
            allBtns.forEach(b => {
              const t = b.textContent?.trim();
              if (t && t.length < 20) btnTexts.push(t);
            });
            return 'not_found:' + btnTexts.join(',');
          })()
        `,
        returnByValue: true,
      }, { sessionId });
      console.log(`[wechat-browser] Submit result: ${submitResult.result.value}`);
      assertSaveClicked(submitResult.result.value);
      await sleep(3000);

      // Verify save success by checking for toast
      const toastCheck = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
        expression: `
          const toasts = document.querySelectorAll('.weui-desktop-toast, [class*=toast]');
          const msgs = [];
          toasts.forEach(t => { const text = t.textContent?.trim(); if (text) msgs.push(text); });
          JSON.stringify(msgs);
        `,
        returnByValue: true,
      }, { sessionId });
      console.log(`[wechat-browser] Toast messages: ${toastCheck.result.value}`);
      const messages: string[] = JSON.parse(toastCheck.result.value || '[]');
      let draftId = '';
      let savedHref = '';
      for (let i = 0; i < 30 && !draftId; i++) {
        const idResult = await cdp.send<{ result: { value: string } }>('Runtime.evaluate', {
          expression: `JSON.stringify({ id: new URL(window.location.href).searchParams.get('appmsgid') || '', href: window.location.href })`,
          returnByValue: true,
        }, { sessionId });
        const locationState = JSON.parse(idResult.result.value || '{}');
        draftId = locationState.id || '';
        savedHref = locationState.href || '';
        if (!draftId) await sleep(500);
      }
      const freshToast = messages.some(m => !(beforeSave.result.value || []).includes(m) && /保存成功|已保存|saved successfully/i.test(m));
      const urlAcknowledged = Boolean(draftId && savedHref && !savedHref.includes('isNew=1'));
      if (!freshToast && !urlAcknowledged) {
        assertSaveConfirmed(messages, beforeSave.result.value || []);
      }
      if (!draftId) throw new Error('Save acknowledgement observed without a draft ID; inspect draft list before retrying');
      console.log(JSON.stringify({
        draft_id: draftId,
        account_id: options.expectedAccountId,
        title,
        image_count: images.length,
        status: 'saved_pending_readback',
      }));
    } else {
      console.log('[wechat-browser] Article composed (preview mode). Add --submit to save as draft.');
    }
  } finally {
    if (cdp) {
      cdp.close();
    }
    console.log('[wechat-browser] Done. Browser window left open.');
  }
}

function printUsage(): never {
  console.log(`Post image-text (贴图) to WeChat Official Account

Usage:
  npx -y bun wechat-browser.ts [options]

Options:
  --markdown <path>  Markdown file for title/content extraction
  --images <dir>     Directory containing images (PNG/JPG)
  --title <text>     Article title (max 20 chars, auto-compressed)
  --content <text>   Article content (max 1000 chars, auto-compressed)
  --image <path>     Add image (can be repeated)
  --expected-account-id <id>  Required original backend account ID (gh_...)
  --submit           Save as draft (default: preview only)
  --profile <dir>    Chrome profile directory
  --draft-id <id>    Resume and update an existing photo draft instead of creating another
  --cover <path>      Cover source; defaults to first photo and uses WeChat crop step
  --account <alias>  Select account by alias (for multi-account setups)
  --help             Show this help

Examples:
  npx -y bun wechat-browser.ts --markdown article.md --images ./photos/
  npx -y bun wechat-browser.ts --title "测试" --content "内容" --image ./photo.png
  npx -y bun wechat-browser.ts --markdown article.md --images ./photos/ --submit
`);
  process.exit(0);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) printUsage();

  const images: string[] = [];
  let submit = false;
  let profileDir: string | undefined;
  let title: string | undefined;
  let content: string | undefined;
  let markdownFile: string | undefined;
  let imagesDir: string | undefined;
  let accountAlias: string | undefined;
  let expectedAccountId: string | undefined;
  let draftId: string | undefined;
  let cover: string | undefined;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--image' && args[i + 1]) {
      images.push(args[++i]!);
    } else if (arg === '--images' && args[i + 1]) {
      imagesDir = args[++i];
    } else if (arg === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (arg === '--content' && args[i + 1]) {
      content = args[++i];
    } else if (arg === '--markdown' && args[i + 1]) {
      markdownFile = args[++i];
    } else if (arg === '--expected-account-id' && args[i + 1]) {
      expectedAccountId = args[++i];
    } else if (arg === '--submit') {
      submit = true;
    } else if (arg === '--profile' && args[i + 1]) {
      profileDir = args[++i];
    } else if (arg === '--draft-id' && args[i + 1]) {
      draftId = args[++i];
    } else if (arg === '--cover' && args[i + 1]) {
      cover = args[++i];
    } else if (arg === '--account' && args[i + 1]) {
      accountAlias = args[++i];
    }
  }

  const extConfig = loadWechatExtendConfig();
  const resolved = resolveAccount(extConfig, accountAlias);
  if (resolved.name) console.log(`[wechat-browser] Account: ${resolved.name} (${resolved.alias})`);

  if (!profileDir && resolved.alias) {
    profileDir = resolved.chrome_profile_path || getAccountProfileDir(resolved.alias);
  }

  if (!markdownFile && !title) {
    console.error('Error: --title or --markdown is required');
    process.exit(1);
  }
  if (!markdownFile && !content) {
    console.error('Error: --content or --markdown is required');
    process.exit(1);
  }
  if (images.length === 0 && !imagesDir) {
    console.error('Error: --image or --images is required');
    process.exit(1);
  }

  await postToWeChat({ title, content, images: images.length > 0 ? images : undefined, imagesDir, markdownFile, submit, profileDir, expectedAccountId, draftId, cover });
}

if (import.meta.main) await main().catch((err) => {
  console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
