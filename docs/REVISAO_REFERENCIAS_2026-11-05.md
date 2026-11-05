# Revisão de referências por documento — 05/11/2026

Revisão local do arquivo `relatorio_AGES_eduardo/bibliografia/bibliografia.bib` e dos usos nos arquivos LaTeX, sem acessar os links. O critério pedido pelo autor é consolidar referências à mesma página e preservar fontes que apontam para páginas ou serviços diferentes e contribuam para afirmações diferentes. As 55 entradas existentes são citadas ou incluídas por `\nocite`.

## Candidatas por URL igual

A comparação desconsiderou somente uma barra final no endereço, sem testar equivalência remota, redirecionamentos ou conteúdo histórico. Para cada grupo, recomenda-se uma entrada, depois de conferir metadados e redirecionar todas as citações:

| Página | Entradas existentes | Proposta | Redução |
|---|---|---|---:|
| TypeScript: `/docs/` | `typescript-docs`, `ages-iv-typescript` | Manter `typescript-docs`, como preferido pelo autor; trocar as citações da entrada IV. O título, a autoria e a data registrados diferem, exigindo revisão dos metadados. | 1 |
| React: `react.dev/` | `react-docs`, `ages-iii-react` | Unificar; a escolha da entrada final depende de reconciliar os autores, títulos e datas que hoje divergem. | 1 |
| PostgreSQL: `/docs/` | `postgresql-docs`, `ages-ii-postgresql`, `ages-iv-postgresql` | Unificar as três; conferir a autoria corporativa e as datas divergentes antes de escolher os metadados. | 2 |
| Figma: página inicial | `ages-i-figma`, `ages-ii-figma` | Manter `ages-i-figma` e redirecionar AGES II; títulos e autoria coincidem, datas de acesso atribuídas diferem. | 1 |
| Docker: página inicial | `ages-ii-docker`, `ages-iii-docker` | Candidata à unificação, com cuidado: os títulos e as datas registradas diferem; o título de 2026 menciona sandboxes de IA e não demonstra, por si só, pertinência à explicação de contêineres. Conferir qual identificação deve ficar. | 1 |

Esses cinco grupos reúnem **11 entradas em cinco referências**, reduzindo **6 entradas** se todas as unificações forem confirmadas: 55 → 49. A mesma URL pode ter conteúdo atualizado entre datas; a inspeção local não prova que duas versões históricas eram idênticas. As divergências de metadados e a pertinência das fontes continuam pendentes de revisão.

## Páginas ou serviços diferentes a preservar

- **TypeScript:** além da documentação principal, preservar por ora `ages-ii-typescript` (guia para programadores JavaScript) e `ages-iii-typescript` (página inicial). São URLs diferentes; a preferência anterior por somente uma entrada pode ser revista à luz do critério mais recente do usuário e das funções das páginas.
- **Figma:** preservar `ages-iii-figma`, guia específico de prototipação, separado da página inicial.
- **Docker:** preservar `ages-iv-docker`, Docker Docs, separado da página inicial.
- **PostgreSQL:** preservar `ages-iii-postgresql`, página inicial, separado da documentação.
- **React Native:** preservar `ages-iv-react-native` separado de React; trata-se de produto/documentação diferentes.
- **Python, FastAPI e GitHub Actions:** preservar as duas entradas de cada grupo, pois apontam para páginas diferentes (documentação/página principal, tutorial ou página de produto). O título “Documentação Python 3.15.0” em entrada com ano de 2024 merece revisão; não comprova a versão usada no projeto.
- **AWS:** preservar referências distintas para Lambda, S3, CloudFront, RDS e IoT Core; são serviços diferentes.

Preservar URLs diferentes nesta revisão é uma recomendação conservadora: ainda é preciso examinar o contexto de cada citação e o conteúdo efetivo das fontes para decidir se ambas são necessárias. Não se abre mão de fontes específicas apenas por terem o mesmo fornecedor.

## Consequências e execução futura

As datas de AGES I/II foram atribuídas por convenção autorizada, não recuperadas do histórico de navegação. A unificação de uma mesma URL pode mudar o autor ou ano exibido em uma edição; por exemplo, manter `typescript-docs` fará sua chamada na AGES IV exibir 2024. O ano da chamada e a data de acesso não comprovam a versão histórica da página ou do software. Os endereços não foram acessados, e não se fez nova verificação de autoria, conteúdo ou disponibilidade.

