# RUIN — 유튜브 채널 「괜히 그런 게 아니야」 제작 프로젝트

## 콘텐츠 제작 공통 지침
모든 콘텐츠 기획·대본·제작·검수는 아래 지침을 공통 기준으로 따른다.

@docs/MASTER_CONTENT_WORKFLOW_V2_LONGFORM.md

## 제작 파이프라인 (3단계, 단계마다 사용자 승인 후 다음 단계로)
1. 텍스트 (기획): AI로 전체 구조와 스토리를 설계한다. 지침 PHASE 01~02 (제작안 템플릿, 대본, 팩트체크 포함).
   - 산출물: 제작안, 확정 대본, 출처 목록. 대본이 확정되면 TTS 음성을 먼저 뽑아 실제 길이를 잰다.
2. 이미지 (사전 검토): 스토리보드 형태로 시각 요소를 테스트한다. 지침 PHASE 03.
   - 산출물: 장면별 스토리보드 이미지, 스타일·캐릭터·배경 레퍼런스 시트, 장면별 프롬프트. 여기서 확정한 이미지가 영상 단계의 레퍼런스가 된다.
3. 영상 (최종 제작): 확정된 레퍼런스로 본편을 생성한다. 지침 PHASE 04~05.
   - 산출물: 장면 영상, 편집본(음성·자막·사운드 싱크), 최종 MP4, 설명란.
- 다음 단계에서 고치면 비용이 커지므로, 사실관계와 대본은 1단계에서, 그림체·구도는 2단계에서 확정한다.

## 제작 예산 단계
- 지금: 무료 제작으로 채널을 키운다. 유료 AI 영상 생성(Higgsfield 등)은 쓰지 않는다.
- 수익이 생기면: 유료 제작(Higgsfield MCP `https://mcp.higgsfield.ai/mcp` 등)으로 퀄리티를 올린다.
- 무료 단계에서는 쇼츠를 먼저 만들고, 화면은 그래픽·모션그래픽 중심(Claude가 HTML+ffmpeg로 렌더링 가능) + 상업 이용 가능한 무료 스톡(Pexels, Pixabay)으로 한다.
- 무료 도구를 쓸 때는 상업적 이용(수익화) 허용 여부를 반드시 확인한다. 비상업 라이선스로 만든 영상은 나중에 수익화하면 문제가 된다.

## 제작 도구 (확정)
- 이미지·영상 생성: Open Generative AI (github.com/Anil-matcha/Open-Generative-AI, MIT). 사용자가 자기 컴퓨터의 데스크톱 앱에서 직접 생성한다.
  - 무료인 것: 로컬 모델만 (이미지: 내장 sd.cpp로 SD 1.5/SDXL/Z-Image, 영상: Wan2GP 별도 설치 + 고성능 GPU 필요).
  - 그 외 모델(Kling, Veo, Flux 등)은 MuAPI를 거치는 유료 생성이다. 무료 단계에서 쓰려면 사용자에게 비용을 먼저 확인한다.
- Claude의 역할: 장면별 이미지·영상 프롬프트, 스타일·캐릭터 레퍼런스 시트 지침 작성 → 사용자가 생성한 파일을 받아 편집·자막·음성 싱크·합성(OpenMontage/FFmpeg/HyperFrames)과 검수.
- 실사 혼합 원칙: AI 이미지·영상만 쓰지 않고, 조사해서 받은 실제 사진·영상·공식 문서를 함께 넣어 AI 느낌을 최소화한다.
  - 우선 출처(상업 이용 가능): 미국 정부 저작물(FAA, eCFR, Federal Register — 퍼블릭 도메인), Wikimedia Commons의 Public domain/CC0/CC BY(CC BY-SA는 동일조건 조건 때문에 피한다), Pexels·Pixabay(무료 API 키 필요).
  - 다른 유튜버·방송·뉴스 영상은 쓰지 않는다(재사용 콘텐츠 정책). 출처와 라이선스는 설명란에 기록한다.
  - 사고·재난 장면은 실제 영상으로 연출하지 않는다(실제 사건의 증거처럼 보이지 않게).
- 클라우드 `ruin` 환경 허용 호스트: api.muapi.ai(키 저장됨, 잔액 확인 후 사용), commons/upload.wikimedia.org, www.ecfr.gov, www.faa.gov, api/images/videos.pexels.com, pixabay.com, cdn.pixabay.com. Wikimedia는 요청이 많으면 429로 막히니 천천히 받는다.
- 실사처럼 보이는 AI 이미지·영상을 쓴 영상은 업로드 시 '변경되거나 합성된 콘텐츠'를 '예'로 표시한다.

## 채널 확정 사항 (다시 묻지 않는다)
- 채널명: 괜히 그런 게 아니야 (YouTube 표기: 「괜히 그런게 아니야」) / 핸들: @괜히그런게아니야
- 주제: 일상 속 "왜?"의 진짜 이유 (생활·물건·음식·몸·교통·여행)
- 끝 멘트: "○○○도… 괜히 그런 게 아니야." / 제목 형식: "○○은 왜 ○○할까?"
- 브랜드: 노랑 #FFD84D, 검정 #141414 / 제목 Black Han Sans, 본문 Noto Sans KR
- 제작 방식: 직접 만든 그래픽 + AI 이미지·영상 + 무료 스톡 영상, 내레이션은 AI 음성(TTS)
- TTS: ElevenLabs Starter(유료)로 확정. 장면별 감정 연기 설계가 기본 제작 지침이다. 키는 `ruin` 환경 network secret(헤더 xi-api-key).
  - 채널 목소리: **Jisun - Warm & Friendly Korean** (voice_id 7Tms2JpTU4QYeCNp0Gtn, 보이스 라이브러리, 추가 요금 없음 rate 1.0)
    - ⚠️ 소유자가 공개를 내리면 사용 보장이 30일뿐이다. 매 영상 음성 원본(mp3)을 저장소에 보관하고, 예비 목소리는 Jiae(3TIJuP53f43TXi08ZJE1, 730일 보장)로 둔다.
  - 모델: **eleven_v4**, language_code ko. Stability 기본값(0.5)부터, Similarity 0.8(Jisun 음색 유지). Style·Speaker Boost·Speed는 v4에서 쓰지 않는다.
  - 감정 연출은 대본 안 Audio Tags로 장면별 설계한다: [curious] [surprised] [excited] [playful] [mischievously] [warmly] [chuckles] [short pause] [dramatically] [serious]
  - 후처리 속도 1.25배속(ffmpeg atempo=1.25). `/with-timestamps` 글자 타이밍을 1.25로 나눠 자막·화면 싱크에 쓴다.
  - Jisun은 말이 느린 편이라(태그 포함 원본 약 43초 → 1.25배 후 약 34초) 쇼츠 목표(30~33초)를 넘기 쉽다. 대본은 200음절 안팎으로 유지한다.
  - 대본 말투: 개구쟁이 크리에이터 톤("어? 이거 뭐야?", "땡!", 의성어).
  - 믹스: 내레이션만 0.9배(약 -0.9dB). 먼저 내레이션 1.0배 믹스에 loudnorm(I=-14, TP=-1.5)을 측정해 그 게인을 구하고, 같은 게인을 내레이션 0.9배 믹스에 적용한 뒤 limiter. 효과음은 0.6배.
- 업로드 기본설정: 카테고리 교육, 언어 한국어, 아동용 아님
- 첫 영상 주제: 비행기 화장실엔 왜 아직 재떨이가 있을까? (14 CFR 25.853 근거. Varig 820편 화재 원인은 담배로 단정하지 않는다)
