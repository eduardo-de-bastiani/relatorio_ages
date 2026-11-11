# Diagnóstico dos testes do harness — 06/11/2026

**Atualização posterior:** as correções foram implementadas e a suíte final passou com **213 testes, exit 0**, reproduzida pelo coordenador. Os resultados 35/10 e oito falhas abaixo documentam o diagnóstico histórico. Ver `docs/CORRECAO_BIBLIOGRAFICA_2026-11-05.md` e `build/validation/years-2026-11-06/summary.json`.

## Reprodução e comparação

Em 05/11, `python3 -m unittest discover -s tests` no estado de trabalho após a correção bibliográfica executou 192 testes e registrou **35 falhas e 10 erros** (`/tmp/bib-correction-tests-final.log`, log temporário). Para comparar, em 06/11 foi criado um clone Git isolado em `/tmp` do commit `4a703f33d329770e733aef036c107930c68b2f50`, sem as alterações bibliográficas ainda não commitadas. A mesma suíte executou 192 testes, com **8 falhas e nenhum erro** (`/tmp/ages-baseline-tests.log`, log temporário). Os oito identificadores com falha no clone também ocorrem no estado posterior; outros **37 casos de falha/erro** surgem apenas no segundo resultado. `unittest` registra casos de subteste separadamente; a diferença não equivale necessariamente a 37 defeitos independentes.

## Causas observadas

1. **Bibliografia congelada nos validadores:** `scripts/migration_harness/technology_prose.py`, função `_matches_frozen_bibliography`, valida o hash da bibliografia e o sufixo aprovados anteriormente. A correção intencional que passou de 55 para 49 entradas altera o arquivo e os metadados. Vários testes deixam de chegar ao comportamento que queriam testar, pois recebem primeiro `Bibliography differs from frozen approved metadata`. Outros verificadores e políticas exigem chaves e anos específicos antigos, por exemplo `ages-ii-postgresql`, `ages-iv-typescript` e `year=2026`. Isso explica diversas falhas em cascata; não indica, por si só, omissão de texto.
2. **Contratos anteriores de títulos, fontes e figuras:** as oito falhas reproduzidas no commit anterior incluem uma verificação de título AGES IV e sete subtestes de reordenação em unidades com figuras. Exemplos no log incluem `invalid_presentation_serialization` e `invalid_image_evidence`: os contratos históricos ainda esperam numeração e fontes antigas. Essas falhas antecedem a alteração bibliográfica; também não provam, isoladamente, que o PDF esteja correto.
3. **Subtestes mutantes com estado compartilhado:** três erros `subsection not found` ocorrem dentro de `test_detached_colon_and_unknown_citations_rejected`. A suíte altera o mesmo conteúdo em subtestes sucessivos e alguns casos posteriores não encontram mais o trecho procurado após mutação anterior. É preciso isolar ou restaurar a fixture para cada caso e demonstrar o comportamento em regressão.
4. **Metadados faltantes e estilo:** 44 referências sem ano documental e quatro sem acesso comprovado continuam `PENDING`. O marcador `[data pendente]` é provisório. O estilo testado ainda não reproduz corretamente marcações de ano estimado, como `2020?`; isso é um problema de conformidade separado da contagem 35/10.
5. **Build versus testes:** o Tectonic gerou o PDF com código 0, mas o gate de compilação reportou 17 avisos `OVERFULL` e dois avisos de links vazios. Isso é um conjunto de problemas distinto dos 35/10 testes. A inspeção visual e a análise das referências continuam necessárias.

## Caminho seguro para corrigir

1. Criar um contrato suplementar versionado para a nova bibliografia, vinculado à autorização do autor, SHA da origem, hashes anterior e posterior, seis pares exatos de chaves, igualdade de URL e alterações de metadados permitidas. Preservar os contratos e exemplos históricos em vez de substituir os hashes indiscriminadamente.
2. Adaptar de forma coordenada as políticas de citação e verificadores de `technology_prose.py` e `preservation.py`, bem como os registros por unidade afetados, para aceitar somente o mapa autorizado. A reconciliação técnica não pode transformar datas de fontes ou acessos sem evidência em PASS normativo.
3. Criar fixtures imutáveis do estado histórico e do estado consolidado; não depender de que os testes copiem o estado vivo do memorial. Acrescentar testes adversariais para URL alterada, chave indevida, hashes divergentes e datas atribuídas. Corrigir o isolamento dos subtestes mutantes.
4. Criar contrato específico para as figuras inseridas/substituídas, fontes informadas, títulos e nova numeração, preservando a rastreabilidade do original. Verificar se os oito casos anteriores passam por razões válidas.
5. Investigar os `OVERFULL` e links vazios separadamente; recompilar e conferir log, referências, lista de figuras e PDF. Corrigir a renderização de datas estimadas com testes de saída efetiva, sem inventar anos.
6. Rodar novamente a suíte integral, a auditoria de origem e a validação das unidades; classificar resultados como PASS/FAIL/PENDING, incluindo os metadados bibliográficos ainda sem evidência.

Trocar somente hashes, desativar testes ou aceitar os marcadores como conformidade esconderia o problema. O diagnóstico é reproduzível a partir dos comandos descritos, mas os logs em `/tmp` podem ser apagados pelo sistema; não foram usados como aprovação do memorial.
