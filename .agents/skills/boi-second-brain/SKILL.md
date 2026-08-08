---
name: boi-second-brain
description: Set up and operate the OKF + BoI Profile Local Private Second Brain through an AI agent. Use for conversation memory, folder curation, raw capture, immutable-source verification, distillation, local search, review, Wiki linking, optional Obsidian, or Team/Public promotion previews.
---

# BoI Second Brain

Use `boi-wiki-local` rules first. `Local Private` means content is not automatically published to BoI Wiki, MCP, Team, or Public scope. When the user chooses Codex or Claude, selected content is processed under that approved AI service and company policy; disclose that boundary and never describe model processing as zero-byte local-only execution. BoI Wiki or MCP transfer still requires an exact approved promotion preview.

## Product boundary

This is a Harness and Skill, not a resident application. Never require Python, Obsidian, MCP, a community plugin, or a background service for an ordinary employee. Use the agent's own file and hashing tools to perform setup and maintenance. Python scripts in this repository are administrator and CI validation tools only.

This is the Flagship cross-cutting capability of BoI Wiki Local. It is not the Meta Harness builder, not the whole product, and not a domain-specific Case. It may extend meeting, research, incident, onboarding, API, quality, or other Harnesses with durable knowledge, but those Harnesses must remain executable without it.

Keep this product flow stable:

```text
conversation · email · web · document · source folder
→ Local Private raw source and provenance
→ search existing knowledge
→ append evidence · correct · isolate conflict · create only when needed
→ actually reusable knowledge
→ Query · Lint · Review
→ assess sharing value
→ OKF 0.1 + BoI Profile canonical promotion candidate
→ user approval
```

For readable material, finish the same approved work with useful knowledge that preserves the source's claims, decisions, constraints, uncertainty, counterevidence, review state, and Local/Remote boundary. A page that only registers a source or promises later distillation is not a successful Second Brain result.

## Start or resume a session

1. Read `harness.lock`, `.boi-harness/package.json`, `data/boi/index.md`, and the closest folder `index.md`. If a validation runtime is available, verify the pinned Harness. Otherwise perform a reduced check by comparing the embedded `release`, canonical `checksum`, `signature`, and `signature_algorithm` fields between lock and snapshot. The canonical package checksum is not the raw `.boi-harness/package.json` file SHA256; never compare those two values or report their expected difference as a mismatch.
2. Locate `data/boi/private/<employee-id>/.boi-local/second-brain-preferences.json`. Never create real personal work under `0000000`.
   - When `agent_session_check` is `true`, perform the saved-mode session check with native agent file tools.
   - When it is `false`, or the mode is `explicit-only`, do not inspect the source folder or retain conversation knowledge automatically. Wait for an explicit natural-language request.
3. When configuration is missing, ask no more than these three questions: Local Profile ID, one of `알아서 정리` / `정리 전 확인` / `요청할 때만`, and an optional source folder.
4. On Windows, call `scripts/setup-native.ps1` through the agent's hidden shell with the resolved Profile ID, mode, and source folder plus `-PreviewOnly`. Parse the `boi-local-setup-preview/v1` result and retain its exact `plan_hash` in the agent audit trail. Do not ask the user to type the command or copy the hash. If PowerShell execution is unavailable, use native agent file tools to construct the same plan and do not claim the canonical setup check ran.
5. Show only the five-line Korean summary explaining what will be automatic, what will remain local, and what will not happen. Apply only after the user approves that exact summary. On Windows, call the same script with the same resolved values plus `-Approve -ConfirmPlanHash <approved hash>`, then require `설치 결과 확인: 통과` and re-read the preferences and required Wiki pages before reporting success. A hash mismatch requires a new preview.
6. Do not open Explorer, a browser, Obsidian, Terminal, or a settings window during agent-driven setup. Shell execution must remain in the agent tool surface, not a user-visible window.

The preferences file is agent-readable configuration, not an OKF knowledge page. Use `templates/second-brain-preferences.example.json` as the contract and preserve unknown fields when updating it.

## Non-negotiable document contract

