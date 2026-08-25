# 코딩 Day 1 기록

주제: 환경 세팅 + 데이터 구조(base / State / Universe) + 탄생 판정(try_birth) 구현.
방식: 내가 직접 짜고, 막히거나 버그 나면 힌트로 잡는 식. 코드는 `src/simulator.py`.

---

## 0. 방향 정하기

### 구현 순서 (우주 하나부터 → 여러 개)
```
1. 데이터 구조 (base, State, Universe)       ← Day 1
2. 우주 하나 돌리기 (탄생 → tick 루프 → 최종)  ← Day 1은 탄생까지
3. 재현성 테스트
4. 몬테카를로 (for N)
5. 분석 (거리, 클러스터링, PCA)
6. 시각화 (Plotly)
```
- 언어: **Python**(기획서 결정 — 결과 확인이 목적, 반복 속도 우선).
- 파일: 지금은 `simulator.py` 하나. 커지면 나중에 쪼갬(단순한 것부터 원칙).

---

## 1. 환경 세팅

### 겪은 문제와 해결
- `conda create -n multiverse python=3.13` 로 환경 생성 (3.14 최신이지만, 과학계산 패키지 호환성 위해 최신 -1/-2가 관례. 안정성 > 최신성).
- **Git Bash에서 `ModuleNotFoundError: numpy`** → conda가 Git Bash와 잘 안 물림. `(multiverse)`가 떠 있어도 실제 활성화가 안 돼 `python`이 엉뚱한 파이썬을 잡음.
  - **해결**: Anaconda Prompt(또는 PowerShell)에서 `conda activate multiverse` → 정상.
- `conda install numpy` → `python -c "import numpy; print(numpy.__version__)"` 로 확인.
- 주의: conda 환경에선 되도록 `conda install`로 통일(pip과 마구 섞으면 꼬임).

---

## 2. base 성격 벡터

```python
import numpy as np
# [O, C, E, A, N]
# [Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism]
# [개방성, 성실성, 외향성, 우호성/친화성, 신경증/정서적 불안정성]
base = np.full(5, 0.5)
```
- Big5 5차원, 모든 우주 공유 출발점. 값 0.5(출발선은 어디 두든 상관없음).
- 자료구조는 **NumPy 배열** 선택 — 이유: ① 벡터 연산 한 방에, ② 나중에 우주 여러 개를 2차원 배열로 벡터화 가능.
- 축 이름은 주석으로 남김(순서 헷갈림 방지).

---

## 3. State (우주 속 '나' 하나의 상태)

### 1차에 넣을 것만 (단순화)
- 나열했던 것: dna, 생존여부, 지능, 경험치, 나이, 생존력, (+빠뜨렸던) **성격 벡터**.
- **지능·경험치는 2차(직업·행동 추론)용** → 1차 divergence 분석엔 불필요 → 뺌.
- 1차 State = `persona`, `vitality`, `status`, `age`.

### class로 결정 (배열 묶음이 아니라)
- 지금은 **우주 1개 로직 검증** 단계 → 직관적이고 디버깅 쉬운 class가 맞음.
- 배열 묶음(벡터화)은 **몬테카를로(1000개) 갈 때** 쓸 무기. 지금은 순서가 이름(1개짜리 벡터화는 이득 없음).
- "나중에 배열로 바꾸기 쉽게" 정도만 염두. 미리 배열로 짜는 것 아님.

### 버그: base 공유 문제 → `.copy()`
```python
class State:
    def __init__(self):
        self.persona = base.copy()   # ← np.copy(base) 도 동일
        self.vitality = 100
        self.status = "ALIVE"
        self.age = 0
```
- 처음엔 `self.persona = base`로 씀 → **모든 State가 같은 base 배열을 공유**(NumPy 대입은 복사가 아니라 참조 공유. C++의 포인터 공유 같음).
- s1이 persona 바꾸면 s2도 바뀜 → **우주 격리 원칙 위반**(호텔 방부터 팠던 그 원칙).
- **해결: `base.copy()`** — 각 State가 독립 복사본. 이게 곧 코드 레벨의 **격리(isolation)**.
- 덤: dna를 State에 따로 안 넣어도 됨 — persona가 그 역할, 원본 base는 밖에 하나만 두고 divergence 기준으로 씀(안 변하니 복사 불필요).
- vitality 시작값 100: 절대값은 의미 없고 이벤트 피해량과의 상대관계가 중요 → 일단 100, 나중에 튜닝.

