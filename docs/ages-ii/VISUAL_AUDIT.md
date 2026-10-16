# Auditoria visual independente — AGES II

**Estado: PENDING, sem FAIL visual atual confirmado.** Reauditei de forma independente todas as 40 páginas do PDF com SHA-256 `c1ca761350f2ab8def3e458323f92c9717a9ca90e3eae2f362a80fc6e414648d`. As páginas 19–40 são o escopo AGES II; páginas 1–18 foram verificadas apenas como contexto. As correções de posição das Figuras 9 e 11–14, prefixo da Figura 15 e estilos das páginas 21, 34 e 37 estão visíveis e conferem com a cascata do ODF. Permanecem pendências de revisão das citações e do texto Docker na p.24, legibilidade da Figura 10, identificação manual das fontes e eventual aceitação humana da página esparsa do sumário. A p.2 resulta da profundidade 2 aprovada no `STYLE_GUIDE.md`; não é classificada como defeito normativo nem há proposta de alterar esse estilo.

PDF: [`build/document/main.pdf`](/home/eduardo/facul/relatorio_ages/build/document/main.pdf)  
Renderizações: `build/visual/c1ca761350f2ab8d/page-01.png`–`page-40.png`; o manifesto `report.json` lista as 40 páginas e seus hashes. Commit do manifesto: `339bba68563f739e622246cb3167c8a2532176bf`; o worktree de origem estava sujo. O hash SHA-256 do PDF identifica o artefato exato desta auditoria.

## Método e cobertura

Abri cada uma das 40 renderizações de página a 120 dpi. As páginas 27–40 foram renderizadas do próprio PDF com `pdftoppm -f 27 -l 40 -png -r 120 ...`; conferi que as 40 imagens correspondem aos hashes do manifesto da renderização. Também conferi dimensões, fontes, imagens e texto extraído. Não usei o relatório do conversor nem a inspeção de um PDF anterior como prova do resultado atual. Não editei PDF, ODT, LaTeX ou estilos.

Comandos/inspeções concluídos com código 0: `sha256sum`, `pdfinfo` (40 páginas A4), `pdffonts -f 19 -l 40` (NimbusSanL regular/negrito/itálico incorporadas), `pdfimages -list` (sete figuras AGES II e PPI), `pdftotext` nas transições e páginas 20–24, 35–39 e 36 (incluindo os sete marcadores da lista), `pypdf` para anotações URI/GoTo, `pdftohtml -xml -hidden` na p.24, e inspeção read-only de `content.xml`/`styles.xml` com `zipfile`/`ElementTree`.

## Achados e decisões pendentes

| ID | Página(s) | Estado / gravidade | Evidência atual e consequência | Ação proposta |
|---|---:|---|---|---|
| VAII-001 | 19–20 | **PASS**; correção anterior, gravidade média | Figura 9 aparece após a introdução e antes de 4.2/4.2.1; não interrompe repositório. Legenda acima, imagem centralizada e fonte abaixo. | Manter posicionamento contextual. |
| VAII-002 | 21–24 | **PASS**; correção anterior, gravidade média | Figuras 11–14 estão no bloco após “Fotos dos protótipos:” e antes de 4.2.5. Títulos e fontes estão visíveis. | Nenhuma correção adicional. |
| VAII-003 | 3, 34 | **PASS**; correção anterior, gravidade baixa | Prefixo “Figura 15” está em negrito tanto na lista como na legenda. | Nenhuma correção adicional. |
| VAII-004 | 24, 40 | **PENDING**; média | Permanecem chamadas como “(ANGULAR. . . , 2024)”, “(TYPESCRIPT. . . , 2024)”, “(DOCUMENTA-ÇÃO. . . , 2024)”, “(FASTAPI. . . , 2024)” e “(POSTGRESQL:. . . , 2024)”. Destinos internos chegam à p.40, mas o rótulo está fragmentado. | Curadoria/mantenedor ajustam apresentação com metadados verificados, sem inferir autoria ou mudar redação; revalidar pp.24/40. |
| VAII-005 | 24 | **PENDING**; baixa | “Documentação Docker” segue sublinhado sem annotation URI; o ODT não fornece âncora/URL para essa ocorrência. | Rever o sublinhado sem criar URL; conferir ausência de destino após nova compilação. |
| VAII-006 | 21 | **PENDING**; decisão humana | Figura 10 mede cerca de 14,7 × 1,9 cm; raster 1288×165 px (~222 ppi). Rótulos são pequenos à escala de página, embora visíveis quando ampliados. | Usuário confirma legibilidade em impressão; se insuficiente, fornecer imagem mais legível ou decidir outra disposição sem reconstruir conteúdo. |
| VAII-007 | 20–23, 34 | **PENDING**; decisão humana | Sete imagens mantêm “Fonte: pendente de identificação” em linha visível abaixo da figura. | Usuário identifica manualmente autoria/fonte de cada imagem; não inferir atribuições. |
| VAII-008 | 21 | **PASS**; correção anterior, gravidade baixa | ODF p0785 tem T226 interno em peso normal que prevalece sobre Strong; no PDF atual Angular, FastAPI e PostgreSQL aparecem regulares, como no estilo efetivo da origem. | Nenhuma correção adicional. |
| VAII-009 | 34 | **PASS**; correção anterior, gravidade baixa | Os títulos de etapa permanecem sublinhados em linhas contínuas, sem as lacunas anteriores. O prefixo Figura 15 continua em negrito. | Nenhuma correção adicional. |
| VAII-010 | 2 | **PENDING**; baixa, apenas para eventual aceitação humana | A página tem somente “4.4 Conclusão” e “Referências” no alto e muito espaço vazio. O `STYLE_GUIDE.md` aprova profundidade 2 para o sumário nas próximas edições; Mariah usa profundidade 1. Não foi identificada violação normativa. | Não alterar nem compactar o estilo aprovado. Pendente apenas se o usuário quiser confirmar a aceitação desta página esparsa; aceita, encerrar sem mudança. |
| VAII-011 | 37 | **PASS**; correção anterior, gravidade baixa | “memory leak” e o espaço entre as palavras estão abrangidos pelo span itálico no PDF atual; a p.37 mantém o fluxo de texto e a caixa reflexiva continua na p.38. | Nenhuma correção adicional. |

