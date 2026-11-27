import json,sys
F='/tmp/claude-0/-home-user-ruin/3ee854b6-f432-5f43-9048-63580097820d/scratchpad/brand/node_modules'
h=open('ep2.html',encoding='utf-8').read().replace('FONTDIR','file://'+F).replace('__TIMELINE__',open('timeline.json',encoding='utf-8').read())
open('ep2_built.html','w',encoding='utf-8').write(h)
