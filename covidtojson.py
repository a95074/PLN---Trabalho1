import re
import json
import unicodedata

filename = "diccionari-multilinguee-de-la-covid-19-simplificado1.xml"
with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()

# Limpezas
texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="12"><i>CAS </i></text>*\n?', '', texto)
texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="\d+">\s*\b(\d+(?:-+\d+)+\b)\s*</text>*\n?', '', texto)

#foi necessário implemenetar esta funçao para depois ao ordenar conceitos com ou sem siglas os acentos nao interfiram
def remove_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

#padrao que encontra os termos e as suas siglas associadas
padrao_siglas = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'<text[^>]+font="11">\s*sigla\s*</text>\s*'
    r'(?P<siglas>(?:<text[^>]+font="25"><b>.*?</b></text>\s*)+?)'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)', #excluido
    re.DOTALL
)

# Padrão para todos os conceitos sem siglas
padrao_conceitos_validos = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',
    re.DOTALL
)

# Padrão para traduções
padrao_traducao = re.compile(
    r'<text[^>]+font="12"><i>\s*(?P<lang>[a-z]{2}(?:\s*\[.*?\])?)\s*</i></text>\s*'
    r'<text[^>]+font="\d+">(?P<traducao>.*?)</text>',
    re.DOTALL
)

siglas_set = set()
termos_siglas = []

for match in padrao_siglas.finditer(texto):
    termo = match.group("termo").strip()
    siglas_bruto = match.group("siglas")
    siglas = re.findall(r'<b>(.*?)</b>', siglas_bruto)
    siglas = [s.strip() for s in siglas if s.strip()]
    termos_siglas.append({
        "termo": termo,
        "siglas": siglas,
        "traducoes": {}  # Se quiseres adicionar traduções aqui depois
    })
    siglas_set.update(s.lower() for s in siglas)  

#extrair todos os conceitos válidos e ignorar os que são apenas siglas
conceitos_finais = []

for match in padrao_conceitos_validos.finditer(texto):
    termo = match.group("termo").strip()
    if termo.lower() not in siglas_set:
        inicio_trad = match.end()
        proximo_texto = texto[inicio_trad:]

        trad = {}
        for t in padrao_traducao.finditer(proximo_texto):
            lang = t.group("lang").strip()
            traducao = t.group("traducao").strip()

            if re.search(r'<text[^>]+font="25"><b>', traducao):
                break  # nova entrada começa, parar

            trad[lang] = traducao

        conceitos_finais.append({
            "termo": termo,
            "siglas": [],
            "traducoes": trad
        })

# Combinar os dois
todos_termos = termos_siglas + conceitos_finais
todos_termos.sort(key=lambda x: remove_acentos(x["termo"]))

with open("termos_oc.json", "w", encoding="utf-8") as f:
    json.dump(todos_termos, f, ensure_ascii=False, indent=2)

with open("teste.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)
