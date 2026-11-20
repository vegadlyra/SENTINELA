
import os, re, json
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

SENTINELA_SYSTEM = """És a SENTINELA, agente de auditoria técnica, controlo de qualidade, testes de software, segurança informática e validação independente de todo o vegadlyraOS. Comunicas em português e referes-te a ti própria no feminino. Auditas TODO o vegadlyraOS: ATLAS, Imhotep, Coder, Escritor, Analítico, Investigador, Gestor de campanhas, e qualquer outro projeto, agente, aplicação ou entrega do vegadlyraOS. Não és só do ATLAS. És do sistema inteiro. Não constróis, não alteras código de produção. Verificas de forma independente. Nunca aprovas sem evidências. Princípio: quem executa não é quem valida. Classificas: CRÍTICO, ALTO, MÉDIO, BAIXO, INFORMATIVO. Aprovação: APROVADA, APROVADA COM RESERVAS, REPROVADA, NÃO VALIDADA."""

HTML = r"""<!doctype html>
<html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SENTINELA do vegadlyraOS - Auditoria</title>
<style>body{font-family:system-ui,Arial,sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#f6f5f0;color:#222}h1{font-size:28px} .card{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin:16px 0} textarea,input{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:15px} button{background:#111;color:white;padding:12px 18px;border:0;border-radius:8px;font-size:16px;cursor:pointer} .badge{display:inline-block;padding:6px 10px;border-radius:20px;font-weight:700} .red{background:#ffe0e0}.green{background:#d9f5d9}.yellow{background:#fff3c4}.muted{color:#666;font-size:14px} pre{white-space:pre-wrap;background:#fafafa;padding:12px;border-radius:8px}</style>
</head><body>
<h1>🛡️ SENTINELA do vegadlyraOS</h1><p>Auditora independente de TODO o vegadlyraOS. Não é só do ATLAS. É do sistema inteiro. Não constrói. Só audita e apresenta evidências.</p>
<p class="muted">Versão Render grátis. Sem cartão. Se adormecer após 15 min sem uso, volta a abrir que ela acorda.</p>
<div class="card"><h2>1. O que foi pedido?</h2><form method="post" action="/auditar">
<label><b>Qual é a parte do vegadlyraOS?</b></label><select name="area" style="width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:15px"><option>ATLAS</option><option>Imhotep</option><option>Coder</option><option>Escritor / Revisor</option><option>Analítico</option><option>Investigador</option><option>Gestor de campanhas</option><option>Outro projeto do vegadlyraOS</option></select><br><br><textarea name="pedido" rows="4" placeholder="Ex: Criar uma funcionalidade no ATLAS, ou um texto, ou uma campanha..." required></textarea>
<h2>2. O que o Coder entregou?</h2><textarea name="entrega" rows="8" placeholder="Cola aqui o que o Coder te entregou: texto, código, link, ficheiro..." required></textarea>
<br><br><button type="submit">Auditar com a SENTINELA</button></form></div>
{% if relatorio %}<div class="card"><h2>Relatório da SENTINELA</h2>
<p><b>Data:</b> {{relatorio.data}} | <b>Versão:</b> {{relatorio.versao}}</p>
<p><b>Estado:</b> <span class="badge {{relatorio.cor}}">{{relatorio.estado}}</span> | <b>Gravidade maior:</b> {{relatorio.gravidade}}</p>
<h3>Problemas encontrados</h3><ul>{% for p in relatorio.problemas %}<li><b>{{p.titulo}}</b> - {{p.desc}} ({{p.gravidade}})</li>{% endfor %}</ul>
<h3>Verificações</h3><ul>{% for v in relatorio.verificacoes %}<li>{{v}}</li>{% endfor %}</ul>
<h3>Recomendações para o Coder</h3><pre>{{relatorio.recomendacoes}}</pre>
<h3>Evidências</h3><pre>{{relatorio.evidencias}}</pre>
<p class="muted">Princípio: quem executa não é quem valida. A SENTINELA não aprova sem evidências.</p>
</div>{% endif %}
<div class="card"><h3>Como usar no Render</h3><p>1. Cria conta grátis em render.com com email.<br>2. Clica New + → Web Service → Build from GitHub ou Upload.<br>3. Carrega esta pasta.<br>4. Render detecta o render.yaml e põe online. Sem cartão.</p></div>
</body></html>
"""

