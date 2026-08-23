# Multiverse Agent Evolution & State Divergence Simulator

다중 우주 환경 변수에 따른 개체 성장 및 상태 분기 시뮬레이터

본 프로젝트는 다중 우주(Multiverse) 가설을 기반으로, 동일한 초기 상태(Genotype/Base State)를 가진 개체(Agent)가 독립된 우주 환경의 무작위 변수에 노출되었을 때 나타나는 성장 궤적, 성격 형성, 그리고 최종 상태의 분기 현상을 모사하고 통계적으로 분석하기 위한 시뮬레이션 엔진입니다.

## 목적 / 용도
개인 사고실험이자 동시성·알고리즘 설계 학습 프로젝트로 진행합니다. 6번의 무한 스트리밍 구조와 7번의 병렬/순차 하이브리드 실행 설계 자체가 학습 목적에 부합하고, 완성도가 올라가면 분기 트리·클러스터링 시각화를 중심으로 포트폴리오용 데모로 전환합니다. 통계적 엄밀성보다 구조 설계와 시각화 완성도를 우선순위로 둡니다.

## 1. Project Overview (프로젝트 개요)
- **핵심 질문**: 무한에 가까운 다중 우주가 존재할 때, 동일한 근원을 가진 '나'라는 개체는 환경 변수와 미시적 확률에 따라 어떻게 다르게 성장하고 변이하는가?
- **목적**:
  - 초기 조건과 외부 파라다임 변화에 따른 에이전트의 동적 발달 궤적(Growth Trajectory) 추적
  - 독립된 N개의 가상 우주(Thread/Context) 내 실행 결과 분석
  - 개체 생존 여부, 성격 변화, 최종 상태 분기율에 대한 정량적 통계 도출

## 2. Theoretical Framework (이론적 배경)
- **다세계 해석 (Many-Worlds Interpretation)**: 관측 또는 확률적 사건이 일어날 때마다 우주의 상태가 새로운 분기(Branch)로 갈라지는 메커니즘 채택
- **동적 에이전트 성장 모델 (Dynamic Agent Evolution)**: 초기 상태값을 공유하는 에이전트가 우주별 변수에 따라 매 시간 단위(Tick)마다 보상과 피드백을 받아 상태를 업데이트하는 구조
- **환경 상수 Variation (Environmental Variance)**: 각 우주의 물리/사회적 상수를 결정론적·확률론적 파라미터로 주입하여 성장 조건 제어

## 3. Architecture & Key Concepts (시스템 구조)
```
[Base Agent Template]
        │ (Branching)
        ├──► [Universe 01] ──► Agent 01 (Divergence / Null)
        ├──► [Universe 02] ──► Agent 02 (Divergence / Null)
        │        ...
        └──► [Universe N ] ──► Agent N (Divergence / Null)
```
- **Universe Context**: 물리 법칙, 생존 난이도, 부모 유전자 결합 확률, 사회적 이벤트 빈도 등을 보유한 독립적 시스템
- **Agent State Engine**: 유전적 기본값(Base DNA), 성격 지표(Persona Matrices), 지능, 경험치, 생존 여부(IsAlive)를 관리하는 개체 객체
- **Branching Event Manager**: 특정 시점(예: 탄생, 환경 변혁, 중대 선택)에 우주 상태를 복제하고 독립적인 무작위 시드값(Seed)을 부여하는 엔진

## 4. Experimental Design (구체적 실험 설계)
### Phase 1: Initialization & Branching
- 동일한 초기 상태 파라미터 `Agent_Base` 정의
- N개의 독립된 우주 인스턴스를 배열 및 스레드 단위로 동시 초기화
- 각 우주마다 별도의 난수 시드(PRNG Seed) 지정

### Phase 2: Environmental Perturbation & Growth Process
- **생성 단계 (Genesis)**: 특정 우주에서는 부모 만남 실패 또는 유전 조합 실패 조건으로 인한 '개체 존재 불능(Null/Not Born)' 처리
- **성장 단계 (Growth Loop)**: 매 시간 단위(Tick)마다 지정된 이벤트 매트릭스 실행 — 사회적 자극, 물리적 환경 변화, 무작위 사고 발생 → 에이전트의 내부 성격 파라미터(예: 외향성, 안정성, 위험 선호도) 재계산

### Phase 3: Trajectory & State Divergence Tracking
- T_end 시점까지 생존한 에이전트들의 최종 스탯 및 성장 이력 수집
- 코사인 유사도(Cosine Similarity) 및 거리 계산 알고리즘을 통한 원본 `Agent_Base`와의 격차 산출

## 5. Metrics & Analytics (분석 지표)
- **Existential Rate (R_exist)**: 전체 N개 우주 중 에이전트가 최종까지 존재 및 생존한 비율
- **Identity Similarity Index (S_identity)**: 기준 우주의 에이전트와 비교했을 때 최종 상태(성격, 능력치)의 유효 일치율
- **Divergence Spectrum**: 에이전트 성장 궤적이 분기된 형태의 클러스터링 결과

## 6. Mathematical & System Logic for 'Infinity' (무한의 로직 및 알고리즘 구현)
실제 시스템 자원의 한계를 극복하고 이론상 '무한(Infinity)'에 가까운 다중 우주를 시스템적으로 모사하기 위해 다음과 같은 알고리즘적 구조를 채택합니다.

