import re
import json

filename = "glossario_ministerio_saude.xml"

#primeiro passo foi retirar manualmente no xml as páginas de introdução que não continham informação relevante para o json
#foi retirado manualmente os indexes e bibliografias

with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()


texto = re.sub(r'</page>\s*\n?', '', texto) #remove todas as trocas de página do ficheiro
texto = re.sub(r'<page number="\d+" position="absolute" top="\d+" left="\d+" height="\d+" width="\d+">*\n?', '', texto)
texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="\d+">\d+</text>*\n?', '', texto)
texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="22">.</text>*\n?', '', texto)
texto = re.sub (r"<i>*\n?", "", texto) #É preciso ser retirado isto porque há termos em ingles em italico 
texto = re.sub (r"</i>*\n?", "", texto)


texto = re.sub (r"<b>*\n?", "", texto) 
texto = re.sub (r"</b>*\n?", "", texto)


def extrair_conceitos(texto):
    padrao_conceito = re.findall(r'<text[^>]*font="21"[^>]*>(.*?)</text>', texto)
    
    conceitos = []
    juntar = ""

    for con in padrao_conceito:
        con = con.strip()
        if juntar:
            juntar += " " + con
            conceitos.append(juntar.strip())
            juntar = ""
        else:
            juntar = con

    if juntar:
        conceitos.append(juntar.strip())
    
    return conceitos

def extrair_categoria(texto):
    match = re.search(
        r'<text[^>]*font="16"[^>]*>\s*<i>Categoria:\s*</i>\s*</text>\s*'
        r'<text[^>]*font="14"[^>]*>(.*?)</text>',
        texto,
        re.DOTALL
    )
    return match.group(1).strip() if match else None


resultado = []

for conceito in extrair_conceitos(texto):
    categoria = extrair_categoria(texto)
    resultado.append({
        "Conceito": conceito,
        "Categoria": categoria
    })


file_out = open("conceitos.json","w",encoding= 'utf-8')
json.dump(resultado,file_out,indent=4,ensure_ascii=False)
file_out.close()



with open("teste.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)
