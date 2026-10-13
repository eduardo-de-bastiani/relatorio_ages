---
name: content-preservation-audit
description: Auditar independentemente preservação de conteúdo de unidade ODT→LaTeX, incluindo ordem, caixas, links e imagens; não confiar no relato do conversor.
---

# content-preservation-audit

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Verificar hash e extrair a unidade do original independentemente. Conferir IDs contra manifesto; o ledger só aponta o destino candidato.
2. Executar `validate --ledger ... --unit ...`; examinar diferenças caractere a caractere e por elemento. Preservar acentos, símbolos, pontuação e ordem.
3. Rejeitar normalização sem prova: remoção de diacríticos/pontuação, igualdade por número de palavras e macros arbitrárias não são equivalências.
4. Conferir arquivos/includes, referências e chaves via `audit-latex`; comparar mídia por hash e URLs/âncoras literais. Distinguir lacuna de origem de omissão da conversão.
5. Entregar relatório com arquivo/ID, evidência, impacto, gravidade, proposta e verificação; não modificar destino ou ledger. Revalidar commit corrigido e registrar o hash examinado.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
