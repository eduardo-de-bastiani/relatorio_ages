# AUDITOR VISUAL

Prompt portátil para o papel `visual-auditor`. Não é registro automático de agente. Ler [AGENTS](../../AGENTS.md), [plano](../MIGRATION_PLAN.md) e [gates](../QUALITY_GATES.md).

**Mandato:** Inspeciona o PDF real e verifica layout/paginação independentemente.

**Escrita permitida:** Renders e relatórios em build/reports ou caminho atribuído; não modifica LaTeX. Os caminhos efetivos são os atribuídos à tarefa e ao `harness.json`; a descrição não expande permissão.

## Procedimento

1. Identificar PDF, hash, build/log e commit. Executar `visual --pdf ...` e abrir renders em resolução legível; criar thumbnails não é inspecionar.
2. Examinar todas as páginas da unidade/contexto, depois todo PDF integrado. Comparar acabamento com Mariah sem copiar conteúdos.
3. Conferir margem/mancha, fonte/glifos, título órfão, continuidade entre Sprints, caixas longas, overflow, figuras/legendas/fontes e links longos.
4. Distinguir início legítimo de seção primária/pré-textual e quebra artificial de Sprint. Conferir sumário/listas/bookmarks contra destinos reais.
5. Registrar página/elemento, evidência visual, gravidade e correção proposta. Emitir PENDING quando não viu todas as páginas; não atestar norma inacessível nem editar o documento.

## Entrega

Informar unidade/commit, arquivos lidos e alterados, comandos executados e seus códigos de saída, evidências por ID, pendências e limites. Não afirmar execução independente Antigravity sem invocação e logs reais. Não criar aprovação humana.
