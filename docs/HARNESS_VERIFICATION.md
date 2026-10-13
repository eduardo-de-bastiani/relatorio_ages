# Evidências da entrega do harness

Execução sobre o código do commit `a881f0992e87c124d2a125cffb4b4cc2ecd000ed`, na branch `harness/migration`. O commit de origem e a branch principal permanecem `44bc0b95ef5ed06c8efa272de4f754cce1d6e4cb`. Nenhuma Sprint foi convertida. O único arquivo original alterado é o `build.sh`, autorizado nesta fase; ODT, template, PDFs originais e comparativo permanecem byte a byte intactos.

## Resultados realmente executados

| Comando/procedimento | Saída | Evidência e limite |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | 51 testes, PASS | Fixtures positivas/negativas: ZIP/XML, caixas aninhadas, índices, objetos, texto, ordem, links, mídia, scopes/locks e logs; não equivalem a memorial convertido |
| `verify-source` | PASS / exit 0 | 112 arquivos protegidos com hashes iguais |
| `inventory --check` | PASS / exit 0 | Reextração integral sem diferenças; 9.298 registros XML/RDF, 77 unidades, 25 Sprints, 34 imagens e 17 reflexões |
| `doctor` | PASS / exit 0 | Python 3.12.8, Tectonic 0.17.0, Biber 2.17, Poppler 26.01.0; seed de 368 recursos sem drift |
| `audit-latex --root Template_AGES___Guvidaletti --entry main.tex` | PASS / exit 0; um aviso | 55 `.tex` alcançáveis; cheatsheet demonstrativo fora do grafo, explicitamente identificado |
| `validate` sem ledger | UNCONVERTED / exit 3 | Integridade de origem PASS; 77 unidades não convertidas, 659 registros textuais autorais, cobertura 0% |
| `./build.sh --profile fixture`, duas execuções seriais | PASS / exit 0, ambas | Biber realmente executado; BBL, sumário, lista de figuras/tabelas gerados; referências/citações resolvidas; PDF byte-idêntico |
| `./build.sh --profile template` | FAIL / exit 1; compilador exit 0 | PDF diagnóstico de 22 páginas; 20 diagnósticos bloqueantes: glifos ausentes, overflow, localização biblatex e destino PDF duplicado |
| `build --profile document` | UNCONVERTED / exit 3 | Destino ausente; nenhum PDF de memorial é apresentado como migrado |
| `visual --pdf build/template/main.pdf` | PENDING / exit 3 | Todas as 22 páginas renderizadas; metadados/fontes/texto/hashes registrados; revisão visual humana continua pendente |
| `validate --unit '../../../escape'` | FAIL / exit 1 | ID desconhecido rejeitado antes de derivar caminho; nenhuma escrita externa |
| `checkpoint --unit ages-i-sprint-0` | PENDING / exit 3 | Dossier não cria aprovação nem autorização do piloto |

Hash do PDF sintético, idêntico nas duas reproduções: `21db22caf2411f9c315b885e4605657756499413d62d15e874bc167f88606216`.

Hash do PDF diagnóstico do template: `44563702a4f4b29042cd348b036332f7a4acd2a5db87a1741e9c452e0e23e8bd`. Ele não substitui o PDF original rastreado e não passou no gate de qualidade.

## Isolamento e coordenação

Foi criado de verdade o worktree `/tmp/ages-harness-isolation-a881f09`, com branch descartável `harness/isolation-check`, a partir do mesmo commit. Nele, `run-task --role extractor -- python3 scripts/migration.py inventory --check` terminou PASS, sem alterações de arquivos nem mudança de branch. O ambiente emitiu mensagens de criação de stream/fd durante a chamada filha; não houve falha dos checks (exit 0), e isso não demonstra sandbox Antigravity.

Um lock `manifest` adquirido no checkout principal impediu a aquisição do mesmo recurso no worktree: `Resource already owned: manifest`. O worktree e sua branch descartável foram removidos depois do teste. Os testes também verificam colisão de lock, reuso por chamada CLI filha, troca indevida de branch e escopo fora da unidade.

As compilações compartilham locks de integração/configuração. Uma tentativa concorrente foi recusada antes do build; a reprodução conclusiva acima foi serial. Não interpretar a recusa como resultado de compilação do perfil nem consultar um PDF antigo como saída dessa tentativa.

Subagentes Codex reais prepararam extração, validação e governança em caminhos distintos. A pesquisa de Antigravity foi somente leitura: versão/help locais e documentação oficial. Delegação/paralelismo Antigravity não foram executados; descoberta automática das skills locais tampouco foi demonstrada. Consulte [AGENT_CAPABILITIES](AGENT_CAPABILITIES.md).

## Riscos e próximo checkpoint

Os gates do memorial permanecem pendentes. Resolver por unidade as pendências de metadados/fontes de imagens, demonstrações do original, whitespace explícito, numeração manual, pré-textuais, vigência normativa e lacunas Recorda. O template precisa de tratamento dos glifos e avisos pelo mantenedor na etapa autorizada. Um parser lexical conservador não atesta macros arbitrárias ou layout.

Piloto recomendado: **AGES I / Easy Choose / Sprint 0**, ID `ages-i-sprint-0`, título original `text-h-0016`, dez registros textuais, destino previsto `relatorio_AGES_eduardo/conteudo/migracao/ages-i-sprint-0.tex`. Exercita texto/listas/reflexão sem dependência de figura complexa. A reflexão terá borda, fonte do corpo e divisão entre páginas, conforme decisão do usuário. A autorização explícita do piloto ainda é necessária.

Detalhes operacionais estão em [HARNESS](HARNESS.md); relatórios locais em `build/`, ignorado pelo Git, com hash/commit e resultado de cada execução. Os diretórios temporários de compilação foram limpos. Artefatos diagnósticos em `build/` ficam disponíveis para revisão e podem ser regenerados.
