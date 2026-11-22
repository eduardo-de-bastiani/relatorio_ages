# Memorial AGES — Eduardo Colla De Bastiani

O PDF para revisão é **[build/document/main.pdf](build/document/main.pdf)**. Edite as fontes em `relatorio_AGES_eduardo/` e gere a prévia com:

```bash
./build.sh --profile document-review
```

O resultado técnico e os logs ficam em `build/document/`. O perfil de revisão não equivale à aprovação humana do memorial. A última revisão técnica registrada passou sem avisos de composição ou `hyperref`.

## Documentação de trabalho

| Documento | Uso |
|---|---|
| [AGENTS.md](AGENTS.md) | Limites de edição e decisões obrigatórias para agentes |
| [Contexto](docs/CONTEXT.md) | Domínio e convenções do memorial |
| [Estilo](docs/STYLE_GUIDE.md) | Apresentação aprovada, links, figuras, citações e reflexões |
| [Operação do harness](docs/HARNESS.md) | Compilar, validar e reproduzir o trabalho |
| [Gates](docs/QUALITY_GATES.md) | Critérios e limites das verificações |
| [Pendências](docs/PENDENCIAS.md) | Questões humanas e histórico de decisões |
| [Plano](docs/MIGRATION_PLAN.md) | Unidades, checkpoints e dependências da migração |

AGES I–III, AGES IV com a conclusão do Recorda, a participação Cliente Hoortech e as considerações finais estão integradas. Permanecem para redação posterior os pré-textuais autorais ainda em placeholder. Fontes de imagens foram indicadas pelo autor; confirmação bibliográfica independente e revisão humana integral continuam sujeitas aos gates.

## Organização

- `RELATORIO_ATUAL.odt`: origem imutável. Não editar.
- `relatorio_AGES_eduardo/`: documento LaTeX atual e imagens utilizadas.
- `relatorio_mariah/`: referência visual protegida, somente leitura.
- `Template_AGES___Guvidaletti/`: fontes do template, usadas pelo perfil de diagnóstico `template`.
- `migration/`: autorizações, ledgers e evidências que sustentam as transformações atuais. Alguns contratos têm hashes fixados pelos validadores; conservar esses arquivos.
- `docs/agents/`, `.agent/skills/`: procedimentos de trabalho. Auditorias e pesquisas históricas conservadas em `docs/` têm vínculos com evidências/aprovações; não são instruções para repetir etapas concluídas.
- `scripts/`, `tests/`, `harness/`: implementação e testes do harness.
- `build/`: resultados locais reproduzíveis. Preservar a prévia atual em `build/document/`. `build/resumo-defesa/` contém preparação local da defesa, incluindo texto e script próprios; não tratá-los como cache descartável.

## Histórico e limpeza

Relatórios intermediários superados, planos já executados, PDFs antigos da raiz/template e caches de tentativas anteriores foram removidos. As regras atuais e as evidências referenciadas por contratos foram mantidas; a limpeza não altera a redação LaTeX, as imagens ou a bibliografia.

Os documentos removidos continuam recuperáveis no commit anterior à limpeza, `1d1d525efa23f23a2b6c3c250273f059747d5f72`. Para consultar um caminho histórico citado nos documentos:

```bash
git show 1d1d525:caminho/do/arquivo.md
```

Evite novos relatórios de tarefa para decisões já concluídas: atualize o documento de trabalho pertinente e mantenha provas exigidas pelos contratos em `migration/`. Resultados de testes, extrações e renderizações devem ficar em `build/`.
