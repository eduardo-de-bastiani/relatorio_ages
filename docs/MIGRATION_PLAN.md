# Plano de execução e checkpoints

## Estado e limite desta fase

Atualização de 17/10/2026: o usuário autorizou a migração parcial de AGES IV / Recorda até Sprint 1, com títulos vazios para Sprints 2–4 e Conclusão do capítulo 6, além do título do capítulo 7 sem seus dez parágrafos. A autorização e os 17 IDs fechados estão em `migration/approvals/ages-iv-partial-authorization.json` e `harness.json`. Dois conversores podem trabalhar em cópias temporárias isoladas em `/tmp`, sem sobreposição de unidades/assets; a integração é serial. O curador trabalha em evidências separadas; a integração da bibliografia é centralizada pelo mantenedor. Auditores de conteúdo e visual terão relatórios em `docs/ages-iv/`. Gerar e inspecionar `build/document/main.pdf`, registrar hashes, limitações e aprovação humana. O capítulo 7 é incluído somente pelo título, conforme decisão explícita; o corpo de dez parágrafos fica identificado como omissão autorizada e pendência editorial futura.


Fase vigente: conversão parcial de **AGES IV / Recorda** mais o complemento pré-textual e trajetória autorizado em 17/10/2026. O usuário declara que o material disponível vai até Sprint 1, inclusive. A compilação deve incluir as unidades do capítulo 6 dessa fase e manter as três Sprints futuras e Conclusão como títulos vazios. O usuário informa que o checkpoint anterior está commitado e enviado na branch `migration/ages-iii`; esta ampliação usa como baseline local observado `31c34e0c164b30a1cb81e289581e48f5279ee1b1` e continua sem commit/push. A referência visual e estrutural é `docs/STYLE_GUIDE.md`. A entrega parcial e o complemento exigem revisão humana.

Escopo fechado desta execução: nove unidades com conteúdo (`chapter-06-text-h-0106`, `chapter-06-text-h-0108`–`0110`, `chapter-06-text-h-0112`–`0114`, `ages-iv-sprint-0`, `ages-iv-sprint-1`) e sete unidades somente com títulos (`chapter-06-text-h-0105`, `chapter-06-text-h-0107`, `chapter-06-text-h-0115`, `ages-iv-sprint-2`–`ages-iv-sprint-4`, `chapter-06-text-h-0122`). A unidade `chapter-07-text-h-0123`, “Considerações finais (Somente AGES IV)”, foi autorizada apenas como título. Os IDs `text-p-1539`–`text-p-1547`, `text-p-1549`, `text-list-0280/0281` e `text-list-item-0225`–`0230` permanecem omitidos conforme a resposta do usuário; a unidade não deve ser reportada como integralmente convertida.

Correção de apresentação solicitada em 16/10/2026: antes da entrega, estão autorizadas somente as alterações dos três trechos de banco/arquitetura/protótipos da AGES I e dos quatro trechos de banco/arquitetura/protótipos/tecnologias da AGES II, além das macros e documentação necessárias, conforme `migration/approvals/ages-i-ii-formatting-authorization.json`. Esta correção não reabre a conversão da AGES I nem autoriza conteúdo de outras unidades. Após corrigir, revalidar as unidades afetadas e recompilar/auditar o documento integrado; somente então apresentar a versão revista da AGES II para aprovação.

Fases do piloto e das AGES I–III são históricas e mantêm seus registros. A autorização vigente é a parte explicitamente delimitada de AGES IV; ela não apaga pendências de fontes, referências ou confirmação normativa anteriores. Os arquivos de autorização identificam e limitam o escopo desta execução.

Baseline: `44bc0b95ef5ed06c8efa272de4f754cce1d6e4cb`; branch de preparação `harness/migration`. Original e comparativo permanecem intactos. A configuração em `harness.json`, [BASELINE](BASELINE.json) e [TOOLCHAIN](TOOLCHAIN.lock.json) registra caminhos, versão e hashes. O harness é entregue executável; isso não significa que o memorial já satisfaz os gates.

