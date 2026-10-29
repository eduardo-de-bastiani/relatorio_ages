# Revisão do piloto — AGES I / Easy Choose / Sprint 0

Somente `ages-i-sprint-0` foi convertido. O PDF contém as seções de contexto originais e essa Sprint; não representa o memorial completo. A execução foi autorizada pela missão do usuário, mas **a aprovação da entrega e qualquer próxima Sprint permanecem pendentes**.

## Entregáveis

- LaTeX: `relatorio_AGES_eduardo/main.tex`, `util/style.tex`, `util/macros.tex` e `conteudo/migracao/ages-i-sprint-0.tex`.
- PDF: `build/document/main.pdf`, duas páginas. SHA-256: `695548198b34270eed8f6da21ebb4af3bb19e1762fd1dba77c04eb23cb611784`.
- Compilação: `build/document/report.json`, `main.log`, `compiler.txt`, `main.aux`, `main.toc` e `main.out`. Build final no commit `f7095af7dce388fa4a366168e748e926be459880`, código 0, sem erros/avisos.
- Manifesto: `docs/CONTENT_MANIFEST.json`, inventário original imutável e overlay de rastreabilidade da única unidade.
- Ledger: `migration/ledgers/ages-i-sprint-0.json`, dez intervalos UTF-8, hash real do LaTeX, contrato de macros e correspondência da âncora original.
- Divergências textuais: `build/validation/ages-i-sprint-0/report.json`; auditoria independente em `CONTENT_AUDIT.md` e `.json`.
- Auditoria visual independente: `VISUAL_AUDIT.md` e `.json`; imagens e medições em `build/pilot/visual-final/` e `build/visual/`.
- Resultados de comandos: `build/pilot/final-validation-results.json`, `latex-structure.json`, `scope-by-owner.json` e `document-build-final.json`.
- Testes sintéticos separados do memorial: `util/test_macros.py` e `util/test_continuity.py`; PDFs/logs/resultados em `build/pilot-macro-test/` e `build/pilot-continuity-test/`.

Artefatos em `build/` são ignorados pelo Git e regeneráveis. A única fonte documental continua sendo o ODT intacto. Nenhum pacote, ferramenta ou skill externa foi instalado; as compilações usam o cache congelado, sem download.

## Conteúdo e rastreabilidade

A extração direta do ODF e a auditoria independente identificaram título e nove parágrafos: quatro do corpo e cinco da reflexão. **10/10 registros correspondem exatamente**, inclusive acentos, pontuação, seis tabs autorais e quatro espaços de borda. Ordem, âncora `__RefHeading___Toc4743_3118176633`, numeração `2.3.1`, registro de sumário e ausência de texto inventado foram conferidos.

Os 43 blocos não autorais incluem parágrafos vazios, um parágrafo somente com TAB e o contêiner da caixa. Seus elementos continuam inventariados e classificados, sem criar espaços verticais artificiais. Seis contêineres de lista no limite final pertencem ao título seguinte; não constituem tarefas desta Sprint e não trouxeram a Sprint 1 para o piloto.

Não existem figuras, tabelas, hyperlinks, notas, citações ou listas autorais nessa unidade. Esses critérios são NOT_APPLICABLE, não elementos omitidos. Nenhum placeholder foi inventado. As macros reutilizáveis para figuras/placeholders estão preparadas, mas não foram exercitadas por uma figura real deste piloto.

## Critérios e limites

| Gate | Resultado do piloto | Evidência / limite |
|---|---|---|
| G0–G1 | PASS | Hash do ODT e 112 arquivos protegidos; reextração integral sem diferenças; inventário de origem preservado |
| G2–G4 | PASS, escopo da Sprint | Dez textos e estrutura integral classificados; zero divergência; mídia/links/notas ausentes na origem |
| G5 | PASS | Grafo de inclusão válido; âncora preservada; label e sumário conferidos no `.aux`/`.toc` |
| G6 | PASS | Compilação offline limpa; hashes de todas as fontes e artefatos conferidos contra o build |
| G7 | PASS técnico | Todas as duas páginas finais reabertas; fonte/posição, bordas, fluxo e legibilidade conferidos por auditor separado |
| G8 | PARCIAL / PENDING | A4, margens laterais, fonte corporal, espaçamento e paginação medidos; não certifica documento integral nem vigência de todas as normas |
| G9 | PENDING | Usuário ainda precisa revisar e aprovar o resultado; próxima Sprint não autorizada |

A suíte integrada executada passou com **65 testes**, incluindo casos negativos de perda/alteração, fonte não normalizada, contrato de macros alterado, texto adicional, ordem, TOC inventado, âncora e escopo de unidade. Os testes de reflexão longa e continuidade compilam documentos sintéticos separados, sem migrar outra Sprint. No teste de continuidade, o título real acompanha texto anterior na página 1; a última reflexão e o título sintético seguinte ocupam a página 2.

A revisão detectou e corrigiu uma diferença entre fontes de paginação nas duas páginas. A versão final usa 10 pt TeX e posição medida de aproximadamente 2 cm do topo/direita, sem alterar o corpo. A escolha de 10 pt implementa tamanho menor e uniforme; esse número específico é uma escolha de apresentação, não uma exigência literal da norma. Fonte e origem: [NBR 14724:2024, versão corrigida 2025, §§5.1 e 5.3](https://vigilanciasanitaria.prefeitura.rio/wp-content/uploads/sites/84/2025/10/ABNT-NBR-14724-2025-informacao-e-documentacao-trabalho-academico.pdf).

O histórico das falhas iniciais dos gates, da âncora corrigida e da necessidade de recompilar após ajuste de estilo permanece nos pareceres. A configuração que gerou o PDF final está vinculada por hashes, e o conteúdo não sofreu revisão editorial.

Após os pareceres, somente os metadados de revisão do ledger e o overlay do manifesto recebem os vínculos finais ao PDF e às auditorias. Os intervalos, hashes de LaTeX, dados de origem, âncoras e contrato das macros permanecem idênticos aos auditados; o relatório `build/pilot/ledger-final/report.json` registra a comparação antes/depois. Os pareceres conservam os hashes das versões efetivamente examinadas, sem reescrever retrospectivamente sua evidência.

## Pendências não resolvidas

1. Aprovação humana do PDF e do piloto; autorização de próxima Sprint é outra decisão.
2. Conformidade integral ABNT e estrutura acadêmica completa dependem do memorial inteiro, das normas ainda pendentes e dos pré/pós-textuais. Não foram simulados no PDF parcial.
3. Figuras, fontes de imagens, referências bibliográficas e dados ausentes das demais unidades continuam nas pendências globais; não bloqueiam este piloto sem esses elementos.
4. Preservação de numeração manual com contador sincronizado e tabs iniciais está comprovada para este caso. Outros títulos, tabs internos, fórmulas, floats ou reflexões aninhadas precisam de procedimentos específicos; o ambiente atual de reflexão suporta parágrafos comuns.
5. O limite inferior da mancha não é ocupado por texto nesta unidade curta; a margem inferior nominal de 2 cm está na configuração, e a ocupação das páginas respeita esse limite. Isso não prova a geometria de todas as páginas futuras.

O comparativo Mariah foi apenas lido como referência de qualidade. Não houve transferência de conteúdo pessoal, projetos ou referências. A principal e o checkpoint do harness permanecem preservados.
