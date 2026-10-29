# Operação do harness

O harness controla a conversão e a validação do memorial. A apresentação da AGES I foi aprovada como padrão visual reutilizável; a única edição autorizada em execução é AGES II / Indústria Digital. Consulte [plano](MIGRATION_PLAN.md), [estilo](STYLE_GUIDE.md), [gates](QUALITY_GATES.md) e [pendências](PENDENCIAS.md).

## Organização do projeto

- `RELATORIO_ATUAL.odt` é a origem imutável, verificada pelo hash em `docs/BASELINE.json`.
- `Template_AGES___Guvidaletti/` é a cópia de referência do template e não é o destino editável.
- `relatorio_mariah/` é referência visual somente para leitura; não recebe conteúdo do memorial atual.
- `relatorio_AGES_eduardo/` contém o destino: `conteudo/migracao/` para unidades LaTeX, `imagens/original/` para mídia preservada, `bibliografia/` para referências e `util/` para estilo e macros compartilhadas.
- `migration/` guarda autorizações, ledgers e evidências; `docs/` guarda governança e relatórios revisáveis; `scripts/migration_harness/` centraliza extração, validação, compilação e inspeção visual; `tests/` contém testes do harness.
- `build/` é ignorado pelo Git e contém apenas resultados reproduzíveis. A saída atual fica em `build/document/`; experimentos e evidências históricas estão separados por etapa em `build/ages-i/`, `build/pilot/`, `build/validation/` e `build/visual/`. Não mover fontes para `build/` nem integrar artefatos gerados.

Os `main.pdf` rastreados na raiz e no template são arquivos de referência históricos. A prévia atual é `build/document/main.pdf`; o `report.json` informa se ela veio de compilação de revisão ou de produção.

## Entradas e rastreabilidade

`BASELINE.json` congela o commit original, SHA-256 do ODT, 112 arquivos protegidos e hashes de todos os 173 arquivos originais. `CONTENT_MANIFEST.json` é gerado pelo EXTRATOR com biblioteca padrão Python, ZIP e XML, sem Pandoc obrigatório. Contém todas as entradas do pacote, todos os nós dos seis XML/RDF, estilos/listas, recursos, unidades e exceções de classificação vinculadas ao hash auditado.

Cada registro tem ID, parte, XPath, ordem, pai, tipo, atributos, hash XML canônico e contexto. Parágrafos/títulos incluem texto sem duplicar conteúdo de caixas descendentes, texto original e segmentos que preservam âncoras. Mídia tem hash, dimensão e ocorrências; imagens e legendas têm vínculos bidirecionais. O destino é **previsto**, não prova de arquivo criado. Registros de layout e índices derivados não serão convertidos como texto autoral independente.

`inventory --check` reextrai a fonte e compara integralmente a estrutura. É o procedimento de leitura recomendado em revisão. `inventory` escreve o manifesto determinístico com lock exclusivo e exige branch de trabalho. O hash do manifesto não substitui a verificação do pacote original.

## Ledger futuro, schema 1

Exemplo de estrutura, sem registrar conversão real:

```json
{
  "schema_version": 1,
  "compilation_root": "relatorio_AGES_eduardo",
  "units": {
    "<id-original>": {
      "state": "converted",
      "tex_path": "<arquivo-relativo-ao-repositorio>",
      "element_map": [{
        "source_id": "<id-do-manifesto>",
        "target_file": "<arquivo-relativo-ao-repositorio>",
        "start_byte": 0,
        "end_byte": 10,
        "target_sha256": "<sha256-do-arquivo-inteiro>"
      }],
      "asset_map": [{
        "source_id": "<id-da-ocorrencia-draw-image>",
        "target_file": "<imagem-relativa-ao-repositorio>"
      }]
    }
  }
}
```

Intervalos UTF-8 são `[start_byte,end_byte)`. O auditor lê bytes reais e verifica o hash; texto declarado pelo conversor no ledger não é prova. Imagem exige também intervalo que contenha seu `\includegraphics` e o arquivo efetivamente referenciado. Ordem é reconstruída pelos arquivos e suas inclusões. URLs e âncoras são conferidas separadamente, preservando percent-encoding, caixa e endereço.

