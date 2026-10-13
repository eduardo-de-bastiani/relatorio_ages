---
name: reference-curation
description: Verificar documentação oficial, URLs e metadados bibliográficos com evidência; não inventar registros nem modificar a bibliografia central.
---

# reference-curation

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Ler o papel reference-curator e as referências originais; atribuir ID a cada evidência, sem transferir referências pessoais da Mariah.
2. Testar sintaxe e disponibilidade separadamente; registrar resposta, redirecionamento e data da consulta. Consulta atual não prova data de acesso histórica.
3. Consultar apenas fontes que sustentem o metadado proposto. Registrar valor original, valor sugerido, URL e evidência de autoria/ano/edição.
4. Salvar em `migration/evidence/references/<id>.json` no escopo atribuído. Ausência é pendência, não oportunidade de preenchimento provável.
5. Enviar propostas ao mantenedor/autor; a integração em `.bib` é exclusiva do mantenedor e depende de decisão. Validar posteriormente chaves/citações e PDF, sem alterar texto autoral.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
