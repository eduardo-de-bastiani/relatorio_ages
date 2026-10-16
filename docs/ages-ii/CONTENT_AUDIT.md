# Reauditoria independente de conteúdo — AGES II (pós-reparo)

**Integridade de conteúdo: PASS no snapshot identificado abaixo.** Os 30 spans inline confirmados no ODF agora estão cobertos por formatação LaTeX sem divergência textual, e o sublinhado de parágrafo P249 também foi preservado. O escopo de conteúdo passou; a prontidão global continua pendente da revisão visual separada, da identificação manual das fontes das figuras e da curadoria bibliográfica.

## Snapshot e método

- ODT lido diretamente: `RELATORIO_ATUAL.odt`; SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. O hash esperado foi confirmado.
- `content.xml` SHA-256: `b8fe0f8a7d35303374f5a25b0bcf17630aa4978489d63bc61be2f1c258130c28`.
- Branch `migration/ages-ii`, HEAD `f3df8d2043cbb59b02aed1b76bc86d2c4bf6ae03`; worktree estava modificado. Os SHA-256 atuais das 15 unidades autorizadas estão em `CONTENT_AUDIT.json`; eles definem precisamente o estado auditado.
- Escopo ODF: filhos de corpo `[642, 879)`, capítulo `4 - PROJETO AGES II – INDÚSTRIA DIGITAL` até antes de `5 - PROJETOS AGES III – SISTEMA DE CONTROLE INTELIGENTE DE ESTACIONAMENTO COM RFID`. Foram conferidos os 15 IDs listados em `harness.json`.
- Extração direta por Python 3.12.8, `zipfile` e `xml.etree.ElementTree`; estilo efetivo resolvido pela cascata de `content.xml` e `styles.xml`.
- Para ênfase, cada XPath foi re-resolvido no ODT; o parágrafo inteiro da origem foi normalizado e exigido como substring única e idêntica no texto LaTeX visível do arquivo-alvo. Em seguida, os offsets de cada caractere original foram aplicados à pilha de macros TeX. Isso confirma trechos fragmentados, inclusive o `d` final de `sampled`, sem confundi-lo com outra letra `d` do parágrafo.
- Os locais dos 31 casos anteriores serviram apenas como endereços de busca. O estilo efetivo e o texto foram verificados novamente no ODT atual; nenhum relatório de conversor foi usado como evidência. Nenhum arquivo LaTeX foi alterado por esta auditoria.

## Resultado dos checks

| Verificação | Estado | Resultado |
|---|---|---|
| ODT imutável e escopo | PASS | Hash confirmado; 15/15 unidades; XPaths resolvidos. |
| Texto, hierarquia e sequência | PASS | Sem diferenças não autorizadas; títulos e ordem conferem. |
| Links | PASS | 13/13 URLs completas idênticas, na mesma ordem e multiplicidade. |
| Imagens | PASS | 7/7 na mesma ordem, com SHA-256 idêntico. |
| Listas | PASS | 9 grupos e 23 itens: Sprint 3, 2 itens; Sprint 4, 21 itens. |
| Reflexões | PASS | 5/5 textos idênticos. |
| 30 spans de ênfase e P249 | PASS | 31/31 cobertos por comandos LaTeX nos offsets de origem. |
| Placeholder de diagrama ausente | PASS | Um placeholder provisório de banco de dados, explicitamente marcado como ausente no ODT. |
| Conteúdo de outra edição | PASS | Intervalo termina no cabeçalho seguinte; arquivos do destino limitados às 15 unidades AGES II. |
| Fontes das figuras / metadados bibliográficos | PENDING | Permanecem nos respectivos fluxos humano e de curadoria. |
| Renderização visual do ODT / layout | PENDING / fora deste escopo | Auditoria visual separada; exportação visual anterior não produziu PDF. |

O inventário de origem contém 237 filhos de corpo, 260 parágrafos, 35 títulos, 68 listas, 64 itens de lista, 19 frames, 12 caixas de texto, 7 imagens e 13 hiperlinks. Não há tabelas, notas, objetos incorporados, fórmulas ou gráficos no intervalo auditado. O manifesto mapeia 182/182 registros considerados.

## Reauditoria das ênfases

