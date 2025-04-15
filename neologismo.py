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
    return ("Sem sigla associada")

def extrair_descricao(trecho):
    padrao_bloco = re.finditer(
        r'<text[^>]*?top="\d+" left="(?P<left>\d+)"[^>]*?font="(?P<font>\d+)"[^>]*?>(.*?)</text>',
        trecho
    )

    descricao_partes = []
    for m in padrao_bloco:
        left = int(m.group("left"))
        font = int(m.group("font"))
        conteudo = m.group(3).strip()

        # Parar se for citação
        if conteudo.startswith("“") or conteudo.startswith('"') or conteudo.startswith("..."):
            break

        # Parar se for início de novo termo
        if left == 128 and font == 23:
            if re.match(r'^[a-zá-úç\- ]{3,}$', conteudo.lower()):
                break

        # Só aceitar blocos font=23 com texto "normal"
        if font == 23 and len(conteudo) > 0 and not any(x in conteudo.lower() for x in ['[ing]', '[esp]', 'sigla:']):
            descricao_partes.append(conteudo)

    if descricao_partes:
        return " ".join(descricao_partes)
    return None


def extrair_citacao(trecho):
    blocos = re.findall(r'<text[^>]*?font="24"[^>]*?>(.*?)</text>', trecho)
    citacao_partes = []
    citando = False

    for linha in blocos:
        texto = re.sub(r'<[^>]+>', '', linha).strip()
        if texto.startswith('“...'):
            citando = True
        if citando:
            citacao_partes.append(texto)
        if texto.endswith('...”') or texto.endswith('...” ') or texto.endswith('...”</i>'):
            break

    if citacao_partes:
        return " ".join(citacao_partes)
    return None



# Lista de resultados
resultado = []

# Iterar sobre os conceitos
for match in padrao_conceito_substantivo.finditer(texto):
    conceito = match.group("conceito").strip()
    genero = match.group("substantivo")
    fim = match.end()

    trecho_pos_termo = texto[fim:fim+6500]

    traducoes = extrair_traducoes(trecho_pos_termo)
    sigla = extrair_sigla(trecho_pos_termo[:600])
    descricao = extrair_descricao(trecho_pos_termo)
    citacao = extrair_citacao(trecho_pos_termo)



    resultado.append({
        "conceito": conceito,
        "substantivo": genero,
        "traducoes": traducoes,
        "sigla": sigla,
        "descricao": descricao,
        "citacao": citacao,
    })


# Exportar o JSON
with open("substantivos.json", "w", encoding="utf-8") as jsonfile:
    json.dump(resultado, jsonfile, ensure_ascii=False, indent=2)

# Guardar XML limpo para reutilização
with open("teste2.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)