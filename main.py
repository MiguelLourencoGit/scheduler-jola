import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    filename='status.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuração da Google Sheet
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

sheet_id = "1UE6pFA_wOaH-qGjG6fbYE2TV8xDpNE55XNcZzae84uE"
sheet = client.open_by_key(sheet_id)
worksheet = sheet.sheet1

# Função para scrapar o preço
def get_price():
    url = 'https://www.continente.pt/produto/cerveja-com-alcool-mini-super-bock-6148284.html'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('span', class_='ct-price-formatted')
        if price:
            preco = price.text.strip().replace("€", "").replace(",", ".")
            logging.info(f"Preço encontrado: {preco} €")
            return float(preco)
        else:
            logging.warning("Preço não encontrado.")
            return None
    else:
        logging.error(f"Erro na requisição: status code {response.status_code}")
        return None

# Função para adicionar o preço à Sheet
def adicionar_preco():
    preco = get_price()
    if preco is None:
        logging.info("Preço não foi adicionado porque não foi encontrado.")
        return
    
    preco_unidade = preco / 30
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    # Vai buscar todas as datas existentes na primeira coluna
    datas_existentes = worksheet.col_values(1)

    if data_hoje in datas_existentes:
        logging.info(f"Já existe entrada para {data_hoje}.")
    else:
        worksheet.append_row([data_hoje, f"{preco:.2f} €", f"{preco_unidade:.2f} €"])
        logging.info(f"Preço adicionado para {data_hoje}: {preco:.2f} € ({preco_unidade:.2f} €/unidade)")

# Executar
adicionar_preco()
