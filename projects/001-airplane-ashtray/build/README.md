# 001 빌드 방법
- index.html: 9:16 장면·자막 타임라인(window.render(t)). 실사 이미지는 assets/real 에서 복사해 같은 폴더에 둔다(door_latch_cc0.jpg, lavatory_pd.jpg, sign_crop.jpg).
- 폰트: @fontsource/black-han-sans, @fontsource/noto-sans-kr 를 ../brand/node_modules 경로에 설치(npm i @fontsource/black-han-sans@5 @fontsource/noto-sans-kr@5).
- 효과음: sfx/*.wav (ffmpeg로 합성) → bash mix.sh → sfx_mix.wav
- 렌더: node render.js (945프레임, 30fps) → ffmpeg -framerate 30 -i frames/f_%04d.jpg -i sfx_mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4
- 내레이션이 생기면 실제 음성 길이에 맞춰 CAPS/SC 타이밍을 조정하고 sfx와 함께 믹스한다.
