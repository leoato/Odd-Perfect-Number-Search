import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import random
import warnings

# 경고 메시지 무시 (계산 중 발생하는 오버플로우 경고 등)
warnings.filterwarnings("ignore")

# --- 설정 ---
FILENAME = "chaos_masterpiece.png"
DPI = 150 
G = 1.0

# --- 1. 황금 질량 비율 (유지) ---
m1 = 1.20
m2 = 1.44
m3 = 1.25
print(f">>> [안전 모드] 충돌 방지 시스템 가동. 질량: {m1}, {m2}, {m3}")

def equations(state, t):
    r1, r2, r3 = state[0:2], state[2:4], state[4:6]
    v1, v2, v3 = state[6:8], state[8:10], state[10:12]

    # 거리 제곱 계산
    r12_sq = np.sum((r2 - r1)**2)
    r13_sq = np.sum((r3 - r1)**2)
    r23_sq = np.sum((r3 - r2)**2)

    # [수정] Softening Parameter (쿠션)
    # 거리가 0이 되어도 분모가 0이 되지 않게 막아주는 안전장치
    # 값을 0.01로 키워서 계산 폭발을 막음
    soft = 0.1 
    
    # 가속도 계산 (Softened Gravity)
    # F = G*m*M / (r^2 + soft^2)^(1.5)
    inv_r12 = (r12_sq + soft**2)**(-1.5)
    inv_r13 = (r13_sq + soft**2)**(-1.5)
    inv_r23 = (r23_sq + soft**2)**(-1.5)

    dv1dt = G * m2 * (r2 - r1) * inv_r12 + G * m3 * (r3 - r1) * inv_r13
    dv2dt = G * m1 * (r1 - r2) * inv_r12 + G * m3 * (r3 - r2) * inv_r23
    dv3dt = G * m1 * (r1 - r3) * inv_r13 + G * m2 * (r2 - r3) * inv_r23

    return np.concatenate((v1, v2, v3, dv1dt, dv2dt, dv3dt))

def get_chaos_init():
    x1, y1 = 0.97000436, -0.24308753
    vx3, vy3 = -0.93240737, -0.86473146
    r1 = np.array([x1, y1])
    r2 = -r1
    r3 = np.array([0.0, 0.0])
    v3 = np.array([vx3, vy3])
    v1 = -0.5 * v3
    v2 = -0.5 * v3
    
    base = np.concatenate((r1, r2, r3, v1, v2, v3))
    # 노이즈 범위 설정
    noise = np.random.normal(0, 0.2, size=base.shape)
    return base + noise

def evaluate_orbit(init_state):
    t = np.linspace(0, 30, 2000)
    try:
        # mxstep을 늘려서 계산이 오래 걸려도 포기하지 않게 함
        sol = odeint(equations, init_state, t, mxstep=5000)
    except:
        return 0, None

    # 결과 분석
    if np.isnan(sol).any() or np.isinf(sol).any(): # 값이 깨졌으면 탈락
        return 0, None

    r1 = sol[:, 0:2]
    r2 = sol[:, 2:4]
    r3 = sol[:, 4:6]
    
    # 너무 멀리 날아갔는지 확인
    max_dist = 0
    for r in [r1, r2, r3]:
        dist = np.max(np.linalg.norm(r, axis=1))
        if dist > max_dist: max_dist = dist
            
    if max_dist > 8.0: return 50, sol # 멀리 가도 일단 그림은 그림 (점수 낮음)
    
    return 100 + (10/max_dist), sol # 좁은 곳에서 놀면 고득점

# --- 메인 실행 ---
def main():
    print(">>> 안정적인 궤도를 찾을 때까지 계속 시도합니다...")
    
    valid_sol = None
    best_score = 0
    
    # 최대 100번 시도 (성공할 때까지)
    for i in range(1, 101):
        y0 = get_chaos_init()
        score, sol = evaluate_orbit(y0)
        
        if score > 0:
            print(f"   시도 {i}: 성공! (점수 {score:.1f})")
            if score > best_score:
                best_score = score
                valid_sol = sol
                
            # 점수가 높으면(안정적이면) 바로 채택
            if score > 102:
                print(">>> 아주 훌륭한 궤도를 찾았습니다!")
                break
        else:
            # 실패해도 조용히 넘어감
            print(f"   시도 {i}: 충돌/발산 (재시도 중...)", end='\r')

    if valid_sol is None:
        print("\n>>> 모든 시도 실패. (매우 운이 없네요, 다시 실행해주세요)")
        return

    print("\n>>> 사진 현상 중...")
    
    # 그리기
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    ax.set_xticks([])
    ax.set_yticks([])
    
    colors = ['#FF0055', '#00CCFF', '#FFE600'] 
    alphas = [0.7, 0.7, 0.9]
    
    for i in range(3):
        x = valid_sol[:, i*2]
        y = valid_sol[:, i*2+1]
        
        ax.plot(x, y, color=colors[i], linewidth=0.8, alpha=alphas[i])
        ax.scatter(x[0], y[0], color=colors[i], s=30, marker='o') # 시작
        ax.scatter(x[-1], y[-1], color=colors[i], s=80, marker='*') # 끝

    plt.title(f"Chaos Orbit (Safe Mode)", color='gray', fontsize=10)
    plt.tight_layout()
    plt.savefig(FILENAME, dpi=DPI, bbox_inches='tight')
    print(f">>> 저장 완료: {FILENAME}")
    plt.show()

if __name__ == "__main__":
    main()