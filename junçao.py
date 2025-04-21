import json


ministerio_json = "glossario_ministerio.json"
neologismos_json = "glossario_neologismos.json"
junçao_conceitos = "glossario_junçao.json"


with open(ministerio_json, "r", encoding="utf-8") as f:
    ministerio = json.load(f)

with open(neologismos_json, "r", encoding="utf-8") as f:
    neologismos = json.load(f)


neologismo_dict = {item["Conceito"]: item for item in neologismos}

for conceito_m in ministerio:
    nome = conceito_m["Conceito"]
    descricao = conceito_m.get("Descrição")

    if nome in neologismo_dict:
        #print(f"Conceito já existe no neologismo: {nome}")
        if not neologismo_dict[nome].get("Descrição") and descricao:
            neologismo_dict[nome]["Descrição"] = descricao
    else:
        neologismo_dict[nome] = conceito_m

resultado_final = sorted(neologismo_dict.values(), key=lambda x: x["Conceito"].lower())

with open(junçao_conceitos, "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, ensure_ascii=False, indent=2)


