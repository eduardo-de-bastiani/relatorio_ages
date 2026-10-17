# Auditoria visual independente — prosa tecnológica AGES I, II e III

Revisor: agente Codex `technology_prose_visual_audit`, papel AUDITOR VISUAL. Data: 17/10/2026. Nenhuma fonte LaTeX, ledger, bibliografia ou configuração foi alterada por este revisor.

## Artefato e resultado

**PASS para a apresentação da correção autorizada das três seções de tecnologias.** Não foi identificado defeito visual novo que exija correção antes da revisão humana. Isso não aprova a edição, não comprova a equivalência factual da reformulação e não certifica conformidade ABNT integral. Fontes de imagens, disponibilidade de URLs e metadados pendentes continuam **PENDING**.

- PDF inspecionado: `build/document/main.pdf`, 64 páginas A4, SHA-256 `27e555177cf74892cee52a90ba5da411ab6b4c4cb379cd954fdd2db17f01a2e1`.
- Branch/commit informados pelo build: `migration/ages-iii`, `96c09d125fcde4623d2f4d2218ee6aaa0cb5c656`, árvore com alterações locais.
- Renders efetivamente vistos: `build/visual/27e555177cf74892/page-01.png` a `page-64.png`; páginas 8, 24–25 e 47–48 abertas individualmente em resolução de leitura.
- Referência visual vista: `build/reference-review/mariah-46.png` e `mariah-47.png`, páginas físicas 46–47/impressas 45–46 da Mariah. A primeira contém a entrada de tecnologias; a segunda mostra os parágrafos de interface, backend e infraestrutura, com chamadas junto aos nomes. Nenhuma informação de projeto da referência foi transferida por este revisor.
- Comparação anterior: `build/visual/1bb11250fba90a86/`, correspondente ao PDF anterior de 65 páginas. Dezessete imagens são binariamente idênticas: páginas 3–7, 19–23 e 40–46. As outras 47 páginas atuais foram abrangidas pela varredura dos seis painéis de contato, com abertura individual dos trechos principais, transições e dúvidas. A redução de uma página não foi tratada como prova de integridade.

## Método e cobertura

Aplicada a skill PDF, com inspeção dos PNGs reais, além da leitura de `docs/STYLE_GUIDE.md` e `docs/QUALITY_GATES.md`. Gerados somente painéis auxiliares em `build/visual/27e555177cf74892/audit-contact-01.png`, `13`, `25`, `37`, `49` e `61`, a partir dos renders existentes. Os painéis foram todos vistos; a análise não se limitou à extração linear de texto.

Além das cinco páginas das tecnologias, foram abertas individualmente as páginas 1–2, 9–12, 18, 31–33, 39, 50–51, 54, 56–58 e 60–64. Isso cobre os índices, o encerramento de cada capítulo, a lista de referências e as transições mais sensíveis entre reflexão e Sprint após o refluxo. Os demais trechos foram examinados nos painéis de contato. Essa varredura detecta distribuição, vazios, sobreposição e alinhamento; não substitui leitura factual de cada palavra.

Verificações executadas de forma independente:

- SHA-256 do PDF e dos logs via `hashlib`; comparação dos hashes dos 64 PNGs com os anteriores. Código de saída 0.
- `pdfinfo build/document/main.pdf`: código de saída 0, 64 páginas, 595,28 × 841,89 pt, PDF 1.5.
- Inspeção de `build/document/report.json`: `returncode: 0`, `status: pass`, `findings: []`, perfil `document-review`. O gate oficial do memorial consta como `NOT_RUN: review-only build`.
- Busca em `main.log`/`main.blg` por `Warning`, `Overfull`, `Underfull`, `undefined`, `Missing character`, `LaTeX Error` e erros iniciados por `!`: nenhum diagnóstico final correspondente. A ausência de matches da busca não foi tratada como falha de compilação.
- Inspeção das anotações pelo `pypdf`: páginas 8, 24, 47 e 48 contêm, respectivamente, 12, 30, 22 e 16 áreas de link `/GoTo`; página 25 não contém chamada tecnológica nova. Uma chamada quebrada em duas linhas pode gerar várias áreas. Essa contagem confirma a existência das áreas clicáveis; a conferência exaustiva de chaves e destinos pertence ao gate estrutural, não à inspeção de aparência.

