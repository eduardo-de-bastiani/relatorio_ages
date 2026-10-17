# Auditoria independente de conteúdo — AGES IV parcial

**Resultado:** a cobertura de conteúdo até Sprint 1 está aprovada nos limites desta auditoria. A edição permanece **PARCIAL**, pois o corpo do capítulo 7 foi omitido por decisão do usuário; os títulos vazios e a aprovação humana final também continuam pendentes de conclusão/revisão. Esta auditoria não substitui a auditoria visual.

**Origem:** `RELATORIO_ATUAL.odt`, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.

**PDF confrontado:** `build/document/main.pdf`, SHA-256 `30be17560bfc9f1207632222fe85e29a1644bbdd36bbf0220a2bc3fae91068be` (85 páginas; A4). O ODT foi aberto diretamente como ZIP/ODF. A conferência leu `content.xml`, `styles.xml`, os recursos de mídia e as entradas correspondentes de `docs/CONTENT_MANIFEST.json`, dos ledgers, dos arquivos LaTeX e do PDF. Não usei relatórios anteriores de conversão/auditoria como prova.

## Escopo e evidências

O conjunto autorizado tem **17 unidades e 287 IDs distintos** no manifesto. A conferência direta confirmou 17 títulos/níveis de seção, 88 parágrafos, 11 legendas, 11 imagens, 20 hyperlinks, 11 caixas de texto, duas caixas de reflexão, 61 contêineres de lista, 49 itens e 16 cabeçalhos de lista. Não há tabelas nem notas atribuídas a estas unidades. Os 287 IDs foram resolvidos individualmente no `content.xml` pelas localizações do manifesto. A fonte, o manifesto e a autorização concordam no hash ODT congelado.

As verificações determinísticas executadas para cada unidade retornaram `PASS` em 16 unidades e `PARTIAL` na unidade do capítulo 7, como autorizado. A sequência, os IDs e os elementos textuais esperados foram confrontados com os intervalos de destino registrados nos ledgers. A única leitura XML que não deve ser tratada como divergência textual é `text-p-1343`/`text-a-0149`: no ODF, esse link contém, dentro de um mesmo parágrafo, o quadro da Figura 25, a imagem, a legenda e o rótulo. A conversão preserva a relação como figura vinculada e frase com link; achatar esse nó XML duplica a legenda no texto de comparação.

| Unidade | Resultado de conteúdo | Evidência/resumo |
|---|---|---|
| `chapter-06-text-h-0105` | PASS | Título do capítulo presente; numeração apresentada conforme a estrutura LaTeX. |
| `chapter-06-text-h-0106` | PASS | Introdução, três parágrafos, Figura 24 e ordem preservados. |
| `chapter-06-text-h-0107` | PASS | Título de desenvolvimento presente. |
| `chapter-06-text-h-0108` | PASS | Dois repositórios e descrições preservados; URLs/âncoras mapeados; citação de App Store adicionada junto ao termo. |
| `chapter-06-text-h-0109` | PASS | Texto de banco de dados preservado; PostgreSQL/Supabase citados junto aos nomes; Figura 25 e link da wiki preservados. |
| `chapter-06-text-h-0110` | PASS | Texto de arquitetura preservado; as 12 tecnologias citadas junto às menções; Figura 26 e link da wiki preservados. |
| `chapter-06-text-h-0112` | PASS | Quatro imagens/legendas em ordem; link de protótipos mantido no destino original. |
| `chapter-06-text-h-0113` | PASS — equivalência semântica | Os 13 itens da lista original foram reestruturados em quatro parágrafos por responsabilidade; conferi cada descrição e qualificadores contra os parágrafos originais. Todos os itens e sua sequência permanecem. As 13 chamadas autor-data estão junto às tecnologias e clicam para os mesmos URLs que estavam nos links originais. A redação não é lexicalmente idêntica; a transformação de apresentação está documentada e a avaliação foi semântica. |
| `chapter-06-text-h-0114` | PASS | EAP, matriz RACI, duas descrições e Figuras 31–32 presentes em ordem. |
| `chapter-06-text-h-0115` | PASS | Título da seção presente; a forma original “no projetos” foi mantida, sem revisão editorial. |
| `ages-iv-sprint-0` | PASS | Dez parágrafos narrativos, Figuras 33–34 e dois parágrafos de reflexão presentes em ordem. |
| `ages-iv-sprint-1` | PASS | Oito parágrafos de atividades, subtítulo retrospectivo e quatro parágrafos subsequentes, além de dois parágrafos de reflexão, presentes em ordem. |
| `ages-iv-sprint-2` | PASS — título | Apenas `6.3.3 Sprint 2`, conforme o original e a instrução de estrutura futura. |
| `ages-iv-sprint-3` | PASS — título | Apenas `6.3.4 Sprint 3`, sem texto inferido. |
| `ages-iv-sprint-4` | PASS — título | Apenas `6.3.5 Sprint 4`, sem texto inferido. |
| `chapter-06-text-h-0122` | PASS — título | Apenas `6.4 Conclusão`, sem texto inferido. |
| `chapter-07-text-h-0123` | PARTIAL — omissão autorizada | Título incluído; 18 IDs associados ao corpo/listas foram omitidos deliberadamente, conforme decisão explícita do usuário. Não é unidade convertida integralmente. |

## Texto, estrutura e ordem

**PASS — parágrafos e sequência.** Nas unidades completas, os parágrafos narrativos e introspectivos aparecem na sequência de origem. A seção de tecnologias é a transformação lexical autorizada pelo padrão aprovado: comparei os 13 rótulos/descrições fonte com cada menção e oração de destino; não encontrei item, atributo ou qualificador omitido, nem fato adicional atribuível ao projeto. Não usei igualdade lexical nem contagem de palavras como prova dessa seção.

