"""EP2 타임라인 빌더: 챕터 음성(1.25배속) 이어붙이기 + 자막 큐 + 장면 앵커 → timeline.json, narration.wav"""
import json, re, subprocess, os

P = os.path.dirname(os.path.abspath(__file__)) + '/../'
A = P + 'assets/audio/'
K = 1.25            # 후처리 배속
GAP = 0.6           # 챕터 사이 기본 쉼
CARD = 1.4          # 챕터 제목 카드 길이(무음)
THINK = 3.0         # 퀴즈 생각할 시간

segs = json.load(open(P + 'script_v2_tags.json', encoding='utf-8'))
order = [s['id'] for s in segs]
titles = {s['id']: s['title'] for s in segs}
chapter_card = {'ch1', 'ch2', 'ch3', 'ch4', 'ch5'}


def dur(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode())


def run(*a):
    subprocess.run(a, check=True)


pieces = []   # (kind, path or seconds)
t = 0.0
offsets = {}
inserts = {}  # seg -> [(local_time_after_speedup, seconds)]
cards = []
think = []
for sid in order:
    al = json.load(open(A + f'{sid}_align.json', encoding='utf-8'))
    chars = al['characters']
    s = ''.join(chars)
    if sid in chapter_card:
        cards.append({'t': round(t, 3), 'dur': CARD, 'title': titles[sid]})
        pieces.append(('sil', CARD)); t += CARD
    fast = A + f'{sid}_fast.wav'
    run('ffmpeg', '-loglevel', 'error', '-y', '-i', A + f'{sid}.mp3', '-af', f'atempo={K},aresample=48000', '-ac', '2', fast)
    if sid == 'quiz1':
        cut = al['character_start_times_seconds'][s.index('[warmly] 답은')] / K
        a1, a2 = A + 'quiz1_a.wav', A + 'quiz1_b.wav'
        run('ffmpeg', '-loglevel', 'error', '-y', '-i', fast, '-t', f'{cut:.3f}', a1)
        run('ffmpeg', '-loglevel', 'error', '-y', '-i', fast, '-ss', f'{cut:.3f}', a2)
        offsets[sid] = [(0, t), (cut, t + THINK)]  # 로컬 cut 이후는 THINK만큼 밀림
        think.append({'t': round(t + cut, 3), 'dur': THINK})
        pieces += [('f', a1), ('sil', THINK), ('f', a2)]
        t += dur(fast) + THINK
    else:
        offsets[sid] = [(0, t)]
        pieces.append(('f', fast)); t += dur(fast)
        if sid == 'quiz2':
            think.append({'t': round(t, 3), 'dur': THINK})
            pieces.append(('sil', THINK)); t += THINK
    pieces.append(('sil', GAP)); t += GAP
END = t + 1.5

# 이어붙이기
lst = []
for i, (k, v) in enumerate(pieces):
    if k == 'sil':
        f = A + f'_sil_{i}.wav'
        run('ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-t', f'{v:.3f}', '-i', 'anullsrc=r=48000:cl=stereo', f)
        lst.append(f)
    else:
        lst.append(v)
with open(A + '_concat.txt', 'w') as fh:
    for f in lst:
        fh.write(f"file '{f}'\n")
run('ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', A + '_concat.txt', '-c', 'pcm_s16le', A + 'narration_full.wav')


def gtime(sid, local):
    """원본 로컬 시간(초) → 전체 타임라인 시간"""
    l = local / K
    base = offsets[sid][0][1]
    if len(offsets[sid]) > 1 and l >= offsets[sid][1][0]:
        return base + l + THINK
    return base + l


def anchor(sid, phrase, end=False, nth=1):
    al = json.load(open(A + f'{sid}_align.json', encoding='utf-8'))
    s = ''.join(al['characters'])
    i = -1
    for _ in range(nth):
        i = s.index(phrase, i + 1)
    j = i + len(phrase) - 1 if end else i
    return round(gtime(sid, (al['character_end_times_seconds'] if end else al['character_start_times_seconds'])[j]), 3)


# 자막 큐 (태그 제거, 문장/쉼표 단위)
caps = []
for sid in order:
    al = json.load(open(A + f'{sid}_align.json', encoding='utf-8'))
    ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    intag = False
    buf, bst, ben = '', None, None
    def flush():
        global buf, bst, ben
        txt = buf.strip().replace('\n', ' ')
        if txt:
            caps.append({'t0': round(gtime(sid, bst), 3), 't1': round(gtime(sid, ben), 3), 'text': txt})
        buf, bst, ben = '', None, None
    for c, a, b in zip(ch, st, en):
        if c == '[': intag = True; continue
        if c == ']': intag = False; continue
        if intag: continue
        if c == '\n':
            flush(); continue
        if not buf.strip() and c == ' ':
            continue
        if bst is None: bst = a
        buf += c; ben = b
        n = len(buf.strip())
        if c in '.?!' and n >= 6:
            flush()
        elif c == ',' and n >= 12:
            flush()
        elif n >= 26 and c == ' ':
            flush()
    flush()
