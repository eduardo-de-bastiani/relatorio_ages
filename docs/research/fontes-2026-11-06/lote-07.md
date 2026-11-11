# Pesquisa de datas bibliográficas — lote 07

**Consulta:** 2026-11-06.  
**Escopo:** quatro chaves atribuídas, conferidas nas URLs cadastradas em `relatorio_AGES_eduardo/bibliografia/bibliografia.bib`. As datas `urldate = 2026-10-17` que permanecem nos registros são anteriores e foram tratadas somente como acessos já registrados localmente; não são a consulta deste lote nem datas de publicação.

## Resultados

### `ages-iv-python`

- **Registro:** Python Software Foundation, “Our Documentation”; URL cadastrada: <https://www.python.org/doc/>.
- **Fonte efetivamente aberta:** a URL exata foi aberta sob o título “Our Documentation | Python.org”. O conteúdo apresenta uma lista de recursos de documentação Python e um link para a documentação Python 3 atual. Não observei redirecionamento. A resposta da ferramenta exibiu uma versão de fallback porque scripts interativos não rodaram.
- **Datas encontradas:** no rodapé da página exata consta “Copyright ©2001-2026” da Python Software Foundation. É copyright geral da página/site, sem data de publicação ou de atualização identificada para o documento. A página vinculada em `https://docs.python.org/3/` declara documentação de Python 3.15.2 e “Last updated on Nov 06, 2026 (08:38 UTC)”; esse é outro documento (a documentação da versão), não a página `/doc/` citada, portanto não usei essa atualização como data da referência.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — somente o copyright geral 2001–2026 está documentado na página citada. Publicação e atualização específicas permanecem sem comprovação; não atribuir 2026 como ano de publicação.
- **Confiabilidade/limitação:** alta para identidade, URL, conteúdo apresentado e copyright visível; insuficiente para datar a publicação da página. O link para a documentação corrente é variável e aponta a outro documento. Fontes abertas: [página cadastrada](https://www.python.org/doc/) e [documentação Python 3 vinculada](https://docs.python.org/3/).

### `ages-iv-fastapi`

- **Registro:** “Tutorial - User Guide”; URL cadastrada: <https://fastapi.tiangolo.com/tutorial/>.
- **Fonte efetivamente aberta:** a URL exata foi recuperada como “Tutorial - User Guide - FastAPI”, sem redirecionamento observado. O conteúdo aberto corresponde ao tutorial e não exibe data de publicação nem indicação “last updated”. O repositório oficial do FastAPI contém o arquivo-fonte `docs/en/docs/tutorial/index.md`, com o mesmo título e conteúdo identificador do tutorial. A página de histórico desse caminho foi aberta, mas a ferramenta mostrou somente registros até março de 2026 e identificou a própria captura como antiga; não serve para datar a versão corrente nem comprova quando a página online foi publicada.
- **Datas encontradas:** nenhuma data editorial explícita na página exata. A história pública do arquivo-fonte registra alterações ao longo do tempo, mas datas de commits não foram tratadas como data de publicação da página. Não foi encontrado copyright datado relevante para este documento na resposta aberta.
- **Classificação:** `PENDENTE` — identidade e conteúdo foram confirmados, mas não há evidência direta suficiente de ano de publicação, criação ou atualização da página online.
- **Confiabilidade/limitação:** alta para título e conteúdo atual da URL citada; insuficiente para data documental. A correspondência do arquivo-fonte está sustentada pelo título/conteúdo; seu histórico consultado estava incompleto/desatualizado e não foi usado como prova cronológica. Fontes: [tutorial cadastrado](https://fastapi.tiangolo.com/tutorial/), [arquivo-fonte oficial](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/tutorial/index.md) e [histórico consultado](https://github.com/fastapi/fastapi/commits/master/docs/en/docs/tutorial/index.md).

### `ages-iv-pydantic`

- **Registro:** “Pydantic Validation”; URL cadastrada: <https://pydantic.dev/docs/validation/latest/get-started/>.
- **Fonte efetivamente aberta:** a URL exata foi recuperada como “Pydantic Validation | Pydantic Docs”, sem redirecionamento observado. A própria página informa “Documentation for version: v2.14.3” e o rodapé mostra “© Pydantic Services Inc. 2025 to present”.
- **Datas encontradas:** o histórico oficial de versões do projeto identifica a versão `v2.14.3` com data `2026-11-04`; a mesma página informa que a release foi publicada no GitHub em 05 Nov, 09:18 (sem fuso indicado no texto recuperado). Essas são datas da versão/release do software, não data de publicação da página de documentação. O copyright “2025 to present” é geral, não data editorial da página.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — a página identifica a versão documentada (v2.14.3), e a release oficial documenta data da versão. Não há publicação nem atualização da página explicitamente datadas; não converter a data da versão em ano de publicação.
- **Confiabilidade/limitação:** alta para título, URL e versão declarada na documentação; alta para os elementos de data conforme apresentados na página oficial de release. A rota `/latest/` é mutável e pode passar a representar outra versão. Fontes: [documentação cadastrada](https://pydantic.dev/docs/validation/latest/get-started/) e [release oficial v2.14.3](https://github.com/pydantic/pydantic/releases/tag/v2.14.3).

### `ages-iv-react-native`

- **Registro:** Meta Platforms, Inc., “Introduction”; URL cadastrada: <https://reactnative.dev/docs/getting-started>.
- **Fonte efetivamente aberta:** a URL exata foi recuperada como “Introduction · React Native”; o H1 é “Introduction”. Não observei redirecionamento. A navegação da página lista “Next” e as versões numeradas, portanto a rota sem versão é mutável. O link de edição distingue a página “next release” e a edição da versão corrente.
- **Datas encontradas:** a própria página exibe “Last updated on Oct 27, 2026”. É data de atualização, não de publicação. A página não informa ano de publicação inicial nem copyright datado no rodapé recuperado.
- **Classificação:** `OUTRA_DATA_DOCUMENTADA` — atualização explícita em 2026-10-27; publicação inicial não comprovada.
- **Confiabilidade/limitação:** alta para título, URL e data de atualização declarada na própria página. Tentei abrir o histórico dos arquivos ligados pelos controles “Edit page”; a ferramenta retornou “Cache miss”, então esse histórico não foi examinado. A rota pode acompanhar a documentação corrente. Fonte: [página cadastrada](https://reactnative.dev/docs/getting-started).

## Contagem e limitações

- `PUBLICACAO_COMPROVADA`: 0
- `OUTRA_DATA_DOCUMENTADA`: 3
- `ANO_ESTIMADO_FUNDAMENTADO`: 0
- `PENDENTE`: 1
- `INACESSIVEL`: 0

As quatro URLs cadastradas foram abertas nesta consulta. Copyright geral, data de versão/release, data de atualização e consulta foram mantidos distintos da publicação. As datas de acesso `2026-10-17` nos registros não foram reatribuídas nem verificadas como novas consultas. Limitações: a abertura da página python.org/doc apresentou fallback por scripts indisponíveis; o histórico da fonte FastAPI estava desatualizado na captura e o histórico dos arquivos de edição do React Native retornou “Cache miss”. Nenhuma data estimada foi proposta.
