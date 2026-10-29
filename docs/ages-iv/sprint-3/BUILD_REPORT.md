# Relatório de build — ajustes da Sprint 3 AGES IV

| Campo | Resultado |
|---|---|
| Comando | `python3 scripts/migration.py build --profile document-review` |
| Compilador | Tectonic 0.17.0 com `--only-cached --untrusted --keep-intermediates --keep-logs`; código de saída 0 |
| Perfil/gate | `document-review`; **FAIL** pela política de avisos não revisados |
| Gate oficial de produção | `NOT_RUN` — perfil de revisão, não perfil de documento |
| PDF | `build/document/main.pdf`, 110 páginas A4 |
| SHA-256 PDF | `651ff8b5eb3555af4df0cf04b8feae69508e26db6f178ee132ce9a42e5e382b7` |
| `main.log` | SHA-256 `297abadfc5623c3891b0b52deda5ee5d10ca433b9fb1c56edff8b88b5b1bc5eb` |
| `compiler.txt` | SHA-256 `c963ee03b52cd890b7bb728c1253ac93f93fc8d504f4fed2860d16ac7dd2c70c` |
| `report.json` | SHA-256 `562e0e6379d4d295319d1376fbfdae73f6c213a24d6e15ce3becbc3cf23c9f00` |
| `main.aux` | SHA-256 `5bfec083b2cc03c74692ad8eb1cd84068fcbe3b9cc00fa9261f66bc56320fb15` |
| Arquivo LaTeX da Sprint 3 | SHA-256 `0322e53585ef6acd3a57078bb8216e514b830ca267e58a4966d6fbb1112d6771` |
| PNG Gantt do usuário | SHA-256 `a507cd17d974f716b1133319a89d19907787cf8f058f4b1fc329deb8e799ee05`; 8191 × 1353 px |
| ODT protegido | SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`, inalterado |

## Achados do build

O compilador terminou normalmente, mas o gate do relatório é **FAIL** por oito `Overfull \hbox` de `1,41573 pt` em entradas do Sumário/Lista de Ilustrações e dois avisos `hyperref` de links vazios. Os overfulls apontam às entradas da Lista de Ilustrações das páginas 103 e 105 e às entradas do Sumário das páginas 100–103, 106 e 107. Os números de página estão visíveis/alinhados nas páginas renderizadas, sem corte aparente. A mesma quantidade e magnitude dos overfulls constavam no build anterior; a Figura 32 deslocou as entradas da lista sem aumentar o aviso.

Os dois avisos Hyperref vêm de `chapter-06-text-h-0109.tex:12` e `chapter-06-text-h-0110.tex:12`, fora do conteúdo Sprint 3. `compiler.txt` mantém outros avisos de overfull em unidades anteriores e o aviso de perfil ICC não incorporado. Nenhuma dessas falhas foi omitida ou corrigida nesta tarefa. O código 0 do Tectonic não transforma o gate de qualidade em PASS.

## Verificações

- `python3 -m unittest tests.test_latex tests.test_preservation`: **PASS**, 123 testes.
- Sete `validate --ledger migration/ledgers/<id>.json --unit <id>` para `ages-iv-sprint-3`, `chapter-03-text-h-0023`, `chapter-03-text-h-0024`, `chapter-03-text-h-0038`, `chapter-05-text-h-0074`, `chapter-06-text-h-0105` e `cliente-hoortech-sprint-4`: **PASS**, zero divergências não autorizadas.
- `python3 scripts/migration.py inventory --check`: **PASS**, sem diferença do manifesto.
- `python3 scripts/migration.py verify-source`: **PASS**, ODT e arquivos protegidos intactos.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex`: **PASS**, 81 arquivos alcançáveis e 35 imagens; um aviso preexistente sobre resolução estática de `\\memorial@citefirstword`.
- `git diff --check`: **PASS**.
- Auditoria independente de conteúdo: **PASS** no escopo autorizado; veja `CONTENT_AUDIT.md` e `TEXT_DIVERGENCES.json`.
- Auditoria visual independente: PASS localizado, com legibilidade interna do gráfico, títulos vazios e aprovação humana **PENDING**; veja `VISUAL_AUDIT.md`.
- `python3 scripts/migration.py visual --pdf build/document/main.pdf`: código 3 e status `pending_human_review`, conforme o gate humano do harness; renderizou o documento completo para inspeção, sem declarar aceite automático.
- `scope-check --role orchestrator` no agregado de trabalho sujo: **FAIL** por incluir saídas de papéis diferentes (manifesto mantido pelo EXTRATOR e arquivos de unidades/recursos). Como esses resultados já estão integrados no mesmo checkout, o verificador não separa o intervalo de escrita de cada papel; nenhuma execução independente em worktree foi alegada.

Não houve commit ou push. A aprovação humana do PDF e a resolução/aceite dos avisos globais permanecem pendentes.
