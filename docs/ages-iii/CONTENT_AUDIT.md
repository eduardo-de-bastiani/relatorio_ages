# Auditoria independente de conteúdo — AGES III

**Integridade de conteúdo: PASS. Status geral da edição: PENDING.** A comparação direta do ODT com as 15 unidades atuais não encontrou omissão, acréscimo factual ou reordenação não autorizada. A revisão semântica de `h0085` está **PASS**, sem alegação de equivalência lexical. Em `h0080`, os dois nós ODF foram unidos em um único parágrafo LaTeX conforme autorização específica, sem mudança na sequência lexical; a extração de texto do PDF atual confirma o espaço em “de prototipagem”. Permanecem pendentes referências, fontes das imagens, achados visuais VA-08/09/10/13 e aprovação humana; VA-03 e VA-04 estão PASS na revisão visual do PDF atual.

## Origem, escopo e método

`RELATORIO_ATUAL.odt` permaneceu intacto e tem SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. Li diretamente o pacote ODF e seus XML/recursos de mídia. Os IDs/XPaths serviram para localizar os elementos, e os arquivos LaTeX atuais foram lidos diretamente. Não usei relato do conversor como prova. A checagem determinística do harness foi executada em memória como verificação auxiliar: 15/15 unidades retornaram `pass`, com alertas de apresentação separados.

O escopo inclui 286 IDs únicos: h0074–h0080, h0085, h0086, Sprints 0–4 e h0097. O conteúdo inclui 106 parágrafos, 16 títulos/subtítulos, 63 listas, 44 itens, 19 cabeçalhos de lista, 13 caixas de texto, oito imagens, 17 links e cinco reflexões com 12 parágrafos preenchidos. Não há tabelas, notas, gráficos, objetos incorporados ou fórmulas no escopo. Os 212 nós `p`/`h` vazios ou whitespace-only são layout, não prosa. Os hashes atuais de todos os 15 `.tex` coincidem com `build/document/report.json`; veja `CONTENT_AUDIT.json`.

## h0085 — verificação semântica

A origem tem descrições fragmentadas por tecnologia; a versão autorizada as apresenta em um parágrafo narrativo. Comparei cada relação entre tecnologia e uso em `content.xml` com o LaTeX atual. Os 13 grupos estão **PASS** para papel, contexto, ordem e qualificadores. A transformação não afirma fatos de implantação ou capacidades novas.

| Tecnologia | Elementos de origem | Resultado |
|---|---|---|
| C# | `text-p-1066` | **PASS** — Backend e gateway; maturidade, produtividade e integração nativa com .NET preservados. |
| .NET | `text-p-1069` | **PASS** — Framework principal para backend e gateway RFID; robustez, performance e integração com nuvem preservadas. |
| React | `text-p-1072, text-p-1073` | **PASS** — Biblioteca da interface web; telas administrativas/de clientes e componentes reutilizáveis preservados. |
| TypeScript e JavaScript | `text-p-1076, text-p-1077` | **PASS** — Uso no frontend para tipagem estática de JavaScript, segurança do código e manutenção preservados. |
| Impinj R700 REST API | `text-p-1080` | **PASS** — Comunicação gateway/leitor RFID físico, configuração e captura de eventos preservados; sem capacidade extra. |
| Entity Framework Core | `text-p-1083, text-p-1084` | **PASS** — ORM no backend .NET, mapeamento relacional, models, migrations, relações, constraints, consultas tipadas, aceleração e padronização preservados; o tab interno de `consultas t<TAB>ipadas` foi removido somente na apresentação, conforme autorização. |
| AWS Lambda | `text-p-1087` | **PASS** — Hospedagem/execução backend serverless, escala sob demanda e menor custo operacional preservados. |
| Amazon S3 | `text-p-1090` | **PASS** — Hospedagem de arquivos estáticos do frontend preservada. |
| Amazon CloudFront | `text-p-1093` | **PASS** — Distribuição do frontend, melhor desempenho e menor latência preservados. |
| Amazon RDS/PostgreSQL | `text-p-1096` | **PASS** — RDS gerenciado hospedando o banco PostgreSQL da aplicação preservado. |
| PostgreSQL | `text-p-1099` | **PASS** — Banco relacional para armazenamento estruturado de informações do sistema preservado. |
| Docker | `text-p-1102` | **PASS** — Padronização de ambientes locais, dependências e apoio a testes automatizados preservados. |
| GitHub Actions/GitLab | `text-p-1105` | **PASS** — Automação CI/CD, validação de qualidade e sincronização dos repositórios GitHub/GitLab preservadas. |

