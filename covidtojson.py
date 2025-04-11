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

# Padrão para todos os conceitos com <i>oc</i>
padrao_conceitos_validos = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',
    re.DOTALL
)

# Primeiro: extrair todas as siglas e os conceitos com siglas
siglas_set = set()
termos_siglas = []

for match in padrao_siglas.finditer(texto):
    termo = match.group("termo").strip()
    siglas_bruto = match.group("siglas")
    siglas = re.findall(r'<b>(.*?)</b>', siglas_bruto)
    siglas = [s.strip() for s in siglas if s.strip()]
    termos_siglas.append({
        "termo": termo,
        "siglas": siglas
    })
    siglas_set.update(s.lower() for s in siglas)  # para evitar termos que são só siglas

# Agora: extrair todos os conceitos válidos e ignorar os que são apenas siglas
conceitos_finais = []

for match in padrao_conceitos_validos.finditer(texto):
    termo = match.group("termo").strip()
    if termo.lower() not in siglas_set:
        conceitos_finais.append({
            "termo": termo,
            "siglas": []
        })

# Combinar os dois
todos_termos = termos_siglas + conceitos_finais

# Guardar resultado em JSON
with open("conceitos_com_siglas.json", "w", encoding="utf-8") as f:
    json.dump(todos_termos, f, ensure_ascii=False, indent=2)

with open("teste.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)


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

