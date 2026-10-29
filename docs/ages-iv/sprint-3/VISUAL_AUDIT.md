# Auditoria visual — PDF atualizado da AGES IV, Sprint 3

**Resultado localizado:** PASS nos elementos inspecionados; três pontos permanecem PENDING. **Gate global do build:** FAIL. **Aceite humano:** PENDING.

- PDF: `build/document/main.pdf` (110 páginas A4).
- SHA-256: `651ff8b5eb3555af4df0cf04b8feae69508e26db6f178ee132ce9a42e5e382b7`.
- Auditoria independente somente leitura; hash conferido.
- Escopo visual inspecionado: páginas 6–7, 10–12, 91–97 e 101–105. O harness renderizou as 110 páginas em `build/visual/651ff8b5eb3555af/`; render automático não equivale à inspeção manual de todas as páginas.

| Página/elemento | Resultado | Evidência |
|---|---|---|
| 7 — Lista de Ilustrações | PASS | Figura 32 aparece na página 92; seguem Figuras 33–35 nas páginas 96, 103 e 105. A legenda longa da Figura 32 ocupa quase toda a linha; o número de página fica alinhado e não há colisão. |
| 11–12 — Sumário | PASS | A entrada “6 CLIENTE AGES – HOORTECH” está em caixa alta; AGES III/IV aparecem com “PROJETO” no singular. A linha extensa de AGES III se divide corretamente; não observei texto cortado. |
| 92 — Figura 32 | PASS/PENDING | Legenda acima, gráfico centralizado e fonte “Fonte: elaboração própria.” abaixo e centralizada. A imagem corresponde ao anexo. Os rótulos internos ficam pequenos quando a página é vista/impressa no tamanho normal; são legíveis com ampliação. Confirmação humana da legibilidade em tamanho de página/impressão permanece PENDING. |
| 91–94 — Sprint 3 | PASS | Sprint começa após a reflexão da Sprint 2 e segue em fluxo contínuo; a remoção do negrito em “14 tarefas do Épico 6” aparece visualmente; a caixa de reflexão está completa e com borda na p. 94. |
| 94 — títulos vazios | PENDING | Sprint 4 e Conclusão aparecem como títulos sem corpo, conforme escopo parcial; há área em branco abaixo, sem folha totalmente vazia. Aceite humano do espaço reservado permanece PENDING. |
| 95 — transição | PASS | A Hoortech começa na página seguinte, sem página em branco intermediária. |
| 96, 103 e 105 — figuras Hoortech | PASS | Figuras 33, 34 e 35 seguem em sequência; legenda acima, imagem centralizada e fonte abaixo/centralizada. |

## Avisos do build

O Tectonic terminou com código 0, mas `build/document/report.json` classifica `document-review` como **FAIL** pela política de avisos não revisados. Oito overfulls de `1,41573 pt` ocorrem nas entradas da Lista de Ilustrações para as páginas 103 e 105 e em entradas do Sumário para páginas 100–103, 106 e 107. Visualmente, os números dessas páginas não parecem cortados. A quantidade e magnitude são iguais às do build anterior; a Figura 32 deslocou as entradas posteriores, sem aumentar os avisos. Dois avisos `hyperref` de links vazios continuam em `chapter-06-text-h-0109.tex:12` e `chapter-06-text-h-0110.tex:12`, fora do recorte Sprint 3. Permanecem outros overfulls no `compiler.txt` e o aviso de perfil ICC; não foram ocultados nem corrigidos nesta tarefa.

## Ferramentas e limites

Comandos/evidências: `python3 scripts/migration.py visual --pdf build/document/main.pdf` (código 3, status `pending_human_review`); `pdfinfo`; `pdftotext`/`pypdf`; `pdftoppm` a 120/140/300 dpi; `pdfimages`; leitura de `.toc`, `.lof`, `main.log` e `compiler.txt`. A auditoria independente cobriu as páginas listadas, não o documento todo. Não modifica LaTeX ou estilo e não substitui a aprovação do usuário.
