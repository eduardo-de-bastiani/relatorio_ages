# Pendências e decisões humanas

## Acordos concluídos

Texto rigorosamente preservado; revisão editorial posterior; Sprints sem início artificial de página; placeholders visuais para diagramas ausentes; aprovação após cada edição; reflexões com borda e mesma fonte do corpo, divisíveis. O usuário dispensou o modelo restrito da Biblioteca PUCRS e definiu Mariah como métrica visual. Não reabrir essas decisões sem novo motivo ou instrução.

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

## Execução autorizada da AGES I

O usuário autorizou a edição completa AGES I / Easy Choose e os dois placeholders provisórios. Esse escopo substitui o limite histórico P01; aprovação do resultado permanece PENDING. Outras edições e Hoortech não estão autorizadas. Registro: `migration/approvals/ages-i-authorization.json`.

| ID | Localização e evidência | Consequência / gravidade | Ação e verificação | Estado |
|---|---|---|---|---|
| AI01 | Banco de dados, text-h-0009: nenhum diagrama incorporado | Material gráfico ausente; média | Placeholder provisório `ages-i-database`; autor fornecerá material; conferir que não entra na lista de figuras reais | PENDING |
| AI02 | Arquitetura, text-h-0010: nenhum diagrama incorporado | Material gráfico ausente; média | Placeholder provisório `ages-i-architecture`; autor fornecerá material; conferir que não entra na lista de figuras reais | PENDING |
| AI03 | Cinco imagens draw-image-0001–0005 sem indicação explícita de autoria/fonte | Proveniência incompleta; alta | Preservar bytes e apresentar fonte pendente; autor identifica origem, curador verifica | PENDING |
| AI04 | Seis links originais tools.ages.pucrs.br sem acesso atual comprovado; curadoria em migration/evidence/references/ages-i.json | Disponibilidade incerta; média | Usuário autorizou manter URLs literalmente e continuar; conferir 11 âncoras/URLs no total, repetir teste remoto posteriormente | PENDING, execução autorizada |
| AI05 | Cinco documentações tecnológicas consultadas em 14/10/2026 | Consulta atual não comprova versão ou data histórica; média | Aparato bibliográfico separado com título/URL/data comprovados; nenhuma referência nova dentro da narrativa | Verificação documental concluída; revisão humana PENDING |
| AI06 | Vigência integral e regras ainda pendentes em P07/P08 | Certificação normativa integral indisponível; alta | Não declarar conformidade normativa total; manter matriz de evidências e revisão posterior | PENDING |

O aceite do resultado deverá identificar PDF, commit e relatórios da edição. A autorização de continuidade dos links não comprova sua disponibilidade nem autoriza completar diagramas ou fontes por inferência.
