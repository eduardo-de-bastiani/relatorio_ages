# Reauditoria das correções de formatação — AGES I e II

Data: 16/10/2026  
Branch: `migration/ages-ii`  
Commit-base do worktree: `339bba68563f739e622246cb3167c8a2532176bf` (worktree modificado; os hashes abaixo identificam o candidato real)  
ODT: `RELATORIO_ATUAL.odt`, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`  
PDF de revisão atual: `build/document/main.pdf`, SHA-256 `b1b914c5ca16815ab5753795ea297cabbe5d49099594884266829126bbe2fa61`, 41 páginas A4.

Este relatório reavalia as correções autorizadas pelo usuário em sete unidades técnicas: banco de dados, arquitetura e protótipos da AGES I; banco de dados, arquitetura, protótipos e tecnologias da AGES II. Também verifica as regras globais compartilhadas de citações e figuras. Não autoriza começar AGES III, AGES IV ou Cliente Hoortech. O PDF é uma compilação de revisão; o gate de documento oficial não foi executado e a aprovação humana continua pendente.

## Resultado das alterações

- As seis frases visíveis de links de wiki agora seguem os padrões descritivos aprovados pelo usuário, mantendo seus endereços originais. A extração independente também encontrou uma sétima âncora de arquitetura vazia na origem de AGES II; ela permanece como destino vazio rastreado porque é uma anotação real do ODT, não um link visível omitido.
- As linhas `Fonte:` das Figuras 1–5 e 9–15 aparecem centralizadas abaixo das imagens. As fontes continuam declaradas como pendentes de identificação, sem atribuição inferida.
- A auditoria independente confirmou 37 chamadas bibliográficas ligadas a entradas existentes: quatro em AGES I e 33 em AGES II. As chamadas repetem autor/título e ano sempre que necessário. A data de acesso fica uma vez na entrada da referência online; não é repetida nas chamadas autor-data.
- O marcador de supressão em citações sem autoria foi corrigido: títulos de uma palavra não recebem reticências; títulos com várias palavras usam a forma `[...]` prevista para a supressão do título. Os antigos resultados como `(ANGULAR. . . , 2024)` eram uma saída malformada do estilo local antigo, não a pontuação correta. Para nomes de autor/entidade, foi removida a caixa alta forçada pelo pacote antigo.
- A opção `repeatfields=true` foi confirmada no `abnt.bbx` v3.4 (2018) fornecido pelo bundle local. Ela impede que autoria e título repetidos sejam substituídos por traços/sublinhados. A configuração alterada está em `relatorio_AGES_eduardo/util/style.tex`.
- As regras reutilizáveis estão registradas em `docs/STYLE_GUIDE.md` e `docs/QUALITY_GATES.md`. As datas de acesso de 2024 para AGES I/II continuam identificadas como convenção atribuída por instrução do usuário, não como histórico recuperado nem exigência da ABNT.

## Integridade e revisão independente

| Verificação | Resultado | Evidência / limite |
|---|---|---|
| Integridade do ODT | PASS | Hash atual igual ao hash congelado no harness; `verify-source` passou. Nenhuma edição do ODT. |
| Conteúdo das sete unidades | PASS, com pendências bibliográficas abaixo | Auditor de conteúdo releu diretamente `content.xml` e os destinos, sem usar o relato do conversor como prova. Todas as unidades validadas tiveram 100% de registros textuais correspondentes; não encontrou narrativa de outro projeto nem conteúdo inventado. As únicas diferenças de apresentação são as autorizadas: frases para as wikis, aparato de citações, legendas padronizadas e placeholders autorizados. |
| Links e citações | PASS estrutural | As URLs originais das wikis/repositórios foram preservadas; 37 chaves de citação existem e têm destinos internos no PDF. Isso não prova que os sites externos estejam ativos ou que todas as fontes sejam adequadas ao enunciado. |
| Compilação de revisão | PASS, com aviso | Tectonic e Biber terminaram com código 0; PDF tem 41 páginas. Há um `Overfull \hbox` de 4.74695 pt (aprox. 1,67 mm) em `chapter-04-text-h-0043.tex:8`; deve ser avaliado visualmente, sem reescrever o conteúdo. O gate de documento oficial permanece `NOT_RUN`, pois o perfil é `document-review`. |
| Testes automatizados | PASS | `python3 -m unittest discover -s tests -q`: 113 testes passaram. Os sete `migration.py validate` desta autorização passaram. `verify-source` passou. `audit-latex` passou com um aviso do analisador estático, que não resolve deterministicamente a macro customizada `\memorial@citefirstword`; a compilação real confirmou a execução TeX. |
| Revisão visual independente | PASS com itens PENDING | O auditor inspecionou as 41 páginas renderizadas. Não encontrou corte de texto corrido, páginas inteiramente vazias, títulos de Sprint isolados nem quebras artificiais de Sprint. Reflexões e placeholders permanecem legíveis e identificados. Conferiu visualmente a centralização das fontes das figuras indicadas acima. |
| Aprovação humana da edição | PENDING | O PDF e os relatórios ainda precisam de revisão do usuário. Nenhuma aprovação foi inferida. |

Ferramentas verificadas: Tectonic 0.17.0, Biber 2.17, Python 3.12.8 e Poppler `pdftotext` 26.01.0. O bundle local fornece `biblatex-abnt` v3.4; sua idade é registrada e a configuração foi validada contra o arquivo de estilo efetivamente instalado. `pytest` não está instalado; não foi instalado, pois `unittest` cobre a suíte existente.

## Pendências abertas

| ID | Evidência e efeito | Estado / ação necessária |
|---|---|---|
| AI09 | A menção `Router-Controller-Service-Repository` não tem uma fonte encontrada que documente diretamente o padrão combinado. | PENDING. Manter sem referência inventada; o usuário pode fornecer uma fonte ou decidir como tratar essa menção. |
| AII10 | O link original de Graph API Explorer aponta para `/guides/explorer/`, enquanto a citação bibliográfica aponta à página geral `/docs/graph-api/`. | PENDING. Curador deve comprovar título, responsabilidade e correspondência da fonte antes de qualquer troca. URL original permanece preservada. |
| AII11 | A entrada “Documentação Python 3.15.0” usa uma URL geral `/pt-br/3/`; a versão realmente usada no projeto não está estabelecida. | PENDING. Confirmar a versão ou aceitar referência sem atribuição de versão; não inferir. |
| AII12 | A referência Docker existente aponta para `https://www.docker.com/`; a página inicial não comprova, sozinha, a documentação técnica sobre ambiente local de testes. | PENDING. Identificar uma fonte apropriada ou obter decisão do usuário; não substituir por URL presumida. |
| AI03 / AII05 | As fontes/autorias das imagens ainda não foram identificadas manualmente. | PENDING. Usuário identifica as fontes; manter os rótulos provisórios até confirmação. |
| AI10 | A Figura 4 termina durante a última linha de produtos na página 7. | RESOLVIDO. Conferi `relatorio_AGES_eduardo/imagens/original/asset-0026.png`: a própria captura termina cortada na borda inferior. O PDF preserva o asset sem corte adicional; não alterei a imagem. |
| AII08 | Os rótulos da Figura 10 são pequenos na escala da página e a legibilidade impressa não foi confirmada. | PENDING. Revisão humana da impressão ou decisão sobre disposição, sem reconstrução do diagrama. |
| AII13 | A página 2 contém só duas entradas do sumário; a página 41 contém uma referência. | PENDING. Decidir se a distribuição é aceitável. Profundidade do sumário não foi alterada silenciosamente. |
| AII14 | Um aviso de overfull de 4.74695 pt aparece no log de compilação. | PENDING. Conferir o ponto correspondente no PDF; o auditor não observou corte, mas o diagnóstico permanece registrado. |
| Links externos | A auditoria confirma endereços e anotações URI no PDF, não a disponibilidade atual de cada site. | PENDING onde já registrado no inventário; nenhuma afirmação de acesso remoto bem-sucedido foi feita. |

