# Revisão atual do PDF — AGES I / Easy Choose

**Resultado técnico: PASS. Apresentação visual aceita pelo usuário; avanço para AGES II autorizado.** Em 16/10/2026, o usuário avaliou positivamente o resultado e condicionou a próxima edição ao registro permanente do padrão, agora documentado em [STYLE_GUIDE](../STYLE_GUIDE.md) e `migration/approvals/ages-i-presentation-accepted.json`. Esta revisão corresponde ao PDF posterior à configuração do parágrafo de tecnologias em uma unidade contínua com citações autor-data e links. Ela substitui avaliações de PDFs anteriores no [índice da edição](README.md).

Revisão executada em 16/10/2026.

O PDF revisado foi [main.pdf](/home/eduardo/facul/relatorio_ages/build/document/main.pdf), com 18 páginas A4 e SHA-256 `e4822c8d8056433af08104b0a9e8edd0f21828350cc9fcb9d2f335ec4a1d0a98`. O build usou o perfil `document-review`; `review_only: true` e `official_document_gate: NOT_RUN` continuam descrevendo corretamente aquele artefato. O aceite humano autoriza reutilizar a apresentação e avançar para AGES II; não transforma retrospectivamente o build de revisão em build oficial nem resolve as pendências factuais/normativas abaixo.

## Verificações executadas

| Verificação | Resultado | Evidência |
|---|---|---|
| Integridade da origem | PASS | `verify-source` e `inventory --check` retornaram 0; 112 arquivos protegidos conferidos. SHA-256 do ODT permaneceu `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. |
| Cobertura ODT → LaTeX | PASS | As 15 unidades autorizadas retornaram PASS, com 100% de cobertura: 102 registros textuais, 5 imagens e 11 ocorrências de links verificadas nos ledgers. |
| Estrutura LaTeX | PASS | `audit-latex`: 18 arquivos alcançáveis, 20 labels, 4 referências cruzadas e 5 entradas bibliográficas; nenhum achado. |
| Testes do harness | PASS | `python3 -m unittest discover -s tests`: 97 testes, sem falhas. |
| Compilação de revisão | PASS | Tectonic 0.17.0 com Biber 2.17, somente cache local; código 0, `findings: []`, sem avisos no log TeX/Biber. Sumário, lista de ilustrações, referências e links foram gerados. |
| Preparação visual automatizada | PASS | `visual --pdf build/document/main.pdf` renderizou as 18 páginas e encontrou 17 anotações de hyperlink. O comando retorna status 3 por desenho: a ferramenta marca a inspeção como pendente até revisão humana. |
| Inspeção visual desta revisão | PASS_WITH_NOTE | Páginas 1–18 abertas e examinadas. Não encontrei corte, página vazia, legenda deslocada ou quebra artificial antes de Sprint. Há a observação de baixa gravidade abaixo. |
| Conformidade ABNT integral | PENDING | A apresentação observada foi comparada às regras e fontes registradas no [guia de estilo](../STYLE_GUIDE.md). A confirmação integral das normas cruzadas/vigência e de eventual requisito específico da professora/AGES continua pendente; este relatório não certifica conformidade total. |

Os arquivos de evidência são [relatório de compilação](../../build/document/report.json), [log TeX](../../build/document/main.log), [log do Biber](../../build/document/main.blg), [saída do compilador](../../build/document/compiler.txt), [relatório de renderização](../../build/visual/e4822c8d8056433a/report.json) e as imagens `page-01.png` a `page-18.png` no mesmo diretório de renderização.

O resumo automatizado dos gates e das 15 unidades está em `build/ages-i/final-checks/current-document-review.json`; os relatórios de origem, inventário, estrutura LaTeX e a saída dos testes também estão em `build/ages-i/final-checks/`.

## Observações visuais

- O sumário e a lista de ilustrações correspondem aos números de página exibidos; as Sprints 0–4 continuam o fluxo do texto, sem quebra obrigatória criada antes do título.
- Os títulos das figuras usam “Figura”, as legendas ficam acima e as indicações de fonte abaixo. Os cinco elementos reais aparecem na lista de ilustrações; os placeholders de banco de dados e arquitetura estão rotulados como provisórios e não são apresentados como figuras concluídas.
- A Figura 5 está visualmente centralizada na página 17. Não identifiquei desalinhamento que exija correção.
- O parágrafo de tecnologias ocupa uma única unidade contínua, sem marcadores visíveis. As citações autor-data e os links das cinco documentações aparecem no PDF; as entradas bibliográficas usam o ano 2024 e acesso em 10/04/2024 conforme instrução explícita do usuário. Essa data escolhida não é prova de acesso histórico.
- Os links de repositórios e documentações estão em fonte regular e mantêm anotações clicáveis. A presença do destino no PDF não comprova disponibilidade remota atual.
- A borda das reflexões continua entre páginas sem cortar texto. A composição não usa fonte menor nas caixas.
- **Nota de baixa gravidade, página 7:** a hifenização automática quebra “TypeScript” como “TypeS- / cript”. A palavra continua íntegra ao recompor a linha, sem alteração do texto-fonte, mas a divisão visual é pouco elegante. Não alterei a redação nem apliquei uma exceção tipográfica sem nova verificação do efeito na mancha e nos avisos de compilação.

## Pendências que continuam abertas

- **Fontes das imagens:** as cinco figuras reais mantêm “Fonte: pendente de identificação”, conforme decisão do usuário de identificar cada origem manualmente.
- **Diagramas ausentes:** banco de dados e arquitetura continuam representados por placeholders provisórios; os diagramas reais ainda serão fornecidos posteriormente.
- **Links AGES:** as URLs originais permanecem no texto e no PDF. A compilação confirma os destinos embutidos, mas sua disponibilidade remota continua pendente.
- **Referências tecnológicas:** as datas de acesso exatas foram atribuídas dentro da janela da AGES I por autorização do usuário; a versão efetivamente usada no projeto não foi inferida.
- **Pendências factuais/normativas:** fontes das cinco imagens, diagramas reais, disponibilidade remota dos links e confirmação integral de conformidade ABNT permanecem abertas. O usuário autorizou avançar para AGES II mantendo-as registradas; a aprovação da edição integrada continua sujeita à revisão do PDF atualizado.

## Organização do workspace aplicada

O harness ganhou o perfil `document-review`, que gera uma prévia do estado de trabalho no caminho estável `build/document/main.pdf`, identifica o resultado como revisão e deixa explícito que o gate de produção não foi executado. O perfil oficial `document` continua exigindo commit limpo.

Para reproduzir a prévia e renderizar as páginas:

```sh
./build.sh --profile document-review
python3 scripts/migration.py visual --pdf build/document/main.pdf
```

Os 12 arquivos auxiliares que estavam misturados à raiz de `build/document/` foram movidos, sem exclusão, para `build/document/history/prior-run-20261016/`, com hashes e caminhos anteriores em `index.json`. Três cópias idênticas de cache Tectonic, geradas por testes e totalizando 150.668.412 bytes, foram removidas; o cache-semente usado pelos builds permanece intacto no cache local e pode ser copiado novamente quando necessário. O tamanho de `build/` passou de aproximadamente 238 MB para 95 MB.

O conteúdo LaTeX, o template, o relatório da Mariah e o ODT não foram movidos nem editados nesta etapa. Os arquivos `main.pdf` rastreados na raiz e dentro do template foram mantidos intactos.
