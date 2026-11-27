const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await p.goto('file://'+path.resolve('index.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
const ts=process.argv.slice(2).map(Number);
for(const t of ts){await p.evaluate(t=>window.render(t),t);await p.screenshot({path:`pv_${t}.jpg`,type:'jpeg',quality:80});}
await b.close();})();
