# Regras do harness de migração

## Escopo e autoridades

Esta fase prepara governança, inventário e validação. **Nenhuma Sprint nem outro conteúdo do memorial deve ser convertido sem autorização posterior.** O commit-base é `44bc0b95ef5ed06c8efa272de4f754cce1d6e4cb`; o registro verificável está em [docs/BASELINE.json](docs/BASELINE.json). Trabalhe na branch de harness, nunca diretamente na principal.

Atualização de fase: o usuário autorizou explicitamente o projeto-piloto **AGES I / Easy Choose / Sprint 0**, registrado em `migration/approvals/pilot-authorization.json`. Trabalhe na branch `migration/pilot-ages-i-sprint-0`; somente essa unidade e a configuração global necessária podem ser preparados. Auditorias independentes e correções são autorizadas. Nenhuma próxima Sprint está autorizada. O checkpoint de entrega ainda exige revisão do usuário.

Leia [CONTEXT](docs/CONTEXT.md), [plano](docs/MIGRATION_PLAN.md), [estilo](docs/STYLE_GUIDE.md), [gates](docs/QUALITY_GATES.md) e [pendências](docs/PENDENCIAS.md). O `harness.json` define caminhos e escopos executáveis; os documentos explicam sua finalidade. Em divergência, interrompa a tarefa afetada e registre a diferença; não amplie permissões.

Autoridades, nesta ordem: instruções explícitas do usuário; original imutável para conteúdo; normas verificadas para apresentação; decisões aprovadas de apresentação. `relatorio_mariah/` é a métrica de qualidade visual definida pelo usuário, somente para leitura. Não transferir narrativa, projetos, referências, epígrafe ou metadados pessoais da Mariah. O modelo restrito da Biblioteca PUCRS foi dispensado pelo usuário e não é dependência.

## Invariantes

- Não revisar português, reformular, expandir, completar ou corrigir fatos nesta fase ou na conversão fiel.
- Preservar acentos, símbolos, pontuação, sequência, âncoras e URLs. Contagem de palavras não comprova integridade.
- Nunca modificar `RELATORIO_ATUAL.odt`; SHA-256 esperado: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Não editar `relatorio_mariah/`. Não confiar em auxiliares/PDFs antigos como prova de compilação.
- Sprints continuam o fluxo: `\input` e título de subseção; nenhuma quebra obrigatória antes do título.
- Diagramas ausentes recebem, na fase autorizada, placeholders visuais claramente provisórios; não inventar seus conteúdos nem suas fontes.
- Reflexões conservam texto e borda, usam a mesma fonte do corpo e admitem divisão entre páginas.
- Revisão editorial e complementações são outra fase.
- Exigir aprovação humana após cada edição AGES. Recomenda-se também um checkpoint próprio para a participação Cliente Hoortech. Aprovação de harness não autoriza o piloto.

## Responsabilidade e escrita

Os sete papéis estão em [docs/agents](docs/agents). Só o EXTRATOR mantém o manifesto; só o MANTENEDOR LATEX escreve estilos/macros/configuração globais. CONVERSORES escrevem apenas a unidade e o ledger atribuídos. Curadoria entrega evidências separadas; integração central é serial. Auditores emitem relatórios sem corrigir o memorial diretamente.

O ORQUESTRADOR coordena e integra; não altera conteúdo. A preparação expressamente autorizada do harness permite alterar documentação, scripts e configuração, não o memorial. A posse de arquivo deve ser registrada antes da execução; duas tarefas não podem possuir o mesmo caminho. Use branches/worktrees para conversores paralelos e integre uma tarefa por vez. Locks são cooperativos: não são uma sandbox de segurança. Não executar comandos não confiáveis sob essa alegação.

Antes e depois de cada tarefa: verificar fonte e escopo, registrar diff e executar os gates correspondentes. Falhas ou cobertura ausente não podem ser convertidas em aprovação automática. Relatórios devem distinguir PASS, FAIL, PENDING e NOT_APPLICABLE com justificativa. Registrar ferramenta, comando, código de saída, commit e hashes dos artefatos.

## Checkpoints e entrega

Faça commits pequenos na branch de trabalho somente quando autorizado. Não sobrescreva trabalho de terceiros, faça reset destrutivo, mude a branch principal ou invente aprovação humana. Uma aprovação precisa de evidência identificável do usuário; um campo JSON sozinho não é autorização.

Artefatos locais ficam em `build/`, conforme configuração. O inventário rastreado não contém arquivos extraídos de mídia redundantes. Não incluir caches, credenciais, PDFs de teste ou auxiliares na integração. Consultar o plano para rollback por commit e reprodução limpa.

Ao concluir: listar arquivos alterados, comandos realmente executados, resultados e limitações. Não declarar agentes Antigravity independentes quando houve execução sequencial ou subagentes de outra ferramenta. Parar antes do piloto e solicitar autorização.

No piloto autorizado, parar após sua entrega e aguardar aprovação para qualquer próxima Sprint. A frase histórica acima sobre parar antes do piloto descreve o encerramento da fase de harness.