A extração efetiva do ODF encontrou **30 spans inline: 28 itálicos e 2 sublinhados**, além de **1 ocorrência de parágrafo sublinhado** (`P249`). Portanto, o total de ocorrências confirmadas é 31. Os 30 spans são cobertos por 26 grupos `\textit` e 2 grupos `\underline`; P249 acrescenta mais um `\underline`. Os detalhes de cada span, incluindo a cadeia de estilos ODF, propriedades efetivas, XPath, offset e ID do grupo de macros no TeX, estão em `CONTENT_AUDIT.json`.

| ID | Unidade | Texto de origem | Ênfase efetiva ODF | XPath do span | Grupo LaTeX que cobre os caracteres |
|---|---|---|---|---|---|
| `ages-ii-emph-0001` | `chapter-04-text-h-0042` | `landing,` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[611]/text:span[3]` | `\textit` (grupo 0) |
| `ages-ii-emph-0002` | `chapter-04-text-h-0042` | `dashboard,` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[611]/text:span[4]` | `\textit` (grupo 1) |
| `ages-ii-emph-0003` | `chapter-04-text-h-0046` | `landing page` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[40]/text:list-item[1]/text:p[2]/text:span[2]` | `\textit` (grupo 0) |
| `ages-ii-emph-0004` | `chapter-04-text-h-0046` | `dashboards` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[40]/text:list-item[1]/text:p[2]/text:span[3]` | `\textit` (grupo 1) |
| `ages-ii-emph-0005` | `chapter-04-text-h-0046` | `Object-Relational Mapping` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[44]/text:list-item[1]/text:p[2]/text:span[1]` | `\textit` (grupo 2) |
| `ages-ii-emph-0006` | `chapter-04-text-h-0046` | `dashboards` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[656]/text:span[1]` | `\textit` (grupo 4) |
| `ages-ii-emph-0007` | `ages-ii-sprint-0` | `web scraping` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[659]/text:span[5]` | `\textit` (grupo 0) |
| `ages-ii-emph-0008` | `ages-ii-sprint-0` | `web scraping` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[659]/text:span[20]` | `\textit` (grupo 1) |
| `ages-ii-emph-0009` | `ages-ii-sprint-0` | `database` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[663]/text:span[10]` | `\textit` (grupo 2) |
| `ages-ii-emph-0010` | `ages-ii-sprint-0` | `sample` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[663]/text:span[12]` | `\textit` (grupo 3) |
| `ages-ii-emph-0011` | `ages-ii-sprint-0` | `CRUD` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[665]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[3]` | `\textit` (grupo 4) |
| `ages-ii-emph-0012` | `ages-ii-sprint-0` | `Create, Read, Update, Delete` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[665]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[5]` | `\textit` (grupo 5) |
| `ages-ii-emph-0013` | `ages-ii-sprint-1` | `joins` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[683]/text:span[4]/text:span[1]` | `\textit` (grupo 0) |
| `ages-ii-emph-0014` | `ages-ii-sprint-1` | `tasks` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[688]/draw:frame[1]/draw:text-box[1]/text:p[1]/text:span[3]` | `\textit` (grupo 1) |
| `ages-ii-emph-0015` | `ages-ii-sprint-2` | `squad` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[714]/text:span[6]` | `\textit` (grupo 0) |
| `ages-ii-emph-0016` | `ages-ii-sprint-2` | `endpoints` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[714]/text:span[7]` | `\textit` (grupo 1) |
| `ages-ii-emph-0017` | `ages-ii-sprint-2` | `sample` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[715]/text:span[1]` | `\textit` (grupo 2) |
| `ages-ii-emph-0018` | `ages-ii-sprint-2` | `d` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[715]/text:span[2]/text:span[1]` | `\textit` (grupo 2) |
| `ages-ii-emph-0019` | `ages-ii-sprint-2` | `hot` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[1]` | `\textit` (grupo 3) |
| `ages-ii-emph-0020` | `ages-ii-sprint-2` | `fix` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[3]` | `\textit` (grupo 4) |
| `ages-ii-emph-0021` | `ages-ii-sprint-2` | `branch` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[4]` | `\textit` (grupo 5) |
| `ages-ii-emph-0022` | `ages-ii-sprint-2` | `develop` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[5]` | `\textit` (grupo 6) |
| `ages-ii-emph-0023` | `ages-ii-sprint-2` | `hot` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[7]` | `\textit` (grupo 7) |
| `ages-ii-emph-0024` | `ages-ii-sprint-2` | `fix` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[8]` | `\textit` (grupo 8) |
| `ages-ii-emph-0025` | `ages-ii-sprint-2` | `develop` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[719]/text:span[9]` | `\textit` (grupo 9) |
| `ages-ii-emph-0026` | `ages-ii-sprint-2` | `endpoints` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[721]/text:span[1]` | `\textit` (grupo 10) |
| `ages-ii-emph-0027` | `ages-ii-sprint-3` | `Indexação das colunas mais consultadas` | underline | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[52]/text:list-item[1]/text:p[1]/text:span[1]/text:span[1]` | `\underline` (grupo 0) |
| `ages-ii-emph-0028` | `ages-ii-sprint-3` | `Reorganização das tabelas` | underline | `/office:document-content[1]/office:body[1]/office:text[1]/text:list[52]/text:list-item[2]/text:p[1]/text:span[1]/text:span[1]` | `\underline` (grupo 1) |
| `ages-ii-emph-0029` | `chapter-04-text-h-0073` | `POC` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[796]/text:span[1]` | `\textit` (grupo 0) |
| `ages-ii-emph-0030` | `chapter-04-text-h-0073` | `(Proof of Concept)` | textit | `/office:document-content[1]/office:body[1]/office:text[1]/text:p[796]/text:span[2]` | `\textit` (grupo 0) |

