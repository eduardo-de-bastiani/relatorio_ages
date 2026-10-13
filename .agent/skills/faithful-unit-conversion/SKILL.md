---
name: faithful-unit-conversion
description: Converter uma unidade documental autorizada de ODT para LaTeX preservando texto, ordem, links e mídia; excluir revisão editorial e configurações compartilhadas.
---

# faithful-unit-conversion

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Ler o papel converter, manifesto e autorização específica; ausência de autorização bloqueia conversão. Receber ID original, destino e ledger exclusivos.
2. Consultar elementos originais da unidade, inclusive reflexões/descendentes e âncoras de imagens. Preservar todos os caracteres e relações; usar somente macros já preparadas pelo mantenedor.
3. Escapar LaTeX sem alterar redação. Não traduzir, corrigir português, completar dados ou inserir quebras antes de Sprints. Registrar transformações comprovadas de serialização.
4. Executar `validate --ledger migration/ledgers/<unit>.json --unit <unit>` e `scope-check --role converter --unit <unit> --base <commit>`; macro não suportada exige análise, não bypass.
5. Entregar diffs por elemento, arquivos e pendências ao auditor independente. PASS local não autoriza próxima edição.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
