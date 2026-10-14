# Auditoria visual independente — AGES I

Estado vigente: **PASS no G7 visual da versão corrigida**, com pendências documentais, de representação, normativas e humanas separadas. Revisor: subagente Codex `ages_i_visual_audit`, papel visual independente. Não houve execução Antigravity.

PDF examinado: `build/ages-i/visual-audit/initial-0903a4ec.pdf`, SHA-256 `0903a4ecb1cf1486fc05dde3df72a6ec12e11e7e3cc8c7d428c8fd2f0b47b61a`; commit de origem `ea4b3ee8cad8b441a04730817a91078bc2b83a2a`. Todas as páginas físicas **1–17** foram abertas individualmente, legíveis, em renders150dpi. Hashes individuais e comandos constam no JSON anexo. Preparar renders não foi tratado como aprovação.

## Histórico da primeira versão — falhas corrigidas

| ID | Estado | Página / evidência | Consequência, correção e retorno |
|---|---|---|---|
| VAI01 | FAIL, alta | p4: Tecnologias inicia antes das Figures3/4; bullet React fica sozinho. p5: figuras dos protótipos. p6: descrição React. | Contexto interrompido. Mantenedor deve conter floats antes de Tecnologias e manter rótulo do item com primeiro parágrafo. Recompilar e inspecionar sequência. |
| VAI02 | FAIL, alta | p13: somente duas linhas no topo; reflexão curta da Sprint4 começa p14. | Vazio artificial. Corrigir cálculo de espaço da caixa após quebra natural; verificar todas reflexões e fluxo da Sprint4. |
| VAI03 | PENDING, média | p3: tabs internos em `text-p-0303`, `text-p-0314`, `text-p-0318`; lacunas mais evidentes em Arquitetura. | Avanço fixo1.251cm mantém tokens; não equivale aos próximos tab stops ODF. Texto legível sem corte. Manter diferença documentada para decisão humana, sem normalização silenciosa. |

Os dois FAILs foram comunicados ao orquestrador antes deste relatório. Correções globais pertencem ao mantenedor; o auditor não alterou memorial, macros, ledger ou mídia.

## Verificações positivas da primeira versão

- Corpo sans-serif Helvetica compatível (`NimbusSanL` incorporada),12pt; reflexão com a mesma família/tamanho, bordas sem sobreposição. Sprint0 divide naturalmente entre p7–8, redesenhando a borda.
- Sprints1/2/4 iniciam em fluxo nas p8/9/12; Sprint3 inicia p11 após p10 quase cheia. Nenhum título de Sprint ficou órfão.
- A4 595.28×841.89pt. Bbox da numeração em todas17p: topo56.693615pt, borda direita538.5828pt, isto é, aproximadamente2cm de topo/direita; corpo inicia x85.039pt≈3cm e termina x538.597pt≈2cm. O limite físico inferior não foi ultrapassado. Espaçamento ordinário visualmente uniforme; medição de configuração acompanhada por PDF real.
- Cinco captions literais Figure1–5 acima das imagens e aparato de fonte pendente abaixo. Figure1 JPEG de metadados atípicos renderiza completo e na orientação correta. Screenshots preservados; títulos e conteúdo principal legíveis, com microtexto inerente à imagem menor.
- p3: dois placeholders explicitamente provisórios, sem simulação de diagrama; não aparecem na lista das cinco figuras reais.
- Sumário e lista de ilustrações na p1 são aparatos derivados; destinos e páginas conferem nesta versão. Sua presença conjunta não é tratada como duplicação autoral, mas a apresentação final e a norma integral permanecem pendentes.
- p16 é página de float da Figure5 após a conclusão; espaço de composição legítimo, sem texto cortado. p17 separa cinco referências de documentação consultadas em2026, com aviso expresso sobre ausência de comprovação histórica.

Comparação somente visual: PDF de Mariah, página física12, renderizado readonly em 100 dpi. Hierarquia sans-serif, densidade, recuos e espaçamento oferecem acabamento semelhante. Nenhuma narrativa, autoria ou metadado foi transferido.

## Limites e rastreabilidade

Fontes das cinco imagens, diagramas ausentes, conformidade normativa integral e aprovação humana da edição: **PENDING**. Tabelas e notas autorais: **NOT_APPLICABLE**, ausentes nesta edição. Limpeza do log de compilação não neutraliza falha visual. A reavaliação final abaixo vincula novo hash/commit e abriu todas as páginas novamente.

Lidos: AGENTS, CONTEXT, MIGRATION_PLAN, STYLE_GUIDE, QUALITY_GATES, PENDENCIAS, EXECUTION_PLAN, papel visual-auditor, skill local pdf-visual-audit e skill PDF global; PDF/log/relatório de build e arquivos globais/unidade citados apenas para diagnóstico. Alterados pelo auditor: somente este relatório e `VISUAL_AUDIT.json`; temporários em `build/ages-i/visual-audit` e renders do CLI em `build/visual`.

