> **Histórico substituído:** esta proposta de 17 páginas antecede a revisão posterior alinhada à Mariah, que também remove os marcadores visuais da lista de tecnologias. Consulte o [parecer final de revisão](POST_FORMAT_REVIEW.md) para o PDF candidato atual (19 páginas, SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`). Esta página preserva evidências históricas e não identifica o artefato que aguarda aprovação.

# Correção de formatação AGES I — candidata à aprovação

**Estado: proposta corrigida e validada, aceite humano PENDING. Não promovida a regra permanente para outros projetos.** Autorização de execução em `migration/approvals/ages-i-format-correction.json`. A branch original continua no baseline `e5a367d438fe865223879ed4742d52379e563335`; as correções permanecem sem commit nela.

O usuário identificou erros concretos no sumário e espaçamentos internos excessivos. O parecer visual anterior classificava os gaps como ressalva e marcou G7 PASS; essa classificação foi insuficiente e o aceite visual foi rejeitado. O PDF anterior `c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f` permanece em snapshot para comparação, mas não serve como aprovação da formatação atual.

## Correções em revisão

| Problema / localização | Causa e consequência | Correção proposta | Verificação |
|---|---|---|---|
| Sumário: capítulo, atividades, Sprints e conclusão desalinhados | Títulos com numeração manual entravam como texto integral; títulos automáticos usavam coluna numérica. Gravidade média | Coluna de 1,8 cm para todos os números; títulos no mesmo X; referências não numeradas alinhadas aos títulos. Prefixos originais `2 -` e `2.4.` preservados | Medição do PDF e inspeção do sumário; conferir todos os 15 títulos, páginas e âncoras |
| Sumário com hierarquia tipográfica uniforme em negrito | Estilos herdados ocultavam distinção entre níveis. Gravidade média | Capítulos/seções em negrito; subseções normais, acompanhando os níveis do corpo | Fontes incorporadas e inspeção do PDF |
| Espaço perdido após travessão nos índices | Expansão Unicode gravava comando TeX cujo delimitador consumia o espaço seguinte. Gravidade média | Grupos vazios delimitam os comandos tipográficos na escrita de sumário/lista de figuras | Conferir `AGES I – EASY CHOOSE` e legendas com espaço após travessão |
| Gaps nos parágrafos `text-p-0303`, `text-p-0314`, `text-p-0318` | Nove tabs internos viravam avanços fixos de 1,251 cm. Gravidade média | Apenas esses nove tabs usam espaço normal de composição; recuos iniciais permanecem | Comparação reversível dos três TeX, validação dos 102 blocos e inspeção dos três parágrafos |

A macro `originalinlinetab` identifica um tab original e o apresenta como espaço normal; `originaltab` continua representando os recuos originais. Os tokens do ODT e suas posições permanecem no manifesto/ledger. Trata-se de uma transformação explícita de **apresentação**, não de igualdade geométrica de whitespace entre ODT e PDF. Nenhuma palavra, acento, pontuação, ênfase ou URL é normalizada por essa política. O validador restringe a transformação aos três IDs, respectivas posições/contagens e à instrução atual do usuário; alterações de redação continuam bloqueadas.

## Artefatos da proposta

- [PDF candidato](../../build/ages-i/format-correction/candidate/document/main.pdf) — 17 páginas, SHA-256 `b51646a946163dde694f1dcbbaac8c85298c18f92721d1552658bd9802b8e568`.
- [Snapshot por hash](../../build/ages-i/format-correction/review/b51646a946163dde694f1dcbbaac8c85298c18f92721d1552658bd9802b8e568/main.pdf).
- [Auditoria independente de conteúdo](CONTENT_AUDIT.md) e [auditoria visual completa](VISUAL_AUDIT.md).
- [Relatório de duas compilações](../../build/ages-i/format-correction/candidate/report.json), [log TeX](../../build/ages-i/format-correction/candidate/document/main.log), [log Biber](../../build/ages-i/format-correction/candidate/document/main.blg).
- [Resultados dos 75 testes](../../build/ages-i/format-correction/tests.txt) e [15 validações / escopo do conversor](../../build/ages-i/format-correction/converter/summary.json).
- [Diferenças textuais e de apresentação](TEXT_DIVERGENCES.json) e [manifesto](../CONTENT_MANIFEST.json).

As compilações foram executadas em clone local temporário, com fontes/código/ledgers candidatos copiados do working tree. Um commit de revisão existiu **somente nesse clone** para satisfazer o gate de build limpo, sem registrar as correções na branch real. O clone foi removido. O [patch da cópia isolada](../../build/ages-i/format-correction/candidate/candidate.patch), os hashes dos fontes e comandos/códigos de saída estão preservados no relatório. As duas compilações produziram o mesmo SHA-256 de PDF. Nenhuma ferramenta foi instalada.

## Aceite e promoção posterior

A aplicação permanente destas decisões a outros projetos está **NOT_APPROVED**. `STYLE_GUIDE.md`, skills e regras globais aprovadas não receberam esta proposta como padrão definitivo. Depois do aceite explícito do usuário sobre o PDF identificado, será possível registrar a decisão aprovada, acrescentar regressões visuais reutilizáveis e integrar o padrão aos próximos projetos em etapa própria.

Continuam pendentes os diagramas reais de arquitetura/banco (placeholders provisórios), fontes das cinco imagens, disponibilidade dos seis links e certificação normativa integral. Não houve migração de outra edição nem revisão editorial. A aprovação desta proposta e da edição permanece humana.

## Resultado da revalidação

- **PASS:** 75 testes automatizados, 15 validações de unidades e auditoria independente dos 102 blocos, 5 imagens, 11 links e reflexões. A mudança de apresentação de nove tabs está explícita no relatório de diferenças.
- **PASS:** duas compilações limpas em clone local isolado, PDF byte a byte idêntico e logs sem achados.
- **PASS visual da proposta:** todas as 17 páginas abertas; números do sumário em X=85,039 pt e títulos em X=136,052–136,063 pt. Espaços dos nove sites internos medidos entre 3,31–4,70 pt ou quebra natural; não há avanço fixo nesses pontos.
- **PENDING:** aprovação humana da proposta/edição e promoção a padrão permanente. A rejeição da apresentação anterior permanece no histórico, sem ser tratada como aceite.

O PDF corrigido também está disponível em [build/document/main.pdf](../../build/document/main.pdf), o caminho já aberto no IDE. O relatório de build identifica o commit temporário do clone, não um commit de aprovação na branch original; `review-state.json` registra essa distinção.
