# Auditoria visual independente — nova inspeção AGES I

**G7: PASS para este PDF, com uma observação de acabamento de baixa gravidade. Aceite humano: PENDING.** Revisão nova por Codex, subagente `/root/mariah_style_visual_auditor`, independente da autoria; não Antigravity. Pareceres anteriores não foram usados como evidência visual ou aprovação.

PDF examinado: `build/ages-i/mariah-format-redo/candidate/main.pdf`

SHA-256: `b0cf8bffb96c157c9d152c8f7627506018bb94adbbd84afca6eb33374d90a344`

Abri individualmente todas as 19 páginas em `build/visual/b0cf8bffb96c157c/page-01.png` até `page-19.png`, em 827×1170 pixels, aproximadamente 100 dpi, com texto legível. O JSON registra cada hash e observação. Não compilei nem alterei o memorial.

## Referência e método

Reabri os renders das páginas físicas 9, 12, 14 e 17 do PDF somente leitura da Mariah, SHA-256 `ec4c925eff76a1dc09f7feeebaf7382be0777d9f180806f54470f33c48a76420`. Comparei mancha, recuos, interlinha, hierarquia, sumário e legendas. Nenhuma captura adicional do usuário estava disponível no contexto deste subagente; não alego comparação com captura indisponível.

Li exatamente `relatorio_AGES_eduardo/main.tex`, `util/style.tex` e `util/macros.tex`, com hashes no JSON. Essa leitura identifica a implementação usada, mas não substitui a inspeção da saída. As conclusões abaixo vêm do PDF/renders; extração Poppler complementou a identificação de fontes e posições.

A fonte corporal é NimbusSanL regular de 12 pt incorporada. O passo de linha medido é 21,668–21,669 bp, com mancha esquerda em x85,03937 bp; o sumário usa títulos em x144,74448 bp e indicativos em x85,03937 bp. Esses parâmetros e a aparência dos recuos correspondem à referência. Capítulo e seções são negritados; subseções e Sprints são regulares. A4 de aproximadamente 595,28×841,89 bp.

## Achados e verificações

| ID / estado | Arquivo e página | Evidência / gravidade | Correção proposta e verificação |
|---|---|---|---|
| VR-01 / PASS | `util/macros.tex` e unidades com figuras; 2/3/5/6/18 | As cinco legendas e entradas da lista estão em romano, com `Figure N:` em negrito. Descrições sem itálico residual; legenda acima e fonte abaixo de cada imagem. | Nenhuma. Renders e fontes do PDF conferidos. |
| VR-02 / PASS | Unidades de repositório, banco, arquitetura, protótipos e tecnologias; 4/5/7/8 | Todas as âncoras de repositório, Wiki e documentação estão em romano. Itens e descrições tecnológicas também estão em romano e compactos. TypeScript conserva sublinhado, sem inclinação. | Nenhuma para o pedido de romano. Renders e NimbusSanL-Regu nas âncoras conferidos. |
| VR-03 / OBSERVATION | `conteudo/migracao/chapter-02-text-h-0012.tex`; 7–8 | `Documentação PostgreSQL` ficou sozinha no topo da 8, após a descrição na 7. Baixa gravidade: o vínculo visual fica mais fraco, embora legível e sem perda. Não é título órfão. | O conversor testou `samepage` no último item PostgreSQL; o PDF reproduzido manteve o mesmo SHA-256 `b0cf8bffb96c157c9d152c8f7627506018bb94adbbd84afca6eb33374d90a344` e a âncora continuou isolada. O wrapper foi revertido por não ajudar e por bloqueio da validação de escopo. Nenhuma alteração segura aplicada; manter a observação leve para revisão humana. Nenhuma alternativa não testada é declarada validada. |
| VR-04 / PASS | `conteudo/migracao/ages-i-sprint-0.tex` até `ages-i-sprint-4.tex`; 8–17 | Sprints no fluxo; títulos nas páginas 8/9/11/13/15, todos acompanhados de texto. Reflexões 2/4 dividem-se em 12–13/15–16, com bordas íntegras. | Nenhuma. Todas as páginas examinadas. |