---

## 4. Universe (우주)

### class + 파라미터는 시드에서 파생
```python
class Universe:
    def __init__(self, seed):
        self.seed = seed
        self.rng = np.random.default_rng(seed)   # seed 기반 난수 생성기
        self.p_born = self.rng.uniform(0.7, 1.0)
        self.bad_ratio = self.rng.random()
        self.difficulty = self.rng.random()
```
- 파라미터 뜻:
  - **p_born**: 태어날 확률(시작 시 1회 판정).
  - **bad_ratio**: 나쁜 일 비율(매 tick 이벤트의 좋은/나쁜). 험난/평탄한 우주 결정.
  - **difficulty**: 생존 난이도(사고가 얼마나 치명적). 잘 죽는 정도.
  - 셋은 **서로 독립**(나쁜 일 많은데 안 죽는 우주도 허용).
- **seed 빼고 전부 난수 파생** — 고정값 박으면 모든 우주가 똑같아짐. 시드 파생이라야 우주마다 다르고 + 재현 가능.

### 범위 조정: `random()` 0~1 → 0.7~1.0
- p_born을 0~1 전체로 뽑으면 0.02 같은 것도 나와 대부분 NOT_BORN → 데이터 안 쌓임.
- 공식: **`random() × (너비) + (시작값)`**, 너비=최대-최소, 시작=최소.
  - 0.7~1.0 → `random()*0.3 + 0.7` (내가 처음 `*0.1+0.6`으로 계산 → 0.6~0.7 나와서 정정).
  - NumPy는 `rng.uniform(0.7, 1.0)`로 한 번에(원리는 곱하고 더하기 동일).

### rng를 어디에 두나 → `self.rng` (전역 아님)
- `try_birth`에서도 난수가 필요 → `__init__`의 지역 `rng`는 사라짐.
- **전역변수 ❌**: 모든 우주가 rng 공유 → 우주 A가 몇 개 뽑았냐에 B가 영향받아 재현·격리 깨짐.
- 파라미터로 넘기기도 가능하나, **`self.rng`로 저장**이 가장 깔끔(우주 자기 rng는 자기가 소유). persona를 State가 갖는 것과 같은 논리.

---

## 5. try_birth (탄생 판정)

### 어느 class의 메서드인가 → Universe
- 태어남을 결정하는 건 **우주(환경)**지, 아직 없는 개체(State)가 아님. p_born도 Universe 소유.

### 최종 코드
```python
    def try_birth(self):
        r = self.rng.random()
        if r < self.p_born:
            return State()      # 태어남
        else:
            return None         # 안 태어남(개체 없음)
```

### 잡은 버그들
- **return 누락**: 처음엔 `State()`만 씀 → 만든 객체가 아무도 안 받아 사라짐 → `return State()`.
- **NOT_BORN 표현**: `State().status="NOT_BORN"`은 이름 없는 객체라 즉시 사라짐 + return 없음.
  - 선택: (A) status="NOT_BORN"인 State vs (B) `None`.
  - **None 선택** — 안 태어난 개체에 persona/vitality가 있는 게 이상함. None이 "개체 없음"을 깔끔히 표현.
- (참고 팁) `!= None`보다 `is not None`이 파이썬 관례.

---

## 6. 테스트 & 결과

### 버그: 무한 루프
```python
for seed in itertools.count():   # 0,1,2... 무한
    ...
    if u.p_born > 1: break        # p_born은 uniform(0.7,1.0)이라 절대 >1 아님 → 안 멈춤
```
- 멈춤 조건이 **절대 성립 안 함** → 무한 루프.
- **해결: 정해진 횟수만** → `for seed in range(20)` (테스트엔 딱 정한 개수가 안전). itertools 불필요.

