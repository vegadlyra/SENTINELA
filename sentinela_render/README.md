# SENTINELA no Render - Guia simples, sem cartão, sem Paris, sem códigos

O que é isto?
É a SENTINELA a viver num computador remoto grátis no Render. Ela não constrói. Ela audita.
Quando o Coder te entrega algo, tu colas aqui e ela faz relatório.

O que precisas?
- Um email. Só isso. Sem cartão. Sem dinheiro.
- O ficheiro SENTINELA.md que já tens, já está dentro da app.

Passos no Render, um a um:
1. Vai a render.com e clica Sign Up. Usa email e palavra passe.
2. Depois de entrares, clica no botão New + em cima.
3. Clica Web Service.
4. Escolhe Build and deploy from a Git repository ou Upload files. Se não tens GitHub, escolhe Upload e carrega esta pasta toda.
5. O Render vai ler sozinho o ficheiro render.yaml. Não precisas de escolher região como Paris. Ele trata disso.
6. Em Plan, confirma que está Free.
7. Clica Create Web Service. Espera 2 a 4 minutos. Ele vai dar-te um link, tipo https://sentinela-xxxx.onrender.com
8. Abre o link. Se aparecer a página da SENTINELA, ela está viva.

O que fazes depois?
- Se a página adormecer depois de 15 minutos sem uso, é normal no grátis. Volta a abrir o link que ela acorda em 20 a 30 segundos.
- Para ela ter cérebro mais forte e grátis, podes depois pôr uma chave grátis do Groq:
  Vai a groq.com, cria conta grátis, copia a chave, no Render vai a Environment, adiciona GROQ_API_KEY com a chave, e faz Redeploy. Sem isto, ela já funciona com auditoria local.

O que a SENTINELA faz aqui?
- Recebe o que foi pedido e o que o Coder entregou.
- Verifica se há testes, fontes, links, dados reais ou simulados.
- Dá estado: APROVADA, APROVADA COM RESERVAS, REPROVADA, NÃO VALIDADA.
- Dá lista de problemas com gravidade e recomendações para o Coder.
- Nunca aprova sem evidências.

O que ela NÃO faz?
- Não altera código.
- Não trabalha à noite sozinha. Só trabalha quando tu falas com ela.
- Não inventa testes que não viu.

Se algo correr mal no Render, copia a mensagem de erro e cola aqui que eu traduzo.
