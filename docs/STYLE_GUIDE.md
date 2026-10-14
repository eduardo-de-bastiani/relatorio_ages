# Apresentação e LaTeX

## Decisões vigentes

O destino segue ABNT padrão. A Biblioteca PUCRS restrita não constitui requisito. O relatório da Mariah é a métrica de acabamento visual solicitada pelo usuário, mantendo seu conteúdo exclusivo em modo leitura. A implementação concreta de suas escolhas será medida contra as normas aplicáveis; exemplos pessoais não serão copiados.

Preservação textual é obrigatória. Reflexões: borda, fonte igual ao corpo e ambiente divisível entre páginas. Sprints: continuidade, sem `\include`, `\newpage`, `\clearpage` ou quebra equivalente na entrada. Diagramas ausentes: placeholders posteriores, visualmente provisórios. Estes são requisitos do usuário, não alegadas prescrições ABNT.

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

## Padrão de implementação futura

- Corpo A4, tamanho 12 recomendado, margens nominais superior/esquerda 3 cm e inferior/direita 2 cm, espaçamento 1,5, conforme NBR 14724 e suas exceções. Medir PDF; configuração nominal sozinha não prova conformidade.
- Seções primárias podem começar em nova página por `\chapter`; Sprints são subseções via `\input`. Título não deve ficar órfão. Uma quebra natural por falta de espaço não é quebra artificial.
- Manter uma única autoridade de margens, fonte e espaçamento. Somente o mantenedor altera `main.tex`, `util/` ou macros compartilhadas. Não repetir redefinições nos arquivos de unidade.
- A família de fonte deve aproximar o relatório da Mariah e suportar todos os caracteres. A norma não é usada como justificativa fictícia para exigir Helvetica. Testar aspas Unicode, acentos e símbolos no PDF.
- Figuras: identificação acima e indicação de fonte abaixo; `\label` após `\caption`; arquivo original intacto e hash validado. Não inventar autoria nem data de captura. Uma fonte desconhecida permanece pendência.
- Escolher posicionamento pelo tamanho e contexto. `[H]` não é obrigatório nem deve ser copiado mecanicamente; verificar espaços e proximidade da chamada no texto.
- Não converter quadros textuais em tabelas numéricas por aparência. Classificação e orientação IBGE dependem do conteúdo.
- Listas devem representar itens e níveis efetivos, não todos os contêineres ODF. A nesting XML do original chega a dez níveis e não pode ser transcrita literalmente.
- Regenerar sumário, lista de ilustrações e referências cruzadas. Profundidade que inclua Sprints é proposta técnica; aprovação final está pendente.
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
