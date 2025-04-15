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


padrao_conceito_substantivo = re.compile(
    r'<text[^>]*?>(?P<conceito>.*?)</text>\s*'
    r'<text[^>]*?><i>\s*(?P<substantivo>s\.f\.|s\.m\.)\s*</i></text>\s*'
)


padrao_texto = re.compile(r'<text[^>]*?>(.*?)</text>')

padrao_sigla = re.compile(
    r'(?:<text[^>]*?>Sigla:\s*</text>\s*<text[^>]*?><i>(.*?)</i></text>'  # caso com <i>
    r'|<text[^>]*?>Sigla:\s*(.*?)</text>)',  # caso tudo numa linha
    re.IGNORECASE
)



# Função para extrair tradução (até 3 linhas após o substantivo)
def extrair_traducoes(trecho):
    blocos = padrao_texto.findall(trecho)
    partes = []

    for bloco in blocos:
        texto_limpo = bloco.strip().lower()

        if "[ing]" in texto_limpo or "[esp]" in texto_limpo:
            partes.append(bloco.strip())
        else:
            # Parar ao primeiro bloco que não contenha tradução
            break

    if partes:
        return " ".join(partes)
    return None

def extrair_sigla(trecho):
    match = padrao_sigla.search(trecho)
    if match:
        return (match.group(1) or match.group(2)).strip()
    return None



# Lista de resultados
resultado = []

# Iterar sobre os conceitos
for match in padrao_conceito_substantivo.finditer(texto):
    conceito = match.group("conceito").strip()
    genero = match.group("substantivo")
    fim = match.end()

    trecho_pos_termo = texto[fim:fim+3000]
    traducoes = extrair_traducoes(trecho_pos_termo)
    sigla = extrair_sigla(trecho_pos_termo[:600])


    resultado.append({
        "conceito": conceito,
        "substantivo": genero,
        "traducoes": traducoes,
        "sigla": sigla
    })


# Exportar o JSON
with open("substantivos.json", "w", encoding="utf-8") as jsonfile:
    json.dump(resultado, jsonfile, ensure_ascii=False, indent=2)

# Guardar XML limpo para reutilização
with open("teste2.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)