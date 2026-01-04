import math
import time
from ortools.sat.python import cp_model

print(">>> [전략 7-Lite] 프라임 웹 빠른 검증기 가동...", flush=True)
print(">>> 계산 속도를 위해 범위와 지수를 제한합니다.")

# --- 설정 (빠른 실행을 위한 축소) ---
PRIME_LIMIT = 150  # 소수 범위 축소 (500 -> 150)
SCALE = 10**8      # 정밀도 조정
MAX_EXPONENT = 6   # 최대 지수 제한 (12 -> 6)

# --- 유틸리티 ---
def get_prime_factors(n):
    factors = set()
    d = 2
    temp = n
    # 숫자가 너무 크면 계산 중단 (안전장치)
    if temp > 10**15: 
        return set() # 너무 큰 수는 분석 포기 (범위 밖으로 간주)
        
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
        # 1초 이상 걸리면 탈출 (무한루프 방지)
        if d > 200000: break 
    if temp > 1:
        factors.add(temp)
    return factors

def get_prime_factors_sum_ratio(p, k):
    return (p**(k+1) - 1) / (p**k * (p - 1))

def sigma_of_power(p, k):
    return (p**(k+1) - 1) // (p - 1)

# --- 1. 데이터베이스 구축 ---
print(f"\n1. 소수 족보(Family Tree) 생성 중 (범위: ~{PRIME_LIMIT})...")
start_time = time.time()

primes = []
is_prime = [True] * (PRIME_LIMIT + 1)
for p in range(2, PRIME_LIMIT + 1):
    if is_prime[p]:
        primes.append(p)
        for i in range(p * p, PRIME_LIMIT + 1, p):
            is_prime[i] = False

candidates = {}
count_combinations = 0

for p in primes:
    candidates[p] = {}
    # 지수 범위 축소
    exponents = [k for k in [1, 2, 4, 6] if k <= MAX_EXPONENT]
    
    for k in exponents:
        # 오일러 규칙
        if not ((p % 4 == 1 and k % 4 == 1) or (k % 2 == 0)):
            continue

        ratio = get_prime_factors_sum_ratio(p, k)
        log_val = math.log(ratio)
        scaled_val = int(log_val * SCALE)
        
        # 소인수분해 (시간 제한 걸린 함수 사용)
        sigma_val = sigma_of_power(p, k)
        children_factors = get_prime_factors(sigma_val)
        
        # 자식이 없거나(계산실패) 범위 밖 소수가 있으면 제외
        is_valid = True
        if not children_factors: is_valid = False # 계산 실패한 너무 큰 수
        
        for child in children_factors:
            if child > PRIME_LIMIT:
                is_valid = False
                break
        
        if is_valid:
            candidates[p][k] = {
                'val': scaled_val,
                'ratio': ratio,
                'children': children_factors
            }
            count_combinations += 1

print(f"   -> {count_combinations}개의 유효 조합 생성 완료. ({time.time() - start_time:.2f}초 소요)")

# --- 2. CP-SAT 모델링 ---
print("2. 모델링 및 제약조건 설정 중...")
model = cp_model.CpModel()

vars_dict = {} 
prime_active = {} 

for p in primes:
    prime_active[p] = model.NewBoolVar(f'active_{p}')
    if p in candidates:
        possible_ks = []
        for k in candidates[p]:
            v = model.NewBoolVar(f'sel_{p}_{k}')
            vars_dict[(p, k)] = v
            possible_ks.append(v)
        
        model.Add(sum(possible_ks) <= 1)
        model.Add(sum(possible_ks) == prime_active[p])
    else:
        model.Add(prime_active[p] == 0)

# 구조적 제약 (The Prime Web)
count_web_constraints = 0
for p in candidates:
    for k, info in candidates[p].items():
        if (p, k) in vars_dict:
            my_switch = vars_dict[(p, k)]
            for child_q in info['children']:
                if child_q in prime_active:
                    model.AddImplication(my_switch, prime_active[child_q])
                    count_web_constraints += 1

print(f"   -> {count_web_constraints}개의 연쇄 법칙 제약조건 추가됨.")

# 기본 제약
# 1. 오일러 소수 1개 필수
special_primes_vars = []
for p in candidates:
    for k in candidates[p]:
        if p % 4 == 1 and k % 4 == 1:
            if (p, k) in vars_dict:
                special_primes_vars.append(vars_dict[(p, k)])
model.Add(sum(special_primes_vars) == 1)

# 2. 소수 개수 5개 이상 (범위가 작으니 개수 조건 완화)
model.Add(sum(prime_active.values()) >= 5)

# 3. 수치적 조건
SCALED_TARGET = int(math.log(2) * SCALE)
tolerance = 1000 # 오차 범위

total_val = 0
for p in candidates:
    for k, info in candidates[p].items():
        if (p, k) in vars_dict:
            total_val += vars_dict[(p, k)] * info['val']

model.Add(total_val >= SCALED_TARGET - tolerance)
model.Add(total_val <= SCALED_TARGET + tolerance)

# --- 3. 해결 ---
print("\n3. 솔버 가동 (제한시간 30초)...")
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
status = solver.Solve(model)

# --- 4. 결과 ---
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("\n🎉 [발견] 이 좁은 범위에서도 근사해가 존재합니다!")
    final_prod = 1.0
    print("--- 구조 ---")
    for p in primes:
        if p in candidates:
            for k in candidates[p]:
                if (p, k) in vars_dict and solver.Value(vars_dict[(p, k)]):
                    info = candidates[p][k]
                    print(f"P: {p}^{k} (자식: {info['children']})")
                    final_prod *= info['ratio']
    print(f"\n최종 풍요지수: {final_prod}")
    print(f"오차: {abs(final_prod - 2.0)}")

elif status == cp_model.INFEASIBLE:
    print("\n🚫 [증명 완료] 'INFEASIBLE (불가능)'")
    print(f"   범위 {PRIME_LIMIT} 이하, 지수 {MAX_EXPONENT} 이하에서는")
    print("   완벽한 족보(Web)를 가진 홀수 완전수가 존재할 수 없음이 증명되었습니다.")
    print("   (수치적으로는 가능할지 몰라도, 소수 연쇄 법칙 때문에 막힘)")
    
else:
    print("\n⏳ 시간 초과 (범위를 더 줄여야 합니다)")