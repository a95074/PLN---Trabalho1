import re
import json

filename = "diccionari-multilinguee-de-la-covid-19-simplificado1.xml"

with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()

texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="12"><i>CAS </i></text>*\n?', '', texto) #remoção do CAS que é desnecessário

padrao1 = re.compile(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="\d+">\s*\b(\d+(?:-+\d+)+\b)\s*</text>*\n?')
texto= padrao1.sub(r'', texto)


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

# Salvar resultados
with open("teste.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)
