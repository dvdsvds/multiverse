# 코딩 Day 2 기록

주제: tick 루프 설계 + 이벤트 뽑기(`_pick_event`) + 적응 공식 적용(`_apply_event`) 구현.
방식: 내가 직접 짜고, 막히거나 버그 나면 힌트로 잡는 식. 코드는 `src/simulator.py`.

---

## 0. 방향 정하기

### Day 2 목표
```
1. tick 루프 뼈대 잡기          ← 오늘
2. 이벤트 사전(events.json) 설계 ← 시도했다가 프로토타입 단계라 보류
3. 이벤트 뽑기 (_pick_event)     ← 오늘, 단순화 버전으로
4. 적응 공식 적용 (_apply_event) ← 오늘
5. vitality / status 판정        ← Day 3로 이월
```
- Day 1에서 만든 `try_birth()`로 태어난 State가 "한 해씩 살아가는" 과정이 tick.
- tick은 **Universe가 소유**(시간이 흐르는 주체는 Universe, rng도 Universe 소유이므로 같은 논리).

---

## 1. tick 루프 뼈대

### 메서드를 나눌지 합칠지
- 처음에 "나눈다"의 의미를 혼동함 — **값 공유 방지 때문에 나눈다**고 착각.
  - 실제로는 메서드를 나누든 합치든가 값 공유 여부(`.copy()` 문제)와는 무관함 — Day 1에서 겪은 참조 공유 문제는 대입 방식(`base` vs `base.copy()`) 때문이지, 함수를 쪼갰냐 안 쪼갰냐와는 상관없음.
- 진짜 이유로 재확인: 각 기능(이벤트 뽑기 / 적용 / vitality / status)이 **독립된 책임**이라 나눠야 나중에 개별 테스트·디버깅이 쉬움.
- 최종 구조:
```python
def tick(self, state):
    event = self._pick_event()
    self._apply_event(state, event)
    self._update_vitality(state, event)   # Day 3
    self._update_status(state)            # Day 3
```
- `_pick_event()`는 `state`를 받지 않음 — 이벤트를 고르는 데 필요한 건 `bad_ratio` 등 Universe가 가진 값뿐, 개체 상태와 무관.

---

## 2. 이벤트 사전(events.json) — 설계했다가 보류

### 처음 시도한 구조
- 이벤트 하나 = `{name, category(good/bad), weight, persona_effects(축마다 다른 개수), vitality_damage(범위)}`.
- 형식은 **JSON**으로 결정 — 이벤트마다 영향받는 축 개수가 다름(가변 길이) → 중첩 구조 필요 → CSV(고정 칼럼)보다 JSON이 적합.
- 저장 위치는 `prototype/events.json` (파일 하나만 있는 지금 단계에 폴더까지 만드는 건 과함 — simple first).
- 로딩은 **1회만, 명시적으로 전달**(`self.rng`처럼 Universe가 소유):
```python
def load_events(path="events.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
```
- 전역변수로 로드(모듈 최상단에서 바로 읽기)는 기각 — "명시적 전달·격리" 원칙과 안 맞음.

### 가중치(weight) 기준을 통계로 잡으려 시도
- "내가 직접 weight를 정하면 주관적"이라는 문제의식으로 **한국 공식 통계에서 이벤트 이름을 가져오자**는 방향으로 조사.
- 확인된 것: 통계청 인구동향조사(혼인·이혼·출생·사망), 경찰청 범죄통계, 고용노동부 산업재해, 소방청 화재통계, 기상청 지진통계, 국토교통부 주거실태조사(자가보유율 → "내 집 마련" 근거), 동행복권(복권 당첨자 수 공식 집계).
- "승진", "연애" 등은 국가가 공식 집계하는 통계가 없음(기업 내부 인사·개인 관계라서) → 이후 통계 검증은 중단하고 브레인스토밍으로 전환.
- **최종 결정: 이벤트 사전 자체를 프로토타입 단계에서는 보류.** 지금은 전체 파이프라인(tick 루프)이 한 번 끝까지 도는 걸 확인하는 게 우선순위 → 세부 이벤트(이름, 통계 근거)는 2차로 미룸.

---

## 3. 단순화 결정: bad_ratio / good_ratio만 사용

### 방향
- 이벤트 이름·세부 사전 없이, **"bad 이벤트가 일어났다 / good 이벤트가 일어났다"**라는 사실만으로 persona를 흔드는 최소 버전으로 감.
- good/bad 판정은 Day 1 `try_birth()`와 같은 패턴:
```python
r = self.rng.random()
if r < self.bad_ratio:
    # bad
else:
    # good
```

