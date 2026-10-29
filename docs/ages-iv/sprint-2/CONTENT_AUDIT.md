# Auditoria de conteúdo — AGES IV, Sprint 2

**Resultado da unidade:** PASS de integridade textual e estrutural, com proveniência suplementar explícita. **Aprovação humana:** PENDING.

## Artefatos e proveniência

- Origem ODT: `RELATORIO_ATUAL.odt`, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Evidência textual autorizadora: `migration/approvals/ages-iv-sprint-2-content-authorization.json`, SHA-256 `949e1204d01661794b1580b15a902b99e53135283e5b69e29b31377839636283`.
- Destino: `relatorio_AGES_eduardo/conteudo/migracao/ages-iv-sprint-2.tex`.
- PDF confrontado: `build/document/main.pdf`, SHA-256 `a07dae33d5d91aea796a41ec8d0c6f1f343fd149645fe8b94e4921e082736662` (107 páginas A4).

A leitura independente de `content.xml` confirmou que a origem contém o título `6.3.3 Sprint 2` (`text-h-0119`, bookmark `__RefHeading___Toc4849_3118176633`), um parágrafo vazio e estruturas de lista vazias antes do título da Sprint 3. Não há prosa, figura, tabela, hyperlink ou nota de Sprint 2 nesse trecho. Os sete parágrafos incorporados foram fornecidos diretamente pelo usuário em mensagem separada e **não** são atribuídos ao ODT nem foram adicionados ao manifesto-fonte.

## Resultado independente

O auditor recebeu a origem e o destino sem usar o relato do conversor como prova. Os sete hashes da autorização são válidos. Cada bloco foi comparado caractere a caractere com o conteúdo autorizado após interpretar somente a marcação inline fornecida (`*…*` como itálico e `` `…` `` como código). Os sete blocos aparecem uma vez e na ordem prevista no LaTeX e no PDF: cinco parágrafos de relato seguidos por dois parágrafos dentro do ambiente `reflection`. O ambiente existente envolve exatamente os dois parágrafos introspectivos.

O título aparece como `5.3.3 Sprint 2`, número decorrente da reorganização documental previamente autorizada. O ID e o bookmark da origem foram mantidos. Nenhum título adicional ou conteúdo de outra edição foi encontrado nesta unidade. Não foram identificadas omissões ou acréscimos nos sete blocos.

A conferência auxiliar de numeração encontrou em `build/document/main.aux` a etiqueta `ages-iv:text-h-0119` com número `5.3.3`, título `5.3.3 Sprint 2` e página 89. O arquivo `.aux` tem SHA-256 `c1da9ea8a9e0db60d89c3e412a28488e6f34fe6c76eb57796ede9a8a3b66b954`. O validador ainda emite `counter_aux_review_required` por não ter campo de evidência `.aux` no ledger; a comparação manual está registrada aqui e não foi usada para suprimir o aviso do harness.

| Unidade/elements | Resultado | Evidência |
|---|---|---|
| `text-h-0119` e bookmark | PASS | Identificador e bookmark preservados; número apresentado como 5.3.3 pela autorização de ordem. |
| `user-ages-iv-sprint-2-report-p01`–`p05` | PASS | Cinco hashes válidos; texto e ordem iguais à autorização; cada parágrafo aparece uma vez no PDF. |
| `user-ages-iv-sprint-2-reflection-p01`–`p02` | PASS | Dois hashes válidos; texto e ordem iguais à autorização; ambos permanecem dentro da caixa `reflection`. |
| Elementos ODF no trecho Sprint 2 | PASS | Apenas título, bookmark, parágrafo e wrappers vazios; sem prosa/imagens/tabelas/links/notas de origem. |

A comparação da extração de texto do PDF desconsiderou apenas ligaturas tipográficas, hifenização no fim de linha e o número corrente de página. O extrator de texto acrescentou um espaço após o ponto final do último parágrafo; a inspeção visual não mostra conteúdo adicional. Essa diferença de serialização está registrada em `TEXT_DIVERGENCES.json` e não foi tratada como mudança da redação.

## Limites e pendências

- Esta auditoria cobre a Sprint 2 e seu trecho no PDF; não certifica todo o memorial.
- A auditoria textual não aprova a apresentação visual; ver `VISUAL_AUDIT.md`.
- O compilador retornou código 0, mas o gate global do perfil `document-review` está FAIL por avisos fora desta unidade e em índices; ver `BUILD_REPORT.md`.
- Revisão e aprovação humana do conteúdo/PDF permanecem PENDING. Não iniciar outra Sprint.

**Auditoria independente:** agente auditor de conteúdo, leitura direta da origem ODF, da autorização, do LaTeX e do PDF; conclusão recebida em 25/10/2026.
