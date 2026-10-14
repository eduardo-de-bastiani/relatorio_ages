# Auditoria visual independente — AGES I

Estado: **FAIL na primeira versão; reavaliação da versão corrigida PENDING**. Revisor: subagente Codex `ages_i_visual_audit`, papel visual independente. Não houve execução Antigravity.

PDF examinado: `build/ages-i/visual-audit/initial-0903a4ec.pdf`, SHA-256 `0903a4ecb1cf1486fc05dde3df72a6ec12e11e7e3cc8c7d428c8fd2f0b47b61a`; commit de origem `ea4b3ee8cad8b441a04730817a91078bc2b83a2a`. Todas as páginas físicas **1–17** foram abertas individualmente, legíveis, em renders150dpi. Hashes individuais e comandos constam no JSON anexo. Preparar renders não foi tratado como aprovação.

## Falhas e pendência observadas

| ID | Estado | Página / evidência | Consequência, correção e retorno |
|---|---|---|---|
| VAI01 | FAIL, alta | p4: Tecnologias inicia antes das Figures3/4; bullet React fica sozinho. p5: figuras dos protótipos. p6: descrição React. | Contexto interrompido. Mantenedor deve conter floats antes de Tecnologias e manter rótulo do item com primeiro parágrafo. Recompilar e inspecionar sequência. |
| VAI02 | FAIL, alta | p13: somente duas linhas no topo; reflexão curta da Sprint4 começa p14. | Vazio artificial. Corrigir cálculo de espaço da caixa após quebra natural; verificar todas reflexões e fluxo da Sprint4. |
| VAI03 | PENDING, média | p3: tabs internos em `text-p-0303`, `text-p-0314`, `text-p-0318`; lacunas mais evidentes em Arquitetura. | Avanço fixo1.251cm mantém tokens; não equivale aos próximos tab stops ODF. Texto legível sem corte. Manter diferença documentada para decisão humana, sem normalização silenciosa. |

Os dois FAILs foram comunicados ao orquestrador antes deste relatório. Correções globais pertencem ao mantenedor; o auditor não alterou memorial, macros, ledger ou mídia.

## Verificações positivas

- Corpo sans-serif Helvetica compatível (`NimbusSanL` incorporada),12pt; reflexão com a mesma família/tamanho, bordas sem sobreposição. Sprint0 divide naturalmente entre p7–8, redesenhando a borda.
- Sprints1/2/4 iniciam em fluxo nas p8/9/12; Sprint3 inicia p11 após p10 quase cheia. Nenhum título de Sprint ficou órfão.
- A4 595.28×841.89pt. Bbox da numeração em todas17p: topo56.693615pt, borda direita538.5828pt, isto é, aproximadamente2cm de topo/direita; corpo inicia x85.039pt≈3cm e termina x538.597pt≈2cm. O limite físico inferior não foi ultrapassado. Espaçamento ordinário visualmente uniforme; medição de configuração acompanhada por PDF real.
- Cinco captions literais Figure1–5 acima das imagens e aparato de fonte pendente abaixo. Figure1 JPEG de metadados atípicos renderiza completo e na orientação correta. Screenshots preservados; títulos e conteúdo principal legíveis, com microtexto inerente à imagem menor.
- p3: dois placeholders explicitamente provisórios, sem simulação de diagrama; não aparecem na lista das cinco figuras reais.
- Sumário e lista de ilustrações na p1 são aparatos derivados; destinos e páginas conferem nesta versão. Sua presença conjunta não é tratada como duplicação autoral, mas a apresentação final e a norma integral permanecem pendentes.
- p16 é página de float da Figure5 após a conclusão; espaço de composição legítimo, sem texto cortado. p17 separa cinco referências de documentação consultadas em2026, com aviso expresso sobre ausência de comprovação histórica.

Comparação somente visual: PDF de Mariah, página física12, renderizado readonly em100dpi. Hierarquia sans-serif, densidade, recuos e espaçamento oferecem acabamento semelhante. Nenhuma narrativa, autoria ou metadado foi transferido.

## Limites e rastreabilidade

Fontes das cinco imagens, diagramas ausentes, conformidade normativa integral e aprovação humana da edição: **PENDING**. Tabelas e notas autorais: **NOT_APPLICABLE**, ausentes nesta edição. Limpeza do log de compilação não neutraliza falha visual. Reavaliação de novo PDF deve vincular novo hash/commit e abrir todas as páginas novamente.

Lidos: AGENTS, CONTEXT, MIGRATION_PLAN, STYLE_GUIDE, QUALITY_GATES, PENDENCIAS, EXECUTION_PLAN, papel visual-auditor, skill local pdf-visual-audit e skill PDF global; PDF/log/relatório de build e arquivos globais/unidade citados apenas para diagnóstico. Alterados pelo auditor: somente este relatório e `VISUAL_AUDIT.json`; temporários em `build/ages-i/visual-audit` e renders do CLI em `build/visual`.

Comandos Poppler (`pdffonts`, `pdftotext -bbox`, `pdftohtml`, `pdftoppm` comparativo) e SHA-256: saída0. `visual --pdf ... --dpi150` foi realmente executado com argumento separado `--dpi 150`: saída3 prevista por revisão humana pendente, ferramentas internas0. Tentativas de importar `fitz`/`lxml` falharam (saída1); nenhuma instalação foi realizada, e medição foi concluída com Poppler/XML da biblioteca padrão. Hash do ODT conferido: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
