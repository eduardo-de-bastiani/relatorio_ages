# Auditoria visual independente — AGES I / Easy Choose / Sprint 0

Revisor: subagente Codex `/root/pilot_visual_final`; execução independente da conversão, sem alegação de Antigravity. Commit compilado: `5826ca435bafb1e4d052f9c8bcd310d336825741`. PDF real SHA-256 `a57e643bd7878e2c2f36c6be20b902aa33a08381694102f2c7b453ea5f33fc93`.

Resultado atual: **FAIL cosmético**, por VIS-001 abaixo. Aprovação humana: **PENDING**. Nenhuma próxima Sprint autorizada ou convertida.

## Inspeção executada

Todas as páginas do PDF real (1–2) e do teste sintético de continuidade (1–2) foram renderizadas a 150 dpi, abertas e inspecionadas individualmente. Também foram abertas as páginas físicas 17–18 do PDF Mariah, somente para comparar acabamento. Renders, hashes, comandos, códigos de saída e medições estão em `VISUAL_AUDIT.json` e `build/pilot/visual-final/measurements.json`.

- **PASS**: texto, acentos e aspas legíveis; nenhum clipping, overflow, sobreposição, título órfão ou página vazia. O branco final da p.2 resulta do fim do escopo autorizado, não de quebra artificial.
- **PASS**: corpo e reflexão usam a mesma fonte NimbusSanL-Regu e 11.955168 pt PDF, equivalente a 12 pt TeX; distância entre baselines17.92723 pt≈1.5×. Aparência sem serifa e texto justificado comparáveis à referência Mariah, sem transferência de narrativa.
- **PASS**: reflexão possui borda em ambos os segmentos e divide naturalmente entre páginas, inclusive no meio do terceiro parágrafo. Não há texto oculto pela borda.
- **PASS**: teste de continuidade mostra texto anterior e título real na p.1; último parágrafo real e título posterior sintético na p.2. A Sprint real não possui quebra obrigatória. O material sintético fica fora do PDF de entrega.
- **PASS geométrico parcial**: A4 595.28×841.89 pt; borda em x85.03937..538.58270 comprova esquerda3cm/direita2cm; topo da p.2≈3cm. Nenhuma tinta entra no mínimo inferior2cm. **PENDING** mensuração do limite inferior exato, pois a mancha desta unidade não chega ao limite; configuração nominal2cm é apenas corroborativa.
- **PASS**: destino PDF `subsection.2.3.1` e âncora original `__RefHeading___Toc4743_3118176633` presentes.
- **NOT_APPLICABLE**: figuras, legendas, fontes gráficas, placeholders, listas autorais, notas, URLs externas, sumário exibido e bibliografia estão ausentes neste piloto.
- **PENDING**: certificação normativa integral/vigência das normas e aprovação humana. Não se declara conformidade ABNT integral.

## Achado

| ID / status | Localização / evidência | Consequência / gravidade | Correção / verificação |
|---|---|---|---|
| VIS-001 / FAIL | PDF real pp.1–2, número de página: p.1 9.96264 pt PDF; p.2 11.955168 pt PDF. Renders abertos confirmam tamanho maior na p.2. | Inconsistência cosmética de paginação; baixa. | Mantenedor uniformiza tamanho global; recompilar, medir os dois números e reabrir ambas as páginas. |

## Limites e execução

Foram lidos AGENTS, CONTEXT, MIGRATION_PLAN, STYLE_GUIDE, QUALITY_GATES, PENDENCIAS, papel visual-auditor e skills locais PDF/visual. Poppler26.01.0 renderizou as páginas. `pypdf` mediu fontes, posições e destinos. Tentativas de importar `fitz` e `pdfplumber` retornaram1 (indisponíveis); não houve instalação. A skill pede CLI `visual`, mas a saída fixa deste comando cai em `build/visual`, fora da posse atribuída: o orquestrador foi informado para executá-lo, e aqui os mesmos comandos Poppler foram usados no caminho autorizado.

Auditoria textual independente continua sendo necessária: glyph mapping, ligaturas e hifenização não tornam a extração PDF prova única de preservação. Somente os relatórios acima e `build/pilot/visual-final/**` foram escritos por este auditor; nenhum LaTeX ou conteúdo foi corrigido por ele.
