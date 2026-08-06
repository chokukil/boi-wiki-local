# BoI Wiki Local Second Brain 구축 및 실제 활용 사례

## 배경

사내 웹 BoI Wiki의 PoC와 커스터마이징이 진행된 이후, 개인 작업 단계에서는 OKF + BoI Profile을 그대로 사용하면서 로컬 문서를 Second Brain처럼 축적할 필요가 생겼다. Obsidian을 필수 플랫폼으로 만들지 않고 Markdown 원천 위에 선택형 탐색 도구로 연결했다.

## 이번 사례에서 수행한 흐름

1. Karpathy LLM Wiki, Second Brain 방법론, Obsidian 공식 문서와 플러그인 저장소를 source ledger로 수집했다.
2. 수집 원문에 SHA256과 잠금 상태를 기록했다.
3. 원문을 수정하지 않고 설계 원칙, 설치 Wiki, 플러그인 보안 기준을 별도 문서로 정제했다.
4. 로컬 검색이 결과 경로와 근거 줄을 반환하는지 확인했다.
5. 기존 템플릿 34개의 부족한 프로필 필드를 additive migration으로 보강했다.
6. 연결된 11개 Wiki 페이지로 저장소, 첫 사용, Obsidian, QuickAdd, Omnisearch, MCP와 promotion을 안내했다.
7. Public과 Team 후보는 Local Private 원문이 아니라 정제본에서 별도로 준비했다.

## 검증 결과

- Obsidian과 MCP가 없는 임시 사용자 공간에서 설치, 수집, 정제, 검색, lint가 동작했다.
- 원문 본문을 바꾸면 SHA256 검증이 실패했다.
- 비밀값이 포함된 Public 후보는 preflight에서 차단됐다.
- 설치를 반복하거나 가이드가 수정된 상태에서 재실행해도 기존 파일을 덮어쓰지 않았다.
- Windows PowerShell과 WSL의 전체 check가 모두 통과했다.
- 설치된 Windows Obsidian 1.12.7에서 기존 Vault는 보존한 채 WSL의 템플릿 Local Private 폴더를 열어 보았다. `EISDIR: illegal operation on a directory, watch` 오류가 재현되어 해당 Vault 창만 닫고 연동을 비활성화했다.
- 최신 manifest 재확인 결과 QuickAdd 2.20.0은 최소 Obsidian 1.13.0을 요구해 확인한 앱 1.12.7과 호환되지 않았다. Omnisearch 1.30.1의 최소 앱 버전은 충족하지만 Vault 감시가 실패했으므로 두 플러그인 모두 설치하지 않았다.
- setup preflight가 Windows host + WSL Vault를 `blocked-verified`로 판정하고 설정 파일을 쓰기 전에 중단하며, 정상 환경에서 만든 설정만 해시 기반으로 복구할 수 있도록 검증했다.

## 운영상 결정

- BoI-native 폴더와 프로필을 유지하고 PARA 폴더 체계를 추가하지 않는다.
- Obsidian은 Vault 탐색, Properties, Bases, Backlinks, Graph를 담당하는 선택형 도구다. 현재 Windows + WSL 조합에서는 실제 감시 오류가 재현되어 사용하지 않는다.
- 기본 커뮤니티 플러그인은 QuickAdd와 Omnisearch만 후보로 둔다.
- WSL Vault가 열리지 않는 상태에서는 플러그인을 설치하지 않으며, Windows 폴더에 그림자 사본도 만들지 않는다.
- 앱 버전 조건만으로 플러그인을 허용하지 않는다. Vault 감시, plugin manifest 최소 버전, 사용자 설치 승인을 모두 통과해야 한다.
- MCP는 사내 문서 검색·참조를 확장하지만 Local Private 자동 업로드 권한을 의미하지 않는다.
- promotion은 민감정보, 출처, 공개 범위, 미리보기, 사용자 승인, 원격 지원 여부를 차례로 확인한다.

## 다음 운영 단계

실제 사용자 사번의 Local Private 공간에 설치 Wiki를 생성하고 로컬 워크플로를 먼저 사용한다. Obsidian은 저장소를 Windows-native 위치로 이전하거나 Linux/WSLg 앱을 쓰는 별도 결정이 있을 때 다시 검증한다. Vault가 정상적으로 열린 뒤에만 QuickAdd와 Omnisearch를 각각 별도 승인으로 설치·검증한다. 원격 MCP가 제공되면 Public 설치 가이드와 이 Team 사례를 다시 미리보기하고 승인된 후보만 등록한다.

## 외부 근거

- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Obsidian Vault](https://help.obsidian.md/vault)
- [Obsidian Community plugins](https://help.obsidian.md/community-plugins)
- [Obsidian plugin security](https://obsidian.md/help/plugin-security)
- [QuickAdd](https://github.com/chhoumann/quickadd)
- [QuickAdd manifest](https://raw.githubusercontent.com/chhoumann/quickadd/master/manifest.json)
- [Omnisearch](https://github.com/scambier/obsidian-omnisearch)
- [Omnisearch manifest](https://raw.githubusercontent.com/scambier/obsidian-omnisearch/master/manifest.json)
