# Auditoria visual pós-padronização — AGES I

> **Histórico substituído:** esta inspeção corresponde ao PDF de 19 páginas, SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`. O PDF atual tem 18 páginas e hash diferente; consulte [CURRENT_REVIEW.md](CURRENT_REVIEW.md).

## Escopo e resultado

Reauditoria independente do PDF candidato `build/document/main.pdf`, com inspeção visual de todas as 19 páginas renderizadas, extração de texto para conferir hierarquia e paginação, e inspeção das anotações PDF para conferir destinos de links internos e externos. O arquivo auditado tem SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`, formato A4 e 19 páginas.

**Resultado: PASS, com pendência humana explícita.** A página 2 está sem número visível; o sumário tem hierarquia completa; títulos de Sprint continuam o fluxo do texto; as figuras e a Figura 5 estão centralizadas; não há páginas vazias, texto cortado ou títulos de Sprint isolados. Na página 7, os cinco itens de tecnologia e seus textos/documentações permanecem em ordem, sem marcadores, conforme solicitado; a transição do restante do texto para a página 8 não introduz quebra artificial. O símbolo `°` aparece legível na página 17. A chamada aparece como `Figura 5` no render e na extração textual, e o número está vinculado à Figura 5 da página 18. Não encontrei falha visual confirmada nesta versão. As fontes das cinco imagens continuam **PENDING**, conforme decisão do usuário de identificá-las manualmente. Os placeholders de arquitetura e banco de dados estão marcados como provisórios.

Não modifiquei o memorial nem estilos globais. As imagens de inspeção estão em `/tmp/ages-i-postformat/final-3543f7/page-01.png` até `page-19.png`; são renderizações temporárias, fora do repositório.

## Procedimentos e evidências

| Verificação | Resultado | Evidência/saída |
|---|---|---|
| SHA-256 e metadados | PASS | `sha256sum build/document/main.pdf` → `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`; `pdfinfo` → 19 páginas, A4. Código de saída 0. |
| Render de todas as páginas | PASS | `pdftoppm -png -r 90 build/document/main.pdf /tmp/ages-i-postformat/final-3543f7/page`; código de saída 0; 19 PNGs gerados. |
| Comparação com a renderização anterior | PASS | Comparação SHA-256 dos PNGs: páginas 7 e 8 mudaram após a remoção dos marcadores; páginas 1–6 e 9–19 permaneceram idênticas. Código de saída 0. |
| Texto e paginação | PASS | `pdftotext -layout`; código de saída 0. Níveis e páginas do sumário correspondem às páginas renderizadas. |
| Destinos dos hiperlinks e referências cruzadas | PASS | Inspeção das anotações via `pypdf` e XML de `pdftohtml`; ambos os comandos terminaram com código 0. Os três repositórios apontam para URLs `tools.ages.pucrs.br/easy-choose/...`; os cinco links documentais levam aos destinos listados; o link da Figura 5 chega à página 18. |
| Apresentação da chamada à Figura 5 | PASS | `pdftotext` retorna `O registro do projeto selecionado está na Figura 5.`; XML mostra `Figura <a href="current.html#18">5.</a>`. Espaço visível e número clicável. |
| Lista de tecnologias sem marcadores | PASS | Render da p. 7 mostra rótulos em parágrafos simples. Extração confirma TypeScript, React, Node.js, Prisma e PostgreSQL uma vez cada, em ordem; cinco descrições/documentações aparecem e `•` ocorre 0 vezes. Código de saída 0. |
| Revisão visual | PASS | Inspeção direta dos 19 PNGs. Não há recorte, sobreposição, página vazia, título isolado ou defeito de centralização confirmado. |

Os links dos repositórios aparecem em frases corridas e mantêm texto clicável. O link de Easy Choose Store quebra entre linhas, mas ambas as caixas de anotação apontam ao mesmo URL completo. Os links não exibem sublinhado no PDF; a inspeção confirmou que são clicáveis.

As Figuras 1–5 usam o rótulo português “Figura”, com título acima e linha “Fonte” abaixo. As cinco imagens estão visualmente centralizadas na área de texto; a Figura 5, na página 18, também está centralizada. **Classificação da composição da Figura 5: PASS; o espaço superior não exige correção.** A evidência geométrica do XML (`pdftohtml -xml -hidden`, código 0) mostra página 18 com 1.262 px de altura, legenda em y=400, imagem em y=429 com 434 px de altura e fonte em y=892. Há cerca de 400 px antes da legenda e 355 px depois da linha de fonte. Assim, embora a figura ocupe uma página própria e deixe uma área branca perceptível acima, o espaço é consequência aceitável do float final em página dedicada e está equilibrado com o espaço inferior. O efeito é consumir uma página para a Figura 5, sem criar uma página quase vazia: imagem, título e fonte ocupam cerca de 40% da altura. A chamada da página 17 aparece agora como “Figura 5” e o número está vinculado à imagem da página 18.

