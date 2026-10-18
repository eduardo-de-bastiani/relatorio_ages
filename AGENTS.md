# Regras do harness de migração

## Escopo e autoridades

**Fase vigente, autorizada pelo usuário em 17/10/2026:** integrar a participação como cliente Hoortech após a conclusão da AGES IV e antes do título final, renumerando capítulos e figuras em sequência. O escopo da tarefa suplementar é exatamente o autorizado em `migration/approvals/cliente-hoortech-and-document-order-authorization.json` e rastreado no overlay do `docs/CONTENT_MANIFEST.json`: dez unidades Hoortech, renumeração de 56 títulos e 29 legendas (86 IDs mapeados) em 56 unidades e a atualização exata de uma referência textual. AGES I, o conteúdo narrativo de AGES II–IV, a capa/pré-textuais e o texto da trajetória não recebem alterações nesta tarefa. A compilação e a aprovação humana de toda a ordem continuam pendentes.

O capítulo 7 (“Considerações finais (Somente AGES IV)”) continua incluído somente como título; seus dez parágrafos e estruturas de lista permanecem deliberadamente omitidos e pendentes. O checkpoint enviado pelo usuário está na branch `migration/ages-iii`; baseline local confirmado para esta ampliação: `8f952a6e3b64c8783cef823e52ed2451af653eae`. Não criar commit nem fazer push desta ampliação sem instrução específica. Conversões paralelas anteriores usaram cópias temporárias sem histórico Git; a integração desta ampliação é serial e não será descrita como delegação independente Antigravity.

**Decisão permanente de apresentação:** as seções de tecnologias de AGES I/II/III foram corrigidas conforme o PDF da Mariah, nos escopos registrados em `migration/approvals/ages-i-ii-iii-technology-prose-correction.json`. O padrão de prosa por função, com citações junto aos nomes e sem rótulos documentais repetidos, é a referência para AGES IV conforme `docs/STYLE_GUIDE.md`.

Histórico de escopo: AGES III / Controle Inteligente de Estacionamento com RFID foi autorizada em 16/10/2026, e a prosa de tecnologias das três edições foi corrigida em 17/10/2026. Os registros e relatórios anteriores são históricos; esta tarefa reabre exclusivamente a ordem do documento e as numerações explicitamente mapeadas na autorização Hoortech.

Registro histórico: em 16/10/2026, o usuário autorizou correções de apresentação/citações nos trechos técnicos `chapter-02-text-h-0009`–`0011` (AGES I) e `chapter-04-text-h-0043`–`0046` (AGES II), além da macro global de fonte de figuras, registradas em `migration/approvals/ages-i-ii-formatting-authorization.json`. Essas alterações estão concluídas no checkpoint aprovado `abe761c`; as convenções são reutilizáveis conforme `docs/STYLE_GUIDE.md` e `docs/QUALITY_GATES.md`. O escopo de execução vigente é definido pelo parágrafo acima e por `harness.json`.

Leia [CONTEXT](docs/CONTEXT.md), [plano](docs/MIGRATION_PLAN.md), [estilo](docs/STYLE_GUIDE.md), [gates](docs/QUALITY_GATES.md) e [pendências](docs/PENDENCIAS.md). O `harness.json` define caminhos e escopos executáveis; os documentos explicam sua finalidade. Em divergência, interrompa a tarefa afetada e registre a diferença; não amplie permissões.

Autoridades, nesta ordem: instruções explícitas do usuário; original imutável para conteúdo; normas verificadas para apresentação; decisões aprovadas de apresentação. `relatorio_mariah/` é a métrica de qualidade visual definida pelo usuário, somente para leitura. Não transferir narrativa, projetos, referências, epígrafe ou metadados pessoais da Mariah. O modelo restrito da Biblioteca PUCRS foi dispensado pelo usuário e não é dependência.

## Invariantes

Escopo desta ampliação: dez unidades Hoortech e somente os 86 IDs da autorização suplementar (56 títulos, 29 legendas e a referência `text-p-0679`). A ordem de capítulos autorizada é: trajetória=1, AGES I=2, AGES II=3, AGES III=4, AGES IV=5, Hoortech=6 e título final=7. As figuras devem ficar em AGES I 1–5, AGES II 6–12, AGES III 13–20, AGES IV 21–31 e Hoortech 32–34. A edição parcial de Recorda conserva Sprints 2–4 e Conclusão como títulos vazios; o corpo do capítulo 7 permanece omitido. Não reabrir ou completar esses textos. A aprovação humana da ordem/documento final é obrigatória.

