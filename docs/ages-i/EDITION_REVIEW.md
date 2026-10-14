# AGES I / Easy Choose — entrega para revisão humana

Resultado: **15 unidades convertidas e auditadas; aprovação humana PENDING**. PDF de 17 páginas, SHA-256 `c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f`. O commit que produziu os fontes/PDF auditados é `25319d941aa0c7c227dd80094b0b25f582be68b6`. Os commits posteriores de documentação/manifesto não alteram esses fontes. A branch de trabalho é `migration/ages-i`; nenhuma outra participação foi migrada.

A conversão preserva 102 blocos textuais, cinco imagens com bytes originais, 11 URLs e cinco reflexões com 17 parágrafos. Os diagramas de banco e arquitetura ausentes aparecem como dois placeholders provisórios, fora da lista de figuras reais. A Sprint 0 mantém o mesmo arquivo LaTeX do piloto.

## Entregáveis

- [PDF atual](../../build/document/main.pdf) e [snapshot identificado](../../build/ages-i/review/c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f/main.pdf)
- [Fontes LaTeX](../../relatorio_AGES_eduardo/main.tex) e [ledgers por unidade](../../migration/ledgers/)
- [Manifesto](../CONTENT_MANIFEST.json), com overlays de execução separados do inventário imutável
- [Diferenças textuais por unidade/Sprint](TEXT_DIVERGENCES.json)
- [Auditoria independente de conteúdo](CONTENT_AUDIT.md) e [auditoria visual completa](VISUAL_AUDIT.md)
- [Log TeX](../../build/document/main.log), [log Biber](../../build/document/main.blg), [saída do compilador](../../build/document/compiler.txt) e [relatório de build](../../build/document/report.json)
- [Resultados dos 71 testes](../../build/ages-i/final-checks/tests.txt), [validações por unidade](../../build/ages-i/integrity/report.json) e [curadoria documental](../../migration/evidence/references/ages-i.json)

## Critérios executados

| Gate | Resultado e evidência |
|---|---|
| G0/G1 — origem e inventário | PASS: ODT SHA congelado, 112 arquivos protegidos e reextração determinística sem divergência; `verify-source`, `inventory --check` |
| G2/G3 — cobertura, texto e ordem | PASS: 15 `validate`, retorno 0, 102/102 textos, diferenças vazias; auditor independente confrontou XML e bytes reais |
| G4 — mídia e URLs | PASS de identidade: cinco hashes de imagens, 11 âncoras/URLs; disponibilidade remota dos seis links de projeto PENDING por decisão expressa do usuário |
| G5 — estrutura | PASS: 18 arquivos TeX alcançáveis, 20 labels, cinco figuras e cinco entradas bibliográficas válidas; nenhum arquivo de outra edição |
| G6 — compilação | PASS: Tectonic 0.17.0/Biber 2.17, offline e em cópia isolada, retorno 0, log final sem erros/avisos; sumário/lista de figuras/bibliografia regenerados |
| G7 — visual | PASS de execução: todas as 17 páginas do PDF final foram abertas pelo auditor independente; ressalvas de tabs/proveniência separadas |
| G8 — normativo | PENDING integral; medições A4, corpo 12 pt, margens e paginação estão documentadas; não se declara certificação completa ABNT |
| G9 — humano | PENDING para todas as 15 unidades; nenhuma aprovação automática ou autorização da próxima edição |

## Unidades e situação

