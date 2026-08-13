# Scientific Foundation Model Knowledge — 고정 Query 후보 답변

> 어떤 Scientific Foundation Model 주장을 장기 지식으로 유지할 수 있고, 법칙 준수·prediction·재현·일반화를 어떻게 구분해야 하는가?

장기 지식으로 유지할 핵심은 모델 이름이나 benchmark 순위가 아니라 검증 가능한 claim 구조다. 각 claim에는 대상 task, 학습·평가 분포, governing assumption, 물리 제약이 들어간 위치, prediction, 비교 baseline, failure envelope와 reproduction 상태가 함께 있어야 한다.

새 사례는 “physics-informed”가 하나의 상태가 아님을 보여준다.

- MetaFO는 제한된 metamaterial geometry와 loading scope에서 operator-based generalization과 inverse design을 보고한다. 이 범위 밖의 보편 mechanics model로 확대할 수 없다.
- CLOUD는 symmetry-consistent representation을 사용하고 CLOUD-DEBYE downstream module에서 thermodynamic consistency를 강제한다. 이 consistency를 모든 property와 regime의 model-wide 보장으로 읽으면 안 된다.
- NEP89은 89 elements, benchmark와 높은 계산 효율을 보고하고 dataset·demo·fine-tuning artifact를 공개했다. artifact availability는 재현 준비도를 높이지만 독립 재현 성공과 보편 정확도를 뜻하지 않는다.

따라서 장기 지식 상태는 최소한 `empirical prediction`, `explicit constraint`, `peer-reviewed`, `artifact-available`, `independently reproduced`, `counterexample-known`을 분리해야 한다. 수정·철회·후속 재현이 없고 claim 범위도 변하지 않으면 새 revision을 만들 필요가 없다.

semiconductor process·device physics에 필요한 방정식, boundary condition, 허용 오차, 실험·simulation baseline과 failure cost가 없으므로 실제 적용성은 unknown이다. 이 답변은 Community 후보이며 current baseline을 자동 변경하지 않는다.