## Comandos e artefatos

Comandos executados nesta revalidação: `python3 -m unittest discover -s tests -q`; `python3 scripts/migration.py verify-source`; `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex`; sete comandos `python3 scripts/migration.py validate --ledger ... --unit ...` para as unidades desta autorização; `python3 scripts/migration.py build --profile document-review` (compilação do PDF candidato); e `python3 scripts/migration.py visual --pdf build/document/main.pdf` (código 3, relatório `pending_human_review`, conforme o gate visual exige). A revisão completa foi feita pelo auditor visual independente em todas as 41 páginas renderizadas.

O PDF pode ser reproduzido em ambiente limpo pelo build de revisão aprovado do harness. Não há commit desta entrega, nem a branch principal foi alterada. As edições continuam no worktree da branch `migration/ages-ii`; confira o diff e os hashes antes de qualquer integração. O ODT mantém o SHA-256 congelado acima. `relatorio_mariah/` permaneceu como referência de leitura e não foi alterado.

## Próxima decisão

Revisar o PDF candidato e os itens PENDING desta tabela. Em particular, a confirmação da Figura 4 e das fontes das imagens é manual; os itens Graph API, Python e Docker exigem evidência bibliográfica antes de serem chamados de conformes. Esta reauditoria não inicia outra edição nem converte texto além das sete unidades autorizadas.