As âncoras em romano atendem à instrução explícita do usuário, que prevalece sobre os links itálicos visíveis na referência da Mariah. Não há itálico residual nas categorias solicitadas: âncoras, legendas/descrições de figuras ou itens/descrições tecnológicas.

Há itálico localizado na narrativa das páginas 15–17: por exemplo `Schema`, `path`, `hooks`, `links`, `seed`, `User Experience`, `StakeHolders`, `Sprint Reviews`, `Easy Choose`, `Selenium` e `SonarQube`. Esses casos não pertencem às categorias acima. Não se declara que o documento inteiro esteja sem itálico.

## Cobertura das 19 páginas

| Páginas | Inspeção efetiva |
|---|---|
| 1–2 | Sumário com seis entradas alinhadas, destinos 3/3/4/8/16/19 conferidos; lista com cinco figuras, rótulos negritados e descrições romanas. |
| 3 | Capítulo e introdução legíveis; Figure 1 inteira no contexto da introdução, sem corte, fonte pendente abaixo. |
| 4–5 | Repositórios/Wikis romanos e sem gaps internos; placeholders do banco/arquitetura inteiros, explicitamente provisórios e junto das respectivas seções. Arquitetura continua naturalmente na 5 antes de Protótipos. Figure 2 completa. |
| 6 | Figures 3–4 completas, rótulos negritados, descrições romanas e fontes abaixo; página legítima de figuras. |
| 7–8 | Lista compacta; React inteiro na 7. Observação sobre a documentação PostgreSQL no topo da 8. Fechamento de Tecnologias e Sprint 0 contínuos. |
| 9–10 | Reflexão 0 inteira na 9 e Sprint 1 com parágrafo na mesma página; continuação na 10 sem vazio artificial. |
| 11–13 | Reflexão 1 inteira na 11; Sprint 2 acompanhada de cinco linhas. Reflexão 2 divide-se em 12–13; Sprint 3 continua na 13. |
| 14–16 | Reflexão 3 inteira; Sprint 4 na 15 e reflexão 4 dividida em 15–16; conclusão começa na 16 com texto suficiente. |
| 17–18 | Conclusão legível; Figure 5 inteira em página legítima de float na 18, com legenda e fonte. |
| 19 | Referências documentais legíveis, URLs sem corte e ressalva explícita de que consulta atual não prova versões históricas. |

Não observei corte, sobreposição, glifo ausente, título isolado, página vazia ou página corporal artificialmente quase vazia. O espaço livre dos índices e referências é compatível com o conteúdo; a página 18 acomoda uma figura completa. Nenhuma figura de protótipo interrompe Tecnologias. Nenhum placeholder é apresentado como diagrama real ou incluído entre as cinco ilustrações.

## Limites e estados

PASS restrito ao G7 deste PDF, com VR-03 como recomendação de acabamento. Não significa identidade absoluta com Mariah: preservam-se `Figure`, pontuação original, reflexões com borda e fonte corporal divisível, dois placeholders e fontes pendentes. A paginação menor uniforme não reproduz a variação de tamanho da referência. Não há aprovação humana nem promoção permanente do padrão.

**PENDING:** aceite humano deste PDF/AGES I; fontes das cinco imagens; diagramas reais; disponibilidade dos links de projeto; certificação normativa integral. **NOT_APPLICABLE:** tabelas e notas autorais ausentes. Integridade textual integral pertence ao parecer de conteúdo; não foi inferida da aparência.

Comandos executados: `pdfinfo`, `sha256sum` do candidato/referência, `pdftotext -bbox`, `pdftohtml -xml -hidden -i -stdout`, `pdffonts`, parsers XML/fontes em memória e `git rev-parse HEAD`, todos com retorno 0. Os 19 renders do candidato e quatro da referência foram abertos via `view_image`. Li os três arquivos de configuração indicados; nenhuma fonte foi modificada.

Branch real no commit `e5a367d438fe865223879ed4742d52379e563335`, com candidato de trabalho. Escritas desta tarefa: somente `docs/ages-i/VISUAL_AUDIT.md` e `.json`. Nenhum commit, aceite humano, autorização de outra edição ou promoção permanente foi criado.
