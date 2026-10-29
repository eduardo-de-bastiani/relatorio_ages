# Revisão crítica pós-formatação — AGES I / Easy Choose

> **Histórico substituído:** este parecer descreve o PDF anterior de 19 páginas, SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`. A apresentação do parágrafo de tecnologias foi alterada depois. Consulte [CURRENT_REVIEW.md](CURRENT_REVIEW.md) para o PDF atual de 18 páginas e seu resultado.

**Estado: candidato pronto para revisão humana; aceite do PDF e promoção do padrão permanecem PENDING.** Esta revisão avalia somente AGES I. O PDF contém 19 páginas e está identificado por SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`.

## Resultado das correções

As correções de apresentação autorizadas foram aplicadas sem revisão editorial da redação:

- Legendas e lista de ilustrações usam “Figura” e travessão, em português. A identificação aparece acima das imagens, as fontes abaixo, as imagens ficam centralizadas e os números/labels continuam disponíveis para referências cruzadas. A chamada à Figura 5 na página 17 agora tem espaço visível e link clicável para a imagem da página 18.
- Os cinco itens de tecnologias continuam em ordem, com os parágrafos e links documentais originais. Os marcadores visuais foram suprimidos a pedido do usuário; essa é uma escolha de apresentação, não uma declaração de que a ABNT proíbe listas com marcadores.
- Os três links dos repositórios foram integrados a frases em prosa, com âncoras clicáveis e as URLs originais intactas. Links e descrições de imagens aparecem em fonte regular.
- O sumário, recuos, entrelinha, margens, hierarquia tipográfica e fluxo das Sprints foram ajustados à referência visual da Mariah nos aspectos aprovados. A página da Figura 5 foi examinada e está centralizada, sem desequilíbrio que exija correção.
- O símbolo `°` é extraído e exibido corretamente. Reflexões mantêm bordas e podem continuar na página seguinte. Os placeholders de banco de dados e arquitetura permanecem identificados como provisórios e não simulam diagramas concluídos.

A lista original do ODT é uma lista de cinco itens. O ledger registra a decisão excepcional de ocultar os glifos, conserva o grupo e a quantidade de itens, e o teste de regressão bloqueia aplicação fora dessa unidade ou uma contagem diferente. O conteúdo dos itens não foi reescrito.

## Matriz normativa e institucional desta revisão

| Critério | Evidência e avaliação | Estado |
|---|---|---|
| Aplicabilidade da NBR 14724 ao memorial | A NBR 14724:2024 declara escopo para trabalhos acadêmicos e similares. A adoção de ABNT padrão foi definida pelo usuário, mas a confirmação formal de que esta entrega institucional específica é avaliada como trabalho regido pela NBR 14724 deve vir da professora/AGES. | PENDING institucional; as verificações abaixo usam a norma como referência solicitada |
| Identificação e apresentação de ilustrações | A cópia consultada da ABNT NBR 14724:2024, item 5.8, determina palavra designativa, número em algarismos arábicos, travessão e título; também prevê fonte imediatamente após a ilustração, citação no texto e inserção próxima do trecho pertinente. “Figura” é a designação em português e as páginas do PDF seguem essa ordem. | PASS de apresentação; PENDING para a proveniência real das cinco imagens |
| Fonte de cada imagem | A linha `Fonte` está abaixo de cada figura, mas o usuário reservou a identificação de origem para revisão manual. A norma exige indicação da fonte consultada ou de que a ilustração é de autoria própria. | PENDING; não é possível declarar conformidade substantiva destas cinco fontes |
| Formato, margens e entrelinha | NBR 14724:2024, itens 5.1–5.2, prevê A4, margens 3 cm superior/esquerda e 2 cm inferior/direita no anverso e entrelinha 1,5 no texto, com exceções em espaço simples. A configuração candidata usa A4, essas margens e entrelinha 1,5; legendas/fontes têm composição compacta. | PASS para a configuração observada; revisão normativa integral ainda pendente |
| Sumário e hierarquia | A NBR 14724 remete o sumário à NBR 6027 e a numeração progressiva à NBR 6024. A hierarquia visível, ordem e páginas foram verificadas no PDF. A consulta integral/atual das normas referenciadas não foi usada para certificar todos os detalhes. | PASS visual; PENDING normativo integral |
| Marcadores da lista de tecnologias | A NBR 14724:2024 consultada não estabelece, nos itens de apresentação verificados, uma proibição geral de marcadores. Por isso, a ausência deles decorre da preferência expressa do usuário e da calibração visual, sem atribuí-la à ABNT. A eventual aplicação de requisitos específicos de alíneas da NBR 6024 a esta lista continua pendente de conferência normativa completa. | PASS como escolha visual; PENDING para conclusão normativa específica |
| Links | As frases dos repositórios mantêm suas URLs originais como destinos e exibem âncoras em fonte regular. A validação confirma anotação clicável no PDF; não comprova disponibilidade atual dos servidores. | PASS preservação e destino no PDF; PENDING disponibilidade remota dos seis links de projeto |
| Orientação PUCRS / AGES | A referência da Mariah foi usada somente como padrão visual, conforme instrução do usuário. Não foi aplicada a Biblioteca PUCRS como modelo institucional. Não foi encontrada nesta revisão nova exigência específica da AGES além das decisões já registradas. | PENDING confirmação institucional adicional, se exigida pela orientação da professora |