- Não revisar português, expandir, completar ou corrigir fatos nesta fase ou na conversão fiel. A reformulação gramatical estritamente necessária nas três seções de tecnologias acima está autorizada, com auditoria independente de todos os fatos e qualificadores.
- Preservar acentos, símbolos, pontuação, sequência, âncoras e URLs. Contagem de palavras não comprova integridade.
- Nunca modificar `RELATORIO_ATUAL.odt`; SHA-256 esperado: `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`.
- Não editar `relatorio_mariah/`. Não confiar em auxiliares/PDFs antigos como prova de compilação.
- Sprints continuam o fluxo: `\input` e título de subseção; nenhuma quebra obrigatória antes do título.
- Diagramas ausentes recebem, na fase autorizada, placeholders visuais claramente provisórios; não inventar seus conteúdos nem suas fontes.
- Reflexões conservam texto e borda, usam a mesma fonte do corpo e admitem divisão entre páginas.
- Aplicar o padrão visual aprovado em `docs/STYLE_GUIDE.md`, distinguindo decisões do usuário, escolhas da referência Mariah, boas práticas técnicas e requisitos normativos verificados.
- Para AGES III, não inventar nem retrodatá-las: a data de acesso de cada fonte deve ser a data real da curadoria. A decisão anterior do usuário permite usar o ano de acesso como rótulo autor-data; isso não prova nem substitui a data factual de publicação. Não inventar autores, versões ou URLs. Fontes AGES III não verificadas ficam PENDING; por decisão explícita de 16/10/2026 registrada em `migration/approvals/ages-iii-pending-references-acceptance.json`, a conversão fiel pode prosseguir preservando URLs e sem criar metadados. Os gates de referência das unidades afetadas continuam PENDING, não PASS.
- Exceção de apresentação vigente nas três seções de tecnologias: seguir `migration/approvals/ages-i-ii-iii-technology-prose-correction.json`. A igualdade lexical não se aplica à prosa reformulada; a integridade factual exige auditoria independente. Os registros anteriores permanecem históricos, inclusive a remoção específica do tab interno em `text-p-1084`; nenhuma normalização genérica é autorizada.
- Revisão editorial e complementações são outra fase.
- Exigir aprovação humana após cada edição AGES e checkpoint próprio para a participação Cliente Hoortech. A autorização desta migração não aprova o resultado final.

## Responsabilidade e escrita

Os sete papéis estão em [docs/agents](docs/agents). Só o EXTRATOR mantém o manifesto; só o MANTENEDOR LATEX escreve estilos/macros/configuração globais. CONVERSORES escrevem apenas a unidade e o ledger atribuídos; o título do capítulo 7 é uma inclusão parcial autorizada, e seus 18 IDs omitidos permanecem explícitos no registro de escopo. Curadoria entrega evidências separadas; integração central é serial. Auditores emitem relatórios sem corrigir o memorial diretamente.

O ORQUESTRADOR coordena e integra; não reescreve conteúdo. Nesta tarefa, CONVERSORES possuem somente os dez arquivos/ledgers Hoortech e três imagens atribuídas; o EXTRATOR mantém o manifesto; o MANTENEDOR LATEX é o único autorizado a alterar `main.tex` para a nova ordem; o ORQUESTRADOR integra os 86 mapeamentos numéricos e a referência `text-p-0679` somente segundo a autorização exata. A posse de arquivo deve ser registrada antes da execução; duas tarefas não podem possuir o mesmo caminho. Cópias temporárias sem `.git` são isolamento de diretório, não worktrees nem sandbox. Integre serialmente. Locks são cooperativos; não executar comandos não confiáveis sob essa alegação.

Antes e depois de cada tarefa: verificar fonte e escopo, registrar diff e executar os gates correspondentes. Falhas ou cobertura ausente não podem ser convertidas em aprovação automática. Relatórios devem distinguir PASS, FAIL, PENDING e NOT_APPLICABLE com justificativa. Registrar ferramenta, comando, código de saída, commit e hashes dos artefatos.

## Checkpoints e entrega

Faça commits pequenos na branch de trabalho somente quando autorizado. Não sobrescreva trabalho de terceiros, faça reset destrutivo, mude a branch principal ou invente aprovação humana. Uma aprovação precisa de evidência identificável do usuário; um campo JSON sozinho não é autorização.

Artefatos locais ficam em `build/`, conforme configuração. O inventário rastreado não contém arquivos extraídos de mídia redundantes. Não incluir caches, credenciais, PDFs de teste ou auxiliares na integração. Consultar o plano para rollback por commit e reprodução limpa.

Ao concluir: listar arquivos alterados, comandos realmente executados, resultados e limitações. Não declarar agentes Antigravity independentes quando houve execução sequencial ou subagentes de outra ferramenta. Entregar o PDF de revisão com auditorias independentes e aguardar aprovação humana da participação Hoortech e da ordem global; não iniciar outra edição nem preencher o corpo do capítulo 7.
