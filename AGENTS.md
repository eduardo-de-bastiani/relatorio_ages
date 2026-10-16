# Regras do harness de migração

## Escopo e autoridades

Fase vigente: migração controlada de **AGES II / Indústria Digital**, autorizada pelo usuário e registrada em `migration/approvals/ages-ii-authorization.json`. Trabalhe na branch `migration/ages-ii`, somente nas 15 unidades do capítulo 4 listadas em `harness.json`. AGES I foi revisada; seu padrão visual foi aprovado para reutilização e está em `docs/STYLE_GUIDE.md`. Não converta Hoortech, AGES III, AGES IV ou qualquer outra unidade nesta fase. Após a entrega da AGES II, aguarde aprovação humana.

**Exceção autorizada pelo usuário em 16/10/2026:** aplicar somente correções de apresentação/citações nos quatro trechos técnicos `chapter-02-text-h-0009`–`0011` (AGES I) e `chapter-04-text-h-0043`–`0046` (AGES II), além da macro global de fonte de figuras, conforme `harness.json` e `migration/approvals/ages-i-ii-formatting-authorization.json`. Esta exceção inclui os textos-âncora descritivos aprovados, citações tecnológicas rastreáveis e centralização da fonte das figuras. Ela não autoriza outra unidade nem a próxima edição. As convenções aprovadas ficam documentadas em `docs/STYLE_GUIDE.md` e `docs/QUALITY_GATES.md` para AGES futuras; isso autoriza reutilizar o padrão quando uma edição vier a ser autorizada, sem autorizar migração antecipada.

Leia [CONTEXT](docs/CONTEXT.md), [plano](docs/MIGRATION_PLAN.md), [estilo](docs/STYLE_GUIDE.md), [gates](docs/QUALITY_GATES.md) e [pendências](docs/PENDENCIAS.md). O `harness.json` define caminhos e escopos executáveis; os documentos explicam sua finalidade. Em divergência, interrompa a tarefa afetada e registre a diferença; não amplie permissões.

Autoridades, nesta ordem: instruções explícitas do usuário; original imutável para conteúdo; normas verificadas para apresentação; decisões aprovadas de apresentação. `relatorio_mariah/` é a métrica de qualidade visual definida pelo usuário, somente para leitura. Não transferir narrativa, projetos, referências, epígrafe ou metadados pessoais da Mariah. O modelo restrito da Biblioteca PUCRS foi dispensado pelo usuário e não é dependência.

## Invariantes

Atualização vigente de escopo: a edição em curso continua sendo **AGES II / Indústria Digital**, IDs `chapter-04-text-h-0039` a `chapter-04-text-h-0047`, Sprints `ages-ii-sprint-0` a `ages-ii-sprint-4` e conclusão `chapter-04-text-h-0073`. Soma-se a exceção de correção listada acima para os três trechos técnicos da AGES I e as quatro seções técnicas da AGES II. A lista executável está em `harness.json`; nenhum outro trecho da AGES I ou de outra edição pode ser convertido nesta tarefa. O documento completo da AGES II exige aprovação humana antes de qualquer próxima edição.

- Não revisar português, reformular, expandir, completar ou corrigir fatos nesta fase ou na conversão fiel.
- Preservar acentos, símbolos, pontuação, sequência, âncoras e URLs. Contagem de palavras não comprova integridade.
- Nunca modificar `RELATORIO_ATUAL.odt`; SHA-256 esperado: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Não editar `relatorio_mariah/`. Não confiar em auxiliares/PDFs antigos como prova de compilação.
- Sprints continuam o fluxo: `\input` e título de subseção; nenhuma quebra obrigatória antes do título.
- Diagramas ausentes recebem, na fase autorizada, placeholders visuais claramente provisórios; não inventar seus conteúdos nem suas fontes.
- Reflexões conservam texto e borda, usam a mesma fonte do corpo e admitem divisão entre páginas.
- Aplicar o padrão visual aprovado em `docs/STYLE_GUIDE.md`, distinguindo decisões do usuário, escolhas da referência Mariah, boas práticas técnicas e requisitos normativos verificados.
- Para referências tecnológicas da AGES I/II, usar a janela 2024 e a convenção de ano/data de acesso explicitamente autorizada; registrar datas escolhidas como atribuídas, não como histórico recuperado.
- Revisão editorial e complementações são outra fase.
- Exigir aprovação humana após cada edição AGES. Recomenda-se também um checkpoint próprio para a participação Cliente Hoortech. Aprovação de harness não autoriza o piloto.

## Responsabilidade e escrita

Os sete papéis estão em [docs/agents](docs/agents). Só o EXTRATOR mantém o manifesto; só o MANTENEDOR LATEX escreve estilos/macros/configuração globais. CONVERSORES escrevem apenas a unidade e o ledger atribuídos. Curadoria entrega evidências separadas; integração central é serial. Auditores emitem relatórios sem corrigir o memorial diretamente.

O ORQUESTRADOR coordena e integra; não altera conteúdo. A preparação expressamente autorizada do harness permite alterar documentação, scripts e configuração, não o memorial. A posse de arquivo deve ser registrada antes da execução; duas tarefas não podem possuir o mesmo caminho. Use branches/worktrees para conversores paralelos e integre uma tarefa por vez. Locks são cooperativos: não são uma sandbox de segurança. Não executar comandos não confiáveis sob essa alegação.

Antes e depois de cada tarefa: verificar fonte e escopo, registrar diff e executar os gates correspondentes. Falhas ou cobertura ausente não podem ser convertidas em aprovação automática. Relatórios devem distinguir PASS, FAIL, PENDING e NOT_APPLICABLE com justificativa. Registrar ferramenta, comando, código de saída, commit e hashes dos artefatos.

## Checkpoints e entrega

Faça commits pequenos na branch de trabalho somente quando autorizado. Não sobrescreva trabalho de terceiros, faça reset destrutivo, mude a branch principal ou invente aprovação humana. Uma aprovação precisa de evidência identificável do usuário; um campo JSON sozinho não é autorização.

Artefatos locais ficam em `build/`, conforme configuração. O inventário rastreado não contém arquivos extraídos de mídia redundantes. Não incluir caches, credenciais, PDFs de teste ou auxiliares na integração. Consultar o plano para rollback por commit e reprodução limpa.

Ao concluir: listar arquivos alterados, comandos realmente executados, resultados e limitações. Não declarar agentes Antigravity independentes quando houve execução sequencial ou subagentes de outra ferramenta. Parar após a entrega AGES II e aguardar aprovação; não iniciar outra edição.