Before creating source-derived knowledge, a metadata-only source record, or conversation memory, read and instantiate the matching repository template; do not reconstruct frontmatter from memory. Use `templates/source-knowledge-template.md` for readable email, web, Markdown/text, tabular material, PDF, or image and complete its reusable knowledge, decisions or constraints, evidence and counterevidence, unknowns, review state, and Local/Remote boundary in the same work. A PDF or image counts as readable only after approval when the current agent can actually open or render the selected file and inspect its relevant content; record the inspected page, region, or visible limitation and keep the original file SHA256 as provenance. Do not silently introduce OCR or claim text, diagrams, or conclusions that were not visible. Use `templates/source-record-template.md` only for binary content the current runtime cannot inspect reliably, unsupported input, low-confidence or incomplete rendering, or content that must be quarantined. Use `templates/agent-memory-template.md` for conversation-derived memory. A pre-existing navigation `index.md` may remain plain Markdown only when it contains links and navigation labels, never decisions, claim status, risk summaries, or review conclusions. Do not create a new index solely for a bounded review. If an index owns substantive summaries, it is a Profile page and must use the same exact OKF + BoI fields and provenance as other knowledge. Every created knowledge, evidence, capture, hypothesis, log, guide, context pack, or SOP page must use the exact OKF + BoI field names.

Never abbreviate or rename these fields:

- `okf_version`, never `okf`
- `boi_profile_version`, never `profile_version`
- `type`, never `profile`
- `boi_id`, never `id`
- `review_after`, never `review_on`
- `source_refs` as structured `{type, ref, note/sha256}` objects, never a string-only list
- `generated_from` as structured `{type, ref, sha256}` objects; when the parent is Local knowledge, hash that exact parent file at derivation time so downstream staleness can be detected

Do not invent enum values. `claim_status` is one of `observed`, `inferred`, `direct`, `conflicted`, `decision`, `open-question`, or `superseded`; never use `mixed`. `lifecycle_state` is one of `working`, `memory`, `background`, `archived`, `delete_candidate`, or `protected`; review-required is a claim or memory review state, not a lifecycle value. For a generic semantic-lint or review artifact, use an existing role such as `comparison` or `continuous-log`; never invent roles such as `validation-note`.

When one source bundle contains independent contradictions, unsupported claims, and stale downstream knowledge, give each issue its own claim-owning Profile page with one machine-readable `claim_status`. A plain Markdown index or summary may link them, but one `claim_status: mixed` page must not own unrelated claims. Each review page explicitly labels evidence, counterevidence, unknowns, and next validation when applicable.

Every `generated_from` item must name a concrete file or immutable source with a SHA256. Do not use an unhashed `user-request:*` pseudo-source; if the exact request is material, hash its canonical UTF-8 text or rely on the concrete selected inputs and parent documents. Compute hashes with the agent's native hashing tool and copy the tool result mechanically. Never type or shorten a digest by hand. Re-read every emitted digest and require exactly 64 lowercase hexadecimal characters before reporting success.

At minimum, preserve the template values for `okf_version: "0.1"`, `boi_profile_version: "0.1-local"`, `visibility: local-private`, `classification: internal`, `owner`, `employee_id`, `local_owner_ref`, `local_only: true`, `promotion_status: local_only`, `archive_status: active`, `artifact_visibility`, `lifecycle_state`, `review_after`, and `contains_sensitive`. A file that omits or renames any required field is not a valid Second Brain result even if its prose is correct. Validate the literal field names before reporting success.

## Easy presets

- `알아서 정리` (`auto-curate`, recommended): set `agent_session_check` to `true` and maintain durable knowledge without asking on each item, within the authorization recorded during setup.
- `정리 전 확인` (`suggest`): set `agent_session_check` to `true` and show a short grouped preview before changing knowledge.
- `요청할 때만` (`explicit-only`): set `agent_session_check` to `false` and act only after natural-language requests such as `기억해줘`, `정리해줘`, or `이 기억은 틀렸어`.

Never say `hook`, `manifest`, `sidecar`, `plan hash`, `NOOP`, or `supersede` in the ordinary user flow. Say `AI 시작·종료 시 자동 확인`, `처리 현황`, `원본 정보 문서`, `승인한 변경 확인값`, `이미 반영됨`, and `이전 내용을 보존하고 최신 내용으로 교체`.

