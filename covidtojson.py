import re
import json


filename = "diccionari-multilinguee-de-la-covid-19-simplificado1.xml"
with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()

texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="12"><i>CAS </i></text>*\n?', '', texto)

texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="\d+">\s*\b(\d+(?:-+\d+)+\b)\s*</text>*\n?', '', texto)

#padrao que encontra os termos e as suas siglas associadas

padrao_siglas = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'           
    r'<text[^>]+font="11">\s*sigla\s*</text>\s*'                     
    r'(?P<siglas>(?:<text[^>]+font="25"><b>.*?</b></text>\s*)+?)'    
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',                      
    re.DOTALL
)

#padrao que encontra os conceitos sem siglas
padrao_conceitos_validos = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',
    re.DOTALL
)

siglas_set = set()
conceitos_finais = []

for match in padrao_conceitos_validos.finditer(texto):
    termo = match.group("termo").strip()
    if termo not in siglas_set:
        conceitos_finais.append(termo)

# Mostrar ou guardar os conceitos
for c in conceitos_finais:
    print(c)

termos_siglas = []

for match in padrao_siglas.finditer(texto):
    termo = match.group("termo").strip()
    siglas_bruto = match.group("siglas")
    siglas = re.findall(r'<b>(.*?)</b>', siglas_bruto)
    siglas = [s.strip() for s in siglas if s.strip()]

    if siglas:
        termos_siglas.append({
            "termo": termo,
            "siglas": siglas
        })

# Guardar resultado em JSON
with open("termos_oc.json", "w", encoding="utf-8") as f:
    json.dump(termos_siglas, f, ensure_ascii=False, indent=2)


# Padrão mais flexível (ignora atributos específicos e espaçamento)
#pattern = re.compile(
    #r'<text[^>]+font="25"><b>([^<]+)</b>\s*</text>\s*'
    #r'<text[^>]+><i>\s*oc\s*</i>',
    #re.DOTALL | re.IGNORECASE
#)

# Verificação de debug
#test_matches = list(pattern.finditer(texto[:2000]))  # Verifica só no início
#print(f"Padrões encontrados nos primeiros 2000 caracteres: {len(test_matches)}")

# Extração completa
#matches = pattern.finditer(texto)
#termos = [match.group(1).strip() for match in matches]

#print(f"\nTermos encontrados: {len(termos)}")
#print("Exemplos:", termos[:5])

