# 001 빌드 방법
- index.html: 9:16 장면·자막 타임라인(window.render(t)). 실사 이미지는 assets/real 에서 복사해 같은 폴더에 둔다(door_latch_cc0.jpg, lavatory_pd.jpg, sign_crop.jpg).
- 폰트: @fontsource/black-han-sans, @fontsource/noto-sans-kr 를 ../brand/node_modules 경로에 설치(npm i @fontsource/black-han-sans@5 @fontsource/noto-sans-kr@5).
- 효과음: sfx/*.wav (ffmpeg로 합성) → bash mix.sh → sfx_mix.wav
- 렌더: node render.js (945프레임, 30fps) → ffmpeg -framerate 30 -i frames/f_%04d.jpg -i sfx_mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4
- 내레이션이 생기면 실제 음성 길이에 맞춰 CAPS/SC 타이밍을 조정하고 sfx와 함께 믹스한다.

## 최종본(ep001_final.mp4) 오디오 처리
- 내레이션: assets/audio/narration_capcut_original.wav (CapCut TTS, 38.4초) → 앞 0.15초 자르고 atempo=1.2 → 31.8초
- index.html의 A 배열이 원래 타임라인(초안) → 내레이션 실제 타이밍으로 구간별 매핑한다.
- 효과음 시각: ding 1.28, scratch 2.65, tok 7.63/9.05/10.45, buzz 13.93, thump 15.48, dingdong 17.95, fire 22.58, thump 24.4, chime 30.79 (각 0.6배 볼륨)
- 마스터: loudnorm I=-14 LUFS, TP -1.5
