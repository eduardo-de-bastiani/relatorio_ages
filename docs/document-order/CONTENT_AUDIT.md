# Auditoria independente de conteúdo e ordem — Hoortech e renumeração

**Resultado da auditoria de conteúdo e ordem: PASS.** A comparação direta do `RELATORIO_ATUAL.odt` com o manifesto, os 56 ledgers autorizados e o LaTeX integrado não encontrou omissões, inversões ou diferenças fora das transformações explicitamente autorizadas. Permanecem itens de rastreabilidade bibliográfica e de revisão visual indicados abaixo; por isso, este relatório não equivale à aprovação humana final.

## Escopo e evidências

- Fonte: [`RELATORIO_ATUAL.odt`](../../RELATORIO_ATUAL.odt), SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`, igual ao hash congelado na autorização.
- Escopo: 56 IDs em [`cliente-hoortech-and-document-order-authorization.json`](../../migration/approvals/cliente-hoortech-and-document-order-authorization.json): 10 unidades Hoortech deslocadas e 46 unidades afetadas pela nova ordem/numeração.
- Destino: [`main.tex`](../../relatorio_AGES_eduardo/main.tex), seus arquivos incluídos, [`CONTENT_MANIFEST.json`](../CONTENT_MANIFEST.json) e `migration/ledgers/`.
- A verificação de fonte contra o manifesto (`verify_manifest`) retornou lista vazia de discrepâncias. A leitura da estrutura ODF considerou `content.xml`, estilos e recursos de mídia, e não somente texto linear.
- A unidade de trabalho foi confrontada com o conteúdo e os registros de origem. Relatórios de conversores e auditorias anteriores não foram usados como evidência.

## Resultado por critério

| Critério | Resultado | Evidência direta |
|---|---|---|
| Cobertura do escopo | PASS | Os 56 IDs autorizados aparecem uma vez cada na composição TeX atual; seus registros e ordem foram conferidos contra a extração ODF/manifesto. |
| Ordem dos capítulos | PASS | `main.tex` organiza: 1 trajetória; 2 AGES I; 3 AGES II; 4 AGES III; 5 AGES IV (inclui 5.4 Conclusão); 6 Participação como cliente Hoortech; 7 Considerações finais (Somente AGES IV). A sequência interna das 10 unidades Hoortech e das outras 46 unidades foi preservada dentro dos respectivos blocos. |
| Hierarquia e títulos | PASS | 56 títulos conferidos, distribuídos em 4 capítulos, 15 seções e 37 subseções; títulos e numeração visível correspondem ao mapa aprovado. |
| Texto, presença e ordem | PASS | O escopo contém 432 registros de texto. 340 correspondem lexicalmente à origem. Os outros 92 pertencem somente às três reescritas técnicas previamente autorizadas: `chapter-04-text-h-0046` (25 registros), `chapter-05-text-h-0085` (30) e `chapter-06-text-h-0113` (37). A comparação semântica direta confirmou, nas três, ordem das tecnologias, usos no projeto, funções e qualificadores; não identifiquei fatos acrescentados ou funções omitidas. |
| Ajuste de referência interna | PASS | Em `text-p-0679`, “No tópico 3.2” mudou para “No tópico 6.2”, conforme autorização explícita. O restante da frase permaneceu igual. |
| Figuras, legendas e numeração | PASS | A composição contém 34 figuras, numeradas em sequência de 1 a 34. As 29 legendas abrangidas pelo remapeamento conservam o texto, com apenas os ajustes autorizados de rótulo/numeração. Os arquivos de imagem comparados correspondem aos bytes dos recursos ODT; não houve divergência de hash. |
| Imagens Hoortech | PASS | As três imagens mantêm vínculo com suas legendas e conteúdo de origem: `draw-image-0006` / `text-p-0663` → Figura 32; `draw-image-0007` / `text-p-0749` → Figura 33; `draw-image-0008` / `text-p-0759` → Figura 34. Os hashes dos recursos ODT e dos arquivos usados no destino coincidem. |
| Links e âncoras | PENDING | Foram localizados 50 hyperlinks ODF. 17 permanecem como links inline no TeX com destino original exato. Os 33 links de documentação nas três seções de tecnologias foram tratados conforme a autorização de reestruturação da prosa; âncoras e URLs originais seguem registrados nos ledgers, e as chamadas autor-data aparecem junto às tecnologias. 31 destinos têm correspondência literal na bibliografia. Dois casos permanecem pendentes, descritos abaixo. |
| Conteúdo do capítulo 7 | PASS | O TeX inclui somente o título do capítulo 7. Os 10 parágrafos e estruturas de lista associados, representados por 18 IDs de conteúdo na autorização parcial de AGES IV, estão intencionalmente omitidos e não foram convertidos como se fossem conteúdo concluído. |
| Conteúdo inventado / outra edição | PASS | A comparação direta não revelou texto estranho à origem dentro das 56 unidades nem conteúdo transferido de outro projeto/edição. |
| Revisão visual / compilação | PENDING | Esta auditoria não compilou nem inspecionou o PDF. Alinhamento, paginação, legibilidade de links, floats e listas de figuras precisam da auditoria visual e do gate de build correspondentes. |

## Pendências e exceções rastreáveis

1. **Graph API — PENDING de equivalência do destino.** O link original `text-a-0126`, âncora Graph API Explorer, aponta para `https://developers.facebook.com/docs/graph-api/guides/explorer/`. A entrada bibliográfica citada (`ages-ii-graph-api`) aponta para `https://developers.facebook.com/docs/graph-api/`. O URL original permanece no ledger; não afirmo que os dois destinos sejam equivalentes.
2. **Impinj — PENDING de correspondência/verificação da fonte.** O link original `text-a-0137` (“Documentação API Impinj R700”) aponta para `https://support.impinj.com/hc/en-us`. A citação usada para a interface IoT aponta a outra URL `https://www.impinj.com/products/technology/key-features/iot-device-interface`. O link original permanece no ledger e a diferença não foi tratada como equivalência.
3. **Fontes das imagens Hoortech — PENDING de identificação humana.** As três imagens e legendas estão preservadas e seus hashes conferem; identificar/publicar a fonte de cada imagem continua pendente.
4. **PDF integrado — PENDING nesta auditoria.** Não realizei compilação ou inspeção visual, conforme escopo. A ordem e a integridade da fonte estão PASS; a apresentação efetiva no PDF não foi avaliada aqui.
5. **Capítulo 7 — conteúdo intencionalmente pendente.** Somente o título está incluído. Os 10 parágrafos e estruturas associados permanecem fora desta entrega por decisão expressa do usuário.

## Base de verificação executada

- Conferência do SHA-256 do ODT e verificação determinística da fonte contra o manifesto.
- Comparação de IDs autorizados, inclusão e hierarquia no grafo de `\input` de `main.tex`.
- Comparação direta dos registros de texto e sequência; análise semântica independente das três unidades cuja prosa foi autorizada para reestruturação.
- Checagem de captions, chamada de figura, numeração sequencial, vínculo caption/imagem e hashes de recursos.
- Confronto dos hyperlinks ODF, hrefs TeX, âncoras e inventário dos links documentais nos ledgers.
- Nenhum build foi executado nesta auditoria.
