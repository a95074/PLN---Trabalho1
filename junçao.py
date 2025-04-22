import json

# Ficheiros de entrada
ministerio_json = "glossario_ministerio.json"
neologismos_json = "glossario_neologismos.json"
covid_json = "glossario_covid.json"

# Ficheiro de saída
junçao_conceitos = "glossario_juncao.json"

# Leitura dos glossários
with open(ministerio_json, "r", encoding="utf-8") as f:
    ministerio = json.load(f)

with open(neologismos_json, "r", encoding="utf-8") as f:
    neologismos = json.load(f)

with open(covid_json, "r", encoding="utf-8") as f:
    covid = json.load(f)

# Dicionário final por conceito
conceitos_unificados = {}

# Função para inserir conceito com origem
def adicionar_conceito(lista, origem):
    for item in lista:
        nome = item["Conceito"]
        if nome not in conceitos_unificados:
            conceitos_unificados[nome] = {"Conceito": nome, "Fontes": {origem: item}}
        else:
            conceitos_unificados[nome]["Fontes"][origem] = item

# Inserção por glossário
adicionar_conceito(ministerio, "ministerio")
adicionar_conceito(neologismos, "neologismo")
adicionar_conceito(covid, "covid")

# Ordenar por nome do conceito
resultado_final = sorted(conceitos_unificados.values(), key=lambda x: x["Conceito"].lower())

# Escrita do resultado
with open(junçao_conceitos, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, ensure_ascii=False, indent=2)
