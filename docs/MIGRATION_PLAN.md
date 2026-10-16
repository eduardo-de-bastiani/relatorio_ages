# Plano de execução e checkpoints

## Estado e limite desta fase

Fase vigente: migração controlada da **AGES II / Indústria Digital**, autorizada na mensagem atual do usuário. A apresentação da AGES I foi aceita para reutilização e registrada em `migration/approvals/ages-i-presentation-accepted.json`; os padrões concretos estão em `docs/STYLE_GUIDE.md`. A branch de integração é `migration/ages-ii`; o conjunto fechado de 15 unidades e a posse de assets estão em `harness.json` e `migration/approvals/ages-ii-authorization.json`. Não incluir a participação como cliente Hoortech nem AGES III–IV. A entrega desta edição exige revisão humana.

Correção de apresentação solicitada em 16/10/2026: antes da entrega, estão autorizadas somente as alterações dos três trechos de banco/arquitetura/protótipos da AGES I e dos quatro trechos de banco/arquitetura/protótipos/tecnologias da AGES II, além das macros e documentação necessárias, conforme `migration/approvals/ages-i-ii-formatting-authorization.json`. Esta correção não reabre a conversão da AGES I nem autoriza conteúdo de outras unidades. Após corrigir, revalidar as unidades afetadas e recompilar/auditar o documento integrado; somente então apresentar a versão revista da AGES II para aprovação.

Fases do piloto e da AGES I são históricas e mantêm seus registros. A mensagem atual autoriza a AGES II, após o usuário aprovar a apresentação da prévia AGES I e solicitar que o padrão fosse documentado. Pendências de fonte de imagem, diagrama ausente, disponibilidade remota de links e confirmação normativa permanecem abertas; os arquivos de autorização explicitam como preservá-las.

Baseline: `44bc0b95ef5ed06c8efa272de4f754cce1d6e4cb`; branch de preparação `harness/migration`. Original e comparativo permanecem intactos. A configuração em `harness.json`, [BASELINE](BASELINE.json) e [TOOLCHAIN](TOOLCHAIN.lock.json) registra caminhos, versão e hashes. O harness é entregue executável; isso não significa que o memorial já satisfaz os gates.

O destino editável é `relatorio_AGES_eduardo/`; AGES I já está convertida e somente as unidades autorizadas de AGES II serão adicionadas nesta fase. A exceção acima permite corrigir a apresentação dos três trechos técnicos já convertidos da AGES I. `Template_AGES___Guvidaletti/` permanece como referência somente leitura. O perfil `template` compila material demonstrativo; o perfil `fixture` testa conteúdo sintético; nenhum deles conta como unidade migrada.

## Fases

| Fase | Entrada e execução | Saída / checkpoint |
|---|---|---|
| 0 — Harness | Congelar origem; registrar ferramentas; construir scripts, manifesto e governança; testar fixtures | Entrega desta fase; nenhuma conversão |
| 1 — Piloto autorizado | AGES I / Easy Choose / Sprint 0 | Concluído e revalidado na edição completa |
| 2 — AGES I | Introdução/desenvolvimento, Sprints 0–4 e conclusão | Convertida; apresentação aceita para reutilização, com pendências factuais/normativas mantidas |
| 3 — Cliente Hoortech | Introdução, apresentação aos alunos, Sprints 0–4, conclusão; sem caixas presumidas | Checkpoint próprio recomendado |
| 4 — AGES II | Somente capítulo 4 / Indústria Digital, 15 unidades detalhadas abaixo | **Fase ativa:** entrega, auditorias, PDF e aprovação humana |
| 5 — AGES III | Introdução/desenvolvimento, Sprints 0–4 e conclusão; corrigir interpretação estrutural das caixas, sem alterar texto | Aprovação humana da edição |
| 6 — AGES IV | Introdução/desenvolvimento/artefatos de gerenciamento, Sprints 0–4 e conclusão; registrar lacunas de 2–4/conclusão | Aprovação humana da edição |
| 7 — Integração | Pré-textuais, trajetória, considerações, referências e apêndices conforme decisões; regenerar índices | Texto integral, normas e PDF completo verificados; aprovação final |
| 8 — Editorial | Somente por autorização específica posterior | Revisão/complementação separada e rastreável |

A ordem documental é trajetória → Easy Choose → Hoortech → Indústria Digital → RFID → Recorda → considerações → pós-textuais. Esta missão escolhe apenas Indústria Digital, embora Hoortech seja anterior no original. Nenhum outro capítulo recebe conteúdo ou é convertido nesta fase.

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

Códigos de saída: `0` = PASS; `1` = FAIL/bloqueio; `3` = não convertido, parcial ou aguardando revisão/aprovação humana. Nesta fase `validate` sem ledger e `build --profile document` retornam `3` deliberadamente. `inventory --check` verifica a reextração sem escrever o manifesto. `run-task` exige checkout limpo, usa locks por recurso entre worktrees e bloqueia conversores/mantenedor enquanto `phase=harness`; mudar esse campo não constitui autorização humana. `scope-check` aplica a exclusividade do manifesto mesmo contra o padrão amplo de documentação do orquestrador.

## Gate e decisão

Consolidar comandos, resultados, diff por unidade, hashes do PDF/log, auditoria textual e visual. Checkpoint humano registra edição/unidade, commit, artefatos, pendências aceitas e evidência da mensagem do usuário. Logs ou booleanos gerados por agentes não substituem aprovação. Ao fim desta fase, parar e aguardar aprovação da AGES II; não iniciar Hoortech nem AGES III–IV.
