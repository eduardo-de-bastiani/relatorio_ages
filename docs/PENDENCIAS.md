# Pendências e decisões humanas

## Acordos concluídos

Texto rigorosamente preservado; revisão editorial posterior; Sprints sem início artificial de página; placeholders visuais para diagramas ausentes; aprovação após cada edição; reflexões com borda e mesma fonte do corpo, divisíveis. O usuário dispensou o modelo restrito da Biblioteca PUCRS e definiu Mariah como métrica visual. Em 16/10/2026, aprovou o padrão visual aplicado à prévia AGES I e autorizou reutilizá-lo; os parâmetros estão agora em [STYLE_GUIDE](STYLE_GUIDE.md), vinculados à aprovação em `migration/approvals/ages-i-presentation-accepted.json`. Essa aprovação da apresentação não comprova fontes de imagens nem certificação integral ABNT.

## Pendências para a fase de migração

| ID | Evidência/localização | Consequência e gravidade | Ação proposta / responsável | Verificação |
|---|---|---|---|---|
| P01 | Execução do piloto autorizada pela missão atual; resultado ainda não aprovado | Avanço prematuro para próxima unidade; crítica | Executar somente AGES I / Easy Choose / Sprint 0 e apresentar a revisão ao usuário | Evidência em migration/approvals/pilot-authorization.json; aprovação da entrega permanece pendente |
| P02 | Recorda: Sprints 2–4 e conclusão vazias no ODT | Memorial incompleto; alta | Conservar a lacuna na migração; complementação posterior pelo autor | Manifesto e relatório de ausências |
| P03 | Pré-textuais, trajetória, considerações e apêndices contêm instruções de modelo | Exclusão pode violar preservação; alta | Usuário aprova quais elementos remanescentes saem do destino | IDs excluídos e motivo em ledger |
| P04 | 34 imagens sem fontes explicitamente identificadas na auditoria | Proveniência ausente; alta | Autor fornece origem/autoria; curador registra evidências | Correspondência por ID/hash |
| P05 | 36 referências textuais sem datas de acesso | Metadados bibliográficos incompletos; alta | Preservar estado; autor/curador distingue acesso documentado de acesso novo | Evidência separada para cada dado |
| P06 | Não há diagramas incorporados para banco/arquitetura de AGES I e banco de AGES II | Lacunas gráficas; média | Placeholders na conversão autorizada; materiais reais posteriormente | Não atribuir hash de mídia inexistente |
| P07 | NBR 6027 integral e confirmação de vigência no catálogo ABNT indisponíveis na auditoria | Certificação normativa incompleta; alta | Obter acesso legítimo e verificar; auditor normativo | Fonte, edição e trechos aplicáveis registrados |
| P08 | Pré-textuais e possíveis exigências particulares não definidos integralmente | Estrutura final pendente; média | Confirmar conjunto obrigatório/optional para ABNT padrão e eventuais instruções da professora | Lista aprovada, sem dependência da Biblioteca PUCRS |
| P09 | Nome solicitado `relatorio_AGES_eduardo`; checkout ainda usa `Template_AGES___Guvidaletti` | Mudança de caminho exige integração; média | Aplicar o nome já solicitado na preparação do destino após autorização do piloto; nenhuma nova decisão de nome é necessária | Configuração central e cadeia de inclusão consistentes |
| P10 | Sumário atual do template exclui Sprints | Navegação incompleta para rastreabilidade; média | Recomendar profundidade 2; confirmar no piloto | PDF e correspondência título–sumário |
| P11 | PDF/fontes do template: glifos ausentes; comparativo não recompila offline por cache de fonte | Build de produção ainda sem gate limpo; alta | Mantenedor resolve na etapa autorizada; não instalar silenciosamente | Build limpo e nenhum glifo ausente |
| P12 | Números e pontuação de títulos/legendas digitados no original | Duplicação de números na conversão; média | Separar indicativo gerado e conteúdo, com autorização de equivalência gráfica | Texto exibido e ledger de transformação |
| P13 | Checkpoint específico de Hoortech não expressamente confirmado | Cliente não deve ficar fora da aprovação; média | Recomendar checkpoint adicional; usuário confirma antes da conversão da participação | Registro humano próprio |
| P14 | ODT contém tabs, quebras explícitas e espaços repetidos/em bordas | Colapsar whitespace pode apagar informação; alta | Comparador bloqueia esses registros; definir representação e comprovar equivalência renderizada no piloto | Diff por ID, fonte XML, PDF e aprovação rastreável; sem normalização silenciosa |

