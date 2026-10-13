# Auditoria independente de conteúdo — piloto AGES I / Easy Choose / Sprint 0

Resultado textual: **PASS em G0–G5 para a unidade; G6 PENDING por mudança de configuração detectada na verificação final; G7 visual, G8 normativo e G9 humano PENDING neste parecer**. Nenhuma próxima Sprint está autorizada. A primeira rodada FAIL está preservada integralmente ao fim deste arquivo e no histórico JSON; CA01/CA02 têm resolução atestada nesta rodada.

Auditor: subagente Codex independente, não Antigravity. Skill: `.agent/skills/content-preservation-audit/SKILL.md`. Commit contextual examinado: `5826ca435bafb1e4d052f9c8bcd310d336825741`, branch `migration/pilot-ages-i-sprint-0`, limpa antes de escrever estes dois relatórios. Os hashes completos efetivos estão no JSON adjunto. Nenhum memorial, ledger, manifesto ou script compartilhado foi alterado por este auditor.

## Prova independente da preservação

Extraí diretamente `content.xml` e `styles.xml` do ZIP `RELATORIO_ATUAL.odt`, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. Não usei relatos do conversor/extrator como prova. O intervalo real vai de `text-h-0016` (`2.3.1 Sprint 0 `, nível 3) até, excluído, `text-h-0017` (`2.3.2 Sprint 1`). IDs foram reconstituídos pela ordem XML. Ledger e manifesto serviram como índices, não como fonte de valores esperados.

Os **10 registros autorais** (título, quatro parágrafos de corpo e cinco da reflexão) foram comparados caractere a caractere contra o LaTeX real. Extraí os nove parágrafos físicos e o argumento do título independentemente dos spans do ledger, conferindo depois ambos os caminhos. Todos são iguais, na ordem original, sem mudar acentos, pontuação, caixa, símbolos ou palavras. Não sobrou texto visível após remover exclusivamente os payloads provados e os comandos estruturais conhecidos. O XML dos spans e seus estilos, incluindo ancestrais Standard/List Paragraph e estilo padrão, não contém ênfase em negrito/itálico a transferir. A reflexão troca Times New Roman 13pt pela família/tamanho do corpo, decisão de apresentação aprovada.

A faixa contém 52 `text:p`: nove autorais, 41 vazios, um parágrafo contendo somente tab (`text-p-0412`) e um contêiner externo da caixa (`text-p-0423`). A caixa `draw-text-box-0006`, em `draw-frame-0010`, conserva seus cinco parágrafos `text-p-0424`–`0428` na ordem; o ambiente reflection é divisível. Sete tabs existem no XML, seis autorais representados por `originaltab{}` e um apenas de layout. Quatro espaços de borda são explícitos por `originalspace{}`. Li as definições reais: tab = `noindent` + `hspace*{1.251cm}`, distância de tabulação comprovada em styles.xml; espaço = `hspace*{fontdimen2 font}`. Não colapsei whitespace na prova textual. A geometria efetiva desses espaços é questão de G7.

Os três wrappers de lista, dois list-items e um list-header da fronteira possuem como única descendência textual real `text-h-0017 / 2.3.2 Sprint 1`, conferida diretamente no XML completo. Não são itens visíveis omitidos da Sprint 0. Nenhuma figura/imagem, tabela, URL/hyperlink, nota, citação ou lista autoral existe nesta unidade: controles respectivos são NOT_APPLICABLE por ausência comprovada, não uma declaração sobre o memorial integral. A âncora literal `__RefHeading___Toc4743_3118176633` permanece como hypertarget visualmente vazio.

Li integralmente main.tex, util/style.tex e util/macros.tex. O grafo contém somente main + dois util + a unidade por input. main usa os títulos de contexto originais e counters chapter=2/section=2.3, sem migrar narrativa de outras unidades; macros de figura/placeholder não são invocadas. A unidade não contém quebra obrigatória antes do título nem conteúdo de outro projeto/Sprint. A menção autoral à futura Sprint 1 no quarto parágrafo foi conservada porque já existe na Sprint 0.

## PDF e numeração efetivos

Li o PDF real `build/document/main.pdf`, SHA-256 `a57e643bd7878e2c2f36c6be20b902aa33a08381694102f2c7b453ea5f33fc93`, por extração complementar pdftotext, e os arquivos main.aux/main.log/compiler.txt/report.json reais. Há duas páginas; título único `2.3.1 Sprint 0`, quatro parágrafos de corpo e cinco da reflexão, com p0426 continuado na segunda página. Aspas curvas, acentos e pontuação estão presentes. Ligaturas ﬁ/ﬂ e hifenização de linhas aparecem na extração; não usei esse fluxo como igualdade única da fonte.

O `.aux` registra `newlabel{sprint:ages-i-0}` com `M@TitleReference {2.3.1}`; o título fonte usa subsection* e refstepcounter, logo não há prefixo automático duplo. O registro toc da subseção deriva literalmente do mesmo título e macro de espaço, sem segunda numberline. Sumário visual não é impresso neste PDF de revisão; foi conferido o registro derivado compilado. Log real: zero Warning, Overfull, Underfull, Missing character ou referências indefinidas. G6 PASS refere-se aos artefatos reais produzidos pelo build limpo, report exit 0 no commit auditado; este auditor não recompilou.

O `validate` continua emitindo `counter_aux_review_required` e `pdf_evidence_pending`. O primeiro foi resolvido pela leitura direta do aux. O segundo explicita a fronteira lexical/visual: este parecer não aprova renders completos. G7 deve ser decidido pelo auditor visual separado, contra o mesmo hash. G8 permanece fora do mandato textual e depende de prova normativa; G9 exige aprovação explícita do usuário para a entrega.