## Automatic conversation maintenance

When `agent_session_check` is `true`, before finishing a response decide whether the exchange has durable value. Save decisions, stable preferences, reusable procedures, resolved problems, and important open loops according to the saved mode. When it is `false` or the mode is `explicit-only`, do this only after the user's explicit request. Do not save greetings, transient status, secrets, raw transcripts, or content already represented.

Search existing `memory_key`, tags, links, titles, and body text before writing. Choose exactly one operation:

- `noop`: no durable value or already represented;
- `append-evidence`: add a new source to the same knowledge;
- `revise`: improve the current topic page;
- `supersede`: preserve history and replace an explicitly corrected statement;
- `create`: only when no existing page can own the knowledge;
- `queue-review`: isolate a conflict, sensitive content, or low-confidence inference.

Conversation-derived memory uses `boi/local-knowledge-note`, `knowledge_role: agent-memory`, `promotion_status: local_only`, and `artifact_visibility: memory`. Directly confirmed statements use `claim_status: direct`; agent inference uses `claim_status: inferred`; conflict uses `claim_status: conflicted`. An agent-memory page is never directly promoted. Distill it into ordinary knowledge, context pack, or SOP first.

For `append-evidence`, do not stop after adding a `source_refs` item. Preserve the existing claim, add the new structured source and `generated_from` lineage, and add one concise dated evidence-history line explaining what the source reconfirmed or changed. Do not copy transient or near-miss text into that history. If the new source adds no distinguishable evidence beyond an identical hash, choose `noop` instead.

For an explicit correction, preserve the old value as an alias or clearly dated history entry, make the corrected value the current statement, and retain both old and new provenance. Add the correcting source to both `source_refs` and `generated_from`; never erase the earlier claim as though it had never existed. If the corrected state is already present, add only missing history or provenance and do not create a duplicate topic.

For byte-identical files, search existing structured provenance by SHA256 before writing. If the hash is new, process the content once and create exactly one OKF + BoI Profile source record or knowledge page; that canonical page may list both observed paths. If the hash is already represented, create no new topic page, but verify that one canonical source record already carries its generic `evidence_type`, exact SHA256, and every observed path. Create or repair only that metadata sidecar when it is missing; a missing-sidecar repair consumes one unique-hash slot in the current batch. Two paths with the same SHA256 must never create two topic pages or two source records. Report the extra path as already reflected.

## Automatic source-folder maintenance

If a source folder is configured and `agent_session_check` is `true`, inspect it exactly once on the first AI turn of a new task with the agent's native file tools. Do not require a Codex, Claude, or Obsidian restart. In `explicit-only` mode, do not open or inventory the folder until the user explicitly asks to organize or review it. The common source folder accepts email, Web Clipper Markdown, ordinary Markdown/text, CSV and other supported tables, PDF, images, and general documents. Web Clipper is one input kind inside that folder, not a separate inbox: identify it from an explicit `source_kind: web-clip` and its URL/capture provenance, never from a folder name alone. Do not create a Web Clipper-specific preference, plan, progress file, required subfolder, watcher, background service, or scheduler. Compute SHA256 for supported files; keep unsupported or incompletely rendered files as content-review-needed without claiming their contents. Ignore temporary, incomplete, and explicitly excluded files. The stored processing state is advisory: narrow candidates by current path, size, and modified time, then use SHA256 as the canonical identity.

Group work adaptively by topic and context rather than a fixed document count. Preserve source bytes, detect duplicates by hash, create an OKF + BoI Profile source record, compare with existing knowledge, and then reinforce, revise, create, or queue review. Resume unfinished groups in the next AI session. Never watch the folder when no agent is running and never move or delete the user's original files.

