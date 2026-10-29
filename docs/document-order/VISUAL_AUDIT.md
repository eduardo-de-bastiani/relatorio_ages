# Auditoria visual independente — PDF de revisão

Data: 2026-10-17  
Artefato: `build/document/main.pdf`  
SHA-256: `981e804929793f73fe662e89076556eecf27275c099a16e052ad134fd5911179`  
Perfil: `document-review`; 105 páginas A4; inspeção do artefato de revisão, não de uma versão oficial.

## Veredito

**Aprovação visual: PENDING — requer validação humana.** Não encontrei cortes, colisões ou páginas totalmente vazias nas áreas examinadas. A sequência das edições e das figuras está visualmente íntegra, e a transição de AGES IV para Cliente Hoortech está na ordem autorizada.

**Gate de build: FAIL.** O `main.log` final contém três ocorrências `Overfull \hbox` de 1,41573 pt e duas advertências `hyperref` por links vazios. As três linhas excedentes não produzem corte ou colisão visível no PDF, mas permanecem falhas técnicas do gate e precisam continuar registradas. O retorno 0 do compilador não altera o status FAIL registrado em `build/document/report.json`.

## Método e cobertura

Confirmei o SHA-256 e as 105 páginas com `sha256sum` e `pdfinfo`. Inspecionei renderizações das páginas pré-textuais 5–12, de todas as páginas do capítulo AGES IV e da participação Cliente Hoortech (73–100), das páginas do título do capítulo 7 e das referências (101–105), além das páginas que contêm as Figuras 1–34. Usei `pdftotext -layout` e `pdftotext -bbox-layout` para conferir ordem, conteúdo visível e posicionamento do sumário. Uma varredura das 105 páginas não encontrou página sem texto.

## Resultado visual

| Área | Evidência no PDF | Resultado |
|---|---|---|
| Sumário e listas | Lista de ilustrações nas páginas PDF 6–7; siglas nas páginas 8–9; sumário nas páginas 10–12. A sequência das Figuras 1–34 aparece na lista. | Sem corte ou colisão. A página 7 contém apenas as quatro últimas entradas da lista e é uma continuação, não uma página vazia. |
| Espaçamento de títulos no sumário | Nas páginas PDF 11–12, `4.1`, `5.1` e `6.1` ficam na coluna de numeração, e `Introdução` começa na coluna de títulos. A renderização ampliada e as caixas de texto confirmam um vão de cerca de 43 pt entre as colunas, igual ao padrão das linhas vizinhas. | **Sem defeito.** A impressão anterior de que esses títulos estavam colados aos números não se confirma no PDF identificado acima. |
| Sequência das edições e figuras | Figura 1 na p.15; 2 p.17; 3–4 p.18; 5 p.29; 6 p.31; 7 p.32; 8–9 p.33; 10–11 p.34; 12 p.45; 13 p.52; 14 p.53; 15 p.55; 16–17 p.56; 18–19 p.57; 20 p.58; 21 p.74; 22 p.75; 23 p.76; 24–25 p.77; 26–27 p.78; 28–29 p.81; 30 p.83; 31 p.84; 32 p.91; 33 p.98; 34 p.100. | Numeração contínua de 1 a 34; ordem entre legendas, imagens e lista consistente. |
| AGES IV e continuidade das Sprints | Capítulo 5 começa na p.73. Sprint 0 começa na p.82; Sprint 1 na p.86. Os títulos vazios de Sprint 2, Sprint 3, Sprint 4 e Conclusão aparecem ao fim da p.89, depois do texto da Sprint 1. | Fluxo contínuo, sem quebra artificial antes das Sprints. Os títulos vazios permanecem, como solicitado, sem narrativa acrescentada. |
| Transições `5.4 → 6 → 7` | `5.4 Conclusão` aparece na p.89; o capítulo 6, Cliente AGES – Hoortech, começa na p.90. A conclusão 6.3 ocupa as p.98–100 e inclui as Figuras 33 (p.98) e 34 (p.100). O título do capítulo 7 aparece sozinho na p.101, conforme o escopo autorizado; Referências começa na p.102. | Ordem correta, sem sobreposição entre capítulos. O capítulo 7 contém somente o título esperado; o corpo não aparece. |
| Legendas, fontes e imagens | Legendas das figuras aparecem acima das imagens; fontes abaixo, centralizadas. As fontes ainda dizem “Fonte: pendente de identificação”. Imagens e legendas permanecem próximas e dentro da área de texto. | Apresentação consistente com o estilo aprovado; identificar as fontes continua sendo pendência humana, não resolvida por esta auditoria. |
| Blocos de reflexão | O bloco de reflexão que atravessa as páginas 85–86 continua com a borda e a fonte do corpo, sem corte de conteúdo. | Divisão entre páginas legível e permitida pelo padrão aprovado. |
| Links, citações e referências | Links e citações permanecem legíveis nos trechos examinados. Referências nas páginas 102–105, inclusive URLs quebradas entre linhas, não apresentam corte visível. | Sem problema visual confirmado. A advertência de link vazio descrita abaixo mantém a verificação semântica de dois destinos pendente. |
| Páginas vazias ou quase vazias | Nenhuma página totalmente vazia. A p.5 mostra o placeholder de resumo; a p.101 contém somente o título do capítulo 7; a p.105 termina a lista de referências. | Os espaços correspondem a placeholders, à estrutura parcial autorizada e ao fim natural da lista; não identifiquei folha vazia artificial. |
| Legibilidade de diagramas | Alguns rótulos internos de diagramas, EAP e capturas de tela são pequenos em escala de página, especialmente nas Figuras 14–15, 22, 28–29 e 30–31. | PENDING para confirmação humana de leitura em zoom/impressão. Não observei conteúdo cortado; a avaliação visual não certifica a legibilidade de cada rótulo em tamanho impresso. |

