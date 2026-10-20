# Narração Carlos Jr — recuperação verificável

Esta branch contém um programa de síntese com VoxCPM2 e um workflow que
somente testa código e instalação. A geração em GitHub Actions ainda não
está habilitada. Nenhuma referência de voz é usada pelo workflow atual.

O editor publicado, o Fake Call e o relay Render não são modificados.
Só um WAV gerado, ouvido e aprovado confirma uma narração pronta.

## Referência privada obrigatória

O programa de síntese recusa ausência de referência, download inválido,
áudio curto demais, silencioso ou corrompido. Não há voz genérica substituta.

No uso local, passe um arquivo próprio por --reference. A opção
--reference-url-env lê o URL de uma variável de ambiente, com origem HTTPS
restrita a resource2.heygen.ai e mensagens de falha sem o URL privado.
Nunca coloque a referência ou seu URL no código, issues, logs ou commits.

Para uma futura execução em nuvem, é necessário autorizar explicitamente
o processamento da referência pelo GitHub Actions e definir o destino da
narração resultante. O workflow atual não acessa secrets, não baixa áudio
de referência e não publica artefatos de voz.

A gravação de secrets requer ação do titular: o conector desta conversa
não oferece escrita na API de secrets do GitHub.

## Validação disponível

A aba Actions executa:
1. Compilação Python e testes com áudio sintético de tom puro.
2. Instalação de Torch CPU e do VoxCPM fixado no commit abaixo.
3. Verificação de dependências e importação do VoxCPM.

Não há síntese nem download de pesos do modelo nesse teste.
O runner padrão Ubuntu usa os minutos gratuitos de repositórios públicos,
segundo a documentação do GitHub. Não há runner pago ou mudança do Render.

## Instalação e uso local

Python 3.11, FFmpeg e libsndfile são necessários.

    python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.8.0 torchaudio==2.8.0
    python -m pip install -c voice/constraints.txt 'voxcpm @ git+https://github.com/OpenBMB/VoxCPM.git@cce58a5b59303c9bd63d12f23afe6a49a4a80c59'
    python -m pip check
    python voice/narrate.py --text-file voice/roteiro-treino-livre.txt \
      --reference /caminho/privado/minha-voz.wav \
      --output /caminho/privado/narracao.wav --device cpu

A síntese em CPU ainda precisa ser testada e pode exceder memória/tempo.
O programa faz o download de openbmb/VoxCPM2 e reaproveita o cache local.
O SHA resolvido é registrado no JSON. Para repetir o snapshot exato,
informe --model-revision <SHA registrado>. Não há integração automática
operacional com o assistente nem com o editor publicado nesta branch.

## Critérios de resultado

- Os testes verificam silêncio, truncamento, canais, duração, preservação
  das palavras ao dividir o roteiro e sigilo dos erros de transporte.
- Importação do motor comprova instalação; não comprova síntese.
- O programa grava WAV mono PCM16 com a taxa nativa do modelo.
- Valida finitude, silêncio e duração antes de gravar a saída final.
- O JSON registra synthesized_needs_listening_review: as métricas não
  comprovam fidelidade do texto nem semelhança vocal.
- Ouvir e comparar com a referência antes de aplicar ao vídeo.
- Falhas encerram a execução sem reciclar narração de outro trabalho.

Fontes:
https://github.com/OpenBMB/VoxCPM
https://docs.github.com/en/actions/reference/runners/github-hosted-runners