### Rastreabilidade dos estilos revistos

Na p.21, `content.xml` registra Angular, FastAPI e PostgreSQL dentro de T226, que define peso normal; o PDF atual apresenta os três em regular. Na p.31, T73 define sublinhado com peso normal; os itens continuam sublinhados como no ODT. Na p.34, T286 sublinha cada título de etapa como um trecho contínuo; a renderização atual não tem lacunas entre palavras. “Links Relevantes” aparece regular e os dois-pontos em negrito conforme o T28 interno normal e o Strong separado. Na p.37, o T43 italic cobre “memory leak”, inclusive o espaço, e o PDF atual apresenta o span completo em itálico. Essas conclusões foram verificadas contra o PDF atual e o ODF, sem usar relato do conversor como prova visual.

## Registro página a página

| Pág. | Estado | Evidência atual |
|---:|---|---|
| 1 | PASS | Sumário apresenta AGES I e AGES II com a hierarquia do capítulo 4 e páginas 19–40 corretamente apontadas. |
| 2 | PENDING | Somente “4.4 Conclusão” e “Referências” aparecem na faixa superior; quase toda a página fica em branco. É consequência da profundidade 2 aprovada no `STYLE_GUIDE.md` (subtítulos/Sprints), enquanto Mariah usa profundidade 1. Observação para eventual aceitação humana; não é defeito normativo e não se propõe compactação. |
| 3 | PASS | Lista de ilustrações contém Figuras 9–15 e páginas 20, 21, 22, 22, 23, 23 e 34; prefixos estão uniformemente em negrito. |
| 4 | PASS | AGES I; página de abertura, hierarquia e imagem enquadradas, sem defeito contextual observado. |
| 5 | PASS | AGES I; prosa e placeholders de banco/arquitetura enquadrados, sem corte visível. |
| 6 | PASS | AGES I; placeholder de arquitetura, hierarquia e Figura 2 legíveis. |
| 7 | PASS | AGES I; Figuras 3 e 4 e respectivas fontes provisórias aparecem na página. |
| 8 | PASS | AGES I; seção de tecnologias em fluxo, sem corte aparente. |
| 9 | PASS | AGES I; Sprint 0 e início da reflexão na página. |
| 10 | PASS | AGES I; reflexão continua com borda e Sprint 1 começa após o fechamento. |
| 11 | PASS | AGES I; relato de Sprint 1 e caixa de reflexão continuam sem corte. |
| 12 | PASS | AGES I; caixa de Sprint 1 fecha e Sprint 2 começa na página. |
| 13 | PASS | AGES I; reflexão de Sprint 2 dentro da borda. |
| 14 | PASS | AGES I; texto da Sprint 3 em fluxo. |
| 15 | PASS | AGES I; reflexão de Sprint 3 fecha e Sprint 4 inicia com texto. |
| 16 | PASS | AGES I; caixa reflexiva termina antes da conclusão. |
| 17 | PASS | AGES I; conclusão continua em texto justificado dentro das margens. |
| 18 | PASS | AGES I; Figura 5 centralizada, título acima e fonte abaixo. |
| 19 | PASS | Título do capítulo e Introdução 4.1 ocupam a página; 4.2 não aparece isolado no rodapé. |
| 20 | PASS | Figura 9 (legenda em negrito acima, imagem centralizada, fonte abaixo) precede 4.2 e 4.2.1; o texto de repositório segue sem interrupção. O início de 4.2.2 aparece ao fim da página e continua na seguinte. |
| 21 | PENDING | Placeholder ages-ii-database é explicitamente provisório e a arquitetura segue com texto em fluxo. “Angular”, “FastAPI” e “PostgreSQL” aparecem regulares, corrigindo o negrito excedente. Figura 10 tem legenda e fonte visíveis, mas os rótulos permanecem pequenos para decisão de legibilidade em impressão. |
| 22 | PASS | Figuras 11 e 12 ocupam o bloco de protótipos em sequência; títulos acima, fontes provisórias abaixo, imagens visíveis e sem texto de 4.2.5 intercalado. |
| 23 | PASS | Figuras 13 e 14 aparecem em sequência após o bloco de protótipos, com títulos acima e fontes abaixo. Ambas as linhas “Fonte” estão visíveis e sem corte. |
| 24 | PENDING | 4.2.5 segue em uma página, sem float no meio. Chamadas de citação mantêm reticências/espaçamento visual fragmentado; “Documentação Docker” continua sublinhado sem destino de link. |
| 25 | PASS | Seção 4.3 e Sprint 0 aparecem na mesma página com corpo de texto em seguida, sem quebra artificial. |
| 26 | PASS | Sprint 0 continua e Sprint 1 começa após a caixa reflexiva, com texto subsequente. |
| 27 | PASS | Continuação de Sprint 1 legível e dentro das margens. |
| 28 | PASS | Texto de Sprint 1 e caixa reflexiva continuam em fluxo, sem título isolado. |
| 29 | PASS | Caixa reflexiva fecha e Sprint 2 começa na mesma página. |
| 30 | PASS | Relato de Sprint 2 continua e a reflexão inicia próxima ao fim da página, com borda visível. |
| 31 | PASS | Reflexão anterior fecha; Sprint 3 segue com texto e itens numerados. Os títulos “Indexação das colunas mais consultadas” e “Reorganização das tabelas” aparecem sublinhados conforme o estilo efetivo do ODT (T73 interno). |
| 32 | PASS | Continuação de Sprint 3 e reflexão dentro das margens; borda visível. |
| 33 | PASS | A reflexão da Sprint 3 fecha e Sprint 4 começa na mesma página com texto/lista, sem quebra obrigatória. |
| 34 | PASS | Legenda Figura 15 tem prefixo em negrito; imagem e fonte provisória aparecem sem corte. Os dois títulos de etapa estão sublinhados em linhas contínuas, sem lacunas entre palavras. |
| 35 | PASS | Sprint 4 continua após a segunda etapa; listas e parágrafos legíveis e dentro das margens. |
| 36 | PASS | Lista “Campos da Nova Tabela” exibe os sete marcadores; texto subsequente continua sem corte. |
| 37 | PASS | O trecho “memory leak” aparece em itálico incluindo o espaço no span; a caixa reflexiva começa no fim da página e prossegue na p.38 com borda. |
| 38 | PASS | Caixa reflexiva termina e a conclusão começa abaixo; sem quebra artificial nem corte. |
| 39 | PASS | Conclusão termina nesta página com espaço inferior; há corpo textual e não se trata de página vazia/quase vazia. |
| 40 | PASS | Referências e URLs completas legíveis, com espaço inferior; sem recorte ou sobreposição. |

