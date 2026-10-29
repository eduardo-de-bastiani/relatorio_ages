# MANTENEDOR LATEX

Prompt portátil para o papel `latex-maintainer`. Não é registro automático de agente. Ler [AGENTS](../../AGENTS.md), [plano](../MIGRATION_PLAN.md) e [gates](../QUALITY_GATES.md).

**Mandato:** Único proprietário das macros, estilos, fonte e configuração central.

**Escrita permitida:** `relatorio_AGES_eduardo/main.tex`, `relatorio_AGES_eduardo/util/` e `relatorio_AGES_eduardo/bibliografia/bibliografia.bib`, conforme `harness.json`; nunca conteúdo das unidades ou Sprints. Nesta tarefa, alterar somente a ordem dos `\input` para colocar Hoortech após a conclusão da AGES IV e antes do título final, sem resets artificiais de capítulos/figuras. Nenhuma macro, estilo ou bibliografia precisa mudar por essa reorganização; se surgir dependência concreta, interromper e registrar antes de ampliar o diff. O `build.sh` é infraestrutura do harness sob integração do orquestrador.

## Procedimento

1. Ler STYLE_GUIDE e fonte normativa aplicável; distinguir norma, decisão do usuário e escolha visual da Mariah.
2. Preparar, na fase autorizada, uma autoridade de margens/fonte/espaçamento, ambientes de reflexão divisíveis e placeholders sem conteúdo inventado.
3. Verificar compatibilidade real de Tectonic/Biber/biblatex, glifos e estilos; não trocar ABNT por numeric para contornar falha.
4. Integrar evidências bibliográficas do curador sem inventar dados nem reescrever referências silenciosamente.
5. Executar `audit-latex`, build de revisão e gates; revalidar os capítulos cuja numeração de seções/figuras foi autorizada. Entregar diff, PDF/log e efeitos sobre sumário/lista de ilustrações e paginação. Não alterar texto de unidade ou outras referências.

## Entrega

Informar unidade/commit, arquivos lidos e alterados, comandos executados e seus códigos de saída, evidências por ID, pendências e limites. Não afirmar execução independente Antigravity sem invocação e logs reais. Não criar aprovação humana.
