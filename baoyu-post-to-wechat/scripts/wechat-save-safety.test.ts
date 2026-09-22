import { test, expect } from 'bun:test';
import { assertBackendAccount } from './wechat-account-guard';
test('backend mismatch stops before writes, matching original ID proceeds', () => {
 let writes=0;
 for (const [expected,actual] of [['wang','suqin'],['wang',''],[undefined,'suqin']]) {
  expect(()=>{assertBackendAccount(expected,actual);writes++;}).toThrow();
 }
 expect(writes).toBe(0);
 assertBackendAccount('gh_test','gh_test'); writes++;
 expect(writes).toBe(1);
});
import { resolveAccount, loadCredentials } from './wechat-extend-config';
import { publishToDraft, uploadToWechat, uploadImagesInHtml } from './wechat-api';
import { compressTitle, compressContent, assertSaveClicked, assertSaveConfirmed } from './wechat-browser';
import { isFreshDraftSave, saveOnlyWhenRequested } from './wechat-article';
const client = (status: number, data: unknown) => (async () => ({ status, json: async () => data })) as any;
const article = { title: 'test', content: '<p>body</p>', thumbMediaId: 'cover', articleType: 'news' } as any;
test('unknown and ambiguous account selection fail closed', () => {
 expect(() => resolveAccount({}, 'wrong')).toThrow('Unknown');
 expect(() => resolveAccount({accounts:[{name:'A',alias:'a'},{name:'B',alias:'b'}]})).toThrow('Select --account');
});
test('selected account cannot use generic credentials or profile', () => {
 const oldId=process.env.WECHAT_APP_ID, oldSecret=process.env.WECHAT_APP_SECRET;
 try { process.env.WECHAT_APP_ID='generic'; process.env.WECHAT_APP_SECRET='secret';
 expect(() => loadCredentials({alias:'nonexistent_test_7264',need_open_comment:1,only_fans_can_comment:0})).toThrow('Missing');
 expect(resolveAccount({chrome_profile_path:'/generic',accounts:[{name:'A',alias:'a'}]},'a').chrome_profile_path).toBeUndefined();
 } finally { if(oldId===undefined) delete process.env.WECHAT_APP_ID; else process.env.WECHAT_APP_ID=oldId; if(oldSecret===undefined) delete process.env.WECHAT_APP_SECRET; else process.env.WECHAT_APP_SECRET=oldSecret; }
});
test('draft API requires HTTP success and media_id', async () => {
 await expect(publishToDraft(article,'fake',client(500,{media_id:'x'}))).rejects.toThrow('HTTP');
 await expect(publishToDraft(article,'fake',client(200,{}))).rejects.toThrow('missing media_id');
 expect((await publishToDraft(article,'fake',client(200,{media_id:'new'}))).media_id).toBe('new');
});
test('image API rejects HTTP and malformed success; failed local body image aborts', async () => {
 await expect(uploadToWechat(Buffer.from('x'),'x.png','image/png','fake','body',client(500,{url:'x'}))).rejects.toThrow('HTTP');
 await expect(uploadToWechat(Buffer.from('x'),'x.png','image/png','fake','material',client(200,{}))).rejects.toThrow('missing');
 await expect(uploadImagesInHtml('<img src="/nonexistent-test-7264.png">','fake','/tmp',[],'news',false,client(200,{}))).rejects.toThrow();
});
test('old appmsgid or stale toast never proves a fresh save', () => {
 const old={appmsgid:'old',isLoading:false,submitText:'',url:'',messages:['保存成功']};
 expect(isFreshDraftSave({...old},old)).toBe(false);
 expect(isFreshDraftSave({...old,appmsgid:'new'},old)).toBe(true);
 expect(isFreshDraftSave({...old,appmsgid:'new',messages:['保存失败']},old)).toBe(false);
});
test('long photo body is rejected without truncation', () => {
 expect(()=>compressContent('a'.repeat(1001))).toThrow('exceeds');
 expect(compressContent('original')).toBe('original');
});

test('browser missing button, absent toast and failed toast fail closed', () => {
 expect(() => assertSaveClicked('not-found')).toThrow('not found');
 expect(() => assertSaveConfirmed([])).toThrow('unconfirmed');
 expect(() => assertSaveConfirmed(['保存失败'])).toThrow('unconfirmed');
 assertSaveClicked('clicked:保存为草稿');
 assertSaveConfirmed(['保存成功']);
});

