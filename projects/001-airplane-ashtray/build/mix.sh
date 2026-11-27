cd "$(dirname "$0")/sfx"
EV="ding:0.9 scratch:3.3 tok:8.4 tok:9.6 tok:10.8 buzz:13.4 thump:15.0 dingdong:17.7 fire:23.2 thump:25.3 chime:29.9"
IN=""; FC=""; i=0
for e in $EV; do n=${e%%:*}; t=${e##*:}; IN="$IN -i $n.wav"; ms=$(python3 -c "print(int($t*1000))"); FC="$FC[$i]adelay=${ms}|${ms}[a$i];"; i=$((i+1)); done
L=""; for j in $(seq 0 $((i-1))); do L="$L[a$j]"; done
ffmpeg -loglevel error -y $IN -f lavfi -t 31.5 -i anullsrc=r=48000:cl=stereo -filter_complex "${FC}${L}[$i]amix=inputs=$((i+1)):normalize=0,atrim=0:31.5[out]" -map "[out]" ../sfx_mix.wav