Comandos Poppler (`pdffonts`, `pdftotext -bbox`, `pdftohtml`, `pdftoppm` comparativo) e SHA-256: saída0. `visual --pdf ... --dpi150` foi realmente executado com argumento separado `--dpi 150`: saída3 prevista por revisão humana pendente, ferramentas internas0. Tentativas de importar `fitz`/`lxml` falharam (saída1); nenhuma instalação foi realizada, e medição foi concluída com Poppler/XML da biblioteca padrão. Hash do ODT conferido: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.

## Reavaliação final

**PASS visual G7** no PDF de 17 páginas SHA-256 `c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f`, commit `25319d941aa0c7c227dd80094b0b25f582be68b6`. Snapshot imutável: `build/ages-i/review/c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f/main.pdf`. Reabertas individualmente todas as páginas físicas **1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17**, em renders 150 dpi; hashes individuais conferidos e registrados no JSON. Nenhuma nova falha visual foi observada.

| Evidência final | Resultado |
|---|---|
| VAI01, p5–7 | PASS: Figures2–4 permanecem nos Protótipos, p5–6; Tecnologias começa p7. React e sua descrição estão juntos p7. |
| VAI02, p13–14 | PASS: Sprint4 inicia em fluxo p13; reflexão segue o texto p14 e a Conclusão começa abaixo. Eliminado o vazio artificial. |
| VAI03, p4 | PENDING: os três parágrafos com tabs internos permanecem legíveis, com lacunas largas e documentadas. Avanço fixo1.251cm não simula próximos tab stops ODF. Aceitação da representação pertence ao checkpoint humano. |
| Reflexões | PASS: Sprint0 p8–9, Sprint1 p10–11 e Sprint2 p11–12 dividem com borda redesenhada e mesma fonte; Sprint3 p13 e Sprint4 p14 sem corte/sobreposição. |
| Fluxo das Sprints | PASS:0 p8,1 p9,2 p11,3 p12,4 p13. Todos iniciam em fluxo; títulos acompanhados de texto. |
| Aparatos e figuras | PASS visual: sumário p1 e lista de ilustrações p2 separados; cinco destinos de figuras3/5/6/6/16 conferidos; placeholders p4 fora da lista. Figure5 agora itálica também em p16 e na lista p2, consistente com original. |
| Imagens e fontes | PASS de renderização: Figure1 p3 orientada/correta, screenshots p5–6 legíveis em seus elementos principais, cinco legendas acima e cinco fontes explicitamente pendentes abaixo. Microtexto das imagens permanece limitado pela escala/arquivo de origem. |
| Página de figura p16 | Espaço legítimo de composição do float após a conclusão; imagem/legenda/fonte íntegros. |
| Referências p17 | Cinco referências atuais claramente separadas da narrativa, com nota da consulta de2026 e limite sobre versões históricas. |

Medição final independente por `pdftotext -bbox` e XML da biblioteca padrão, saída0: números impressos p2–17 têm topo56.693615pt e borda direita538.5828pt≈2cm das bordas A4; margem esquerda de corpo85.03937pt≈3cm e limite direito538.597115pt≈2cm. p1 do sumário não imprime numeral: composição pré-textual/numeração integral permanece assunto normativo pendente. `pdffonts`, saída0, confirma NimbusSanL regular/negrito/itálico incorporadas. Corpo/reflexão permanecem12pt Helvetica compatível; numeral10pt, sem glifo ausente observado.

Hashes finais conferidos: log `d8360bd7a833d83c5766eb5b76075db62b912f865b66753bd585669698745683`; macro `66b48c4a396515321760beb1c3c1310f81d9ffcbbc24ba20d9c26b931f51e082`. Relatório de build identificado com o mesmo commit/PDF apresenta retorno0 e nenhum finding; foi usado como evidência complementar, após exame real das páginas. O CLI visual final foi preparado pelo orquestrador; o auditor leu seu relatório e verificou hashes/abriu todos os renders, sem alegar nova execução de build.

**PENDING separado do PASS G7:** fontes/autoria das cinco imagens; disponibilidade atual dos seis links de projeto; aceitação dos gaps de tabs; dois diagramas reais ainda ausentes; conformidade ABNT integral e decisões finais pré-textuais; aprovação humana da AGES I. Não há aprovação automática de nenhum desses itens. **NOT_APPLICABLE:** tabelas e notas autorais, ausentes nesta edição.

Na reavaliação o auditor alterou exclusivamente `docs/ages-i/VISUAL_AUDIT.md` e `.json`; nenhuma fonte LaTeX, ledger, macro, mídia ou conteúdo de Mariah foi escrita.
