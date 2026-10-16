# Regras do harness de migração

## Escopo e autoridades

Fase vigente: migração controlada de **AGES III / Sistema de Controle Inteligente de Estacionamento com RFID**, autorizada pela mensagem do usuário em 16/10/2026 e registrada em `migration/approvals/ages-iii-authorization.json`. O usuário aprovou a entrega identificada de AGES I/II; checkpoint `abe761c`. Trabalhe na branch `migration/ages-iii`, somente nas 15 unidades do capítulo 5 listadas em `harness.json`. Reutilize as decisões visuais aprovadas em `docs/STYLE_GUIDE.md`. Não converta Hoortech, AGES IV ou qualquer outra unidade nesta fase. Após a entrega de AGES III, aguarde aprovação humana.

Registro histórico: em 16/10/2026, o usuário autorizou correções de apresentação/citações nos trechos técnicos `chapter-02-text-h-0009`–`0011` (AGES I) e `chapter-04-text-h-0043`–`0046` (AGES II), além da macro global de fonte de figuras, registradas em `migration/approvals/ages-i-ii-formatting-authorization.json`. Essas alterações estão concluídas no checkpoint aprovado `abe761c`; as convenções são reutilizáveis conforme `docs/STYLE_GUIDE.md` e `docs/QUALITY_GATES.md`. O escopo de execução vigente é definido pelo parágrafo acima e por `harness.json`.

Leia [CONTEXT](docs/CONTEXT.md), [plano](docs/MIGRATION_PLAN.md), [estilo](docs/STYLE_GUIDE.md), [gates](docs/QUALITY_GATES.md) e [pendências](docs/PENDENCIAS.md). O `harness.json` define caminhos e escopos executáveis; os documentos explicam sua finalidade. Em divergência, interrompa a tarefa afetada e registre a diferença; não amplie permissões.

Autoridades, nesta ordem: instruções explícitas do usuário; original imutável para conteúdo; normas verificadas para apresentação; decisões aprovadas de apresentação. `relatorio_mariah/` é a métrica de qualidade visual definida pelo usuário, somente para leitura. Não transferir narrativa, projetos, referências, epígrafe ou metadados pessoais da Mariah. O modelo restrito da Biblioteca PUCRS foi dispensado pelo usuário e não é dependência.

## Invariantes

Atualização vigente de escopo: o usuário autorizou exatamente as 15 unidades AGES III enumeradas em `harness.json` e `migration/approvals/ages-iii-authorization.json`: `chapter-05-text-h-0074`–`0080`, `chapter-05-text-h-0085`, `chapter-05-text-h-0086`, Sprints `ages-iii-sprint-0`–`ages-iii-sprint-4` e conclusão `chapter-05-text-h-0097`. A posse dos oito assets também consta nesses arquivos. A aceitação humana anterior de AGES I/II está vinculada ao PDF no registro `migration/approvals/ages-i-ii-final-acceptance.json`; não apaga pendências factuais. Nenhuma unidade de AGES IV ou da participação Cliente Hoortech está autorizada. A entrega AGES III exige aprovação humana antes de qualquer próxima edição.

- Não revisar português, reformular, expandir, completar ou corrigir fatos nesta fase ou na conversão fiel.
- Preservar acentos, símbolos, pontuação, sequência, âncoras e URLs. Contagem de palavras não comprova integridade.
- Nunca modificar `RELATORIO_ATUAL.odt`; SHA-256 esperado: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Não editar `relatorio_mariah/`. Não confiar em auxiliares/PDFs antigos como prova de compilação.
- Sprints continuam o fluxo: `\input` e título de subseção; nenhuma quebra obrigatória antes do título.
- Diagramas ausentes recebem, na fase autorizada, placeholders visuais claramente provisórios; não inventar seus conteúdos nem suas fontes.
- Reflexões conservam texto e borda, usam a mesma fonte do corpo e admitem divisão entre páginas.
- Aplicar o padrão visual aprovado em `docs/STYLE_GUIDE.md`, distinguindo decisões do usuário, escolhas da referência Mariah, boas práticas técnicas e requisitos normativos verificados.
- Para AGES III, não inventar nem retrodatá-las: a data de acesso de cada fonte deve ser a data real da curadoria. A decisão anterior do usuário permite usar o ano de acesso como rótulo autor-data; isso não prova nem substitui a data factual de publicação. Não inventar autores, versões ou URLs. Fontes AGES III não verificadas ficam PENDING; por decisão explícita de 16/10/2026 registrada em `migration/approvals/ages-iii-pending-references-acceptance.json`, a conversão fiel pode prosseguir preservando URLs e sem criar metadados. Os gates de referência das unidades afetadas continuam PENDING, não PASS.
- Revisão editorial e complementações são outra fase.
- Exigir aprovação humana após cada edição AGES. Recomenda-se também um checkpoint próprio para a participação Cliente Hoortech. Aprovação de harness não autoriza o piloto.

## Responsabilidade e escrita

Os sete papéis estão em [docs/agents](docs/agents). Só o EXTRATOR mantém o manifesto; só o MANTENEDOR LATEX escreve estilos/macros/configuração globais. CONVERSORES escrevem apenas a unidade e o ledger atribuídos. Curadoria entrega evidências separadas; integração central é serial. Auditores emitem relatórios sem corrigir o memorial diretamente.

O ORQUESTRADOR coordena e integra; não altera conteúdo. A preparação expressamente autorizada do harness permite alterar documentação, scripts e configuração, não o memorial. A posse de arquivo deve ser registrada antes da execução; duas tarefas não podem possuir o mesmo caminho. Use branches/worktrees para conversores paralelos e integre uma tarefa por vez. Locks são cooperativos: não são uma sandbox de segurança. Não executar comandos não confiáveis sob essa alegação.

Antes e depois de cada tarefa: verificar fonte e escopo, registrar diff e executar os gates correspondentes. Falhas ou cobertura ausente não podem ser convertidas em aprovação automática. Relatórios devem distinguir PASS, FAIL, PENDING e NOT_APPLICABLE com justificativa. Registrar ferramenta, comando, código de saída, commit e hashes dos artefatos.

## Checkpoints e entrega

Faça commits pequenos na branch de trabalho somente quando autorizado. Não sobrescreva trabalho de terceiros, faça reset destrutivo, mude a branch principal ou invente aprovação humana. Uma aprovação precisa de evidência identificável do usuário; um campo JSON sozinho não é autorização.

Artefatos locais ficam em `build/`, conforme configuração. O inventário rastreado não contém arquivos extraídos de mídia redundantes. Não incluir caches, credenciais, PDFs de teste ou auxiliares na integração. Consultar o plano para rollback por commit e reprodução limpa.

Ao concluir: listar arquivos alterados, comandos realmente executados, resultados e limitações. Não declarar agentes Antigravity independentes quando houve execução sequencial ou subagentes de outra ferramenta. Parar após a entrega AGES III e aguardar aprovação; não iniciar AGES IV nem Hoortech.