O destino editável é `relatorio_AGES_eduardo/`; as edições AGES I–III e a porção principal autorizada de AGES IV permanecem integradas no checkpoint anterior. Esta ampliação acrescenta somente `pretext`, `resumo` e `chapter-01-text-h-0001`, conforme sua autorização suplementar; os arquivos de conteúdo dos projetos continuam intactos. `Template_AGES___Guvidaletti/` permanece como referência somente leitura. O perfil `template` compila material demonstrativo; o perfil `fixture` testa conteúdo sintético; nenhum deles conta como unidade migrada.


**Complemento autorizado em 17/10/2026:** além das 17 unidades Recorda acima, o usuário autorizou a inclusão da capa, três títulos pré-textuais vazios, placeholder de resumo, lista automática de ilustrações, as 39 siglas existentes no ODT, o sumário e o texto pronto da trajetória. O escopo exato são `pretext`, `resumo` e `chapter-01-text-h-0001`, rastreados em `migration/approvals/ages-iv-frontmatter-authorization.json` e nos três ledgers correspondentes. A ordem requerida é capa → Dedicatória → Agradecimentos → Epígrafe → Resumo → Lista de Ilustrações → Lista de Siglas → Sumário → trajetória → capítulos AGES existentes. A trajetória é transcrita sem os dois parágrafos de instrução do modelo. A lista de ilustrações é regenerada pelo LaTeX. Os arquivos/capítulos AGES II–IV permanecem inalterados por este complemento. A revisão visual humana e a aprovação da entrega continuam pendentes.

## Fases

| Fase | Entrada e execução | Saída / checkpoint |
|---|---|---|
| 0 — Harness | Congelar origem; registrar ferramentas; construir scripts, manifesto e governança; testar fixtures | Entrega desta fase; nenhuma conversão |
| 1 — Piloto autorizado | AGES I / Easy Choose / Sprint 0 | Concluído e revalidado na edição completa |
| 2 — AGES I | Introdução/desenvolvimento, Sprints 0–4 e conclusão | Convertida; apresentação aceita para reutilização, com pendências factuais/normativas mantidas |
| 3 — Cliente Hoortech | Introdução, apresentação aos alunos, Sprints 0–4, conclusão; sem caixas presumidas | Checkpoint próprio recomendado |
| 4 — AGES II | Somente capítulo 4 / Indústria Digital, 15 unidades detalhadas abaixo | Concluída e aprovada pelo usuário em 16/10/2026; pendências factuais permanecem registradas |
| 5 — AGES III | Capítulo 5 / RFID: introdução, desenvolvimento, cinco Sprints e conclusão; conferir caixas de reflexão aninhadas e parágrafo vazio de Sprint 2, sem alterar texto | Conversão e revisão entregues; usuário confirmou aprovação na mensagem de 17/10/2026 |
| 6 — AGES IV | Capítulo 6 / Recorda: introdução, desenvolvimento, Sprints 0–1, títulos vazios 2–4 e conclusão | **Fase ativa parcial:** conversão, auditorias, PDF e aprovação humana; capítulo 7 inclui somente o título; corpo explicitamente omitido |
| 7 — Integração | Pré-textuais, trajetória, considerações, referências e apêndices conforme decisões; regenerar índices | Texto integral, normas e PDF completo verificados; aprovação final |
| 8 — Editorial | Somente por autorização específica posterior | Revisão/complementação separada e rastreável |

A ordem dos elementos nesta entrega é: capa → Dedicatória → Agradecimentos → Epígrafe → Resumo → Lista de Ilustrações → Lista de Siglas → Sumário → trajetória → Easy Choose → Hoortech → Indústria Digital → RFID → Recorda → considerações → referências. As etapas anteriores permanecem nos checkpoints já registrados. Esta missão inclui somente as 17 unidades principais de Recorda e as três unidades complementares expressamente autorizadas; não autoriza alterações de texto dos projetos nem outra edição AGES.