As caixas de reflexão preservam a borda e a fonte do corpo. A reflexão da Sprint 2 atravessa as páginas 12–13 com continuação legível e borda mantida. Nenhum título de Sprint começa em página nova por regra de formatação: Sprint 0 começa após a seção 2.3 na página 8; Sprint 1 começa após a reflexão da Sprint 0 na página 9; Sprint 2, Sprint 3 e Sprint 4 começam nas páginas 11, 13 e 15, respectivamente, depois do conteúdo anterior.

## Resultado por página

| Página | Status | Evidência visual e observações |
|---:|---|---|
| 1 | PASS | Sumário legível, níveis 2, 2.1, 2.2.1–2.2.5 e 2.3.1–2.3.5 visíveis, páginas alinhadas à direita e links internos ativos. |
| 2 | PASS | Lista de ilustrações em português; sem número de página visível após o último ajuste. Cinco entradas e números de página legíveis. |
| 3 | PASS / PENDING | Introdução e Figura 1 bem alinhadas; chamada interna resolve; imagem centralizada. Fonte da imagem permanece pendente de identificação manual. |
| 4 | PASS | Subseções e os três links dos repositórios em prosa; destinos conferidos. Placeholder de banco de dados delimitado e marcado como provisório. |
| 5 | PASS | Placeholder de arquitetura claramente provisório; seção de protótipos e Figura 2 legíveis e alinhadas. Fonte pendente de identificação manual. |
| 6 | PASS / PENDING | Figuras 3 e 4 legíveis, centralizadas e com fontes posicionadas abaixo. Identificação das fontes pendente. |
| 7 | PASS | Lista sem marcadores conforme solicitado. Extração confirma os cinco rótulos — TypeScript, React, Node.js, Prisma e PostgreSQL — em ordem, com descrições e linhas documentais; visualmente não há item ou texto cortado. |
| 8 | PASS | Parágrafo final de tecnologias continua no topo; transição para seção 2.3 e Sprint 0 na mesma página, sem quebra artificial. |
| 9 | PASS | Caixa de reflexão da Sprint 0 inteira, borda contínua; título Sprint 1 vem após o texto e já tem parágrafo na mesma página. |
| 10 | PASS | Continuação de Sprint 1, texto alinhado e sem títulos isolados. |
| 11 | PASS | Caixa de reflexão da Sprint 1 termina antes do título Sprint 2; Sprint 2 começa com texto na mesma página. |
| 12 | PASS | Sprint 2 prossegue; reflexão inicia em caixa legível perto do final da página, com continuação para a página seguinte. |
| 13 | PASS | Continuação/fechamento da caixa de reflexão sem perda visual; Sprint 3 começa depois da caixa e tem texto abaixo. |
| 14 | PASS | Continuação de Sprint 3 e caixa reflexiva completa, sem recortes ou sobreposição. |
| 15 | PASS | Sprint 4 e sua caixa de reflexão permanecem legíveis e dentro das margens. |
| 16 | PASS | Fechamento da reflexão anterior e início da conclusão; sem título órfão ou quebra artificial. |
| 17 | PASS | Símbolo `°` em “2° e 4° JK” está visível e legível. A chamada à imagem aparece como “Figura 5”; extração textual e XML confirmam o espaço e o link do número para a Figura 5 na p. 18. |
| 18 | PASS / PENDING | Figura 5 horizontalmente centralizada, título acima e fonte abaixo; a origem da imagem segue pendente de identificação manual. Float final ocupa página própria. XML mede legenda y=400, imagem y=429–863 e fonte y=892 em página de 1.262 px: aproximadamente 400 px de espaço acima e 355 px abaixo; o bloco está verticalmente equilibrado. É uma página de figura justificável, não página quase vazia. |
| 19 | PASS | Referências e URLs legíveis e clicáveis; espaçamento homogêneo; nenhum texto ultrapassa a margem. A página é parcial, mas contém a lista de referências, sem ser página vazia. |

## Pendências e limites

- **PENDING — fontes das Figuras 1–5:** requer identificação manual do usuário. Este parecer confirma somente a apresentação da linha de fonte; não valida autoria, origem ou atribuição.
- **NOT_APPLICABLE — conteúdo de outras edições:** o PDF auditado contém apenas AGES I; esta auditoria não avalia as demais edições.
- Esta é uma auditoria de apresentação do PDF candidato. Ela não certifica integralmente conformidade ABNT nem substitui revisão normativa/editorial do memorial.

## Comandos e códigos de saída

- `pdfinfo build/document/main.pdf` — 0; 19 páginas A4.
- `pdftoppm -png -r 90 build/document/main.pdf /tmp/ages-i-postformat/final-3543f7/page` — 0; 19 renderizações.
- `pdftotext -layout build/document/main.pdf /tmp/ages-i-postformat/final-3543f7/main.txt` — 0; extração confirma `Figura 5` na p. 17.
- Leitura de anotações/URIs por script Python com `pypdf` — 0.
- `pdftohtml -xml -hidden build/document/main.pdf /tmp/ages-i-postformat/final-3543f7/current.xml` — 0; confirma que o número da chamada está vinculado ao destino interno da Figura 5.
- Comparação dos SHA-256 dos PNGs da versão anterior com o candidato atual — 0; somente a p. 17 mudou.
