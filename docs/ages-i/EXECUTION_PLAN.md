# AGES I / Easy Choose — plano de execução controlada

Autorização do usuário: iniciar somente AGES I e utilizar placeholders para os diagramas ausentes de arquitetura e banco de dados. Baseline `68d159b9b4168f2a913f5c1e4913c30397310437`, branch `migration/ages-i`. A principal, o ODT e o comparativo permanecem preservados; o PDF do piloto foi copiado para `build/pilot/review-snapshot/` antes da futura integração.

## Escopo confirmado antes da conversão

Extração direta de `content.xml` e `styles.xml`, entre `text-h-0002` e o início de Hoortech (`text-h-0023`): 15 unidades, 102 blocos textuais, cinco imagens/legendas, 11 hyperlinks e cinco reflexões. Não há tabela nem nota. Os 11 links são três repositórios, três wikis e cinco documentações tecnológicas. A contagem preliminar de 12 hyperlinks foi corrigida pela extração XML, sem alterar a fonte.

| Ordem | Unidade original | ID do manifesto | Textos |
|---|---|---|---:|
| 1 | Título da edição | chapter-02-text-h-0002 | 1 |
| 2 | Introdução | chapter-02-text-h-0003 | 5 |
| 3 | Desenvolvimento do Projeto | chapter-02-text-h-0007 | 1 |
| 4 | Repositório do código Fonte do Projeto | chapter-02-text-h-0008 | 7 |
| 5 | Banco de dados utilizado | chapter-02-text-h-0009 | 3 |
| 6 | Arquitetura utilizada | chapter-02-text-h-0010 | 3 |
| 7 | Protótipos das telas desenvolvidas | chapter-02-text-h-0011 | 7 |
| 8 | Tecnologias utilizadas | chapter-02-text-h-0012 | 20 |
| 9 | Atividades desempenhadas pelo aluno no projeto | chapter-02-text-h-0014 | 1 |
| 10 | Sprint 0, revalidar piloto | ages-i-sprint-0 | 10 |
| 11 | Sprint 1 | ages-i-sprint-1 | 12 |
| 12 | Sprint 2 | ages-i-sprint-2 | 7 |
| 13 | Sprint 3 | ages-i-sprint-3 | 9 |
| 14 | Sprint 4 | ages-i-sprint-4 | 7 |
| 15 | Conclusão | chapter-02-text-h-0022 | 9 |

Os destinos por unidade são os já registrados no manifesto em `relatorio_AGES_eduardo/conteudo/migracao/`. Títulos sem texto de desenvolvimento são contêineres estruturais, não lacunas a completar. Preservar títulos, pontuação e erros autorais. A numeração mistura prefixos ODF gerados e indicativos digitados manualmente; o extrator documentou a diferença. Cinco tecnologias correspondem a cinco bullets, com parágrafos de continuação. Quebras suaves armazenadas e contêineres vazios não criam páginas artificiais.

## Dependências e distribuição

1. EXTRATOR delimita elementos, estilos, listas, legendas/âncoras e mídia. Evidências em `build/ages-i/extraction/`; inventário original permanece imutável.
2. MANTENEDOR é o único escritor de `main.tex`, `util/**` e `.bib`. Prepara entradas das 15 unidades, sumário/lista de figuras, captions literais, fontes pendentes e placeholders não numerados. Não traduzir o prefixo original `Figure` nem atribuir autoria inexistente.
3. CURADOR verifica as cinco documentações e registra os seis links de projeto separadamente. Só o mantenedor integra metadados bibliográficos com evidência; não inserir citações novas dentro da narrativa original.
4. Após resolver o bloqueio abaixo, criar até dois worktrees separados a partir do mesmo checkpoint global. Conversor A: unidades 1–8 e suas quatro imagens; conversor B: unidades 9–15, incluindo revalidação da Sprint 0 e imagem da conclusão. Cada um escreve exclusivamente arquivos/ledgers/assets atribuídos, sem arquivos compartilhados. Se isolamento não estiver demonstrado, executar serialmente.
5. Integrar uma unidade por vez, executar verificação textual/mídia/URLs, auditoria independente, compilação em contexto e inspeção visual. Divergência não resolvida impede concluir a unidade.
6. Consolidar somente a edição AGES I; auditar as 102 correspondências, cinco imagens, 11 links, cinco reflexões, hierarquia e continuidade das Sprints. Gerar PDF e registrar overlay de rastreabilidade pelo extrator. Não incluir Hoortech ou outra edição.

Imagens terão arquivos originais com SHA-256 e posse por unidade. O aparato de fonte desconhecida precisa ser identificado como pendência, nunca como autoria presumida. Placeholders de banco/arquitetura são provisórios, fora da lista de figuras reais. Alteração de macro global exige atualizar contratos e revalidar o piloto. PDFs de checkpoints precisam de caminhos imutáveis por hash, para não invalidar evidências ao recompilar a edição.

## Bloqueio de referências — orientação solicitada

As cinco documentações oficiais foram verificadas; novas propostas bibliográficas contêm somente título, URL e data da consulta atual documentada, sem autor/ano presumidos. Os seis links de projeto não tiveram disponibilidade atual comprovada: navegação indisponível nas ferramentas e falha de DNS nos testes HTTP locais. Isso não prova link quebrado nem autenticação obrigatória.

A missão exige interrupção quando uma referência não puder ser verificada. Foi solicitado ao usuário escolher entre preservar literalmente os seis links com disponibilidade PENDING e prosseguir, ou aguardar verificação. **Usuário respondeu: “Preservar links e continuar com a pendência registrada (recomendado)”. Bloqueio de execução resolvido; disponibilidade dos seis links permanece PENDING.** A alternativa recomendada não transforma esses links em referências verificadas e mantém os placeholders já autorizados.

Curadoria: `migration/evidence/references/ages-i.json`. Pendências adicionais: autoria/fontes das cinco imagens; diagramas não incorporados; conformidade normativa integral. Não há evidência de conteúdo ilegível ou incompleto nos textos da edição. Aprovação da entrega continua humana e posterior.
