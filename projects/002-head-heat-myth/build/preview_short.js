const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
const [html,...ts]=process.argv.slice(2);const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
for(const t of ts.map(Number)){await p.evaluate(t=>window.render(t),t);await p.screenshot({path:`sp_${path.basename(html,'.html')}_${t}.jpg`,type:'jpeg',quality:70});}
console.log('errors',errs);await b.close();})();
