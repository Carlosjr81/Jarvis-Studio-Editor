---
name: jarvis-clone-voz
description: Gerar narração de vídeos com a voz própria do titular previamente aprovada por ele, usando referência privada e VoxCPM2 local sem créditos. Usar para Jarvis Clone Voz, minha voz clonada, narração com minha voz ou voz aprovada em vídeos futuros, inclusive em fluxos de edição de vídeo.
---

# Jarvis Clone Voz

Usar somente a referência vocal privada que o titular já ouviu e aprovou. Preservar seu timbre e o modo de geração do teste. Não criar outro clone nem trocar o trecho de referência automaticamente.

## Recuperar a voz em um chat novo

1. Usar a habilidade Library para buscar o perfil privado de voz padrão aprovada do titular. Reutilizar o identificador quando fornecido pelo contexto; caso contrário, buscar pelo propósito e ler o resultado. Não selecionar perfil de outra pessoa. Se persistir ambiguidade entre perfis aprovados, esclarecer qual deve ser usado.
2. Recuperar o pacote de referências privadas indicado no perfil, seguindo o fluxo de materialização da Library. Resolver o arquivo a partir do perfil lido; não inventar títulos, identificadores ou caminhos de conversas anteriores.
3. Ler `default_voice.json`. Exigir `is_default=true`, `approval.status=approved_by_user` e SHA256 do áudio igual a `reference_sha256`. Usar `reference_audio` e `reference_transcript` do perfil; não usar a amostra sintetizada como nova referência.
4. Manter amostras e identificadores privados fora de repositórios públicos e logs. Preservar as demais tomadas apenas como arquivo.

## Gerar o áudio solicitado

Receber o roteiro ou usar o já fornecido na tarefa de vídeo. Priorizar síntese local sem créditos; não acionar serviços pagos como alternativa automática.

Usar o código VoxCPM do commit `cce58a5b59303c9bd63d12f23afe6a49a4a80c59` e o modelo `openbmb/VoxCPM2` no snapshot `32279effe8c19989596f05d353d1447f51d9e915`. Reaproveitar pesos disponíveis. Usar PyTorch CPU 2.8.0, torchaudio 2.8.0 e transformers 4.57.1, compatíveis com o fluxo validado. Python, PyTorch CPU, NumPy e SoundFile são necessários. Não presumir instalação nem disponibilidade dos pesos em um ambiente novo.

Repetir o fluxo do teste aprovado, com os caminhos reais da referência recuperada:

```python
from pathlib import Path
import torch
import numpy as np
import soundfile as sf
from huggingface_hub import snapshot_download
from voxcpm import VoxCPM

snapshot = snapshot_download('openbmb/VoxCPM2', revision='32279effe8c19989596f05d353d1447f51d9e915')
torch.set_num_threads(4)
old_dtype = torch.get_default_dtype()
try:
    torch.set_default_dtype(torch.bfloat16)
    model = VoxCPM.from_pretrained(snapshot, load_denoiser=False,
                                  optimize=False, device='cpu', local_files_only=True)
finally:
    torch.set_default_dtype(old_dtype)

with torch.inference_mode():
    wav = np.asarray(model.generate(
        text=roteiro, reference_wav_path=str(referencia),
        prompt_wav_path=str(referencia),
        prompt_text=Path(transcricao).read_text(encoding='utf-8').strip(),
        seed=42, cfg_value=2.0, inference_timesteps=10,
        max_len=256, retry_badcase=False), dtype=np.float32).reshape(-1)
```

Definir `roteiro`, `referencia`, `transcricao` e o destino a partir da tarefa e do pacote. Não deixar variáveis sem resolução na execução. Dividir roteiros longos por frases, com até 200 caracteres por trecho e sem perder palavras. Manter seed 42, cfg 2.0 e 10 passos em cada trecho. Se o limite de geração for atingido, reduzir o tamanho da frase e gerar novamente; não entregar uma fala cortada.

Validar que o áudio seja finito, não silencioso e tenha duração compatível com o roteiro. Concatenar trechos com pausas de 0,14 s e atenuar somente quando o pico exceder 0,98. Gravar PCM16 mono com a taxa nativa de 48 kHz. Não alterar tom ou velocidade automaticamente. Registrar no resultado os hashes da referência e do áudio, o snapshot e os parâmetros efetivos. Parâmetros iguais não garantem identidade binária entre hardwares diferentes.

Conferir o texto gerado por transcrição quando houver recurso disponível. A aprovação desta referência não substitui a conferência de conteúdo de cada novo vídeo.

## Salvar e integrar

Salvar a narração solicitada pela Library e entregar o arquivo. Se a tarefa incluir montagem de vídeo, fornecer a narração ao fluxo Jarvis Instagram como pista separada de música e efeitos, preservando as regras da marca. Não adicionar trilha nem publicar conteúdo por conta deste pedido de voz.

## Tratar indisponibilidade

Se houver acesso ao pacote e ao motor, gerar mesmo que a pasta de cadastro de habilidades esteja indisponível. Se faltar pacote, modelo ou execução, informar o componente exato, sem substituir por voz genérica.

Só declarar a habilidade instalada em chats novos após confirmar cadastro pessoal ou distribuição por plugin. Fonte versionada em um projeto comprova preservação, não instalação global.

