---
name: abnt-compliance
description: Verificar apresentação acadêmica ABNT com exigências vinculadas a fontes e medição de PDF; não inventar regras institucionais ou declarar vigência sem prova.
---

# abnt-compliance

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Ler STYLE_GUIDE para fontes/edições e PENDENCIAS para lacunas. Biblioteca PUCRS foi dispensada; não tratá-la como gate ausente.
2. Para cada regra, registrar norma/edição/seção, evidência e aplicabilidade ao memorial. Distinguir norma, decisão do usuário, boa prática técnica e escolha visual de Mariah.
3. Medir PDF e confrontar configuração: margens, fonte/tamanho, espaçamento/exceções, títulos, sumário, citações, referências, figuras e tabelas.
4. Testar saída efetiva do estilo bibliográfico e compilador; nomes abntex2/biblatex-abnt não provam conformidade. Não substituir ABNT por numeric para contornar falha.
5. Emitir matriz PASS/FAIL/PENDING com arquivo/página, consequência, gravidade e verificação. Texto integral ou vigência inacessível fica PENDING; não copiar regras de memória como exigência confirmada.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
