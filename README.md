# Jarvis Studio · OpenCut

Editor de vídeo com a interface do OpenCut Classic e um painel adicional do Jarvis Studio.

Use o editor: https://jarvis-studio-video.carlos-jr-81.chatgpt.site

## Privacidade

O endereço do editor compartilha o software. Ele não compartilha projetos, vídeos, fotos, arquivos, contas conectadas ou credenciais do proprietário.

- Edição local: mídias e projetos ficam no navegador e dispositivo de cada visitante. Pessoas usando o mesmo perfil de navegador compartilham esse armazenamento local.
- Nuvem: cada operação exige identidade autenticada do ChatGPT fornecida pelo Sites. O servidor isola projetos, mídias, pedidos e resultados pelo identificador do usuário; conhecer um identificador de projeto não autoriza acesso.
- Contas de ferramentas externas: o editor não herda conexões ou tokens do ChatGPT do proprietário. Cada pessoa precisa de acesso próprio para ferramentas externas e eventuais serviços pagos.
- O repositório contém código e ativos públicos do software. Não contém vídeos, projetos pessoais, backups, amostras de voz ou segredos de contas.

## Código completo

O pacote `jarvis-studio-source.zip` contém os 1.072 arquivos do código e dos ativos públicos, com suas pastas preservadas. Baixe o arquivo e extraia antes de executar os comandos abaixo. Não há projetos pessoais, mídias de usuários ou credenciais nesse pacote.

## Desenvolvimento

```sh
npm ci
npm run build:opencut
```

A interface OpenCut é gerada em `opencut/out`. Sirva com fallback de SPA para usar as rotas de projetos e editor. O painel integrado depende das rotas do Studio original (`/studio`) no servidor incluído em `worker/`.

Para a hospedagem Sites completa, configure sua própria `.openai/hosting.json` com a identidade real do seu Site, binding R2 `BUCKET` e a capability MCP. Execute `npm run build` e publique pelo fluxo oficial Sites. Este repositório não concede acesso ao Site ou armazenamento do autor.

A busca Freesound usa o segredo opcional `FREESOUND_API_KEY` no servidor. Nunca inclua chaves no código ou em arquivos versionados.

## Origem e limites

OpenCut Classic: https://github.com/OpenCut-app/opencut-classic · commit `cf5e79e919144200294fb9fed22a222592a0aeea`. A licença MIT upstream está preservada em `opencut/LICENSE`. O projeto principal está em reescrita. Funções anunciadas para a nova API/MCP/headless não fazem parte desta incorporação.

As abas de transições e ajustes ainda têm funções incompletas upstream. O suporte visual a celular não está otimizado pelo OpenCut Classic. GPU, codecs, renderização e exportação variam conforme o navegador.

## Verificações

Compilação, motor WASM, backups com mídias/efeitos, autenticação, isolamento por usuário, CSRF, limites de arquivos, entrega HTTP, timeline, legendas, fila e retorno do Jarvis foram verificados. A reprodução/exportação em cada aparelho deve ser validada separadamente.
