import os, re, json
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

SENTINELA_SYSTEM = """Es a SENTINELA v3, agente de auditoria tecnica, controlo de qualidade, testes de software, seguranca informatica e validacao independente de todo o vegadlyraOS. Comunicas em portugues e referes-te a ti propria no feminino. Auditas TODO o vegadlyraOS: ATLAS, Imhotep, Coder, Escritor, Analitico, Investigador, Gestor de campanhas, e qualquer outro projeto. Nao es so do ATLAS. Nao constrois, nao alteras codigo de producao. Verificas de forma independente, ponto a ponto. Nunca aprovas sem evidencias. Principio: quem executa nao e quem valida. Classificas: CRITICO, ALTO, MEDIO, BAIXO, INFORMATIVO. Aprovacao: APROVADA, APROVADA COM RESERVAS, REPROVADA, NAO VALIDADA."""

HTML = r"""<!doctype html>
<html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SENTINELA do vegadlyraOS - Auditoria</title>
<style>body{font-family:system-ui,Arial,sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#f6f5f0;color:#222}h1{font-size:28px} .card{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,.06);margin:16px 0} textarea,input{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:15px} button{background:#111;color:white;padding:12px 18px;border:0;border-radius:8px;font-size:16px;cursor:pointer} .badge{display:inline-block;padding:6px 10px;border-radius:20px;font-weight:700} .red{background:#ffe0e0}.green{background:#d9f5d9}.yellow{background:#fff3c4}.muted{color:#666;font-size:14px} pre{white-space:pre-wrap;background:#fafafa;padding:12px;border-radius:8px} table{width:100%;border-collapse:collapse} td,th{border:1px solid #ddd;padding:8px;text-align:left;font-size:14px} th{background:#f0f0f0}</style>
</head><body>
<h1>🛡 SENTINELA do vegadlyraOS</h1><p>Auditora independente de TODO o vegadlyraOS. Nao e so do ATLAS. E do sistema inteiro. Nao constroi. So audita e apresenta evidencias, ponto a ponto.</p>
<p class="muted">Versao Render gratis. Sem cartao. Se adormecer apos 15 min sem uso, volta a abrir que ela acorda.</p>
<div class="card"><h2>1. O que foi pedido?</h2><form method="post" action="/auditar">
<label><b>Qual e a parte do vegadlyraOS?</b></label><select name="area" style="width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:15px"><option>ATLAS</option><option>Imhotep</option><option>Coder</option><option>Escritor / Revisor</option><option>Analitico</option><option>Investigador</option><option>Gestor de campanhas</option><option>Outro projeto do vegadlyraOS</option></select><br><br><textarea name="pedido" rows="4" placeholder="Ex: Criar uma funcionalidade no ATLAS, ou um texto, ou uma campanha..." required></textarea>
<h2>2. O que o Coder entregou?</h2><textarea name="entrega" rows="8" placeholder="Cola aqui o que o Coder te entregou: texto, codigo, link, ficheiro, log de testes..." required></textarea>
<br><br><button type="submit">Auditar com a SENTINELA</button></form></div>
{% if relatorio %}<div class="card"><h2>Relatorio da SENTINELA</h2>
<p><b>Data:</b> {{relatorio.data}} | <b>Versao:</b> {{relatorio.versao}}</p>
<p><b>Estado:</b> <span class="badge {{relatorio.cor}}">{{relatorio.estado}}</span> | <b>Gravidade maior:</b> {{relatorio.gravidade}}</p>
<h3>Auditoria ponto a ponto</h3>
<table><tr><th>Ponto</th><th>Estado</th><th>Evidencia</th></tr>{% for item in relatorio.ponto_a_ponto %}<tr><td><b>{{item.numero}}.</b> {{item.texto}}</td><td><b>{{item.estado}}</b></td><td>{{item.evidencia}}</td></tr>{% endfor %}</table>
<p class="muted">{{relatorio.numeros_info}}</p>
<h3>Problemas encontrados</h3><ul>{% for p in relatorio.problemas %}<li><b>{{p.titulo}}</b> - {{p.desc}} ({{p.gravidade}})</li>{% endfor %}</ul>
<h3>Verificacoes</h3><ul>{% for v in relatorio.verificacoes %}<li>{{v}}</li>{% endfor %}</ul>
<h3>Recomendacoes para o Coder</h3><pre>{{relatorio.recomendacoes}}</pre>
<h3>Evidencias</h3><pre>{{relatorio.evidencias}}</pre>
<p class="muted">Principio: quem executa nao e quem valida. A SENTINELA nao aprova sem evidencias.</p>
</div>{% endif %}
<div class="card"><h3>Como usar no Render</h3><p>1. Cria conta gratis em render.com com email.<br>2. Clica New + → Web Service → Build from GitHub ou Upload.<br>3. Carrega esta pasta.<br>4. Render detecta o render.yaml e poe online. Sem cartao.</p></div>
</body></html>
"""