### 6.1. Infinite Representation Logic (무한 공간 표현)
**Lazy Evaluation & Procedural Generation (절차적 우주 생성)**
- 모든 우주를 동시에 메모리에 로드하지 않고, $2^{64}$ 이상 공간을 가지는 64-bit PRNG Seed(예: PCG64 / Xoshiro256++)를 매핑
- 우주 U_k의 물리 법칙, 환경 변수, 사건 발생 분포는 모두 `Seed(k)`로부터 필요 시점에 동적으로 생성(Determined-on-demand)되므로 O(1)의 메모리 공간으로 무한에 가까운 공간을 표현

**Monte Carlo Convergence Engine (통계적 수렴 제어)**
- 고정된 N번의 반복 대신, 탐색된 우주들에서 '나와 100% 동일한 개체가 발견될 확률' 및 '성격 분기 스펙트럼의 신뢰구간'을 실시간 추적
- 아래 표준오차 SE 조건이 충족될 때까지 백그라운드 루프가 무한히 우주를 탐색·수집:

```
SE = sqrt( p(1-p) / n ) < ε
```
(p: 관측된 비율, n: 탐색한 우주 수, ε: 목표 오차 한계)

## 7. Execution Architecture: Sequential vs Parallel (실행 및 동시성 구조)
시스템 자원 효율을 최대화하고 무한 확장성을 보장하기 위해 Hybrid Stream & Pool Architecture를 적용합니다.

```
[Seed Generator (Infinite Stream)]
        │
        ▼
[Worker Thread / Process Pool] ──► (Parallel Execution: Universe K ~ K+N)
        │
   [Event & Tick Loop]
        │
   ┌────┴────┐
   ▼         ▼
[Null/Dead Agent]   [Completed Cycle]
(Early Pruning)            │
(Memory Release)           ▼
   │                [Metrics Collector]
   └──────────┬─────────────┘
              ▼
   [Queue Next Seed (Continuous Loop)]
```

### 7.1. Execution Pipeline Options
**Parallel Execution Phase (동시 병렬 실행 - 인프라 임계치 제한)**
- 적용 시점: 특정 기점 T_0에서 양자 분기(Branching)가 일어나는 직후 N개 우주
- 구현: Thread Pool / Process Pool을 통한 CPU 코어 단위 Parallelism
- N개의 우주가 독립된 Context로 병렬 진화하며, 우주 간 공유 자원 잠금(Locking)을 최소화하기 위해 메시지 파싱(Lock-free Queue) 방식 적용

**Sequential Queue Phase (순차 스트리밍 실행 - 무한 탐색 처리)**
- 적용 시점: 동시 병렬 인프라 스레드 수를 초과하는 대규모/무한 우주 탐색 시
- 구현: 하나의 Worker가 Seed → Simulation Loop → State Dump → Resource Reset 단계를 순차적/배치(Batch)로 실행. 메모리 복잡도는 단일 우주 실행 수준인 O(1)로 고정

**Early Pruning & Garbage Collection (조기 가지치기)**
- 생성 단계(Genesis) 또는 성장 과정(Growth Loop)에서 부모의 불일치, 유전 조합 실패, 치명적 사고로 인해 개체가 생존 불가능(Null/Dead)해진 우주는 즉시 시뮬레이션을 중단하고 메모리를 반납

## 8. Data Model & State Machine (상태 머신 및 데이터 구조)
### 8.1. Agent State Matrix
```
A_state(t) = (DNA_base, P(t), Status)

P(t) = [P_extroversion, P_neuroticism, P_risk-tolerance, ...]^T   (동적 변형 성격 매트릭스)

Status ∈ { NOT-BORN, ALIVE, TERMINATED }
```

### 8.2. State Transition Function
```
A_state(t + Δt) = f( A_state(t), E_universe(t, Seed_k) )
```
E_universe: 해당 우주의 환경 변수 및 무작위 자극 이벤트 벡터

## 9. 기술 스택 (Tech Stack)
1단계 프로토타입은 **Python + NumPy/Numba(연산) + Plotly(분기 트리·클러스터링 시각화)**로 빠르게 구조를 검증합니다. 구조가 자리잡고 N을 키울 필요가 생기면, O(1) 메모리 무한 스트리밍 구조의 이점을 제대로 살리기 위해 **C++ (또는 Rust) + 스레드 풀**로 코어 시뮬레이션 루프만 이식합니다 — dvd의 C++ 시스템 프로그래밍 경험과도 맞는 방향입니다. 시각화·분석 레이어는 Python에 남겨 개발 속도를 유지합니다.

## 10. 실행 규모 견적
1단계 프로토타입 목표는 **N=1,000, ε=0.05**로 잡고 노트북에서 몇 분 내 완료되는지부터 확인합니다. 우주 1개당 1000 tick, 상태 갱신 O(1) 연산 기준이면 단일 스레드로도 이 규모는 수 초~수십 초 내 처리가 가능할 것으로 예상되며, 이 실측 결과로 이후 N을 늘릴지, 아니면 이 프로젝트 성격상 N=1,000 수준의 소규모로도 충분한지(무한 스트리밍 구조가 굳이 필요 없을 수도 있음) 판단합니다.
