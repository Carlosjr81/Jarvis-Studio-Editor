# Voz aprovada e recuperação privada

A referência vocal ouvida e aprovada pelo titular em 20/10/2026 substitui clones anteriores rejeitados. Recuperar pela Library o perfil privado de voz padrão aprovado do titular. Usar identificador já fornecido no contexto ou buscar pelo propósito e ler o perfil atual. Recuperar o pacote nele indicado, sem publicar nomes de arquivos privados, IDs, gravações ou segredos no código compartilhável.

Dentro do pacote, ler default_voice.json. Exigir is_default=true, approval.status=approved_by_user e SHA256 de reference_audio igual a reference_sha256. Não usar áudio sintetizado como referência. Priorizar o fluxo local VoxCPM2 documentado em voice-runtime.md; VoiceStudio permanece opção local somente se conseguir respeitar a referência aprovada. Provedores anteriores não substituem automaticamente a voz atual.

Usar código VoxCPM no commit cce58a5b59303c9bd63d12f23afe6a49a4a80c59, modelo openbmb/VoxCPM2 no snapshot 32279effe8c19989596f05d353d1447f51d9e915, referência áudio+transcrição, seed 42, cfg 2.0, 10 passos e saída PCM16 mono 48 kHz. Conferir disponibilidades reais; a pasta de habilidade não instala o motor.

Usar o fluxo integrado mesmo sem o atalho Jarvis Clone Voz. Validar com `python scripts/preflight.py --voice-profile CAMINHO/default_voice.json`. Se faltar pacote, motor ou pesos, identificar o componente e continuar tarefas independentes, sem trocar por voz genérica.

Para sintetizar com perfil aprovado e pesos já presentes, executar `python scripts/narrate_approved.py --voice-profile CAMINHO/default_voice.json --text-file ROTEIRO.txt --output NARRACAO.wav`. O script não baixa pesos nem usa créditos. Verificar a revisão instalada do código VoxCPM antes de declarar reprodução do ambiente original. Usar voice-runtime.md como referência técnica e conferir cada saída por transcrição e escuta. Fracionar texto longo em frases até 200 caracteres; conferir ausência de truncamento e palavras perdidas, pausas de 0,14 s, pico até 0,98 sem alteração automática de tom ou velocidade. Conferir texto e escuta de cada nova locução; aprovação da referência não aprova automaticamente todo áudio futuro.
