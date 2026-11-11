# Diagnóstico do build de revisão — 11/11/2026

## Correções aplicadas

Após autorização do usuário, o mantenedor ampliou o campo dos números de página para `2em`, mantendo a borda direita dos números alinhada à margem. As duas âncoras ODF vazias passaram a comentários de origem com ID e URL preservados no ledger. As novas URLs visíveis receberam pontos de quebra após hífens já existentes; a chamada longa de banco de dados da AGES III recebeu alinhamento local à esquerda. Nenhum limiar de aviso foi elevado, e não houve supressão de diagnósticos.

O build final `./build.sh --profile document-review` terminou com **retorno 0, `status: pass` e `findings: []`**: zero `OVERFULL`, zero `UNDERFULL` e zero avisos `hyperref`. PDF de 116 páginas: `build/document/main.pdf`, SHA-256 `3a71ba163dfd72c03b8cc928e255a36e81c6bdc71e0f649386b8883e97d3adf4`. Auditor independente conferiu os números de três dígitos nas páginas 7 e 12 e as URLs longas nas páginas 55 e 57; todos os 20 destinos aparecem nas anotações URI. A inspeção visual foi pontual. Isto aprova o gate técnico deste perfil de revisão; a aprovação humana e a conformidade global do memorial continuam separadas.

## Diagnóstico anterior às correções

PDF originalmente examinado: SHA-256 `044d8d09e005f9c9ea54e2871ae7b918b28364883ccfa47381f08cb381347fbc`, 115 páginas A4. O compilador retornava **0**, mas o gate era **FAIL** devido aos avisos abaixo. A tabela preserva a causa e a recomendação do diagnóstico inicial; ambos os itens estão agora corrigidos.

| Ocorrência | Local e evidência | Efeito real | Correção técnica futura | Estado |
|---|---|---|---|---|
| 17 `Overfull \hbox (1.41573pt too wide)` | `build/document/main.log` e entradas `main.lof:37–39` (páginas 102, 109, 111) + `main.toc:81–82,85–94,97,100` (páginas 100–113) | São **exclusivamente números de página com três dígitos** no sumário/lista de ilustrações. Excedem a margem de texto em cerca de 0,5 mm; o PDF mantém todos os dígitos visíveis e dentro da folha. Não representam parágrafos ou figuras cortados. | Ampliar o campo reservado ao número de página no sumário e na lista de ilustrações, depois verificar alinhamento e paginação visualmente. Somente o mantenedor LaTeX deve alterar a configuração global. | Problema pequeno, porém real; gate FAIL até correção ou aceitação justificada. |
| 2 `Package hyperref Warning: Suppressing empty link on input line 12` | `chapter-06-text-h-0109.tex:12` e `chapter-06-text-h-0110.tex:12` | Ambos são `\href` com conteúdo **vazio** herdado da estrutura ODT. `hyperref` não cria uma anotação clicável sem texto. Os links visíveis de Banco de Dados e Arquitetura, nas linhas 18 dos mesmos arquivos, continuam presentes. | Preservar destino/ID no ledger e deixar de emitir os `\href` vazios, mediante suplemento e teste de preservação; não remover os links visíveis. | Aviso técnico sem perda de texto visível; gate FAIL até correção ou aceitação justificada. |

O primeiro item foi confirmado pelo texto exato de cada caixa no log (`102`–`113`) e pela geometria extraída com Poppler do PDF; o segundo, pelo código das linhas indicadas e pelas anotações de URL presentes no PDF. Não foram acessados links remotos. O histórico foi preservado; o resultado vigente está na seção de correções acima.