**PASS — `text-h-0118`.** O elemento é um `text:h` ODF de nível 3 (“Retrospectiva da Sprint 1”), ainda que use o estilo `P416`. No destino ele é um título de subseção sem numeração, não uma linha de texto em negrito; aparece na sequência da Sprint 1 no PDF (página 79). O título e o conteúdo que o segue não foram perdidos.

**PASS — estrutura de Sprint.** Sprints 0 e 1 continuam como entradas de subseção no fluxo LaTeX. Os arquivos não introduzem quebra obrigatória antes dos títulos. Sprint 2–4 e conclusão do capítulo 6 são nós de título vazios no próprio ODF e permanecem sem corpo no destino.

**PASS — reflexões.** As duas caixas ODF contêm quatro parágrafos não vazios no total. Os mesmos quatro parágrafos aparecem, em duas chamadas ao ambiente `reflection`, sem acréscimo de narrativa.

**PASS — listas e estruturas encaixadas.** As listas estruturais do ODF não acrescentaram texto visível fora de seus descendentes. As listas EAP/RACI são representadas no destino como itens com suas descrições; não há tabela original neste escopo. O quadro da Figura 25 está dentro de um hyperlink no ODF, estrutura que foi inspecionada no XML e mantida como link da figura e do texto associado.

## Imagens, legendas e referências

**PASS — integridade e sequência das imagens.** As 11 imagens incorporadas foram comparadas byte a byte com seus arquivos de destino; os 11 SHA-256 coincidem. Seus IDs e legendas correspondem às Figuras 24–34, na mesma ordem da origem. As legendas receberam a transformação visual aprovada de “Figure N:” para “Figura N –”; o restante do texto de cada legenda está preservado. A atribuição de autoria/origem das imagens continua **PENDING** para identificação manual; por isso, as linhas “Fonte: pendente de identificação” não são consideradas fontes verificadas.

**PASS — links e destinos.** Os 20 hyperlinks originais foram inventariados. Os 13 links de documentação da seção de tecnologias mantêm exatamente seus URLs nos registros bibliográficos e estão presentes como destinos clicáveis dos respectivos autores-data no PDF. Os links de repositórios e wikis mantêm seus URLs e estão presentes no PDF pelos rótulos descritivos escolhidos no padrão aprovado; os rótulos textuais foram adaptados conforme as instruções de apresentação. As chamadas de App Store e TanStack Query também apontam para as páginas oficiais suplementares autorizadas. Conferi as anotações URI do PDF, não apenas os comandos LaTeX.

**PENDING — disponibilidade externa de cinco URLs AGES.** Os dois endereços de repositório e os três endereços de wiki permanecem com disponibilidade não verificada, conforme decisão do usuário. O destino e a âncora continuam preservados; não infiro que o endereço esteja acessível atualmente.

**PENDING — dois anchors originalmente vazios.** `text-a-0148` e `text-a-0150` estão serializados no LaTeX como hyperlinks sem texto. O PDF/`hyperref` suprime links vazios e emite avisos; os mesmos URLs são acessíveis por links visíveis correspondentes nas seções de banco de dados/arquitetura e pela figura da base de dados. A anotação vazia em si não se materializa no PDF.

**PENDING — escopo factual das citações.** Os documentos oficiais citados apoiam a identificação e as descrições gerais das tecnologias. Não demonstram por si só fatos específicos do Recorda, como prontidão para distribuição na App Store ou configuração efetiva de cada ferramenta. O texto original foi mantido; esta auditoria atesta sua preservação e não certifica esses fatos fora da fonte autoral.

## Omissão autorizada do capítulo 7

**PARTIAL, conforme decisão explícita.** `text-h-0123`, “7 - CONSIDERAÇÕES FINAIS (Somente AGES IV)”, está no LaTeX e no PDF. Os seguintes 18 IDs permanecem fora do destino nesta entrega: `text-p-1539`, `text-p-1540`, `text-p-1541`, `text-list-0280`, `text-list-item-0225`, `text-p-1542`, `text-list-0281`, `text-list-item-0226`, `text-p-1543`, `text-list-item-0227`, `text-p-1544`, `text-list-item-0228`, `text-p-1545`, `text-list-item-0229`, `text-p-1546`, `text-list-item-0230`, `text-p-1547` e `text-p-1549`. Incluem dez parágrafos, seis itens de lista e dois contêineres. A seção continua pendente de produção, não concluída.

## Comandos e limitações desta auditoria

- `sha256sum RELATORIO_ATUAL.odt build/document/main.pdf` — os hashes correspondem aos valores registrados acima.
- Leitura somente de `content.xml` e `styles.xml` do ODT com `zipfile` e `xml.etree.ElementTree`; resolução dos 287 XPaths do escopo; inspeção dos níveis ODF, listas, links e nós de figura/caixa.
- Comparação em lote dos 11 recursos ODF com os 11 arquivos mapeados nos ledgers — 11/11 hashes coincidentes.
- `python3 scripts/migration.py validate --ledger … --unit …` para as 17 unidades — 16 `PASS`, capítulo 7 `PARTIAL` autorizado.
- `pdftotext -layout build/document/main.pdf /tmp/agesiv-final.txt` e leitura do PDF com `pypdf` — conferidos títulos presentes, citações e destinos URI.

O relatório é de integridade do conteúdo-fonte e de correspondência estrutural. A disponibilidade dos endereços, a identificação das fontes das imagens, a revisão visual, a validade normativa geral e a aprovação humana final permanecem fora de um `PASS` nesta auditoria.
