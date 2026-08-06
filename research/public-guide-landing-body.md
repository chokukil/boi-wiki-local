# OKF + BoI Profile 기반 BoI Wiki Local 설치와 사용법

이 가이드는 한 장짜리 설명서가 아니라 서로 연결된 Wiki 페이지로 제공됩니다. 사용자는 필요한 단계만 따라갈 수 있습니다.

## Wiki 페이지 구성

- 시작하기: Local Second Brain의 목적과 최소 구성
- 저장소 설치: 에이전트, Windows PowerShell, WSL/Linux 경로
- 첫 설정: 사용자 ID, Harness, Local Private 프로필 확인
- 10분 튜토리얼: 원문 수집, 별도 정제, 로컬 검색, 검토
- Obsidian 설치와 Vault: 선택형 앱 설치와 기존 폴더 연결
- Obsidian Core 설정: Search, Backlinks, Properties, Bases, Graph
- 커뮤니티 플러그인 보안: 제3자 코드 검토와 승인 경계
- QuickAdd: 로컬 수집 입력 시작점
- Omnisearch: 로컬 Vault 검색 확장과 HTTP 기능 비활성화
- MCP와 공유: 연결 모드 차이와 Team/Public promotion
- 문제 해결과 FAQ: 설치, 파일 감시, 무결성, 용어 설명

## 기본 원칙

1. Obsidian과 MCP가 없어도 로컬 기능은 동작합니다.
2. 수집 원문은 잠그고 정제 문서를 별도로 만듭니다.
3. MCP 연결만으로 Local Private 문서가 웹에 올라가지 않습니다.
4. Team/Public 등록은 정제 초안, 민감정보·출처·범위 검증, 미리보기, 사용자 승인, 원격 등록 지원을 모두 요구합니다.
5. Obsidian 연결은 host와 Vault transport를 먼저 진단합니다. Windows Obsidian이 WSL Vault를 감시하지 못하면 선택 기능만 건너뛰고 그림자 사본을 만들지 않습니다.
6. QuickAdd와 Omnisearch는 Vault 파일 감시, 현재 plugin manifest의 최소 앱 버전, 사용자 설치 승인을 각각 통과한 뒤에만 설치합니다.

각 페이지는 표준 Markdown 링크와 OKF·BoI Profile 메타데이터를 사용합니다. Obsidian은 같은 파일에 백링크, Properties, Bases와 Graph 탐색을 더하지만 필수 저장소는 아닙니다.

## 참고 자료

- [Obsidian 공식 다운로드와 설치 안내](https://obsidian.md/help/Getting%2Bstarted/Download%2Band%2Binstall%2BObsidian)
- [Obsidian Vault 안내](https://help.obsidian.md/vault)
- [Obsidian 커뮤니티 플러그인 보안 안내](https://help.obsidian.md/community-plugins)
- [Obsidian 플러그인 보안](https://obsidian.md/help/plugin-security)
- [QuickAdd manifest](https://raw.githubusercontent.com/chhoumann/quickadd/master/manifest.json)
- [Omnisearch manifest](https://raw.githubusercontent.com/scambier/obsidian-omnisearch/master/manifest.json)
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
