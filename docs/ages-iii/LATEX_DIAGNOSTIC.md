# Diagnóstico técnico do LaTeX — AGES III

Data: 17/10/2026  
Branch: `migration/ages-iii`  
Commit-base observado: `96c09d1` (sem commit nesta tarefa)

## Correção do glifo U+00B7 na bibliografia

O build completo em `build/document/compiler.txt` registrava a falha `Font TS1/phv/b/n/12=phvb8c ... not loadable`. A entrada de GitHub em `relatorio_AGES_eduardo/bibliografia/bibliografia.bib` contém o ponto médio U+00B7 no título e o autor corporativo `{{GitHub}}`; no contexto em negrito, a macro anterior `\textperiodcentered` solicitava a variante TS1/phv/b/n indisponível.

Alteração restrita em `relatorio_AGES_eduardo/util/style.tex`: o mapeamento de U+00B7 agora envolve `\textperiodcentered{}` em `\textnormal{...}`. O caractere, título, autor e metadados bibliográficos permanecem inalterados; o glifo continua sendo um ponto médio, em peso normal.

Verificação isolada em cópia temporária completa do projeto:

```sh
cd /tmp/ages-iii-u00b7-font-apj6yvyt/source
tectonic --only-cached --untrusted --keep-intermediates --keep-logs main.tex
```

Resultado: código de saída `0`; PDF de 65 páginas. O log não contém `TS1/phv/b/n/12=phvb8c` nem `Font ... not loadable`. A página 64 renderizada foi inspecionada e mostra o título do GitHub com o ponto médio visível. A compilação isolada ainda registra o aviso de overfull indicado abaixo e avisos de perfil ICC; também informa que não há diretório de cache Fontconfig gravável. Esses avisos ambientais não impediram a geração do PDF.

Artefatos dessa verificação temporária:

- PDF: `/tmp/ages-iii-u00b7-font-apj6yvyt/source/main.pdf`, SHA-256 `e8f9cbbb84d3b68bc7341f481c5773db76b076eb97c84dff27389f31bd3b5f7e`.
- Imagem inspecionada: `/tmp/ages-u00b7-bibliography-final.png`, SHA-256 `60994e97008b91e1cbbd0adb44cede0850c0c3ecb5e79004c11fba54f8862865`.
- Cópia de `util/style.tex` usada no teste, SHA-256 `4910d078652ffe8adae0a0d91383d6a3743eb2f900f544e5890b253df5cdb6b4`.
- Tectonic `0.17.0`.

## Aviso tipográfico de h0085

**Status: PENDING.** O build temporário reproduz `Overfull \hbox (2.72131pt too wide)` no parágrafo de tecnologias de `chapter-05-text-h-0085.tex`, ao final da linha visual que contém “gateway do projeto, empregou-”. A inspeção ampliada das páginas 47–48 do PDF usado na auditoria não identificou corte de texto ou protrusão visualmente intrusiva, mas o aviso permanece no log.

Foram avaliadas em cópia temporária alternativas locais de `\looseness`, `\emergencystretch` e `\spaceskip`. `\looseness` não eliminou o aviso. `\emergencystretch` suficientemente amplo e as variantes de `\spaceskip` eliminaram o overfull, mas alteraram a distribuição dos espaços e/ou a quebra de linhas do parágrafo inteiro. Não foi aplicada nenhuma dessas alterações: o escopo desta tarefa permite o ajuste tipográfico mínimo da macro compartilhada e proíbe alterações globais de layout ou de conteúdo da unidade. O texto e o layout de h0085 permanecem intactos; a disposição deste aviso exige avaliação posterior dentro do escopo de layout autorizado.

## Validações e limites

- `git diff --check`: PASS.
- `python3 scripts/migration.py audit-latex --root relatorio_AGES_eduardo --entry main.tex`: PASS estrutural, sem erros; emite o aviso já existente `unsupported_citation_command` para `\memorial@citefirstword` em `util/style.tex`.
- Build isolado acima: código `0`; corrigiu o erro de fonte TS1 em negrito. O aviso h0085 e os avisos ICC permanecem.
- Não foi executado build compartilhado em `build/`; nesta tarefa não editei conteúdo, bibliografia ou scripts e não criei commit.
