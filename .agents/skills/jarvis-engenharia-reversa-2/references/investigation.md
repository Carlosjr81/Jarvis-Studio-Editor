# Procedimento de investigação

## Evidência

Para cada achado, registrar origem, caminho/linha ou endpoint/documentação, comportamento observado, confiança e teste capaz de confirmá-lo. Não tratar nome de função como prova de funcionamento. Ler o código relevante após localizar símbolos com rg.

## Reconstruir mecanismo

Mapear entrada → transformação → estado → saída; identificar cliente/servidor, biblioteca, permissões, formatos e modo offline. Em sistemas existentes, localizar ponto de extensão, testes, falhas e contrato externo. Preferir integração pequena e revisável.

## Viabilidade

Confrontar requisitos com o aparelho, navegador e API reais. Indicar dependência confirmada e componente ausente. Para Ray-Ban/Eyes Scan ou chamadas, usar documentação atual e testes no dispositivo antes de alegar conexão completa. Não apresentar um APK de simulação como telefonia real.

## Construir e testar

Preservar o projeto e criar mudanças isoladas. Verificar o fluxo que demonstra o requisito, inclusive falha previsível relevante. Distinguir compilação, teste automatizado, publicação e uso real. Não prometer “sem custos” quando o fluxo necessita GPU/serviço pago não autorizado.

## Contingência REA

O relato histórico documenta falha de REA 6.4.0 com Node e /proc e sucesso de análise estática com versão 4.1.0 em dois arquivos. Isso é histórico de teste, não disponibilidade atual. Identificar o projeto oficial e fixar revisão antes de baixar. Se isso não for possível, usar source_audit.py, ler os arquivos e manter a conclusão limitada à evidência coletada.
