# Plano de execução e checkpoints

## Estado e limite desta fase

Atualização: fase 1 autorizada pelo usuário na missão “PROJETO-PILOTO DE CONVERSÃO FIEL”. Escopo exclusivo `ages-i-sprint-0`, branch `migration/pilot-ages-i-sprint-0`; o histórico da preparação abaixo permanece registrado. O destino agora contém somente configuração global e piloto, não o memorial integral. A evidência de execução autorizada está em `migration/approvals/pilot-authorization.json`; aprovação do resultado e da próxima Sprint continuam pendentes.

Baseline: `44bc0b95ef5ed06c8efa272de4f754cce1d6e4cb`; branch de preparação `harness/migration`. Original e comparativo permanecem intactos. A configuração em `harness.json`, [BASELINE](BASELINE.json) e [TOOLCHAIN](TOOLCHAIN.lock.json) registra caminhos, versão e hashes. O harness é entregue executável; isso não significa que o memorial já satisfaz os gates.

O destino final proposto é `relatorio_AGES_eduardo/`, ainda não criado nem convertido. O template continua em `Template_AGES___Guvidaletti/`. O perfil `template` compila o material demonstrativo existente; o perfil `fixture` testa conteúdo sintético; nenhum deles conta como unidade migrada.

## Fases

| Fase | Entrada e execução | Saída / checkpoint |
|---|---|---|
| 0 — Harness | Congelar origem; registrar ferramentas; construir scripts, manifesto e governança; testar fixtures | Entrega desta fase; nenhuma conversão |
| 1 — Piloto autorizado | Confirmar autorização específica; preparar macros pelo mantenedor; extrair escopo; converter **AGES I / Easy Choose / Sprint 0** | Ledger, diff, PDF, auditorias independentes; aprovação do piloto |
| 2 — AGES I | Unidades de introdução/desenvolvimento, Sprints 0–4 e conclusão; manter piloto aprovado ou revalidar mudanças | Aprovação humana da edição completa |
| 3 — Cliente Hoortech | Introdução, apresentação aos alunos, Sprints 0–4, conclusão; sem caixas presumidas | Checkpoint próprio recomendado |
| 4 — AGES II | Introdução/desenvolvimento, Sprints 0–4 e conclusão | Aprovação humana da edição |
| 5 — AGES III | Introdução/desenvolvimento, Sprints 0–4 e conclusão; corrigir interpretação estrutural das caixas, sem alterar texto | Aprovação humana da edição |
| 6 — AGES IV | Introdução/desenvolvimento/artefatos de gerenciamento, Sprints 0–4 e conclusão; registrar lacunas de 2–4/conclusão | Aprovação humana da edição |
| 7 — Integração | Pré-textuais, trajetória, considerações, referências e apêndices conforme decisões; regenerar índices | Texto integral, normas e PDF completo verificados; aprovação final |
| 8 — Editorial | Somente por autorização específica posterior | Revisão/complementação separada e rastreável |

A ordem documental é trajetória → Easy Choose → Hoortech → Indústria Digital → RFID → Recorda → considerações → pós-textuais. O projeto-piloto não deve modificar outras Sprints. Sprint 0 de Easy Choose foi escolhida por exercitar texto, listas e reflexão sem depender de figura complexa; é um teste do caminho completo, não amostra suficiente para atestar as 34 imagens.

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
python3 scripts/migration.py build --profile document
python3 scripts/migration.py visual --pdf build/document/main.pdf
python3 scripts/migration.py checkpoint --help
```

Consultar `--help` antes de fornecer parâmetros de checkpoint e saída; não criar autorização pelo comando. `validate` sem ledger demonstra integridade do inventário, não aprovação de conversão. `build --profile document` deve recusar destino não preparado. O PDF do perfil `template` pode existir e ainda reprovar por glifos/avisos: preservar o código de saída e o relatório.

Códigos de saída: `0` = PASS; `1` = FAIL/bloqueio; `3` = não convertido, parcial ou aguardando revisão/aprovação humana. Nesta fase `validate` sem ledger e `build --profile document` retornam `3` deliberadamente. `inventory --check` verifica a reextração sem escrever o manifesto. `run-task` exige checkout limpo, usa locks por recurso entre worktrees e bloqueia conversores/mantenedor enquanto `phase=harness`; mudar esse campo não constitui autorização humana. `scope-check` aplica a exclusividade do manifesto mesmo contra o padrão amplo de documentação do orquestrador.

## Gate e decisão

Consolidar comandos, resultados, diff por unidade, hashes do PDF/log, auditoria textual e visual. Checkpoint humano registra edição/unidade, commit, artefatos, pendências aceitas e evidência da mensagem do usuário. Logs ou booleanos gerados por agentes não substituem aprovação. Ao fim desta fase, parar: apenas a autorização explícita inicia o piloto.
