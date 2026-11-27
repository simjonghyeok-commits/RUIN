const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const [html,dur,out,fps]=process.argv.slice(2);const FPS=Number(fps||30);
(async()=>{fs.mkdirSync(out,{recursive:true});const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.resolve(html));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
const N=Math.round(FPS*Number(dur));
for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/FPS);await p.screenshot({path:`${out}/f_${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:90});}
await b.close();console.log('frames',N);})();
