import csv
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from datetime import datetime

# Programa que utiliza Selenium + BeautifulSoup4 para web scrapping em site com HTML não-estático


def get_url_careerjet(profissao):
    """Formata a url para a profissão pretendida"""

    template = "https://www.careerjet.pt/buscar/empregos?s={}/"
    url = template.format(profissao)
    return url


def format_date_careerjet(date):
    """Formata a data, calculando o dia, mês e ano atuais com base na informação da tag html"""

    # Se for há menos de um dia
    if 'hora' in date:
        dia = datetime.today().day
        mes = datetime.today().month
        ano = datetime.today().year
        date_formated = f"{ano:04d}-{mes:02d}-{dia:02d}"

    # Se for há menos de um ano
    elif 'dia' in date:
        date_unformated = date.replace("Há", "").replace("dias", "").replace(" ", "").replace("dia", "")
        dia_unformated = int(date_unformated)
        dia = abs(datetime.today().day - dia_unformated)

        # Se o mês mudar para o anterior
        if dia >= datetime.today().day:
            mes = datetime.today().month - 1
            if mes < 1:
                mes = datetime.today().replace(month=12).month
                ano = datetime.today().year - 1
        # Se o mês for o mesmo que o atual
        else:
            mes = datetime.today().month
            ano = datetime.today().year

        date_formated = f"{ano:04d}-{mes:02d}-{dia:02d}"

    # Se for há mais de um mês
    else:
        date_unformated = (date.replace("Há", "").replace("mês", "").replace(" ", "")
                           .replace("meses", "").replace("mes", "").replace("es", ""))
        mes_unformated = int(date_unformated)
        # Converte o valor para positivo (evita dia negativo incompatível com formato de datas)
        mes = abs(datetime.today().month - mes_unformated) + 12
        dia = datetime.today().day

        # Se o ano mudar para o anterior
        if mes >= mes_unformated:
            ano = datetime.today().year - 1
        # Se o ano for o mesmo que o atual
        else:
            ano = datetime.today().year

        date_formated = f"{ano:04d}-{mes:02d}-{dia:02d}"

    return date_formated


def extrair_vaga_careerjet(vaga):
    """Extrai o texto contido nas tags HTML que tenham um identificador único"""

    titulo = vaga.find("a").text.strip()

    # Se o nome da empresa for anunciado
    if vaga.find("p", class_="company"):
        empresa = vaga.find("p", class_="company").text.strip()
    # Se o nome da empresa for anônimo
    else:
        empresa = 'Sigiloso'

    tag_cidade = vaga.find("ul", class_="location")
    # Mostra apenas a região mais abrangente da vaga (ex: excluindo o bairro quando dá duas localizações)
    cidade2 = tag_cidade.find_all("li")[0].text.strip()

    # Pega a data no formato "há x tempo" e retorna uma string no formato "yyyy-mm-dd"
    data = vaga.find("span", class_="badge").text.strip()
    data_postagem = format_date_careerjet(data)

    data_consulta = datetime.today().date()

    # Seleciona o valor (não o texto) do identificador 'href=...' na tag 'a' dentro de 'h2'
    href = vaga.h2.a.get("href")
    # Cria o link da vaga adicionando o href ao link da página inicial
    link = "https://www.careerjet.pt" + href

    # Cria uma tupla para cada vaga. Adiante, a tupla será adicionada a uma lista
    registro = (titulo, cidade2, empresa, data_postagem, data_consulta, link)

    return registro


def buscar_careerjet(profissao):
    """Roda o programa inicial de rotina"""

    # Lista que receberá as tuplas dos registros de vagas
    lista_registros = []
    url = get_url_careerjet(profissao)

    # Extração de dados
    while True:
        # Abre o selenium com o chrome webdriver para carregar o conteúdo JS
        # Com o Requests + BeautifulSoup4 não era possível acessar as tags
        driver = webdriver.Chrome()
        driver.get(url)
        # Dá tempo para o programa carregar o conteúdo da página
        time.sleep(2)

        # Executa o script de JS para rolar para ponto (x=0, y=document.body.scrollHeight), o fim da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # Encontra todas as tags HTML/XML para extrair as informações das vagas
        html = BeautifulSoup(driver.page_source, 'lxml')

        # Encontra a tag que contém todos os dados de uma vaga
        vagas = html.find_all('article', attrs={'class': 'job'})

        # Itera pelas vagas e adiciona os dados de cada uma à lista_registros
        for vaga in vagas:
            registro = extrair_vaga_careerjet(vaga)
            lista_registros.append(registro)

        # Atualiza a url para a próxima página enquanto houver a tag 'a' com 'rel="next"' (botão next da página)
        try:
            href_next = html.find("a", rel="next").get("href")
            url = "https://www.careerjet.pt" + href_next

        # Tratamento de erros para não dar crash no programa
        except AttributeError:
            break

    # Salva os dados em um arquivo CSV para importá-lo à database MySQL
    with open(f'{profissao}_carrerjet.csv', 'w', newline='', encoding='utf-8') as c:
        writer = csv.writer(c)
        writer.writerow(["titulo", "cidade", "empresa", "dataPostagem", "dataConsulta", "link"])
        writer.writerows(lista_registros)


buscar_careerjet('programador')

# O CSV é importado para a database WebScrap, que tem na tabela 'programador' a coluna 'link' como chave primária
# Os registros importados serão adicionados apenas se tiverem link diferente dos que estão na tabela
# Ao longo do tempo, a tabela irá crescer e mostrar a progressão no número real de novas ofertas de emprego,
# desconsiderando as vagas repostadas automaticamente e renovação de anúncios, trazendo dados fidedignos de ofertas.
