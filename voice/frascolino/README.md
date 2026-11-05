# Frascolino translúcido PET — Globalpack

Fluxo exclusivo de clonagem por referência usando VoxCPM2 em CPU no GitHub Actions.
Não lê nem modifica o perfil, os secrets ou os arquivos da voz pessoal de Carlos Jr.
O código público não contém referência privada, URL de download, senha ou áudio.

## Configurar a referência e executar

1. Em Settings > Secrets and variables > Actions, crie dois secrets exclusivos:
   - FRASCOLINO_REFERENCE_URL: endereço HTTPS de download direto do arquivo
     Referencia_Voz_Frascolino_Translucido_PET_Globalpack.mp4 já autorizado.
     O arquivo não precisa ser publicado. Um URL assinado temporário serve se
     permanecer válido durante a execução. Não use página de visualização que exija
     login; não coloque o endereço em código, inputs ou comentários.
   - FRASCOLINO_ARCHIVE_PASSWORD: senha exclusiva e aleatória com pelo menos
     20 caracteres; guarde-a para abrir o pacote. Não reutilize credenciais pessoais.
2. Integre o PR com este workflow à branch principal.
3. Abra Actions > Jarvis - Frascolino PET (isolado) > Run workflow.
   Escolha mode=clone. mode=validate testa sem acessar qualquer referência.
4. Baixe o artefato Frascolino-PET-encrypted-<run_id> antes de expirar em um dia.
   Extraia o ZIP externo do Actions e abra Frascolino_PET_Globalpack_AES256.zip
   usando 7-Zip e a senha exclusiva. Salve o pacote em armazenamento privado durável.

Configurar secrets e acionar workflow_dispatch exige a interface do GitHub ou um
cliente autorizado com essas capacidades. O conector usado na implementação não
oferece escrita de secrets nem despacho de workflows. O PR dispara somente testes.

## Pacote de voz

O ZIP AES-256 inclui:
- o MP4 original preservado;
- referencia.wav, mono PCM16 16 kHz: início de até 12 segundos do original;
- Frascolino_Amostra_Teste.wav, mono PCM16 48 kHz;
- texto_teste.txt;
- profile.json com profile_id=frascolino_pet_globalpack e is_default=false;
- LEIA-ME.txt.

O modo reference_only não exige transcrição e não usa uma amostra sintetizada como
referência. Se o início do vídeo tiver silêncio, música ou outro falante, a referência
precisa ser revisada antes do uso; o teste técnico não separa fontes de áudio.
Não altera tom nem velocidade. Não treina um novo checkpoint: o perfil conserva a
referência e os parâmetros para condicionamento da voz em futuras gerações.
Não substitua default_voice.json pessoal por este profile.json.

## Testes e limites

Pull requests do mesmo repositório executam testes de sigilo de URLs, bloqueio de
origens locais, recusa de senha ausente e pacote criptografado verificável, além
dos testes da voz pessoal. Depois instalam as dependências fixadas e carregam
VoxCPM2 em CPU. Isso confirma instalação/carregamento, não semelhança vocal.

A síntese real só ocorre em workflow_dispatch com mode=clone e ambos os secrets.
Falha de download, decoder, memória, modelo, áudio ou criptografia encerra o job;
não há fallback para a voz pessoal nem para uma voz genérica.
O perfil registra sample_approval=pending_listening_review. As métricas técnicas
não confirmam transcrição correta nem semelhança; ouvir e comparar antes de usar.

Somente o ZIP criptografado é enviado como artefato. O repositório é público e
artefatos podem ser baixados por quem tenha acesso de leitura; a criptografia
protege os arquivos internos. Nomes de entradas ZIP não são confidenciais.
Referência, perfil e amostra em claro ficam apenas no diretório temporário da
execução e não são versionados, publicados nem cacheados.
A senha não está no ZIP; uma senha fraca permite ataques offline.

Código VoxCPM fixado: cce58a5b59303c9bd63d12f23afe6a49a4a80c59.
Pesos: openbmb/VoxCPM2, snapshot 32279effe8c19989596f05d353d1447f51d9e915.
O download de pesos é seguido de inferência local no runner, sem API de clonagem.
Runner padrão ubuntu-24.04; timeout 90 min; sem runner pago.
Não há promessa de velocidade, memória suficiente ou qualidade antes do teste real.
O artefato do Actions é temporário, não é backup permanente.

Se a CPU do runner não comportar a síntese, use este mesmo script em computador
local com RAM suficiente, Python 3.11, FFmpeg e as dependências fixadas. Preserve o
perfil em diretório privado separado. Não acione serviços de voz externos.

Fontes:
- https://github.com/OpenBMB/VoxCPM
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts
