import re
import json

filename = "diccionari-multilinguee-de-la-covid-191.xml"

with open(filename, 'r', encoding='utf-8') as file:
    texto = file.read()