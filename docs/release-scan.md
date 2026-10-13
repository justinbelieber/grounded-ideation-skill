# Local publication audit

Date: 2026-10-13. The release scanner reads actual staged bytes, including files that
would otherwise be ignored. It does not rely on .gitignore as proof of privacy.

The initial scan found a local Python executable path in the exported developer pilot's
capability metadata. The public copy now uses a portable redacted tool label and a refreshed
control hash. Research assertions and their artifact hashes are unchanged; the original
private test workspace was not altered for this export. A regression test verifies that
sensitive staged bytes are caught even when the working copy has already been cleaned.

The final scan reports no automatic credential/email/machine-path/binary/resource findings.
This is not a guarantee of privacy or legal clearance. Manual inspection of the manifest,
public examples, notices and efficacy language found no intentionally included private
research, full paper, upstream prompt, model or invented performance claim.

The maintainer subsequently requested public publication under `justinbelieber` and
selected MIT for original contributions. No private author name is used. Owner,
visibility and license choices are recorded in release-state.json. The human review
checklist remains available; no human file-by-file inspection or legal clearance is asserted.
The final publication scan must read the updated staged bytes. Runs, environments and
source caches remain excluded from the public inventory.