An explicit type request such as `웹 클립만 처리해줘` or `새 PDF만 처리해줘` limits only the current run. Leave unselected new hashes pending; do not mark them complete. The same SHA256 observed under different paths or apparent types produces one canonical knowledge candidate and one review item, with every observation preserved in provenance. Every readable new unique hash uses `templates/source-knowledge-template.md` and becomes a reusable `OKF 0.1 + BoI Profile 0.1-local` candidate with claims, decisions or constraints, evidence, counterevidence, unknowns, review state, and Local/Remote boundary. Put every candidate in the review queue and do not increase the current approved knowledge revision before human approval. If there are no new unique hashes, return `no-change` without creating or editing a report, document, index, log, progress state, or revision.

For a large folder, the approved plan must name ordered adaptive batches and a resumable progress file. One user approval covers every unchanged batch in that exact plan. Process a bounded batch per AI turn, persist completed source hashes and the next batch, and continue on later turns without asking for file-by-file approval. Require a new preview only when the plan hash, source hash, scope, or Local/Remote boundary changes. Do not spend an entire turn repeatedly retrying one failed index or optional navigation update; preserve completed records, record the failure path, and continue or stop with a resumable next step.

When `.boi-local/source-folder-plan.json` and `.boi-local/source-folder-progress.json` already exist, treat them as an approved resume contract only after all of these checks pass: the exact plan-file SHA256 equals `approved_plan_hash`; the current path, byte count, and SHA256 of every planned source reproduce the plan's `source_manifest_hash`; completed and already-reflected hash sets do not overlap; and `next_batch.source_refs` is the first unchanged batch inside `remaining_source_refs`. If any check fails, stop before writing and show a new preview. If they pass, do not ask for another approval: process only that exact next batch, never recreate a completed hash, preserve the plan file byte-for-byte, and update the progress file so every newly completed hash is removed from remaining refs and the following batch becomes the next resume point. In that bounded resume turn, create exactly one canonical Profile artifact per new unique source hash, never a sidecar plus derivative pages. For readable text, Markdown, email, tabular, PDF, or image sources, instantiate `templates/source-knowledge-template.md`; that artifact must be useful now and preserve the reusable claims, decisions, instructions, constraints, uncertainty, counterevidence, and review or promotion boundary actually present in the inspected content. A wrapper that only says the source was hashed or promises later distillation is a failed ingest. For PDF or image input, record what the current runtime actually inspected and any unreadable pages, cropped regions, missing context, or confidence limitation. Use `templates/source-record-template.md` only when the current runtime could not inspect the binary reliably, for unsupported input, or for content that must be quarantined. The one artifact must carry the exact `evidence_sha256`, generic `evidence_type`, `source_refs`, and `generated_from`. Update progress immediately after those artifacts and finish the portable completion summary; defer optional navigation or cross-source synthesis to a later review. Use `boi-local-source-folder-plan/v1` with `scope: local-private`, `preserve_originals: true`, `remote_auto_upload: false`, `user_confirmed: true`, a hash-bound `source_manifest`, and ordered batches; the progress file remains `boi-local-source-folder-progress/v1`.

Choose a bounded apply batch from the available context, source complexity, conflict risk, and the amount of existing knowledge that must be compared. Record the chosen batch and its reason in the approved plan. A duplicate path stays in the same batch as its canonical hash and does not consume another unique-source slot. Reduce the batch when sources are complex or conflicted; never use a fixture-specific file count or enlarge a batch merely to finish within one response.

The first source-folder turn is strictly read-only: inventory path, size, extension, SHA256, duplicate groups, topic batches, and risk flags, then return the exact plan hash. Do not create or edit a Profile, index, log, or progress file before approval. During preview, do not invoke image viewers, OCR, PDF renderers, or content extraction for binary files; classify them from path, extension, and hash and plan them as content-review-needed. After approval, never claim unseen binary contents as facts.

Before creating resumable state, read and instantiate `templates/source-folder-progress.example.json`. Store it at `.boi-local/source-folder-progress.json` with the exact `boi-local-source-folder-progress/v1` field names below. Preserve those keys on every update and do not invent aliases such as `approved_plan_sha256`, `source_manifest_sha256`, `newly_completed_sha256`, or `completed_unique_sha256_count`.

```json
{
  "schema": "boi-local-source-folder-progress/v1",
  "approved_plan_hash": "<sha256>",
  "source_manifest_hash": "<sha256>",
  "completed_sha256": [],
  "already_reflected_sha256": [],
  "remaining_source_refs": [],
  "next_batch": {},
  "status": "in_progress"
}
```

