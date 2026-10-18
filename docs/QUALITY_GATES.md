# Gates verificáveis

## Semântica dos resultados

**PASS** exige evidência executada; **FAIL** identifica divergência; **PENDING** significa ausência de prova ou decisão; **NOT_APPLICABLE** exige justificativa. Cobertura parcial não vira PASS total. Qualidade do harness e qualidade do memorial são resultados distintos. Fixtures sintéticas provam comportamento dos scripts, não integralidade do memorial.

| Gate | Evidência exigida | Critério / tratamento de falha |
|---|---|---|
| G0 — Origem | `verify-source`, baseline e status/diff | ODT com SHA-256 congelado; comparativo inalterado; nenhuma escrita fora de escopo |
| G1 — Inventário | `inventory`, `validate`, hashes e XPaths | ZIP íntegro; recursos referenciados presentes; IDs estáveis; ordem e descendentes de caixas/títulos examinados |
| G2 — Cobertura da unidade | Ledger e fonte extraída independentemente | Todo elemento pertencente à unidade corresponde a destino ou classificação justificada; unidade não convertida é PENDING |
| G3 — Texto e ordem | `validate --ledger ... --unit ...`; diff por elemento | Acentos, pontuação, símbolos e sequência preservados; não aceitar mero total de palavras. Exceção: reestruturação em prosa expressamente autorizada pelo usuário deve ser identificada como transformação, nunca como igualdade lexical, e exige auditoria independente de conteúdo antes da unidade passar |
| G4 — Mídia e URLs | Hash de arquivo, referência no destino, URL/âncora por elemento | Imagem correta e íntegra; URLs originais iguais e bem formadas; âncoras preservadas; links remotos não testados explicitamente continuam sem declaração de disponibilidade |
| G4a — Referências tecnológicas | Inspecionar as seções de banco de dados, arquitetura, protótipos e tecnologias contra o `.bib` e a evidência do curador | Cada produto/ferramenta nomeado aponta para uma referência verificada por chamada autor-data clicável; URL original permanece intacta; fonte sem metadados suficientes fica PENDING, sem autoria ou URL inventada |
| G4b — Forma da chamada | Extrair chamadas renderizadas do PDF e comparar com NBR 10520:2023, itens 6.1.1.1–6.1.1.4 | Fonte sem autoria usa o título no formato normativo: título de uma palavra sem supressão; título com várias palavras com primeira palavra + `[...]`; capitalização e pontuação corretas; sem reticências automáticas fora dos colchetes |
| G4c — Lista de referências | Inspecionar entradas repetidas para a mesma autoria/título e o PDF renderizado | Campos repetidos permanecem completos e legíveis, sem substituição por traços/sublinhados; opções efetivas do estilo bibliográfico são suportadas pela versão instalada |
| G5 — Estrutura LaTeX | `audit-latex`, grafo de inclusão e fontes completas | Sem arquivos omitidos, include indevido de Sprint, referências indefinidas, labels duplicados ou chave bibliográfica inexistente |
| G6 — Compilação | Build limpo, versões, log e relatório | Processador bibliográfico correto; índices resolvidos; sem erros, glifos ausentes, citações/referências indefinidas; overflow exige avaliação explícita |
| G7 — Visual | PDF identificado por hash, renders e relatório assinado pelo revisor | Todas as páginas legíveis; Sprints contínuas; títulos não órfãos; reflexões divisíveis; imagem, legenda e fonte em contexto; linha “Fonte:” centralizada segundo a apresentação aprovada; autoria continua pendente até identificação |
| G8 — Normativo | Matriz com fonte/edição/seção e medição do PDF | Exigências verificadas cumpridas; norma inacessível ou regra sem prova fica PENDING |
| G9 — Humano | Mensagem do usuário vinculada a commit/PDF/relatórios | Aprovação explícita após cada edição; piloto e Hoortech com decisão própria conforme plano |

## Expectativas da auditoria, não metas cegas

A origem auditada contém 25 títulos de Sprint, quatro edições como aluno e uma participação como cliente, 34 imagens/legendas, 17 caixas de reflexão com 48 parágrafos não vazios, 36 referências textuais e 39 siglas. O inventário XML registra 1.634 `text:p`, 123 `text:h`, 52 caixas, 86 quadros e 188 hyperlinks, dos quais 104 são de índices. Estas contagens usam categorias diferentes e não podem ser somadas como conteúdos independentes.

Checar expectativas contra o extractor atual e explicar diferenças de classificação. Não exigir que o LaTeX reproduza contêineres XML, títulos sem texto, números de índice antigos ou 116 páginas. Nunca ajustar os valores esperados para esconder perda. Índices regenerados e exclusões autorizadas precisam de classificação/justificativa rastreável.

