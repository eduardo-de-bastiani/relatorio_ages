# Auditoria independente de conteúdo — AGES II

**Resultado geral: FAIL.** A comparação textual, hierárquica, de links, imagens, listas e reflexões passou nos escopos verificados, mas a conversão do snapshot contém **31 omissões confirmadas de ênfase**: 30 ocorrências inline e um parágrafo sublinhado. O resultado não deve ser usado como aprovação da unidade até correção e reauditoria.

## Base, escopo e método

- ODT lido diretamente: `RELATORIO_ATUAL.odt`; SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- SHA-256 de `content.xml`: `b8fe0f8a7d35303374f5a25b0bcf17630aa4978489d63bc61be2f1c258130c28`.
- Snapshot-alvo: commit `1fdeefeda92c574e42b3ffd539db24346f8a00b7`, branch isolada `migration/ages-ii-content-audit`; os hashes das 15 unidades estão em `CONTENT_AUDIT.json`.
- Delimitação independente em `content.xml`: filhos de corpo `[642, 879)`, do título `4 - PROJETO AGES II – INDÚSTRIA DIGITAL` até antes de `5 - PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID`.
- Escopo autorizado: 15 IDs, conforme lista fechada em `harness.json` e manifesto. Nenhuma unidade externa foi examinada como conteúdo de destino.
- Extração: Python 3.12.8, biblioteca padrão `zipfile` + `xml.etree.ElementTree`; comparação ODF/XML/LaTeX por IDs e XPath. Normalização textual: NFC e colapso de espaços; acentos, pontuação, símbolos e ordem lexical preservados. Hashes de mídia calculados sobre os bytes no ZIP e no destino.
- O alvo foi lido apenas como comparação. Relatórios do conversor não foram usados como evidência; as ocorrências de ênfase foram confirmadas em `content.xml`, `styles.xml`, cadeia efetiva de estilos e bloco LaTeX associado.

## Inventário estrutural

| Elemento no escopo ODF | Contagem |
|---|---:|
| Filhos do corpo | 237 |
| `text:p` | 260 |
| `text:h` | 35 |
| `text:list` / `text:list-item` | 68 / 64 |
| `draw:frame` / `draw:text-box` / `draw:image` | 19 / 12 / 7 |
| `text:a` | 13 |
| Tabelas / notas / objetos / fórmulas / gráficos | 0 / 0 / 0 / 0 / 0 |

A rastreabilidade no manifesto cobre 182 de 182 registros considerados, sem registro sem unidade/destino. Frames não-imagem foram inventariados; objetos, tabelas, notas, fórmulas e gráficos não apareceram dentro do intervalo de escopo.

## Resultado dos gates de conteúdo

| Verificação | Estado | Evidência resumida |
|---|---|---|
| Hash do ODT e resolução de XPaths | PASS | Hash esperado confirmado; zero XPath sem resolução. |
| Presença e ordem do texto | PASS | Nenhuma divergência textual não autorizada. Duas frases de repositório foram adaptadas conforme instrução explícita da usuária. |
| Hierarquia e títulos | PASS | Cabeçalhos e sequência correspondem às 15 unidades autorizadas. |
| Hiperlinks | PASS | 13 ocorrências, URLs completas e multiplicidade idênticas; nenhum URL ausente ou extra. |
| Imagens | PASS | 7 de 7 na ordem e com SHA-256 binário idêntico. |
| Listas autorais | PASS | 9 grupos comparados: Sprint 3 tem 2 itens; Sprint 4 tem 21 itens nos 8 grupos restantes. |
| Reflexões | PASS | 5 de 5 caixas; textos iguais, IDs `draw-text-box-0021, draw-text-box-0022, draw-text-box-0023, draw-text-box-0024, draw-text-box-0026`. |
| Elementos não-textuais detectáveis por inventário | PASS | Nenhuma tabela, nota, fórmula, gráfico ou objeto incorporado no escopo XML. |
| Ênfases de texto | FAIL | 30 spans com estilo efetivo ausente no LaTeX. |
| Sublinhado de estilo de parágrafo | FAIL | `text-p-0839` “Documentação Docker” tem sublinhado ODF efetivo, sem equivalente LaTeX. |
| Fonte das figuras | PENDING | A origem/autoria continua para identificação manual; não inferida. |
| Metadados de novas referências tecnológicas | PENDING | Curadoria bibliográfica separada; não avaliada aqui. |
| Render visual do ODT | PENDING | Conversão para PDF falhou; detalhes abaixo. |

## Links preservados

As 13 URLs, em ordem de ocorrência no escopo, são:

- `https://developers.facebook.com/docs/graph-api/guides/explorer/`
- `https://docs.python.org/pt-br/3/`
- `https://docs.sqlalchemy.org/en/20/`
- `https://fastapi.tiangolo.com/`
- `https://tools.ages.pucrs.br/industria-digital/industria-digital-backend`
- `https://tools.ages.pucrs.br/industria-digital/industria-digital-frontend`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Banco%20de%20dados`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Mockups`
- `https://v17.angular.io/docs`
- `https://www.postgresql.org/docs/`
- `https://www.typescriptlang.org/pt/docs/handbook/typescript-in-5-minutes.html`

As adaptações textuais autorizadas são: (1) link de frontend, âncora-fonte `Repositório Indústria Digital Frontend` → âncora-alvo `Indústria Digital Frontend`, com a frase autorizada “Mais informações podem ser encontradas no repositório Indústria Digital Frontend.”; (2) a mesma estrutura para `Indústria Digital Backend`. Os endereços completos foram preservados, inclusive o `%20` no link de banco de dados.

## Figuras preservadas

| ID ODF / asset | Unidade | Membro do ODT | Destino | SHA-256 dos bytes | Legenda no alvo |
|---|---|---|---|---|---|
| `draw-image-0009` / `asset-0018` | `chapter-04-text-h-0040` | `Pictures/1000000000000FC000000BD0A1701859.jpg` | `imagens/original/asset-0018.jpg` | `e72fefda1ff42e6892d4baaf060c368f88d9e7b5839c75c4e7d2f2c44a2949ff` | Figura 9 – Foto do Time - AGES II |
| `draw-image-0010` / `asset-0008` | `chapter-04-text-h-0044` | `Pictures/1000000000000508000000A57BE2D817.png` | `imagens/original/asset-0008.png` | `17d98d72ab9a0d49427a6b318a7b57fadbbd2443f9e1f40fb3db285e9b51e35e` | Figura 10 – Arquitetura da Aplicação - AGES II |
| `draw-image-0011` / `asset-0020` | `chapter-04-text-h-0045` | `Pictures/10000001000003F50000023C0EC79B82.png` | `imagens/original/asset-0020.png` | `07edbb01f49f214603297d772bf61774b67fbdfa7c3d2dcb90300718cc109e30` | Figura 11 – Landing Page - AGES II |
| `draw-image-0012` / `asset-0022` | `chapter-04-text-h-0045` | `Pictures/10000001000003F50000023C87C0702C.png` | `imagens/original/asset-0022.png` | `c3dcc3f66ab7db5f22e6b5e33c52d10881ba6bcc1e6448124dac731fcaa41962` | Figura 12 – Tela de Dashboard - AGES II |
| `draw-image-0013` / `asset-0021` | `chapter-04-text-h-0045` | `Pictures/10000001000003F50000023C6CDB69B2.png` | `imagens/original/asset-0021.png` | `51285b445604b4f618d56aff677dfabc86e51afc51b328c13514eabd62228fd6` | Figura 13 – Tela do Mapa - AGES II |
| `draw-image-0014` / `asset-0023` | `chapter-04-text-h-0045` | `Pictures/10000001000003F50000023CA09C645F.png` | `imagens/original/asset-0023.png` | `83c21f098a170ec931eeda44cd0d32cf79928605502892ae2a99816cb018b0d5` | Figura 14 – Tela das Empresas - AGES II |
| `draw-image-0015` / `asset-0025` | `ages-ii-sprint-4` | `Pictures/10000001000004D0000002BCC1C29F70.png` | `imagens/original/asset-0025.png` | `4c17f14fb04490efc3d6ba20df9e5dbe0cce9e200c247253b698b22de2fa3f42` | Figura 15 – Fluxo de Processamento de Presença Digital - AGES II |

Todas as figuras usam no alvo `Fonte: pendente de identificação`; isso continua pendência humana, sem atribuição inventada. O placeholder aprovado para o diagrama ausente de banco de dados é provisório e não foi contado como imagem original concluída.

## Omissões de ênfase confirmadas

A cadeia de estilos e as propriedades efetivas por span estão detalhadas no JSON. Os spans ODF não têm ID próprio no manifesto; `audit_occurrence_id` é um identificador gerado por esta auditoria e cada ocorrência mantém o ID estável do parágrafo e seu XPath. O comando esperado abaixo registra o tipo de comando, não uma proposta de reescrita do texto.