test('preview cannot invoke save; explicit submit invokes exactly once', async () => {
 let clicks = 0;
 const save = async () => { clicks++; };
 expect(await saveOnlyWhenRequested(false, save)).toBe(false);
 expect(clicks).toBe(0);
 expect(await saveOnlyWhenRequested(true, save)).toBe(true);
 expect(clicks).toBe(1);
});

test('approved photo title is never rewritten and stale photo toast is rejected', () => {
 expect(compressTitle('原来的标题')).toBe('原来的标题');
 expect(()=>compressTitle('如何'+ '甲'.repeat(21))).toThrow('exceeds');
 expect(()=>assertSaveConfirmed(['保存成功'], ['保存成功'])).toThrow('unconfirmed');
});

import { extractArticleHtml } from './wechat-html';
test('all save paths consume only approved HTML and retain inline root styles', () => {
 const fragment='<section id="article" style="color:blue"><h2>题</h2><p><strong>内容</strong></p><img src="1.png"><img src="2.png"><img src="10.png"></section>';
 const result=extractArticleHtml('<body>OUTSIDE_SENTINEL<button>复制</button>'+fragment+'</body>');
 expect(result).not.toContain('OUTSIDE_SENTINEL');
 expect(result).toContain('style="color:blue"');
 expect(result.indexOf('1.png')).toBeLessThan(result.indexOf('2.png'));
 expect(result.indexOf('2.png')).toBeLessThan(result.indexOf('10.png'));
 expect(()=>extractArticleHtml('<body><button>复制</button><p>文</p></body>')).toThrow();
 expect(()=>extractArticleHtml(fragment+fragment)).toThrow();
});

import { saveCurrentDraft } from './wechat-save-current';
test('actual save entry gates account/title/button and returns pending readback only', async () => {
 let writes=0, reads=0;
 const evaluator=async(expression:string)=>{
  if(expression.includes('user_name'))return 'gh_a';
  if(expression.includes('data-placeholder'))return 'title';
  if(expression.includes('b.click()')){writes++;return true;}
  reads++;return {id:reads>1?'draft-1':'',href:`https://example.test/${reads}`,messages:[]};
 };
 await expect(saveCurrentDraft(evaluator,'gh_b','title')).rejects.toThrow('mismatch');
 await expect(saveCurrentDraft(evaluator,'gh_a','wrong')).rejects.toThrow('Title mismatch');
 expect(writes).toBe(0);
 const result=await saveCurrentDraft(evaluator,'gh_a','title');
 expect(writes).toBe(1);expect(result.draft_id).toBe('draft-1');expect(result.status).toBe('saved_pending_readback');
});
test('article draft saver targets the visible save label, never the publish container', async () => {
 let clickExpression=''; let reads=0;
 const evaluator=async(expression:string)=>{
  if(expression.includes('user_name'))return 'gh_a';
  if(expression.includes('data-placeholder'))return 'title';
  if(expression.includes('b.click()')){clickExpression=expression;return true;}
  reads++;return {id:reads>1?'draft-1':'',href:`https://example.test/${reads}`,messages:[]};
 };
 await saveCurrentDraft(evaluator,'gh_a','title');
 expect(clickExpression).toContain("==='保存为草稿'");
 expect(clickExpression).not.toContain('#js_submit');
});
test('actual save entry never accepts stale draft id, missing button or failure notice', async () => {
 const base=async(expression:string)=>{
  if(expression.includes('user_name'))return 'gh_a';
  if(expression.includes('data-placeholder'))return 'title';
  if(expression.includes('b.click()'))return true;
  return {id:'old',href:'https://example.test/old',messages:['保存成功']};
 };
 await expect(saveCurrentDraft(base,'gh_a','title',1)).rejects.toThrow('unknown');
 await expect(saveCurrentDraft(async e=>e.includes('b.click()')?false:base(e),'gh_a','title')).rejects.toThrow('button');
 await expect(saveCurrentDraft(async e=>e.includes('messages:Array')?{id:'new',messages:['保存失败']}:base(e),'gh_a','title')).rejects.toThrow('not confirmed');
});
test('actual save entry accepts an existing draft only after its editor URL changes', async () => {
 let reads=0;
 const evaluator=async(expression:string)=>{
  if(expression.includes('user_name'))return 'gh_a';
  if(expression.includes('data-placeholder'))return 'title';
  if(expression.includes('b.click()'))return true;
  reads++;
  return {id:'draft-1',href:reads>1?'https://example.test/edit?appmsgid=draft-1&saved=1':'https://example.test/edit?appmsgid=draft-1',messages:[]};
 };
 const result=await saveCurrentDraft(evaluator,'gh_a','title');
 expect(result.draft_id).toBe('draft-1');
});