As pendências de apresentação/conteúdo não autorizam ação editorial. Bloqueiam a unidade ou gate que delas depende; não a implementação do harness. Material ausente não pode ser convertido em referência ou diagrama presumido.

## Resultado do piloto

A unidade `ages-i-sprint-0` foi convertida e auditada isoladamente. P09 foi atendida com o destino `relatorio_AGES_eduardo/`, mantendo o template original somente para leitura. P10 usa profundidade 2 e registro do título preservado; sua aprovação visual pelo usuário permanece pendente. P11 foi resolvida para os caracteres usados neste piloto, com compilação sem avisos; isso não certifica todas as fontes/símbolos futuros. P12/P14 foram resolvidas para seus dez registros por título literal com contador sincronizado e macros de tabs/espaços verificadas, sem normalização da fonte. Não generalizar o resultado para as demais unidades. Os pareceres e pendências específicas estão em [pilot/PILOT_REVIEW.md](pilot/PILOT_REVIEW.md).

Execução autorizada não equivale a aprovação do resultado. Não iniciar a próxima Sprint sem mensagem explícita do usuário.

## Como registrar nova pendência

Adicionar ID estável, elemento/arquivo afetado, evidência concreta, impacto, gravidade, responsável, decisão necessária e método de verificação. Resolvido exige evidência e data; não apagar o histórico da decisão.

## Execução anterior da AGES I

O usuário autorizou a edição completa AGES I / Easy Choose e os dois placeholders provisórios. A aprovação da apresentação visual da prévia de 18 páginas e a autorização de prosseguir para AGES II estão registradas em `migration/approvals/ages-i-presentation-accepted.json` e `migration/approvals/ages-ii-authorization.json`. Fontes das figuras, diagramas reais, disponibilidade remota de links e confirmação normativa continuam pendentes. O PDF identificado na aprovação e o escopo do aceite estão detalhados em `docs/ages-i/CURRENT_REVIEW.md`.

| ID | Localização e evidência | Consequência / gravidade | Ação e verificação | Estado |
|---|---|---|---|---|
| AI01 | Banco de dados, text-h-0009: nenhum diagrama incorporado | Material gráfico ausente; média | Placeholder provisório `ages-i-database`; autor fornecerá material; conferir que não entra na lista de figuras reais | PENDING |
| AI02 | Arquitetura, text-h-0010: nenhum diagrama incorporado | Material gráfico ausente; média | Placeholder provisório `ages-i-architecture`; autor fornecerá material; conferir que não entra na lista de figuras reais | PENDING |
| AI03 | Cinco imagens draw-image-0001–0005 sem indicação explícita de autoria/fonte | Proveniência incompleta; alta | Preservar bytes e apresentar fonte pendente; autor identifica origem, curador verifica | PENDING |
| AI04 | Seis links originais tools.ages.pucrs.br sem acesso atual comprovado; curadoria em migration/evidence/references/ages-i.json | Disponibilidade incerta; média | Usuário autorizou manter URLs literalmente e continuar; conferir 11 âncoras/URLs no total, repetir teste remoto posteriormente | PENDING, execução autorizada |
| AI05 | Cinco documentações tecnológicas consultadas em 14/10/2026 | Consulta atual não comprova versão ou data histórica; média | Aparato bibliográfico separado com título/URL/data comprovados; nenhuma referência nova dentro da narrativa | Verificação documental concluída; revisão humana PENDING |
| AI06 | Vigência integral e regras ainda pendentes em P07/P08 | Certificação normativa integral indisponível; alta | Não declarar conformidade normativa total; manter matriz de evidências e revisão posterior | PENDING |

O aceite do resultado deverá identificar PDF, commit e relatórios da edição. A autorização de continuidade dos links não comprova sua disponibilidade nem autoriza completar diagramas ou fontes por inferência.

### Ressalvas da entrega AGES I