As 13 chamadas documentais aparecem logo após suas descrições correspondentes e conservam âncora e URL do ODT, em ordem. O conectivo individual e o ponto após a âncora seguem a autorização. h0085 tem 19 ocorrências de citação e 16 chaves distintas; todas existem no `.bib`.

A aprovação de autoria corporativa foi cotejada com os campos `author` atuais: as 19 atribuições respaldadas por evidência coincidem. Para TypeScript e JavaScript/MDN, a decisão mantém fallback baseado no título porque não foi verificada autoria corporativa adequada; essas duas entradas continuam sem `author`, e o PDF atual apresenta `TypeScript: […]` e `Introduction […]`. Esse fallback é **PASS** segundo a decisão registrada, não uma divergência. O ano 2026 corresponde à data real de acesso `2026-10-16`; não está sendo usado como data de publicação.

A atribuição de autoria e a preservação semântica não validam o suporte de cada fonte à história de uso. O URL original da Impinj (`text-a-0137`) permanece PENDING; a fonte complementar sustenta identidade/capacidades gerais, não uso histórico no projeto. A evidência de S3 e Docker é parcial. Quatro URLs de repositório/wiki (`text-a-0129`–`text-a-0132`) permanecem indeterminados. A chave de Fielding existe no `.bib`, mas seu ledger continua dizendo “centralized integration pending”; preservar `claim_support_status: PARTIAL`.

## Protótipos em h0080

Os rótulos “Telas de Administrador” (`text-p-1056`) e “Telas de Cliente” (`text-h-0084`) foram removidos conforme autorização do usuário. As cinco figuras 19–23 permanecem em ordem, e as legendas 22 e 23 identificam telas de cliente. As oito imagens do escopo têm bytes iguais aos recursos do ODT; a autoria das fontes permanece pendente.

O `content.xml` do ODT contém dois elementos `text:p` consecutivos, associados no manifesto aos IDs `text-p-1053` (XPath `/office:document-content[1]/office:body[1]/office:text[1]/text:p[826]`, ordem 6494) e `text-p-1054` (XPath `/office:document-content[1]/office:body[1]/office:text[1]/text:p[827]`, ordem 6495). O primeiro contém “Os protótipos de alta-fidelidade foram construídos no Figma, ferramenta web de” (SHA-256 do texto UTF-8 `88b98de18aa28f45ae5d224d1f9001937a563846545f5b43a52e4db26a3dadf0`); o segundo contém “prototipagem e design.” (SHA-256 `3fdca8d9d3abc7d7c68fc5ffc3b65a90e389989d5d4405f5505748f31bd1cc15`). São IDs do manifesto, não atributos `xml:id` do ODF.

A autorização `migration/approvals/ages-iii-prototype-intro-merge.json` permite unir somente essa fronteira. O arquivo LaTeX marca ambos os IDs em comentários de origem, não insere `\par` entre eles e mantém um único parágrafo até o fechamento após “design.”. O ledger os rastreia em spans `335–442` e `464–486` do mesmo arquivo, com SHA-256 de destino `05c5878eed951aca51b4e2d5dc4786a834a1220b7367b7e4acf1d4aa88510baf`; SHA-256 atual do ledger: `62a9dd8a787b3e1eadaf3c34f01f44ab59c2627f1075b71c3833ca3f40d7e862`. A sequência lexical reunida é “Os protótipos de alta-fidelidade foram construídos no Figma, ferramenta web de prototipagem e design.” e corresponde à origem, acrescentando-se separadamente a citação autor-data existente de Figma após o nome.

Para o PDF atual (SHA-256 `1bb11250fba90a866e55a95250bf022915655feef90ecf487da80c3c9e755ac7`), `pdftotext -layout -enc UTF-8 build/document/main.pdf -` extrai na página 44 as linhas “Os protótipos de alta-ﬁdelidade foram construídos no Figma (Figma, 2026), ferra-” e “menta web de prototipagem e design.”. A extração confirma o espaço entre “de” e “prototipagem”. Ela mostra a quebra/hifenização automática de “ferramenta” como `ferra-`/`menta`. A auditoria visual independente para este mesmo SHA confirma VA-03 e VA-04 **PASS**; VA-08, VA-09, VA-10 e VA-13 continuam **PENDING**. A junção de conteúdo está **PASS**, autorizada; o gate visual geral e a aprovação humana da edição permanecem pendentes.

