
import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn; seaborn.set()
from pandas_datareader import data as pdr
from bs4 import BeautifulSoup
import xlsxwriter
from matplotlib.backends.backend_pdf import PdfPages
from fpdf import FPDF
# Из данных есть:
# Цены на продукт А, который уже есть на рынке Европы
# ----- октябрь 2018 - 
# ----- ноябрь 2018 - 
# ----- февраль 2019 -

# Котировки нефти, курс eur/usd
dbc = pd.read_excel('/Users/georgiekevkhishvili/Desktop/home/cur_oil.xlsx')

# Затраты на производство
PRODUCTION_COST = 400 # (EUR)

# Расходы на логистику
EU_LOGISTIC_COST_EUR = 30 # в Европу в евро
CN_LOGISTIC_COST_USD = 130 # в Китай в долларах



#С этого сайта берем курс валюты EUR/USD
URL = 'https://www.val.ru/valratios.asp?t1=978&t2=840'

# * Справочная информация по клиентам(объемы, локации, комментарии) 
customers = {
    'Monty':{
        'location':'EU',
        'volumes':200,
        'comment':'moving_average'
    },
    
    'Triangle':{
        'location':'CN',
        'volumes': 30,
        'comment': 'monthly'
    },
    'Stone':{
        'location':'EU',
        'volumes': 150,
        'comment': 'moving_average'
    },
    'Poly':{
        'location':'EU',
        'volumes': 70,
        'comment': 'monthly'
    }
}
# Скидки
discounts = {'up to 100': 0.01, # 1%
             'up to 300': 0.05, # 5%
             '300 plus': 0.1}   #10%




def cost_logistic(region, currency):
        if region == 'EU':
            price = EU_LOGISTIC_COST_EUR
        elif region == 'CN':
            price = CN_LOGISTIC_COST_USD/currency
        else:
            print('Неизвестный регион ', region)
        return price
    
#Цена на заводе       
def fcc(price, currency):
    cost = (16 * price/currency) + PRODUCTION_COST
    return cost

#Цена с доставкой (Цена на заводе + доставка)
def ddp (price, currency, region):
    k1= fcc(price, currency)
    k2= cost_logistic(region, currency)
    cost_ddp =k1  + k2
    return cost_ddp

#Расчет скользящей средней (SMA) за последние 10 дней
def sma(volumes):
    day = 10
    SMA = dbc.dropna().copy()
    return SMA['DDP'].tail(day).sum()/day*volumes 

#Расчет средней (EMA) за последние 30 дней
def ema(volumes):
    day = 30
    SMA = dbc.dropna().copy()
    return SMA['DDP'].tail(day).sum()/day*volumes 

#Получение курса на текущий день
def get_rate(URL):
    
    source = requests.get(URL)
    main_txt = source.text
    soup = BeautifulSoup(main_txt, 'html.parser')
    k = soup.find_all('td')
    l = str(k[180])
    l = l.replace('<td width="80">', '')
    l = float(l.replace('</td>', ''))
    return l


def get_price():
    for key, value in customers.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        region = value['location']
        comment = value['comment']
        volumes = value['volumes']
        if comment =='moving_average':
            price = float('{:.2f}'.format(sma(volumes))) #2 знака после запятой
            if region =='EU':
                all_price = price + EU_LOGISTIC_COST_EUR
            else:
                all_price = price + CN_LOGISTIC_COST_USD
            cost = 'Magic_White_Powder '+ '      ' + str(volumes)+ '      ' + str(all_price)
            pdf.cell(10, 20, cost)
            pdf.output(f'/Users/georgiekevkhishvili/Desktop/home/{key}.pdf', 'F')
        elif comment == 'monthly':
            price = float('{:.2f}'.format(ema(volumes))) #2 знака после запятой
            if region =='EU':
                all_price = price + EU_LOGISTIC_COST_EUR
            else:
                all_price = price + CN_LOGISTIC_COST_USD
            cost = 'Magic_White_Powder '+ '      ' + str(volumes)+ '      ' + str(all_price) #цену переводим в строковый тип чтобы записать его в pdf
            pdf.cell(10, 20, cost)
            pdf.output(f'/Users/georgiekevkhishvili/Desktop/home/{key}.pdf', 'F')
    


def get_price_ex(kol, name):  # Данная функция получает курс валют из сайта val.ru, 
    pdf = FPDF()           #затем получаем стоимость и записываем в pdf файл 
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    price = float('{:.2f}'.format(ema(kol) * get_rate('https://www.val.ru/valratios.asp?t1=978&t2=840')))
    cost = 'Magic_White_Powder '+ '      ' + str(kol)+ '      ' + str(price)
    pdf.cell(10, 20, cost)
    pdf.output(f'/Users/georgiekevkhishvili/Desktop/home/{name}.pdf', 'F')



writer = pd.ExcelWriter('/Users/georgiekevkhishvili/Desktop/home/demo.xlsx', engine='xlsxwriter')
for key, value in customers.items():
    region = value['location']
    dbc['FCA'] = fcc(dbc['OIL'], dbc['EURUSD=X'])
    dbc['DDP'] = ddp(dbc['OIL'], dbc['EURUSD=X'], region)
    dbc.to_excel(writer, sheet_name = key)
writer.save()
dbc.plot(x='Date', y='DDP');