## CA06 — atualização durante verificação final

PENDING (alta): style.tex foi alterado durante auditoria para paginação de 10pt, SHA corrente `b99e8231e36abfe69ae2e295f4940c67ab8c617b01db4855614b3ea8db0a82a0`; os artefatos anteriormente examinados fixam SHA `e75349de...`. G6 abaixo descreve a rodada anterior e exige novo build + revalidação para fechar a árvore corrente. Nenhuma divergência autoral detectada.

## Achados e retorno

- **CA01 PASS (high)** — `docs/CONTENT_MANIFEST.json / $.migration_overlay; scripts/migration.py`. Evidência: inventory --check e validate reexecutados independentemente, exit 0; 10/10 registros, 100% cobertura, differences=[]; mesmo hash de manifesto da primeira rodada. Consequência: Bloqueio anterior do validador resolvido sem remover inventário original. Correção/ação: Contrato do harness aceita overlay de migração; nenhuma correção textual pelo auditor. Verificação: build/pilot/content-final/gate-1.txt e gate-2.txt; hashes do manifesto/harness anexos.

- **CA02 PASS (medium)** — `relatorio_AGES_eduardo/util/macros.tex / memorialfigure; scripts/migration.py`. Evidência: audit-latex reexecutado exit 0, quatro arquivos, nenhuma imagem/citação/referência, um label; leitura integral confirma macro figure não invocada. Consequência: Falso bloqueio do recurso formal #1 resolvido; nenhuma imagem original omitida no piloto. Correção/ação: Análise do harness distingue definição de macro de sua invocação; fonte da unidade e main examinados independentemente. Verificação: build/pilot/content-final/gate-3.txt e grafo input de quatro arquivos.

- **CA03 PASS (high)** — `build/document/main.pdf/main.aux/main.log; text-h-0016 e p0413/0424–0428`. Evidência: PDF real de duas páginas lido por pdftotext; contém título único, quatro parágrafos de corpo e cinco de reflexão, incluindo continuação de p0426. .aux confirma referência 2.3.1 e toc derivado; log real zero linhas Warning/Overfull/Underfull/Missing character/undefined. Consequência: Pendência de existência/saída textual real resolvida; inspeção visual de espaços/borda segue gate separado. Correção/ação: Build limpo identificado no report.json, commit 5826ca4 e PDF SHA anexos; auditor não recompilou nem alterou memorial. Verificação: PDF/texto/aux/log reais examinados; G7 permanece PENDING neste parecer e depende de VISUAL_AUDIT.

- **CA04 PENDING (medium)** — `G7 / docs/pilot/VISUAL_AUDIT.*`. Evidência: Validador lexical emite pdf_evidence_pending como lembrete de inspeção renderizada; este papel lê fonte e extração PDF, não emite inspeção visual completa. Consequência: Não converter aprovação lexical em aprovação de layout, tabs/espaços ou bordas. Correção/ação: Auditor visual verifica renders completos do mesmo SHA de PDF. Verificação: Relatório visual independente vinculado ao PDF a57e643bd7878e2c2f36c6be20b902aa33a08381694102f2c7b453ea5f33fc93.

- **CA05 PENDING (critical)** — `G9 / checkpoint de entrega do piloto`. Evidência: Autorização permite executar piloto; nenhuma evidência de aprovação humana deste resultado. Consequência: Próxima Sprint/edição não autorizada. Correção/ação: Apresentar piloto e aguardar decisão do usuário. Verificação: Mensagem humana identificável vinculada ao commit e hashes finais.

## Comandos realmente executados e arquivos alterados

- `python3 build/pilot/content-final/independent.py` — exit 0; evidência `build/pilot/content-final/independent-evidence.json`.
- `python3 scripts/migration.py verify-source` — exit 0; evidência `build/pilot/content-final/gate-0.txt`.
- `python3 scripts/migration.py inventory --check` — exit 0; evidência `build/pilot/content-final/gate-1.txt`.
- `python3 scripts/migration.py validate --ledger migration/ledgers/ages-i-sprint-0.json --unit ages-i-sprint-0` — exit 0; evidência `build/pilot/content-final/gate-2.txt`.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex` — exit 0; evidência `build/pilot/content-final/gate-3.txt`.
- `pdftotext -layout build/document/main.pdf build/pilot/content-final/pdf.txt` — exit 0; evidência `build/pilot/content-final/gate-4.txt`.
- `pdfinfo build/document/main.pdf` — exit 0; evidência `build/pilot/content-final/gate-5.txt`.

Leituras adicionais executadas: cat, Python ZIP/XML/estilos, git rev-parse/branch/status, inspeção de auxiliares e cálculo SHA-256. Uma primeira leitura tentou `docs/agents/AUDITOR_CONTEUDO.md` (inexistente, cat exit 1); o papel correto `docs/agents/content-auditor.md` foi localizado e lido em seguida. Isto não é falha da preservação.

Arquivos rastreados alterados: somente `docs/pilot/CONTENT_AUDIT.md` e `.json`. Scripts/evidências locais criados somente em `build/pilot/content-final/`. Nenhum commit foi realizado por este auditor. Resultado vinculado ao commit contextual e hashes reais; mudanças posteriores exigem igualdade dos arquivos examinados ou reauditoria. Aprovação para executar piloto não equivale à aprovação da entrega; parar antes de qualquer próxima Sprint.

---

## Histórico integral da primeira auditoria (antes das correções)

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