### 무엇을 바꿀지 (축 선택)
- 후보 A) 5축 중 1개만 랜덤 선택해서 흔들기
- 후보 B) good/bad 상관없이 5축 전부 흔들기
- 후보 C) 랜덤 개수·랜덤 조합으로 흔들기
- **선택: A** — 프로토타입 단계라 가장 단순, bad_ratio가 결과에 명확히 반영되고, 나중에 이벤트 사전(여러 축 동시 변화)으로 확장할 때도 자연스럽게 이어짐(1개 축 → N개 축).

### 축 이름 상수화
```python
# [O, C, E, A, N]
O, C, E, A, N = range(5)
```
- `base[axis]` 인덱스 혼동(3번이 A였는지 N이었는지) 방지용.

### 변화량(delta) 범위도 우주마다 다르게
- "변화량을 아직 선언 안 했다"는 걸 자각 → 고정값 vs 랜덤범위 중 **랜덤범위** 선택(프로토타입이어도 단순화).
- delta_min/delta_max도 `bad_ratio`처럼 **시드에서 파생되는 Universe별 파라미터**로 결정(우주마다 성향이 달라야 하니까 공통 상수로 고정하지 않음).
- 두 값을 각각 독립적으로 뽑으면 `min >= max`가 될 수 있는 문제 → 뽑고 나서 정렬하는 방식 채택:
```python
a = self.rng.random()
b = self.rng.random()
self.delta_min, self.delta_max = min(a, b), max(a, b)
```
- "이러면 범위가 극단적으로(너무 좁거나 너무 넓게) 갈리는 우주가 많지 않을까?" 하는 의문 → `|a-b|`의 기댓값은 1/3, 극단값(0 또는 1 근처)은 조합의 수가 적어서 드물게만 나옴 → 대부분 우주는 중간 범위로 몰림. 통제 로직 추가 없이 그대로 두기로 함(억지 상관관계·통제를 넣지 않는다는 기존 원칙 재확인).

---

## 4. `_pick_event` 구현

### 최종 코드
```python
def _pick_event(self):
    axis = self.rng.integers(0, 5)
    delta = self.rng.uniform(self.delta_min, self.delta_max)
    r = self.rng.random()
    if r < self.bad_ratio:
        return (axis, -delta)
    else:
        return (axis, delta)
```

### 잡은 실수
- 처음엔 `-abs(delta)`로 음수를 만듦. `delta_min`, `delta_max`가 항상 0~1 사이 양수라 `delta`도 항상 양수 → `abs()`는 불필요한 방어 코드. `-delta`로 충분 → 제거.

---

## 5. `_apply_event` 구현

### 적응 공식 (기획 문서 12.3)
```
distance = (Δ > 0) ? (1 - n) : n
n        = n + Δ × distance
```

### 잡은 실수 (순서대로)
1. **`state`를 매개변수로 안 받음** — `def _apply_event(self):`로 정의해놓고 `state.persona`를 쓰려 함 → `state`, `event`를 매개변수로 추가.
2. **`State()`로 새 객체를 만들어버림** — `n = State().persona[axis]`. 지금 tick 중인 개체가 아니라 **완전히 새로운 State**를 만들어서 엉뚱한 값을 읽는 것. `State`(클래스)와 `state`(매개변수 이름)를 헷갈린 것으로 보였으나, 실제 원인은 이름 혼동이 아니라 `State()`를 호출해버린 것 — Python은 대소문자를 구분하므로 매개변수명 `state`는 클래스명과 무관하게 정상 동작함.
3. **계산 결과를 저장 안 함** — `n = n + delta * distance`까지만 하고 끝 → 지역 변수만 바뀌고 실제 개체는 안 바뀜. `state.persona[axis] = ...`로 재대입해야 함.

### 최종 코드
```python
def _apply_event(self, state, event):
    axis, delta = event
    n = state.persona[axis]
    distance = (1 - n) if (delta > 0) else n
    state.persona[axis] = n + delta * distance
```
- `_apply_event`는 `state.persona`를 직접 바꾸는 side-effect 함수라 **return 불필요**(호출부에서도 리턴값을 안 받음).

---

## 6. 테스트 & 잡은 버그

### 버그 1: seed 하드코딩
```python
for seed in range(20):
    events = load_events("events.json")
    u = Universe(seed = 0, events=events)   # ← seed 변수 안 쓰고 0 고정
```
- 결과: `p_born`이 20번 다 `0.8910885061964363`로 동일, `result`도 전부 `None`.
- **원인**: `seed=seed`가 아니라 `seed=0`으로 박아둠 → 매번 시드 0짜리 우주만 생성.
- **수정**: `Universe(seed=seed, events=events)`.
- 버그 재현 결과는 `seed0_bug_result.txt`로 별도 저장(README 기록용).

