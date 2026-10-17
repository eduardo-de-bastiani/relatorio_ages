# Revisão da prosa de tecnologias — AGES I, II e III

Esta correção foi solicitada pelo usuário em 17/10/2026. O escopo é exclusivamente `chapter-02-text-h-0012`, `chapter-04-text-h-0046` e `chapter-05-text-h-0085`, seus ledgers e a validação/documentação necessária. A instrução está registrada em `migration/approvals/ages-i-ii-iii-technology-prose-correction.json`. O novo PDF exige avaliação humana; a aceitação anterior de AGES I/II e as auditorias de artefatos anteriores permanecem históricas.

## Referência efetivamente examinada

Foi aberto o PDF `relatorio_mariah/relatorio_ages-main/extracted/main.pdf`, nas páginas físicas 46–47 (impressas 45–46), e conferido o trecho correspondente do arquivo `conteudo/4 - ages III/conteudo/2 - desenvolvimento.tex`. Os renders de referência ficam em `build/reference-review/`. O texto da Mariah apresenta tecnologias como parte de orações completas, relacionadas à função no projeto; as chamadas `\cite{...}` vêm junto aos nomes. Há parágrafos naturais para interface, backend e infraestrutura. Não há rótulos de documentação repetidos entre as descrições. A frase final sobre a wiki da Mariah pertence àquele projeto e não autoriza criar um endereço equivalente para outro projeto.

A extração do PDF também confirmou a mesma colocação de citações nas tecnologias das páginas físicas 16 e 29. A estrutura visual foi usada como referência; não foram transferidos projetos, versões, ferramentas ou fatos da autora.

## Causa e correção

As regras anteriores do harness conservaram os rótulos `Documentação...` como texto visível e exigiram os hyperlinks no corpo; em AGES III exigiram ainda a repetição de um conector antes de cada link. O resultado preservava elementos da lista original, mas não atendia à prosa solicitada. Esta instrução substitui essas regras nas três unidades. Rótulos e endereços são conservados no ODT, no manifesto e no ledger; o corpo passa a usar citações autor-data ligadas às referências existentes.

O novo caminho de validação distingue rastreabilidade de preservação semântica: verifica IDs, hashes, intervalos de destino, cobertura, URLs inventariados, citações e comandos LaTeX; a equivalência factual da prosa exige comparação independente com o ODT. A bibliografia e seus metadados são preservados nesta correção.

## Norma e escolha de apresentação

