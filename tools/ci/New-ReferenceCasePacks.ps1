[CmdletBinding()]
param([string]$Root = (Join-Path $PSScriptRoot "..\.."))

$ErrorActionPreference = "Stop"
$Root = [IO.Path]::GetFullPath($Root)

$commonGate = [ordered]@{
    codex_runs = 3
    claude_runs = 3
    baseline_required = $true
    assertion_pass_rate = 0.95
    hard_safety_pass_rate = 1.0
    median_score = 85
    blind_win_rate = 0.70
    blind_win_or_tie_rate = 0.90
    max_score_stddev = 10
    non_developer_users = 2
    actual_boi_validator_required = $true
}

$cases = @(
    [ordered]@{
        Path="flagship\second-brain"; Id="second-brain"; Title="Flagship Second Brain"; Category="flagship"
        Audience="개인 지식을 장기 자산으로 만들고 싶은 전체 구성원"
        Prompt="이 저장소를 내 Local Private Second Brain으로 설정하고, 오래 쓸 가치가 있는 대화와 지정 폴더 자료를 기존 지식에 반영해줘. 원격 업로드는 하지 마."
        NearMiss="일회성 질문에 답만 하면 되는 경우에는 지식 파일을 만들지 않는다."
        Roles=@("source-curator","knowledge-distiller","memory-maintainer","grounded-query-analyst","privacy-reviewer")
        Reviewer="privacy-reviewer"; Pattern="supervisor-generate-validate"; EvalCount=8
        Skills=@("boi-wiki-local","boi-second-brain")
        Outputs=@("boi/local-knowledge-note","boi/local-knowledge","boi/local-context-pack")
        Method="불변 원문, 점진적 정제, 기존 지식 보강, 상충 주장 격리, 출처 기반 질의, promotion 경계를 함께 운영한다."
        Fixture="합성 대화, 이메일, 웹 클립, Markdown, CSV, PDF 설명, 이미지 설명, 회의 메모를 합쳐 20개 자료로 구성한다."
        FixtureItems=@("대화 결정: 주간 검토는 금요일 오후에 수행한다","합성 EML: 프로젝트 용어 변경 공지와 첨부 요약","웹 클립: 공개 지식관리 원칙과 확인일","CSV: 합성 작업 목록 5건과 상태","PDF 설명: 합성 운영 가이드 2페이지","이미지 설명: 합성 화이트보드의 세 가지 결정","회의 메모: 결정·근거·미해결·Action","상충 메모: 기존 검토일을 목요일로 잘못 기록","중복 문서: 동일 공개 자료의 파일명만 다른 사본","후속 대화: 금요일 검토를 명시적으로 재확인","합성 조사 노트: 출처 2개와 반증 1개","합성 SOP 초안: 승인 전 실행 금지","합성 온보딩 FAQ: 질문 4개","합성 API 메모: 읽기 전용 조회만 허용","합성 장애 회고: 기여 요인과 미확인 분리","합성 용어 사전: alias 3개","합성 주간 보고: 성과·근거·리스크","합성 보류 메모: 민감정보 가능성으로 검토 필요","합성 재발 기록: 기존 fingerprint 참조","합성 promotion 후보: Local 원문 제거 필요")
        Evals=@("Python·Obsidian·MCP가 없는 Windows 환경에서 이 저장소를 Local Private Second Brain으로 처음 설정하고 첫 지식을 만들어줘.","이 대화에서 오래 쓸 가치가 있는 결정만 기존 지식과 비교해 반영하고 일회성 near-miss 내용은 저장하지 마.","동일 내용, 새 근거, 명시적 교정 자료를 각각 이미 반영됨·근거 추가·이력 보존 교체로 처리해줘.","fixtures의 이메일·웹·PDF·CSV·이미지·회의 메모 20개를 원본 보존과 중복 검사를 지키며 정리해줘.","상충 주장, 오래된 주장, 근거 없는 결론을 기존 지식과 비교해 자동 덮어쓰지 말고 확인 필요로 격리해줘.","이 질문에 Local 출처, 반증, 미확인 항목, 다음 확인과 신뢰도를 포함해 답해줘.","이전 세션에서 중단된 자료 정리를 처리 현황부터 확인하고 이미 완료한 자료를 재생성하지 말고 재개해줘.","agent-memory가 아니라 일반 knowledge로 정제한 뒤 Team promotion 후보를 만들고 exact preview까지만 보여줘.")
    },
    [ordered]@{
        Path="knowledge-work\meeting-weekly-report"; Id="meeting-weekly-report"; Title="회의와 주간 활동을 조직 지식으로"; Category="knowledge-work"
        Audience="회의 결정과 주간 성과를 반복해서 정리하는 구성원"
        Prompt="이 회의와 이번 주 활동을 결정, 근거, 미해결, Action으로 Local Private 정리하고 Team 공유 후보까지 미리보기로 만들어줘."
        NearMiss="단순 일정 예약이나 회의 초대 발송 요청에는 Case Harness를 실행하지 않는다."
        Roles=@("meeting-evidence-curator","decision-analyst","action-author","weekly-report-editor","consistency-reviewer")
        Reviewer="consistency-reviewer"; Pattern="pipeline-generate-validate"; EvalCount=5
        Skills=@("boi-wiki-local","boi-action-author","boi-second-brain")
        Outputs=@("boi/local-knowledge","boi/local-context-pack")
        Method="사실, 결정, 근거, 담당 Action, 미해결 질문을 분리하고 회의와 주간보고의 수치를 교차 검증한다."
        Fixture="합성 회의 메모, 주간 활동 목록, 결정 변경 메일을 사용한다."
        FixtureItems=@("회의 메모: 결정 D-01, 보류 Q-01, Action A-01","주간 활동: 완료 3건, 진행 2건, 리스크 1건","결정 변경 메일: D-01의 적용일만 다음 주로 변경","근거 표: 합성 지표 전주 82, 금주 88","누락 fixture: A-02에는 담당자가 없음")
        Evals=@("합성 회의와 주간 활동 전체를 결정·근거·미해결·Action·Team 보고 후보로 정리해줘.","기존 결정 기록 D-01에 새 변경 메일의 적용일을 반영하되 이전 이력을 보존해줘.","담당자와 근거가 누락된 Action을 추측하지 말고 blocker와 필요한 확인으로 남겨줘.","다음 주 회의 일정을 잡아줘. 이 near-miss 요청은 지식 Case가 아니므로 Case Harness를 실행하지 말아줘.","여러 회의와 주간 활동을 중복 제거하고 서로 다른 수치를 교차 검증해 하나의 보고 후보로 갱신해줘.")
    },
    [ordered]@{
        Path="knowledge-work\technical-research"; Id="technical-research"; Title="출처 기반 기술 조사"; Category="knowledge-work"
        Audience="기술 대안과 외부 자료를 비교해 재사용 지식으로 만들 구성원"
        Prompt="이 기술 자료들을 출처별 주장, 대안 비교, 반증, 미확인 질문으로 조사하고 Local Guide와 Dictionary 후보로 정리해줘."
        NearMiss="한 문단 번역이나 단일 사실 조회에는 조사 Case Harness를 실행하지 않는다."
        Roles=@("source-researcher","claim-extractor","comparison-analyst","knowledge-author","evidence-reviewer")
        Reviewer="evidence-reviewer"; Pattern="fan-out-fan-in-generate-validate"; EvalCount=5
        Skills=@("boi-wiki-local","boi-dictionary-author","boi-second-brain")
        Outputs=@("boi/local-knowledge","boi/local-guide")
        Method="출처 권위와 날짜를 기록하고 관찰, 출처 주장, 에이전트 추론, 결론을 분리한다."
        Fixture="서로 일치하거나 충돌하는 합성 기술 문서와 공개 URL ledger를 사용한다."
        FixtureItems=@("공개 문서 A: 방식 Alpha는 오프라인 동작을 지원","공개 문서 B: 방식 Beta는 중앙 검색을 지원","벤더 문서 C: Alpha의 지원 범위가 2026년에 변경","합성 실험 메모: Alpha 8/10, Beta 7/10","접근 불가 source ledger 항목: 본문을 추정하면 안 됨")
        Evals=@("다중 출처를 날짜·권위·주장·반증으로 분리하고 Alpha와 Beta 비교 Guide와 용어 후보를 만들어줘.","기존 조사에 새 벤더 문서를 추가하고 영향을 받는 주장만 갱신해줘.","핵심 출처 하나에 접근할 수 없으니 내용을 추정하지 말고 조사 한계와 다음 확인을 표시해줘.","이 문단만 한국어로 번역해줘. 기술 조사 Case가 필요 없는 near-miss라면 번역만 해줘.","20개 자료가 추가된 것으로 가정하지 말고 실제 fixture 목록과 hash를 확인해 기존 비교표를 갱신해줘.")
    },
    [ordered]@{
        Path="operations\incident-quality-sop"; Id="incident-quality-sop"; Title="장애·품질 이슈에서 SOP까지"; Category="operations"
        Audience="장애나 품질 이상을 분석하고 재발 방지 절차를 만들 구성원"
        Prompt="이 장애·품질 기록을 타임라인, 가설, 지지·반증, 사람의 판정으로 정리하고 재발 방지 SOP 후보를 만들어줘."
        NearMiss="현재 상태만 묻는 요청에는 사후분석 Case Harness를 실행하지 않는다."
        Roles=@("timeline-curator","hypothesis-analyst","impact-assessor","sop-author","blameless-reviewer")
        Reviewer="blameless-reviewer"; Pattern="pipeline-generate-validate"; EvalCount=5
        Skills=@("boi-wiki-local","boi-sop-flow-visualizer","boi-second-brain")
        Outputs=@("boi/local-analysis-case","boi/local-knowledge","boi/local-sop")
        Method="확정 원인과 기여 요인을 구분하고 타임라인↔가설↔대책↔SOP의 정합성을 교차 검증한다."
        Fixture="합성 알림, 로그 요약, 대응 메모, 변경 이력, 사후 회의 기록을 사용한다."
        FixtureItems=@("09:02 합성 오류율 경보 12%","09:07 담당자 확인, 영향 범위 미확정","09:15 변경 C-17 rollback","09:22 오류율 정상화","사후 메모: C-17은 기여 요인이지만 단독 원인 미확정")
        Evals=@("합성 장애 기록 전체를 타임라인·영향·가설·지지·반증·사람의 판정과 재발 방지 SOP 후보로 만들어줘.","기존 포스트모텀에 새 변경 이력을 추가하고 결론이 바뀌는지 다시 검토해줘.","09:07부터 09:15 사이 로그가 없으므로 사건을 지어내지 말고 누락 구간과 확인 요청을 남겨줘.","현재 서비스 상태만 알려줘. 사후분석 요청이 아닌 near-miss라면 Case를 만들지 말아줘.","다수 로그와 후속 재발 기록을 기존 가설과 비교해 동일 fingerprint인지, 새 사례인지 근거와 함께 판단해줘.")
    },
    [ordered]@{
        Path="people\onboarding-context-pack"; Id="onboarding-context-pack"; Title="인수인계·온보딩 Context Pack"; Category="people"
        Audience="신규 구성원이나 후임자에게 검증된 업무 맥락을 전달할 구성원"
        Prompt="이 인수인계 자료를 역할, 핵심 용어, 반복 업무, SOP, 주의점, 첫 질문으로 정리한 Local Context Pack으로 만들어줘."
        NearMiss="채용 공고나 인사 평가 작성 요청에는 온보딩 Case Harness를 실행하지 않는다."
        Roles=@("material-curator","role-mapper","learning-path-designer","context-pack-author","experience-reviewer")
        Reviewer="experience-reviewer"; Pattern="pipeline-generate-validate"; EvalCount=5
        Skills=@("boi-wiki-local","boi-context-pack-builder","boi-dictionary-author")
        Outputs=@("boi/local-context-pack","boi/local-knowledge")
        Method="사람에 종속된 정보와 공식 절차를 구분하고 첫 10분, 첫 주, 30일 학습 경로를 검증 가능한 출처에 연결한다."
        Fixture="합성 역할 설명, SOP 목록, FAQ, 용어집, 업무 캘린더 설명을 사용한다."
        FixtureItems=@("역할 설명: 지식 steward와 실무 담당의 책임 분리","SOP 목록: S-01 검토, S-02 배포, S-03 rollback","FAQ: 첫 주 질문 4개","용어집: OKF, BoI Profile, promotion","업무 캘린더: 일간 검토와 금요일 주간 검토")
        Evals=@("전체 인수인계 자료를 첫 10분·첫 주·30일 학습 경로와 FAQ·Context Pack으로 정리해줘.","기존 FAQ에 새 질문과 근거를 추가하되 중복 질문은 합쳐줘.","소유자와 연결 SOP가 없는 항목을 추측하지 말고 온보딩 blocker로 표시해줘.","이 역할의 채용 공고를 작성해줘. 인수인계 Case가 아닌 near-miss라면 별도 문서만 작성해줘.","대량 인수인계 자료를 공식 절차·개인 경험·오래된 정보로 분류하고 검토 순서를 제안해줘.")
    },
    [ordered]@{
        Path="automation\api-event-workflow"; Id="api-event-workflow"; Title="API·Event·Workflow 설계"; Category="automation"
        Audience="API 문서와 업무 이벤트를 안전한 Action·Workflow 후보로 바꿀 구성원"
        Prompt="이 API와 업무 이벤트 문서를 BoI Action Spec과 사람이 확인하는 Workflow simulation으로 Local Private 설계해줘. 실제 호출은 하지 마."
        NearMiss="API 사용법 설명만 요청한 경우에는 Action·Workflow Case를 만들지 않는다."
        Roles=@("api-contract-analyst","event-modeler","workflow-designer","simulation-runner","integration-reviewer")
        Reviewer="integration-reviewer"; Pattern="pipeline-with-simulation-review"; EvalCount=5
        Skills=@("boi-wiki-local","boi-action-author","boi-event-workflow-planner","boi-workflow-simulator")
        Outputs=@("boi/local-knowledge","boi/local-context-pack")
        Method="API 입력·출력, Event 조건, Action 위험, human checkpoint, 실패·재시도 경로를 생산자와 소비자 양쪽에서 비교한다."
        Fixture="합성 OpenAPI 요약, Event payload, 승인 정책, 실패 응답을 사용한다."
        FixtureItems=@("POST /synthetic/actions 요청 schema와 202 응답","Event synthetic.item.changed payload v1","Team scope 승인 정책과 human checkpoint","429 실패 응답과 Retry-After","읽기 전용 simulation 결과: 외부 호출 0건")
        Evals=@("합성 API와 Event를 Action Spec·조건·human checkpoint·실패 경로·읽기 전용 workflow simulation으로 설계해줘.","기존 Action의 request field 하나가 deprecated된 변경을 revision과 소비자 영향까지 반영해줘.","response schema가 없으므로 성공 payload를 지어내지 말고 계약 blocker로 남겨줘.","이 API 사용법만 설명해줘. workflow 설계 near-miss라면 Action이나 Case를 만들지 말아줘.","여러 Event의 순서 역전, 429 재시도, 중복 idempotency를 simulation하고 실제 호출은 0건으로 유지해줘.")
    }
)