## Verificações gerais

- **Continuidade e paginação — PASS:** Sprints 0–4 começam nas pp.25, 26, 29, 31 e 33; títulos vêm acompanhados de texto e não há quebra obrigatória antes de cada Sprint. A conclusão começa depois da reflexão da Sprint 4.
- **Figuras e placeholders — PASS/PENDING:** Figuras 9–15 estão em contexto, com legendas e linhas de fonte visíveis; numeração e lista coincidem. A fonte de cada imagem continua pendente de identificação manual. O placeholder de banco na p.21 é claramente provisório e identificado como `ages-ii-database`.
- **Reflexões e listas — PASS:** caixas mantêm borda nas continuações naturais; os sete marcadores da lista da p.36 estão presentes.
- **Referências/links — PENDING parcial:** URLs e destinos bibliográficos estão presentes; a p.24 ainda tem rótulos de citação visualmente fragmentados e Docker sublinhado sem destino. Não verifiquei disponibilidade remota.
- **Margens e espaços — PASS/PENDING:** não encontrei texto cortado, sobreposição, conteúdo fora das margens ou página totalmente vazia. A p.2 é esparsa por causa da profundidade 2 de sumário já aprovada (PENDING somente para eventual aceitação humana, sem proposta de alteração); a p.39 contém conclusão e não é quase vazia.
- **Padrão de apresentação aprovado — PASS parcial:** hierarquia, corpo, recuos, legendas e imagens seguem o padrão de referência; pendências remanescentes estão discriminadas acima.

## Limitações e histórico

Esta auditoria cobre a apresentação visual do PDF atual, não certifica integralmente ABNT nem comprova preservação textual completa. Proveniência das imagens e leitura impressa da Figura 10 dependem de validação humana. A página esparsa do sumário decorre da profundidade 2 aprovada no `STYLE_GUIDE.md`; permanece como observação pendente apenas se o usuário quiser confirmar sua aceitação, sem sugerir mudança normativa ou de estilo. O worktree de origem estava sujo, então o commit informado não identifica sozinho todo o snapshot. O relatório inicial do PDF `16cf08d4…`, a reauditoria `835cf3…` e a revisão da cascata de estilos foram preservados em `VISUAL_AUDIT.json` sob `history`. As correções foram julgadas novamente apenas com o hash atual `c1ca7613…`; qualquer próxima compilação exige nova inspeção das páginas afetadas.
