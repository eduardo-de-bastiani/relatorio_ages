# Auditoria independente da correção de prosa tecnológica

Data: 17/10/2026. Papel: AUDITOR DE CONTEÚDO, subagente Codex separado do conversor. Commit observado: `96c09d125fcde4623d2f4d2218ee6aaa0cb5c656`, com alterações de trabalho identificadas pelos hashes abaixo. Escopo: somente `chapter-02-text-h-0012`, `chapter-04-text-h-0046` e `chapter-05-text-h-0085`, conforme `migration/approvals/ages-i-ii-iii-technology-prose-correction.json`.

**Resultado textual/semântico e associação ao PDF: PASS. Referências externas: PENDING** nas limitações indicadas abaixo. Não foi concedida aprovação humana, normativa global ou das edições. A auditoria visual é separada deste relatório.

## Método e origem

Leitura direta de `RELATORIO_ATUAL.odt`, por ZIP e `xml.etree.ElementTree`, aplicando os XPaths do manifesto ao `content.xml`. Foram examinados os 75 títulos/parágrafos das três seções, os descendentes dos hyperlinks, os estilos das ênfases autorais e os contêineres de listas dos 164 registros autorizados. O ledger foi usado apenas para testar rastreabilidade e spans, não como prova dos fatos. A comparação de todos os fatos e qualificadores abaixo foi feita entre o XML efetivo e o LaTeX efetivo; não foi utilizado o relato do conversor como evidência.

