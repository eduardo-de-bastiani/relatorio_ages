# Apresentação e LaTeX

## Decisões vigentes

O destino segue ABNT padrão. A Biblioteca PUCRS restrita não constitui requisito. O relatório da Mariah é a métrica de acabamento visual solicitada pelo usuário, mantendo seu conteúdo exclusivo em modo leitura. A implementação concreta de suas escolhas será medida contra as normas aplicáveis; exemplos pessoais não serão copiados.

Preservação textual é obrigatória. Reflexões: borda, fonte igual ao corpo e ambiente divisível entre páginas. Sprints: continuidade, sem `\include`, `\newpage`, `\clearpage` ou quebra equivalente na entrada. Diagramas ausentes: placeholders posteriores, visualmente provisórios. Estes são requisitos do usuário, não alegadas prescrições ABNT.

## Padrão visual aprovado para as edições AGES

Em 16/10/2026, o usuário aprovou a apresentação da prévia AGES I identificada em `docs/ages-i/CURRENT_REVIEW.md` e autorizou reutilizar o padrão nas edições seguintes. O registro está em `migration/approvals/ages-i-presentation-accepted.json`. O PDF aprovado como referência visual tinha SHA-256 `e4822c8d8056433af08104b0a9e8edd0f21828350cc9fcb9d2f335ec4a1d0a98`. Isto aprova a apresentação observada e seu uso futuro; não certifica por si só ABNT integral nem resolve fontes de imagens, diagramas ou links pendentes.

Aplicar os seguintes parâmetros, comparados com o PDF da Mariah e medidos no PDF AGES I:

