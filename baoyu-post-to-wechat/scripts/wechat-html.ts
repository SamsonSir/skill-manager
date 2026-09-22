import { load } from 'cheerio';

// One extraction contract for API and browser paths. Keep the styled root itself.
export function extractArticleHtml(source: string): string {
  const $ = load(source);
  const articles = $('#article');
  const outputs = $('#output');
  const gzh = $('#gzh-content');
  if (articles.length > 1 || outputs.length > 1 || gzh.length > 1) throw new Error('Ambiguous article regions');
  const region = articles.length ? articles : outputs.length ? outputs : gzh.length ? gzh : $('body');
  if (region.find('button,script,style,input,textarea,select,iframe,form').length) {
    throw new Error('Article contains preview controls or non-inline content; provide article.html');
  }
  if (!region.text().trim() && !region.find('img').length) throw new Error('Empty article');
  return region.is('body') ? region.html()!.trim() : $.html(region);
}