SHA-256 do ODT: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef` — PASS, igual ao congelado. Bibliografia: `52b7a3442d7a1feae8e7cb66ab909570455ab12c6d5dd5fbb8f1f065e76963a3` — PASS, igual à autorização; nenhuma alteração bibliográfica foi usada nesta correção.

O PDF da Mariah foi lido diretamente com `pdftotext -f 46 -l 47 -layout`, páginas físicas 46–47. A seção 4.1.5 usa prosa agrupada por frontend, backend e infraestrutura, com chamadas adjacentes aos nomes. A prosa nova adota esse tipo de agrupamento com os fatos de Eduardo: não transfere SalesPilot, React 19, Vite, TanStack, Spring Boot, Java, ferramentas, versões ou afirmações pessoais da referência. A referência também possui uma chamada final para a wiki “Tecnologias”; a autorização atual manda retirar os rótulos individuais do memorial de Eduardo, sem inventar uma wiki agregadora.

## Artefatos LaTeX auditados

| Unidade | SHA-256 do LaTeX | Cobertura conferida |
|---|---|---|
| AGES I / `chapter-02-text-h-0012` | `3f71d3ed8760c2adc0468242b265683602be79dc41bca53a63b15f8795fd4422` | 39 registros; 20 títulos/parágrafos; cinco links originais; cinco chaves bibliográficas |
| AGES II / `chapter-04-text-h-0046` | `52fc0062cc5d1974661378cf69f344eb383985c83456768aa6166f4914f8a5cb` | 50 registros; 25 títulos/parágrafos; sete links originais; dez chaves bibliográficas |
| AGES III / `chapter-05-text-h-0085` | `ce4695311f6d3041eba51d2c71fe97ce91c0c9138f995d26d24a41bc42e803d0` | 75 registros; 30 títulos/parágrafos; 13 links originais; 16 chaves bibliográficas |

Os caminhos são `relatorio_AGES_eduardo/conteudo/migracao/<unidade>.tex` e `migration/ledgers/<unidade>.json`. Em todos os mapas examinados, os hashes do destino correspondem aos bytes do LaTeX atual, os hashes de texto da origem correspondem ao manifesto, todos os IDs autorizados têm mapa ou disposição estrutural e todos os rótulos/links retirados do corpo têm intervalos vazios explícitos. A remoção é autorizada e não é classificada como perda indevida.

Hashes dos ledgers finais, na mesma ordem: `6ea322a0c410fda35f84261bf0e68114e9ddeffdddfc20fc594bb525ce057980`, `d39cf4975271dfc7a66aecd161ecdfea315585c8ce52d81d2e37acaeb2f9ca9f`, `504d4ba9e8eb6d48c42db63c9497713c1ac64a68e200a3fe5e0b54c04bfc27fc`. Os arquivos finais encerram o último parágrafo por `\par`; esse fechamento não acrescenta texto e protege a fronteira do próximo arquivo incluído.

## Associação ao PDF final

PDF efetivamente extraído: `build/document/main.pdf`, SHA-256 `27e555177cf74892cee52a90ba5da411ab6b4c4cb379cd954fdd2db17f01a2e1`. O hash do build final foi confirmado igual ao artefato extraído; não se atribui esta revisão ao PDF anterior `1bb11250…`.

As seções estão nas páginas físicas/impressas 8 (AGES I), 24–25 (AGES II) e 47–48 (AGES III). A leitura integral dessas páginas confirma os blocos acima no texto exibido, incluindo o fim da integração de AGES II na página 25 e o trecho de Entity Framework Core/infraestrutura/CI na página 48. “Consultas tipadas” aparece contínuo. Não aparecem os 25 rótulos soltos de documentação nem as antigas chamadas repetidas. Os nomes são seguidos das chamadas autor-data. A extração preserva algumas ligaturas de fonte e hifenização de fim de linha; isso foi considerado na leitura, sem usar remoção indiscriminada de caracteres como prova de equivalência.

As chamadas existentes `TypeScript [...]`, `Python (Documentação [...], 2024)`, `PostgreSQL: [...]` e outras abreviações de títulos continuam presentes, pois vêm da bibliografia congelada e não de rótulos documentais reinseridos na prosa. Esta revisão não inventa autoria para torná-las iguais às chamadas da Mariah. A forma desses metadados pode ser avaliada separadamente pelo usuário; não se confunde com perda de conteúdo nesta correção. A existência de chamadas na extração não prova por si só o clique dos links; as anotações de navegação e aparência pertencem à revisão visual independente.

## AGES I — fatos e ordem

| Origem direta | Evidência preservada no destino | Resultado |
|---|---|---|
| `text-p-0376`, `0378`–`0380` | TypeScript nas telas do tablet com componentes React; tipagem estática; segurança e manutenção do Front-end; lógica de negócios, APIs, integrações e a mesma segurança/manutenção no servidor | PASS |
| `text-p-0385`–`0387` | React na interface do tablet; interação com fluxograma para descobrir melhores suplementos; interfaces web de lojista/administrador; layouts similares e funções específicas por usuário | PASS |
| `text-p-0390`–`0391` | Node.js nas APIs RESTful; comunicação Front-end/banco; gerenciamento das requisições e respostas necessárias ao sistema | PASS |
| `text-p-0394`–`0395` | Prisma como ORM; consultas, inserções, atualizações e exclusões; modelagem e integração segura/eficiente com PostgreSQL | PASS |
| `text-p-0398`–`0399` | PostgreSQL como banco principal; usuários, configurações de tablets, lojistas/administradores, suplementos e demais informações necessárias | PASS |
| `text-p-0402` | Integração completa para usuários finais; fluxograma no tablet; gestão de tablets pelo lojista em plataforma específica e gestão global pelos administradores em plataforma dedicada | PASS |

Ordem dos blocos TypeScript → React → Node.js → Prisma → PostgreSQL → integração mantida. A correção gramatical “utilizado com banco” → “utilizado como banco” não acrescenta fato. O nome TypeScript e os demais produtos têm chamada adjacente na primeira menção substantiva do parágrafo. Não há rótulos “Documentação”, blocos de lista, frases documentais soltas ou quebras de página na seção.

## AGES II — fatos, qualificadores e ênfases

| Origem direta | Evidência preservada no destino | Resultado |
|---|---|---|
| `text-p-0810`, `0812`–`0813` | Angular no Front-end desenvolvido em TypeScript; landing page, dashboards, mapa e empresas; HTTP para Back-end e JSON recebido; interface atualizada em tempo real | PASS |
| `text-p-0817`–`0818` | Python no Back-end; requisições web à Graph API; dados de usuários de redes sociais; enriquecimento, algoritmo de presença digital e comunicação com Front-end via FastAPI | PASS |
| `text-p-0821`–`0822` | FastAPI como API/interface entre Angular e PostgreSQL; lógica de negócios e troca de dados entre componentes | PASS |
| `text-p-0825`–`0826` | Graph API para requisições e dados de perfis sociais; integração ao sistema, enriquecimento e cálculo de presença digital | PASS |
| `text-p-0829`–`0830` | SQLAlchemy como ORM (Object-Relational Mapping); entidades/tabelas PostgreSQL; manipulação e consultas via Python | PASS |
| `text-p-0833`–`0834` | PostgreSQL relacional; empresas presentes na base da Receita Federal e dados de perfis sociais; consultas via FastAPI e SQLAlchemy | PASS |
| `text-p-0837`–`0838` | Docker para ambientes locais de testes, especialmente PostgreSQL; consistência/confiabilidade dos testes em desenvolvimento | PASS |
| `text-p-0841` | Experiência completa/otimizada; pesquisa por CNAE (expansão conservada) e/ou região; mapa interativo/localização; redes sociais, contato, dashboards de presença digital, visibilidade/engajamento online e apoio a decisões | PASS |

Ordem Angular/TypeScript → Python → FastAPI → Graph API → SQLAlchemy → PostgreSQL → Docker → integração mantida. Os itálicos de `landing page`, `dashboards` em ambas as ocorrências e `Object-Relational Mapping` correspondem ao estilo ODF `T175`, cuja propriedade `fo:font-style="italic"` foi lida no próprio `content.xml`. Não são itálicos novos aplicados a hyperlinks. As citações existentes estão junto aos nomes, com a primeira ocorrência de cada produto devidamente chamada em seu parágrafo; não há necessidade de repetir a mesma fonte a cada frase contínua. HTTP/JSON mantêm suas referências existentes. Sem listas ou rótulos documentais no corpo.

## AGES III — fatos e qualificadores

| Origem direta | Evidência preservada no destino | Resultado |
|---|---|---|
| `text-p-1066` | C# em backend/gateway; maturidade, produtividade e integração nativa com ecossistema .NET | PASS |
| `text-p-1069` | .NET como framework principal no backend e gateway RFID; robustez, performance e boa integração com nuvem | PASS |
| `text-p-1072`–`1073` | React na interface web; telas administrativas/de clientes; componentes reutilizáveis | PASS |
| `text-p-1076`–`1077` | TypeScript no frontend adicionando tipagem estática ao JavaScript; segurança do código/manutenção | PASS |
| `text-p-1080` | Impinj R700 REST API na comunicação gateway/leitor RFID físico; configuração e captura de eventos | PASS semântico; comprovação da fonte original PENDING |
| `text-p-1083`–`1084` | Entity Framework Core como ORM no backend .NET; entidades → tabelas relacionais; models, migrations, relacionamentos, constraints e consultas tipadas; aceleração do desenvolvimento e padronização do acesso aos dados | PASS |
| `text-p-1087` | AWS Lambda serverless para hospedar/executar backend; escalabilidade sob demanda e menor custo operacional | PASS |
| `text-p-1090` | Amazon S3 para arquivos estáticos do frontend da aplicação web | PASS semântico; força da fonte já pendente |
| `text-p-1093` | CloudFront distribui frontend com melhor desempenho e menor latência | PASS |
| `text-p-1096` | RDS gerenciado hospeda PostgreSQL da aplicação | PASS |
| `text-p-1099` | PostgreSQL relacional para armazenamento estruturado das informações do sistema | PASS |
| `text-p-1102` | Docker padroniza ambientes locais, executa dependências e apoia testes automatizados | PASS semântico; força da fonte já pendente |
| `text-p-1105` | GitHub Actions para pipelines CI/CD, qualidade do código e sincronização entre GitHub/GitLab | PASS |

Ordem de todas as 13 tecnologias mantida. Citações adicionais a JavaScript, RFID e GitLab são as mesmas fontes já integradas, não fatos nem referências novos desta correção. A junção “consultas tipadas” corresponde à remoção do único tab interno expressamente aprovada anteriormente; não há letra adicionada. As ênfases antigas nos rótulos de tecnologias não foram transferidas como listas; a substituição por prosa está autorizada. Nenhuma função foi substituída por mera descrição genérica do produto, nenhuma versão foi inventada e não há repetição de “Mais informações podem ser encontradas em: Documentação”.

## Links originais e referências congeladas

Os 25 hyperlinks originais têm âncora e `xlink:href` idênticos no XML e em `documentation_links` dos ledgers. Foram retirados apenas da apresentação destas seções, por instrução explícita. Não se presume que um hyperlink antigo e uma referência suplementar sejam equivalentes.

| IDs de origem | Destinos conferidos | Resultado |
|---|---|---|
| `text-a-0111`–`0115` | `https://www.typescriptlang.org/docs/`; `https://react.dev/`; `https://nodejs.org/docs/latest/api/`; `https://www.prisma.io/docs`; `https://www.postgresql.org/docs/` | PASS de igualdade com ledger e entradas bibliográficas existentes |
| `text-a-0122`–`0125`, `0127`–`0128` | `https://v17.angular.io/docs`; `https://www.typescriptlang.org/pt/docs/handbook/typescript-in-5-minutes.html`; `https://docs.python.org/pt-br/3/`; `https://fastapi.tiangolo.com/`; `https://docs.sqlalchemy.org/en/20/`; `https://www.postgresql.org/docs/` | PASS de igualdade com ledger e entradas existentes |
| `text-a-0126` | Origem/ledger: `https://developers.facebook.com/docs/graph-api/guides/explorer/`; referência `ages-ii-graph-api`: `https://developers.facebook.com/docs/graph-api/` | PENDING de equivalência e disponibilidade; a referência genérica não prova o endereço Explorer |
| `text-p-0839` | “Documentação Docker” sem hyperlink no ODT; referência existente `ages-ii-docker`: `https://www.docker.com/` | PASS da classificação sem URL original; não inventar um `text:a`; comprovação bibliográfica permanece separada |
| `text-a-0133`–`0136`, `0138`–`0145` | `https://learn.microsoft.com/dotnet/csharp/`; `https://dotnet.microsoft.com/`; `https://react.dev/`; `https://www.typescriptlang.org/`; `https://learn.microsoft.com/ef/core/`; `https://aws.amazon.com/lambda/`; `https://aws.amazon.com/s3/`; `https://aws.amazon.com/cloudfront/`; `https://aws.amazon.com/rds/`; `https://www.postgresql.org/`; `https://www.docker.com/`; `https://github.com/features/actions` | PASS de igualdade com ledger/entradas existentes; a força das evidências anteriores não é ampliada |
| `text-a-0137` | Origem/ledger: `https://support.impinj.com/hc/en-us`; referência suplementar `ages-iii-impinj-iot-interface`: `https://www.impinj.com/products/technology/key-features/iot-device-interface` | PENDING; URLs distintos, suporte raiz não comprovado; sem substituição no ledger |