## Critérios da correção

| Critério | Página/evidência observada | Resultado |
|---|---|---|
| Prosa organizada pelo uso no projeto | p.8: telas/servidor, interface/APIs, dados e integração; p.24–25: interface, backend, persistência, testes e resultado; p.47–48: backend/gateway, interface, leitor/persistência, nuvem e automação | PASS |
| Citações junto aos nomes | Exemplos visíveis: TypeScript/React na p.8; Angular/TypeScript/Python na p.24; C#/.NET/React na p.47 e AWS/Docker/GitHub na p.48 | PASS |
| Remoção de documentação solta e chamadas repetidas | Nenhum rótulo autônomo “Documentação...”, sequência “Nome: (autor, ano) Utilizado...” ou conector repetido “Mais informações podem ser encontradas em:” nas três seções | PASS |
| Comparação com a construção da Mariah | Mesma estratégia de parágrafos por responsabilidade e citações inseridas nas orações, sem copiar a narrativa ou o conjunto tecnológico dela | PASS |
| Tipografia e ênfases | Corpo regular, alinhamento justificado e recuos consistentes. A p.24 conserva ênfases em termos como `landing page`, `dashboards` e `Object-Relational Mapping`; não aparecem itálicos artificiais em chamadas de documentação | PASS visual; origem das ênfases é objeto da auditoria de conteúdo |
| Espaçamento e margens | Nas páginas 8, 24–25 e 47–48, linhas e parágrafos usam o mesmo padrão do corpo. Nenhuma palavra invade a margem ou é cortada. Ausência de espaçadores documentais soltos após remoção dos links | PASS |
| Entrada/saída da seção | p.8 encerra antes de Atividades/Sprint 0 na p.9; p.25 e p.48 trazem as atividades e início da Sprint 0 após a prosa de tecnologias, com texto suficiente abaixo dos títulos | PASS |
| Paginação | Nenhum título novo ficou isolado no rodapé; nenhum salto obrigatório novo antes de Sprint foi observado. A continuação de parágrafo entre p.24–25 e p.47–48 é legível | PASS |
| Reflexões após refluxo | Bordas continuam por segmentos legíveis; p.10, 12, 31, 33, 51, 54, 56, 58 e 60 mostram encerramentos de reflexão seguidos de Sprint/conclusão no mesmo fluxo | PASS visual |
| Sumário e ilustrações | Sumário p.1–2 aponta tecnologias para 8, 24 e 47; atividades para 9, 25 e 48; referências para 62. Lista p.3 mantém as 20 ilustrações, numeradas 1–5 e 9–23; o intervalo de numeração preexistente não foi alterado nesta correção. Títulos e páginas correspondem ao artefato visto | PASS visual |
| Figuras, legendas e fontes | Nenhuma nova separação imprópria observada. Figura 23 e sua fonte centralizada permanecem juntas na p.47, antes do título de tecnologias. Imagens e fontes das páginas idênticas não mudaram | PASS visual; autoria PENDING |
| Páginas vazias | Nenhuma página em branco. Vazios ao final de capítulos, dos índices e da última página de referências são funcionais; não se confundem com quebras artificiais de Sprint | PASS |

## Registro de questões e limites