## Plano de unidades AGES II

O capítulo 4 do manifesto (`text-h-0039` até `text-h-0073`) contém 15 unidades. A união de IDs rastreados soma 332 registros: 134 parágrafos, 16 títulos, 68 contêineres de lista, 64 itens de lista, 13 hyperlinks, 12 caixas de texto e sete imagens. Cinco caixas são reflexões das Sprints; sete caixas preservam legendas vinculadas às imagens. O capítulo não contém tabela nem nota. Contêineres vazios e índices gerados continuam classificados pelo manifesto, não como texto autônomo.

| Ordem | Unidade | ID | Conversor | Assets exclusivos |
|---:|---|---|---|---|
| 1 | 4 - PROJETO AGES II – INDÚSTRIA DIGITAL | `chapter-04-text-h-0039` | A | — |
| 2 | 4.1 Introdução | `chapter-04-text-h-0040` | A | `asset-0018` — foto do time |
| 3 | 4.2 Desenvolvimento do Projeto | `chapter-04-text-h-0041` | A | — |
| 4 | 4.2.1 Repositório do código Fonte do Projeto | `chapter-04-text-h-0042` | A | — |
| 5 | 4.2.2 Banco de dados utilizado | `chapter-04-text-h-0043` | A | placeholder provisório; diagrama não existe na origem |
| 6 | 4.2.3 Arquitetura utilizada | `chapter-04-text-h-0044` | A | `asset-0008` |
| 7 | 4.2.4 Protótipos das telas desenvolvidas | `chapter-04-text-h-0045` | A | `asset-0020`–`asset-0023` |
| 8 | 4.2.5 Tecnologias utilizadas | `chapter-04-text-h-0046` | A | sete documentações tecnológicas |
| 9 | 4.3 Atividades desempenhadas pelo aluno no projeto | `chapter-04-text-h-0047` | B | — |
| 10–14 | Sprints 0–4 | `ages-ii-sprint-0`–`ages-ii-sprint-4` | B | Sprint 4: `asset-0025` |
| 15 | 4.4. Conclusão | `chapter-04-text-h-0073` | B | — |

Conversor A recebe oito arquivos/ledgers e as seis imagens de Introdução, Arquitetura e Protótipos. Conversor B recebe sete arquivos/ledgers e a imagem da Sprint 4. MANTENEDOR LATEX integra `main.tex` e `.bib` uma vez, após o registro das referências pelo curador; a posse desses arquivos compartilhados nunca é distribuída aos conversores.

Pendências durante a execução: diagrama de banco de dados ausente → placeholder visual provisório, sem conteúdo inventado; fonte/autoria das sete imagens → “pendente de identificação” até resposta manual do usuário; disponibilidade atual dos links de repositórios/wikis → preservar URLs originais e registrar o resultado do teste separadamente. Os sete links de documentação tecnológica são Angular, TypeScript, Python, FastAPI, Graph API Explorer, SQLAlchemy e PostgreSQL. Curadoria verifica URL oficial, título e entidade responsável; não afirma versão efetivamente usada.

O usuário informou que a atuação AGES II ocorreu entre agosto e novembro de 2024 e autorizou atribuir datas de acesso nessa janela. Para esta edição foi selecionada 15/10/2024 para as documentações tecnológicas, com ano bibliográfico 2024, seguindo sua instrução. Essa data é uma convenção atribuída, não histórico real de navegação. Se a evidência de uma documentação oficial não sustentar o registro, parar essa referência e registrar a pendência antes de integrar a bibliografia.

## Plano de unidades AGES III