## Links, figuras, reflexões e Sprints

Os 17 URLs coincidem com a origem após decodificar escapes LaTeX (`\%`→`%`, `\#`→`#`). As 13 âncoras de h0085 permanecem textualmente iguais; quatro âncoras anteriores foram reescritas no padrão aprovado, sem mudar destinos. O mapeamento por ID, URL, âncora e ordem está em `TEXT_DIVERGENCES.json`. A igualdade do URL não comprova sua disponibilidade externa.

As oito imagens e suas posições lógicas correspondem por SHA-256; a sequência de legendas é Figura 16–23 com a padronização “Figura N –”. As cinco reflexões e 12 parágrafos preenchidos estão preservados. Sprints 0–4 seguem a ordem original sem quebra obrigatória de página antes dos títulos. O ODT mantém o `<text:tab/>` original em `text-p-1084`; a autorização `migration/approvals/ages-iii-internal-tab-removal.json` remove esse tab apenas na apresentação de `consultas tipadas`. No `content.xml`, o parágrafo contém quatro tabs (três de layout já tratadas sob a disposição prévia `inline_tab_layout` e um entre `t` e `ipadas`). O LaTeX atual mapeia `text-p-1083`, `text-p-1084` e `text-p-1085` em sequência; os spans adjacentes não carregam a nova exceção e o link de documentação Entity Framework permanece no span seguinte. `pdftotext` no PDF SHA `1bb11250fba90a866e55a95250bf022915655feef90ecf487da80c3c9e755ac7` extrai “pregado na criação de models, migrations, relacionamentos, constraints e consultas” seguido por “tipadas, acelerando o desenvolvimento e padronizando o acesso aos dados. Mais”, formando “consultas tipadas” sem a separação interna. A auditoria visual atual também marca VA-04 PASS. A narrativa completa segue sob a autorização semântica anterior; não alego equivalência lexical do parágrafo todo.

## PDF e avisos

O PDF avaliado está em [build/document/main.pdf](/home/eduardo/facul/relatorio_ages/build/document/main.pdf), SHA-256 `1bb11250fba90a866e55a95250bf022915655feef90ecf487da80c3c9e755ac7`, 65 páginas A4. `pdfinfo` e `pdftotext -layout -enc UTF-8` retornaram código 0. Esta reauditoria de conteúdo não recompilou o documento. A auditoria visual delta independente está concluída para o mesmo PDF e seus achados estão discriminados abaixo. O `main.log` atual (SHA-256 `a76e9938299f10139eab14517f0b9321f7701b8fc46663bf0a8b1f8681055d8b`) contém o overfull de 2,72131 pt em h0085; o gate de compilação continua FAIL.

`compiler.txt` atual (SHA-256 `89c82e70c621261182e61f37d4512fadda59976837e274e4d842866dadc1a85b`) também agrega avisos de h0043 (4,74695 pt), h0075 (92,78046 pt), h0079 (60,17422 pt) e repete o aviso de h0085 em passagens agregadas, além dos avisos ICC. Os três primeiros não aparecem no `main.log` atual. A auditoria visual independente do PDF atual (SHA `1bb11250fba90a866e55a95250bf022915655feef90ecf487da80c3c9e755ac7`) concluiu VA-03 e VA-04 **PASS**; VA-08, VA-09, VA-10 e VA-13 permanecem **PENDING**, portanto o status visual geral continua pendente.

## Pendências

1. Resolver VA-08, VA-09, VA-10 e VA-13 conforme o relatório visual; VA-03 e VA-04 estão **PASS** no PDF atual. A aprovação humana da edição ainda é necessária.
2. Identificar fontes das oito figuras e verificar destinos/referências que continuam pendentes ou parciais.
3. Reconciliar o status bibliográfico do ledger Fielding sem alterar o suporte factual `PARTIAL`.
4. Manter o overfull final visível no log e avaliar correção tipográfica sem alterar redação; a remoção do tab interno foi aprovada e validada.
5. Aguardar aprovação humana da edição AGES III.

Esta auditoria não é certificação integral de conformidade ABNT nem autorização para outra edição.
