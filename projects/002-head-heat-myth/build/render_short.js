const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const [html,dur,out]=process.argv.slice(2);
(async()=>{fs.mkdirSync(out,{recursive:true});const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
const N=Math.round(30*Number(dur));
for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/30);await p.screenshot({path:`${out}/f_${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:90});}
await b.close();console.log('frames',N);})();
