import { test, expect } from 'bun:test';
import { resolveAccount, loadCredentials } from './wechat-extend-config';
import { publishToDraft, uploadToWechat, uploadImagesInHtml } from './wechat-api';
import { compressContent, assertSaveClicked, assertSaveConfirmed } from './wechat-browser';
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