The two hash sets must not overlap and their union must account for every unique source hash. On completion, keep both sets, set `remaining_source_refs` to an empty list, set `next_batch` to an empty object, and mark `status` as `completed`; this state is Local Private audit data, not a promotable Profile document.

Summarize results in user language: existing knowledge reinforced, new topics created, duplicates already reflected, items needing review, and items remaining. Keep artifact links repository-relative or identify them by repository-relative path so the handoff remains valid after an isolated workspace is moved or packaged. Do not expose an evaluator or temporary workspace path. Do not ask for file-by-file approval in `auto-curate` mode.

## Choose the operation

- Folder of mixed sources: inventory email, web clips, tabular data, documents, images, meeting notes, and analysis exports. Split work into adaptive batches. Follow the saved preset; only `suggest` requires an item-group preview.
- Loose source or meeting notes: create an immutable capture with the agent's native file and SHA256 tools. Treat the marked source section as immutable.
- Refined knowledge: create a separate derived page and cite the Local source. Never edit the capture to make it look refined.
- Local lookup: search Markdown and metadata with the agent's native search tools; return file-backed citations.
- Quality or lifecycle review: inspect the OKF/BoI contract, links, provenance, stale claims, contradictions, and review dates directly. Repository scripts are optional CI oracles, not the employee workflow.
- Beginner help: start at `notes/guide/00-start-here.md` in the user's Local Private Vault.
- Obsidian: treat it as an optional Markdown IDE. Do not make local operation depend on the app or a plugin.
- Team/Public sharing: compile a Local preview that shows blockers, warnings, target scope, structured source refs, reviewer, candidate body, and exact hash. Validate the sanitized projection against the actual target BoI Wiki contract when that capability is available. Require a new explicit approval before any remote submit.

## Operate the Local LLM Wiki

