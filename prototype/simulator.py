import numpy as np
import json

# [O, C, E, A, N]
# [Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism]
# [개방성, 성실정, 외향성, 우호성/친화성, 신경증/정서적 불안정성]
base = np.full(5, 0.5)
O, C, E, A, N = range(5)

def load_events(path="events.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class State:
    def __init__(self):
        self.persona = base.copy()
        self.vitality = 100
        self.status = "ALIVE"
        self.age = 0

class Universe:
    def __init__(self, seed, events):
        self.seed = seed
        self.rng = np.random.default_rng(seed) # seed 기반 난수 생성기
        self.event = events # TODO: 프로토타입 단계랑 아직 미사용. 추후에 _pick_event에서 참조
        self.p_born = self.rng.uniform(0.7, 1.0)
        self.bad_ratio = self.rng.random()
        self.difficulty = self.rng.random()
        a = self.rng.random()
        b = self.rng.random()
        self.delta_min, self.delta_max = min(a, b), max(a, b)

    def try_birth(self):
        r = self.rng.random()
        if r < self.p_born:
            return State()
        else:
            return None

    def _pick_event(self):
        axis = self.rng.integers(0, 5)
        delta = self.rng.uniform(self.delta_min, self.delta_max)
        r = self.rng.random()
        if r < self.bad_ratio:
            return (axis, -delta)
        else:
            return (axis, delta)

    def _apply_event(self, state, event):
        axis, delta = event
        n = state.persona[axis]

        distance = (1 - n) if (delta > 0) else n
        state.persona[axis] = n + delta * distance

if __name__ == "__main__":
    # 정해진 횟수만
    for seed in range(20):
        events = load_events("events.json")
        u = Universe(seed=seed, events=events)
        result = u.try_birth()
        if result is not None:
            print("seed: ", seed, "| P_born: ", u.p_born, " | result: ", result)
        else:
            print("seed: ", seed, "| P_born: ", u.p_born, " | result: None")