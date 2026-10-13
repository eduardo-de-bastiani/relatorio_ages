# Auditoria independente de conteúdo — piloto AGES I / Sprint 0

Resultado desta rodada: **FAIL nos gates do harness; PASS na comparação independente do texto-fonte; PENDING no PDF real e no checkpoint humano**. Não autoriza outra Sprint.

Auditor: subagente Codex independente; não Antigravity. Skill aplicada: `.agent/skills/content-preservation-audit/SKILL.md`. Commit examinado: `9ad29b909c24dc55072263fd50c7b3d01cdfe658`, branch `migration/pilot-ages-i-sprint-0`, árvore com alterações. O JSON adjunto fixa hashes efetivos dos arquivos; não declara aprovação de um commit futuro.

## Prova independente

ODT congelado: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. Extração direta do ZIP/XML, sem reutilizar o extractor do harness nem o relato do conversor. Limites definidos por título de nível 3 `text-h-0016` até o próximo título real de nível ≤3 (`text-h-0017` / Sprint 1), incluindo descendentes da caixa ancorada.

Os 10 registros autorais (título, quatro parágrafos de corpo e cinco de reflexão) são iguais caractere a caractere aos bytes reais do LaTeX depois de decodificar exclusivamente `originaltab` e `originalspace`. A ordem física dos nove parágrafos é idêntica. Acentos, caixa, números, símbolos e pontuação permanecem íntegros. Não foi usada contagem de palavras nem normalização de espaços como prova. Os intervalos candidatos vieram do ledger; os valores esperados vieram exclusivamente do XML original. Todos os intervalos foram relidos do arquivo real.

Cobertura independente: 52 `text:p` = nove autorais, 41 vazios, um só tab (`text-p-0412`) e um contêiner externo da caixa (`text-p-0423`). Estes últimos 43 não representam 43 textos perdidos. O contêiner `draw-frame-0010` e `draw-text-box-0006` é preservado representativamente pelo ambiente `reflection`; seus cinco parágrafos têm mapeamento individual. Três listas, dois list-items e um list-header do fim do intervalo são wrappers cuja descendência autoral é exclusivamente o título da Sprint 1, fora do piloto; nenhuma lista visível da Sprint 0 foi omitida. Todos os IDs/contêineres/inline nodes desta faixa constam na evidência JSON.

Sete tabs existem no XML da faixa: seis no conteúdo autoral, representados explicitamente, e um no parágrafo vazio de layout. Quatro espaços de borda relevantes permanecem como macros explícitas: título, início de p0413, fim de p0424 e fim de p0426. O tab é implementado por `noindent` + `hspace*{1.251cm}`, distância padrão de tabulação ODF examinada; o espaço por `hspace*{fontdimen2 font}`. A equivalência gráfica ainda requer PDF.

As definições de estilos XML da unidade e seus spans foram examinadas: não há ênfase em negrito/itálico a conservar. T81 troca Times New Roman 13pt pela fonte do corpo conforme decisão aprovada; isso é apresentação, não reescrita. Não há imagens, figuras, tabelas, hyperlinks ou notas nesta unidade: esses controles são NOT_APPLICABLE por ausência comprovada na fonte. A âncora literal `__RefHeading___Toc4743_3118176633`, inicialmente ausente, foi restaurada no destino e revalidada por este auditor. O título usa `subsection*` com o número original; não soma uma segunda numeração. `addcontentsline` é metadado derivado, não duplicação visível do título no corpo.

O restante do arquivo, excluídos bytes mapeados e comentários, contém apenas estrutura explicitamente examinada: hypertarget, subsection*, label, addcontentsline, nove noindent e begin/end reflection. Nenhum texto autoral adicional foi encontrado. main.tex inclui somente o piloto e dois títulos de contexto presentes na fonte (sem migrar sua narrativa). util/style.tex/macros.tex foram lidos diretamente: não há inserção de narrativa oculta nesta invocação. Macros para figuras/placeholders não são invocadas. Não há conteúdo de outra edição nem da próxima Sprint.

## Achados e verificações

- **CA01 FAIL (high)** — docs/CONTENT_MANIFEST.json / $.migration_overlay. Evidência: validate exit 1: manifest-unexpected-field. Consequência: Gate de inventário/cobertura automatizado não executa comparação integral. Correção: Proprietário harmoniza extensão do manifesto com o validador, mantendo inventário original verificável. Retorno: Reexecutar validate --ledger migration/ledgers/ages-i-sprint-0.json --unit ages-i-sprint-0.

- **CA02 FAIL (medium)** — relatorio_AGES_eduardo/util/macros.tex:77. Evidência: audit-latex exit 1: missing_or_dynamic_asset #1 em memorialfigure não invocada.. Consequência: Gate estrutural ainda falha; não comprova omissão de imagem na unidade (zero imagens no XML). Correção: Mantenedor remove macro inutilizada ou responsável pelo harness implementa análise conservadora de invocações de macro. Retorno: Reexecutar audit-latex e verificar nenhum recurso dinâmico realmente invocado fica sem cobertura.

- **CA03 PENDING (high)** — build/document/main.pdf; text-p-0413/0424–0428; text-h-0016. Evidência: PDF real não disponível nesta rodada. Fonte contém seis originaltab e quatro originalspace; definições examinadas diretamente.. Consequência: Equivalência gráfica de tabs/espaços e saída efetiva dos glifos depende de PDF real. Correção: Compilar destino limpo e inspecionar PDF/render real. Retorno: Hash do PDF/log, pdftotext complementar e inspeção visual de todas as páginas.

## Comandos realmente executados

- `python3 scripts/migration.py verify-source` — exit 0; saída: `build/pilot/content-audit/gate-0.txt`.
- `python3 scripts/migration.py validate --ledger migration/ledgers/ages-i-sprint-0.json --unit ages-i-sprint-0` — exit 1; saída: `build/pilot/content-audit/gate-1.txt`.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex` — exit 1; saída: `build/pilot/content-audit/gate-2.txt`.
- `python3 build/pilot/content-audit/independent.py` — exit 0; evidência: `build/pilot/content-audit/independent-evidence.json`.
- Leituras com cat/Python ZIP XML, git status/diff/rev-parse/branch, sha256sum — executadas; nenhuma modificação do memorial/ledger/manifesto. Uma inspeção exploratória do manifesto retornou exit 1 por tratar lista como dict, corrigida na leitura seguinte; não foi gate nem evidência de conteúdo.

Arquivos escritos por este auditor: `docs/pilot/CONTENT_AUDIT.md`, `docs/pilot/CONTENT_AUDIT.json` e evidências auxiliares sob `build/pilot/content-audit/`. Limites: análise de fonte não substitui execução TeX nem revisão visual; G6/G7/G8/G9 permanecem pendentes nesta rodada.
