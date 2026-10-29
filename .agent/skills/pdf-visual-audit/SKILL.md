---
name: pdf-visual-audit
description: Inspecionar PDF e renders para paginação, tipografia, figuras e qualidade visual de memorial; geração de thumbnails não equivale a revisão.
---

# pdf-visual-audit

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Ler o papel visual-auditor e STYLE_GUIDE. Identificar PDF/hash/commit/log e executar `visual --pdf <arquivo>`.
2. Abrir todas as páginas em resolução legível; registrar páginas realmente inspecionadas. Conferir glifos, overflow, margens, espaçamento e legibilidade de figuras.
3. Verificar transições de Sprints e caixas longas; não confundir espaço legítimo de pré-textual ou seção primária com quebra artificial.
4. Comparar qualidade visual com Mariah em leitura, sem copiar narrativas/metadados. Conferir legendas/fontes, sumário, listas e referências cruzadas.
5. Emitir relatório por página com evidência e severidade. Revisão incompleta é PENDING; não corrigir LaTeX nem atestar norma apenas pelo aspecto visual.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
