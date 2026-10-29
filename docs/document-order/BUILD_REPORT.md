# Build and validation report — Hoortech document reordering

Date: 2026-10-17  
Branch/base commit: `migration/ages-iii` / `8f952a6e3b64c8783cef823e52ed2451af653eae`  
Build profile: `document-review` (review-only; not an official document build)

## Result

The review PDF was generated at [`build/document/main.pdf`](../../build/document/main.pdf), SHA-256 `981e804929793f73fe662e89076556eecf27275c099a16e052ad134fd5911179` (105 A4 pages). The compiler returned exit code 0, but the harness build report is **FAIL** because its warning policy blocks acceptance when warnings remain unreviewed. This PDF is suitable for inspection, not evidence of a passing release build.

The exact command was:

```text
python3 scripts/migration.py build --profile document-review
tectonic --only-cached --untrusted --keep-intermediates --keep-logs main.tex
```

`build/document/report.json` records the command, source hashes, toolchain-lock hash, PDF hash, return code and findings. Auxiliary compiler outputs remain under the ignored `build/document/` directory.

## Findings

The build report flags three `Overfull \hbox` entries at 1.41573 pt:

| Generated file and line | Entry | Assessment |
|---|---|---|
| `main.lof:35` | Figure 34, page 100 | The list entry exceeds its available line width by 1.41573 pt. Visual clipping/collision awaits the independent visual report. |
| `main.toc:97` | Chapter 7 title, page 101 | The ToC entry exceeds its available line width by 1.41573 pt. Visual clipping/collision awaits the independent visual report. |
| `main.toc:100` | References, page 102 | The ToC entry exceeds its available line width by 1.41573 pt. Visual clipping/collision awaits the independent visual report. |

The compiler output also reports eight overfull boxes in existing content files `chapter-04-text-h-0043.tex`, `chapter-05-text-h-0075.tex`, `chapter-05-text-h-0079.tex`, `chapter-05-text-h-0085.tex`, `chapter-06-text-h-0109.tex` and `chapter-06-text-h-0113.tex`. Their overflow amounts range from 3.73651 pt to 92.78046 pt. The independent visual auditor inspected the corresponding PDF pages 31, 51, 53–54, 58–59, 74–75 and 79 and found no visible clipping or collision. These remain compiler diagnostics and are not converted to PASS; this task does not authorize edits to those contents.

Two `hyperref` warnings say “Suppressing empty link on input line 12” in `chapter-06-text-h-0109.tex` and `chapter-06-text-h-0110.tex`. The corresponding empty ODF anchors were preserved. Tectonic also reports an unsupported ICC profile v4.3 and that the profile was not embedded.

## Scope and release status

The reordering authorization and maintainer role limit LaTeX changes in this task to the order of `\input` commands in `relatorio_AGES_eduardo/main.tex`. The three ToC/LoF overfull entries likely require a global list-number-width adjustment; changing a macro or style is outside that authorized file scope. Do not alter global layout until the user approves an explicit scope amendment. The other content overfulls are also outside this reordering task.

Therefore, build status remains **FAIL**, visual review and human approval remain **PENDING**, and the official-document gate was **NOT_RUN** for this review-only build. The PDF hash above identifies the exact artifact inspected; rebuild and update this report after any authorized correction.
