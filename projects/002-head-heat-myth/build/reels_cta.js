// Renders transparent CTA overlays for Instagram Reels versions of the Shorts.
const {chromium}=require('playwright');const path=require('path');
// const FONT='/tmp/claude-0/-home-user-ruin/3ee854b6-f432-5f43-9048-63580097820d/scratchpad/brand/node_modules/@fontsource/black-han-sans/files/black-han-sans-korean-400-normal.woff2';
const items=JSON.parse(process.argv[2]);
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const [id,text] of items){
 for(const layer of ['bg','cta']){
  const fs=require('fs');fs.writeFileSync('_reels_tmp.html',`<html><head><link rel=stylesheet href='file:///tmp/claude-0/-home-user-ruin/3ee854b6-f432-5f43-9048-63580097820d/scratchpad/brand/node_modules/@fontsource/black-han-sans/index.css'><style>
 html,body{margin:0;background:transparent}
 #bg{position:absolute;left:30px;right:30px;top:1540px;height:200px;background:#141414}
 #cta{position:absolute;left:60px;right:60px;top:1425px;text-align:center;font-family:\'Black Han Sans\';font-size:60px;color:#141414;background:#FFD84D;border:7px solid #141414;border-radius:24px;padding:16px 10px;white-space:nowrap}
 </style></head><body>${layer==='bg'?'<div id="bg"></div>':`<div id="cta">${text}</div>`}</body></html>`);await p.goto('file://'+path.resolve('_reels_tmp.html'));
  await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(200);
  if(layer==='cta'){await p.evaluate(()=>{const c=document.getElementById('cta');let f=60;while(c.scrollWidth>c.clientWidth&&f>40){f-=2;c.style.fontSize=f+'px';}});}
  await p.screenshot({path:`reels_${layer}_${id}.png`,omitBackground:true});
 }}
await b.close();console.log('ok');})();
