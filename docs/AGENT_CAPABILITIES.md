# Delegação, isolamento e skills

## Antigravity: documentado versus executado

A CLI instalada foi inspecionada na versão **1.3.3**. O help demonstra opções de agente, modo de execução, saída estruturada e sandbox; isto não comprova uma migração com múltiplos agentes funcionando. A pesquisa oficial consultou [subagents](https://www.antigravity.google/docs/subagents), [skills](https://www.antigravity.google/docs/skills), [rules](https://www.antigravity.google/docs/rules) e [projects](https://www.antigravity.google/docs/projects).

| Capacidade | Evidência / limite | Alternativa viável |
|---|---|---|
| Delegação `invoke_subagent` e modos `inherit`, `branch`, `share` | Descritos na documentação; não exercitados aqui como runtime Antigravity | Prompts portáveis de `docs/agents/`, execução manual serial |
| CLI `--agent`, `--print`, saída JSON/schema, modo, sandbox e projeto | Inspeção de help; sem atestado de isolamento de conteúdo desta migração | Encapsular tarefa pelo CLI do harness, controlar paths e revisar diff |
| Paralelismo | Capacidade documental; não foi demonstrada com Sprints reais | Worktree/branch por unidade, ou serial quando indisponível |
| Compartilhamento de checkout | Pode permitir colisões; modo compartilhado não satisfaz exclusividade por si só | Posse de caminhos, locks cooperativos e integração serial |
| Custom agents | Paths/configuração próprios da ferramenta exigem acesso disponível | Sete documentos de papel portáveis; não são agentes auto-registrados |
| Skills locais | Documentação aceita `.agent/skills/` como caminho de compatibilidade | Carregar `SKILL.md` explicitamente; não alegar auto-discovery testado |

A sessão de construção do harness utilizou subagentes Codex reais com arquivos atribuídos e coordenação do orquestrador. Essa execução não é prova de execução independente Antigravity. Não houve conversores trabalhando em Sprints. Eventual teste futuro do runtime deve registrar versão, invocação, tarefas, logs, worktrees e resultados observáveis antes de afirmar que a capacidade foi validada.

## Papéis lógicos

| Papel | Documento | Exclusividade |
|---|---|---|
| ORQUESTRADOR | [orchestrator](agents/orchestrator.md) | Plano/checkpoints e integração serial; sem conteúdo autoral |
| EXTRATOR | [extractor](agents/extractor.md) | Manifesto e extração determinística |
| MANTENEDOR LATEX | [latex-maintainer](agents/latex-maintainer.md) | Configuração, estilos, macros globais |
| CONVERSOR | [converter](agents/converter.md) | Uma unidade e um ledger atribuídos |
| CURADOR DE REFERÊNCIAS | [reference-curator](agents/reference-curator.md) | Evidências bibliográficas separadas |
| AUDITOR DE CONTEÚDO | [content-auditor](agents/content-auditor.md) | Relatórios; fonte lida independentemente |
| AUDITOR VISUAL | [visual-auditor](agents/visual-auditor.md) | PDF/renders e relatórios; não corrige LaTeX |

Esses nomes coincidem com os papéis do `harness.json`. Documentos são prompts de tarefa, não alegação de mecanismo autônomo instalado. `run-task` controla lock cooperativo e conferência de escopo; ele não concede isolamento de sistema operacional nem torna seguro um comando arbitrário. Para paralelismo futuro, exigir worktrees distintos e diffs revisados.

## Skills

`grill-with-docs` foi localizada e usada na entrevista inicial; `grilling` orienta a compreensão compartilhada. A decisão respondida pelo usuário foi incorporada. `find-skills` foi inspecionada e é útil para descobrir procedimentos ausentes, mas nenhuma skill externa foi instalada: extração/validação são implementadas pelo próprio harness e skills locais revisáveis são suficientes.

Sete skills próprias vivem em `.agent/skills/`, compatibilidade legada documentada do Antigravity, pois `.agents/` e `.codex/` deste ambiente são somente leitura. Não são instaladas globalmente nem tiveram descoberta automática testada. O invocador deve ler o arquivo explicitamente quando necessário. Todas delegam algoritmos ao mesmo CLI, evitando scripts duplicados.

Para qualquer skill externa futura: registrar origem e versão/commit, ler integralmente `SKILL.md`, scripts e recursos utilizados; identificar permissões e efeitos; testar em ambiente isolado; só então instalar mediante escopo autorizado. Não executar instaladores opacos nem adicionar dependências somente por resultado de busca.
