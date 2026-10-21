# Narração Carlos Jr — recuperação verificável

## Referência vigente para novos vídeos — 20/10/2026

O titular enviou nove novos vídeos (340544, 340551, 340553, 340555,
340557, 340559, 340561, 340562 e 340580) e pediu que servissem de base
para sua voz em todos os vídeos futuros. O clone anterior foi rejeitado
pelo titular por falta de semelhança. Não usá-lo como substituto silencioso.

O banco privado `Carlos_Jr_Voz_2026-10-20.zip` contém os áudios originais,
onze trechos de fala, transcrições automáticas e `perfil_voz.json`.
Recuperar esse arquivo privado pelo conector ChatGPT Library; não colocar
amostras, identificadores privados ou URLs assinados neste repositório público.
O perfil distingue preparação, síntese e aprovação da semelhança vocal.
As transcrições automáticas ainda exigem conferência por escuta.

Usar a referência principal do banco com áudio e transcrição:

    python voice/narrate.py --text-file roteiro.txt \
      --reference /caminho/privado/Carlos_Jr_Referencia_Principal.wav \
      --reference-text-file /caminho/privado/Carlos_Jr_Referencia_Principal.txt \
      --output /caminho/privado/narracao.wav --device cpu

Com `--reference-text-file`, o motor recebe a mesma referência como
`reference_wav_path` e `prompt_wav_path`, mais seu `prompt_text`.
Registrar hashes da referência e da transcrição no resultado. Sem o argumento,
a rota antiga de clonagem só por áudio permanece disponível por compatibilidade.
Preservar os nove áudios para selecionar outra tomada quando necessário;
não concatenar as pausas, tomadas repetidas e ruído como uma referência única.

O workflow atual continua lendo o secret anterior; esta alteração não o
substitui. Não iniciar uma geração por esse workflow afirmando usar as
novas amostras sem atualizar/verificar sua referência privada primeiro.
A habilidade pessoal instalada também precisa apontar para o novo banco:
o diretório `/root/.codex/skills/remote-skills` estava ausente nesta sessão,
logo não houve salvamento da habilidade. A política e o suporte a áudio+texto
ficam persistidos neste projeto, sem declarar integração global concluída.

Este diretório adiciona uma rota de síntese VoxCPM2 à branch de recuperação.
Não modifica o editor publicado, o Fake Call nem o relay Render.
Os dez testes e a importação do VoxCPM passaram na execução 39471312713.
A execução 39472323151 concluiu a síntese em 2026-10-20, usando a referência
privada cadastrada pelo titular: WAV mono PCM16, 48000 Hz, 19,24 segundos.
A saída passou nas verificações de duração e presença de áudio.
O registro anterior de aprovação foi superado pelo relato posterior do titular
de que a voz estava estranha e não se parecia com sua voz.
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

O workflow roda somente por acionamento manual na aba Actions.
Primeiro executa os testes e valida a importação do motor.
A etapa de narração só roda quando o secret existe, após os testes.
Sem secret, o resumo registra "Referência pendente", sem gerar áudio.

Após cadastrar o secret, abra Actions > Jarvis - Voz Carlos Jr > Run workflow.
A geração exige esse acionamento explícito em cada execução. A aba Actions mostra o progresso e disponibiliza o artefato
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
- O fluxo só roda manualmente pela aba Actions; commits não iniciam novas gerações.

MoneyPrinterTurbo aceita narração externa. Depois de ouvir o WAV, use o
argumento --custom-audio-file com seu caminho real em cada execução: esse
caminho não é persistido pela WebUI. O áudio precisa existir antes da montagem.
Não substituir ausência de WAV por uma voz padrão.

Compatibilidade conferida no README-en.md e app/services/task.py do commit
90f77011d7e3b46d382e6d0180dabfb6725ffee4 do MoneyPrinterTurbo.
O manual é guia de instalação/montagem; não contém backup do perfil vocal.