Somente políticas opcionais `tex_quotes`, `tex_dashes` e `canonical_unicode` estão reconhecidas, com testes específicos. Não servem para corrigir redação. Tabs, quebras explícitas e espaços repetidos/em bordas do original bloqueiam aprovação automática e exigem procedimento adicional comprovado. Contadores, citações expandidas, macros de reflexões/placeholders e outros comandos não reconhecidos também precisam de verificação renderizada e extensão testada do auditor; não serão ignorados para produzir PASS.

## Compilação e reprodução

`./build.sh --profile fixture` testa material sintético com `memoir`, Helvetica, `biblatex-abnt` e Biber. O perfil isola o processamento bibliográfico dos defaults de idioma do `abntex2`; não representa aprovação ABNT de um memorial. `--profile template` compila o template original, incluindo `abntex2`, e expõe seus defeitos atuais.

`./build.sh --profile document-review` compila o estado atual de `relatorio_AGES_eduardo/` para revisão humana e disponibiliza o PDF em `build/document/main.pdf`, mesmo com alterações ainda não commitadas. O relatório marca `review_only: true` e `official_document_gate: NOT_RUN`; compilação não aprova conteúdo nem libera outra edição. `./build.sh --profile document` é o build de produção e exige checkout limpo com as alterações congeladas em commit.

Cada tentativa invalida PDFs/auxiliares anteriores, verifica fontes protegidas, versões, recursos do cache e grafo LaTeX. Copia fontes sem auxiliares para um diretório temporário, usa o cache existente, fixa `SOURCE_DATE_EPOCH`/UTC e executa Tectonic `--only-cached --untrusted --keep-intermediates --keep-logs`. Tectonic invoca Biber e faz os passes necessários. Não há download de pacote ou instalação automática.

Resultados, logs, BBL/BCF, índices e hashes ficam em `build/<perfil>/`; diretório temporário é limpo ao sair. Qualquer aviso não revisado bloqueia aceitação. Um PDF disponível pode ser somente diagnóstico. Alteração de versão/cache exige atualização explícita do lock e nova reprodução; o lock não deve ser regenerado silenciosamente para esconder drift.

O seed contém 368 arquivos do cache existente. Para outra máquina, provisionar legitimamente esse mesmo seed e versões: o lock identifica os recursos, mas não distribui uma instalação TeX. Pandoc, compiladores separados e latexmk são opcionais e ausentes neste ambiente. ODF usa somente a biblioteca padrão; `pypdf` complementa hyperlinks de PDF. Ausência de `pypdf` torna essa evidência pendente, sem impedir renderização Poppler.

## Coordenação e evidências

Os sete papéis são prompts portáveis em `docs/agents/`; as sete skills estão em `.agent/skills/`. `run-task` exige branch/worktree limpo, proprietário/escopo definido e comando confiável. Locks por recurso compartilham a identidade Git comum entre worktrees. Uma chamada CLI filha pode reutilizar o lock ainda mantido pelo processo pai. São controles cooperativos, sem garantia de sandbox contra comandos adversários. Depois, conferem branch, diff desde o commit inicial e hashes protegidos; violações não fazem reset automático.

Use worktree por conversor e integração serial. Um campo de configuração ou dossier gerado não autoriza a migração. `checkpoint --unit <id>` produz somente `pending_human_approval` em `build/checkpoints/`. Evidência identificável da mensagem do usuário e vínculo ao commit/PDF continuam obrigatórios.

`visual --pdf <caminho-relativo>` renderiza **todas** as páginas, extrai metadados, fontes, texto e hyperlinks, e registra hashes. O resultado permanece `pending_human_review`: alguém precisa abrir e conferir as páginas. Relatórios de conteúdo têm diferenças por unidade em `build/validation/<id>/report.json`. Código `3` comunica cobertura/revisão pendente, nunca aprovação.
