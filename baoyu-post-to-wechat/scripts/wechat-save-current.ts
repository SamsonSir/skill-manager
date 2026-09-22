import { assertBackendAccount, ACCOUNT_ID_EXPRESSION } from './wechat-account-guard.ts';
type Evaluate = (expression: string) => Promise<any>;
export async function saveCurrentDraft(evaluate: Evaluate, expectedAccountId: string, expectedTitle: string, timeoutMs=15000) {
  assertBackendAccount(expectedAccountId, await evaluate(ACCOUNT_ID_EXPRESSION));
  const title = await evaluate(`document.querySelector('.ProseMirror[data-placeholder]')?.textContent || document.querySelector('#title')?.value || ''`);
  if (!expectedTitle || title !== expectedTitle) throw new Error('Title mismatch; draft not saved');
  const read = () => evaluate(`(() => ({id:new URL(location.href).searchParams.get('appmsgid') || '',href:location.href,messages:Array.from(document.querySelectorAll('.weui-desktop-toast,.weui-desktop-toptips,.js_tips')).map(e=>(e.textContent||'').trim()).filter(Boolean)}))()`);
  const before = await read();
  // `#js_submit` is the publish action on the current WeChat editor.  Never
  // use its first button as a save fallback: doing so can schedule/publish an
  // article when the caller requested a draft.  Match the visible save label
  // exactly and fail closed if WeChat changes that control.
  const clicked = await evaluate(`(() => {const b=Array.from(document.querySelectorAll('button')).find(e=>(e.textContent||'').trim()==='保存为草稿' && e.getBoundingClientRect().width>0);if(!b||b.disabled)return false;b.click();return true})()`);
  if (!clicked) throw new Error('Save button missing or disabled; no save issued');
  const start=Date.now();
  while(Date.now()-start<timeoutMs) {
    const current=await read();
    if(current.messages.some((m:string)=>/失败|错误|fail|error/i.test(m))) throw new Error('Save not confirmed; reconcile existing attempt before retry');
    if(current.id && (current.id!==before.id || current.href!==before.href || current.messages.some((m:string)=>!before.messages.includes(m)&&/保存成功|已保存/.test(m)))) return {draft_id:current.id,account_id:expectedAccountId,title,status:'saved_pending_readback'};
    await new Promise(r=>setTimeout(r,500));
  }
  throw new Error('Save outcome unknown; reconcile draft list, do not create another draft');
}