| Ocorrência | Unidade | Parágrafo | XPath do span | Texto fonte | Propriedades efetivas | Comando esperado | Arquivo-alvo |
|---|---|---|---|---|---|---|---|
| `ages-ii-emph-0001` | `chapter-04-text-h-0042` | `text-p-0774` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[611]/text:span[3]` | landing, | `{"fo:font-size": "12pt", "style:text-underline-style": "none", "fo:color": "#000000", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0042.tex` |
| `ages-ii-emph-0002` | `chapter-04-text-h-0042` | `text-p-0774` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[611]/text:span[4]` | dashboard, | `{"fo:font-size": "12pt", "style:text-underline-style": "none", "fo:color": "#000000", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0042.tex` |
| `ages-ii-emph-0003` | `chapter-04-text-h-0046` | `text-p-0813` | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[40]/text:list-item[1]/text:p[2]/text:span[2]` | landing page | `{"fo:font-size": "12pt", "fo:color": "#000000", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0046.tex` |
| `ages-ii-emph-0004` | `chapter-04-text-h-0046` | `text-p-0813` | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[40]/text:list-item[1]/text:p[2]/text:span[3]` | dashboards | `{"fo:font-size": "12pt", "fo:color": "#000000", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0046.tex` |
| `ages-ii-emph-0005` | `chapter-04-text-h-0046` | `text-p-0830` | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[44]/text:list-item[1]/text:p[2]/text:span[1]` | Object-Relational Mapping | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0046.tex` |
| `ages-ii-emph-0006` | `chapter-04-text-h-0046` | `text-p-0841` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[656]/text:span[1]` | dashboards | `{"fo:font-size": "12pt", "fo:color": "#000000", "style:text-underline-style": "none", "fo:font-weight": "normal", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0046.tex` |
| `ages-ii-emph-0007` | `ages-ii-sprint-0` | `text-p-0844` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[659]/text:span[5]` | web scraping | `{"fo:font-size": "12pt", "fo:color": "#000000", "fo:font-style": "italic", "fo:font-weight": "normal"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0008` | `ages-ii-sprint-0` | `text-p-0844` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[659]/text:span[20]` | web scraping | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0009` | `ages-ii-sprint-0` | `text-p-0848` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[663]/text:span[10]` | database | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0010` | `ages-ii-sprint-0` | `text-p-0848` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[663]/text:span[12]` | sample | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0011` | `ages-ii-sprint-0` | `text-p-0851` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[665]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[3]` | CRUD | `{"fo:font-size": "13pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0012` | `ages-ii-sprint-0` | `text-p-0851` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[665]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[5]` | Create, Read, Update, Delete | `{"fo:font-size": "13pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-0.tex` |
| `ages-ii-emph-0013` | `ages-ii-sprint-1` | `text-p-0870` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[683]/text:span[4]/text:span[1]` | joins | `{"fo:font-size": "12pt", "fo:font-style": "italic", "fo:font-weight": "normal"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-1.tex` |
| `ages-ii-emph-0014` | `ages-ii-sprint-1` | `text-p-0876` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[688]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[3]` | tasks | `{"fo:font-size": "13pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-1.tex` |
| `ages-ii-emph-0015` | `ages-ii-sprint-2` | `text-p-0906` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[714]/text:span[6]` | squad | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0016` | `ages-ii-sprint-2` | `text-p-0906` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[714]/text:span[7]` | endpoints | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0017` | `ages-ii-sprint-2` | `text-p-0907` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[715]/text:span[1]` | sample | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0018` | `ages-ii-sprint-2` | `text-p-0907` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[715]/text:span[2]/text:span[1]` | d | `{"fo:font-size": "12pt"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0019` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[1]` | hot | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0020` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[3]` | fix | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0021` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[4]` | branch | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0022` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[5]` | develop | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0023` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[7]` | hot | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0024` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[8]` | fix | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0025` | `ages-ii-sprint-2` | `text-p-0911` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[9]` | develop | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0026` | `ages-ii-sprint-2` | `text-p-0913` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[721]/text:span[1]` | endpoints | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-2.tex` |
| `ages-ii-emph-0027` | `ages-ii-sprint-3` | `text-p-0936` | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[52]/text:list-item[1]/text:p[1]/text:span[1]/text:span[1]` | Indexação das colunas mais consultadas | `{"fo:font-size": "12pt", "fo:font-style": "normal", "style:text-underline-style": "solid", "fo:font-weight": "normal"}` | `\underline{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-3.tex` |
| `ages-ii-emph-0028` | `ages-ii-sprint-3` | `text-p-0937` | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[52]/text:list-item[2]/text:p[1]/text:span[1]/text:span[1]` | Reorganização das tabelas | `{"fo:font-size": "12pt", "style:text-underline-style": "solid", "fo:font-weight": "normal"}` | `\underline{…}` | `relatorio_AGES_eduardo/conteudo/migracao/ages-ii-sprint-3.tex` |
| `ages-ii-emph-0029` | `chapter-04-text-h-0073` | `text-p-1020` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[796]/text:span[1]` | POC | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0073.tex` |
| `ages-ii-emph-0030` | `chapter-04-text-h-0073` | `text-p-1020` | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[796]/text:span[2]` | (Proof of Concept) | `{"fo:font-size": "12pt", "fo:font-style": "italic"}` | `\textit{…}` | `relatorio_AGES_eduardo/conteudo/migracao/chapter-04-text-h-0073.tex` |

Ocorrências por unidade:

| Unidade | Omissões |
|---|---:|
| `ages-ii-sprint-0` | 6 |
| `ages-ii-sprint-1` | 2 |
| `ages-ii-sprint-2` | 12 |
| `ages-ii-sprint-3` | 2 |
| `chapter-04-text-h-0042` | 2 |
| `chapter-04-text-h-0046` | 5 |
| `chapter-04-text-h-0073` | 2 |

O 31º caso é nível de parágrafo e está fora da tabela de spans: `text-p-0839` em `/office:document-content[1]/office:body[1]/office:text[1]/text:list[46]/text:list-item[1]/text:p[3]`. Estilo `P249` com cadeia `Standard → P249`; propriedade efetiva `{"fo:font-size": "12pt", "fo:color": "#2a6099", "style:text-underline-style": "solid"}`. O trecho é texto simples, não hiperlink. A linha de destino observada: `{'line': 45, 'text': 'Documentação Docker'}`. A regra de apresentação aprovada para retirar estilo visual de âncoras não se aplica.

### Exclusões verificadas para evitar falsos positivos

- `text-h-0068`: P270 → Heading_20_2 → Standard contém declarações efetivas de fonte normal e peso normal em P270, que cancelam negrito/itálico herdados. Portanto, não há ênfase a transportar e o alvo simples está correto.
- Estilo exclusivamente decorrente de hyperlink/âncora: não contado como falha, por decisão de apresentação registrada em `docs/STYLE_GUIDE.md:18` (âncoras pretas, regulares e sem itálico). URLs e âncoras foram verificadas em gate próprio.
- Não se contou mera segmentação de `text:span` sem propriedade tipográfica efetiva.

## Pendências e limitações

1. **Falha confirmada:** corrigir as 31 ocorrências de ênfase e reauditar, preservando exatamente texto e pontuação.
2. **Pendente:** identificação manual da fonte/autoria das sete figuras.
3. **Pendente:** curador verificar metadados e fontes das seis chaves tecnológicas `ages-ii-angular`, `ages-ii-typescript`, `ages-ii-python`, `ages-ii-fastapi`, `ages-ii-sqlalchemy`, `ages-ii-postgresql`.
4. **Pendente de evidência visual do original:** comando `libreoffice -env:UserInstallation=file:///tmp/agesii-lo-profile2 --headless --convert-to pdf --outdir /tmp/agesii-odt-render ./RELATORIO_ATUAL.odt` terminou com código 1, aviso dconf de filesystem somente leitura, sem PDF de saída. Não é possível concluir daí que haja divergência; é limitação da ferramenta/ambiente.
5. A auditoria não substitui auditoria visual nem validação de compilação. Esses gates têm escopo próprio.

## Reprodução e ferramentas

| Comando/ação | Resultado |
|---|---|
| `python3 /tmp/audit_ages_ii_independent.py` | exit 0; extração direta independente ODF→inventário e comparação textual/elementar. |
| `python3 /tmp/refine_emphasis_tex.py` | exit 0; dados intermediários de spans e bloco TeX; relatório final filtrou apenas FAIL confirmado após revisão de estilos. |
| Leitura ZIP/XML adicional de `content.xml` e `styles.xml` | concluiu; resolução de cascata aplicada a estilos de parágrafo e caractere. |
| `python3 --version` | Python 3.12.8. |
| `libreoffice --version` | LibreOffice 26.2.6.3 (Build 3). |
| Conversão visual ODT→PDF | exit 1; nenhum PDF; PENDING, não tratado como divergência comprovada. |

Os scripts de auditoria são temporários em `/tmp` e não fazem parte deste commit. A auditoria é reprodutível a partir do snapshot e dos comandos, mas qualquer alteração posterior aos arquivos-alvo invalida a comparação correspondente. A versão detalhada e os hashes completos estão em `CONTENT_AUDIT.json`; diferenças textuais aprovadas estão em `TEXT_DIVERGENCES.json`.