## Avisos finais e pendências técnicas

| Localização | Evidência final | Efeito observado | Gravidade e encaminhamento |
|---|---|---|---|
| `main.lof:35`, Lista de Ilustrações, página PDF 7, entrada da Figura 34 (página indicada 100) | `main.log:1096`: `Overfull \hbox (1.41573pt too wide)`. | O número 100 está visível na margem direita, sem corte nem colisão. | **FAIL técnico.** Ajustar, sob autorização do mantenedor LaTeX, a largura da coluna/entrada da lista; recompilar e rever a página 7. |
| `main.toc:97`, Sumário, página PDF 12, capítulo 7 (página indicada 101) | `main.log:1105`: `Overfull \hbox (1.41573pt too wide)`. | O número 101 está visível, sem corte nem colisão. | **FAIL técnico.** Corrigir centralmente a largura disponível para o número de página/entrada; recompilar e rever a página 12. |
| `main.toc:100`, Sumário, página PDF 12, Referências (página indicada 102) | `main.log:1110`: `Overfull \hbox (1.41573pt too wide)`. | O número 102 está visível, sem corte nem colisão. | **FAIL técnico.** Mesmo encaminhamento; verificar que ambas as entradas do sumário e a entrada da lista de ilustrações deixam de gerar overfull. |
| `chapter-06-text-h-0109.tex:12` e `chapter-06-text-h-0110.tex:12`, páginas PDF 74–75 | `main.log:1181` e `main.log:1185`: `Package hyperref Warning: Suppressing empty link on input line 12.` | Nenhum texto ou símbolo ausente é perceptível na página; a advertência indica que o destino de um link vazio foi suprimido. | **PENDING semântico.** Confirmar se são âncoras ODF vazias sem destino útil ou se algum destino precisa ser recuperado. Não apagar nem mascarar o aviso sem essa verificação. |
| Saída do compilador `build/document/compiler.txt:32–33` | Aviso de perfil ICC versão 4.3 não suportado na configuração PDF atual e perfil não incorporado. Esse aviso não aparece no `main.log` final. | Não observei alteração de cor evidente nas imagens renderizadas. A reprodução de cores entre visualizadores/impressoras não fica garantida pelo perfil. | **PENDING técnico.** Registrar separadamente do `main.log` e avaliar o perfil na configuração de PDF autorizada. |