O conjunto fechado contém 15 unidades: `chapter-05-text-h-0074`–`chapter-05-text-h-0080`, `chapter-05-text-h-0085`, `chapter-05-text-h-0086`, `ages-iii-sprint-0`–`ages-iii-sprint-4` e `chapter-05-text-h-0097`. O manifesto rastreia 286 IDs únicos: 106 parágrafos, 16 títulos, 63 contêineres de lista, 44 itens, 19 cabeçalhos de lista, 17 hyperlinks, 13 caixas de texto e oito imagens. Não há tabelas. Cinco caixas são reflexões (12 parágrafos não vazios e um vazio em Sprint 2); oito caixas restantes são legendas em quadros. As caixas devem ser lidas pela ordem lógica dos descendentes, e o parágrafo vazio deve permanecer rastreado até validação visual. A origem incorpora diagramas de banco e arquitetura, portanto não há placeholder previsto para esses diagramas.

| Grupo | Unidades | Arquivos/escopo | Responsabilidade |
|---|---|---|---|
| A | `chapter-05-text-h-0074`–`chapter-05-text-h-0080`, `chapter-05-text-h-0085` | título, introdução, desenvolvimento, repositórios, banco, arquitetura, protótipos e tecnologias; oito unidades de conteúdo e oito imagens | Conversor A; somente seus arquivos LaTeX, assets atribuídos e ledgers |
| B | `chapter-05-text-h-0086`, `ages-iii-sprint-0`–`ages-iii-sprint-4`, `chapter-05-text-h-0097` | título de atividades, cinco Sprints e conclusão; sete unidades, sem mídia | Conversor B; somente seus arquivos LaTeX e ledgers |

Assets exclusivos: `chapter-05-text-h-0075` recebe `asset-0015.jpg` (foto da equipe); `chapter-05-text-h-0078` recebe `asset-0014.png` (diagrama do banco); `chapter-05-text-h-0079` recebe `asset-0004.png` (diagrama de arquitetura); `chapter-05-text-h-0080` recebe `asset-0028.png`–`asset-0032.png` (cinco protótipos). Os oito têm bytes e hashes no manifesto. Fontes/autoria não comprovadas serão indicadas como pendentes, sem inferência.

