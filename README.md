## API сайта hh.ru ##

Задача: используя API сайта, получить список интересующих вакансий, вывести в читаемом формате, построить дашборд. 

Задача реализована с помощью 4 скриптов, основной из них main.py

**Python**

<details> <summary>Код main.py</summary>

```python
import pandas as pd
import requests
from time import sleep
from datetime import datetime as dt

import database
import to_html


def get_full_description(vacancy_id):
    """Получает полную информацию о вакансии по ID
       Например: ID = 129649979, тогда url: https://api.hh.ru/vacancies/129984355
    """
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при запросе вакансии {vacancy_id}: {response.status_code}")
        return None



"""
Получить список вакансий по
за период 1 дней и на удаленную работу 
 1. профессиональные роли: 156, 165, 160 или python или робототехник в названии вакансии , без опыта
 2. профессиональные роли: 156 или робототехник в названии вакансии и с опытом 1-3 года
"""
url = 'https://api.hh.ru/vacancies'
lst_experim = ['noExperience', 'between1And3']
params = {
    'per_page': 100,
    'period': 1,
    'schedule': 'remote',
    'search_field': 'name'
}
detailed_vacancies = [] # вакансии с полным описанием

for exper in lst_experim:
    params['experience'] = exper
    if exper == 'noExperience':
        params['text'] = 'professional_role:(156 OR 165 OR 160) OR ( (NAME:python OR NAME:робототехник) AND NOT (NAME:преподаватель OR NAME:учитель OR NAME:педагог) )'
    else:
        params['text'] = 'professional_role:156 OR (NAME:робототехник AND NOT (NAME:преподаватель OR NAME:учитель OR NAME:педагог))'
    
    for page in range(20):  # Максимум 20 страниц на выдачу
        params['page'] = page
        sleep(0.5)
        print(f"Смотрим страницу №{page}")
        response = requests.get('https://api.hh.ru/vacancies', params=params)

        # Если все страницы уже просмотрели, то вернёт не 200 или пустой список
        if response.status_code != 200 or not response.json()['items']:
            print("ПРОСМОТРЕЛИ ВСЕ СТРАНИЦЫ")
            break

        data = response.json()
    
        all_vacancies = data['items']
        #pprint(all_vacancies)
    
        # Получим полное описание вакансии
        for i, vacancy in enumerate(all_vacancies):
            vacancy_id = vacancy.get('id')
        
            # Задержка, чтобы не превысить лимит запросов
            sleep(0.2)  # 5 запросов в секунду - в пределах лимита
            print(f"Номер вакансии {i}")
            details = get_full_description(vacancy_id)
    
            if details:
                # Объединяем vacancy с полным описанием full_description и скиллами key_skills из details
                detailed_vacancy = {
                    'id': vacancy_id,
                    'name': vacancy.get('name'),
                    'url': vacancy.get('alternate_url'),
                    'employer': vacancy.get('employer', {}).get('name'),
                    'area': vacancy.get('area', {}).get('name'),
                    'salary_from': vacancy.get('salary', {}).get('from') if vacancy.get('salary') else None,
                    'salary_to': vacancy.get('salary', {}).get('to') if vacancy.get('salary') else None,
                    'salary_currency': vacancy.get('salary', {}).get('currency') if vacancy.get('salary') else None,
                    'professional_roles': vacancy.get('professional_roles'),
                    'published_at': vacancy.get('published_at')[:10],
                    'experience': vacancy.get('experience', {}).get('name'),
                    'schedule': vacancy.get('schedule', {}).get('name'),
                    'employment': vacancy.get('employment', {}).get('name'),
                    'full_description': details.get('description'),  # Полное описание вакансии
                    'key_skills': [skill.get('name') for skill in details.get('key_skills', [])]
                }
        
            detailed_vacancies.append(detailed_vacancy)
    
      
# Создаем DataFrame
df = pd.DataFrame(detailed_vacancies).sort_values(by=['experience', 'published_at'], ascending=[True, False])

# Список ключевых навыков:
key_skills = ['a/b-тест', 'ad-hoc', 'ad/hoc', 'agile', 'airflow', 'ansible', 'api', 'bash', 'big data', 'ci/cd', 'clickhouse', 'c++', 'c#', 'data-driven', 'dag', 'datalens', 'dax', 'dbt', 'django', 'docker', 'dwh', 'eda', 'etl', 'excel', 'git', 'grafana', 'greenplum', 'hadoop', 'java', 'jenkins', 'kafka', 'kubernetes', 'looker studio', 'mathplotlib', 'mariadb', 'metabase', 'mongodb', 'mvp', 'mysql', 'n8n', 'numpy', 'oracle', 'pandas', 'postgresql', 'power bi', 'power query', 'power pivot', 'prometheus', 'psycopg2', 'python', 'pytorch', 'rabbitmq', 'redis', 'seaborn', 'sklearn', 'spark', 'sql', 'sqlite', 'sqlalchemy', 'superset', 'tableau', 'terraform', 'витрин', 'воронка', 'пайплайн', 'статистик', 'метрик']

# Создадим столбец с скиллами из key_skills, присутствующие в столбцах 'full_description' и 'key_skills'
df['all_skills'] = df['full_description'].apply(lambda description: [skill for skill in key_skills if skill in description.lower()])
df['all_skills'] = df.apply( lambda row: list(set(row['all_skills'] + [skill.lower() for skill in row['key_skills']])), axis=1 )
print(df.shape)

#Преобразуем столбцы с типом list в строки.  Нужно для конкатенации и для записи в базу данных
df['professional_roles'] = df['professional_roles'].apply(lambda cell: '; '.join([role.get('name', 'нет роли') for role in cell]))
df['key_skills'] = df['key_skills'].apply(lambda cell: ', '.join(cell) if isinstance(cell, list) else cell)
df['all_skills'] = df['all_skills'].apply(lambda cell: ', '.join(cell) if isinstance(cell, list) else cell)
    
#Преобразуем published_at в тип date
df['published_at'] = pd.to_datetime(df['published_at'])

#Записываем в веб-страницу
to_html.write_html(df)

#Записываем в postgresql
database.write_db(df)
```
</details>