- A4; margens superior/esquerda de 3 cm e inferior/direita de 2 cm; corpo em família Helvetica compatível, 12 pt; avanço entre linhas de aproximadamente 21,669 pt; recuo de primeira linha de aproximadamente 0,62 cm; espaço entre parágrafos `0pt plus 1pt`.
- Títulos de capítulo à esquerda e em negrito; seções no tamanho do corpo, com negrito onde usado na referência; subseções no tamanho do corpo sem negrito. A hierarquia e numeração de cada edição vêm do ODT e devem ser conferidas individualmente.
- Sumário acompanha a profundidade visual da referência (capítulos e seções); Sprints permanecem no corpo e na rastreabilidade, sem iniciar página artificialmente. Quebra natural por falta de espaço continua permitida.
- Links são pretos, em fonte regular e com texto âncora descritivo; repositórios são apresentados em frases corridas, com o nome do repositório clicável. Não usar itálico em links nem em descrições de figuras. Não acrescentar listas com marcadores onde a referência e a decisão aprovada pedem texto corrido.
- Nas seções descritivas de banco de dados, arquitetura e protótipos, apresentar as wikis em frases corridas com âncoras descritivas: “Mais detalhes podem ser encontrados aqui: Banco de Dados”; “Mais informações sobre a arquitetura estão disponíveis em: Arquitetura”; e “Os mockups de cada tela podem ser visualizados no seguinte link: Protótipo das Telas”. Preservar o endereço original de cada wiki. Adaptar singular/plural somente se o destino da seção exigir; não deixar rótulos soltos como “Wiki da Arquitetura”.
- A seção de tecnologias fica em um único parágrafo contínuo, seguindo a organização aprovada na AGES I: tecnologias agrupadas por finalidade, citações autor-data clicáveis diretamente para documentação oficial e entradas bibliográficas correspondentes. Preservar o texto e a ordem da origem; a conversão de itens em uma frase contínua é uma decisão de apresentação aprovada, não uma autorização para resumir ou reescrever.
- Em descrições de banco de dados, arquitetura e protótipos, toda menção nominal a produto, linguagem, framework, ORM, banco de dados ou ferramenta de prototipação deve apontar por citação autor-data clicável para uma entrada bibliográfica verificada. Fazer isso também quando a tecnologia aparecer fora do parágrafo “Tecnologias utilizadas”. Repetir autor/ano em toda chamada no texto quando necessário para identificar a fonte; não repetir a data de acesso na chamada. Termos técnicos genéricos sem fonte específica verificada não recebem atribuição inventada: registrar como pendência quando forem tratados como tecnologia citável.
- Pela NBR 10520:2023, fontes sem autoria/responsabilidade são citadas pelo título: título de uma palavra usa essa palavra sem sinal de supressão; título de várias palavras usa a primeira palavra seguida por `[...]` (com as regras próprias quando começa por artigo ou monossílabo). Usar letras maiúsculas e minúsculas na chamada, não caixa alta automática. Os três pontos que apareciam como `(ANGULAR. . . , 2024)` eram uma saída malformada do estilo local `biblatex-abnt` de 2018: a supressão era aplicada até a títulos de uma palavra e a pontuação/espaçamento ficavam incorretos. A regra foi corrigida em `util/style.tex`; por exemplo, um título de uma palavra agora aparece como `(Angular, 2024)`, enquanto um título maior pode aparecer como `(TypeScript [...], 2024)`. O marcador `[...]` só representa a supressão de parte do título segundo a regra de citação; não é abreviação genérica de nome de tecnologia. Não atribuir autoria para eliminar a supressão sem evidência.
- A chamada autor-data remete à referência completa e pode ser hiperlink para ela. Em cada chamada, o ano acompanha autor/título; a data de acesso não se repete no texto. Para documentos online, a NBR 6023:2025 registra URL e data de acesso na entrada bibliográfica; manter essa informação uma vez na referência de cada documento. A preferência do usuário já registrada para usar 2024 em AGES I/II e 2026 em AGES III/IV é uma convenção de apresentação autorizada para esses memoriais, com datas marcadas na proveniência como atribuídas, e não deve ser descrita como exigência ABNT nem como histórico recuperado.
- Referências repetidas para a mesma entidade/ano, quando exigidas pelas datas atribuídas a edições diferentes, devem exibir seus dados completos, sem substituir autor ou título por traços/linhas de sublinhado. O estilo ABNT local é configurado com `repeatfields=true` para este fim. É uma escolha de clareza alinhada à referência visual do usuário; as entradas continuam separadas quando a data atribuída por edição difere.
- Regra histórica para AGES I/II: o usuário autorizou datas de acesso atribuídas dentro das respectivas janelas de 2024; registrá-las como atribuídas, nunca como histórico recuperado. Regra vigente para AGES III/IV (instrução mais recente de 16/10/2026): não inventar nem retrodatá-las; registrar a data real em que a fonte foi verificada. A chamada pode usar o ano de acesso real conforme a preferência de apresentação anteriormente aprovada, sem declarar que esse é o ano factual de publicação quando a fonte não o informa. Preservar metadados de publicação comprovados; quando faltarem ou a saída bibliográfica não puder distingui-los corretamente, registrar PENDING e pedir decisão. Não inferir versão utilizada no projeto.
- Identificação e título de figura em português (“Figura”), título acima e fonte abaixo; centralizar a imagem e a linha de fonte abaixo da imagem. Manter `\label` após `\caption`. A centralização da fonte é padrão visual aprovado, não uma exigência normativa isolada. A autoria/fonte da imagem é um dado factual: usar “pendente de identificação” até confirmação do usuário. Posicionar cada figura conforme contexto e tamanho, sem aplicar `[H]` a todas.
- Reflexões mantêm borda e fonte/tamanho do corpo, podendo continuar entre páginas. Placeholders de conteúdo ausente são visualmente provisórios, distinguíveis de figuras reais e ausentes da lista de ilustrações.
- Números de página ficam menores que o corpo e uniformes no documento. Espaços pré-textuais e de capítulos são avaliados segundo sua função; remover somente espaços artificiais comprovados.

Estes itens misturam decisões do usuário e medidas de referência. Eles não devem ser descritos como exigências da ABNT. Se uma regra normativa verificada exigir apresentação diferente, registrar o conflito e pedir decisão em vez de alterar silenciosamente o padrão aprovado.

## Fontes normativas e status

