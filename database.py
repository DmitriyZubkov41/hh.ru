import pandas as pd
from sqlalchemy import Integer, Text, String, DateTime, Float, create_engine, text


# Строка подключения к базе данных
# Для пользователя dmitriy:
connection_string = "postgresql://dmitriy:123@localhost:5432/hh"

# Создаем движок SQLAlchemy
engine = create_engine(connection_string)

def write_db(df):
    '''
    #Преобразуем столбцы с типом list в строки
    df['professional_roles'] = df['professional_roles'].apply(lambda cell: '; '.join([role.get('name', 'нет роли') for role in cell]))
    df['key_skills'] = df['key_skills'].apply(lambda cell: ', '.join(cell) if isinstance(cell, list) else cell)
    df['all_skills'] = df['all_skills'].apply(lambda cell: ', '.join(cell) if isinstance(cell, list) else cell)
    
    #Преобразуем published_at в тип date
    df['published_at'] = pd.to_datetime(df['published_at'])
    '''

    # Определяем типы данных для колонок
    dtype_mapping = {
        'id': Integer,
        'name': Text,
        'url': Text,
        'employer': Text,
        'area': String(100),
        'salary_from': Float,
        'salary_to': Float,
        'salary_currency': String(10),
        'published_at': Text,
        'experience': String(50),
        'schedule': String(50),
        'employment': String(50),
        'full_description': Text,
        'key_skills': Text,
        'all_skills': Text,
        'professional_roles': Text
    }


    
    # Сохраняем DataFrame в базу данных
    table_name = 'vacancies'
    
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False,
        dtype=dtype_mapping,
        chunksize=1000,
        method='multi'
    )
    
    print(f"DataFrame сохранен в таблицу '{table_name}'")
