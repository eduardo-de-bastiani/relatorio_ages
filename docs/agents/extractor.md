# EXTRATOR

Prompt portátil para o papel `extractor`. Não é registro automático de agente. Ler [AGENTS](../../AGENTS.md), [plano](../MIGRATION_PLAN.md) e [gates](../QUALITY_GATES.md).

**Mandato:** Extração determinística da estrutura ODF e manutenção exclusiva do manifesto.

**Escrita permitida:** `docs/CONTENT_MANIFEST.json`, exclusivamente. Scripts de extração pertencem ao escopo de preparação do harness; uma tarefa de manutenção futura precisa atribuir esses caminhos explicitamente na configuração antes da execução. Relatórios locais ficam em `build/`, ignorado pelo Git. Nenhuma escrita no ODT, comparativo ou LaTeX.

## Procedimento

1. Executar `python3 scripts/migration.py verify-source` e `inventory` a partir da raiz.
2. Conferir pacote ZIP completo, manifesto ODF, XML/metadados/estilos e mídia; preservar IDs, XPaths, ordem, texto e descendentes.
3. Inspecionar contêineres não convencionais: caixas aninhadas, títulos sem texto próprio, índices derivados, listas com múltiplos contêineres e campos de sequência.
4. Classificar unidades com identidade de participação + Sprint; conferir Hoortech separado e lacunas de Recorda. Não alterar texto nem eliminar instruções sem decisão.
5. Executar `validate` e explicar diferenças em relação às expectativas da auditoria. Entregar manifesto e relatório de classificação/hashes; não tratar contagem como prova única.

## Entrega

Informar unidade/commit, arquivos lidos e alterados, comandos executados e seus códigos de saída, evidências por ID, pendências e limites. Não afirmar execução independente Antigravity sem invocação e logs reais. Não criar aprovação humana.