| Fonte | Uso | Status e origem |
|---|---|---|
| NBR 14724:2024, versão corrigida 2025 | Apresentação de trabalho acadêmico | Texto acessível: [Prefeitura do Rio](https://vigilanciasanitaria.prefeitura.rio/wp-content/uploads/sites/84/2025/10/ABNT-NBR-14724-2025-informacao-e-documentacao-trabalho-academico.pdf) |
| NBR 6024:2012 | Numeração de seções | [UFSC](https://cnm.paginas.ufsc.br/files/2020/02/ABNT-NBR-6024.pdf) |
| NBR 6027:2012 | Sumário | Texto integral e vigência permanecem pendentes de confirmação |
| NBR 10520:2023 | Citações | [UFOPA](https://ibef.ufopa.edu.br/media/file/site/ibef/documentos/2023/539ca74865f4abf0dc9c181e1124a284.pdf) |
| NBR 6023:2025 | Referências | [FHO](https://www.fho.edu.br/assets/documentos/FHO_Biblioteca_Referencia_ABNT_6023_2025.pdf) |
| NBR 6028:2021 | Resumo | [UFSC](https://presencial.moodle.ufsc.br/mod/resource/view.php?id=351974) |
| IBGE, 3ª edição, 1993 | Tabelas numéricas | [Publicação IBGE](https://biblioteca.ibge.gov.br/visualizacao/livros/liv23907.pdf) |

São fontes institucionais que hospedam textos das normas; não equivalem a confirmação do catálogo oficial da ABNT. Registrar edição, seção e evidência de cada regra. A confirmação final de vigência está pendente e não bloqueia a construção do harness. NBR 10719 não se aplica automaticamente pelo nome “relatório”. Não inventar requisitos da professora.

### Convenções de citação e fonte de figura — atualização 16/10/2026

O usuário pediu a correção nas seções técnicas de AGES I e II e a reutilização desta convenção nas próximas edições. As chamadas sem autoria seguem a NBR 10520:2023, itens 6.1.1.4(a)–(d); nomes de pessoa ou entidade em chamada parentética usam maiúsculas e minúsculas conforme itens 6.1.1.1–6.1.1.3. Para fontes online, a NBR 6023:2025, item 6.6, prevê URL e data de acesso na referência. A Biblioteca Central da PUCRS resume a mudança de caixa em chamadas autor-data em [sua orientação de 2023](https://biblioteca.pucrs.br/noticias/atualizacao-da-norma-de-citacoes-da-abnt-nbr-10520-julho-2023/). A evidência institucional e as limitações de acesso às normas estão em [docs/norms/ABNT_CITATION_EVIDENCE.md](norms/ABNT_CITATION_EVIDENCE.md).

Na composição visual solicitada, toda linha “Fonte:” permanece abaixo da imagem e centralizada dentro da largura do texto. O rótulo de fonte ainda fica “pendente de identificação” enquanto o usuário não confirmar a proveniência. Esses dois parâmetros são uma escolha aprovada do memorial; a NBR 14724 exige a indicação de fonte, mas não deve ser citada como prova de alinhamento centralizado.

## Padrão de implementação futura

- Corpo A4, tamanho 12 recomendado, margens nominais superior/esquerda 3 cm e inferior/direita 2 cm, espaçamento 1,5, conforme NBR 14724 e suas exceções. Medir PDF; configuração nominal sozinha não prova conformidade.
- Seções primárias podem começar em nova página por `\chapter`; Sprints são subseções via `\input`. Título não deve ficar órfão. Uma quebra natural por falta de espaço não é quebra artificial.
- Manter uma única autoridade de margens, fonte e espaçamento. Somente o mantenedor altera `main.tex`, `util/` ou macros compartilhadas. Não repetir redefinições nos arquivos de unidade.
- A família de fonte deve aproximar o relatório da Mariah e suportar todos os caracteres. A norma não é usada como justificativa fictícia para exigir Helvetica. Testar aspas Unicode, acentos e símbolos no PDF.
- Figuras: identificação acima e indicação de fonte abaixo; `\label` após `\caption`; arquivo original intacto e hash validado. Não inventar autoria nem data de captura. Uma fonte desconhecida permanece pendência.
- Escolher posicionamento pelo tamanho e contexto. `[H]` não é obrigatório nem deve ser copiado mecanicamente; verificar espaços e proximidade da chamada no texto.
- Não converter quadros textuais em tabelas numéricas por aparência. Classificação e orientação IBGE dependem do conteúdo.
- Listas devem representar itens e níveis efetivos, não todos os contêineres ODF. A nesting XML do original chega a dez níveis e não pode ser transcrita literalmente.
- Regenerar sumário, lista de ilustrações e referências cruzadas. Para as próximas edições, usar a profundidade 2 da prévia AGES I aprovada, registrando que a Mariah usa profundidade 1.
- Pré-textuais: medir espaços legítimos de composição separadamente dos vazios artificiais. Não copiar capa, epígrafe, autoria ou ano da Mariah.
- Bibliografia: preservar os 36 registros originais; metadados documentados podem ser sugeridos separadamente, sem completar silenciosamente. Datas de acesso ausentes não serão inventadas.
- `abntex2`/`biblatex-abnt` instalados são antigos; validade da saída atual não decorre do nome do pacote. O mantenedor integra eventual ajuste bibliográfico, e a curadoria fornece evidência.
- Remover demonstrações do destino apenas mediante classificação e decisão registradas; o original permanece preservado no manifesto.

## Verificação

No piloto, o título original `2.3.1 Sprint 0 ` é conservado literalmente em subseção sem prefixo automático duplicado; `refstepcounter{subsection}` mantém a referência `2.3.1`, conferida no `.aux`. A entrada do sumário é derivada do mesmo título. A âncora original do ODT permanece via `hypertarget` com argumento visual vazio. Não generalizar esse tratamento sem auditar a numeração de cada título futuro.

Tabs autorais iniciais usam `originaltab`, com distância `1.251cm` documentada no estilo padrão ODF; espaços explícitos de borda usam `originalspace` e o espaço da fonte. O comparador recupera esses tokens exatamente e exige contrato/hash das definições, sem colapsar o texto original. O piloto usa `noindent` nos quatro parágrafos do corpo e cinco da reflexão, evitando contar o tab duas vezes. A reflexão usa família e tamanho do corpo, conforme decisão aprovada; uma borda é redesenhada para cada segmento natural de página. O construtor remove glue de altura do `vsplit` antes de imprimir; somente a badness da caixa temporária, não impressa, tem limiar local elevado. Diagnósticos horizontais e da saída permanecem ativos. A auditoria visual verifica o resultado real.

Figuras, notas, listas autorais, hyperlinks e citações não existem nesta Sprint. Os ambientes reutilizáveis estão definidos, mas nenhuma figura/placeholder é inserido artificialmente para exercitá-los no memorial. O teste sintético das macros e continuidade fica separado do PDF de revisão.

Aplicar [QUALITY_GATES](QUALITY_GATES.md), auditoria independente do texto e inspeção do PDF completo. Registrar cada desvio com arquivo/localização, evidência, consequência, gravidade, proposta e método de verificação. Falta de norma acessível produz PENDING, nunca uma regra inventada.

## Ampliação comprovada para AGES I

O parágrafo `text-p-0473` da Sprint 1 começa com dois `text:tab`. O estilo P124 não declara tabulações próprias; o padrão de `styles.xml` declara distância `1.251cm`. Representar ambos, em sequência, por `originaltab`, sem remover um deles. O validador aceita uma sequência inicial de tabs sob o mesmo contrato e compara sua quantidade exata; tabs internos continuam bloqueados. Teste de regressão inclui perda de um tab e tab interno. Conferir também o recuo efetivamente exibido no PDF; a prova lexical não certifica o layout.

A extração das seções técnicas também identificou tabs internos explícitos em `text-p-0303`, `text-p-0314` e `text-p-0318`. Cada token permanece na mesma posição por `originaltab`, sob contrato e comparação exata; tabs perdidos, deslocados ou substituídos por espaços continuam falhando. A macro representa cada tab por um avanço fixo de 1.251 cm, conforme o passo padrão ODF. Isso não reproduz o alinhamento aos próximos tab stops de um processador ODF: o texto é recomposto em novas linhas no LaTeX. Essa diferença de apresentação exige inspeção visual desses três parágrafos; não implica remoção nem normalização do texto de origem. Esta extensão substitui a restrição anterior a tabs iniciais; não amplia o suporte a quebras explícitas ou macros desconhecidas.
