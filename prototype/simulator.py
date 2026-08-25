import numpy as np

# [O, C, E, A, N]
# [Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism]
# [개방성, 성실정, 외향성, 우호성/친화성, 신경증/정서적 불안정성]
base = np.full(5, 0.5)

class State:
    def __init__(self):
        self.persona = base.copy()
        self.vitality = 100
        self.status = "ALIVE"
        self.age = 0

class Universe:
    def __init__(self, seed):
        self.seed = seed
        self.rng = np.random.default_rng(seed) # seed 기반 난수 생성기
        self.p_born = self.rng.uniform(0.7, 1.0)
        self.bad_ratio = self.rng.random()
        self.difficulty = self.rng.random()

    def try_birth(self):
        r = self.rng.random()
        if r < self.p_born:
            return State()
        else:
            return None

import itertools

# 무한루프
# for seed in itertools.count():
#     u = Universe(seed)
#     result = u.try_birth()
#     if result is not None:
#         print("seed: ", seed, "| P_born: ", u.p_born, " | result: ", result)
#     else:
#         print("seed: ", seed, "| P_born: ", u.p_born, " | result: None")

# 정해진 횟수만
for seed in range(20):
    u = Universe(seed)
    result = u.try_birth()
    if result is not None:
        print("seed: ", seed, "| P_born: ", u.p_born, " | result: ", result)
    else:
        print("seed: ", seed, "| P_born: ", u.p_born, " | result: None")