# Integração de pré-textuais e trajetória — revisão pendente

Data: 17/10/2026

Branch: `migration/ages-iii`

Baseline local: `31c34e0c164b30a1cb81e289581e48f5279ee1b1`

Autorização: `migration/approvals/ages-iv-frontmatter-authorization.json`

Fonte ODT: SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef` (inalterada)

## Escopo integrado

A instrução suplementar autoriza somente as unidades `pretext`, `resumo` e `chapter-01-text-h-0001`. A autorização principal de Recorda, com suas 17 unidades, continua delimitada pelo registro próprio. Os arquivos LaTeX de conteúdo das edições e projetos já integrados não foram editados nesta ampliação; `main.tex` apenas passou a incluir os elementos novos e a preservar a numeração de capítulos já existente. A capa do ODT não contém um registro de imagem; por isso foi transcrita a composição textual, sem inventar ou buscar um elemento gráfico ausente. A inspeção do ODT foi estrutural, por XML/estilos; a renderização direta do original em LibreOffice não estava disponível na auditoria anterior, portanto a equivalência visual da capa ainda depende da revisão humana deste PDF.

| Ordem no PDF | Conteúdo | Página(s) física(s) | Origem/rastreabilidade |
|---|---|---:|---|
| 1 | Capa transcrita do ODT | 1 | IDs do ledger `pretext` |
| 2 | Dedicatória — título vazio | 2 | `text-p-0034`; instruções do modelo omitidas conforme autorização |
| 3 | Agradecimentos — título vazio | 3 | `text-p-0065`; texto genérico omitido conforme autorização |
| 4 | Epígrafe — título vazio | 4 | `text-p-0068`; instruções do modelo omitidas conforme autorização |
| 5 | Resumo — placeholder | 5 | `text-p-0095`, `text-p-0097`; instrução genérica substituída pelo marcador pedido |
| 6 | Lista de Ilustrações gerada | 6–7 | Captions e páginas recalculados do LaTeX; não se reutilizou o índice cacheado do ODT |
| 7 | Lista de Siglas | 8–9 | 39 entradas, `text-p-0143`–`text-p-0181`, na ordem do ODT |
| 8 | Sumário | 10–12 | Gerado do documento integrado |
| 9 | Apresentação da trajetória | 13–14 | Título, seis parágrafos autorais e dois bookmarks; instruções genéricas omitidas |
| 10 | Projetos já integrados | a partir da p. 15 | Seguem após a trajetória; conteúdo dos arquivos de projeto permaneceu inalterado |

Os elementos pré-textuais começam em páginas próprias, como observado no padrão de apresentação da Mariah, mantendo a ordem específica indicada pelo usuário. O título da trajetória aparece no sumário; o primeiro capítulo AGES continua numerado como capítulo 2.

## Integridade e ferramentas

Os três ledgers suplementares validaram com status `PASS`: 19/19 registros da unidade pré-textual, 45/45 registros de Resumo/listas e 9/9 registros da trajetória. A cobertura da trajetória inclui seis parágrafos de conteúdo e dois títulos-instrução deliberadamente omitidos. A lista de siglas contém as 39 entradas do ODT. As validações são lexicais/estruturais; elas não substituem aprovação visual humana.

`verify-source` e `inventory --check` passaram. `audit-latex --root relatorio_AGES_eduardo` passou com um aviso estático: `util/style.tex:173`, comando `\\memorial@citefirstword` não resolvido deterministamente pelo analisador. A suíte `python3 -m unittest discover -s tests -v` passou com 175 testes. `pytest` não está instalado no ambiente; a suíte do projeto foi executada pelo `unittest` disponível.

Compilação de revisão executada por `python3 scripts/migration.py build --profile document-review`, com Tectonic em modo somente cache. PDF: `build/document/main.pdf`, 94 páginas, SHA-256 `1ca275910d94e80c9b4a81f7b39f591e066f2b1e1178750f6bad8ecd3a99d00d`. O processo do compilador retornou 0, mas o harness marcou o resultado como `FAIL` por dois avisos `hyperref` “Suppressing empty link on input line 12”, durante a inclusão de `chapter-06-text-h-0109.tex` e `chapter-06-text-h-0110.tex`. Esses arquivos dos projetos não foram alterados nesta ampliação. `compiler.txt` agrega ainda oito avisos `Overfull \hbox` de passes de compilação e os avisos de perfil ICC v4.3 não suportado/não incorporado; `main.log` final não contém `Overfull` nem `Underfull`. O gate de documento oficial não foi executado; este PDF é de revisão.

A inspeção visual do orquestrador abrangeu as páginas 1–14 renderizadas por `pdftoppm`: capa, títulos vazios, Resumo, listas, sumário e trajetória. A sequência e a legibilidade desses elementos foram confirmadas. A lista de ilustrações ocupa as páginas 6–7, mas a página 7 contém somente a última entrada (Figura 34), com grande área vazia; isso está registrado como pendência de apresentação para o usuário decidir se quer ajustar o espaçamento dessa lista. Não se declara auditoria visual independente nem aprovação humana. A chamada ao comando automático `migration.py visual` foi interrompida sem gerar relatório, portanto não conta como gate PASS. A revisão visual do memorial completo continua pendente.

## Pendências para revisão

- A capa mantém literalmente os campos genéricos “AGES I,II, III OU IV” e “Ano”; não foram escolhidos edição ou ano.
- Dedicatória, Agradecimentos e Epígrafe contêm somente seus títulos; o Resumo mostra `[Resumo pendente de redação]`.
- Os dois avisos `hyperref` mantêm o gate automático do PDF em `FAIL`; investigar os links vazios sem modificar os projetos nesta ampliação.
- Falta a aprovação humana do PDF e da composição completa. Nenhuma edição AGES seguinte foi iniciada.
- A última entrada da Lista de Ilustrações fica sozinha na página 7; avaliar se a distribuição atual é aceitável ou se se autoriza um ajuste localizado de espaçamento.

## Arquivos e evidências

- PDF de revisão: `build/document/main.pdf`
- Relatório de compilação: `build/document/report.json`
- Log TeX: `build/document/main.log`
- Saída do compilador: `build/document/compiler.txt`
- Inclusões: `relatorio_AGES_eduardo/main.tex`
- Conteúdo novo: `relatorio_AGES_eduardo/conteudo/migracao/capa.tex`, `pretext.tex`, `resumo.tex`, `lista-de-siglas.tex`, `chapter-01-text-h-0001.tex`
- Ledgers: `migration/ledgers/pretext.json`, `resumo.json`, `chapter-01-text-h-0001.json`
- Autorização suplementar: `migration/approvals/ages-iv-frontmatter-authorization.json`
