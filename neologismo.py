import re
import json

filename = "glossario_neologismos_saude.xml"

#primeiro passo foi retirar manualmente no xml as páginas de introdução que não continham informação relevante para o json
#foi retirado manualmente os indexes e bibliografias

with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()

texto = re.sub(r'</page>\s*\n?', '', texto) #remove todas as trocas de página do ficheiro
texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="23"> </text>*\n?', '',texto)
texto = re.sub(r'<page number="\d+" position="absolute" top="\d+" left="\d+" height="\d+" width="\d+">*\n?', '', texto)
texto = re.sub(r'<text[^>]*?>\((\d+)\)\s*</text>*\n?', '', texto)


padrao_completo = re.findall(
    r'<text[^>]*?>(.*?)</text>\s*'  # conceito
    r'<text[^>]*?><i>(s\.f\.|s\.m\.)</i></text>\s*',
    texto
)

resultado = [
    {
        "conceito": conceito,
        "substantivo": genero,
    }
    for conceito, genero in padrao_completo
]


with open("substantivos.json", "w", encoding="utf-8") as jsonfile:
    json.dump(resultado, jsonfile, ensure_ascii=False, indent=2)

with open("teste2.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)