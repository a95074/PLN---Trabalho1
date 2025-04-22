import re

file_covid = "diccionari-multilinguee-de-la-covid-19.xml"

with open(file_covid, "r", encoding="utf-8") as file:
    xml = file.read()

# 🔧 Limpeza inicial
xml = re.sub(r"</page>", "", xml)
xml = re.sub(r"<page[^>]*>", "", xml)
xml = re.sub(r"<fontspec[^>]*/>", "", xml)
xml = re.sub(r"\s*\n\s*", "", xml)

# 🔍 Identificar todos os conceitos (número e nome)
conceitos = re.findall(r'<text[^>]+font="11">(\d+)\s*</text>\s*<text[^>]+font="2[5,6]"><b>(.*?)</b></text>', xml)
conceitos.sort(key=lambda x: int(x[0]))

# 🔍 Regex para identificar blocos de texto por conceito
padrao_bloco = re.compile(
    r'<text[^>]+font="11">' + r'{}' + r'\s*</text>\s*<text[^>]+font="2[5-6]"><b>{}</b></text>(.*?)(?=<text[^>]+font="11">\d+\s*</text>|$)',
    re.DOTALL
)

resultados = []

for i, (num, nome) in enumerate(conceitos):
    padrao_conceito = padrao_bloco.pattern.format(re.escape(num), re.escape(nome))
    match = re.search(padrao_conceito, xml)
    
    if not match:
        print(f"[!] Bloco não encontrado para: {nome}")
        continue
    bloco = match.group(1)

    # Substantivo
    sub_match = re.search(r'<i>\s*n\s*m?\s*</i>', bloco)
    substantivo = sub_match.group(0).strip("<i> </i>") if sub_match else ""

    # Traduções
        # Traduções válidas (evita capturar 'n', 'n m', etc.)
    traducoes = re.findall(r'<i>([a-z\[\]\s]+)</i></text>\s*<text[^>]+font="11">(.*?)</text>',bloco)

    traducoes_formatadas = []
    for lang, termo in traducoes:
        lang = lang.strip()
        termo = termo.strip()
        # Ignorar se a "língua" for só 'n', 'n m', 'n f', etc.
        if not re.match(r'^n(\s+[mf])?$', lang):
            traducoes_formatadas.append(f"{lang}: {termo}")


    # Sigla
    sigla_match = re.search(r'sigla\s*</text>\s*<text[^>]+font="25"><b>(.*?)</b></text>', bloco)
    sigla = sigla_match.group(1).strip() if sigla_match else ""

    # Descrição (filtra número e siglas)
    descricoes = re.findall(r'<text[^>]+font="(?:11|27)">(.+?)</text>', bloco)
    descricoes_filtradas = []

    for d in descricoes:
        texto = d.strip()

        # Ignorar números, siglas curtas e nomes repetidos
        if re.fullmatch(r'[0-9,\s]+', texto):  # só números e vírgulas
            continue
        if texto.lower() == nome.lower():  # nome do conceito repetido
            continue
        if re.match(r'^[A-Z]{2,5}$', texto):  # siglas
            continue
        if texto.lower() in [t.split(": ")[-1].lower() for t in traducoes_formatadas]:  # está nas traduções
            continue
        if re.search(r'sigla|Nota:', texto, re.IGNORECASE):
            continue

        descricoes_filtradas.append(texto)

    descricao = " ".join(descricoes_filtradas)

    # Citação (nota explicativa, tipicamente com "Nota:")
    citacao_match = re.search(r'(Nota:.*?)(?=<text[^>]+font="11">|\Z)', bloco, re.DOTALL)
    if citacao_match:
        citacao_bruta = citacao_match.group(1)

        # Remove tags <text ...> e deixa só o texto plano
        citacao_limpa = re.sub(r'<[^>]+>', '', citacao_bruta).strip()
        citacao = re.sub(r'\s+', ' ', citacao_limpa)  # reduzir espaços múltiplos
    else:
        citacao = ""

    resultados.append({
        "Conceito": nome,
        "Substantivo": substantivo,
        "Traduções": traducoes_formatadas,
        "Sigla": sigla,
        "Descricao": descricao,
        "Citação": citacao
    })

# ✅ Mostrar resultados

for r in resultados:
    print("Conceito:", r["Conceito"])
    print("Substantivo:", r["Substantivo"])
    print("Traduções:", r["Traduções"])
    print("Sigla:", r["Sigla"])
    print("Descrição:", r["Descricao"])
    print("Citação:", r["Citação"])
    print("-" * 70)
    
    
# 🔄 Exportar para JSON  
import json
file_out="glossario_covid.json"
with open(file_out, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
print(f"Arquivo JSON exportado: {file_out}")