# Revisão e aplicação de chamadas bibliográficas solicitadas pela professora — 10/11/2026

## Estado após a autorização do usuário

O usuário autorizou a retirada de `[...]` e confiou ao projeto a eliminação de chamadas repetidas dentro de uma mesma seção, preservando citações em seções e edições distintas. A apresentação foi ajustada em `relatorio_AGES_eduardo/util/style.tex`, e as 13 segundas/terceiras chamadas mapeadas abaixo foram retiradas dos cinco arquivos de conteúdo. A primeira ocorrência de cada chave **permanece em cada seção**; a redação e a pontuação do texto não foram alteradas. Os registros de transformação estão em `migration/approvals/citation-deduplication-2026-11-10.json` e nos ledgers das cinco unidades.

| IDs | Resultado verificado |
|---|---|
| C01 | Marcador retirado na chamada renderizada. |
| C02 | Marcador retirado na chamada renderizada. |
| C03 | Marcador retirado na chamada renderizada; o rótulo continua “Documentação”. |
| C04 | Marcador retirado na chamada renderizada; o rótulo continua “Graph”. |
| C05 | Marcador retirado na chamada renderizada. |
| C06 | Chamada inteira retirada como repetição R06; não há substituição renderizada. |
| C07 | Marcador retirado; a pontuação final solta do primeiro termo também foi corrigida: `(TypeScript, 2026)`. |
| C08 | Marcador retirado; o rótulo continua “Introduction”. |
| C09 | Marcador retirado na chamada renderizada. |
| C10 | Marcador retirado na chamada renderizada. |
| C11 | Marcador retirado; o rótulo continua “Tutorial”. |
| C12 | Marcador retirado na chamada renderizada. |
| C13 | Marcador retirado na chamada renderizada. |
| C14 | Marcador retirado; o rótulo continua “Getting”. |
| C15 | Marcador retirado; o rótulo continua “Tutorial”. |
| C16 | Marcador retirado na chamada renderizada. |
| C17 | Marcador retirado na chamada renderizada. |
| C18 | Marcador retirado na chamada renderizada. |
| C19 | Marcador retirado; o rótulo continua “Getting”. |
| R01 | Segunda chamada retirada; primeira mantida. |
| R02 | Segunda chamada retirada; primeira mantida. |
| R03 | Segunda chamada retirada; primeira mantida. |
| R04 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R05 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R06 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R07 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R08 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R09 | Terceira chamada retirada na mesma seção; primeira mantida. |
| R10 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R11 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R12 | Chamada posterior retirada na mesma seção; primeira mantida. |
| R13 | Chamada posterior retirada na mesma seção; primeira mantida. |

Auditoria independente: **103 → 90** chamadas `\cite`, **49 chaves distintas preservadas**, prosa e pontuação idênticas após retirar apenas citações/espaçadores, `.bib` e ODT intactos. O PDF atualizado é `build/document/main.pdf`, SHA-256 `2f2b5e1556597de86321facf0f979e26305b008a8cbe8557427437de9c0f99d6`: zero `[...]`; 18 alvos C ainda renderizados sem o marcador, e C06 retirado por R06. O compilador retornou zero, mas o gate geral continua FAIL por 17 ocorrências `OVERFULL` e dois avisos `hyperref`. A conformidade normativa G4b para chamadas por título sem autoria segue **PENDING**; a forma visual foi aprovada pela professora, sem atribuir autor inexistente.

## Mapeamento anterior à aplicação

As tabelas seguintes preservam o diagnóstico e as recomendações **antes da autorização mais recente**; o estado aplicado de cada ID está na tabela acima. A capa foi tratada separadamente. A fonte de inspeção inicial foi `relatorio_AGES_eduardo/conteudo/migracao/`, confrontada com `relatorio_AGES_eduardo/bibliografia/bibliografia.bib` e com a prévia anterior `build/document/main.pdf` (SHA-256 `72479fe6a72c53464e8ccdd5c3ea1be0a4a7fec33a4759e52572b6712ba1304b`). O `main.pdf` na raiz não foi usado. Não foram acessados links externos.

