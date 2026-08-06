# Obsidian 선택 기능 호환성 게이트

## 확인 결과

- Windows Obsidian 1.12.7에서 WSL의 Local Private 폴더를 Vault로 열었을 때 `EISDIR: illegal operation on a directory, watch` 오류가 발생했다.
- 2026-08-01의 QuickAdd manifest는 버전 2.20.0과 최소 Obsidian 1.13.0을 표시한다. 확인한 Windows Obsidian 1.12.7에는 최신 QuickAdd를 설치하지 않는다.
- 같은 날짜의 Omnisearch manifest는 버전 1.30.1과 최소 Obsidian 1.7.2를 표시한다. 앱 버전 조건은 충족하지만 Vault 파일 감시가 실패했으므로 설치하지 않는다.

## 적용한 게이트

1. `boi_setup.py doctor`와 `obsidian-preview`가 Obsidian host와 Vault transport를 구분한다.
2. Windows host와 WSL Vault 조합은 `blocked-verified`로 판정하고 설정 적용을 거부한다.
3. 차단된 경우 Obsidian 없이 Local Second Brain을 계속 사용하고 그림자 Vault를 만들지 않는다.
4. 정상 Vault에서만 Core 설정을 적용하며 새 파일과 해시는 managed manifest에 기록한다.
5. 복구 명령은 해시가 그대로인 managed 파일만 제거하고 사용자 수정 파일과 Markdown을 보존한다.
6. QuickAdd와 Omnisearch는 Vault 파일 감시, 앱 최소 버전, 사용자 설치 승인을 모두 통과한 뒤 각각 설치한다.

## 근거

- [Obsidian plugin security](https://obsidian.md/help/plugin-security)
- [QuickAdd manifest](https://raw.githubusercontent.com/chhoumann/quickadd/master/manifest.json)
- [Omnisearch manifest](https://raw.githubusercontent.com/scambier/obsidian-omnisearch/master/manifest.json)
