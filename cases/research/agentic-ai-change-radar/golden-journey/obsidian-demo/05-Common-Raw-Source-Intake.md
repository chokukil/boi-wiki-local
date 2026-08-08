---
demo_stage: intake
demo_status: local-only
demo_order: 5
review_state: preview
tags: [raw-source, web-clip, local-private]
---

# 공통 Raw Source Intake

Web Clipper는 별도 파이프라인이 아니라 이메일, Markdown·TXT, CSV, PDF, 이미지와 함께 공통 원본 폴더에 들어오는 `web-clip` 유형입니다.

```yaml
source_kind: web-clip
source_url: https://example.com/public-source
source_title: Public source example
source_author: Example Author
source_site: Example Site
published_at: 2026-08-01
captured_at: 2026-08-07 09:00
```

원문은 이동·정규화하지 않습니다. 경로·크기·수정 시각으로 후보를 좁히고 SHA256으로 중복을 판정합니다. 새 unique hash 하나만 지식 후보 하나와 review 항목 하나가 됩니다.

이 페이지는 공개 합성 예시이며 실제 Local Private 경로나 원문을 포함하지 않습니다.