Foram encontradas **19 chamadas renderizadas com `[...]`**, correspondentes a **19 chamadas `\cite` em 11 entradas bibliográficas**. Todas as 11 entradas estão sem campo `author` no `.bib` local. A ausência desse campo não demonstra, por si, que a página externa não possua responsável. O gate G4b em `docs/QUALITY_GATES.md` e `docs/STYLE_GUIDE.md` atualmente exige supressão do restante do título, com `[...]`, quando a fonte sem autoria tem título de mais de uma palavra. Assim, retirar os colchetes de uma chamada baseada no título pode criar uma desconformidade. Antes de cada futura substituição, verificar se há **autoria institucional comprovada** ou outra identificação bibliográfica sustentável. O nome de uma tecnologia no texto não deve ser automaticamente tratado como autor da documentação.

Na tabela, “remoção literal para exame” mostra somente a retirada de `[...]`, sem substituir o restante da chamada por um nome de tecnologia. **Não é uma correção já aprovada no gate nem alteração aplicada**. Alguns resultados ficariam genéricos ou com pontuação estranha; isso reforça a necessidade de decidir a identificação bibliográfica antes da edição.

## A. Chamadas com `[...]` — decisão individual pendente

Todos os caminhos desta tabela são relativos a `relatorio_AGES_eduardo/conteudo/migracao/`. Cada ID designa **uma ocorrência**, mesmo quando várias usam a mesma chave.

| ID | Local | Chave | Chamada atual no PDF | Remoção literal para exame | Título no `.bib` | Risco/ação antes de editar |
|---|---|---|---|---|---|---|
| C01 | `chapter-04-text-h-0043.tex:8`, AGES II §3.2.2 | `ages-ii-sqlalchemy` | `(SQLAlchemy [...], 2024)` | `(SQLAlchemy, 2024)` | SQLAlchemy 2.0 Documentation | Médio: confirmar autoria/forma de identificação antes de suprimir o restante do título. |
| C02 | `chapter-04-text-h-0046.tex:8`, AGES II §3.2.5 | `ages-ii-typescript` | `(TypeScript [...], 2024)` | `(TypeScript, 2024)` | TypeScript para programadores JavaScript | Médio: mesma verificação. |
| C03 | `chapter-04-text-h-0046.tex:10`, AGES II §3.2.5 | `ages-ii-python` | `(Documentação [...], 2024)` | `(Documentação, 2024)` | Documentação Python 3 | **Alto:** rótulo genérico; não substituir por “Python” como autor sem prova. |
| C04 | `chapter-04-text-h-0046.tex:10`, AGES II §3.2.5 | `ages-ii-graph-api` | `(Graph [...], 2024)` | `(Graph, 2024)` | Graph API - Documentation | Médio: rótulo curto e ambíguo; conferir tratamento bibliográfico. |
| C05 | `chapter-04-text-h-0046.tex:14`, AGES II §3.2.5 | `ages-ii-sqlalchemy` | `(SQLAlchemy [...], 2024)` | `(SQLAlchemy, 2024)` | SQLAlchemy 2.0 Documentation | Médio: mesma fonte de C01; aplicar decisão bibliográfica consistente às duas chamadas. |
| C06 | `chapter-04-text-h-0046.tex:14`, AGES II §3.2.5 | `ages-ii-python` | `(Documentação [...], 2024)` | `(Documentação, 2024)` | Documentação Python 3 | **Alto:** mesma fonte e rótulo genérico de C03. |
| C07 | `chapter-05-text-h-0085.tex:12`, AGES III §4.2.5 | `ages-iii-typescript` | `(TypeScript: [...], 2026)` | `(TypeScript:, 2026)` | TypeScript: JavaScript With Syntax For Types. | Médio: dois pontos ficariam pendurados; confirmar identificação antes de alterar. |
| C08 | `chapter-05-text-h-0085.tex:12`, AGES III §4.2.5 | `ages-iii-javascript` | `(Introduction [...], 2026)` | `(Introduction, 2026)` | Introduction - JavaScript \| MDN | **Alto:** rótulo genérico; não substituir por “JavaScript” como autor sem prova. |
| C09 | `chapter-06-text-h-0109.tex:9`, AGES IV §5.2.2 | `ages-iv-supabase` | `(Supabase [...], 2026)` | `(Supabase, 2026)` | Supabase Docs | Médio: confirmar autoria/forma de identificação. |
| C10 | `chapter-06-text-h-0110.tex:9`, AGES IV §5.2.3 | `ages-iv-expo` | `(Expo [...], 2026)` | `(Expo, 2026)` | Expo documentation | Médio: confirmar autoria/forma de identificação. |
| C11 | `chapter-06-text-h-0110.tex:9`, AGES IV §5.2.3 | `ages-iv-fastapi` | `(Tutorial [...], 2026)` | `(Tutorial, 2026)` | Tutorial - User Guide | **Alto:** rótulo genérico; “FastAPI” não consta do título registrado. |
| C12 | `chapter-06-text-h-0110.tex:9`, AGES IV §5.2.3 | `ages-iv-pydantic` | `(Pydantic [...], 2026)` | `(Pydantic, 2026)` | Pydantic Validation | Médio: confirmar autoria/forma de identificação. |
| C13 | `chapter-06-text-h-0110.tex:9`, AGES IV §5.2.3 | `ages-iv-supabase` | `(Supabase [...], 2026)` | `(Supabase, 2026)` | Supabase Docs | Médio: mesma fonte de C09. |
| C14 | `chapter-06-text-h-0110.tex:9`, AGES IV §5.2.3 | `ages-iv-jest` | `(Getting [...], 2026)` | `(Getting, 2026)` | Getting Started | **Alto:** rótulo genérico; “Jest” não consta do título registrado. |
| C15 | `chapter-06-text-h-0113.tex:8`, AGES IV §5.2.5 | `ages-iv-fastapi` | `(Tutorial [...], 2026)` | `(Tutorial, 2026)` | Tutorial - User Guide | **Alto:** mesma fonte de C11. |
| C16 | `chapter-06-text-h-0113.tex:8`, AGES IV §5.2.5 | `ages-iv-pydantic` | `(Pydantic [...], 2026)` | `(Pydantic, 2026)` | Pydantic Validation | Médio: mesma fonte de C12. |
| C17 | `chapter-06-text-h-0113.tex:10`, AGES IV §5.2.5 | `ages-iv-expo` | `(Expo [...], 2026)` | `(Expo, 2026)` | Expo documentation | Médio: mesma fonte de C10. |
| C18 | `chapter-06-text-h-0113.tex:12`, AGES IV §5.2.5 | `ages-iv-supabase` | `(Supabase [...], 2026)` | `(Supabase, 2026)` | Supabase Docs | Médio: mesma fonte de C09/C13. |
| C19 | `chapter-06-text-h-0113.tex:14`, AGES IV §5.2.5 | `ages-iv-jest` | `(Getting [...], 2026)` | `(Getting, 2026)` | Getting Started | **Alto:** mesma fonte de C14. |

