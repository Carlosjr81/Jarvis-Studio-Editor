---
name: jarvis-ltx-mobile-2
description: Preparar prompts e acompanhar geração de vídeos LTX no fluxo móvel Jarvis, preservando continuidade visual e custo autorizado. Usar para Jarvis LTX Mobile 2 ou geração LTX pelo celular.
---

# Jarvis LTX Mobile 2

Ler [fluxo](references/ltx-workflow.md), [origem](references/origin.md) e [operação](references/operation.md). Recuperar o acesso ao fluxo, sem duplicar o Site existente nem prometer geração sem custos.

1. Identificar roteiro, duração, proporção, referência visual, continuidade e áudio desejado. Preparar prompt concreto preservando rosto, roupa, logo e anatomia.
2. Conferir o conector LTX disponível e seu esquema atual. Usar status de conexão apenas como leitura: configured não confirma autenticação, saldo ou custo.
3. Priorizar alternativa local quando o pedido exigir zero créditos. Não chamar geração paga para testar instalação da habilidade.
4. Para geração LTX paga, exigir aprovação vigente do conteúdo e do custo atual. Não reutilizar saldo histórico como saldo atual nem presumir preço.
5. Usar request_key UUID único para cada intenção nova e manter a mesma chave em retentativas do mesmo pedido. Reconciliar job existente antes de gerar de novo.
6. Acompanhar o job próprio no intervalo permitido, baixar e salvar o vídeo concluído imediatamente. Não confundir job criado com vídeo entregue.
7. Conferir rosto, boca, cabeça, membros e continuidade; não entregar deformação rejeitada como padrão. Integrar vídeo, capa e voz aprovada ao Instagram 2 quando solicitado.

O painel existente é https://jarvis-ltx-mobile.carlos-jr-81.chatgpt.site. Operações do Site devem usar a ferramenta Sites com sua identidade real. Não pedir chave API no chat nem gravá-la na habilidade. Não alegar que renomear o atalho valida autenticação externa.
