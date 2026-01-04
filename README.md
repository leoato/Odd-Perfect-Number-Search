# 🌌 Chaos & Perfect Numbers: AI-Assisted Mathematical Discovery

> **연구자:** 차동균 (Dongkyun Cha)

이 저장소는 AI(LLM) 및 구글 OR-Tools와 협력하여 수행한 두 가지 계산수학 연구 프로젝트의 결과물을 담고 있습니다.

## 🏆 Project 1: 홀수 완전수 탐색 (Odd Perfect Number Search)
**"2000년 난제에 도전하다: 수치적 스푸프(Numerical Spoof)의 발견"**

우리는 **구글 OR-Tools (CP-SAT Solver)**를 사용하여 홀수 완전수 문제를 '로그 배낭 문제(Logarithmic Knapsack Problem)'로 재해석했습니다. 그 결과, 기존 수학계에 보고된 적 없는 **오차 $10^{-10}$ 수준의 수치적 근사해**를 발견했습니다.

### 핵심 성과
- **발견된 수:** $N = 13^1 \times 5^{12} \times 7^6 \times 11^4 \dots$
- **풍요지수(Abundancy Index):** $1.9999999992...$ (목표값 2.0)
- **결론:** 수치적으로는 완벽에 가깝지만, **'프라임 웹(Prime Web)'** 검증기를 통해 작은 소수 범위 내에서는 구조적으로 존재 불가능함을 증명했습니다.

---

## 🌌 Project 2: 삼체 문제의 카오스 궤도 (Three-Body Chaos)
**"혼돈 속의 질서: 비대칭 질량의 춤"**

질량이 서로 다른 세 별($m_1=1.20, m_2=1.44, m_3=1.25$)이 충돌하지 않고 아름답게 공전하는 **'준-안정적 카오스 궤도'**를 발견했습니다. 유전 알고리즘 기반의 확률적 탐색을 통해 단 2번의 시도 만에 이 희귀한 궤도를 포착했습니다.

![Chaos Orbit Visualization](chaos_masterpiece.png)
*(위 이미지는 코드를 통해 직접 생성한 궤도 시각화 결과입니다)*

---

### 📂 파일 설명
- `odd_perfect_search_full_paper.pdf`: 연구 논문 (PDF)
- `odd_perfect_search.py`: 홀수 완전수 탐색 알고리즘 (Python)
- `three_body_chaos.py`: 삼체 문제 시뮬레이터 (Python)

---
*이 연구는 AI와의 협업을 통해 진행되었습니다.*
