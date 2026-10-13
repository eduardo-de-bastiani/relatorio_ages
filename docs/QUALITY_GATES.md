# Gates verificáveis

## Semântica dos resultados

**PASS** exige evidência executada; **FAIL** identifica divergência; **PENDING** significa ausência de prova ou decisão; **NOT_APPLICABLE** exige justificativa. Cobertura parcial não vira PASS total. Qualidade do harness e qualidade do memorial são resultados distintos. Fixtures sintéticas provam comportamento dos scripts, não integralidade do memorial.

| Gate | Evidência exigida | Critério / tratamento de falha |
|---|---|---|
| G0 — Origem | `verify-source`, baseline e status/diff | ODT com SHA-256 congelado; comparativo inalterado; nenhuma escrita fora de escopo |
| G1 — Inventário | `inventory`, `validate`, hashes e XPaths | ZIP íntegro; recursos referenciados presentes; IDs estáveis; ordem e descendentes de caixas/títulos examinados |
| G2 — Cobertura da unidade | Ledger e fonte extraída independentemente | Todo elemento pertencente à unidade corresponde a destino ou classificação justificada; unidade não convertida é PENDING |
| G3 — Texto e ordem | `validate --ledger ... --unit ...`; diff por elemento | Acentos, pontuação, símbolos e sequência preservados; não aceitar mero total de palavras |
| G4 — Mídia e URLs | Hash de arquivo, referência no destino, URL/âncora por elemento | Imagem correta e íntegra; URLs originais iguais e bem formadas; âncoras preservadas; links remotos não testados explicitamente continuam sem declaração de disponibilidade |
| G5 — Estrutura LaTeX | `audit-latex`, grafo de inclusão e fontes completas | Sem arquivos omitidos, include indevido de Sprint, referências indefinidas, labels duplicados ou chave bibliográfica inexistente |
| G6 — Compilação | Build limpo, versões, log e relatório | Processador bibliográfico correto; índices resolvidos; sem erros, glifos ausentes, citações/referências indefinidas; overflow exige avaliação explícita |
| G7 — Visual | PDF identificado por hash, renders e relatório assinado pelo revisor | Todas as páginas legíveis; Sprints contínuas; títulos não órfãos; reflexões divisíveis; figuras/legendas/fontes corretas |
| G8 — Normativo | Matriz com fonte/edição/seção e medição do PDF | Exigências verificadas cumpridas; norma inacessível ou regra sem prova fica PENDING |
| G9 — Humano | Mensagem do usuário vinculada a commit/PDF/relatórios | Aprovação explícita após cada edição; piloto e Hoortech com decisão própria conforme plano |

## Expectativas da auditoria, não metas cegas

A origem auditada contém 25 títulos de Sprint, quatro edições como aluno e uma participação como cliente, 34 imagens/legendas, 17 caixas de reflexão com 48 parágrafos não vazios, 36 referências textuais e 39 siglas. O inventário XML registra 1.634 `text:p`, 123 `text:h`, 52 caixas, 86 quadros e 188 hyperlinks, dos quais 104 são de índices. Estas contagens usam categorias diferentes e não podem ser somadas como conteúdos independentes.

Checar expectativas contra o extractor atual e explicar diferenças de classificação. Não exigir que o LaTeX reproduza contêineres XML, títulos sem texto, números de índice antigos ou 116 páginas. Nunca ajustar os valores esperados para esconder perda. Índices regenerados e exclusões autorizadas precisam de classificação/justificativa rastreável.

## Equivalência textual estrita

Só aceitar transformações de serialização listadas e testadas pelo decodificador: caracteres reservados escapados, comandos tipográficos que exibem o mesmo conteúdo e marcadores explícitos de estrutura. Preservar o valor original no manifesto. Não remover acentos, pontuação, símbolos, caixa, números ou URLs para diminuir o diff. Não colapsar espaços/quebras semanticamente relevantes; justificar cada exceção.

Um parser conservador não é um motor TeX: macro desconhecida, texto oculto ou construção não suportada deve gerar falha/pendência. Extração do PDF complementa a comparação de fonte e a inspeção visual, mas hifenização, ordem de extração, glyph mapping e ligaturas impedem tratá-la como prova única. Não confiar no texto esperado escrito pelo próprio conversor como prova do texto efetivamente presente no destino.

## Limites automatizados

Regex de LaTeX não prova a saída de macros arbitrárias. Reconhecimento heurístico de reflexão/referência exige conferir IDs e fontes. Detecção de comandos de quebra identifica candidatos; inspeção da página decide se há quebra artificial. A disponibilidade de uma URL exige teste remoto e registro separado, não apenas análise sintática.

Auditor textual lê a origem independentemente do relatório do conversor. Auditor visual lê PDF/render real, não uma lista de avisos. A preparação de renders por `visual` não constitui inspeção humana completa. Relatório obrigatório: página/elemento, evidência, consequência, gravidade, correção proposta e verificação de retorno.

## Checkpoint

Gates automáticos aprovados não autorizam editorial nem próxima edição. Para aprovação, apresentar diff por Sprint, lacunas, alterações de representação, PDF e riscos restantes. Registro de aprovação sem evidência identificável do usuário é inválido. Mudanças no commit/PDF após aprovação invalidam o vínculo e exigem nova revisão dos efeitos.