O ODT tem três links de repositório, uma wiki de banco de dados e 13 links de documentação tecnológica (C#, .NET, React, TypeScript, Impinj R700 API, Entity Framework Core, AWS Lambda, S3, CloudFront, RDS, PostgreSQL, Docker e GitHub Actions). O curador compara URLs e âncoras ao manifesto, registra evidência e a data real de acesso; metadados não comprovados permanecem PENDING. Em 16/10/2026, o usuário autorizou continuar com os links originais preservados e pendências explícitas; ver `migration/approvals/ages-iii-pending-references-acceptance.json`. Não inventar nem retrodatá-las, nem criar autores, versões, publicações, citações ou URLs sem evidência. As unidades podem ser convertidas fielmente, mas os gates bibliográficos permanecem PENDING até a evidência ou decisão humana pertinente.

Conversores podem trabalhar em paralelo somente nas worktrees `migration/ages-iii-converter-a` e `migration/ages-iii-converter-b`, criadas a partir do checkpoint limpo desta branch. A integração de `main.tex`, macros e bibliografia é serial e pertence ao MANTENEDOR LATEX. Curadoria escreve somente evidência separada até a integração central.

## Unidade e dependências

O EXTRATOR define os elementos e a chave de cada unidade no manifesto. Cada tarefa recebe: ID de unidade, IDs de origem, commit/hashes, destinos permitidos, dependências, skill aplicável e resultados esperados. CONVERSOR recebe somente a unidade e seu ledger. Material compartilhado depende do MANTENEDOR; referências dependem de evidência do CURADOR; nenhum agente altera um arquivo fora de sua posse para destravar a tarefa.

Antes de cada conversão: origem verificada, classificação de contêineres resolvida, destino e ledger atribuídos, macros estáveis e autorização do estágio registrada. Depois: validação independente → compilação → inspeção visual → integração serial → checkpoint humano. A edição seguinte só começa quando a anterior atingir o checkpoint; extração/curadoria somente de leitura podem avançar sem convertê-la.

## Isolamento e versionamento

- Branch de preparação separada da principal; commits pequenos por governança, extração, validação e build.
- Para tarefas futuras paralelas, uma branch/worktree por unidade a partir do mesmo commit de macros. Exemplo: `git worktree add ../relatorio-ages-u01 -b migration/u01 <commit-aprovado>`. O caminho externo precisa estar autorizado no ambiente; caso contrário, usar diretório permitido ou execução serial.
- Atribuir arquivos antes da tarefa. Locks de `run-task` são cooperativos por papel/unidade; os checks de escopo detectam violações posteriores. Não fornecem isolamento de sistema operacional.
- Integração serial pelo orquestrador; nenhuma escrita simultânea em manifesto, main, estilos, bibliografia ou plano. Mudança global requer revalidação das unidades já integradas.
- Não remover conflitos escolhendo cegamente um lado. Conflito de conteúdo/ledger volta ao proprietário para comparação com a origem.
- Rollback pela branch/commit da unidade, preservando evidência de falha. Não resetar a principal nem apagar trabalho alheio. Revalidar hashes e gates após reversão.

## Comandos do harness

Executar a partir da raiz, usando o intérprete registrado no toolchain:

```sh
python3 scripts/migration.py verify-source
python3 scripts/migration.py inventory
python3 scripts/migration.py doctor
python3 scripts/migration.py validate
python3 scripts/migration.py audit-latex --root Template_AGES___Guvidaletti --entry main.tex
python3 scripts/migration.py build --profile fixture
python3 scripts/migration.py build --profile template
```

Na futura unidade autorizada:

```sh
python3 scripts/migration.py run-task --role converter --unit <id> -- <comando>
python3 scripts/migration.py validate --ledger migration/ledgers/<id>.json --unit <id>
python3 scripts/migration.py scope-check --role converter --unit <id> --base <commit-inicial>
python3 scripts/migration.py build --profile document-review
python3 scripts/migration.py build --profile document
python3 scripts/migration.py visual --pdf build/document/main.pdf
python3 scripts/migration.py checkpoint --help
```

Consultar `--help` antes de fornecer parâmetros de checkpoint e saída; não criar autorização pelo comando. `validate` sem ledger demonstra integridade do inventário, não aprovação de conversão. `document-review` compila o estado de trabalho para revisão humana e marca o gate oficial como não executado; `document` é o build de produção e exige commit limpo. O PDF do perfil `template` pode existir e ainda reprovar por glifos/avisos: preservar o código de saída e o relatório.

Códigos de saída: `0` = PASS; `1` = FAIL/bloqueio; `3` = não convertido, parcial ou aguardando revisão/aprovação humana. Nesta etapa, `validate` sem ledger e `build --profile document` retornam `3` deliberadamente. `inventory --check` verifica a reextração sem escrever o manifesto. `run-task` exige checkout limpo e usa locks cooperativos por recurso entre worktrees. A proteção de conversores/mantenedor durante `phase=harness` continua aplicável à preparação do harness; a execução da edição exige a autorização humana e o escopo corrente já registrados em `harness.json`. `scope-check` aplica a exclusividade do manifesto mesmo contra o padrão amplo de documentação do orquestrador.

## Gate e decisão

Consolidar comandos, resultados, diff por unidade, hashes do PDF/log, auditoria textual e visual. Checkpoint humano registra edição/unidade, commit, artefatos, pendências aceitas e evidência da mensagem do usuário. Logs ou booleanos gerados por agentes não substituem aprovação. Ao fim desta entrega parcial de AGES IV, parar e aguardar aprovação humana; não iniciar outra edição nem Hoortech.