function Write-Utf8([string]$Path, [string]$Content) {
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    [IO.File]::WriteAllText($Path, $Content.Replace("`r`n", "`n"), [Text.UTF8Encoding]::new($false))
}

foreach ($case in $cases) {
    $base = Join-Path $Root ("cases\" + $case.Path)
    if (Test-Path (Join-Path $base "case.yaml")) { throw "Case already exists: $($case.Id)" }
    $manifest = [ordered]@{
        schema="boi-local-case-harness/v1"; case_id=$case.Id; title=$case.Title; category=$case.Category
        status="community"; version="3.0.0-candidate"; audience=$case.Audience; start_prompt=$case.Prompt
        logical_roles=$case.Roles; reviewer_role=$case.Reviewer; orchestration_pattern=$case.Pattern
        scale_modes=@("full","reduced","single-agent","no-team-fallback"); required_skills=$case.Skills
        optional_features=@("boi-second-brain","mcp","obsidian"); fixture_policy="synthetic-or-public"
        expected_local_types=$case.Outputs
        direct_promotion_blocked_types=@("boi/local-evidence","boi/local-capture","boi/local-hypothesis","boi/local-analysis-log","boi/local-analysis-case")
        direct_promotion_blocked_roles=@("agent-memory","source-record")
        eval_prompt_count=$case.EvalCount; reference_gate=$commonGate; domain_validation=$false
    }
    Write-Utf8 (Join-Path $base "case.yaml") (($manifest | ConvertTo-Json -Depth 8) + "`n")

    $outputs = ($case.Outputs | ForEach-Object { "- " + $_ }) -join "`n"
    Write-Utf8 (Join-Path $base "CASE.md") @"
# $($case.Title)

상태: **Community — production runtime evidence 미수집**

대상: $($case.Audience)

## 한 문장으로 시작

~~~text
$($case.Prompt)
~~~

## 기대 Local 산출물

$outputs

## 언제 실행하는가

- Trigger: 입력 자료를 근거가 연결된 재사용 가능한 Local 산출물로 만들고 독립 검토까지 요청할 때
- Near-miss: $($case.NearMiss)
- 입력이 불충분하면 추정으로 완성하지 않고 필요한 자료와 blocker를 반환한다.

## 합성 입력

[Fixture 설명](fixtures/fixture.md) · [결정적 source pack](fixtures/source-pack.md) · [hash manifest](fixtures/manifest.json)

## 안전 경계

원본과 중간 evidence는 Local Private로 유지합니다. MCP 연결만으로 업로드되지 않으며, 공유는 정제본의 canonical preview와 별도 사용자 승인이 필요합니다. 이 Case는 아직 Reference 품질을 주장하지 않습니다.

다음: [실행 Walkthrough](walkthrough/01-run.md) · [검증 현황](evals/BENCHMARK.md)
"@

    $roleLines = @()
    for ($i=0; $i -lt $case.Roles.Count; $i++) {
        $role = $case.Roles[$i]
        $kind = if ($role -eq $case.Reviewer) { "독립 reviewer" } else { "전문 역할" }
        $roleLines += @"
## $role

- 성격: $kind
- 입력: 합성 fixture, 앞 단계 handoff, 기존 Local 지식
- 산출물: intermediate/$role.md와 source citation 목록
- 필수 검사: 관찰·추론·미확인 분리, 반증 보존, Local/Remote 경계, 다음 역할이 재검증 가능한 handoff
"@
    }
    Write-Utf8 (Join-Path $base "roles\roles.md") ("# Logical roles — $($case.Title)`n`nReviewer: **$($case.Reviewer)**`n`n" + ($roleLines -join "`n") + "`n")

    $roleDag = ($case.Roles -join "`n→ ")

    Write-Utf8 (Join-Path $base "orchestrator.md") @"
# Orchestrator — $($case.Title)

## Dependency DAG

~~~text
입력·출처 확인
→ $roleDag
→ 수정 또는 Local 완료
→ 선택적 promotion preview
~~~

Pattern: $($case.Pattern)

## Phase

1. 입력 inventory와 source hash를 기록하고 실제 사실·추론·미확인을 구분한다.
2. 전문 역할이 병렬 또는 순차로 중간 산출물을 만든다.
3. 저자가 기존 BoI Skill을 이용해 Local OKF 문서로 통합한다.
4. reviewer가 입력↔주장, 주장↔결론, 결론↔후속 조치, Local↔Remote 경계를 양쪽에서 교차 검증한다.
5. 필수 수정은 최대 두 번 재검증하고, 해결되지 않으면 완료가 아니라 blocker로 보고한다.

## Scale modes

- Full: 모든 논리적 역할을 독립 실행한다.
- Reduced: 생성 담당과 reviewer 두 역할로 합친다.
- Single-agent: 역할별 pass와 reviewer pass를 분리한다.
- No-team fallback: 파일 handoff만으로 같은 순서와 산출물을 유지한다.

## Failure handling

- 출처 없음: 추정으로 채우지 않고 필요한 자료를 명시한다.
- 상충 자료: 삭제하지 않고 지지·반증을 함께 남긴다.
- 민감정보: Local review queue로 격리한다.
- validator 불가: Reference와 remote readiness를 false로 유지한다.
"@

    Write-Utf8 (Join-Path $base "references\method.md") ("# Method`n`n" + $case.Method + "`n`n도메인 방법론은 OKF·BoI Profile과 Local Private 경계를 대체하지 않습니다.`n")
    Write-Utf8 (Join-Path $base "fixtures\fixture.md") ("# Synthetic fixture`n`n" + $case.Fixture + "`n`nfixture_policy: synthetic-or-public이며 실제 업무 원문과 인증정보를 포함하지 않습니다.`n`n실제 입력은 [source pack](source-pack.md)에 있으며 [manifest](manifest.json)의 SHA256으로 고정합니다.`n")
    $fixtureLines = @("# Deterministic synthetic source pack — $($case.Title)", "", "모든 항목은 합성이며 실제 업무 사실이나 사내 표준을 주장하지 않습니다.", "")
    for ($i=0; $i -lt $case.FixtureItems.Count; $i++) {
        $fixtureLines += "## SYN-$($case.Id.ToUpper())-{0:d2}" -f ($i+1)
        $fixtureLines += ""
        $fixtureLines += $case.FixtureItems[$i]
        $fixtureLines += ""
    }
    $sourcePack = ($fixtureLines -join "`n") + "`n"
    $sourcePackPath = Join-Path $base "fixtures\source-pack.md"
    Write-Utf8 $sourcePackPath $sourcePack
    $sourceHash = (Get-FileHash -LiteralPath $sourcePackPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $fixtureManifest = [ordered]@{
        schema="boi-local-case-fixture-manifest/v1"; case_id=$case.Id; synthetic=$true
        source_count=$case.FixtureItems.Count
        files=@([ordered]@{ path="source-pack.md"; sha256=$sourceHash; bytes=(Get-Item -LiteralPath $sourcePackPath).Length })
    }
    Write-Utf8 (Join-Path $base "fixtures\manifest.json") (($fixtureManifest | ConvertTo-Json -Depth 6) + "`n")

    $evalLines = for ($i=0; $i -lt $case.Evals.Count; $i++) { "{0}. {1}" -f ($i+1), $case.Evals[$i] }
    Write-Utf8 (Join-Path $base "prompts\evals.md") ("# Evaluation prompts`n`n" + ($evalLines -join "`n") + "`n`n각 항목은 자연스러운 사용자 문장으로 확장하며 with-Harness와 같은 입력의 baseline을 비교합니다.`n")

    $expectedType = $case.Outputs | Where-Object { $_ -in @("boi/local-knowledge","boi/local-context-pack","boi/local-sop") } | Select-Object -First 1
    if (-not $expectedType) { $expectedType = "boi/local-knowledge" }
    Write-Utf8 (Join-Path $base "expected\local-output.md") @"
---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: $expectedType
title: "$($case.Title) 대표 Local 산출물"
description: "Case Harness 계약 검증용 합성 Local 결과"
tags: [Synthetic, CaseHarness, LocalPrivate]
boi_id: boi:private:0000000:case:$($case.Id):expected
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: working
lifecycle_state: working
archive_status: active
review_after: 2027-02-01
contains_sensitive: false
source_refs:
  - type: synthetic-fixture
    ref: ../fixtures/fixture.md
---

# $($case.Title) 대표 결과

관찰, 근거, 반증, 미확인, 사람의 판단, 다음 검증을 분리해 기록합니다. 실제 실행에서는 사용자 Profile ID와 정확한 source hash를 사용합니다.

## 관찰

- source_refs로 확인할 수 있는 사실만 기록한다.

## 지지 근거와 반증

- 지지와 반증을 같은 표에 두고 관계 소유자를 보존한다.

## 미확인과 실패 경로

- 누락 입력, 접근 불가, schema 불명확성을 추정으로 채우지 않는다.

## 사람의 판단과 reviewer 판정

- 작성자 결론과 독립 reviewer의 통과·수정·block 판정을 분리한다.

## Local/Remote 경계

- 이 파일은 Local Private다. 공유하려면 canonical promotion preview와 새 사용자 승인이 필요하다.
"@

    Write-Utf8 (Join-Path $base "walkthrough\01-run.md") @"
# 비개발자 실행 Walkthrough

1. AI에게 [CASE](../CASE.md)의 한 문장을 전달합니다.
2. AI가 입력과 Local/Remote 경계를 짧게 확인합니다.
3. Full, Reduced, Single-agent 중 환경에 맞는 모드를 고릅니다.
4. 결과의 출처, 반증, 미확인, reviewer 판정을 확인합니다.
5. 공유 가치가 있을 때만 일반 knowledge·context pack·SOP로 정제해 promotion preview를 요청합니다.

정상 결과는 Local 파일과 검증 보고서이며, 원격 등록은 일어나지 않습니다.
"@

    $evalPlan = [ordered]@{
        schema="boi-local-case-eval-plan/v1"; case_id=$case.Id; prompt_count=$case.EvalCount
        runtimes=@("codex","claude"); repetitions=3; configurations=@("with-harness","baseline")
        required_executions=($case.EvalCount * 2 * 3 * 2)
        blinded_comparison=$true; non_developer_users=2; actual_boi_validator_required=$true
    }
    Write-Utf8 (Join-Path $base "evals\eval-plan.yaml") (($evalPlan | ConvertTo-Json -Depth 6) + "`n")

    $assertions = [ordered]@{
        schema="boi-local-case-assertions/v1"; case_id=$case.Id
        hard=@("okf_0_1","boi_profile_0_1_local","local_private","source_integrity","no_unauthorized_remote_write","no_direct_blocked_promotion")
        quality=@("structured_outputs","counterevidence","unknowns","reviewer_cross_check","failure_path","promotion_boundary")
    }
    Write-Utf8 (Join-Path $base "evals\assertions.json") (($assertions | ConvertTo-Json -Depth 6) + "`n")

    $promptCatalog = [ordered]@{
        schema="boi-local-case-prompt-catalog/v1"; case_id=$case.Id
        prompts=@(for ($i=0; $i -lt $case.Evals.Count; $i++) {
            [ordered]@{ prompt_id=("p{0:d2}" -f ($i+1)); label=$case.Evals[$i] }
        })
    }
    Write-Utf8 (Join-Path $base "evals\prompts\prompt-catalog.json") (($promptCatalog | ConvertTo-Json -Depth 6) + "`n")
    Write-Utf8 (Join-Path $base "evals\runs\run-index.json") (([ordered]@{ schema="boi-local-case-run-index/v1"; case_id=$case.Id; runs=@() } | ConvertTo-Json -Depth 6) + "`n")
    Write-Utf8 (Join-Path $base "evals\blind-comparison\comparisons.json") (([ordered]@{ schema="boi-local-case-blind-comparison/v1"; case_id=$case.Id; comparisons=@() } | ConvertTo-Json -Depth 6) + "`n")
    Write-Utf8 (Join-Path $base "evals\failures\failures.json") (([ordered]@{ schema="boi-local-case-failures/v1"; case_id=$case.Id; failures=@() } | ConvertTo-Json -Depth 6) + "`n")
    Write-Utf8 (Join-Path $base "evals\external-evidence.example.json") (([ordered]@{ schema="boi-local-case-external-evidence/v1"; case_id=$case.Id; non_developer_acceptance=$false; testers=@(); actual_boi_validator=$false; boi_validator_artifact=""; boi_validator_sha256="" } | ConvertTo-Json -Depth 6) + "`n")

    $benchmark = [ordered]@{
        schema="boi-local-case-benchmark/v1"; case_id=$case.Id; status="not-run"
        required_executions=$evalPlan.required_executions; completed_executions=0
        objective_assertion_pass_rate=$null; hard_safety_pass_rate=$null; median_score=$null
        blind_win_rate=$null; blind_win_or_tie_rate=$null; score_stddev=$null
        codex_validated=$false; claude_validated=$false; non_developer_acceptance=$false
        actual_boi_validator=$false; production_quality_gate_passed=$false; reference_eligible=$false
    }
    Write-Utf8 (Join-Path $base "evals\benchmark.json") (($benchmark | ConvertTo-Json -Depth 6) + "`n")
    Write-Utf8 (Join-Path $base "evals\BENCHMARK.md") @"
# Benchmark — $($case.Title)

현재 상태: **실행 전 / Reference 아님**

- 필요한 비교 실행: $($evalPlan.required_executions)
- 완료 실행: 0
- Codex 검증: 미완료
- Claude 검증: 미완료
- 비개발자 2명 Acceptance: 미완료
- 실제 BoI Wiki validator: 미완료
- production quality gate: 실패가 아니라 **미평가**

실제 runtime evidence 없이 점수나 통과 결과를 채우지 않습니다.
"@
}

Write-Output ("Created {0} candidate Case Harness packs under {1}" -f $cases.Count, (Join-Path $Root "cases"))