## B. Repetições de referência no mesmo parágrafo

A auditoria percorreu **103 chamadas `\cite` em 49 chaves** nos arquivos LaTeX do memorial e agrupou ocorrências por parágrafo e função da afirmação. As três situações abaixo estão na **mesma linha/parágrafo** de `chapter-04-text-h-0044.tex:10`, seção de arquitetura da AGES II, página impressa 35 do PDF.

| ID | Chave | Primeira chamada, a manter | Segunda chamada | Proposta e motivo | Estado |
|---|---|---|---|---|---|
| R01 | `ages-ii-fastapi` | após “que utiliza o FastAPI” | após “O FastAPI” | **Remover apenas a segunda `\cite{ages-ii-fastapi}`**, preservando nome e frase. É a mesma fonte no mesmo fluxo explicativo, sem nova atribuição independente. | Candidato forte; não aplicado. |
| R02 | `ages-ii-angular` | após “No Front-end, o Angular” | após “para o Angular” | Avaliar individualmente. A segunda chamada acompanha a afirmação de atualização da interface em tempo real; pode haver motivo para mantê-la. | Pendente de decisão; não aplicar automaticamente. |
| R03 | `ages-iv-postgresql` | após “banco de dados PostgreSQL” | após “consultas SQL” | **Manter**: mesma chave acompanha dois termos e afirmações técnicas diferentes. | Revisado; nenhuma remoção proposta. |

