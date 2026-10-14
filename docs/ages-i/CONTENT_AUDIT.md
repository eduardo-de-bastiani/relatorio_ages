# Auditoria independente de conteúdo — AGES I

**PASS no escopo de preservação de conteúdo**, commit `25319d941aa0c7c227dd80094b0b25f582be68b6`. PDF de 17 páginas: SHA-256 `c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f`. Aprovação humana e aceitação da entrega **PENDING**.

Auditoria por subagente Codex separado, com extração direta do ODT imutável e decodificador TeX próprio. Não é execução Antigravity. O ledger apenas indica intervalos candidatos; a prova usa os bytes reais do destino contra o XML independente, sem confiar em texto esperado escrito pelo conversor.

| Verificação final | Resultado |
|---|---|
| Texto, acentos, símbolos, pontuação, espaços/tabs explícitos e ordem | PASS, 102/102 blocos; 15 validações exit 0 |
| IDs/XML contra manifesto; intervalos e hashes dos destinos | PASS |
| Hierarquia original e cinco itens de tecnologias | PASS; 17 parágrafos agrupados nos cinco itens, incluindo continuações |
| Cinco reflexões | PASS; mesmos 17 parágrafos originais, na ordem e dentro dos ambientes |
| Cinco mídias | PASS; hashes iguais aos membros correspondentes do ZIP, ocorrências e legendas preservadas |
| Onze URLs/âncoras e bookmarks | PASS; 11 URI autorais iguais nas anotações do PDF, além de 5 URI bibliográficas curadas |
| Negrito, itálico e sublinhado em corpo/legendas | PASS; CA-01 resolvido; cinco legendas com itálico |
| Contadores .aux, sumário e lista de figuras | PASS; 15 títulos originais, Sprints 2.3.1–2.3.5, figuras 1–5 |
| Dois placeholders provisórios | PASS; sem conteúdo/fonte inventados e fora da lista de figuras |
| Cinco referências curadas separadas da narrativa | PASS; campos idênticos à evidência, datas da consulta atual, sem autor/ano presumidos |
| Auditoria estática e origem executadas por este auditor | PASS, exit 0 |
| Compilação integrada identificada | PASS, relatório final sem achados, exit 0; este auditor não executou novo build |
| Disponibilidade dos seis links de projeto | PENDING, preservação autorizada sem alegar disponibilidade |
| Fontes/autoria das cinco imagens | PENDING, nenhuma atribuição inventada |
| Alinhamento exato de tabs, vazios de composição e inspeção visual integral | PENDING, revisão visual separada |
| Conformidade normativa integral e aprovação humana | PENDING |

## Histórico preservado — CA-01 resolvido

A primeira auditoria, em `ea4b3ee8cad8b441a04730817a91078bc2b83a2a`, resultou em **FAIL**. PDF daquela auditoria: `0903a4ecb1cf1486fc05dde3df72a6ec12e11e7e3cc8c7d428c8fd2f0b47b61a`.

- **Arquivo/ID:** `relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0022.tex:30`, `text-p-0650`.
- **Evidência anterior:** P64 herda de Figure o itálico nos 42 caracteres da legenda 5. O argumento de `memorialfigure` e sua entrada `.lof` não tinham `textit`; as legendas 1–4 preservavam essa ênfase.
- **Consequência e gravidade:** perda de ênfase original; média.
- **Correção e retorno:** no commit final acima, o argumento real está envolvido em `textit`. A comparação independente passa para os 42 caracteres/estilos; intervalo/hash do ledger, validação da unidade, `.lof` e PDF final foram rechecados. **PASS, resolvido**, sem apagar a falha histórica. Nenhuma alteração ao memorial foi feita pelo auditor.

## Evidência final e limites

ODT SHA-256 `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. A extração independente deriva 102 blocos, cinco imagens, 11 links e cinco reflexões (17 parágrafos); todos os 102 IDs/textos foram confrontados com o manifesto. A resolução de estilos usa a herança `style:parent-style-name` e propriedades de negrito, itálico e sublinhado. A tipografia de títulos é avaliada como apresentação global; suas letras, níveis e contadores foram conferidos separadamente.

Comandos efetivamente executados nesta reauditoria: `python3 build/ages-i/audit/compare.py` (0), com reextração direta e `validate --ledger … --unit …` para todas as 15 unidades (cada um 0); `verify-source` (0); `audit-latex --root relatorio_AGES_eduardo --entry main.tex` (0); `python3 build/ages-i/audit/final_checks.py` (0), incluindo anotações URI reais via pypdf, contadores `.aux`, entradas `.toc/.lof`, cinco entradas `.bbl` e igualdade de campos com a curadoria. O JSON pareado registra comandos, hashes, arquivos examinados, histórico da falha e evidências por artefato.

A lista de ilustrações final tem exatamente cinco entradas, todas com `Figure` literal e itálico; os placeholders não entram nela. O sumário possui os 15 títulos originais e a entrada separada das referências curadas. O main final contém somente as 15 unidades autorizadas; as Sprints usam `input`, sem quebra obrigatória na entrada. A quebra entre listas pré-textuais fica fora da narrativa; `FloatBlock` contém os protótipos antes das tecnologias. `penalty0` na reflexão permite uma quebra sem obrigá-la e não modifica texto. A posição/continuidade efetiva pertence à revisão visual.

As datas bibliográficas são da consulta da curadoria atual, nunca datas históricas inferidas. `nocite` ocorre após `postextual`; não foram inseridas citações na narrativa. Foram comparados os cinco conjuntos de campos bibliográficos reais com `migration/evidence/references/ages-i.json`.

Tabs internos de p0303/p0314/p0318 usam avanços fixos de 1,251 cm, um para cada tab original; isso preserva o token, mas não prova a mesma posição horizontal dos tab stops ODF. Os dois tabs de p0473 também permanecem presentes. Lacunas de proveniência, links não verificados e apresentação não viram PASS por ausência de falha automatizada. Nenhuma norma nem aprovação humana é inferida.

Arquivos alterados pelo auditor: somente este relatório e `CONTENT_AUDIT.json`; evidências locais em `build/ages-i/audit/`. Snapshot identificado: `build/ages-i/review/c9621fdb46bd2818cf84d606b0355c5ec3a6ccbcbe7fb8295cdc46f706cfe90f/`. Qualquer alteração posterior de conteúdo/configuração/PDF exige conferir os efeitos. **Não autoriza próxima edição nem revisão editorial.**
