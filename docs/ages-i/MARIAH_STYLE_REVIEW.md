# Formatação da Mariah — comparação e proposta aplicada à AGES I

> **Versão substituída para revisão:** o PDF e o hash abaixo identificam um candidato anterior. A revalidação posterior removeu os marcadores visuais da lista de tecnologias, atualizou os relatórios independentes e identificou o candidato atual em [POST_FORMAT_REVIEW.md](POST_FORMAT_REVIEW.md): 19 páginas, SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`.

**Estado: candidata validada, aguardando aceite humano.** Preferência expressa do usuário registrada em `migration/approvals/ages-i-mariah-style.json`. Nenhum commit das correções foi criado na branch real; nenhuma outra edição foi migrada. A promoção permanente continua pendente do aceite da versão identificada.

A apresentação anterior não era igual à referência: coincidia na família de fonte e nas margens, mas tinha entrelinha menor, recuos distintos, capítulo centralizado e sumário mais detalhado. A proposta atual acompanha as medidas efetivas do PDF da Mariah, não apenas valores declarados no template.

## Comparação efetiva dos PDFs

| Elemento | Referência da Mariah | Proposta atual |
|---|---|---|
| Papel e margens | A4; superior/esquerda 3 cm, inferior/direita 2 cm | Iguais |
| Corpo | Helvetica compatível, 12 pt, fonte NimbusSanL incorporada | Igual |
| Avanço das linhas | Aproximadamente 21,669 pontos do PDF | 21,668–21,669 pontos; antes cerca de 17,93 |
| Recuo da primeira linha | Aproximadamente 17,559 pontos do PDF (0,62 cm) | Igual; um só recuo, sem somar tabs autorais |
| Espaço entre parágrafos | `0pt plus 1pt` da classe | Igual |
| Capítulos | Alinhados à esquerda e em negrito | Igual; título/numeração original preservados |
| Seções/subseções | Tamanho normal; seções em negrito, subseções regulares | Igual |
| Sumário | Somente capítulos/seções (`tocdepth=1`) | Igual; Sprints continuam no corpo e no manifesto |
| Coluna dos títulos do sumário | X≈144,743 pontos do PDF | X≈144,744; diferença aproximada de 0,001 ponto |
| Entre capítulo e conteúdo | 24 pt na configuração | Igual |
| Links | Pretos | Igual; âncoras e URLs originais preservadas |

A fonte vem da mesma família tipográfica; os compiladores e a representação interna das fontes no PDF diferem, portanto não se afirma identidade binária com o relatório dela. A comparação de layout foi feita contra o PDF existente, em leitura. Nenhum texto, projeto, referência ou metadado pessoal da Mariah foi transferido.

## Diferenças deliberadamente mantidas

- **Numeração das páginas:** a referência alterna 10 pt nas páginas iniciais de capítulo e 12 pt nas demais. Mantivemos 10 pt uniforme e menor que o corpo, conforme a exigência normativa já verificada no projeto. Não se copiou essa alternância.
- **Reflexões:** seu memorial conserva as caixas com borda, mesma fonte do corpo e divisão natural entre páginas; esse elemento não existe na referência.
- **Diagramas ausentes:** os dois placeholders continuam claramente provisórios. As cinco imagens originais mantêm indicação de fonte pendente, sem atribuição inventada.
- **Conteúdo original:** redação, numeração digitada, títulos/ênfases das legendas e divisões autorais permanecem preservados. Isso inclui identificadores literais `Figure`, `2 -` e `2.4.`; não se traduziu nem reescreveu o memorial para imitar a redação da referência.
- **Posicionamento de figuras:** a composição mantém leitura contextual sem impor `[H]` a todas as imagens. Sprints continuam sem quebra obrigatória de página.

## Preservação e validação

Os 82 parágrafos autorais têm política de apresentação rastreada; tabs e espaços iniciais continuam identificáveis no original/ledger, sem acrescentar recuos visíveis. Foram alteradas 59 declarações de recuo de prosa/reflexão; os 11 parágrafos de links isolados e as listas mantêm alinhamento estrutural. Os nove tabs internos da correção anterior continuam como espaços normais de composição. Essa transformação de aparência não é apresentada como igualdade literal de whitespace no PDF.

- **PASS conteúdo:** 102 blocos, 15 títulos, 5 imagens/legendas, 11 links, 5 reflexões com 17 parágrafos, ordem, pontuação e ênfases conferidos independentemente contra o ZIP/XML do ODT.
- **PASS automático:** 15 validações finais e 83 testes. As transformações dos 15 TeX são reversíveis até os bytes do baseline; conteúdo pessoal não foi revisado.
- **PASS compilação:** duas compilações limpas em clone local isolado geraram PDF byte a byte idêntico, sem achados de log. O commit de revisão existiu somente no clone temporário, não na branch original.
- **PASS visual da proposta:** todas as 19 páginas abertas e comparadas à referência; figuras/contexto, reflexões, placeholders e fluxo das Sprints sem defeitos corrigíveis observados.
- **PENDING:** aceite humano, promoção permanente, diagramas reais, proveniência das imagens, disponibilidade dos seis links e certificação normativa integral.

## Entregáveis identificados

- PDF daquele candidato: 19 páginas; SHA-256 `9670b53640a3b2f67977100bc51fd381af56403d96b941f15f6e37252aa04d38`. O binário não está mais disponível nesse caminho; veja o PDF atual em [CURRENT_REVIEW.md](CURRENT_REVIEW.md).
- [Snapshot imutável](../../build/ages-i/mariah-style/review/9670b53640a3b2f67977100bc51fd381af56403d96b941f15f6e37252aa04d38/main.pdf).
- [Auditoria visual comparativa](VISUAL_AUDIT.md) e [auditoria independente de conteúdo](CONTENT_AUDIT.md).
- [Diferenças e transformações](TEXT_DIVERGENCES.json), [manifesto](../CONTENT_MANIFEST.json) e [autorização da proposta](../../migration/approvals/ages-i-mariah-style.json).
- [Comandos/duas compilações](../../build/ages-i/mariah-style/candidate/report.json), [log TeX](../../build/ages-i/mariah-style/candidate/document/main.log), [Biber](../../build/ages-i/mariah-style/candidate/document/main.blg) e [15 validações](../../build/ages-i/mariah-style/converter/final-validation-results.json).
- [Comparação medida do mantenedor](../../build/ages-i/mariah-style/maintainer/report.json) e [resultado dos testes](../../build/ages-i/mariah-style/tests-result.json).

A referência e o ODT continuam intactos. O PDF integral do memorial ainda não foi migrado: esta entrega contém somente AGES I e seus aparatos de revisão. Aprovar o padrão de apresentação não autoriza automaticamente a próxima edição.
