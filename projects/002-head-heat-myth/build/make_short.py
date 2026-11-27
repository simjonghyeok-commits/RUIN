import json
base=open('ep2_built.html',encoding='utf-8').read()
shorts=json.load(open('shorts.json',encoding='utf-8'))
css="""<style>
html,body{width:1080px!important;height:1920px!important;background:#141414!important}
#wrap{position:absolute;left:0;top:520px;width:1920px;height:1080px;transform:scale(.5625);transform-origin:0 0;overflow:hidden}
#cap{bottom:auto!important;top:1210px!important;left:40px!important;right:40px!important}
#cap span{font-size:62px!important;white-space:normal!important;word-break:keep-all;max-width:1000px!important;background:#141414!important}
#title{position:absolute;left:0;right:0;top:110px;text-align:center;font-family:'Black Han Sans';font-size:92px;line-height:1.18;color:#FFD84D;white-space:pre-line}
#cta{position:absolute;left:60px;right:60px;top:1560px;text-align:center;font-family:'Black Han Sans';font-size:66px;color:#141414;background:#FFD84D;border:7px solid #141414;border-radius:24px;padding:22px 10px;opacity:0}
</style>"""
for s in shorts:
  h=base.replace('</head>',css+'</head>')
  h=h.replace('<div id="stage"></div>','<div id="wrap"><div id="stage"></div>').replace('<div id="logo">','</div><div id="logo">',1)
  # logo stays inside wrap -> move logo into wrap: simpler: close wrap after logo
  h=h.replace('</div><div id="logo">','<div id="logo">',1)
  h=h.replace('<div id="cap"></div>','')
  h=h.replace('<script>',f'<div id="cap"></div><div id="title">{s["title"]}</div><div id="cta">{s["cta"]}</div><script>',1)
  # close wrap after logo div
  h=h.replace('<div class="g bh">괜히</div></div>\n<div id="cap">','<div class="g bh">괜히</div></div></div>\n<div id="cap">',1)
  h=h.replace('window.render(0);',f'''const _r=window.render;const T0={s["t0"]},DUR={s["dur"]};
window.render=function(t){{_r(T0+t);document.getElementById('cta').style.opacity=t>DUR-2.6?Math.min(1,(t-(DUR-2.6))/0.3):0;}};window.render(0);''')
  open(f'ep2_short_{s["id"]}.html','w',encoding='utf-8').write(h)
print('ok')