Ocorrências por unidade:

| Unidade | Cobertura |
|---|---:|
| `ages-ii-sprint-0` | 6 spans |
| `ages-ii-sprint-1` | 2 spans |
| `ages-ii-sprint-2` | 12 spans |
| `ages-ii-sprint-3` | 2 spans |
| `chapter-04-text-h-0042` | 2 spans |
| `chapter-04-text-h-0046` | 4 spans |
| `chapter-04-text-h-0073` | 2 spans |

Dois agrupamentos contíguos foram confirmados por alinhamento caractere a caractere:

- `text-p-0907`: os spans `sample` e `d` terminam formando o original `sampled`; ambos caem dentro do mesmo grupo `\textit{sampled}` em `ages-ii-sprint-2.tex` (linha 12), com o texto completo do parágrafo igual ao ODT.
- `text-p-1020`: os spans `POC` e `(Proof of Concept)` são cobertos pelo mesmo grupo `\textit{POC (Proof of Concept)}` em `chapter-04-text-h-0073.tex` (linha 12), novamente com o parágrafo completo igual.

O parágrafo `text-p-0839` tem cadeia de estilo `Standard → P249`, com `text-underline-style=solid` efetivo. O destino contém `\underline{Documentação Docker}` em `chapter-04-text-h-0046.tex` (linha 45), cobrindo os 19 caracteres não-espaço. Ele é texto simples, não âncora de link. O antigo falso positivo `text-h-0068` também foi rechecado: `P270 → Heading_20_2 → Standard`, com P270 definindo fonte e peso `normal`; não exige ênfase no alvo.

## Links, figuras, reflexões e listas

As URLs conferidas, na ordem do ODT e do LaTeX, são:

- `https://tools.ages.pucrs.br/industria-digital/industria-digital-frontend`
- `https://tools.ages.pucrs.br/industria-digital/industria-digital-backend`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Banco%20de%20dados`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura`
- `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Mockups`
- `https://v17.angular.io/docs`
- `https://www.typescriptlang.org/pt/docs/handbook/typescript-in-5-minutes.html`
- `https://docs.python.org/pt-br/3/`
- `https://fastapi.tiangolo.com/`
- `https://developers.facebook.com/docs/graph-api/guides/explorer/`
- `https://docs.sqlalchemy.org/en/20/`
- `https://www.postgresql.org/docs/`

As duas alterações de âncora/frase no repositório Frontend e Backend são as adaptações explicitamente autorizadas; os endereços permanecem intactos. O comparador textual não encontrou diferenças não autorizadas.

