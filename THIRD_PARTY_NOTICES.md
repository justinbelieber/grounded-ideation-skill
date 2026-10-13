# Third-party notices and provenance

The maintainer selected MIT for original contributions and publication under the
GitHub handle `justinbelieber`. No official endorsement or legal clearance is claimed.

| Material | Verified terms / use | Files affected |
| --- | --- | --- |
| [IdeaScientist code](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/LICENSE) | CC BY-NC 4.0; read for method/implementation audit; no code or prompts intentionally copied or mechanically rewritten | Method citations in docs/source-audit.md, docs/method-mapping.md, skill guidance |
| [IdeaScientist paper v1](https://arxiv.org/abs/2610.04074v1) | arXiv license link is CC BY 4.0; ideas cited and bibliographic metadata recorded; no figures/full text distributed | README files, CITATION.cff, mapping and narrow live smoke |
| [Svalbard Idea Vault card](https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault) | Card labels generated fields CC BY 4.0 and metadata CC0; underlying papers retain their own terms. These statements were inspected, not independently adjudicated. No data downloaded. | docs/source-audit.md only |
| [OpenAI skill-creator](https://github.com/openai/skills/tree/main/skills/.system/skill-creator) | Its LICENSE.txt says Apache-2.0. Guidance consulted; installed metadata generator used; no generator/validator source redistributed | agents/openai.yaml generated from independently supplied values; skill format |
| [Codex documentation](https://learn.chatgpt.com/docs/build-skills) | Consulted for interoperability; linked rather than republished | Installation text and metadata |

Original project files: `skills/grounded-ideation/scripts/research_artifacts.py`, all
schemas/templates/profiles, tests, fixtures, eval tasks, release scanner and independently
written documentation. The MIT scope is limited to these original contributions.
Reading an upstream design and writing different words does not by itself settle whether
an adaptation exists. A maintainer must inspect the guidance/schema selections and mapping;
if any content is deemed copied/adapted or uncertain, isolate it, preserve the applicable
attribution/noncommercial obligations and revise the license scope. Do not relicense
upstream material by labeling this entire repository MIT. LICENSE grants MIT permissions for original contributions only. CITATION.cff uses
the maintainer-provided public handle; no private author name is disclosed.

Runtime dependencies are installed by users, not vendored. Tested package metadata:
jsonschema 4.26.0 (MIT), attrs 26.1.0 (MIT), jsonschema-specifications 2025.9.1 (MIT),
referencing 0.37.0 (MIT), rpds-py 2026.9.1 (MIT), typing-extensions 4.16.0 (PSF-2.0).
Test-only PyYAML 6.0.3 is MIT. Preserve upstream licenses if ever bundling these packages;
recheck the resolved versions. Python itself is separately installed, not distributed.
GitHub Actions reference checkout/setup-python; no action source is vendored.

The public corpus/fixture prose is original and conspicuously synthetic. It contains no
real DOI/arXiv impersonation. The real-source smoke uses a public primary source and clearly
states its narrow coverage. No private user research, downloaded paper, upstream prompt,
model or weight belongs in the distribution. See docs/release-checklist.md for final review.