## Equivalência textual estrita

Só aceitar transformações de serialização listadas e testadas pelo decodificador: caracteres reservados escapados, comandos tipográficos que exibem o mesmo conteúdo e marcadores explícitos de estrutura. Preservar o valor original no manifesto. Não remover acentos, pontuação, símbolos, caixa, números ou URLs para diminuir o diff. Não colapsar espaços/quebras semanticamente relevantes; justificar cada exceção.

Uma reestruturação narrativa autorizada é classificada separadamente da serialização textual. O validador pode conferir escopo, IDs, ordem, hyperlinks, chamadas e estrutura, mas não prova equivalência semântica. A unidade fica PENDING até um auditor independente comparar cada afirmação com a origem e registrar os conceitos preservados, alterações de apresentação e eventuais omissões/acréscimos. A regra corrente para prosa tecnológica está em `docs/STYLE_GUIDE.md`; não amplia o escopo de unidades autorizadas em `harness.json`.

Um parser conservador não é um motor TeX: macro desconhecida, texto oculto ou construção não suportada deve gerar falha/pendência. Extração do PDF complementa a comparação de fonte e a inspeção visual, mas hifenização, ordem de extração, glyph mapping e ligaturas impedem tratá-la como prova única. Não confiar no texto esperado escrito pelo próprio conversor como prova do texto efetivamente presente no destino.

## Limites automatizados

Regex de LaTeX não prova a saída de macros arbitrárias. Reconhecimento heurístico de reflexão/referência exige conferir IDs e fontes. Detecção de comandos de quebra identifica candidatos; inspeção da página decide se há quebra artificial. A disponibilidade de uma URL exige teste remoto e registro separado, não apenas análise sintática.

Auditor textual lê a origem independentemente do relatório do conversor. Auditor visual lê PDF/render real, não uma lista de avisos. A preparação de renders por `visual` não constitui inspeção humana completa. Relatório obrigatório: página/elemento, evidência, consequência, gravidade, correção proposta e verificação de retorno.

Na revisão dos parágrafos técnicos, cada produto/ferramenta deve ter sua fonte identificada por chamada para referência verificada, conforme `STYLE_GUIDE.md`. Na prosa de tecnologias, colocar a chamada junto à primeira menção substantiva em cada parágrafo coerente e repetir quando necessário para identificar uma nova atribuição, evitando duplicatas na mesma explicação contínua. A data de acesso pertence à entrada bibliográfica online, não é repetida como parte obrigatória de cada chamada autor-data. Um link original cuja fonte ainda não tem metadados continua PENDING e deve permanecer preservado sem uma citação bibliográfica inventada.

## Correção de prosa tecnológica — 17/10/2026

Nas três unidades autorizadas em `migration/approvals/ages-i-ii-iii-technology-prose-correction.json`, o gate exige: cobertura de todos os IDs e hashes de origem; rótulos e URLs retirados do corpo explicitamente inventariados; bibliografia intacta; citações adjacentes aos nomes com chaves existentes; ausência de rótulos `Documentação`, chamadas documentais repetidas, listas e quebras artificiais. Mais de um parágrafo natural é permitido, como na referência Mariah. O validador v2 deve rejeitar ledger legado nessas três unidades enquanto esta correção estiver vigente. A passagem técnica não prova a preservação dos fatos: a auditoria independente precisa comparar toda a prosa com o ODT e registrar omissões/acréscimos, sem confiar no relato do conversor. Inspecionar os hyperlinks internos de citações no PDF e os URLs nas referências. Os relatórios anteriores continuam históricos; a revisão desta correção fica em `docs/technology-review/`.

Se uma tecnologia exigir referência oficial que não estava hiperlinkada no ODF, a curadoria deve registrar a página e seus limites; a citação suplementar só pode ser integrada com autorização exata que identifique unidade, registro textual, termo, chave bibliográfica e URL. Essa autorização não substitui nem reescreve links originais. Sem autorização, a citação suplementar permanece PENDING. O validador deve aceitar apenas o conjunto e o hash bibliográfico expressamente autorizados.

## Gate da etapa parcial AGES IV

Para a entrega parcial de AGES IV, aplicar somente as 17 unidades identificadas em `migration/approvals/ages-iv-partial-authorization.json`. Conferir 287 IDs do inventário no escopo: as unidades do capítulo 6 cobrem 268 IDs, incluindo 11 imagens, 20 hyperlinks/âncoras e duas reflexões. Sete títulos do capítulo 6 sem corpo permanecem vazios. Em `chapter-07-text-h-0123`, somente `text-h-0123` é incluído; os outros 18 IDs listados em `authorized_title_only_inclusion.omitted_source_record_ids` são omissões deliberadas autorizadas, não conversões completas. O relatório de integridade deve separar: título presente, corpo omitido por decisão e conteúdo da seção futura pendente. A aprovação humana final permanece necessária mesmo que os gates técnicos passem.