Todas as 31 chaves obrigatórias existem na bibliografia congelada e estão citadas no LaTeX das três seções. As datas/autores/URLs da bibliografia não foram alterados. Esta auditoria não realizou novos acessos remotos e não promove PENDING para PASS: atesta igualdade e preservação dos dados existentes, não disponibilidade atual dos serviços ou comprovação histórica das datas atribuídas de AGES I/II.

## Pendências e retorno

| ID | Arquivo/localização e evidência | Consequência / gravidade | Correção proposta e verificação |
|---|---|---|---|
| TR-C01 | Extração das três seções no PDF final `27e555…`, páginas 8, 24–25 e 47–48 | PASS da associação e conteúdo exibido | Hash final confirmado; leitura de todos os trechos e continuações concluída; visual por auditor separado |
| TR-C02 | `text-a-0126`/`ages-ii-graph-api` e `text-a-0137`/`ages-iii-impinj-iot-interface` têm destinos distintos | Equivalência/proveniência permanece PENDING; média | Preservar URLs originais no ledger e referências existentes sem inventar equivalência; decisão factual em fase própria |
| TR-C03 | Descrições antigas de Docker/integração bibliográfica nos ledgers foram corrigidas pelo CONVERSOR | RESOLVIDO; baixa; não houve perda no memorial | Releitura dos ledgers finais confirmou ausência de hyperlink original de Docker, presença da referência suplementar e integração existente sem ampliar força da evidência |
| TR-C04 | Fontes AGES III S3/Docker sustentam identidade/função geral, com limitação já registrada; Impinj original não comprovado | Evidência factual externa PENDING; média | Manter pendência e não apresentar esta preservação semântica como nova confirmação dos fatos |

