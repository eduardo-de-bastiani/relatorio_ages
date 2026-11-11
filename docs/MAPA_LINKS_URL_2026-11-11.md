# Mapa de links com rótulo para apresentação como URL — 11/11/2026

## Aplicação autorizada em 11/11/2026

Os **20 links desta tabela foram convertidos para URLs completas visíveis e clicáveis**, preservando todos os destinos: seis na AGES I, cinco na AGES II, quatro na AGES III e cinco na AGES IV. Nas dez chamadas de repositório, a frase passou a “Mais informações podem ser encontradas em:”; as demais frases foram preservadas. O suplemento `migration/approvals/url-presentation-2026-11-11.json` e os 14 ledgers mantêm os IDs, textos anteriores/posteriores e hashes. Os dois `\href` vazios da AGES IV passaram a comentários com seus IDs e destinos; a âncora vazia de AGES II foi preservada. Nenhum destino foi acessado. Não há link com rótulo visível na participação Cliente Hoortech.

Os caminhos da tabela são relativos a `relatorio_AGES_eduardo/conteudo/migracao/`; as linhas e os rótulos registram o **inventário anterior à aplicação**. A implementação usa `\url{destino}`, sem aninhar links. `%` e `_` dentro desses novos comandos são preservados pelo leitor de URL do LaTeX. A configuração permite quebra após hífens existentes; somente a chamada longa do banco de dados da AGES III usa alinhamento local à esquerda para evitar justificação inadequada. O corpo narrativo continua com sua composição anterior.

PDF final de revisão: `build/document/main.pdf`, SHA-256 `3a71ba163dfd72c03b8cc928e255a36e81c6bdc71e0f649386b8883e97d3adf4`. `./build.sh --profile document-review` retornou zero com `status: pass` e `findings: []`; ver também `docs/DIAGNOSTICO_BUILD_2026-11-11.md`. A aprovação humana do resultado continua pendente.

| ID ODT / parágrafo | Edição e tópico | Arquivo:linha anterior | Rótulo substituído | URL exibida |
|---|---|---|---|---|
| `text-a-0105` / `text-p-0304` | AGES I, repositório | `chapter-02-text-h-0008.tex:6` | Easy Choose Admin | `https://tools.ages.pucrs.br/easy-choose/easychooseadmin` |
| `text-a-0106` / `text-p-0307` | AGES I, repositório | `chapter-02-text-h-0008.tex:8` | Easy Choose Store | `https://tools.ages.pucrs.br/easy-choose/easychoosevarejista` |
| `text-a-0107` / `text-p-0310` | AGES I, repositório | `chapter-02-text-h-0008.tex:10` | Easy Choose API | `https://tools.ages.pucrs.br/easy-choose/easychooseapi` |
| `text-a-0108` / `text-p-0315` | AGES I, banco de dados | `chapter-02-text-h-0009.tex:8` | Banco de Dados | `https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/Banco%20de%20Dados` |
| `text-a-0109` / `text-p-0319` | AGES I, arquitetura | `chapter-02-text-h-0010.tex:8` | Arquitetura | `https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/arquitetura` |
| `text-a-0110` / `text-p-0323` | AGES I, protótipos | `chapter-02-text-h-0011.tex:8` | Protótipo das Telas | `https://tools.ages.pucrs.br/easy-choose/wiki/-/wikis/design_mockups` |
| `text-a-0116` / `text-p-0775` | AGES II, repositório | `chapter-04-text-h-0042.tex:12` | Indústria Digital Frontend | `https://tools.ages.pucrs.br/industria-digital/industria-digital-frontend` |
| `text-a-0117` / `text-p-0778` | AGES II, repositório | `chapter-04-text-h-0042.tex:18` | Indústria Digital Backend | `https://tools.ages.pucrs.br/industria-digital/industria-digital-backend` |
| `text-a-0118` / `text-p-0782` | AGES II, banco de dados | `chapter-04-text-h-0043.tex:10` | Banco de Dados | `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Banco%20de%20dados` |
| `text-a-0120` / `text-p-0789` | AGES II, arquitetura | `chapter-04-text-h-0044.tex:15` | Arquitetura | `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Arquitetura` |
| `text-a-0121` / `text-p-0793` | AGES II, protótipos | `chapter-04-text-h-0045.tex:10` | Protótipo das Telas | `https://tools.ages.pucrs.br/industria-digital/wiki/-/wikis/Mockups` |
| `text-a-0129` / `text-p-1030` | AGES III, repositório | `chapter-05-text-h-0077.tex:12` | RFID Frontend | `https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/frontend` |
| `text-a-0130` / `text-p-1033` | AGES III, repositório | `chapter-05-text-h-0077.tex:18` | RFID Backend | `https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/backend` |
| `text-a-0131` / `text-p-1036` | AGES III, repositório | `chapter-05-text-h-0077.tex:24` | RFID Gateway | `https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/gateway` |
| `text-a-0132` / `text-p-1043` | AGES III, banco de dados | `chapter-05-text-h-0078.tex:16` | Banco de Dados | `https://tools.ages.pucrs.br/sistema-de-controle-inteligente-de-estacionamento-com-rfid/impinj-rfid-wiki/-/wikis/Banco%20de%20Dados` |
| `text-a-0146` / `text-p-1333` | AGES IV, repositório | `chapter-06-text-h-0108.tex:12` | Recorda Frontend | `https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/frontend` |
| `text-a-0147` / `text-p-1336` | AGES IV, repositório | `chapter-06-text-h-0108.tex:18` | Recorda Backend | `https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/backend` |
| `text-a-0149` / `text-p-1343` | AGES IV, banco de dados | `chapter-06-text-h-0109.tex:18` | Banco de Dados | `https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/Banco%20de%20Dados` |
| `text-a-0151` / `text-p-1362` | AGES IV, arquitetura | `chapter-06-text-h-0110.tex:18` | Arquitetura | `https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/arquitetura` |
| `text-a-0152` / `text-p-1393` | AGES IV, protótipos | `chapter-06-text-h-0112.tex:21` | Protótipo das Telas | `https://tools.ages.pucrs.br/2026-2/2jk-4jk/recorda/wiki/-/wikis/design_mockups` |

