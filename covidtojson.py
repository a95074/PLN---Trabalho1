import re
import json
import unicodedata

filename = "diccionari-multilinguee-de-la-covid-19-simplificado1.xml"
with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()

texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="12"><i>CAS </i></text>*\n?', '', texto)

texto = re.sub(r'<text top="\d+" left="\d+" width="\d+" height="\d+" font="\d+">\s*\b(\d+(?:-+\d+)+\b)\s*</text>*\n?', '', texto)

texto = re.sub(r'-*\n?', '', texto) #remoção do travessão


#foi necessário implemenetar esta funçao para depois ao ordenar conceitos com ou sem siglas os acentos nao interfiram

def remove_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

#função para extrair traduções depois do termo
def extrair_traducoes(texto_pos_termo):
    padrao_traducao = re.compile(
        r'<text[^>]+font="12"><i>(?P<lang>\w+(?: \[..\])?)\s*</i></text>\s*'
        r'<text[^>]+font="11">(?P<traducao>.*?)</text>',
        re.DOTALL
    )
    traducoes = {}
    for match in padrao_traducao.finditer(texto_pos_termo):
        lang = match.group("lang").strip()
        traducao = match.group("traducao").strip()
        traducoes[lang] = traducao
    return traducoes

def extrair_descricao(texto_pos_traducao):
    padrao_linha_descricao = re.compile(
        r'<text[^>]+font="(?:11|27|33)">(?P<linha>.*?)</text>'
    )
    descricao = []
    for match in padrao_linha_descricao.finditer(texto_pos_traducao):
        linha = match.group("linha").strip()
        # Se encontrarmos um novo termo (font 25), paramos
        if re.search(r'<text[^>]+font="25"><b>', texto_pos_traducao[match.start():]):
            break
        descricao.append(linha)
    return " ".join(descricao)


#padrao que encontra os termos e as suas siglas associadas

padrao_siglas = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'<text[^>]+font="11">\s*sigla\s*</text>\s*'
    r'(?P<siglas>(?:<text[^>]+font="25"><b>.*?</b></text>\s*)+?)'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',
    re.DOTALL
)

# Padrão para todos os conceitos sem siglas

padrao_conceitos_validos = re.compile(
    r'<text[^>]+font="25"><b>(?P<termo>[^<]+)</b></text>\s*'
    r'(?=<text[^>]+font="12"><i>\s*oc\s*</i>)',
    re.DOTALL
)

siglas_set = set()
termos_siglas = []

for match in padrao_siglas.finditer(texto):
    termo = match.group("termo").strip()
    siglas_bruto = match.group("siglas")
    siglas = re.findall(r'<b>(.*?)</b>', siglas_bruto)
    siglas = [s.strip() for s in siglas if s.strip()]
    siglas_set.update(s.lower() for s in siglas)

    # procurar traduções após a última sigla capturada
    fim = match.end()
    trecho_pos_termo = texto[fim:fim+2000]  # limitar o tamanho para segurança
    traducoes = extrair_traducoes(trecho_pos_termo)
    descricao = extrair_descricao(trecho_pos_termo)

    termos_siglas.append({
        "termo": termo,
        "siglas": siglas,
        "traducoes": traducoes,
        "descricao": descricao
    })

#extrair todos os conceitos válidos e ignorar os que são apenas siglas

conceitos_finais = []

for match in padrao_conceitos_validos.finditer(texto):
    termo = match.group("termo").strip()
    if termo.lower() not in siglas_set:
        fim = match.end()
        trecho_pos_termo = texto[fim:fim+2000]
        traducoes = extrair_traducoes(trecho_pos_termo)
        descricao = extrair_descricao(trecho_pos_termo)
        conceitos_finais.append({
            "termo": termo,
            "siglas": [],
            "traducoes": traducoes,
            "descricao": descricao
        })

# Combinar os dois
todos_termos = termos_siglas + conceitos_finais
todos_termos.sort(key=lambda x: remove_acentos(x["termo"]))

with open("termos_oc.json", "w", encoding="utf-8") as f:
    json.dump(todos_termos, f, ensure_ascii=False, indent=2)

with open("teste.xml", 'w', encoding='utf-8') as novo_arquivo:
    novo_arquivo.write(texto)