As mensagens de overfull em arquivos de conteúdo que aparecem apenas no `compiler.txt` não são contadas como avisos do `main.log` final. Elas estão listadas e avaliadas visualmente em separado abaixo. O aviso ICC também fica separado porque aparece na saída do compilador, mas não nesse log.

### Overfulls listados somente em `compiler.txt`

O relatório `compiler.txt` também contém oito caixas excedentes em seis arquivos de conteúdo. Eles não aparecem no `main.log` final e, por isso, ficam registrados como **diagnósticos da saída agregada do compilador**, sem serem apresentados como avisos finais desse log. Inspecionei as páginas atuais correspondentes no PDF para verificar o efeito visual:

| Arquivo/linha em `compiler.txt` | Excesso reportado | Página(s) PDF correspondente(s) | Resultado da inspeção visual |
|---|---:|---:|---|
| `chapter-04-text-h-0043.tex:8` | 4,74695 pt | 31 | Parágrafo de banco de dados; linhas permanecem dentro da área visual de texto, sem corte ou colisão. |
| `chapter-05-text-h-0075.tex:9` | 92,78046 pt | 51 | Introdução AGES III; não observei texto cortado na margem ou sobreposição. |
| `chapter-05-text-h-0079.tex:18` | 60,17422 pt | 53–54 | Seção de arquitetura AGES III, incluindo a continuação do texto; não observei corte nem colisão. |
| `chapter-05-text-h-0085.tex:13` | 38,51414 pt | 58 | Seção de tecnologias AGES III; o parágrafo permanece legível e dentro da mancha. |
| `chapter-05-text-h-0085.tex:22` | 23,56216 pt | 58–59 | Continuação da seção de tecnologias AGES III; não observei clipping ou sobreposição na passagem de página. |
| `chapter-06-text-h-0109.tex:9` | 31,79472 pt | 74–75 | Parágrafo do banco de dados AGES IV atravessa a página normalmente; texto não parece cortado. Os links vazios são registrados separadamente. |
| `chapter-06-text-h-0113.tex:8` | 51,42633 pt | 79 | Seção de tecnologias AGES IV; parágrafo legível, sem colisão visível. |
| `chapter-06-text-h-0113.tex:12` | 3,73651 pt | 79 | Mesmo trecho; não observei corte ou colisão. |

Essas ocorrências continuam sendo avisos de composição reportados por `compiler.txt` e precisam de revisão técnica antes de qualquer gate que exija compilação sem overfull. A inspeção indica que não geram clipping perceptível nessas páginas do PDF; isso não converte os avisos em PASS nem demonstra ausência de extrapolação tipográfica em todos os visualizadores.

## Comparação com o padrão aprovado

O PDF mantém o padrão visual já aprovado com base no relatório da Mariah: corpo sem serifa, hierarquia numérica de seções, Sprints seguindo o fluxo do texto, legendas em português acima das figuras, fontes centralizadas abaixo e URLs legíveis nas referências. A revisão se limitou à apresentação; não propõe alterações de conteúdo nem identifica fontes de imagem por inferência.

## Decisão

Não encontrei defeito visual impeditivo nas páginas inspecionadas. A aprovação visual permanece **PENDING** até a validação humana dos diagramas pequenos, das fontes de imagem pendentes e dos links vazios. O build permanece **FAIL** pelos três overfulls finais e conserva os dois avisos de `hyperref`; a advertência ICC permanece registrada separadamente. Nenhuma dessas pendências foi ocultada ou tratada como resolvida.