Функция get_full_description() нужна чтобы получить полное описание вакансии. 

Отправляем запрос на API с нужными мне параметрами, в первом вложенном цикле обходим все страницы, во втором вложенном цикле применяем функцию get_full_description.

В результате всех итераций сформировали словарь  detailed_vacancies. Из него создаём датафрейм. 

У меня была идея определить чаще всего встречаемый набор знаний у дата аналитика. Поэтому в датафрейме создал еще один столбец из скиллов, встрещающихся в полном описании ('full_description') и ключевых скиллах ('key_skills'). Чтобы потом через SQL сгруппировать по этому столбцу и вытащить наиболее часто встречаемое значение.

Функция write_db(), поместил её в другой модуль database. Из названия понятно, что её назначение записать датафрейм в базу данных. Куда записывается, определяется строкой:
```
connection_string = "postgresql://dmitriy:123@localhost:5432/hh"
```
В ней устанавливаем соединение с базой данных hh пользователем dmitriy с паролем '123'.

У вас скорее всего таких настроек не будет, то если захотите выполнить main.py, то вам нужно будет или закомментировать строку: database.write_db(df) или в выше приведённой строке свои настройки вписать.

Функция write_html размещена в модуле to_html. Служит для записи датафрейма в веб-страницу. Сначала я хотел записать в csv  файл, но  его неудобно читать. Потом записывал в xlsx, уже лучше, но подумал, что раз текст описания содержит html теги, то удобнее всего изучать вакансии в веб-формате.

**Скрипт skills.ru**
<details> <summary>Код skills.py</summary>

```python
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
```
</details>

Этот скрипт в отличии от файлов database.py и html.py выполняется отдельно от main.py, командой: python3 skills.py (в Linux).
Нужен для исследования по востребованности знаний для аналитика данных. 

В первоначальном варианте реализовал скрипт используя API сайта. В итоге получал например для mariadb или sqlite количество вакансий больше 200, когда всего вакансий примерно 270. Явная пурга. Связано это с тем, что когда api не находит вакансии, то в data['found'] подсовывает все похожие вакансии. Был вариант снова использовать full_description, но мне показалось проще парсить страницу поиска, вытаскивать из неё определенный веб-элемент, из этого элемента вытаскивать число найденных вакансий. К счастью не пришлось использовать selenium, не люблю эту библиотеку. 

Ключевые слова собрал в список key_skills. По каждому слову выполняю запрос, получаю в ответ веб-страницу (не json при использовании api). counter - искомый веб-элемент страницы. Вытаскиваю число - количество вакансий. Записываю данные в список statistik. Этот список записываю в файл key_words_ .csv . Всё на мой взгляд очень просто.

В принципе этого файла достаточно, чтобы сделать определённые выводы. Но решил дополнительно сделать из него дашборд.

**Создание дашборда**

Файл key_words .csv поместил в базу данных ClickHouse. В Superset на основе этой таблицы создал датасет, чарты и дашборд.

![Дашборд](статистика-по-ключевым-словам.jpg)

Дополнительно в Excel построил диаграммы, как в дашборде из Superset. Сохранил в файл key_words.xlsx



