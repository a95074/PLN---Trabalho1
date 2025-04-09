import re
import json

filename = "diccionari-multilinguee-de-la-covid-19.xml"

#primeiro passo foi retirar manualmente no xml as páginas de introdução que não continham 

with open(filename, 'r', encoding='utf-8') as file:
    ficheiro = file.read()