def auditar_local(pedido, entrega):
    problemas=[]
    verificacoes=[]
    texto = (pedido + " " + entrega).lower()
    entrega_lower = entrega.lower()
    # checks
    if "teste" not in entrega_lower and "test" not in entrega_lower:
        problemas.append({"titulo":"Sem testes demonstrados","desc":"Não há evidência de testes executados. Não posso validar.","gravidade":"ALTO"})
    else:
        verificacoes.append("Encontrei menção a testes, mas preciso de ver a execução para validar.")
    if "simulad" in entrega_lower or "exemplo" in entrega_lower or "fictício" in entrega_lower or "ficticio" in entrega_lower:
        problemas.append({"titulo":"Possível dado simulado","desc":"Aparecem palavras como simulado ou exemplo. Dados de exemplo não podem ser apresentados como reais.","gravidade":"ALTO"})
    if "http" not in entrega_lower and "link" not in entrega_lower and "fonte" not in entrega_lower:
        problemas.append({"titulo":"Sem fonte verificável","desc":"Não encontrei link ou fonte. Sem fonte, não posso confirmar proveniência.","gravidade":"MÉDIO"})
    else:
        verificacoes.append("Encontrei menção a fonte ou link, verificar se abre de verdade.")
    if len(entrega.strip()) < 200:
        problemas.append({"titulo":"Entrega muito curta","desc":"Entrega curta demais para ser uma funcionalidade completa.","gravidade":"MÉDIO"})
    if "pronto" in entrega_lower and "falta" not in entrega_lower:
        verificacoes.append("Afirma estar pronto, verificar se corresponde ao que foi pedido.")
    if not problemas:
        estado="APROVADA COM RESERVAS"
        cor="yellow"
        grav="BAIXO"
    elif any(p["gravidade"]=="ALTO" for p in problemas):
        estado="REPROVADA"
        cor="red"
        grav="ALTO"
    else:
        estado="APROVADA COM RESERVAS"
        cor="yellow"
        grav="MÉDIO"
    # Try Groq if key exists
    groq_key = os.environ.get("GROQ_API_KEY")
    recomend = "1. Mostrar execução real dos testes.\n2. Mostrar links directos das fontes que abrem.\n3. Separar dados reais de dados de exemplo.\n4. Dizer o que falta, sem dizer que está pronto se não está."
    if groq_key:
        try:
            import urllib.request, json as js
            payload = {"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":SENTINELA_SYSTEM},{"role":"user","content":f"Pedido: {pedido}\nEntrega: {entrega}\nFaz relatório curto em português, com estado APROVADA, APROVADA COM RESERVAS, REPROVADA ou NÃO VALIDADA, problemas, gravidade e recomendações."}],"temperature":0.2,"max_tokens":1200}
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=js.dumps(payload).encode(), headers={"Authorization":f"Bearer {groq_key}","Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = js.loads(r.read().decode())
                txt = data["choices"][0]["message"]["content"]
                recomend = txt
                verificacoes.append("Auditoria com cérebro Groq (grátis) activada.")
        except Exception as e:
            verificacoes.append(f"Cérebro Groq não disponível ({e}), usei auditoria local.")
    return {"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "versao":"v2-vegadlyraOS", "estado":estado, "cor":cor, "gravidade":grav, "problemas":problemas if problemas else [{"titulo":"Nenhum problema crítico detectado nesta verificação rápida","desc":"Isto não é aprovação total. É preciso ver código e testes a correr.","gravidade":"INFORMATIVO"}], "verificacoes":verificacoes, "recomendacoes":recomend, "evidencias": f"Pedido recebido: {pedido[:300]}\n\nEntrega recebida (primeiros 600 caracteres):\n{entrega[:600]}"}

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, relatorio=None)

@app.route("/auditar", methods=["POST"])
def auditar():
    pedido = request.form.get("area","vegadlyraOS") + " | " + request.form.get("pedido","")
    entrega = request.form.get("entrega","")
    rel = auditar_local(pedido, entrega)
    return render_template_string(HTML, relatorio=rel)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","agente":"SENTINELA","versao":"v2-vegadlyraOS"})

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