import re as _re
caps = [c for c in caps if _re.sub(r'[\s\"\'.,!?…“”]', '', c['text'])]
for c in caps:
    if c['text'].count('"') == 1:
        c['text'] = c['text'].replace('"', '')
# 큐 사이 빈틈 메우기(짧은 공백은 앞 자막 유지)
for a, b in zip(caps, caps[1:]):
    if b['t0'] - a['t1'] < 0.35:
        a['t1'] = b['t0']

json.dump({'end': round(END, 3), 'cards': cards, 'think': think, 'caps': caps,
           'offsets': offsets}, open(P + 'build/timeline_base.json', 'w'), ensure_ascii=False, indent=1)
print('END', round(END, 1), 'caps', len(caps))

# 장면 앵커 (장면 시작 시각)
S = lambda *a, **k: anchor(*a, **k)
scenes = [
 {'t': 0, 'type': 'photo', 'src': 'knit_hat.jpg', 'pos': '50% 25%', 'bubble': {'t': S('intro', '"모자 써'), 'text': '"모자 써!"'}},
 {'t': S('intro', '실제로 미국'), 'type': 'evidence', 'head': '미국 육군 생존 교범', 'src': 'U.S. Army survival manual',
  'quote': ['추울 땐 머리를 꼭 가려라', '머리로 체온의 <mark>40~45%</mark>가 빠진다'], 'ko': '오랫동안 상식처럼 퍼진 숫자', 'note': '교범 조언의 요지 (원문 인용 아님)'},
 {'t': S('intro', '그런데 이 숫자'), 'type': 'big', 'text': '40~45%', 'stamp': {'t': S('intro', '틀렸습니다'), 'text': '틀림'}},
 {'t': S('intro', '더 이상한'), 'type': 'loops', 'items': [
     {'t': S('intro', '진짜 실험'), 'text': '진짜 실험에서 나온 숫자?'},
     {'t': S('intro', '딱 한 가지'), 'text': '빠진 한 가지는?'},
     {'t': S('intro', '정말로 맞는'), 'text': '정말 맞는 사람은?'}]},
 {'t': S('quiz1', '먼저 골라'), 'type': 'quiz', 'q': 'Q1. 머리로 빠지는 열은?', 'opts': ['절반 가까이', '4분의 1 정도', '10% 안팎'],
  'optT': [S('quiz1', '하나,'), S('quiz1', '둘,'), S('quiz1', '셋,')], 'think': think[0]['t'], 'hold': S('quiz1', '답은 조금')},
 {'t': cards[0]['t'], 'type': 'card', 'n': '1', 'title': '숫자의 출처'},
 {'t': S('ch1', '미국 육군'), 'type': 'evidence', 'head': '미국 육군 생존 교범', 'src': 'U.S. Army survival manual',
  'quote': ['추울 땐 머리를 꼭 가려라', '머리로 체온의 <mark>40~45%</mark>'], 'ko': '군대 교범 → 부모님 잔소리', 'note': '교범 조언의 요지 (원문 인용 아님)'},
 {'t': S('ch1', '군대 교범에'), 'type': 'illo', 'id': 'door'},
 {'t': S('ch1', '그럼 이 숫자는'), 'type': 'illo', 'id': 'cold'},
 {'t': S('ch1', '그런데 이 실험'), 'type': 'illo', 'id': 'magnify'},
 {'t': cards[1]['t'], 'type': 'card', 'n': '2', 'title': '실험의 함정'},
 {'t': S('ch2', '참가자들은'), 'type': 'illo', 'id': 'arctic', 'arrowsT': S('ch2', '열은 어디로든')},
 {'t': S('ch2', '이 숫자가 왜'), 'type': 'illo', 'id': 'pants', 'eqT': S('ch2', '바지 없이')},
 {'t': S('ch2', '그럼 공정하게'), 'type': 'illo', 'id': 'scale'},
 {'t': cards[2]['t'], 'type': 'card', 'n': '3', 'title': '진짜 숫자'},
 {'t': S('ch3', '2006년'), 'type': 'illo', 'id': 'tank', 'dipT': S('ch3', '물속에 넣기')},
 {'t': S('ch3', '결과는 단순'), 'type': 'illo', 'id': 'area', 'plusT': S('ch3', '그런데 머리까지')},
 {'t': S('ch3', '2008년에는'), 'type': 'evidence', 'head': '영국의학저널 BMJ (2008)', 'src': 'Vreeman & Carroll, “Festive medical myths”, BMJ 2008;337:a2769',
  'quote': ['수영복만 입은 사람으로 실험했다면', '머리로 잃는 열은 <mark>많아야 10%</mark>'], 'ko': '머리가 특별히 열을 더 잃는 게 아니다', 'note': '논문 내용 요약 (원문 인용 아님)'},
 {'t': S('ch3', '그러니까 퀴즈'), 'type': 'quiz', 'q': 'Q1. 머리로 빠지는 열은?', 'opts': ['절반 가까이', '4분의 1 정도', '10% 안팎'], 'reveal': 2, 'revealT': S('ch3', '3번'), 'all': True},
 {'t': S('quiz2', '그럼 여기서'), 'type': 'quiz', 'q': 'Q2. 그럼 모자는?', 'opts': ['쓸데없다', '체온 지키기 1순위', '사람에 따라 다르다'],
  'optT': [S('quiz2', '하나,'), S('quiz2', '둘,'), S('quiz2', '셋,')], 'think': think[1]['t']},
 {'t': cards[3]['t'], 'type': 'card', 'n': '4', 'title': '반전 ① 그래도 모자'},
 {'t': S('ch4', '여기서'), 'type': 'big', 'text': '절반만 정답', 'small': '"모자 안 써도 되네?"'},
 {'t': S('ch4', '머리가 특별히'), 'type': 'illo', 'id': 'coat'},
 {'t': S('ch4', '그리고 아까'), 'type': 'evidence', 'head': 'J Appl Physiol (2006)', 'src': 'Pretorius et al. 2006, 찬물 머리 담금 실험',
  'quote': ['머리를 찬물에 담그자', '전체 열 손실은 <mark>약 10%</mark> 증가', '중심 체온 하강 속도는 <mark>평균 42%</mark> 증가'], 'ko': '빠진 열은 조금, 몸은 훨씬 빨리 식었다', 'note': '논문 초록 요약 (원문 인용 아님)'},
 {'t': S('ch4', '그러니까 결론은'), 'type': 'photo', 'src': 'knit_hat.jpg', 'pos': '50% 70%', 'tags': ['모자', '장갑', '목도리']},
 {'t': S('ch4', '그런데 이 잔소리'), 'type': 'illo', 'id': 'babyTease'},
 {'t': cards[4]['t'], 'type': 'card', 'n': '5', 'title': '반전 ② 신생아 모자'},
 {'t': S('ch5', '아기가 태어나면'), 'type': 'illo', 'id': 'baby'},
 {'t': S('ch5', '신생아는 몸에'), 'type': 'illo', 'id': 'proportion', 'x3T': S('ch5', '게다가')},
 {'t': S('ch5', '1981년'), 'type': 'evidence', 'head': 'Archives of Disease in Childhood (1981)', 'src': 'Stothers, “Head insulation and heat loss in the newborn” 56(7):530–4',
  'quote': ['만삭 신생아 13명, 27°C', '솜 덧댄 모자 → 전체 열 손실 <mark>75%</mark>로', '배에 두른 띠 → 효과 없음'], 'ko': '아기에게는 머리가 정말 큰 구멍', 'note': '논문 초록 요약 (원문 인용 아님)'},
 {'t': S('ch5', '재미있는 건'), 'type': 'illo', 'id': 'noeffect', 'bandT': S('ch5', '얇은 붕대')},
 {'t': S('ch5', '그러니까 퀴즈'), 'type': 'quiz', 'q': 'Q2. 그럼 모자는?', 'opts': ['쓸데없다', '체온 지키기 1순위', '사람에 따라 다르다'], 'reveal': 2, 'revealT': S('ch5', '3번'), 'all': True},
 {'t': S('ending', '정리해 볼게요'), 'type': 'recap', 'items': [
     {'t': S('ending', '첫째'), 'text': '절반이 머리로? → 틀림 (많아야 10%)'},
     {'t': S('ending', '둘째'), 'text': '머리만 내놓은 실험에서 나온 숫자'},
     {'t': S('ending', '셋째'), 'text': '그래도 모자는 OK, 아기에겐 필수'}]},
 {'t': S('ending', '같은 모자인데'), 'type': 'twohats'},
 {'t': S('ending', '그리고 이 통념'), 'type': 'next', 'items': [
     {'t': S('ending', '"물은'), 'text': '물은 하루 여덟 잔?'},
     {'t': S('ending', '"설탕'), 'text': '설탕 먹으면 흥분?'}]},
 {'t': S('ending', '퀴즈 두 개'), 'type': 'comment'},
 {'t': S('ending', '알고 보면'), 'type': 'end'},
]
json.dump({'end': round(END, 3), 'cards': cards, 'think': think, 'caps': caps, 'scenes': scenes},
          open(P + 'build/timeline.json', 'w'), ensure_ascii=False, indent=1)
print('scenes', len(scenes))
