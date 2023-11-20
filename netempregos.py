import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
from time import sleep

# Programa que utiliza o Requests + BeautifulSoup4 para web scraping em site com HTML estático


def get_url_net_empregos(profissao):
    """Formata a url para a profissão pretendida"""

    template = "https://www.net-empregos.com/{}/"
    url = template.format(profissao)
    return url


def format_date_net_empregos(date):
    """Formata a data para YYYY-MM-DD"""

    dia, mes, ano = map(int, date.split("-"))
    return f"{ano:04d}-{mes:02d}-{dia:02d}"


def extrair_vaga_net_empregos(vaga):
    """Extrai o texto contido nas tags HTML que tenham um identificador único"""

    titulo = vaga.find("a", "oferta-link").text.strip()

    # Extração e formatação de data para padronizar na database MySQL
    data_unformated = vaga.ul.li.text
    data_postagem = format_date_net_empregos(data_unformated)
    data_consulta = datetime.today().strftime("%Y-%m-%d")

    # Itera sobre os índices de uma lista de dados com cidade e nome da empresa
    lista = vaga.find_all("li")
    cidade = lista[1].text.strip()
    empresa = lista[3].text.strip()

    # Seleciona o valor (não o texto) do identificador 'href=...' na tag 'a' com identificador "oferta-link"
    href = vaga.find("a", "oferta-link").get("href")
    # Cria o link da vaga adicionando o href ao link da página inicial
    link = "https://www.net-empregos.com" + href

    # Cria uma tupla para cada vaga. Adiante, a tupla será adicionada a uma lista
    registro = (titulo, cidade, empresa, data_postagem, data_consulta, link)

    return registro


def buscar_net_empregos(profissao):
    """Roda o programa principal de rotina"""

    # Lista que receberá as tuplas dos registros de vagas
    lista_registros = []
    url = get_url_net_empregos(profissao)

    # Extração de dados
    while True:
        # Acessa o site
        response = requests.get(url)
        # Encontra todas as tags HTML para extrair as informações das vagas
        site = BeautifulSoup(response.text, "html.parser")
        sleep(0.2)

        # Encontra a tag que contém todos os dados de uma vaga
        vagas = site.find_all("div", class_="job-item")

        # Itera pelas vagas e adiciona os dados de cada uma à lista_registros
        for vaga in vagas:
            registro = extrair_vaga_net_empregos(vaga)
            lista_registros.append(registro)

        # Atualiza a url para a próxima página caso só haja botão 'próximo'
        if url == f"https://www.net-empregos.com/{profissao}/":
            try:
                href_next_page = site.find("a", {"class": "d-lg-none"}).get("href")
                url = "https://www.net-empregos.com" + href_next_page

            # Tratamento de erros para não dar crash no programa
            except AttributeError:
                break

        # O botão 'próximo' e 'anterior' têm mesmo identificador, por isso o href copiado é do index 1 ('próximo')
        else:
            try:
                href_next_page = site.find_all("a", {"class": "d-lg-none"})
                href_next_page2 = href_next_page[1].get("href")
                url = "https://www.net-empregos.com" + href_next_page2

            except (AttributeError, IndexError):
                break

    # Salva os dados em um arquivo CSV para importá-lo à database MySQL
    with open(f"{profissao}_net_empregos.csv", 'w', newline='', encoding='utf-8') as n:
        writer = csv.writer(n)
        writer.writerow(["titulo", "cidade", "empresa", "dataPostagem", "dataConsulta", "link"])
        writer.writerows(lista_registros)


buscar_net_empregos('programador')

# O CSV é importado para a database WebScrap, que tem na tabela 'programador' a coluna 'link' como chave primária
# Os registros importados serão adicionados apenas se tiverem link diferente dos que estão na tabela
# Ao longo do tempo, a tabela irá crescer e mostrar a progressão no número real de novas ofertas de emprego,
# desconsiderando as vagas repostadas automaticamente e renovação de anúncios, trazendo dados fidedignos de ofertas.
