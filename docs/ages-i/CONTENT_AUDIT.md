# Auditoria independente de conteúdo — AGES I

**FAIL**, commit `ea4b3ee8cad8b441a04730817a91078bc2b83a2a`, PDF SHA-256 `0903a4ecb1cf1486fc05dde3df72a6ec12e11e7e3cc8c7d428c8fd2f0b47b61a`. Aprovação humana **PENDING**. Auditoria por subagente Codex separado; não é execução Antigravity.

Extração direta do ZIP/XML original, com serializador próprio de espaços/tabs/quebras e resolução de herança de estilos. Derivados **102 blocos, 5 imagens, 11 links e 5 reflexões (17 parágrafos)**. SHA-256 do ODT `e8647819c353f68c0862869f205974a475dcec944eefaa1cf0fa462fb8bd67ef`. O ledger apenas localiza intervalos candidatos; foram lidos bytes reais e comparados ao XML independente, sem usar texto esperado do conversor como prova.

| Verificação | Resultado |
|---|---|
| Texto, acentos, símbolos, pontuação, espaços/tabs explícitos e ordem | PASS, 102/102 blocos; 15 validações exit 0 |
| IDs/XML contra manifesto; cobertura e intervalos/hash dos destinos | PASS |
| Hierarquia e cinco itens de tecnologias com suas continuações | PASS |
| Cinco reflexões, todos os 17 parágrafos originais | PASS |
| Cinco mídias e correspondência arquivo/ocorrência/legenda | PASS, hashes iguais ao ZIP |
| Onze URLs/âncoras e bookmarks | PASS; URI reais do PDF também conferidas |
| Ênfases em negrito, itálico e sublinhado | **FAIL, CA-01**; demais posições de corpo/legenda preservadas |
| Contadores .aux, sumário e lista de figuras | PASS: seção 2; 2.1–2.4; Sprints 2.3.1–2.3.5; figuras 1–5 |
| Dois placeholders provisórios, fora da lista de figuras | PASS |
| Cinco referências novas verificadas, aparato separado da narrativa | PASS; datas de curadoria atuais, sem autor/ano presumidos |
| Auditoria estática própria | PASS, exit 0 |
| Build integrado identificado | PASS, relatório limpo exit 0; não alegada recompilação por este auditor |
| Disponibilidade dos seis links de projeto; fontes das cinco imagens | PENDING, pendência autorizada, nenhuma autoria inventada |
| Inspeção visual integral; certificação normativa; aprovação humana | PENDING |

## CA-01 — perda de itálico na legenda 5

- **Arquivo/ID:** `relatorio_AGES_eduardo/conteudo/migracao/chapter-02-text-h-0022.tex:30`, `text-p-0650`.
- **Evidência:** P64 herda de Figure o itálico em todos os 42 caracteres. O segundo argumento real de `memorialfigure` está sem `textit`; a entrada correspondente de `main.lof` confirma a diferença. As legendas 1–4 têm o itálico preservado.
- **Consequência e gravidade:** perda de ênfase original; média. Texto literal preservado não resolve essa divergência.
- **Correção proposta:** conversor envolve a legenda literal em `textit`, atualiza intervalos/hash do ledger e recompila.
- **Verificação de retorno:** repetir comparação independente de caracteres/estilos, validar a unidade, conferir `.lof` e PDF corrigido. Auditor não modifica memorial nem ledger.

## Evidências e limites

Comandos realmente executados: `verify-source` (0), extração independente Python (0), comparação própria de bytes/ênfases (0), `validate --ledger … --unit …` para as quinze unidades (todos 0), `audit-latex --root relatorio_AGES_eduardo --entry main.tex` (0), inspeção de URI do PDF com pypdf (0) e confronto XML/manifesto dos 102 IDs/textos (0). Detalhes por comando, arquivos e SHA-256 estão no JSON pareado. Tentativas preliminares do driver foram corrigidas antes do resultado; PyMuPDF indisponível foi substituído por pypdf instalado.

A conferência de `.aux/.toc/.lof/.bbl` é do build real identificado acima. Hierarquia, numeração literal e índices foram conferidos separadamente do texto autoral. A bibliografia tem apenas as cinco chaves documentadas na curadoria, com `nocite` após `postextual`; nenhuma citação foi acrescentada à narrativa.

Tabs internos de p0303/p0314/p0318 usam avanços fixos de 1,251 cm, um para cada tab original; isso preserva o token, mas não comprova a mesma posição horizontal dos tab stops ODF. A inspeção visual permanece separada. Nenhuma norma ou aprovação humana é inferida de PASS automatizado.

Arquivos alterados por este auditor: somente este relatório e `CONTENT_AUDIT.json`; evidências locais em `build/ages-i/audit/`. **Reauditoria obrigatória após a correção; não aprova entrega, revisão editorial ou próxima edição.**