- New evidence: build a read-only inventory and a proposed update plan with the source hash, affected pages, relationship changes, Local-only boundary, and exact plan hash. Apply only the exact plan the user approved.
- Investigation question: separate compiled Wiki pages, supporting evidence, and optional remote BoI references. Read the most relevant compiled pages before opening raw evidence. Use explicit `Answer`, `Evidence`, `Counterevidence`, `Unknowns`, `Next checks`, and `Confidence` headings (or clear equivalents in the user's language), with exact citations. For every counterclaim, state whether it changes the current reviewed conclusion; an unverified counterclaim must not silently override reviewed knowledge. If those sections cannot be supported, say the Wiki is insufficient and propose an intake or review step; do not fill the gap from model memory. Save only a reviewed answer with at least one Local citation.
- Wiki health: report contradictions, stale claims, orphans, broken links, and missing provenance; never rewrite conclusions automatically. When the review introduces selected source files or would create or update any Profile page, the first turn is read-only and returns the exact Local Private change preview. A request to "record" or "organize" findings is not approval of an unseen exact plan; write only after the user approves that preview and the source hashes are unchanged.
- Preserve source claim identifiers such as `Claim B`, `H2`, or a decision ID verbatim in the review page title or body. Do not replace an identifiable unsupported claim with an unlabeled paraphrase. Use `conflicted` for a competing claim, `open-question` for an unsupported claim awaiting evidence, and `observed` for a stale downstream condition.
- Investigation pattern: use generic `boi/local-analysis-case`, `boi/local-evidence`, `boi/local-hypothesis`, `boi/local-analysis-log`, and distilled knowledge pages for research, incidents, quality, audit, or technical comparison. Domain examples belong in owner-reviewed Cases, never in this generic Skill or core schema.
- Evidence categories: create `email`, `web-clip`, `tabular-data`, `document`, `image`, `meeting-note`, or `analysis-export`. Domain meaning belongs in reviewed tags and derived documents. Read legacy evidence values for compatibility but do not generate them.
- The priority order is existing BoI Wiki contract, OKF 0.1, BoI Profile, Local Private boundary, Ingest/Query/Lint workflow, then optional Obsidian views. External LLM Wiki examples never replace the OKF + BoI schema.

On Windows, if the normal workspace edit tool fails once because of the sandbox, use the documented workspace-local PowerShell UTF-8 fallback immediately. Do not retry the same failed write, inspect ACLs, or diagnose unrelated environment state. Keep the apply turn bounded to the approved review pages, their nearest index, and one log entry; validate those exact files and finish without running the full repository test suite.

## Answer from the Second Brain

1. Search with the user's exact question and the narrowest known `case_id` when applicable.
2. Start from the highest-ranked compiled role: decision record for current judgments, hypothesis page for a challenged hypothesis, recurrence fingerprint for a repeated signal, continuous log for history, or promotion-ready knowledge for sharing questions.
3. Use evidence sidecars only through their explicit `source_refs`, `supports`, or `contradicts` relationship. Preserve the relationship owner such as `H3:supports` versus `H3:contradicts`.
4. Separate observation, inference, and human decision in the prose. A supported contributor is not a confirmed root cause.
5. Cite Local sources by path and exact SHA256. Cite MCP results by canonical BoI ID, revision, and visibility. Never merge the two citation types silently.
6. Before a maintainer claims that a packaged example is production quality, require the repository benchmark and assertion evidence. This is a release gate, not an employee action.

## Preserve the knowledge model

- Use OKF `0.1` with local BoI Profile `0.1-local` for Local Private files.
- Require `visibility: local-private`, `local_only: true`, `archive_status: active`, and lifecycle metadata.
- Keep capture sources and derived knowledge as separate documents connected by `source_refs` and `generated_from`.
- Use standard Markdown links so the Wiki works in a text editor, Git viewer, agent, and Obsidian.
- If a closest `index.md` already exists, add link-only navigation without restating claims. Do not create one solely for a bounded review. Update an existing Local log, or create a new log only as a fully profiled OKF + BoI page with exact source lineage.
- Leave backlink and graph visualization to Obsidian; do not generate a separate platform graph.

## Connection boundary

- Without MCP, write, search, organize, and review local files only.
- With MCP, shared BoI Wiki content may be searched and cited while writing local files.
- MCP connectivity never uploads Local Private files automatically.
- MCP 없음: boi-wiki-local의 로컬 문서만 작성·검색·정리.
- MCP 연결됨: 사내 boi-wiki 문서를 검색·참조하여 로컬 문서 작성 가능.
- 단순 MCP 연결만으로는 Local Private 문서가 웹에 자동 적재되지 않음.
- Team/Public 적재: promotion 초안 → 민감정보·출처·공개 범위 검증 → 미리보기 → 사용자 승인 → 원격 등록 기능이 지원될 때만 가능.
- The preflight command only creates a Local package and sanitized projection. It never submits.

An explicit request to install or connect BoI Wiki MCP is an agent-driven setup route, not a request to search the currently configured tool list. Follow the repository source preview first, then the pinned MCP connection descriptor and `scripts/connect-boi-wiki-mcp.ps1` Preview → approval → Apply → client restart → Verify contract. Internal Bitbucket authentication or repository-access failure blocks fallback. A DNS, route, refusal, or timeout may select the external GitHub source, but that selection is read/update provenance only and never authorizes push, promotion, or Local Private transfer. The MCP endpoint remains independent and must come from the approved descriptor, environment, or the user.

## Finish

For an ordinary employee, use at most five non-empty lines: one short outcome line and up to four compact bullets. Combine conversation mode, source folder, original preservation, remote auto-upload off, optional Obsidian/MCP status, and one natural-language next-use example instead of expanding them into separate diagnostics. Do not mention Harness verification mechanics unless something failed, and do not require the user to run commands.

For administrator or release validation only, run the repository checks when their optional validation runtime is available. Never run or require these commands as a condition of ordinary employee setup, update, capture, query, review, or promotion preview success:

Run:

```powershell
python scripts\local_lint.py --employee-id ID
python scripts\local_wiki.py --employee-id ID wiki-lint
python scripts\local_review.py --employee-id ID --check
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File .\check.ps1
```

Report created files, source integrity, local-only status, promotion readiness, and any approval still required.
