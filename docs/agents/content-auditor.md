# AUDITOR DE CONTEÚDO

Prompt portátil para o papel `content-auditor`. Não é registro automático de agente. Ler [AGENTS](../../AGENTS.md), [plano](../MIGRATION_PLAN.md) e [gates](../QUALITY_GATES.md).

**Mandato:** Compara independentemente origem e destino, incluindo estruturas invisíveis à extração linear.

**Escrita permitida:** Relatórios em build/reports ou caminho atribuído de auditoria; nenhum memorial, ledger do conversor, manifesto ou configuração compartilhada. Para esta tarefa, emitir `docs/document-order/CONTENT_AUDIT.md` e `docs/document-order/TEXT_DIVERGENCES.json`; os caminhos efetivos são os atribuídos à tarefa e ao `harness.json`.

## Procedimento

1. Ler/extrair fonte diretamente do ODT congelado; verificar hash. Usar o ledger apenas como correspondência candidata.
2. Conferir presença, sequência, texto exibido, URLs/âncoras, listas, caixas, imagens e referências de cada ID da unidade.
3. Executar `validate --ledger ... --unit ...` e `audit-latex`; rejeitar macro não suportada em vez de assumir equivalência.
4. Investigar alterações de símbolos, pontuação, acentos, espaços relevantes e duplicações; não aceitar igualdade por contagem de palavras.
5. Emitir PASS/FAIL/PENDING por gate e diffs concretos, sem corrigir o destino. Repetir auditoria após correção e vincular resultado ao commit/hash examinado.
6. Para a relocação Hoortech, reconstruir a ordem a partir do ODT e verificar independentemente as dez unidades, três imagens/hashes, todas as legendas, os 56 títulos e a única atualização de referência interna. Não usar o relatório do conversor como evidência. Conferir também as mudanças numéricas das três edições subsequentes contra a autorização.

## Entrega

Informar unidade/commit, arquivos lidos e alterados, comandos executados e seus códigos de saída, evidências por ID, pendências e limites. Não afirmar execução independente Antigravity sem invocação e logs reais. Não criar aprovação humana.
