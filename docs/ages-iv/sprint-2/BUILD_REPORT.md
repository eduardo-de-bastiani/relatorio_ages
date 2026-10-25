# Relatório de compilação — AGES IV, Sprint 2

| Campo | Resultado |
|---|---|
| Comando | `python3 scripts/migration.py build --profile document-review` |
| Perfil | `document-review` (somente revisão; gate oficial de documento não executado) |
| Compilador | Tectonic concluiu com código 0 |
| Gate do build | **FAIL** — a política bloqueia avisos não revisados |
| PDF | `build/document/main.pdf` |
| SHA-256 PDF | `a07dae33d5d91aea796a41ec8d0c6f1f343fd149645fe8b94e4921e082736662` |
| PDF | 107 páginas, A4 |
| Relatório/logs | `build/document/report.json`, `main.log`, `compiler.txt` |

Hashes dos artefatos de compilação: `main.log` `bc01f76d9161d5990b1542f8cc520fa3b16aeec390b68b28cdd1b83aaa2dd93d`; `compiler.txt` `a07505acbc807be2c0604e4c8426ec58ec9363a633fde363191b7f5e26349dd2`; `report.json` `ad8bc7398bcee2ffc4c39570cfa8e58367bacabf0c918ad8983277e11e8a88c7`; `main.aux` `c1da9ea8a9e0db60d89c3e412a28488e6f34fe6c76eb57796ede9a8a3b66b954`.

O `main.log` final registra cinco overfulls de 1,41573 pt nos índices `.lof`/`.toc` (linhas do log 1096, 1101, 1110, 1115 e 1120) e dois avisos de link vazio `hyperref` (linhas 1191 e 1195), referentes a outras unidades AGES IV. O resumo `compiler.txt` ainda aponta overfulls em conteúdos de AGES II–IV e nas listas; também registra perfil ICC v4.3 não suportado/não incorporado. São avisos globais preexistentes, nenhum atribuído ao arquivo da Sprint 2.

O PDF foi processado pelo comando visual do harness, que retornou `pending_human_review` após renderizar as páginas. Os agentes independentes inspecionaram as páginas 89–92 e emitiram PASS visual local. Esse parecer não transforma o gate global FAIL em PASS nem certifica o restante do documento.

## Rastreabilidade e resultados de validação

- Ledger da unidade: `migration/ledgers/ages-iv-sprint-2.json`, agora vinculado ao PDF pelo caminho e SHA-256 acima.
- Validação do ledger: PASS, sem diferenças textuais ODT; registra aviso de revisão da numeração compilada, revisão humana do texto suplementar e revisão visual.
- Conferência manual de `main.aux`: PASS para a numeração `5.3.3 Sprint 2` na página 89. O aviso `counter_aux_review_required` permanece no resultado do harness, pois seu schema não consome uma evidência `.aux` declarada; o aviso não foi ocultado.
- Auditoria de conteúdo independente: PASS para os sete parágrafos autorizados e o título ODT; ver `CONTENT_AUDIT.md` e `TEXT_DIVERGENCES.json`.
- Auditoria visual independente: PASS local nas páginas 89–92; ver `VISUAL_AUDIT.md`.
- Aprovação humana da Sprint 2/PDF: PENDING.
