import pandas as pd
import requests
from time import sleep
from datetime import date


# Получить сколько вакансий по слову есть с фильтром 'professional_roles' = 156 и опыт=1-3 года
url = 'https://api.hh.ru/vacancies'

params = {
    'per_page': 100,
    'professional_role': 156,
    'experience': 'between1And3',
    'period': 10,
    'search_field': 'description'
}


key_skills = ['a/b-тест', 'ad-hoc', 'ad/hoc', 'agile', 'airflow', 'ansible', 'api', 'bash', 'big data', 'ci/cd', 'clickhouse', 'c++', 'c#', 'data-driven', 'datalens', 'dax', 'dbt', 'django', 'docker', 'dwh', 'eda', 'etl', 'excel', 'git', 'grafana', 'greenplum', 'hadoop', 'java', 'jenkins', 'kafka', 'kubernetes', 'looker studio', 'mathplotlib', 'metabase', 'mongodb', 'mvp', 'mysql', 'n8n', 'numpy', 'oracle', 'pandas', 'postgresql', 'power bi', 'power query', 'power pivot', 'prometheus', 'python', 'pytorch', 'rabbitmq', 'redis', 'seaborn', 'sklearn', 'spark', 'sql', 'sqlalchemy', 'superset', 'tableau', 'terraform', 'витрин', 'воронка', 'пайплайн', 'статистик', 'метрик']
statistik = []
total = requests.get('https://api.hh.ru/vacancies?professional_role=156&experience=between1And3&period=10').json()['found']

for word in key_skills:
    print(word)
    count = 0
    params['text'] = word
    for page in range(20):
        params['page'] = page
        sleep(0.6)
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        if response.status_code != 200 or not response.json()['items']:
            break
        data = response.json()
        count += len(data['items'])
    statistik.append([word, count, round(count*100/total, 1)])

df = pd.DataFrame(statistik, columns=['Слово', 'Количество', f'Процент из {total}'])
df = df.sort_values(by='Количество', ascending=False)
df.to_csv(f'key_words_{date.today().strftime("%d.%m.%Y")}.csv', index=False)
