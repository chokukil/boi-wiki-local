# Maintainer evaluation tools

`Invoke-CaseEval.ps1` is the Windows-native execution boundary for synthetic Case Harness comparisons. It is not an employee dependency and does not make a Case `verified` or `reference` by itself.

```powershell
# Readiness only; never opens a login window.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\Invoke-CaseEval.ps1 `
  -Action Doctor -Runtime codex

# Explicit synthetic pilot. Output stays outside the repository under LocalAppData.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\Invoke-CaseEval.ps1 `
  -Action Run -Runtime codex `
  -Configuration with-harness -PromptId p01 -Repetition 1 `
  -ModelId gpt-5.6-sol -ReasoningSetting high -ConfirmSyntheticRun
```

The runner creates a fresh Git workspace, exposes only the selected synthetic inputs and allowed Harness files, disables MCP and submit tools, preserves raw logs outside the repository, and records an execution capture. Both comparison arms receive the same checksum-recorded execution envelope and read-only command policy. An independent evaluator must validate outputs and create the final run artifact before the benchmark counts the run.

Codex on Windows requires an exec-policy rule even for some read-only inspection commands in a non-interactive run. The runner therefore copies [`codex-readonly-eval.rules`](codex-readonly-eval.rules) into the current user's Codex rules directory only for the lifetime of the run and removes it in `finally`. The policy permits only `git status`, `git ls-tree`, `git diff`, `git rev-parse`, and `rg`; file creation still uses the runtime's native edit tool inside the workspace-write sandbox. A later run removes only stale `boi-synthetic-eval-*.rules` files whose owning process is gone; unrelated user rules are never changed.

After a pilot, run the deterministic oracle against the external run directory. A failing exit code is expected when the Harness result is incomplete; the report must not be manually changed into a pass.

```powershell
python .\scripts\case_run_assertions.py `
  "$env:LOCALAPPDATA\BoI-Wiki-Local-Evals\<run-id>" `
  --output "$env:LOCALAPPDATA\BoI-Wiki-Local-Evals\<run-id>\control\deterministic-evaluation.json"
```

Python here is a maintainer/CI oracle only. It is never an employee setup or Second Brain requirement.

Claude login is always manual. If `Doctor` reports `authenticated: false`, the runner stops without opening or automating authentication UI.

On Codex for Windows, `workspace-write` is downgraded to read-only when the Windows sandbox implementation is disabled. The runner explicitly requests the unelevated restricted-token implementation and production evidence must prove that the effective turn context is writable. For diagnosis only, maintainers may use `-CodexSandboxMode danger-full-access -ConfirmUnsandboxedSyntheticPilot`; such a run is always `production_evidence: false` and cannot receive completed execution credit.
