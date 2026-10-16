# Auditoria independente de conteúdo — AGES I, pós-correção

> **Histórico substituído:** esta comparação de PDF corresponde ao SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`, anterior à alteração autorizada do parágrafo de tecnologias. A revisão atual e seus limites estão em [CURRENT_REVIEW.md](CURRENT_REVIEW.md).

**Resultado de integridade:** PASS para o conteúdo autoral auditado. **Entrega/aceitação humana:** PENDING. Nenhuma divergência de texto ficou sem correspondência no candidato final.

O PDF comparado naquela execução foi `build/document/main.pdf`, SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4` (19 páginas, A4). O binário anterior não está mais disponível nesse caminho; a saída atual está identificada em [CURRENT_REVIEW.md](CURRENT_REVIEW.md). O original [RELATORIO_ATUAL.odt](/home/eduardo/facul/relatorio_ages/RELATORIO_ATUAL.odt) manteve o SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`; o `content.xml` dentro do ZIP tem SHA-256 `b8fe0f8a7d35303374f5a25b0bcf17630aa4978489d63bc61be2f1c258130c28`.

## Escopo e método

Extraí novamente o ODT por ZIP/XML e usei o XML original como autoridade. Os 15 identificadores de unidade aprovados cobrem 102 elementos textuais únicos: 15 títulos, 82 parágrafos e cinco legendas. Comparei essa sequência com os trechos LaTeX atuais e com o texto extraído do PDF. Os ledgers serviram apenas para localizar faixas de bytes nos arquivos de destino; não usei texto esperado do conversor como evidência.

A comparação autorizou somente as apresentações registradas em `migration/approvals/ages-i-presentation-corrections.json`: rótulos de figuras em português, normalização numérica explicitada ali, chamadas cruzadas, frases dos três links de repositório e supressão visual dos marcadores das cinco tecnologias. Nos cinco itens, nomes, parágrafos e ordem continuam iguais à origem. A comparação de PDF normalizou ligaturas Unicode e hifenização de fim de linha, retirando linhas que contêm apenas folio; não ignorou acentos, pontuação ou ordem.

## Resultados

| Verificação | Estado | Evidência |
|---|---|---|
| Integridade do ODT | PASS | Hash do ODT e do `content.xml` conferem com a referência imutável. |
| Texto ODT → LaTeX | PASS | 102/102 elementos em ordem; 15/15 unidades; nenhum ID não correspondido. |
| Texto ODT → PDF | PASS | 102/102 elementos em ordem no PDF `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`; nenhuma omissão ou inserção autoral encontrada. |
| Hierarquia | PASS | Os 15 títulos da edição mantêm sequência e subdivisões. |
| Figuras e legendas | PASS | Cinco imagens idênticas byte a byte; cinco legendas no PDF na ordem original, com os rótulos autorizados “Figura”. |
| URLs e âncoras | PASS | 11 hrefs originais distintos correspondem ao conjunto de 11 destinos externos do PDF. |
| Reflexões | PASS | Cinco caixas, 17 parágrafos textuais; conteúdo conferido em ordem. Dois parágrafos vazios de layout na primeira caixa não continham texto autoral. |
| Tecnologias | PASS | TypeScript, React, Node.js, Prisma e PostgreSQL permanecem nessa ordem, com seus parágrafos. Os marcadores visuais foram suprimidos conforme a autorização de apresentação. |
| Placeholders | PASS | Banco de dados (`ages-i-database`) e arquitetura (`ages-i-architecture`) aparecem como provisórios, sem conteúdo de diagrama inventado. |
| Conteúdo de outras edições | PASS | Não encontrei títulos de AGES II–IV ou Hoortech no candidato. Menções originais a outras edições dentro da narrativa AGES I permanecem. |
| Grau e chamada da Figura 5, p. 17 | PASS | O PDF mostra e extrai `2° e 4°`; a página renderizada mostra espaço em `Figura 5`. A falha de espaçamento do candidato anterior foi corrigida e esse PDF antigo está supersedido. |
| Origem das imagens | PENDING | As cinco atribuições permanecem “Fonte: pendente de identificação”, para revisão manual do usuário. |
| Disponibilidade atual de links de projeto | PENDING | Seis URLs de repositórios/wikis foram preservadas; o acesso atual não foi verificado. |
| Histórico bibliográfico | PENDING | Cinco referências oficiais foram curadas e têm evidência correspondente; as versões históricas usadas em 2024 e metadados ausentes de autoria/ano não podem ser inferidos. |
| Aprovação humana | PENDING | Ainda não há aprovação do resultado da edição. |

As cinco referências de tecnologia são aparato curado externamente, separado dos 102 blocos autorais. Seus registros oficiais correspondem a `typescript-docs`, `react-docs`, `nodejs-docs`, `prisma-docs` e `postgresql-docs`. A consulta atual não prova qual versão histórica foi usada; nenhum autor, ano de publicação ou data histórica de acesso foi inventado.

## Rastreabilidade

O arquivo [CONTENT_AUDIT_POST_FORMAT.json](/home/eduardo/facul/relatorio_ages/docs/ages-i/CONTENT_AUDIT_POST_FORMAT.json) registra individualmente os 102 IDs, hash do texto extraído de cada bloco, unidades, URLs completas, imagens e hashes, legendas, reflexões, itens tecnológicos, placeholders, comandos e limitações. `unmatched_ids` está vazio.

A conferência textual utilizou Python 3.12.8, `pypdf` 6.18.0 e Poppler 26.01.0. Os comandos de hash, extração do ODT, comparação de unidades, extração PDF, inspeção de anotações e renderização da página 17 tiveram código de saída 0. A compilação do candidato foi feita pelo orquestrador; este auditor não compilou nem modificou o memorial.

Este relatório atesta preservação de conteúdo no escopo acima. A auditoria normativa/visual completa e a aprovação humana continuam como gates separados.
