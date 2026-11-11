# Correção bibliográfica — 05/11/2026

**Atualização de 06/11/2026:** o autor autorizou aproximações para substituir os marcadores de ano pendente. Foram adicionadas 44 datas EDTF com sinal de dúvida, preservando as cinco datas documentais comprovadas. A prévia atual não contém `[data pendente]`; as lacunas de evidência de publicação original continuam registradas, e os resultados históricos abaixo não equivalem ao estado final dos testes após as correções de 06/11.

O autor autorizou corrigir a utilização do ano de acesso como se fosse ano da fonte e consolidar páginas duplicadas. Links tecnológicos não foram acessados, conforme orientação anterior. A evidência utilizada é local e está em `migration/evidence/references/bibliography-reconciliation-2026-11-05.json`, incluindo as 55 entradas originais, o mapa das seis chaves substituídas, os acessos e as limitações. A origem ODT permanece imutável.

## Resultado

- 55 entradas → 49, consolidando as cinco páginas de TypeScript, React, PostgreSQL, Figma e Docker; páginas diferentes e serviços distintos permanecem separados.
- Citações e `\nocite` foram remapeados. Auditoria independente por agente separado comparou os sete arquivos narrativos ao commit `4a703f33d329770e733aef036c107930c68b2f50` e identificou somente mudanças nas chaves de `\cite`, sem mudança da redação; confirmou URL igual nas seis fusões e hashes dos mapeamentos atualizados. A auditoria não equivale a uma nova revisão semântica completa do ODT.
- As cinco datas documentais anteriores foram preservadas: RFC 9110 (2022), RFC 8259 (2017), MQTT (2019), NIST RFID (2007) e dissertação de Fielding (2000). O ano da citação usa a data da fonte; não usa automaticamente a data de acesso. Datas fictícias atribuídas anteriormente foram removidas.
- Acessos reais foram usados somente onde identificados em evidências locais. **Quatro acessos permanecem pendentes**: Excalidraw (página inicial), Figma (página inicial), Graph API e RFC 9110. Uma busca pela RFC 9110 não comprova abertura da página; a RFC 8259 foi consultada em 16/10/2026 conforme evidência local.
- **44 das 49 entradas não possuem ano documental suficientemente comprovado nos registros locais**. O PDF exibe `[data pendente]` na citação e na referência. Esse texto é provisório, não uma data estimada conforme a NBR 6023:2025. Fontes diferentes que compartilham a mesma autoria e carecem de data podem aparecer com sufixos provisórios como `[data pendente][b]`.
- O tratamento de datas estimadas como `2020?` ainda é PENDING: no teste isolado o estilo congelado não preservou a marca de incerteza. Não incluir ano estimado sem evidência e sem corrigir/testar sua renderização.

## Verificações