Nenhuma entrada foi removida nesta revisão. Ao implementar uma consolidação: registrar as chaves e metadados antigos como histórico; escolher uma entrada por grupo; remapear cada `\cite` e verificar `\nocite`; confirmar que nenhuma chave ficou órfã; recompilar e conferir citações, bibliografia e auditorias. A validação antiga pode exigir ajuste explícito para reconhecer a alteração autorizada.

## Critério de data mais recente — atualização de 05/11/2026

O autor determinou que, quando a **mesma página** for citada em mais de um projeto e suas entradas forem consolidadas, a referência resultante use a data de acesso mais recente registrada entre elas. Esse critério substitui as propostas de manter datas mais antigas nesta revisão. Páginas diferentes continuam separadas. A análise a seguir não acessou os links e não alterou o `.bib` nem as citações.

| Página | Acessos registrados | Data a manter para a entrada consolidada | Chaves candidatas à remoção, depois de remapear citações |
|---|---|---|---|
| TypeScript `/docs/` | `typescript-docs`: 10/04/2024; `ages-iv-typescript`: 17/10/2026 | **17/10/2026**. É possível conservar a chave e o título `typescript-docs` preferidos pelo autor e atualizar seu `urldate`; `ages-iv-typescript` tem título e autoria diferentes, que devem ser reconciliados. | `ages-iv-typescript` |
| React `react.dev/` | `react-docs`: 10/04/2024; `ages-iii-react`: 16/10/2026 | **16/10/2026**. A entrada de III registra `Meta Platforms, Inc.` e a de I registra `React`; escolher autoria/título com base na evidência existente, sem supor equivalência. | Uma das duas; por exemplo, `react-docs` se escolhida a entrada de III. Atualizar também o `\nocite` em `main.tex`. |
| PostgreSQL `/docs/` | `postgresql-docs`: 10/04/2024; `ages-ii-postgresql`: 15/10/2024; `ages-iv-postgresql`: 17/10/2026 | **17/10/2026**. A entrada de IV já possui essa data; reconciliar nome da entidade e título antes da escolha final. | Duas das três; por exemplo, `postgresql-docs` e `ages-ii-postgresql` se escolhida a entrada de IV. Atualizar o `\nocite` de `postgresql-docs`. |
| Figma, página inicial | `ages-i-figma`: 10/04/2024; `ages-ii-figma`: 15/10/2024 | **15/10/2024**. Mantendo `ages-i-figma`, atualizar seu `urldate` para a data mais recente e remapear as citações de II. | `ages-ii-figma` |
| Docker, página inicial | `ages-ii-docker`: 15/10/2024; `ages-iii-docker`: 16/10/2026 | **16/10/2026**. Escolher uma entrada e reconciliar seus títulos divergentes; o título de 2026 sobre sandboxes de IA não demonstra automaticamente pertinência às citações de contêineres. | Uma das duas após decidir os metadados, por exemplo `ages-ii-docker` se escolhida a entrada III. |

São **seis entradas removíveis como duplicatas**, condicionadas ao remapeamento e à revisão indicados: 55 → 49. Não se muda a data de acesso de uma página apenas porque outra página da mesma tecnologia é citada em um projeto posterior. Assim, os guias e páginas distintos de TypeScript, Figma, Docker, PostgreSQL, Python, FastAPI, GitHub Actions e os serviços AWS continuam com suas próprias datas e referências.

O campo `urldate` é uma data de acesso, não comprova a data de publicação. A configuração atual em `relatorio_AGES_eduardo/util/style.tex` usa `urldate` como primeira opção para o ano da citação; por isso, ao manter uma única entrada com acesso em 2026, também poderá aparecer **2026 nas chamadas dos projetos de 2024**. O campo `year` de entradas anteriores não deve ser alterado ou apresentado como ano factual de publicação sem evidência. Datas atribuídas pelo usuário permanecem identificadas como atribuídas; as de curadoria já registradas em 2026 não se tornam fictícias por serem reutilizadas.

A inspeção local não mostra acesso posterior além das datas acima. A mesma URL pode ter mudado de conteúdo entre acessos; a comparação dos campos não prova identidade das versões. Para executar a limpeza posteriormente, atualizar citações e `\nocite`, preservar os metadados anteriores na rastreabilidade e validar a bibliografia e o PDF. Nenhuma remoção ou mudança de data foi aplicada nesta análise.
