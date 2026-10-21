---
name: jarvis-engenharia-reversa-2
description: Investigar como aplicativos, sites e funcionalidades funcionam e desenvolver alternativas verificáveis. Usar para Jarvis Engenharia Reversa 2, análise de código, investigação REA ou integração de uma função em outro projeto.
---

# Jarvis Engenharia Reversa 2

Ler [investigação](references/investigation.md), [origem](references/origin.md) e [operação](references/operation.md). Executar investigação, explicação simples, evidências, construção e testes, conforme o objetivo autorizado.

1. Resolver aplicativo/site, funcionalidade e projeto de destino a partir do contexto. Perguntar apenas o elemento indispensável ausente; não interromper trabalho independente.
2. Inspecionar código e documentação acessíveis antes de atribuir capacidades. Usar ferramentas de pesquisa para informações públicas atuais, conectores para repositórios autorizados e acesso de arquivos para materiais privados.
3. Inventariar entradas, processamento, saídas, estado, dependências, interfaces e limites observados. Registrar origem e trecho que sustenta cada conclusão.
4. Para análise estática local, executar `python scripts/source_audit.py PASTA --output RELATORIO.json`. O script não executa o aplicativo analisado e suas regex são heurísticas, não análise semântica completa.
5. Explicar em português simples o mecanismo, separar observado/inferido/proposto e descrever o caminho viável para integrar.
6. Implementar a alternativa no projeto existente quando solicitado, preservando dados e funcionalidades. Executar os testes adequados e entregar mudanças concretas. Não declarar integração concluída só por escrever instruções.
7. Se uma dependência falhar, registrar erro e tentar alternativa comprovável. Não depender de RuFlo, acesso /proc ou um instalador desconhecido para toda análise.

O histórico registra REA 6.4.0 e fallback 4.1.0, mas não recuperou seu repositório/comandos oficiais. Verificar identidade e fonte antes de instalar ou invocar um pacote chamado REA. Usar o analisador próprio desta pasta como contingência local identificada; não chamá-lo de REA oficial.

Não executar código de terceiros apenas para inspecioná-lo. Respeitar acessos existentes; não contornar autenticação nem copiar segredos. Em telefonia, câmera, dispositivos e APIs, diferenciar protótipo, simulação e fluxo real em hardware. Ausência de API ou permissão não se resolve renomeando uma habilidade.
