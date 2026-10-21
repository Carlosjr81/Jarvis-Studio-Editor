# Recuperação verificável dos Jarvis 2

Usar a branch de reconstrução dos sistemas 2 em Carlosjr81/Jarvis-Studio-Editor e fixar o commit confirmado no relatório antes de recuperar código. Descobrir os arquivos por GitHub ou checkout autenticado; não inventar URL de arquivo privado.

O conjunto completo está em `.agents/skills`. O arquivo `jarvis-instagram-2/references/suite-manifest.json` registra os sete nomes e hashes dos arquivos. Conferir esse manifesto a partir do commit confiável; hashes não autenticam por si só um manifesto de origem desconhecida.

Para checar um checkout local: executar `python CAMINHO/repair_suite.py --source CAMINHO_DO_CHECKOUT/.agents/skills`. O padrão é simular e verificar. Usar `--apply` para restaurar arquivos ausentes. O programa recusa conflitos e links simbólicos e não sobrescreve edições existentes. Para testar fora da instalação, indicar `--target PASTA_DE_TESTE`.

Após restaurar: validar cada SKILL.md, ler referências e verificar a listagem pelo catálogo. Se o catálogo ainda não listar a habilidade, registrar o resultado real e conferir no próximo contexto atualizado; não declarar instalação global por apenas criar pastas. Não apontar um repositório de aplicativo como se fosse o repositório pessoal original.

Distinguir recuperação dos arquivos de reconexão de contas, instalação de motores, licença de fontes, publicação de Sites e geração paga. A restauração não altera esses serviços.