- `python3 scripts/migration.py verify-source`: PASS, arquivos protegidos íntegros.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex`: PASS com aviso preexistente `unsupported_citation_command`; 49 entradas e 108 citações identificadas. Isso não comprova metadados nem ABNT.
- Fixture isolada `abntex2`/Tectonic/Biber pelo mantenedor: fonte publicada em 2020 com acesso em 2026 citada como 2020; tese de 2000 citada como 2000; fonte sem data com marcador visível. O teste de data aproximada revelou a limitação acima.
- `python3 -m unittest discover -s tests -p test_latex.py`: 19 testes PASS.
- `python3 -m unittest discover -s tests`: 192 testes, **35 falhas e 10 erros**. A maior parte dos testes de prosa aborta porque a bibliografia e as chaves foram congeladas nos contratos antigos; há também falhas relativas a numeração de figuras e erros de fixtures mutantes. Não foi feito bypass nem atualização indiscriminada de hashes. É necessário contrato suplementar com mapeamento exato, URLs, alterações permitidas, hashes, evidência e testes adversariais, mantendo fixtures históricas e os metadados desconhecidos como PENDING.
- `./build.sh --profile document-review`: Tectonic retornou 0 e gerou `build/document/main.pdf` (115 páginas; SHA-256 `0fa6051bc6189e71d807f2015e1bbcd79f6771c38e852cc4317f0f4335ad89a7`). O gate permanece **FAIL** por 17 ocorrências `OVERFULL` de 1,41573 pt e dois avisos de links vazios; revisão humana do PDF é PENDING. O PDF é uma prévia, não atestado de conformidade.
- A auditoria de fontes originais e os validadores históricos continuam exigindo reconciliação individual. Os resultados do teste completo foram obtidos sobre o estado de trabalho desta tarefa; o arquivo de log temporário é `/tmp/bib-correction-tests-final.log`.

## Pendências

Obter evidências para os 44 anos e quatro acessos ausentes, ou efetuar consulta futura autorizada e registrar a data real; resolver títulos/autorias ainda não comprovados; criar contrato suplementar e testes que reconheçam a consolidação sem enfraquecer os contratos anteriores; corrigir a formatação de anos estimados; investigar os avisos de compilação; submeter a bibliografia e o PDF completos à revisão humana. A proibição do usuário de acessar links impediu nova consulta nesta etapa.

## Anos aproximados — 06/11/2026

Por autorização direta do autor, as 44 fontes sem ano receberam estimativas editoriais da versão documental consultada: `2024?` para Entity Framework Core, cuja página identifica atualização em 2024, e `2026?` para as outras 43. A escolha de 2026 nas páginas sem data específica é uma suposição editorial autorizada, não prova de proximidade da publicação original. A base e a confiança de cada entrada estão em `migration/evidence/references/estimated-years-2026-11-06.json`.

As cinco datas documentais factuais permanecem intactas. Remover somente as 44 linhas `date={YYYY?}` reconstrói exatamente o hash da bibliografia intermediária `6be2693c464927ace22c8d3f99250a877de1256455abfc7673396e0578e4aaf6`; o hash final é `cdcab53b070ad7735b77ec27d0d02ec84d8180d89369baa0e82f1dfcbf7b763d`. Nenhuma autoria, URL ou data exata de acesso foi criada por esse preenchimento.

O estilo foi testado com Tectonic/Biber para exibir anos aproximados como `[2026?]` e, quando necessário, `[2026?a]`/`[2026?b]`, mantendo as datas factuais sem colchetes e os links das citações. A extração do PDF integrado confirmou zero ocorrências de `[data pendente]`. Os quatro acessos sem comprovação e as incertezas de publicação original continuam como pendências factuais; o uso de colchetes não é declaração de conformidade integral com a ABNT.


## Verificação final dos testes — 06/11/2026

Os contratos suplementares agora reconhecem somente a bibliografia consolidada/estimada autorizada, os seis remapeamentos, as transformações de numeração, fontes das figuras e os dois títulos no singular. Hashes, dados de origem e escopos foram mantidos fechados; as fixtures históricas permanecem exercitadas. Os subtestes mutantes restauram seus dados em `finally`. Há testes adversariais de mudança de URL, chave, hash, classificação de data, fonte, asset e título; o Gantt só usa número histórico 32 sem o contrato posterior, e exige 35 no contexto atual.

A suíte integral foi executada pelo agente e reproduzida independentemente pelo coordenador: **213 testes PASS, código 0** (77,990 segundos na reprodução). `verify-source` e `audit-latex` passaram; o último conserva o aviso anterior `unsupported_citation_command`. Em 13 unidades afetadas, 12 auditorias técnicas passaram; `ages-iv-sprint-3` conserva somente `invalid_pdf_evidence` porque o ledger ainda aponta para PDF anterior. Essa evidência visual não foi promovida a atual sem revisão.

O PDF atual tem 115 páginas, zero `[data pendente]`, SHA-256 `f9cf7504186674e272274948344b4de359253a5a0fcb37fb7b268d5ef200ea7d`; os hashes de todos os arquivos-fonte da compilação coincidem com as fontes atuais. Tectonic retornou 0; o gate de compilação continua FAIL pelos 17 `OVERFULL` de 1,41573 pt e dois avisos de links vazios. As páginas 16 e 113 foram examinadas visualmente como amostra da saída de citações/referências, não como revisão completa.

Logs e resultados ficam em `build/validation/years-2026-11-06/` (artefatos locais ignorados pelo Git), com resumo em `summary.json`. Os números 35 falhas/10 erros e oito falhas históricas das seções anteriores descrevem estados anteriores e foram superados pela suíte final. Os quatro acessos sem comprovação e a publicação original das 44 fontes estimadas continuam pendências factuais, embora não haja mais marcadores no PDF.
