# Pesquisa de datas bibliográficas — lote 06

**Consulta:** 2026-11-06.  
**Escopo:** cinco chaves atribuídas, verificadas nas URLs cadastradas em `relatorio_AGES_eduardo/bibliografia/bibliografia.bib`. As datas `urldate = 2026-10-16` já registradas na bibliografia são anteriores e não foram tratadas como consulta deste lote nem como datas documentais.

## Resultados

### `ages-iii-figma`

- **Registro:** Figma, “Guide to prototyping in Figma”; URL cadastrada: <https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma>.
- **Fonte aberta:** a URL exata foi recuperada como “Guide to prototyping in Figma – Figma Learn - Help Center”; o corpo confirma o título “Guide to prototyping in Figma” e trata de fluxos, conexões e interações de protótipos. Não foi observado redirecionamento no resultado da abertura.
- **Datas encontradas:** a página aberta não exibe publicação ou última atualização; busca no texto recuperado por “updated”, “Published” e “©” não encontrou esses elementos. A consulta ao endpoint público de artigo Zendesk (`https://help.figma.com/api/v2/help_center/en-us/articles/360040314193.json`) não foi examinável pela ferramenta web; portanto não se obteve metadado de criação/atualização por essa via.
- **Classificação:** `PENDENTE` — a identidade e o conteúdo da página foram confirmados, mas não há evidência direta de ano de publicação, criação ou atualização. Nenhuma data de artigo relacionado ou de busca foi atribuída a esta página.
- **Confiabilidade/limitação:** alta para título, URL e conteúdo atual; insuficiente para data documental. A falta de data exibida não prova que a página nunca tenha sido datada em metadado não exposto.

### `ages-iii-javascript`

- **Registro:** “Introduction - JavaScript | MDN”; URL cadastrada: <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Introduction>.
- **Fonte aberta:** a URL exata foi recuperada com o título “Introduction - JavaScript | MDN”; não foi observado redirecionamento. O corpo identifica a página como a introdução do JavaScript Guide.
- **Datas encontradas:** ao final da página, MDN declara: “This page was last modified on Jul 8, 2026 by MDN contributors.” Trata-se explicitamente da **última modificação**, não de publicação inicial. A página liga ao arquivo correspondente em `mdn/content` no GitHub; tentei abrir a página de histórico de commits desse caminho, mas a ferramenta retornou “Cache miss”. A página oficial aberta basta para documentar a atualização; o histórico não foi confirmado independentemente.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — atualização explicitamente identificada em 2026-07-08; ano de publicação/criação não comprovado.
- **Confiabilidade/limitação:** alta para o título, URL e data de última modificação declarada pela própria MDN; não há evidência de publicação inicial. O rodapé geral também informa conteúdo ©1998–2026 por contribuidores individuais, mas esse intervalo de copyright não foi usado como data da página. A página apresenta atribuição a contribuidores MDN e não nomeia Mozilla como autora individual ou exclusiva.

### `ages-iii-rfid-parking-use-cases`

- **Registro:** TransCore, “Parking & Access Control”; URL cadastrada: <https://transcore.com/rfid/parking-access-control>.
- **Fonte aberta:** a URL exata foi recuperada como “TransCore | Parking & Access Control”; H1 “Parking & Access Control”. O conteúdo descreve aplicações de identificação automática de veículos/RFID em estacionamento e controle de acesso. Não foi observado redirecionamento.
- **Datas encontradas:** não há data de publicação ou atualização explícita no conteúdo recuperado. O rodapé da página mostra “© TransCore 2026”. Isso é copyright geral do site, não data identificada para este documento.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — apenas copyright geral 2026 está visível; ano de publicação/criação/atualização da página permanece não comprovado.
- **Confiabilidade/limitação:** alta para identidade, conteúdo e copyright visível; baixa para qualquer inferência de data documental. Não atribuir 2026 como ano de publicação.

### `ages-iii-impinj-r700`

- **Registro:** Impinj, Inc., “Impinj R700 Series RAIN RFID Readers”; URL cadastrada: <https://www.impinj.com/products/readers/impinj-r700>.
- **Fonte aberta:** a URL exata foi recuperada, sem redirecionamento observado. O H1 é “Impinj R700 Series RAIN RFID Readers”; o título de navegador atual acrescenta a chamada “for Enterprise-grade IoT Solutions”. A página atualmente apresenta uma seção “Meet the upgraded Impinj R700” e recursos da série R700.
- **Datas encontradas:** não há publicação ou atualização identificada para a página. O rodapé informa “© 2012 - 2026 Impinj, Inc. All rights reserved.”, intervalo de copyright corporativo geral. A página lista notícias e conteúdos relacionados datados — inclusive anúncio de produto —, mas essas datas são dos itens relacionados, não desta página; não foram usadas como data dela.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — copyright geral corporativo 2012–2026; publicação/atualização da página não comprovada.
- **Confiabilidade/limitação:** alta para identidade, título H1, conteúdo atual e aviso de copyright; o copyright não é data de publicação do documento. O texto atual enfatiza uma versão “upgraded”, sem número de versão ou data que permita datar a página citada.

### `ages-iii-impinj-iot-interface`

- **Registro:** Impinj, Inc., “Impinj IoT Device Interface”; URL cadastrada: <https://www.impinj.com/products/technology/key-features/iot-device-interface>.
- **Fonte aberta:** a URL exata foi recuperada, sem redirecionamento observado. O H1 é “Impinj IoT Device Interface”. A página descreve interface web, REST API, transferência MQTT/Kafka, eventos e compatibilidade com modelos de leitores.
- **Datas encontradas:** não há publicação ou atualização identificada para a página. O rodapé informa “© 2012 - 2026 Impinj, Inc. All rights reserved.”, copyright corporativo geral. Entre os conteúdos relacionados consta “Impinj IoT Device Interface Enables Deploying Impinj R700 at Scale”, datado de 29 Dec 2020. Essa data pertence ao item de blog relacionado, não à página consultada, e não comprova publicação desta página.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — copyright geral corporativo 2012–2026; publicação/atualização da página não comprovada.
- **Confiabilidade/limitação:** alta para identidade, título H1, conteúdo atual e copyright; nenhuma evidência direta de quando a página foi publicada ou atualizada. A data de dezembro de 2020 é apenas de conteúdo relacionado e não foi adotada como data da fonte.

## Contagem e limitações

- `PUBLICACAO_COMPROVADA`: 0
- `OUTRA_DATA_DOCUMENTADA`: 4
- `ANO_ESTIMADO_FUNDAMENTADO`: 0
- `PENDENTE`: 1
- `INACESSIVEL`: 0

As cinco páginas exatas foram recuperadas nesta consulta, mas nem todas expõem metadados editoriais. Não foi possível examinar o endpoint Zendesk da Figma nem a página de histórico GitHub da MDN por retorno “Cache miss” da ferramenta. Não se usaram resultados de busca, copyright geral, datas de itens relacionados, datas de consulta ou datas de acesso como prova de publicação. A consulta deste lote ocorreu em 2026-11-06; isso não altera o `urldate` já registrado para essas referências.
