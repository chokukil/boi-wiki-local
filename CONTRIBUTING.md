# BoI Wiki Local 기여 가이드

공유 저장소에는 프로그램, 템플릿, 테스트, 비민감 공용 예제만 기여합니다. 실제 `data/boi/private/{사번}/` 문서는 Git PR이 아니라 BoI promotion 절차로 공유합니다. `boi-local-release-acceptance/v3` 파일럿 evidence도 사용자 문서가 아니지만 저장소 밖의 승인된 위치에만 보관하며 PR에 넣지 않습니다. privacy 검사는 schema version과 관계없이 모든 release-acceptance evidence를 차단합니다.

## Windows 기여 흐름

1. stable 브랜치를 최신 상태로 만든 뒤 feature branch를 만듭니다.
2. 변경 범위를 작게 유지하고 테스트를 추가합니다.
3. 다음 검사를 실행합니다.

```powershell
.\check.cmd
python scripts\contribution_check.py
git add <검토한 파일>
python scripts\contribution_check.py --staged
```

4. staged diff에 실제 사번, 업무 원문, 로컬 경로, PAT, 비밀번호, SSH private key, `.env`, `.obsidian`이 없는지 직접 확인합니다.
5. 외부 기준 저장소에서는 GitHub PR, 사내 반입 후에는 Bitbucket PR에 목적, 사용자 영향, OKF/BoI Profile 호환성, 테스트 결과를 같은 형식으로 기록합니다.

검사를 우회하거나 Local Private 파일을 예제로 익명화했다고 가정하지 않습니다. 공용 예제가 필요하면 `0000000` template profile에서 합성 데이터로 새로 작성합니다.