As referências suplementares de App Store (`text-p-1332`) e TanStack Query (`text-p-1347`), ausentes como links no ODF, estão limitadas a `migration/approvals/ages-iv-supplemental-citations-authorization.json` e às URLs oficiais correspondentes em `migration/evidence/references/ages-iv.json`. Não extrapolar essa autorização para outros termos ou unidades; a aprovação final da edição continua pendente.

## Checkpoint

Gates automáticos aprovados não autorizam editorial nem próxima edição. Para aprovação, apresentar diff por Sprint, lacunas, alterações de representação, PDF e riscos restantes. Registro de aprovação sem evidência identificável do usuário é inválido. Mudanças no commit/PDF após aprovação invalidam o vínculo e exigem nova revisão dos efeitos.


## Complemento pré-textual e trajetória (17/10/2026)

- Confirmar o escopo suplementar contra `migration/approvals/ages-iv-frontmatter-authorization.json`: somente `pretext`, `resumo` e `chapter-01-text-h-0001`; manter os capítulos dos projetos inalterados.
- Conferir a ordem compilada: capa, Dedicatória, Agradecimentos, Epígrafe, Resumo, Lista de Ilustrações, Lista de Siglas, Sumário, trajetória e capítulos existentes. Elementos que seguem o padrão de páginas da referência Mariah começam em páginas próprias.
- Conferir as 39 entradas da lista de siglas na ordem do ODT, texto da trajetória, placeholders, bookmarks e exclusões das instruções genéricas por ID nos ledgers.
- Os campos genéricos `AGES I,II, III OU IV` e `Ano` da capa ficam deliberadamente sem decisão/autopreenchimento; resumo, dedicatória, agradecimentos e epígrafe não recebem texto autoral.
- Validação lexical PASS não equivale à inspeção visual. PDF de revisão deve ser renderizado e as páginas pré-textuais e a transição para a trajetória devem ser examinadas. Avisos de compilação bloqueiam o gate até serem investigados; aprovação humana permanece PENDING.

## Relocação Hoortech e reindexação do documento (17/10/2026)

Esta etapa depende de `migration/approvals/cliente-hoortech-and-document-order-authorization.json`, do hash imutável do ODT e do overlay `migration_overlay.document_order`. Não altera conteúdo narrativo das edições AGES I–IV.

| Gate | Critério de aprovação |
|---|---|
| H1 — Cobertura | Converter exatamente dez unidades Hoortech; conferir parágrafos, listas, três imagens e demais estruturas pelos IDs do ODT. Cada imagem preserva o hash original; as fontes ficam pendentes, sem atribuição inventada. |
| H2 — Ordem | `main.tex` compila a ordem: trajetória 1, AGES I 2, AGES II 3, AGES III 4, AGES IV 5, Hoortech 6, título final 7. Nenhum `setcounter` mascara a ordem nem reinicia capítulos/figuras artificialmente. |
| H3 — Mapeamento numérico | As 56 legendas de título e 29 legendas de figura cobrem exatamente os registros autorizados; cada texto final é derivado do texto ODF preservando sufixos/legendas. A única troca de prosa é `text-p-0679`, 3.2→6.2. Mudança fora dos 86 IDs reprova. |
| H4 — Figuras e referências | Conferir no PDF figuras consecutivas 1–34 (AGES I 1–5, AGES II 6–12, AGES III 13–20, AGES IV 21–31, Hoortech 32–34), lista de ilustrações, labels, `\ref`, contadores e links. |
| H5 — Conteúdo independente | O auditor relê o ODT congelado e compara as dez unidades Hoortech, imagens/legendas/listas/ênfases, além de conferir todas as trocas numéricas permitidas. O relatório do conversor não serve como evidência. |
| H6 — Visual integrado | O auditor examina o PDF completo por hash, com foco nas transições de capítulos 5→6→7, continuidade das Sprints Hoortech, títulos órfãos, figuras, fontes, sumário e lista de ilustrações. |
| H7 — Aprovação | Aprovação humana da participação Hoortech e da nova ordem permanece PENDING até manifestação explícita ligada aos artefatos finais. Não iniciar outra edição antes desse aceite. |

Resultado de cada gate: PASS, FAIL, PENDING ou NOT_APPLICABLE com evidência. Um manifesto ou JSON de autorização não substitui inspeção do conteúdo e do PDF.