### 수정 후 결과 (seed 0~19)
```
seed:  0 | P_born:  0.8910885061964363  | result: None
seed:  1 | P_born:  0.853546487410077   | result:  <simulator.State object ...>
seed:  2 | P_born:  0.7784836402747949  | result:  <simulator.State object ...>
...
seed: 11 | P_born:  0.7385710608307599  | result: None
...
seed: 19 | P_born:  0.8261136387187782  | result:  <simulator.State object ...>
```
- `p_born`이 시드마다 달라짐, `result`도 시드 0·11에서만 `None` — Day 1에서 확인한 재현성·개체 예측 불가 특성이 그대로 유지됨을 재확인.

### `_pick_event` + `_apply_event` 수동 호출 검증
```
=== 태어난 개체 초기 persona (seed=1) ===
[0.5 0.5 0.5 0.5 0.5]

tick 1: axis=1(C), delta=-0.5724  |  0.5000 -> 0.2138
tick 2: axis=4(N), delta=-0.3294  |  0.5000 -> 0.3353
tick 3: axis=4(N), delta=-0.5218  |  0.3353 -> 0.1603
tick 4: axis=2(E), delta=-0.5049  |  0.5000 -> 0.2475
tick 5: axis=4(N), delta=-0.5685  |  0.1603 -> 0.0692

=== 최종 persona ===
[0.5        0.21379159 0.24754431 0.5        0.0691807 ]
```
- 값이 0~1 경계를 넘지 않고 적응 공식대로 움직이는 것 확인(경계에 가까울수록 변화폭이 줄어드는 것도 tick 3→5의 N축 변화량에서 확인됨: 0.5218 → 0.5685지만 실제 반영폭은 0.1750 → 0.0911로 감소).

### 버그 2 (발견만, 수정은 보류): 모듈 최상위 for문
- `test_apply.py`에서 `from simulator import Universe, State, load_events`만 했는데 seed 0~19 결과가 같이 출력됨.
- **원인**: `simulator.py` 맨 아래 `for seed in range(20): ...`가 들여쓰기 없이 최상위 레벨에 있음 → `import` 시점에 Python이 파일의 최상위 코드를 전부 실행해버림.
- **해결책(적용은 보류, 다음에 처리)**:
```python
if __name__ == "__main__":
    for seed in range(20):
        ...
```

---

## 오늘 완성분
```
✅ tick 루프 뼈대 설계 (Universe가 소유, 4단계로 메서드 분리)
✅ 이벤트 사전(JSON) 설계 시도 → 프로토타입 단계라 보류 결정
✅ bad_ratio/good_ratio 기반 단순화 이벤트 모델 확정
✅ delta_min/delta_max 시드 파생 파라미터 추가
✅ _pick_event 구현 및 검증
✅ _apply_event 구현 및 검증 (버그 3개 수정)
✅ seed 하드코딩 버그 발견 및 수정
= tick 4단계 중 앞 2단계(이벤트 뽑기 → 적용) 완성
```

## 배운 것 / 실수 요약
1. "메서드를 나눈다"는 값 공유(참조/copy) 문제와 무관 — 나누는 진짜 이유는 책임 분리·테스트 용이성
2. JSON vs CSV: 데이터가 가변 길이·중첩 구조면 JSON, 고정 칼럼이면 CSV
3. 이벤트 weight를 객관화하려고 공식 통계까지 찾아봤지만, 지금 단계엔 과함 — 프로토타입은 파이프라인 완성이 우선, 세부는 2차로
4. 확률/범위 파라미터를 두 번 독립으로 뽑으면 `min > max` 같은 깨진 관계가 나올 수 있음 → 뽑고 정렬(`min()`, `max()`)로 해결
5. 균등분포 두 값의 거리 기댓값은 1/3 — 극단값은 드물게만 나오므로 별도 통제 로직 불필요
6. `State`(클래스)와 `state`(매개변수)는 대소문자로 완전히 다른 이름 — Python이 헷갈릴 일 없음. 실제 버그는 이름 혼동이 아니라 `State()`를 호출해 새 객체를 만든 것
7. side-effect로 객체를 직접 바꾸는 함수는 return 불필요
8. 반복문에 넣는 변수는 실제로 그 변수를 쓰고 있는지 항상 확인 (`seed=0` 하드코딩 버그)
9. 모듈 최상위 코드는 import 시점에 그대로 실행됨 — 테스트/재사용할 파일은 `if __name__ == "__main__":`으로 감싸야 함(적용은 Day 3로 이월)

## 다음 (Day 3 후보)
- `_update_vitality(state, event)` — 이벤트로 인한 vitality 감소 처리
- `_update_status(state)` — vitality 기준 생사 판정
- `tick()` 메서드 조립 (4단계 전부 연결)
- `if __name__ == "__main__":` 적용