### 실행 결과 (seed 0~19)
```
seed:  0  | P_born:  0.8910885061964363  | result:  <__main__.State object at 0x00000257D84D81A0>    → State
seed:  1  | P_born:  0.853546487410077   | result: None                                              ← 안 태어남!
seed:  2  | P_born:  0.7784836402747949  | result:  <__main__.State object at 0x00000257D84D1090>
seed:  3  | P_born:  0.7256947501430873  | result:  <__main__.State object at 0x00000257D84D11D0>
seed:  4  | P_born:  0.9829168316717103  | result:  <__main__.State object at 0x00000257D840E650>
seed:  5  | P_born:  0.9415008771236141  | result:  <__main__.State object at 0x00000257D840E780>
seed:  6  | P_born:  0.8614493054415829  | result:  <__main__.State object at 0x00000257D84A9250>
seed:  7  | P_born:  0.8875286399814001  | result:  <__main__.State object at 0x00000257D84809E0>
seed:  8  | P_born:  0.7980916829816682  | result:  <__main__.State object at 0x00000257D8480AF0>
seed:  9  | P_born:  0.9610747611910253  | result:  <__main__.State object at 0x00000257D5E94B50>
seed:  10 | P_born:  0.9868005128886925  | result:  <__main__.State object at 0x00000257D845E450>
seed:  11 | P_born:  0.7385710608307599  | result:  <__main__.State object at 0x00000257D843E8A0>
seed:  12 | P_born:  0.7752473374325338  | result:  <__main__.State object at 0x00000257D843E990>
seed:  13 | P_born:  0.9594392761049759  | result:  <__main__.State object at 0x00000257D84865F0>
seed:  14 | P_born:  0.9492949956667335  | result:  <__main__.State object at 0x00000257D84866D0>
seed:  15 | P_born:  0.9078230103895457  | result:  <__main__.State object at 0x00000257D847E1A0>
seed:  16 | P_born:  0.8700750516638095  | result:  <__main__.State object at 0x00000257D8470DD0>
seed:  17 | P_born:  0.9535224378393705  | result:  <__main__.State object at 0x00000257D8470E90>
seed:  18 | P_born:  0.8197917307652718  | result:  <__main__.State object at 0x00000257D83F6410>
seed:  19 | P_born:  0.8261136387187782  | result:  <__main__.State object at 0x00000257D83F6360>
```
- **태어남/None 둘 다 정상 작동 확인.** try_birth 완성.
- seed 1: p_born 0.85로 높은데도 None → 확률 높아도 개별 결과는 모름. 학습의 **"개체는 예측 불가"**가 코드로 확인됨.
- (seed 42는 p_born≈0.93, 두 번 만들어도 값 동일 → **재현성** 확인 완료.)

---

## 오늘 완성분
```
✅ base 벡터 (Big5, 축 이름 주석)
✅ State (persona/vitality/status/age, .copy()로 격리)
✅ Universe (seed→파라미터 파생, 재현성 확인)
✅ try_birth (탄생 판정, State/None 둘 다 작동)
= 우주 하나의 "시작(탄생)"까지 완성
```

## 배운 것 / 실수 요약
1. NumPy 대입은 참조 공유 → 독립 원하면 `.copy()` (= 코드 레벨 격리)
2. rng는 전역 ❌, `self.rng`로 우주가 소유 (재현·격리)
3. 범위 조정 = `random()*너비 + 시작값` (또는 `uniform`)
4. 함수는 `return` 해야 값이 밖으로 나감
5. 무한 루프 주의 — 멈춤 조건이 실제로 성립하는지 확인. 테스트는 `range(N)`
6. None 비교는 `is not None`

## 다음 (Day 2 후보)
- 태어난 State로 **tick 루프** 시작: 이벤트 뽑기 → f(적응 공식) → status 판정
- 디렉토리 정리: `docs/`(기획서+record), `src/`(코드)