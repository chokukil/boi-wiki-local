---
demo_stage: optional-tools
demo_status: preview-only
demo_order: 6
review_state: approval-required
tags: [quickadd, web-clipper, common-source]
---

# QuickAdd·Web Clipper 설치 preview

두 도구는 선택 사항이며 서로 다른 승인·복구 단위입니다.

| 도구 | 역할 | 저장 대상 | 이번 데모 상태 |
|---|---|---|---|
| QuickAdd 2.21.0 | Obsidian에서 수집 입력을 빠르게 시작 | 이미 선택한 공통 source folder | 설치하지 않음·preview만 |
| Obsidian Web Clipper | 브라우저에서 원문 Markdown 저장 | 같은 공통 source folder | 템플릿만 제공·확장 미설치 |

QuickAdd는 Obsidian 1.13.0 이상과의 호환성을 공식 manifest에서 확인한 뒤 승인한 Vault에만 설치합니다. startup macro, AI provider, 외부 API는 활성화하지 않습니다.

Web Clipper 템플릿은 `source_kind: web-clip`, URL, 제목, 작성자·사이트, 게시일, 수집 시각과 본문만 기록합니다. SHA256 계산, 지식 승인, revision 증가와 원격 전송은 하지 않습니다.

```text
QuickAdd와 Web Clipper 설치 preview를 보여줘.
대상은 지금 승인한 공통 원본 폴더로 제한하고 서로 별도로 승인받아.
```