| Unidade original | ID / arquivo | Conteúdo | Visual | Aceite humano |
|---|---|---|---|---|
| 2 - PROJETO AGES I – EASY CHOOSE | [chapter-02-text-h-0002](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0002.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Introdução | [chapter-02-text-h-0003](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0003.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Desenvolvimento do Projeto | [chapter-02-text-h-0007](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0007.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Repositório do código Fonte do Projeto | [chapter-02-text-h-0008](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0008.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Banco de dados utilizado | [chapter-02-text-h-0009](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0009.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Arquitetura utilizada | [chapter-02-text-h-0010](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0010.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Protótipos das telas desenvolvidas | [chapter-02-text-h-0011](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0011.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| Tecnologias utilizadas | [chapter-02-text-h-0012](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0012.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3 Atividades desempenhadas pelo aluno no projeto | [chapter-02-text-h-0014](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0014.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3.1 Sprint 0 | [ages-i-sprint-0](../../relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-0.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3.2 Sprint 1 | [ages-i-sprint-1](../../relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-1.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3.3 Sprint 2 | [ages-i-sprint-2](../../relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-2.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3.4 Sprint 3 | [ages-i-sprint-3](../../relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-3.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.3.5 Sprint 4 | [ages-i-sprint-4](../../relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-4.tex) | PASS | PASS com ressalvas documentadas | PENDING |
| 2.4. Conclusão | [chapter-02-text-h-0022](../../relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0022.tex) | PASS | PASS com ressalvas documentadas | PENDING |

Não há unidade omitida ou com divergência de conteúdo não resolvida. PASS técnico não equivale a aprovação humana. Tabelas/notas autorais: NOT_APPLICABLE, ausentes nesta edição.

## Falhas encontradas e corrigidas

| Achado | Evidência e correção | Verificação de retorno |
|---|---|---|
| CA-01, média: itálico da legenda 5 perdido | `text-p-0650`, conclusão: conversor restaurou a ênfase herdada do ODT e regenerou spans/hashes | Auditor independente conferiu caracteres/estilos e `.lof`; PDF final itálico |
| VAI01, alta: figuras dos protótipos interrompiam React | `main.tex`: mantenedor adicionou `FloatBlock` após protótipos; sem quebra obrigatória antes de Sprints | Figuras nas p5–6; tecnologias e item React completos na p7 |
| VAI02, alta: página quase vazia antes da reflexão Sprint 4 | `util/macros.tex`: `penalty0` atualiza o page builder antes de medir o espaço; permite, sem impor, quebra | Texto e caixa em fluxo na p14; todas as reflexões reinspecionadas |
| Validador: suporte restrito a um tab inicial | Três parágrafos técnicos e p0473 continham tabs adicionais; comparador ampliado para tokens explícitos 1:1, com contrato e sem normalização | Testes aceitam tokens corretos e rejeitam perda/deslocamento; 15 validações PASS |
| Verificador estático: quebra pré-textual vazava para Sprints | Estado de quebra passou a acompanhar arquivos incluídos, sendo consumido pelo título do capítulo | Regressões preservam bloqueio de quebra real, inclusive via arquivo vazio/intermediário |

## Pendências para o autor

| Pendência / gravidade | Localização e consequência | Encaminhamento e verificação |
|---|---|---|
| AI01/AI02 — diagramas ausentes, média | Banco e arquitetura: nenhum diagrama incorporado ao ODT | Autor fornecerá materiais; preencher placeholders em etapa posterior autorizada e conferir proveniência |
| AI03 — fontes das cinco imagens, alta | Figuras 1–5: não há indicação explícita de autoria/fonte | Apresentadas como fonte pendente; confirmar origem antes da versão final |
| AI04 — seis links de projeto, média | URLs preservadas, disponibilidade atual não comprovada | Usuário autorizou continuar com PENDING; repetir verificação remota quando possível |
| AI07/VAI03 — tabs internos, média | p0303/p0314/p0318, página 4 do PDF: avanços fixos de 1,251 cm criam lacunas legíveis, diferentes dos próximos tab stops ODF | Tokens e posições no texto preservados; autor revisa a representação visual. Não remover tabs por conta própria |
| AI06 — normativo/pré-textuais, alta | Conformidade ABNT integral e configuração final do memorial ainda dependem de verificação | Consultar STYLE_GUIDE/PENDENCIAS; não inferir vigência integral nem exigências da professora |
| AI08 — aprovação da edição, crítica para avanço | Todas as 15 unidades e o PDF identificado | Usuário aprova/reprova esta entrega; outra edição continua fora do escopo |

As cinco referências novas são documentações verificadas na consulta de 14/10/2026, em aparato separado da narrativa. Essa data não é data histórica do autor e não comprova versões utilizadas no projeto. Nenhum autor, ano ou versão foi inventado.

## Coordenação e isolamento

Dois conversores Codex trabalharam em worktrees reais separados: `/tmp/relatorio-ages-i-converter-a` (oito unidades) e `/tmp/relatorio-ages-i-converter-b` (sete unidades). Só o mantenedor alterou globais; curadoria entregou evidências separadas; integração por cherry-pick foi serial. O extrator mantém exclusivamente os overlays do manifesto. Auditores separados examinaram origem/resultado e PDF, sem modificar o memorial. Não houve alegação de execução Antigravity.

Os dois auditores gravaram seus pareceres finais e evidências antes de a execução das respectivas sessões terminar por limite de uso; a integração confere os arquivos, hashes e comandos efetivamente registrados. O erro de encerramento da sessão não foi tratado como validação adicional.

## Reprodução e limites

Em checkout limpo desta branch, com o cache/toolchain congelados já existentes:

```bash
python3 scripts/migration.py verify-source
python3 scripts/migration.py inventory --check
python3 -m unittest discover -s tests
python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex
python3 scripts/migration.py build --profile document
python3 scripts/migration.py visual --pdf build/document/main.pdf --dpi 150
```

Para cada ID da tabela: `python3 scripts/migration.py validate --ledger migration/ledgers/<ID>.json --unit <ID>`. O CLI visual retorna 3 por revisão humana pendente, mesmo quando suas ferramentas retornam 0; preparar renders não aprova o PDF. `build/` é local e ignorado pelo Git; PDFs, renders e auxiliares não foram integrados como fontes. Os scripts/manifesto/ledgers e logs locais identificados permitem repetir as verificações; nenhuma dependência nova foi instalada.

Rollback: conservar o checkpoint do piloto `68d159b9b4168f2a913f5c1e4913c30397310437` e os commits unitários da branch; reverter commits específicos em branch de trabalho, sem reset destrutivo, sem tocar no ODT ou na principal. Parar aqui e aguardar a aprovação humana da AGES I.
