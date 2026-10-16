# Reauditoria independente final — AGES II

**PASS de preservação de conteúdo e das projeções de apresentação autorizadas.** Aprovação humana e aceitação da entrega **PENDING**. HEAD `339bba68563f739e622246cb3167c8a2532176bf` com alterações não commitadas; os hashes individuais no JSON identificam os bytes auditados.

PDF integrado: `build/document/main.pdf`, **40 páginas**, SHA-256 `c1ca761350f2ab8def3e458323f92c9717a9ca90e3eae2f362a80fc6e414648d`. Main SHA-256 `4c4affdedfbd456e699c0ce43ebe2c3795d569f3d2342c0e314da955318ea828`. Conferidos diretamente o hash do PDF e a igualdade de `source_files` do relatório de build com os 15 arquivos atuais, main, macros, estilo e bibliografia. Trata-se de `document-review`, gate oficial **NOT_RUN**; não foi alegado build limpo de produção.

ODT lido diretamente, SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. Extração e decodificação próprias, sem usar relatos de conversores ou pareceres anteriores como prova de conteúdo. Ledger usado somente para localizar intervalos candidatos.

| Conferência atual | Resultado |
|---|---|
| 150 blocos, cobertura, acentos, símbolos, pontuação e tokens de whitespace | PASS, preservados ou com projeção expressamente autorizada |
| Ordem | PASS, incluindo figura/legenda p0962 antes do texto próprio de p0961, conforme ordem inline do frame original |
| Hierarquia | PASS, 15 títulos reais; h0068 preservado como parágrafo conforme estilo efetivo normal de 12 pt |
| Cinco reflexões | PASS, todos os 15 parágrafos originais e sua ordem |
| Listas | PASS, 23 itens preservados; sete grupos de tecnologias no parágrafo contínuo autorizado |
| 13 hyperlinks e bookmarks | PASS, URLs exatas e âncoras autorizadas |
| Graph API | PASS da preservação literal no TeX e URI real na página 24: `https://developers.facebook.com/docs/graph-api/guides/explorer/` |
| Sete imagens/ocorrências/legendas | PASS, SHA-256 iguais aos membros correspondentes do ODT; prefixo Figura em negrito e título regular |
| Ênfases p0785/p0961/p0969/p0998 | PASS, correções conferidas diretamente contra os estilos efetivos do ODT |
| Placeholder do banco | PASS, um provisório, sem conteúdo/fonte inventados e fora da lista de figuras |
| .aux / lista de figuras | PASS, capítulo 4, Sprints 4.3.1–4.3.5 e figuras 9–15 |
| Main / contexto de figuras | PASS, 15 AGES I preexistentes + exatamente15 AGES II; sem Hoortech/III/IV; foto antes de 4.2 e protótipos antes das tecnologias |
| Gates estáticos / validação | PASS, quinze validações anteriores nesta auditoria; 13 arquivos inalterados e duas unidades alteradas novamente validadas (0); audit-latex/verify-source novamente (0) |
| Disponibilidade Graph API/projetos, fontes das sete imagens e diagrama real | PENDING |
| Normas, inspeção visual integral e aprovação humana | PENDING |

## Retorno das correções, com histórico preservado

O PDF anterior desta auditoria, `835cf3b35045f4ed2977bb84736dd2b259fd267be8c0362589fd625d6b5ef932`, teve **FAIL** de ênfase. O histórico permanece no JSON e os arquivos `*_INITIAL.*` foram preservados e reconferidos por hash.

- **AII-CONTENT-F01 — resolvido/PASS**, `chapter-04-text-h-0044`, p0785: o ODT usa `Strong_Emphasis → T226`, cujo `fo:font-weight="normal"` sobrepõe o negrito externo. O alvo atual remove o negrito acrescentado em Angular, FastAPI e PostgreSQL; todas as 24 letras agora concordam com a fonte efetiva. Texto, pontuação e espaços continuam iguais.
- **AII-CONTENT-F02 — resolvido/PASS**, `ages-ii-sprint-4`, p0961 e p0969: `Strong_Emphasis → T286` mantém peso normal e sublinhado sólido sobre cada frase completa. O alvo atual usa um grupo por frase, incluindo seus seis e quatro espaços; as dez interrupções antes apontadas foram eliminadas. Os marcadores `originalleadbreak` permanecem fora do grupo e preservados.
- **AII-CONTENT-O01 — resolvido/PASS**, p0998: `Strong_Emphasis → T43` abrange “memory leak”, inclusive o espaço em itálico; o alvo atual usa um único `textit{memory leak}`, concordando também no estado desse espaço.

A única diferença de fonte de whitespace remanescente na comparação mecânica são os tabs iniciais sem glifo de p0765/p0984, cobertos pela projeção de indentação autorizada. Não há perda de palavra, pontuação ou ênfase visível. Os sete títulos de figuras estão regulares por decisão de apresentação aprovada; isso não é uma omissão de itálico.

## Evidências e limites

Nesta rodada foram relidos diretamente os **15 arquivos atuais** e reextraído o ODT. Apenas as unidades de arquitetura e Sprint 4 mudaram desde a conferência anterior; ambas receberam novamente `validate --ledger … --unit …` com saída 0. A nova comparação própria dos 150 blocos, ordem lógica, links, hashes das sete mídias, reflexões e estrutura passou. `verify-source` e `audit-latex --root relatorio_AGES_eduardo --entry main.tex` foram repetidos com saída 0. As anotações URI e o contexto de figuras foram lidos do PDF final com pypdf; o relatório de build aponta compilação review exit0. Comandos, hashes por arquivo/artefato e detalhes do histórico constam dos JSONs pareados.

O conteúdo das outras edições não foi reauditado: as 15 unidades AGES I preexistentes aparecem no main integrado, e nenhuma unidade Hoortech/AGES III/AGES IV foi incluída. A seção tecnológica conserva os sete grupos na ordem original; “Documentação Docker” permanece texto sem link inventado. Graph API mantém seu endereço literal, sem referência bibliográfica não comprovada. Datas bibliográficas em 2024 são convenções atribuídas por autorização, não histórico recuperado nem prova de publicação.

Esta auditoria de conteúdo não substitui a inspeção visual integral nem certifica ABNT integral. Fontes/autoria das sete imagens, disponibilidade remota, diagrama real e aprovação humana continuam **PENDING**. Não autoriza outra edição ou revisão editorial.

Arquivos alterados pelo auditor: somente `CONTENT_AUDIT.md`, `CONTENT_AUDIT.json` e `TEXT_DIVERGENCES.json`; evidências locais em `build/ages-ii/audit-final/`. Nenhum TeX, ledger, manifesto, pendência global ou commit foi alterado pelo auditor. Mudanças posteriores exigem reavaliar seus efeitos e o vínculo com o PDF.
