import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
from time import sleep


def get_url(profissao):
    """Formata a url para a profissão pretendida"""
    template = f"https://www.careerjet.pt/buscar/empregos?s={profissao}/"
    return template


headers = {
    "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

url = get_url('programador')
request = requests.get(url, headers=headers)

site = BeautifulSoup(request.text, "html.parser")

tag = site.main
print(tag)



