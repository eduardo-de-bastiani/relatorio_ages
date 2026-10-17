# Plano da etapa parcial — AGES IV / Recorda

Data: 17/10/2026. Escopo autorizado: `migration/approvals/ages-iv-partial-authorization.json` e `harness.json`.

O usuário informou que a edição está pronta até a Sprint 1, inclusive, e pediu que Sprints 2–4 e Conclusão permaneçam com título para preenchimento posterior. Não converter conteúdo além dessas unidades.

## Inventário do escopo

`docs/CONTENT_MANIFEST.json` contém 17 unidades selecionadas: 16 unidades estruturais/textuais do capítulo 6 e a unidade parcial do capítulo 7. O conjunto soma 287 IDs distintos: 78 parágrafos narrativos no capítulo 6 e dez parágrafos do capítulo 7 autorizados para omissão, 11 parágrafos de legenda, 17 títulos de capítulo/seção, um subtítulo de retrospectiva, 11 imagens, 20 hiperlinks, 13 caixas de texto, 61 contêineres de lista, 49 itens de lista e 16 cabeçalhos de lista. Há duas reflexões pessoais e nenhum registro de tabela no escopo. `python3 scripts/migration.py inventory --check` foi concluído com PASS e sem diferenças; `verify-source` confirmou o SHA-256 esperado do ODT.

Unidades com conteúdo: `chapter-06-text-h-0106`, `chapter-06-text-h-0108`–`0110`, `chapter-06-text-h-0112`–`0114`, `ages-iv-sprint-0` e `ages-iv-sprint-1`.

Unidades estruturais: `chapter-06-text-h-0105`, `chapter-06-text-h-0107`, `chapter-06-text-h-0115`, `ages-iv-sprint-2`–`ages-iv-sprint-4` e `chapter-06-text-h-0122`. `chapter-07-text-h-0123` é parcial: mapear o título e registrar a omissão autorizada dos dez parágrafos/estruturas restantes.

A distribuição das 11 imagens e seus IDs de arquivo está registrada em `harness.json`: foto da equipe (1), diagramas de banco e arquitetura (2), protótipos (4), artefatos EAP/RACI (2), imagens da Sprint 0 (2). Atribuição de fonte permanece pendente até confirmação humana. Os vinte hyperlinks incluem âncoras vazias e visíveis; preservar cada destino e a relação com seu texto conforme ODF/ledger. Em 17/10/2026, o usuário autorizou prosseguir com os cinco destinos de repositórios/wikis sem conteúdo verificável, mantendo os sete registros de link e disponibilidade `PENDING`; a decisão e os URLs originais estão em `migration/approvals/ages-iv-pending-references-acceptance.json`.

## Sequência e dependências

1. Curadoria consulta os links originais de tecnologias e documenta metadados, autoria e destinos efetivamente verificados; não edita a bibliografia compartilhada.
2. Conversor migra as unidades textuais, imagens, hyperlinks, legendas, listas e reflexões. A seção de tecnologias segue o padrão aprovado da Mariah, com citações ao lado das tecnologias e relação explícita com o uso no Recorda, sem completar fatos ausentes.
3. Mantenedor integra centralmente somente as novas entradas bibliográficas sustentadas pela curadoria e conecta as 17 unidades na ordem correta em `main.tex`. Macros/estilos globais permanecem sob sua responsabilidade exclusiva.
4. Auditor de conteúdo compara o ODF original diretamente com cada unidade e o PDF, sem usar o relato do conversor como prova. Auditor visual revisa o PDF completo e páginas de transição, reflexões, imagens e títulos vazios.
5. Corrigir falhas confirmadas, recompilar, renovar auditorias necessárias e apresentar o PDF com hash para aprovação humana.

O branch dedicado não pôde ser criado no repositório porque `.git` está somente para leitura. Para obter isolamento efetivo, serão criadas duas cópias temporárias completas do estado autorizado em `/tmp`, uma por conversor, com unidades e assets sem interseção. Cada tarefa executa e registra seus próprios gates; a integração para o branch não principal observado, `migration/ages-iii`, será serial. Os commits temporários servem apenas para dar ao wrapper um baseline limpo nas cópias descartáveis; não alteram o histórico do repositório do usuário.

## Decisão explícita sobre o capítulo 7

O usuário respondeu “Incluir apenas o título”. A origem conserva `7 - CONSIDERAÇÕES FINAIS (Somente AGES IV)`; na apresentação, aplicar `7 CONSIDERAÇÕES FINAIS (Somente AGES IV)`, sem sinal entre indicativo e título, conforme NBR 6024:2012, item 4.1(d), registrando a transformação no ledger. Aplicar a mesma normalização a `6 - PROJETOS AGES IV - RECORDA `: o hífen entre o número 6 e o título não aparece no resultado, mas o hífen interno em `AGES IV - RECORDA` permanece. Omitir nesta entrega os dez parágrafos `text-p-1539`–`text-p-1547` e `text-p-1549`, além dos contêineres `text-list-0280/0281` e itens `text-list-item-0225`–`0230`. Registrar a unidade como parcial, não como conteúdo integralmente migrado. A futura redação depende do usuário; não inferir ou reutilizar os textos de orientação do ODT.

Sprints 2–4 e Conclusão do capítulo 6 são títulos originais vazios e devem aparecer como estrutura, sem placeholder narrativo nem texto inventado. A ausência de conteúdo nessas unidades é intencional nesta etapa.