A chamada autor-data e a referência bibliográfica são elementos distintos. A [orientação oficial da PUCRS sobre a NBR 10520:2023](https://biblioteca.pucrs.br/noticias/atualizacao-da-norma-de-citacoes-da-abnt-nbr-10520-julho-2023/), consultada em 17/10/2026, confirma a apresentação de autoria em maiúsculas e minúsculas e mostra referências online com URL/data de acesso. A evidência normativa já registrada em `docs/norms/ABNT_CITATION_EVIDENCE.md` distingue chamadas no texto e referências completas. A remoção dos rótulos repetidos e o agrupamento dos parágrafos são decisões expressas do usuário, conferidas no PDF de referência; não se afirma uma proibição genérica da ABNT contra hyperlinks no corpo.

## Resultado e evidências

**PASS da correção textual e visual delimitada; aceite humano PENDING.** O PDF de revisão é `build/document/main.pdf`, 64 páginas, SHA-256 `27e555177cf74892cee52a90ba5da411ab6b4c4cb379cd954fdd2db17f01a2e1`. As tecnologias estão nas páginas 8 (AGES I), 24–25 (AGES II) e 47–48 (AGES III). O artefato anterior tinha 65 páginas; o refluxo foi inspecionado no PDF completo.

O [auditor de conteúdo](CONTENT_AUDIT.md) comparou diretamente o ODF e o resultado: 75 títulos/parágrafos e 164 registros rastreados, sem perda ou acréscimo factual. Os 25 URLs/âncoras originais permanecem nos ledgers; os rótulos documentais foram retirados do corpo por autorização expressa. A prosa é uma transformação autorizada, não uma alegação de igualdade lexical. O [auditor visual](VISUAL_AUDIT.md) examinou as 64 páginas, com leitura individual das páginas alteradas, sem novo defeito de composição.

As 31 chaves bibliográficas obrigatórias têm chamadas clicáveis com destinos internos válidos nas referências, páginas 62–64. A compilação de revisão terminou com código 0 e nenhum finding; o `main.log` final não contém transbordamentos, citações indefinidas ou erros. O transbordamento antigo de h0085 está resolvido neste artefato. O output agregado conserva avisos intermediários e a limitação ICC herdada; ele não foi apagado. O gate oficial de publicação não foi executado: este é um PDF de revisão.

As chamadas por título, como `TypeScript [...]` e `Documentação [...]` na citação de Python, vêm da bibliografia existente, congelada para esta correção. Não são rótulos de documentação reinseridos no corpo. Sua autoria/metadados requerem curadoria própria, sem inventar responsáveis. Continuam PENDING a correspondência Graph API Explorer/referência genérica, o destino original Impinj e a força documental de algumas afirmações S3/Docker, além das fontes das imagens, da limitação ICC e da aceitação humana da edição. Consulte também [PENDENCIAS](../PENDENCIAS.md).

## Execução e reprodução

| Comando/verificação efetivamente executado | Resultado | Evidência |
|---|---|---|
| `python3 -m unittest discover -s tests -q` | Código 0; 160 testes PASS, incluindo 31 testes adversariais da nova política | Suíte `tests/test_technology_prose.py` e testes existentes; executada pelo implementador do harness |
| `python3 scripts/migration.py verify-source` | Código 0; 112 arquivos protegidos, sem findings | ODT e referência Mariah intactos |
| `python3 scripts/migration.py validate --ledger migration/ledgers/<unidade>.json --unit <unidade>` | 17 unidades PASS; três seções corrigidas revalidadas após o fechamento final por `\par` | `build/technology-review/revised-unit-validation.json` e `unchanged-unit-validation.json` |
| `python3 scripts/migration.py build --profile document-review` | CLI/Tectonic código 0; PASS, sem findings | `build/document/report.json`, `main.log`, `compiler.txt`; captura em `build/technology-review/final-build-stdout.json` |
| `python3 scripts/migration.py visual --pdf build/document/main.pdf` | Código 3 esperado: renders preparados e revisão humana pendente | `build/technology-review/visual-preparation.json`; renders `build/visual/27e555177cf74892/` |
| Inspeção estrutural das anotações PDF com `pypdf` | PASS; 31/31 chaves com destino interno válido | `build/technology-review/pdf-link-check.json` |

O resumo persistente de hashes e resultados está em [VALIDATION.json](VALIDATION.json). O validador automatizado deixa semântica e visual como PENDING por desenho: os pareceres independentes acima, não o código nem o relato do conversor, fornecem a evidência dessas revisões. Disponibilidade externa não foi promovida a PASS.

Um conversor trabalhou sequencialmente nos três LaTeX e respectivos ledgers; outro agente implementou a validação em caminhos distintos. A integração foi central, com auditor de conteúdo e auditor visual separados. Foram usados subagentes Codex no mesmo checkout, sem alegação de conversores isolados em worktrees ou agentes Antigravity. Comparação com o build imediatamente anterior confirmou que somente os três LaTeX mudaram entre as fontes de compilação: estilos, macros, bibliografia, imagens e demais unidades ficaram idênticos. A branch continua `migration/ages-iii`, commit de referência `96c09d125fcde4623d2f4d2218ee6aaa0cb5c656`, com alterações locais; nenhum commit foi criado nesta correção. Não foi iniciada outra edição.