## C. Chamadas repetidas em parágrafos distintos do mesmo tópico

Aqui “tópico” significa a mesma seção LaTeX. A repetição da chave oferece uma oportunidade de revisão, mas **não prova redundância**: cada novo parágrafo pode usar a fonte para outra função da tecnologia. O levantamento abaixo cobre cada segunda ou terceira ocorrência dentro da seção, com sua linha anterior. Todos os caminhos continuam relativos a `relatorio_AGES_eduardo/conteudo/migracao/`.

| ID | Arquivo e chave | Chamada anterior → chamada examinada | Decisão sugerida | Motivo |
|---|---|---|---|---|
| R04 | `chapter-02-text-h-0012.tex`, `ages-iii-react` | linha 6 → linha 9 | Manter por ora | O novo parágrafo introduz o React especificamente na interface do tablet; a primeira chamada está ligada ao conjunto TypeScript/React. |
| R05 | `chapter-04-text-h-0046.tex`, `ages-ii-angular` | linha 8 → linha 11 | Revisar antes de remover | A linha 11 aborda a comunicação da API com a interface Angular, diferente da descrição inicial das telas. |
| R06 | `chapter-04-text-h-0046.tex`, `ages-ii-python` | linha 10 → linha 14 | Manter por ora | A linha 14 descreve consultas e manipulação de dados por ORM, função diferente da coleta e enriquecimento citada antes. |
| R07 | `chapter-04-text-h-0046.tex`, `ages-ii-fastapi` | linha 10 → linha 15 | Revisar antes de remover | A linha 15 trata de consultas ao PostgreSQL, enquanto a primeira chamada acompanha comunicação com o Front-end. |
| R08 | `chapter-04-text-h-0046.tex`, `ages-iv-postgresql` | linha 11 → linha 14 | Manter por ora | A nova menção situa o banco no mapeamento ORM. |
| R09 | `chapter-04-text-h-0046.tex`, `ages-iv-postgresql` | linha 14 → linha 17 | Manter por ora | A nova menção descreve ambiente de testes local com Docker. |
| R10 | `chapter-05-text-h-0079.tex`, `ages-iii-dotnet` | linha 9 → linha 15 | Manter por ora | A primeira citação acompanha backend em nuvem; a segunda, o gateway local. |
| R11 | `chapter-05-text-h-0079.tex`, `ages-iii-rfid-nist` | linha 12 → linha 15 | Manter por ora | A primeira acompanha eventos de hardware RFID; a segunda, o leitor instalado no ambiente local. |
| R12 | `chapter-05-text-h-0085.tex`, `ages-iii-dotnet` | linha 8 → linha 15 | Manter por ora | A segunda menção explica integração do Entity Framework com .NET, função nova no tópico. |
| R13 | `chapter-05-text-h-0085.tex`, `ages-iii-rfid-nist` | linha 9 → linha 14 | Manter por ora | A segunda menção acompanha a comunicação do gateway com o leitor físico via API. |

Não se propõe retirar chamadas apenas porque a mesma fonte aparece em seções ou projetos diferentes. Os IDs R02, R05 e R07 indicam os casos em que uma revisão humana pode preferir menos chamadas sem deixar uma nova afirmação sem sustentação.

## Plano anterior à autorização (registro histórico)

1. Decidir C01–C19 por **chave bibliográfica**, comprovando autoria institucional quando esta for a solução; manter consistência entre chamadas repetidas da mesma fonte e a entrada na lista de referências. Se não houver autoria comprovada nem outra base segura, registrar o impasse entre a forma desejada e G4b em vez de apresentar o nome da tecnologia como autor presumido.
2. Tratar R01 como remoção pontual sugerida; revisar R02, R05 e R07 em contexto; conservar os demais enquanto sustentarem explicações distintas. Não remover a referência bibliográfica de uma chave que continua citada em outro ponto.
3. Após autorização específica, comparar os trechos antes/depois, validar chaves e referências, recompilar `build/document/main.pdf` e inspecionar as chamadas renderizadas. A aplicação posterior está registrada no início deste documento; a revisão de conformidade normativa continua pendente.
