# Narração Carlos Jr — recuperação verificável

Este diretório adiciona uma rota de síntese VoxCPM2 à branch de recuperação.
Não modifica o editor publicado, o Fake Call nem o relay Render.
Os dez testes e a importação do VoxCPM passaram na execução 39471312713.
A execução 39472323151 concluiu a síntese em 2026-10-20, usando a referência
privada cadastrada pelo titular: WAV mono PCM16, 48000 Hz, 19,24 segundos.
A saída passou nas verificações de duração e presença de áudio.
O titular aprovou o áudio em 2026-10-20, após receber o resultado.
Só um WAV gerado, ouvido e aprovado confirma o resultado.

## Referência privada

A voz autorizada é obrigatória. O programa recusa ausência de referência,
download inválido, áudio curto demais, silencioso ou corrompido.
Não há fallback para voz genérica.

No repositório, abra Settings > Secrets and variables > Actions >
New repository secret e crie CARLOS_VOICE_REFERENCE_URL com o URL HTTPS
da referência privada já autorizada do usuário no HeyGen.
O URL não deve ser colocado no código, em inputs públicos de workflow,
issues, logs ou commits. O download só permite resource2.heygen.ai.
Uma referência WAV própria também pode ser usada localmente.

A configuração do secret exige ação do titular: o conector usado nesta
conversa não oferece escrita na API de secrets do GitHub.

## Execução da branch de recuperação (autorizada pelo titular)

O workflow roda os testes e valida a importação do motor em pull requests
e em pushes na main. A etapa de narração só roda quando o secret existe, após os testes.
Sem secret, o resumo registra "Referência pendente", sem gerar áudio.

Após cadastrar o secret, um novo commit em voice/ ou no workflow dispara
a geração. A aba Actions mostra o progresso e disponibiliza o artefato
Treino-Livre-Carlos-Jr-<run_id> após conclusão.

O arquivo de referência não é versionado, enviado a artefatos nem cacheado.
Os únicos artefatos são a narração final, métricas, segmentos e dependências.
A retenção é de um dia. O repositório é público; quem tem acesso aos
artefatos pode ouvir a narração promocional, portanto não use roteiro privado.

O runner padrão Ubuntu evita cobrança de serviços de voz.
Os minutos de runners padrão são gratuitos em repositórios públicos segundo
a documentação do GitHub. Armazenamento segue a cota da conta.
A síntese em CPU é experimental e pode ser lenta ou exceder memória/tempo.
Não há provisionamento de runner pago nem alteração do plano Render.

## Uso local com modelo baixado

Python 3.11, FFmpeg, bibliotecas de voice/constraints.txt e código VoxCPM
fixado em cce58a5b59303c9bd63d12f23afe6a49a4a80c59.

    python voice/narrate.py --text-file voice/roteiro-treino-livre.txt \
      --reference /caminho/privado/minha-voz.wav \
      --output /caminho/privado/narracao.wav --device cpu

O download do modelo usa snapshot_download e reaproveita o cache local.
O SHA efetivamente resolvido é registrado no JSON. Para repetir exatamente
o snapshot, informe --model-revision <SHA registrado>.

## Critérios de resultado

- Os testes verificam silêncio, truncamento, canais, duração, preservação
  das palavras ao dividir o roteiro e sigilo dos erros de transporte.
- A importação do VoxCPM é um teste de instalação; não é teste de síntese.
- A síntese grava WAV mono PCM16 com a taxa nativa do modelo.
- Valida finitude, silêncio e duração antes de publicar a saída.
- O JSON registra "synthesized_needs_listening_review": métricas técnicas
  não comprovam fidelidade do texto nem semelhança vocal.
- Ouvir e comparar com a referência antes de aplicar ao vídeo.
- Falhas encerram a execução; não reciclam arquivo de outra narração.

Fontes:
https://github.com/OpenBMB/VoxCPM
https://docs.github.com/en/actions/reference/runners/github-hosted-runners

## Execução comprovada e continuidade da montagem

- Execução: https://github.com/Carlosjr81/Jarvis-Studio-Editor/actions/runs/39472323151
- Artefato (retenção de 24 horas): https://github.com/Carlosjr81/Jarvis-Studio-Editor/actions/runs/39472323151/artifacts/12288806792
- Pesos fixados no snapshot: 32279effe8c19989596f05d353d1447f51d9e915
- O secret é persistente no repositório; a referência não está nos commits.
- O fluxo pode rodar manualmente pela aba Actions ou por alterações em voice/ na main.

MoneyPrinterTurbo aceita narração externa. Depois de ouvir o WAV, use o
argumento --custom-audio-file com seu caminho real em cada execução: esse
caminho não é persistido pela WebUI. O áudio precisa existir antes da montagem.
Não substituir ausência de WAV por uma voz padrão.

Compatibilidade conferida no README-en.md e app/services/task.py do commit
90f77011d7e3b46d382e6d0180dabfb6725ffee4 do MoneyPrinterTurbo.
O manual é guia de instalação/montagem; não contém backup do perfil vocal.
