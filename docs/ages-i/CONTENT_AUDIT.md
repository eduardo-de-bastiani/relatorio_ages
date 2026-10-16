# Auditoria independente de conteúdo — proposta de estilo Mariah / AGES I

**PASS para preservação de conteúdo; entrega e aprovação humana PENDING.** HEAD real `e5a367d438fe865223879ed4742d52379e563335`, branch `migration/ages-i`, árvore modificada. PDF candidato: SHA-256 `9670b53640a3b2f67977100bc51fd381af56403d96b941f15f6e37252aa04d38`, 19 páginas. Commit de build `e1019ac9d7ecd3cb8a97388c4b50a4805732c074` existe somente no clone isolado; não é commit da branch real.

Um subagente Codex separado extraiu diretamente ZIP/XML do ODT imutável (`e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`) e usou seu próprio decodificador TeX conservador. Os ledgers forneceram apenas intervalos candidatos; os bytes reais foram comparados ao XML, sem confiar em texto esperado do conversor. Não houve execução Antigravity.

| Verificação | Resultado |
|---|---|
| Texto, acentos, símbolos, pontuação, ênfases e ordem | PASS: 102 blocos, incluindo 15 títulos, 82 parágrafos de corpo e cinco legendas, comparados por caractere |
| Gates executáveis | PASS: 15 validações, verify-source e audit-latex, todos exit 0 |
| Escopo da apresentação | PASS: 82/82 IDs autorizados e somente eles possuem reference_paragraph_layout |
| Estrutura integral | PASS: mesmos cinco ambientes de reflexão com 17 parágrafos; listas, âncoras e demais estrutura conservadas |
| Mídia, URLs e bibliografia | PASS: cinco hashes ZIP iguais; 11 âncoras/URLs originais e cinco URLs bibliográficas no PDF; cinco registros curados intactos |
| Sumário, títulos e contadores | PASS: 15 títulos/counters no corpo; 16 entradas brutas; profundidade 1 altera somente exposição do índice |
| Legendas e lacunas | PASS: cinco legendas literais em itálico; dois placeholders claramente provisórios e fora da lista de figuras |
| Build identificado | PASS: fontes do build isolado iguais às auditadas; PDF/aux/índices/URIs examinados; auditor não recompilou |
| Visual, normas integrais e aceite humano | PENDING; auditoria textual não os presume |
| Disponibilidade remota e autoria das imagens | PENDING |

A instrução vigente pede: “Batendo com o relatório da Mariah, estamos utilizando a mesma formatação? Eu gostaria de usar a mesma formatação que ela”, em `migration/approvals/ages-i-mariah-style.json`. A solicitação anterior de correção e de aprovação antes de tornar permanente continua registrada em `migration/approvals/ages-i-format-correction.json`. Execução autorizada não equivale a aceite nem a padrão futuro.

Todos os **15 arquivos TeX completos** são idênticos byte a byte ao baseline após reversão apenas de 59 declarações `\indent` para `\noindent`, nove nomes `originalinlinetab` para `originaltab` e um `originalleadingspace` para `originalspace`. Isso verifica também estruturas fora dos intervalos de texto. Os nove tabs internos de `text-p-0303`, `text-p-0314` e `text-p-0318` continuam rastreados nas posições originais e imprimem espaço normal. Tabs iniciais usam `originaltab`, agora de avanço zero; somente o espaço inicial de `text-p-0413` usa `originalleadingspace`, também zero. Os outros espaços explícitos permanecem intactos. O decoder recupera os tokens originais; **não se afirma igualdade literal do whitespace visível no PDF**. Os 11 parágrafos de hyperlink integral e as listas conservam alinhamento estrutural; 59 parágrafos de corpo/reflexão passam a usar recuo da proposta.

Sumário com profundidade 1 é alteração explícita de apresentação: subseções/Sprints continuam no corpo e nos arquivos derivados, embora ausentes do sumário renderizado. Os 15 títulos foram confrontados com o XML, inclusive indicativos e pontuação; o whitespace de prefixos é separado como metadado no índice, sem alegar igualdade literal de espaçamento visual. Referências continuam como aparato pós-textual curado; nenhuma redação da Mariah foi transferida.

Macros SHA-256 `811761e2b49067cfda51438c243ae40bf816c8d5375fad229a43cdc70306c28f`; estilo `0cc5717a271e90029f9eece3bdaf841945e87fb72c416994318996a5b7fcb24f`. Hashes individuais e comandos constam no JSON e em `build/ages-i/mariah-style/content-audit/`. Executados `compare.py` (extração XML própria e 15 validates), `details.py`, `final_checks.py` e `index_checks.py`, além de verify-source e audit-latex; saídas finais 0. Duas chamadas iniciais dos drivers falharam por dependência ainda não concluída e caminho de relatório incorreto; foram repetidas com sucesso, sem alteração das fontes.

O histórico permanece no JSON e em snapshots locais. CA-01 (itálico da legenda 5) continua resolvido. PDF `c9621f…` teve preservação textual aprovada tecnicamente, mas apresentação rejeitada pelo usuário; o tratamento anterior de G7 foi inadequado. A proposta intermediária `b51646a9…` também não recebeu aceite e precede o pedido de igualar a Mariah. Nenhum PASS textual certifica igualdade visual nem aprovação humana.

Arquivos alterados pelo auditor: somente `docs/ages-i/CONTENT_AUDIT.md` e `.json`; scripts/resultados locais no runtime atribuído. Nenhum memorial, ledger, manifesto, macro ou estilo foi editado. Mudanças posteriores requerem revalidar efeitos. **Aprovação do candidato, promoção permanente e avanço a outros projetos permanecem PENDING.**
