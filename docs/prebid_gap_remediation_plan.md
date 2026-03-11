# PreBid Master AI Gap Remediation Plan

## Current Audit Verdict
- Not production-complete for the full enterprise requirement spec.
- Current baseline is prototype level with partial support for parse/synthesize.

## Sprint 1 (High Risk, Must Close)
1. Workspace 3 bid generation chain must compile and run.
2. Full-document mandatory-clause extraction must not truncate at 4k chars.
3. Offline export must produce standalone HTML package from synthesized schema.
4. Mission anchors and guard scripts must stay active after account switch/upgrades.

### Sprint 1 Acceptance
- `/api/prebid/bid-draft` returns compliance matrix + risk list + markdown draft path.
- `/api/prebid/export-offline` outputs a runnable HTML file under `strike_packages/`.
- `parse_rfp` supports `.pdf`, `.txt`, `.md`, `.docx`.
- `star_clauses` includes deterministic extraction from full input text.

## Sprint 2 (Core Productization)
1. Add Workspace 1/2/3 explicit front-end workbench routes and workflow states.
2. Add remark/score mapping overlay with page refs and score refs.
3. Add local persistence (`localStorage`/`IndexedDB`) for draft progress and demo state.
4. Add offline package manifest + static JSON bundle + deterministic checksum.

### Sprint 2 Acceptance
- Three separate workbench entries and role-driven action menus.
- Demo refresh does not lose state.
- Offline package works with no backend service.

## Sprint 3 (Enterprise Hardening)
1. RBAC/authentication and project-level data isolation.
2. Encrypted file storage and audit trails.
3. OCR pipeline for scanned PDFs and Word compatibility extension.
4. Non-functional targets: parse latency, package size, browser compatibility.

### Sprint 3 Acceptance
- Role matrix enforced by backend auth policy.
- Security controls validated with audit logs.
- 100-page parse under SLA target in benchmark environment.

## Immediate Next Build Order
1. Stabilize backend APIs and parser/output contracts.
2. Wire UI to new APIs and expose explicit three-workbench flow.
3. Build regression tests for bid draft generation and offline export.
