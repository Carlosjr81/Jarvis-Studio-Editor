# Operações LTX verificáveis

No momento da reconstrução, o conector expõe:
- ltx_connection_status: leitura de configuração; não confirma saldo ou autenticação.
- ltx_generate_video: geração paga, exige cost_approved=true após aprovação real do conteúdo/custo e request_key UUID; nunca transmitir API key.
- ltx_get_video_job: consultar job do próprio usuário, esperar ao menos cinco segundos entre consultas; ao concluir, baixar e salvar, sem repetir a geração.

Conferir os esquemas atuais antes de chamar. Os nomes/modelos/resoluções podem mudar; não inventar endpoint REST nem converter pedido “sem créditos” em autorização de custo. Se autenticação não estiver confirmada, relatar separadamente de configuração existente. Manter aprovação e ID de job durante retomadas.

Para consistência visual: usar a mesma referência aprovada, descrever pose/movimento/ambiente, preservar direção de luz e figurino; evitar movimentos extremos de pescoço/corpo. Prévia e render final precisam de QA. Um controle de custo não garante qualidade de geração.
