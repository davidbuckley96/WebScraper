from datetime import datetime


def format_date_careerjet(date):

    if 'hora' in date:
        date_formated = datetime.today().date()

    elif 'dia' in date:
        date_unformated = date.replace("Há", "").replace("dias", "").replace(" ", "").replace("dia", "")
        dia_unformated = int(date_unformated)
        dia = abs(datetime.today().day - dia_unformated)
        if dia >= datetime.today().day:
            mes = datetime.today().month - 1
            if mes < 1:
                mes = datetime.today().replace(month=12).month
                ano = datetime.today().year - 1
        else:
            mes = datetime.today().month
            ano = datetime.today().year

        date_formated = f"{ano}-{mes}-{dia}"

    else:
        date_unformated = date.replace("Há", "").replace("mês", "").replace(" ", "").replace("meses", "").replace("mes", "").replace("es", "")
        mes_unformated = int(date_unformated)
        mes = abs(datetime.today().month - mes_unformated) + 12
        dia = datetime.today().day
        if mes >= mes_unformated:
            ano = datetime.today().year - 1
        else:
            ano = datetime.today().year

        date_formated = f'{ano}-{mes}-{dia}'

    return date_formated


print(format_date_careerjet('Há 18 meses'))