| ID/status | Arquivo/localização | Evidência concreta | Consequência e gravidade | Correção/tratamento e verificação |
|---|---|---|---|---|
| TV-01 — RESOLVIDO | h0012, h0046, h0085; p.8, 24–25, 47–48 | A apresentação em lista disfarçada e as chamadas de documentação antes reclamadas não aparecem no PDF atual; a explicação está nas orações sobre uso no projeto | Problema de leitura e aderência à referência visual corrigido | Manter a estrutura por responsabilidade. Nova inspeção dos renders atuais realizada; conteúdo exige auditoria independente própria |
| TV-02 — PENDING herdado | Citações p.24 e p.47 | Aparecem chamadas por título, entre elas `TypeScript [...]`, `Documentação [...]`, `Graph [...]`, `PostgreSQL: [...]`, `SQLAlchemy [...]` e `Introduction [...]` | Menor aproximação nominal à referência Mariah, mas sem truncamento gráfico. Gravidade baixa para aparência; validade factual/autoria não decidida aqui | A bibliografia e seus metadados foram mantidos intactos nesta correção; atribuições novas exigem evidência. O guia vigente admite supressão de título longo quando não há autoria comprovada. Não substituir por autoria inventada; curadoria futura deverá comprovar o nome responsável antes de eventual alteração. Não confundir `Documentação [...]` dentro da chamada bibliográfica com o rótulo de hyperlink eliminado da prosa |
| TV-03 — PENDING herdado | Indicações de fonte, inclusive Figura 23 p.47 | `Fonte: pendente de identificação` continua centralizada e legível | A apresentação está consistente, mas não fornece a proveniência factual da imagem. Gravidade factual a resolver pelo usuário | Identificar manualmente a fonte; revalidar legenda/fonte após a alteração. Esta revisão não declara imagens documentalmente concluídas |
| TV-04 — AVALIADO, sem defeito final observado | `build/document/compiler.txt` versus `main.log` | O agregado contém cinco avisos `Overfull` (h0043, h0075, h0079 e dois h0085), ausentes no `main.log` final e no relatório final. Os renders correspondentes p.20, 41–43 e 47–48 foram vistos sem invasão de margem | Os avisos agregados de passes anteriores não demonstram overflow no PDF final; gravidade visual não materializada no artefato atual | Preservar o agregado como evidência. Basear o diagnóstico de layout no log final e no PDF visto, sem apagar os avisos históricos nem atribuir seu desaparecimento a edição de conteúdo |
| TV-05 — PENDING técnico herdado | `build/document/compiler.txt` | `ICC profile format spec. version 4.3.0 not supported in current PDF version setting` e `ICC profile not embedded` | Limitação de gerenciamento de cor/arquivamento; nenhuma mancha, perda de figura ou falha gráfica visível no render. Gravidade baixa para esta revisão, não avalia impressão/PDF-A | Não converter mídia nem alterar perfil neste escopo. Revisão técnica de exportação/cores permanece separada |
| TV-06 — PENDING | Edição e memorial como um todo | Artefato usa perfil de revisão; fonte de imagens, referências/URLs e aprovação humana ainda não foram concluídas | PASS da correção visual não equivale a aprovação final, ABNT integral ou migração completa | Submeter este PDF identificado ao usuário, junto da auditoria de conteúdo e pendências. Não iniciar outra edição com base neste relatório |

`main.log` final tem SHA-256 `c8e340a74fab2ba4870d69f9e795834c288acbfe284d2438514f2095d006c12f`; o agregado `compiler.txt` da compilação final, `d8a1a1933f2e2261734d19a68516c38a501fc5aaeda5bf4fa4878e0a884d68ff`. A recompilação após o fechamento explícito dos parágrafos por `\par` produziu PDF e `main.log` byte a byte idênticos aos inspecionados; os renders e resultados visuais acima permanecem válidos por essa identidade. O agregado final mantém os mesmos avisos descritos em TV-04/TV-05.

Não foram executados cliques em visualizador nem testes remotos de URLs por este auditor. Não se inferem disponibilidade de destinos, validade de data de publicação/acesso, autoria de imagens ou conformidade normativa integral a partir da aparência. A verificação visual se aplica apenas ao SHA-256 identificado acima; uma recompilação que altere o PDF requer reavaliar seus efeitos.
