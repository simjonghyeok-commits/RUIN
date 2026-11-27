const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await p.goto('file://'+path.resolve('index.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
const FPS=30,DUR=32.4,N=Math.round(FPS*DUR);
for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/FPS);await p.screenshot({path:`frames/f_${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close();console.log('frames',N);})();
