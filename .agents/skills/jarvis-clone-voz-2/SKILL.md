---
name: jarvis-clone-voz-2
description: Gerar narração com a voz própria previamente aprovada do titular, recuperando perfil privado e usando VoxCPM2 local sem créditos. Usar para Jarvis Clone Voz 2, minha voz aprovada ou narração pessoal em vídeos.
---

# Jarvis Clone Voz 2

Ler [fluxo aprovado](references/approved-flow.md), [operação](references/operation.md) e [origem](references/origin.md). Manter referência aprovada; não gerar outro clone nem trocar por voz genérica automaticamente.

1. Recuperar o perfil privado de voz padrão do titular pela Library, usando o identificador real já disponível ou busca por finalidade. Ler o perfil atual e materializar o pacote nele indicado. Não pedir os vídeos novamente sem tentar recuperar o pacote.
2. Resolver `default_voice.json`, referência e transcrição reais. Exigir is_default=true, aprovação approved_by_user e hash igual ao aprovado.
3. Executar `python scripts/preflight.py --voice-profile CAMINHO/default_voice.json`.
4. Sintetizar o roteiro solicitado com `python scripts/narrate_approved.py --voice-profile CAMINHO/default_voice.json --text-file ROTEIRO.txt --output NARRACAO.wav`. O script usa pesos em cache, verifica a revisão instalada e não aciona serviço pago.
5. Conferir duração, integridade, palavras, escuta e truncamento. Registrar hashes e parâmetros. A aprovação da referência não substitui revisão do áudio novo.
6. Salvar e entregar o WAV pedido; em vídeo, fornecer a narração em pista separada para Instagram 2 ou Studio Editor 2. Não adicionar música sem pedido.

Preferir execução local. Se faltar motor, pesos ou pacote, dizer qual; executar partes independentes sem substituir por clone antigo. Não alterar tom ou velocidade automaticamente. Não usar o secret antigo de um workflow alegando que contém a nova referência.

Acesso ao SKILL.md, cadastro no catálogo, arquivo de voz gerado e semelhança aprovada são verificações distintas. Não prometer disponibilidade global apenas por salvar código no GitHub.