- **AI07 / VAI03 — RESOLVIDA neste candidato, média:** nove tabs internos em `text-p-0303`, `text-p-0314` e `text-p-0318` continuam rastreados no ODF/manifesto e são exibidos como espaços normais de composição, decisão de apresentação autorizada pelo usuário. Comparação de conteúdo passou; PDF atual e reauditoria visual estão identificados em `ages-i/POST_FORMAT_REVIEW.md`. Esta resolução é apenas desta AGES I e não é regra permanente para outras edições sem aprovação posterior.
- **AI08 — aceite de avanço registrado:** as 15 unidades passaram pelos gates técnicos; o usuário aprovou a apresentação da prévia identificada e autorizou a AGES II, mantendo explícitas as pendências factuais/normativas acima. Esse aceite não substitui a identificação manual das fontes nem a futura aprovação da edição integrada.

Os achados CA-01 (itálico), VAI01 (floats fora de contexto) e VAI02 (página quase vazia) foram corrigidos e reavaliados; histórico e evidências estão nos pareceres da edição.

### Correção solicitada após revisão humana da AGES I

A proposta histórica de 17 páginas e a revisão de 19 páginas foram sucedidas pela alteração do parágrafo de tecnologias. A prévia atual tem 18 páginas e SHA-256 `e4822c8d8056433af08104b0a9e8edd0f21828350cc9fcb9d2f335ec4a1d0a98`; a compilação e os testes técnicos passaram. O usuário aprovou sua apresentação e autorizou reutilizar o padrão. Fontes de imagens, diagramas reais e conformidade normativa integral continuam **PENDING**. Consulte [a revisão atual](ages-i/CURRENT_REVIEW.md); os relatórios `POST_FORMAT` preservam avaliações históricas de PDFs anteriores.

### Preferência de formatação da Mariah

O usuário aprovou a apresentação da prévia e pediu que o padrão da Mariah seja aplicado às próximas edições. As cinco tecnologias da AGES I aparecem em um parágrafo com citações autor-data, links e referências; 2024 e 10/04/2024 foram atribuídos por instrução explícita, não recuperados de histórico de navegação. A regra reutilizável e suas limitações constam do [STYLE_GUIDE](STYLE_GUIDE.md). A autorização ativa agora é somente AGES II, registrada em `migration/approvals/ages-ii-authorization.json`.

## Execução autorizada da AGES II

O usuário autorizou migrar somente AGES II / Indústria Digital, capítulo 4 do ODT, em 15 unidades listadas em `harness.json`. A autorização está em `migration/approvals/ages-ii-authorization.json`. Sete imagens estão incorporadas e recebem fonte pendente até identificação; o diagrama de banco de dados ausente recebe placeholder provisório. Os links originais serão preservados sem alterações; a disponibilidade remota será registrada separadamente. Para referências tecnológicas, usar 2024 e uma data de acesso atribuída dentro da janela agosto–novembro de 2024, conforme instrução prévia do usuário, e manter essa proveniência explícita.

| ID | Localização e evidência | Consequência / gravidade | Ação e verificação | Estado |
|---|---|---|---|---|
| AII01 | `chapter-04-text-h-0046`, `text-a-0126`: https://developers.facebook.com/docs/graph-api/guides/explorer/; a página oficial não foi acessível na auditoria de 16/10/2026 | Metadados bibliográficos atuais não confirmados; média | Por decisão explícita do usuário, preservar URL e âncora originais e continuar a edição. Não inferir/substituir metadados nem criar entrada bibliográfica até haver evidência; conferir URL textual/hash e presença da pendência no relatório | PENDING, continuação autorizada em `migration/approvals/ages-ii-reference-decision.json` |
| AII02 | `chapter-04-text-h-0043`, `text-h-0043`: o ODT não incorpora o diagrama do banco de dados | Lacuna gráfica no capítulo; média | Inserir somente o placeholder provisório autorizado `ages-ii-database`; o usuário fornecerá o diagrama posteriormente; validar que fique fora da lista de figuras reais | PENDING, placeholder autorizado em `migration/approvals/ages-ii-authorization.json` |
| AII03 | `chapter-04-text-h-0046`, `text-a-0126` e `text-p-0839`: Graph API permanece sem metadados verificáveis; “Documentação Docker” não tem hyperlink no ODT | Duas referências sem entrada bibliográfica sustentada; média | Preservar literalmente o link Graph API; manter o rótulo Docker sem URL nova; não criar entradas até evidência válida; conferir no relatório da curadoria e no LaTeX | PENDING, decisão Graph em `migration/approvals/ages-ii-reference-decision.json`; Docker em `migration/evidence/references/ages-ii.json` |
