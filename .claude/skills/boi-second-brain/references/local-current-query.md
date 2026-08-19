# Local Current Query

Use this operation only when the user asks for an answer from approved Local Current knowledge. It uses native file, search, and SHA256 capabilities and never calls MCP.

## Bounded execution

1. Bind the active real Profile; never fall back to `0000000`.
2. Resolve one question or decision topic and read exactly one Current Knowledge Manifest.
3. Verify the Manifest, its immutable snapshot, and every selected approved Local artifact in one hashing pass.
4. Read only the approved allowlist for Current claims. Search indexes and topic notes may rank candidates but are never evidence or approval authority.
5. Reread the selected source bytes, keep material evidence and counterevidence, and apply the source limit.
6. Compose through `answer-surface-contract.md` and `citation-surface-contract.md`; run at most one presentation-only critic.

## Missing Current

If no valid Manifest exists, do not call the result Current. For an explicit reviewed-only request such as `검토한 내용만으로 답해줘`, report that no reviewed answer is available and do not substitute Review, raw, history, or newly discovered material. Ordinary questions use the bounded fallback defined in the main Skill instead; that fallback does not make every knowledge page reviewed.

## No-write behavior

A query changes no Knowledge, Current Manifest, snapshot, History, Review Queue, log, progress state, or Remote data. A saved answer is a separate governed request and never becomes Current merely because it was saved.
