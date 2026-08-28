#!/usr/bin/env bash
# export-pdf.sh — Export an HTML presentation to PDF
#
# Usage:
#   bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
info() { echo -e "${CYAN}ℹ${NC} $*"; }
ok()   { echo -e "${GREEN}✓${NC} $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }

VIEWPORT_W=1920; VIEWPORT_H=1080; COMPACT=false
POSITIONAL=()
for arg in "$@"; do
    case $arg in --compact) COMPACT=true; VIEWPORT_W=1280; VIEWPORT_H=720 ;;
    *) POSITIONAL+=("$arg") ;; esac
done
set -- "${POSITIONAL[@]}"

[[ $# -lt 1 ]] && { err "Usage: bash scripts/export-pdf.sh <path-to-html> [output.pdf] [--compact]"; exit 1; }
INPUT_HTML="$1"
[[ ! -f "$INPUT_HTML" ]] && { err "File not found: $INPUT_HTML"; exit 1; }
INPUT_HTML=$(cd "$(dirname "$INPUT_HTML")" && pwd)/$(basename "$INPUT_HTML")

if [[ $# -ge 2 ]]; then OUTPUT_PDF="$2"
else OUTPUT_PDF="$(dirname "$INPUT_HTML")/$(basename "$INPUT_HTML" .html).pdf"; fi
OUTPUT_DIR=$(dirname "$OUTPUT_PDF"); mkdir -p "$OUTPUT_DIR"
OUTPUT_PDF="$OUTPUT_DIR/$(basename "$OUTPUT_PDF")"

echo ""; echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       Export Slides to PDF            ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"; echo ""

! command -v npx &>/dev/null && { err "Node.js required. Install: brew install node"; exit 1; }
ok "Node.js found"

TEMP_DIR=$(mktemp -d)
TEMP_SCRIPT="$TEMP_DIR/export-slides.mjs"
SERVE_DIR=$(dirname "$INPUT_HTML")
HTML_FILENAME=$(basename "$INPUT_HTML")

cat > "$TEMP_SCRIPT" << 'EXPORT_SCRIPT'
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFileSync, mkdirSync, unlinkSync } from 'fs';
import { join, extname } from 'path';

const SERVE_DIR = process.argv[2];
const HTML_FILE = process.argv[3];
const OUTPUT_PDF = process.argv[4];
const SCREENSHOT_DIR = process.argv[5];
const VP_WIDTH = parseInt(process.argv[6]) || 1920;
const VP_HEIGHT = parseInt(process.argv[7]) || 1080;

const MIME_TYPES = { '.html':'text/html','.css':'text/css','.js':'application/javascript','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif','.svg':'image/svg+xml','.webp':'image/webp' };

const server = createServer((req, res) => {
  const decodedUrl = decodeURIComponent(req.url);
  let filePath = join(SERVE_DIR, decodedUrl === '/' ? HTML_FILE : decodedUrl);
  try {
    const content = readFileSync(filePath);
    const ext = extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
    res.end(content);
  } catch { res.writeHead(404); res.end('Not found'); }
});

const port = await new Promise((resolve) => { server.listen(0, () => resolve(server.address().port)); });
console.log(`  Local server on port ${port}`);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: VP_WIDTH, height: VP_HEIGHT } });
await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(1500);

const slideCount = await page.evaluate(() => document.querySelectorAll('.slide').length);
console.log(`  Found ${slideCount} slides`);
if (slideCount === 0) { console.error('  ERROR: No .slide elements found.'); await browser.close(); server.close(); process.exit(1); }

mkdirSync(SCREENSHOT_DIR, { recursive: true });
const screenshotPaths = [];

for (let i = 0; i < slideCount; i++) {
  await page.evaluate((index) => {
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide, idx) => {
      if (idx === index) { slide.style.display = ''; slide.style.opacity = '1'; slide.classList.add('active'); }
      else { slide.style.display = 'none'; slide.classList.remove('active'); }
    });
    slides[index]?.scrollIntoView({ behavior: 'instant' });
  }, i);
  await page.waitForTimeout(300);
  await page.evaluate((index) => {
    const slides = document.querySelectorAll('.slide');
    slides[index]?.querySelectorAll('.reveal').forEach(el => { el.style.opacity = '1'; el.style.transform = 'none'; });
  }, i);
  await page.waitForTimeout(100);
  const screenshotPath = join(SCREENSHOT_DIR, `slide-${String(i + 1).padStart(3, '0')}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  screenshotPaths.push(screenshotPath);
  console.log(`  Captured slide ${i + 1}/${slideCount}`);
}
await browser.close(); server.close();

console.log('  Assembling PDF...');
const browser2 = await chromium.launch();
const pdfPage = await browser2.newPage();
const imagesHtml = screenshotPaths.map((p) => {
  const imgData = readFileSync(p).toString('base64');
  return `<div class="page"><img src="data:image/png;base64,${imgData}" /></div>`;
}).join('\n');

await pdfPage.setContent(`<!DOCTYPE html><html><head><style>*{margin:0;padding:0;}@page{size:${VP_WIDTH}px ${VP_HEIGHT}px;margin:0;}.page{width:${VP_WIDTH}px;height:${VP_HEIGHT}px;page-break-after:always;overflow:hidden;}.page:last-child{page-break-after:auto;}img{width:${VP_WIDTH}px;height:${VP_HEIGHT}px;display:block;object-fit:contain;}</style></head><body>${imagesHtml}</body></html>`, { waitUntil: 'load' });
await pdfPage.pdf({ path: OUTPUT_PDF, width: `${VP_WIDTH}px`, height: `${VP_HEIGHT}px`, printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
await browser2.close();
screenshotPaths.forEach(p => unlinkSync(p));
console.log(`  ✓ PDF saved to: ${OUTPUT_PDF}`);
EXPORT_SCRIPT

info "Setting up Playwright..."; echo ""
cd "$TEMP_DIR"
cat > "$TEMP_DIR/package.json" << 'PKG'
{ "name": "slide-export", "private": true, "type": "module" }
PKG
npm install playwright &>/dev/null || { err "Failed to install Playwright."; rm -rf "$TEMP_DIR"; exit 1; }
npx playwright install chromium 2>/dev/null || { err "Failed to install Chromium."; rm -rf "$TEMP_DIR"; exit 1; }
ok "Playwright ready"; echo ""

SCREENSHOT_DIR="$TEMP_DIR/screenshots"
info "Exporting slides to PDF..."; echo ""
[[ "$COMPACT" == "true" ]] && info "Using compact mode (1280×720)"

node "$TEMP_SCRIPT" "$SERVE_DIR" "$HTML_FILENAME" "$OUTPUT_PDF" "$SCREENSHOT_DIR" "$VIEWPORT_W" "$VIEWPORT_H" || {
    err "PDF export failed."; rm -rf "$TEMP_DIR"; exit 1
}
rm -rf "$TEMP_DIR"

echo ""; echo -e "${BOLD}════════════════════════════════════════${NC}"
ok "PDF exported successfully!"; echo ""
echo -e "  ${BOLD}File:${NC}  $OUTPUT_PDF"
FILE_SIZE=$(du -h "$OUTPUT_PDF" | cut -f1 | xargs); echo "  Size: $FILE_SIZE"
echo -e "${BOLD}════════════════════════════════════════${NC}"; echo ""
command -v open &>/dev/null && open "$OUTPUT_PDF" || command -v xdg-open &>/dev/null && xdg-open "$OUTPUT_PDF"
