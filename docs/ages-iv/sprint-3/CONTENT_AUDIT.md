# Reauditoria independente de conteúdo — AGES IV, Sprint 3 e ajustes de apresentação

**Resultado:** PASS para o escopo textual/rastreável abaixo. **Aprovação humana do PDF:** PENDING.

## Artefatos examinados

- ODT imutável: `RELATORIO_ATUAL.odt`, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Unidade LaTeX Sprint 3: `relatorio_AGES_eduardo/conteudo/migracao/ages-iv-sprint-3.tex`, SHA-256 `0322e53585ef6acd3a57078bb8216e514b830ca267e58a4966d6fbb1112d6771`.
- Imagem anexada pelo usuário e cópia no repositório: SHA-256 `a507cd17d974f716b1133319a89d19907787cf8f058f4b1fc329deb8e799ee05`, PNG de 8191 × 1353 px.
- PDF integrado: `build/document/main.pdf`, SHA-256 `651ff8b5eb3555af4df0cf04b8feae69508e26db6f178ee132ce9a42e5e382b7`, 110 páginas A4.
- Evidências: autorizações `ages-iv-sprint-3-content-authorization.json` e `ages-iv-sprint-3-figure-and-display-authorization.json`; ledgers das sete unidades afetadas; `main.aux`, `.toc`, `.lof` e PDF.

## Achados independentes

O ODT contém para `ages-iv-sprint-3` apenas o título `text-h-0120` (“6.3.4 Sprint 3”) e estruturas vazias. Não contém a narrativa, reflexão, legenda/fonte nem o Gantt. Os 13 blocos da Sprint — nove parágrafos de relato, legenda, fonte e dois parágrafos introspectivos — foram comparados diretamente com a autorização/mensagem do usuário: todos aparecem uma vez, em ordem, sem divergência lexical não autorizada. A marcação de ênfase foi preservada, exceto a retirada autorizada do negrito em “14 tarefas do Épico 6”; as ênfases de `code freeze`, `To Do` e `In Progress` permanecem.

A imagem do PDF é a cópia byte a byte do anexo do usuário. A Figura 32 consta na p. 92 e na Lista de Ilustrações; a legenda e “Fonte: elaboração própria.” correspondem à autorização. Não foi copiado para a legenda o título que aparece dentro da imagem.

As entradas da Lista de Ilustrações mantêm a sequência Figura 32 (Gantt), Figura 33 (`text-p-0663`), Figura 34 (`text-p-0749`) e Figura 35 (`text-p-0759`). No Sumário, `text-h-0023`, `text-h-0074` e `text-h-0105` exibem, respectivamente, “6 CLIENTE AGES – HOORTECH”, “4 PROJETO AGES III – …” e “5 PROJETO AGES IV - RECORDA”. A comparação dos arquivos correspondentes confirma que os títulos no corpo continuam com a redação anterior; apenas `\addcontentsline` mudou.

Nenhum conteúdo de outras edições foi introduzido. O manifesto-fonte do ODT continua sem narrativa/imagem de Sprint 3, coerente com a proveniência suplementar direta do usuário.

## Matriz de conteúdo

| Verificação | Estado | Evidência |
|---|---|---|
| ODT e fonte original | PASS | Hash protegido; unidade contém título e wrappers vazios, sem corpo da Sprint ou Gantt. |
| 13 blocos diretos do usuário | PASS | 9 relatos + legenda + fonte + 2 reflexões conferidos em ordem; zero divergência lexical não autorizada. |
| Retirada de negrito | PASS | Só a marcação em “14 tarefas do Épico 6” foi removida; a redação visível não mudou. |
| PNG recebida | PASS | Hash e dimensões conferidos contra origem/anexo; nenhum redesenho ou dado extraído foi inserido como texto. |
| Figura 32 e Hoortech 33–35 | PASS | `.aux`, `.lof`, PDF e três legendas mostram sequência consistente. |
| Três rótulos do Sumário | PASS | Ajustes exatos aparecem no Sumário; os títulos LaTeX do corpo não mudaram. |
| Aprovação humana | PENDING | Deve revisar o PDF completo, em especial os detalhes pequenos do gráfico e a ordem integrada do documento. |

## Execução e limites

Auditor independente, leitura somente. Comparou o conteúdo autorizado e o ODT sem tomar o relato do conversor como evidência; inspecionou hashes, ledgers, `.aux/.toc/.lof`, texto e recursos de imagem do PDF; renderizou a p. 92. Ferramentas/comandos: `sha256sum`, scripts Python para comparar os 13 blocos e inspecionar `content.xml`/hashes, `rg`, `pdfinfo`, `pypdf`, `pdftoppm` e `pdfimages`. Não editou arquivos.

Esta reauditoria é específica às alterações descritas; não reabre auditorias integrais de cada capítulo. O Gantt é fornecido diretamente pelo usuário e não existe no ODT. A validação de conteúdo não aprova sua legibilidade gráfica em tamanho impresso; a auditoria visual registra esse ponto separadamente.
