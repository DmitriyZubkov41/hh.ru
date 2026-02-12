import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
import re

'''
   Получить сколько вакансий по ключевому слову есть с фильтром 'professional_roles' = 156 и опыт=1-3 года и период = 10
'''

url = 'https://hh.ru/search/vacancy'

key_skills = ['a/b-тест', 'ad-hoc', 'ad/hoc', 'agile', 'airflow', 'ansible', 'api', 'bash', 'big data', 'ci/cd', 'clickhouse', 'c++', 'c#', 'data-driven', 'dag', 'datalens', 'dax', 'dbt', 'django', 'docker', 'dwh', 'eda', 'etl', 'excel', 'git', 'grafana', 'greenplum', 'hadoop', 'java', 'jenkins', 'kafka', 'kubernetes', 'looker studio', 'mathplotlib', 'mariadb', 'metabase', 'mongodb', 'mvp', 'mysql', 'n8n', 'numpy', 'oracle', 'pandas', 'postgresql', 'power bi', 'power query', 'power pivot', 'prometheus', 'psycopg2', 'python', 'pytorch', 'rabbitmq', 'redis', 'seaborn', 'sklearn', 'spark', 'sql', 'sqlite', 'sqlalchemy', 'superset', 'tableau', 'terraform', 'витрин', 'воронка', 'пайплайн', 'статистик', 'метрик']


params = {
    'professional_role': 156,
    'experience': 'between1And3',
    'search_period': 10,
    'items_on_page': 100
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

statistik = []
total = requests.get('https://api.hh.ru/vacancies?professional_role=156&experience=between1And3&period=10').json()['found']

for word in key_skills:
    params['text'] = word
    
    response = requests.get(url, params=params, headers=headers)

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    #элемент<h1 data-qa="title" class="magritte-text___gMq2l_7-0-27 magritte-text-overflow___UBrTV_7-0-27 
    counter = soup.find('h1', {'data-qa': 'title'})
    print(counter.text)
    if 'ничего не' in counter.text:
        statistik.append([word, 0, 0])
    else:
        #number = int(''.join(char for char in counter.text if char.isdigit()))
        match = re.search(r'(\d+)', counter.text)
        number = int(match.group(1)) if match else 0
        statistik.append([word, number, round(number*100/total, 1)])

statistik.sort(key=lambda x: x[1], reverse=True)

# Запишем список в csv файл
filename = f'key_words_{date.today().strftime("%d.%m.%Y")}.csv'
with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['Слово', 'Количество', f'Процент из {total}'])
    writer.writerows(statistik)