| Ocorrência de imagem | Unidade | Destino | SHA-256 do conteúdo binário | Legenda no alvo |
|---|---|---|---|---|
| `draw-image-0009` | `chapter-04-text-h-0040` | `asset-0018` → `imagens/original/asset-0018.jpg` | `e72fefda1ff42e6892d4baaf060c368f88d9e7b5839c75c4e7d2f2c44a2949ff` | Figura 9 – Foto do Time - AGES II |
| `draw-image-0010` | `chapter-04-text-h-0044` | `asset-0008` → `imagens/original/asset-0008.png` | `17d98d72ab9a0d49427a6b318a7b57fadbbd2443f9e1f40fb3db285e9b51e35e` | Figura 10 – Arquitetura da Aplicação - AGES II |
| `draw-image-0011` | `chapter-04-text-h-0045` | `asset-0020` → `imagens/original/asset-0020.png` | `07edbb01f49f214603297d772bf61774b67fbdfa7c3d2dcb90300718cc109e30` | Figura 11 – Landing Page - AGES II |
| `draw-image-0012` | `chapter-04-text-h-0045` | `asset-0022` → `imagens/original/asset-0022.png` | `c3dcc3f66ab7db5f22e6b5e33c52d10881ba6bcc1e6448124dac731fcaa41962` | Figura 12 – Tela de Dashboard - AGES II |
| `draw-image-0013` | `chapter-04-text-h-0045` | `asset-0021` → `imagens/original/asset-0021.png` | `51285b445604b4f618d56aff677dfabc86e51afc51b328c13514eabd62228fd6` | Figura 13 – Tela do Mapa - AGES II |
| `draw-image-0014` | `chapter-04-text-h-0045` | `asset-0023` → `imagens/original/asset-0023.png` | `83c21f098a170ec931eeda44cd0d32cf79928605502892ae2a99816cb018b0d5` | Figura 14 – Tela das Empresas - AGES II |
| `draw-image-0015` | `ages-ii-sprint-4` | `asset-0025` → `imagens/original/asset-0025.png` | `4c17f14fb04490efc3d6ba20df9e5dbe0cce9e200c247253b698b22de2fa3f42` | Figura 15 – Fluxo de Processamento de Presença Digital - AGES II |

As reflexões identificadas no ODT (`draw-text-box-0021, draw-text-box-0022, draw-text-box-0023, draw-text-box-0024, draw-text-box-0026`) estão presentes como 5 ambientes e seu texto é idêntico. Os 9 grupos de listas preservam seus 23 itens; não houve omissão ou reordenação observada.

O único placeholder é `\diagramplaceholder{ages-ii-database}{Diagrama do banco de dados ausente no ODT; preenchimento posterior.}` em `chapter-04-text-h-0043.tex`. Ele se identifica como provisório e não apresenta arquitetura ou dados inventados.

## Pendências e limites

- **PASS de conteúdo para este snapshot**, não aprovação da edição inteira. A aprovação humana continua necessária conforme `AGENTS.md`.
- **PENDING:** a identificação manual da fonte/autoria das sete figuras.
- **PENDING:** proveniência e metadados das seis referências de tecnologia a cargo da curadoria.
- **PENDING separado:** a renderização visual do ODT não foi repetida neste ciclo; o PDF de origem não foi produzido na tentativa anterior. Esta tarefa não inspecionou layout nem substitui o auditor visual.
- Nenhuma compilação foi feita nesta auditoria de conteúdo.

## Comandos e resultados

| Comando | Resultado |
|---|---|
| `sha256sum RELATORIO_ATUAL.odt` | exit 0; hash esperado `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. |
| `python3 /tmp/audit_ages_ii_postrepair.py` | exit 0; checks independentes das 15 unidades. |
| `python3 /tmp/agesii_reaudit_emphasis_v3.py` | exit 0; 30 spans inline PASS e P249 PASS, com resolução direta de estilos/offsets. |
| `python3 -m py_compile /tmp/audit_ages_ii_postrepair.py /tmp/agesii_reaudit_emphasis_v3.py` | exit 0. |
| Validação dos JSONs e hashes das 15 unidades | PASS; registrados em `CONTENT_AUDIT.json`. |

Os scripts e relatórios intermediários ficaram em `/tmp`; somente os três relatórios finais foram atualizados no projeto. O snapshot mudou depois da versão inicial; os arquivos `_INITIAL` foram preservados sem alteração.
