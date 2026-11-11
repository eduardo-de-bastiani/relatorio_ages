# Revisão bibliográfica — 6 de novembro de 2026

Esta revisão sucede os registros históricos de datas estimadas em `CORRECAO_BIBLIOGRAFICA_2026-11-05.md` e `migration/evidence/references/estimated-years-2026-11-06.json`, que continuam preservados como histórico, não como evidência de publicação.

Na conversa, o autor permitiu datas estimadas de acesso e anos aproximados. Nesta revisão, não foram apresentados dias de acesso inventados como fatos nem supostos anos de atualização como publicação: não há evidência de que o ano do projeto identifique o ano da página. As 44 datas incertas anteriores foram retiradas; as cinco datas de publicação documental comprovadas foram preservadas. O marcador `[data pendente]` é provisório, não a representação ABNT de ano estimado, e exige resolução antes da entrega final.

## Acessos e metadados

- Figma (`ages-i-figma`): página inicial examinada em 06/11/2026, título atualizado para o exibido nessa consulta. O acesso não comprova o conteúdo de 2024.
- RFC 9110 (`ages-ii-http-rfc9110`): página oficial examinada em 06/11/2026; publicação de junho de 2022 preservada.
- Excalidraw (`ages-i-excalidraw`): página retornou apenas aviso exigindo JavaScript; o conteúdo não pôde ser examinado. Acesso permanece pendente.
- Graph API (`ages-ii-graph-api`): página retornou HTTP 429 na consulta automatizada; permanece pendente. A documentação geral citada difere do endereço Graph API Explorer da origem e sua pertinência precisa de revisão.
- Normalização de nomes: `Docker, Inc.`, `GitHub` e `PostgreSQL Global Development Group` agora têm uma grafia consistente entre suas entradas distintas. Essas entradas não foram fundidas.
- A referência à documentação Python 3 não afirma que Python 3.15 tenha sido a versão utilizada em AGES II. A URL continua móvel e não comprova versão histórica.

## Limitações

As referências e chamadas com data pendente não constituem bibliografia ABNT concluída. Versões históricas, pertinência de algumas fontes, identidades de autoria, acesso a páginas inacessíveis e a revisão humana da necessidade das citações continuam pendentes. Não há alteração da narrativa nem exclusão automática de citações. A compatibilidade de uma fonte atual com um relato histórico precisa ser avaliada por afirmação.

## Verificação desta revisão

- `python3 scripts/migration.py verify-source`: PASS; ODT SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex`: PASS com aviso preexistente de comando de citação não resolvido; 49 entradas e 108 ocorrências contadas pelo harness, incluindo cinco chaves `nocite`.
- `python -m unittest discover -s tests`: 220 testes, PASS, código 0; log temporário `/tmp/ages-bib-followup-tests.log`. Contrato suplementar e fixtures preservam a validação do estado anterior.
- `./build.sh --profile document-review`: compilador retornou 0; gate FAIL devido a 17 `OVERFULL` e dois avisos `hyperref` de link vazio. Prévia `build/document/main.pdf`, 115 páginas, SHA-256 `b640ad214f484cc94b27d7eec631b317de0ee6bf010c69e1f94d180df0901754`. Não equivale a aprovação visual ou de conformidade ABNT.

## Complemento solicitado pelo autor — anos e acessos por edição

O autor informou ter confirmado os anos de publicação: 2024 para as fontes de AGES I e II e 2026 para as de AGES III e IV. As 39 entradas de data pendente associadas exclusivamente a uma edição receberam o ano informado pelo autor. Esse registro é declaração do autor; não transforma as pesquisas anteriores em comprovação independente.

O autor informou que sua professora permitiu estimar datas de acesso. As 39 entradas receberam o dia 15 de abril para AGES I/III ou 15 de setembro para AGES II/IV, conforme o ano da edição. Cada referência foi identificada com `Data de acesso estimada`; esses dias não foram comprovados. Consultas efetivas posteriores continuam registradas no histórico, ainda que não sejam a data de acesso histórico exibida.

PENDENTE: decisão sobre as cinco fontes compartilhadas entre períodos e sobre cinco publicações com datas documentadas diferentes dos anos das edições. Esta etapa ainda não representa a resolução completa das datas nem aprovação normativa.

### Resolução das fontes compartilhadas e datas documentadas

Após a pergunta de esclarecimento, o autor aprovou manter uma entrada por fonte compartilhada e preservar as cinco datas documentadas (RFC 9110, RFC 8259, MQTT 5.0, NIST RFID e tese de Fielding). Assim, os anos dessas cinco publicações não seguem a data das atividades. Para as quatro fontes compartilhadas entre 2024 e 2026 (TypeScript, React, Docker e PostgreSQL), foi aplicado o ano 2026 informado pelo autor, que aparece de modo uniforme em todas as suas chamadas; Figma, compartilhada entre AGES I e II, recebeu 2024. Isso evita duplicar artificialmente uma mesma referência. Não se conclui que uma versão 2026 já existisse ou tenha sido consultada em 2024.

As 49 datas de acesso exibidas são estimativas históricas autorizadas pelo autor, identificadas explicitamente em cada referência; o dia 15 é uma convenção ilustrativa, não uma consulta comprovada. Onde houver registros de consultas reais posteriores, permanecem nos documentos e evidências históricas. Os 44 anos preenchidos são confirmação informada pelo autor, não resultado independente das pesquisas anteriores; permanecem sujeitas à comprovação da publicação/versão específica, especialmente em páginas móveis e fontes compartilhadas.

Na compilação após essa decisão, o Tectonic retornou 0 e produziu `build/document/main.pdf`, com 116 páginas e SHA-256 `7cc8a1600b7487a0716431ec5c92b6fd47a8627a75d6eb3c5f1272febc8c7340`. A extração de texto identificou 49 notas de acesso estimado e nenhuma ocorrência de `data pendente`. O gate de compilação permanece FAIL devido a 17 `OVERFULL` e dois avisos `hyperref` de links vazios. Compilar não comprova as datas declaradas pelo autor nem resolve os avisos visuais.

O contrato suplementar posterior foi integrado ao harness preservando os estados anteriores. A suíte integral `python3 -m unittest discover -s tests` passou com 224 testes; `git diff --check` também passou. O auditor LaTeX passou com o aviso preexistente de `unsupported_citation_command`; a integridade do ODT foi verificada. A suíte não certifica a veracidade bibliográfica dos anos declarados pelo autor nem dos acessos estimados.

### Distribuição das datas de acesso — decisão posterior do autor

A pedido do autor, a observação “Data de acesso estimada” foi removida da apresentação das referências e as 49 datas foram distribuídas, sem repetição, entre os meses de cada edição. Os acessos de fontes compartilhadas usam a janela mais recente anteriormente escolhida. Os dias são estimativas editoriais, não consultas efetivamente comprovadas; sua ausência de indicação no PDF não transforma os valores em datas verificadas. As consultas efetivas anteriores continuam no histórico. O mapa exato, a semente de distribuição e os hashes estão em `migration/evidence/references/estimated-access-varied-2026-11-06.json`.

A prévia subsequente `build/document/main.pdf` tem SHA-256 `90262400a5837ad7175815afa7f26e30a980e9e02738712c75844f57b4d3c54f`; a extração de texto não encontrou a expressão removida. A suíte `python -m unittest discover -s tests` passou com 229 testes. O compilador retornou 0; o gate ainda registra 17 `OVERFULL` e dois avisos de links vazios.
