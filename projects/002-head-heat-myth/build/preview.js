const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+path.resolve('ep2_built.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
for(const t of process.argv.slice(2).map(Number)){await p.evaluate(t=>window.render(t),t);await p.screenshot({path:`pv_${t}.jpg`,type:'jpeg',quality:70});}
console.log('errors',errs);await b.close();})();
