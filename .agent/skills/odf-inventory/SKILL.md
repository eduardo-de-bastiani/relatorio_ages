---
name: odf-inventory
description: Extrair e inventariar ODT/ODF com rastreabilidade de XML, caixas, mídia e hyperlinks; usar para gerar ou auditar o manifesto deste memorial.
---

# odf-inventory

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Ler AGENTS e CONTEXT; conferir o hash via `python3 scripts/migration.py verify-source`.
2. Executar `inventory`. A fonte é o ZIP/XML integral, não uma extração linear. Checar entradas sem correspondência, estilos, índices, objetos, caixas aninhadas e recursos.
3. Comparar categorias da auditoria: 34 imagens, 17 reflexões, 36 referências textuais, 39 siglas, 25 Sprints; explicar discrepâncias sem ajustar expectativas para esconder perda.
4. Executar `validate`. Inspecionar um título sem texto próprio que possua descendentes e uma caixa aninhada; confirmar não haver perda ou duplicação.
5. Entregar manifesto com hashes/IDs/XPaths/ordem/unidades e classificação de ausências. Nenhuma conversão é autorizada por esta skill.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