STOPWORDS = set(["para","com","que","sao","uma","umas","uns","dos","das","pelo","pela","pelos","pelas","esta","este","isto","isso","ainda","como","mais","mas","por","sem","quando","onde","cada","sobre","entre","depois","antes","entao","pois"])

def extrair_pontos(pedido_texto):
    pontos = []
    for linha in pedido_texto.splitlines():
        m = re.match(r'\s*\d+[\.\)]\s*(.+)', linha)
        if m:
            t = m.group(1).strip()
            if len(t) > 5:
                pontos.append(t)
    if not pontos:
        for linha in pedido_texto.splitlines():
            t = linha.strip()
            if len(t) > 20 and "ATLAS" not in t[:10]:
                pontos.append(t)
    return pontos

def auditar_local(pedido, entrega):
    problemas = []
    verificacoes = []
    pedido_lower = pedido.lower()
    entrega_lower = entrega.lower()
    entrega_strip = entrega.strip()
    pontos = extrair_pontos(pedido)
    ponto_a_ponto = []
    for idx, ponto in enumerate(pontos, start=1):
        ponto_lower = ponto.lower()
        numeros_ponto = re.findall(r'\b\d+(?:[.,]\d+)?\b', ponto)
        palavras = [w for w in re.findall(r'[a-zà-ú]{4,}', ponto_lower) if w not in STOPWORDS]
        numeros_ok = True
        if numeros_ponto:
            numeros_ok = all(n in entrega for n in numeros_ponto)
        palavras_encontradas = [w for w in palavras if w in entrega_lower]
        if numeros_ponto and numeros_ok:
            estado_ponto = "PASSOU"
            evidencia = f"Numeros {', '.join(numeros_ponto)} encontrados na entrega."
        elif numeros_ponto and not numeros_ok:
            estado_ponto = "NAO PROVADO"
            falta = [n for n in numeros_ponto if n not in entrega]
            evidencia = f"Faltam numeros {', '.join(falta)} na entrega."
        elif len(palavras_encontradas) >= 2:
            estado_ponto = "PASSOU"
            evidencia = f"Palavras encontradas: {', '.join(palavras_encontradas[:4])}."
        elif len(palavras_encontradas) == 1:
            estado_ponto = "NAO PROVADO"
            evidencia = f"So encontrei: {palavras_encontradas[0]}. Falta provar resto."
        else:
            estado_ponto = "NAO PROVADO"
            evidencia = "Nao encontrei palavras chave deste ponto na entrega."
        if palavras_encontradas:
            kw = palavras_encontradas[0]
            pos = entrega_lower.find(kw)
            if pos >= 0:
                evidencia = entrega[max(0,pos-60):pos+120].replace("\n"," ") + " [...]"
        ponto_a_ponto.append({"numero": idx, "texto": ponto[:140], "estado": estado_ponto, "evidencia": evidencia})
    numeros_pedido = sorted(set(re.findall(r'\b\d+(?:[.,]\d+)?\b', pedido)))
    numeros_encontrados = [n for n in numeros_pedido if n in entrega]
    numeros_falta = [n for n in numeros_pedido if n not in entrega]
    numeros_info = f"Numeros do pedido encontrados na entrega: {', '.join(numeros_encontrados) if numeros_encontrados else 'nenhum'} | Em falta: {', '.join(numeros_falta) if numeros_falta else 'nenhum'}"
    termos_teste_forte = ["teste executado", "testes executados", "log de testes", "clicado e funcionou", "clicado, funcionou", "teste: passou", "25/25", "testes: "]
    termos_teste_fraco = ["teste", "test", "testado", "clicado", "clique", "verificado", "print", "screenshot", "captura", "tentativas", "ver ficha", "sacar selecao", "sacar seleção"]
    tem_teste_forte = any(t in entrega_lower for t in termos_teste_forte)
    tem_teste_fraco = any(t in entrega_lower for t in termos_teste_fraco)
    if tem_teste_forte:
        verificacoes.append("Encontrei prova forte de teste executado, log ou clique com resultado.")
    elif tem_teste_fraco:
        verificacoes.append("Encontrei prova fraca de teste manual, print, clique ou tentativas, mas falta log de teste executado passo a passo.")
        problemas.append({"titulo": "Teste manual sem log completo", "desc": "Ha indicios de teste manual, mas falta log passo a passo: o que foi clicado, o que aconteceu, e o ficheiro criado.", "gravidade": "MEDIO"})
    else:
        problemas.append({"titulo": "Sem testes demonstrados", "desc": "Nao ha evidencia de testes executados, nem log, nem clique, nem print descrito. Nao posso validar.", "gravidade": "ALTO"})
    negacao_exemplo = re.search(r'(sem|não|nao|nenhum|nunca|não é|nao e)\b[^.]{0,40}\b(exemplo|simulado|simulada|fictício|ficticio)', entrega_lower)
    negacao_inventou = "nao inventou" in entrega_lower or "não inventou" in entrega_lower or "nao inventa" in entrega_lower or "não inventa" in entrega_lower
    if negacao_exemplo or negacao_inventou:
        verificacoes.append("Menciona 'sem dados de exemplo' ou 'nao inventou', nao e dado simulado, e afirmacao de dados reais. Nao conto como problema.")
    elif "simulad" in entrega_lower or "fictício" in entrega_lower or "ficticio" in entrega_lower:
        problemas.append({"titulo": "Possivel dado simulado", "desc": "Aparecem palavras como simulado ou ficticio sem negacao. Dados de exemplo nao podem ser apresentados como reais.", "gravidade": "ALTO"})
    elif "exemplo" in entrega_lower:
        problemas.append({"titulo": "Possivel dado de exemplo", "desc": "Aparece a palavra exemplo sem dizer que e sem exemplo. Confirmar se e real ou exemplo.", "gravidade": "MEDIO"})
    if "http" not in entrega_lower and "link" not in entrega_lower and "fonte" not in entrega_lower and "dados.gov.pt" not in entrega_lower:
        problemas.append({"titulo": "Sem fonte verificavel", "desc": "Nao encontrei link ou fonte. Sem fonte, nao posso confirmar proveniencia.", "gravidade": "MEDIO"})
    else:
        verificacoes.append("Encontrei mencao a fonte ou link, verificar se abre de verdade.")
    if "dados.gov.pt" in entrega_lower:
        verificacoes.append("Fonte dados.gov.pt mencionada, e fonte real oficial.")
    if "duplicad" in pedido_lower and "duplicad" in entrega_lower:
        if "avis" in entrega_lower or "pergunt" in entrega_lower or "verificar" in entrega_lower:
            verificacoes.append("Duplicado mencionado com aviso ou pedido de verificacao, preciso confirmar se o aviso funcionou ao clicar.")
        else:
            problemas.append({"titulo": "Duplicado sem prova de aviso", "desc": "Ha duplicado mencionado mas sem prova de que o ATLAS avisou com hora e perguntou antes.", "gravidade": "MEDIO"})
    if len(entrega_strip) < 200:
        problemas.append({"titulo": "Entrega muito curta", "desc": "Entrega curta demais para ser uma funcionalidade completa.", "gravidade": "MEDIO"})
    if "pronto" in entrega_lower and "falta" not in entrega_lower:
        verificacoes.append("Afirma estar pronto, verificar se corresponde ao que foi pedido.")
    tem_alto = any(p["gravidade"] == "ALTO" for p in problemas)
    todos_passaram = ponto_a_ponto and all(p["estado"] == "PASSOU" for p in ponto_a_ponto)
    if tem_alto:
        estado, cor, grav = "REPROVADA", "red", "ALTO"
    elif todos_passaram and tem_teste_forte:
        estado, cor, grav = "APROVADA", "green", "BAIXO"
    elif todos_passaram and tem_teste_fraco:
        estado, cor, grav = "APROVADA COM RESERVAS", "yellow", "BAIXO"
    elif ponto_a_ponto and any(p["estado"] == "NAO PROVADO" for p in ponto_a_ponto):
        estado, cor, grav = "APROVADA COM RESERVAS", "yellow", "MEDIO"
    else:
        estado, cor, grav = "APROVADA COM RESERVAS", "yellow", "BAIXO"
    linhas_rec = []
    for p in ponto_a_ponto:
        if p["estado"] != "PASSOU":
            linhas_rec.append(f"Provar ponto {p['numero']}: {p['texto'][:90]} - mostrar print ou log do clique e o resultado.")
    linhas_rec.append("1. Mostrar log de testes passo a passo: o que foi clicado, o que aconteceu.")
    linhas_rec.append("2. Mostrar links directos das fontes que abrem, ex: dados.gov.pt.")
    linhas_rec.append("3. Se diz sem dados de exemplo, manter essa frase, nao contar como problema.")
    linhas_rec.append("4. Dizer o que falta, sem dizer que esta pronto se nao esta.")
    recomend = "\n".join(linhas_rec)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            import urllib.request, json as js
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": SENTINELA_SYSTEM}, {"role": "user", "content": f"Pedido: {pedido}\nEntrega: {entrega}\nFaz relatorio curto em portugues, ponto a ponto, com estado e recomendacoes."}], "temperature": 0.2, "max_tokens": 1200}
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=js.dumps(payload).encode(), headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = js.loads(r.read().decode())
                txt = data["choices"][0]["message"]["content"]
                recomend = recomend + "\n\n--- Parecer Groq ---\n" + txt
                verificacoes.append("Auditoria com cerebro Groq (gratis) activada.")
        except Exception as e:
            verificacoes.append(f"Cerebro Groq nao disponivel ({e}), usei auditoria local v3.")
    evidencias = f"Pedido recebido (completo):\n{pedido[:2000]}\n\nEntrega recebida (primeiros 6000 caracteres):\n{entrega[:6000]}\n\n{numeros_info}"
    return {"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "versao": "v3-vegadlyraOS", "estado": estado, "cor": cor, "gravidade": grav, "problemas": problemas if problemas else [{"titulo": "Nenhum problema critico detectado nesta verificacao", "desc": "Isto nao e aprovacao total. E preciso ver codigo e testes a correr.", "gravidade": "INFORMATIVO"}], "verificacoes": verificacoes, "recomendacoes": recomend, "evidencias": evidencias, "ponto_a_ponto": ponto_a_ponto if ponto_a_ponto else [{"numero": 1, "texto": "Pedido sem pontos numerados", "estado": "NAO PROVADO", "evidencia": "Escreve o pedido com 1. 2. 3. para auditar ponto a ponto."}], "numeros_info": numeros_info}

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, relatorio=None)

@app.route("/auditar", methods=["POST"])
def auditar():
    pedido = request.form.get("area", "vegadlyraOS") + " | " + request.form.get("pedido", "")
    entrega = request.form.get("entrega", "")
    rel = auditar_local(pedido, entrega)
    return render_template_string(HTML, relatorio=rel)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agente": "SENTINELA", "versao": "v3-vegadlyraOS"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