Fonte normativa consultada: [ABNT NBR 14724:2024 — cópia do texto hospedada pela UFPB](https://www.ccs.ufpb.br/coordfarm/wp-content/uploads/sites/21/sites/454/2026/03/ABNT_NBR_14724_2024-1.pdf), itens 5.1, 5.2 e 5.8; o catálogo para consulta oficial de normas é o [ABNT Catálogo](https://www.abntcatalogo.com.br/pav.aspx). O texto integral das normas cruzadas e qualquer regra institucional específica não acessível permanece PENDING; este relatório não declara conformidade ABNT integral.

## Integridade e revisão independente

- **PASS:** 92 testes automatizados da suíte; 15/15 unidades da AGES I validadas, sem divergência textual registrada; integridade do ODT e dos 112 arquivos protegidos confirmada.
- **PASS:** auditoria da estrutura LaTeX encontrou 18 arquivos alcançáveis, 20 labels, 4 referências internas, 5 citações e 5 entradas bibliográficas, sem achados.
- **PASS:** duas compilações em cópias isoladas, com Tectonic 0.17.0 e Biber 2.17, produziram PDFs com o mesmo SHA-256. O relatório preserva os comandos, códigos de saída e hashes; o log TeX não contém avisos/erros. O gate oficial de produção não foi executado porque as mudanças seguem sem commit e aguardam revisão humana.
- **PASS_WITH_PENDING — conteúdo independente:** relatório [de auditoria de conteúdo](CONTENT_AUDIT_POST_FORMAT.md) e dados JSON (sua chave é o SHA deste PDF). A comparação foi feita contra o ODT, sem usar a justificativa do conversor como prova.
- **PASS_WITH_PENDING — visual independente:** [auditoria visual das 19 páginas](VISUAL_AUDIT_POST_FORMAT.md) e [resultado JSON](VISUAL_AUDIT_POST_FORMAT.json), ambos identificados pelo mesmo SHA. Nenhuma falha visual confirmada; fontes das imagens aguardam decisão manual.

## Pendências e próximo checkpoint

1. **PENDING — usuário:** identificar e fornecer a fonte/autoria de cada uma das cinco imagens reais. Não completar essas linhas por inferência.
2. **PENDING — conteúdo ausente:** receber posteriormente os diagramas reais de arquitetura e banco de dados; os dois placeholders continuam provisórios.
3. **PENDING — referências:** confirmar a disponibilidade atual dos seis links de projeto; as URLs originais foram mantidas.
4. **PENDING — normas/instituição:** concluir conferência das normas cruzadas vigentes e de eventual orientação específica da professora/AGES.
5. **PENDING — aceite humano:** revisar e aprovar ou pedir ajustes para este PDF identificado. Somente depois do aceite o padrão poderá ser registrado como permanente para os demais projetos. Nenhuma edição além de AGES I foi iniciada.

## Artefatos

- PDF de revisão do candidato anterior — 19 páginas; SHA-256 `3543f768de00b24de46fc09a615eec241ffe22197040e0a55e118ecba848e7f4`. O binário não está mais disponível nesse caminho; `build/document/main.pdf` aponta para o PDF atual identificado em [CURRENT_REVIEW.md](CURRENT_REVIEW.md).
- [Relatório de compilação reproduzível](../../build/document/review-candidate-report.json), [log TeX](../../build/document/main.log), [log do Biber](../../build/document/main.blg) e [bibliografia processada](../../build/document/main.bbl).
- [Manifesto](../CONTENT_MANIFEST.json), [divergências de texto/apresentação](TEXT_DIVERGENCES.json), [pendências](../PENDENCIAS.md) e [autorização explícita das correções](../../migration/approvals/ages-i-presentation-corrections.json).
