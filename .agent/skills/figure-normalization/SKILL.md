---
name: figure-normalization
description: Preparar representação LaTeX rastreável de figuras, fontes e referências cruzadas sem alterar as imagens originais; usar somente na unidade autorizada.
---

# figure-normalization

Skill local do harness. Ler [AGENTS](../../../AGENTS.md), [gates](../../../docs/QUALITY_GATES.md) e o papel correspondente em [docs/agents](../../../docs/agents). O CLI comum é `python3 scripts/migration.py`, executado da raiz; consultar `--help` para parâmetros opcionais. Não instalar dependências nem ampliar escopo ao carregar esta skill.

## Procedimento

1. Localizar imagem/legenda/âncora no manifesto; verificar SHA-256 e arquivo original. Não substituir imagem visualmente parecida.
2. Usar definição do mantenedor para identificação acima, fonte abaixo e label após caption. Criar label único vinculado ao ID; não remover texto de legenda.
3. Registrar fonte desconhecida como pendência, sem supor “elaborado pelo autor”. Para ausência original, utilizar placeholder visual previamente definido, sem diagrama inventado.
4. Avaliar tamanho e posicionamento; `[H]` não é regra. Não modificar raster, crop ou resolução sem autorização; analisar legibilidade no PDF.
5. Executar `audit-latex`, validação de ledger/mídia e build autorizado. Conferir lista de ilustrações e chamadas; entregar evidência visual ao auditor. Esta skill não permite editar macros compartilhadas como conversor.

## Resultado verificável

Registrar unidade/commit, comandos e códigos de saída, arquivos realmente examinados, evidências e limitações. Usar PASS/FAIL/PENDING; não criar aprovação humana nem afirmar que esta skill foi auto-descoberta ou executada por Antigravity sem teste real.
