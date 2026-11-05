# Inclusão de diagramas — 05/11/2026

O autor forneceu quatro imagens e autorizou substituir a antiga figura de sistema de AGES II pelo diagrama de deploy. A evidência, hashes, numeração e referência à imagem original conservada estão em `migration/approvals/ages-i-ii-diagrams-2026-11-05.json`. As quatro fontes continuam pendentes de identificação. As imagens são cópias íntegras dos arquivos recebidos; os três placeholders foram substituídos.

## Verificações

- PDF de revisão: `build/document/main.pdf`, SHA-256 `72db1048d7f1bc8f60780a068f929c4f1f10bc0f8b7e9688d6c9d6a9a9cfac1d`; 113 páginas. Tectonic encerrou com código 0, mas o gate de compilação é **FAIL**: 10 ocorrências de `OVERFULL` de 1,41573 pt e 2 avisos de links vazios. Conferir `build/document/report.json` e `main.log`.
- Lista de ilustrações extraída do PDF: figuras 1–38 em sequência. Diagramas 2, 3, 9 e 10 aparecem, respectivamente, nas páginas 17, 18, 34 e 35. A chamada dos protótipos passou a exibir “Figuras 4 a 6”.
- Revisão visual realizada nas páginas 17, 18, 34 e 35 e verificação textual do contexto final: diagramas, legendas e fontes centralizadas; a resolução dos textos pequenos nos diagramas de banco de dados requer revisão humana no tamanho de impressão. A revisão não cobre o documento inteiro.
- `verify-source`: PASS; `audit-latex`: PASS com aviso preexistente `unsupported_citation_command`; `python3 -m unittest discover -s tests -p test_latex.py`: 15 testes PASS; `git diff --check`: PASS.
- Conferência de 784 intervalos rastreados e hashes em ledgers: sem divergências detectadas além da alteração explícita de títulos. Este teste não substitui auditoria semântica independente.
- `validate --unit chapter-04-text-h-0044 --ledger migration/ledgers/chapter-04-text-h-0044.json`: **BLOCKED**. O contrato histórico exige a antiga imagem e legenda (`draw-image-0010` e `text-p-0788`) e a numeração antiga; não reconhece a substituição autorizada nem a nova sequência. A ocorrência original e o arquivo original permanecem rastreados no registro de autorização e no ledger. A adequação do validador e dos overlays históricos fica pendente; nenhuma validação integral é alegada.
- O validador das duas unidades dos títulos AGES III/IV também continua bloqueado desde a mudança anterior de “PROJETOS” para “PROJETO”. Não se alteraram as autorizações históricas para mascarar a divergência.

A inspeção foi feita na mesma sessão de execução, não por auditor independente. Aprovação humana da prévia permanece pendente.