## Comandos e limites

- `python3` com `zipfile`, `xml.etree.ElementTree`, `json`, `hashlib` e `re`: leitura direta dos 75 títulos/parágrafos via XPaths, comparação de hashes e mapas, cobertura dos 164 IDs, âncoras/URLs dos 25 hyperlinks e 31 chaves — código 0 nas verificações finais. A tentativa exploratória inicial com `lxml` encontrou módulo indisponível; foi substituída pela biblioteca padrão, sem instalação e sem limitação da leitura.
- `pdftotext -f 46 -l 47 -layout relatorio_mariah/relatorio_ages-main/extracted/main.pdf -` — código 0; somente referência de estrutura, sem transferir conteúdo.
- Leitura de `content.xml` para resolução de estilos de ênfase — código 0; `T175` confirmado itálico.
- `git rev-parse HEAD` — código 0; commit informado acima. Sem commit ou alteração do memorial pelo auditor.
- Chamada direta da função pura `migration_harness.preservation.audit_conversion(manifest, ledger, repo, unit_id=...)` nas três unidades finais — processo código 0, resultado PASS em cada unidade, cobertura 100%; 6/15/18 ocorrências de citações. Usou-se a função sem gravar outros relatórios. O aviso automatizado de revisão semântica pendente é tratado pela comparação independente deste relatório, não convertido em prova automática.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex` — código 0, PASS, 48 arquivos, 40 entradas bibliográficas, 80 citações, sem chave inexistente; aviso conservador `unsupported_citation_command` sobre `\memorial@citefirstword` de estilo não resolve por si a saída da macro.
- `pdftotext -layout build/document/main.pdf -` e extração explícita da página 25 — código 0; conteúdo das três seções/continuações lido, PDF SHA `27e555…`.
- Build final foi executado centralmente pelo orquestrador e comunicado com código 0/PASS, sem findings. Este auditor não atribui a si a execução do build nem a inspeção visual do PDF.

Único arquivo alterado por este auditor: `docs/technology-review/CONTENT_AUDIT.md`. Não foram modificados origem, memorial, ledgers, bibliografia, manifesto ou configuração. Auditoria semântica não substitui inspeção visual, verificação normativa completa ou aprovação humana.