### Registro anterior dos links vazios e itens já em formato de URL

As duas âncoras vazias AGES IV descritas abaixo já foram convertidas em comentários/ledger pela execução autorizada; a ocorrência AGES II permanece.

- `text-a-0119`, `chapter-04-text-h-0044.tex:9`: `\href` com `\mbox{}` vazio; não é um rótulo visível. O link da arquitetura de AGES II com texto está em `text-a-0120`.
- `text-a-0148`, `chapter-06-text-h-0109.tex:12`: `\href` de corpo vazio; o link visível de banco da AGES IV está em `text-a-0149`.
- `text-a-0150`, `chapter-06-text-h-0110.tex:12`: `\href` de corpo vazio; o link visível de arquitetura da AGES IV está em `text-a-0151`. Os dois últimos geram os avisos `hyperref` documentados em `build/document/main.log`; a correção dos avisos é tarefa separada de remover rótulos.
- AGES III, tópicos 4.2.3 e 4.2.4, já têm URLs visíveis nas **fontes das figuras** e não apresentam `\href` rotulado nem frase final de link no corpo. Nenhuma URL de fonte de figura foi incluída como candidato de troca. Se o objetivo for acrescentar uma URL também ao fim desses tópicos, isso é uma **adição de conteúdo/apresentação separada**, não uma substituição de rótulo existente.

### Divergências que exigem atenção na execução

1. O exemplo fornecido pelo usuário para o Banco de Dados da **AGES II** repete a URL de Arquitetura. O destino real de `text-a-0118` é `.../Banco%20de%20dados`; `text-a-0120` aponta para `.../Arquitetura`. Preservar cada destino próprio, salvo nova decisão explícita.
2. O rótulo “Easy Choose Store” (`text-a-0106`) aponta para o caminho `easychoosevarejista`. Não inferir uma URL diferente a partir do rótulo.
3. O link de Banco de Dados da AGES I (`text-a-0108`) usa `Banco%20de%20Dados`, enquanto a fonte da Figura 2 usa `Banco-de-Dados`. O mapa conserva o destino do **link do corpo**; reconciliar os dois endereços exigiria verificação separada.
4. O link visível de Arquitetura da AGES IV (`text-a-0151`) usa `/arquitetura`, enquanto a fonte da Figura 26 usa `/infraestrutura`. São URLs distintas no documento; não substituí-las automaticamente uma pela outra.

**Estado de execução:** os 20 IDs foram aplicados e rastreados; destinos idênticos aos do inventário. Revisar humanamente legibilidade e composição do PDF final antes de aprovar a apresentação global.

### Verificação executada

- As 14 unidades passaram em `migration.py validate`, com 22 registros de transformação (20 URLs visíveis e dois links vazios), sem erros. As suítes `tests.test_preservation` e `tests.test_url_reconciliation` passaram juntas: 116 testes, retorno zero; os casos adversariais rejeitam mudança de destino, contrato, bytes de destino e alinhamento fora do escopo.
- Auditor Terra Medium independente confirmou nas fontes os 20 destinos e a preservação de citações/figuras. No PDF final encontrou anotações URI para todos os destinos e verificou visualmente as páginas 7, 12, 55 e 57: URLs longas legíveis dentro das margens e números de três dígitos alinhados. Os segmentos anotados examinados ficaram entre x=85,039 e 538,584 pt na folha A4 de largura 595,28 pt.
- O build final não registra `OVERFULL`, `UNDERFULL` ou avisos `hyperref`. A inspeção visual foi pontual, não uma auditoria das 116 páginas; não houve acesso remoto aos destinos. O ODT conserva seu SHA-256 imutável.
- `audit-latex` terminou em PASS. Seu leitor conservador emite quatro alertas para `%` literal dentro de `\url` e o alerta já existente da macro de citação; os quatro URLs percent-encoded foram verificados no compilador e nas URIs do PDF, sem alteração de destino. Esses alertas estáticos não são avisos do log de compilação.
