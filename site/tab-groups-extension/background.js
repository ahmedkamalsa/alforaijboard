const GROUPS=[
  {title:'🏠 الفريج', color:'blue', patterns:['alforaijboard','alforaij','bwspcsiazbwrrxpgoldx']},
  {title:'🤖 Hermes', color:'orange', patterns:['hermes-orchestrated','zsemkiomjgrqjjogmrwv','ahmedkamalsa/hermes']},
  {title:'🔍 بحث', color:'green', patterns:['openrouter','aistudio.google','youtube.com','google.com/search']},
  {title:'🛠 تطوير', color:'grey', patterns:['github.com/ahmedkamalsa/alforaijboard/actions','supabase.com/dashboard']}
];
function match(url, pats){ url=(url||'').toLowerCase(); return pats.some(p=>url.includes(p.toLowerCase())); }
async function groupAll(){
  const tabs=await chrome.tabs.query({currentWindow:true});
  let grouped=0, groups=0;
  for(const g of GROUPS){
    const ids=tabs.filter(t=>match(t.url||'', g.patterns)).map(t=>t.id).filter(Boolean);
    if(!ids.length) continue;
    const gid=await chrome.tabs.group({tabIds: ids});
    await chrome.tabGroups.update(gid, {title: g.title, color: g.color, collapsed: true});
    grouped+=ids.length; groups++;
  }
  return {grouped, groups};
}
chrome.runtime.onMessage.addListener((msg, sender, sendResponse)=>{
  if(msg && msg.type==='GROUP_TABS'){
    groupAll().then(r=>sendResponse({ok:true, ...r})).catch(e=>sendResponse({ok:false, error:String(e)}));
    return true;
  }
});
chrome.action.onClicked.addListener(async ()=>{
  const r=await groupAll();
  chrome.notifications && chrome.notifications.create({type:'basic', iconUrl:'', title:'تم التجميع', message: groupedToText(r)});
});
function groupedToText(r){ return `تم ${r.grouped} تبويب في ${r.groups} مجموعات — مطوية`; }
