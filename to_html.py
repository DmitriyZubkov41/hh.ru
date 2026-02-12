from datetime import date


def write_html(df):
    """
       Отформатировать df и записать его в веб-страницу
    """
    #Сначала сформируем столбец column1 из других столбцов
    df['column1'] = df.apply(
        lambda row: (
            f"Опубликовано: {row.get('published_at', '').strftime('%d.%m.%Y')}"
            f"\nОпыт: {row.get('experience', '')}"
            f"\nРоли: {row.get('professional_roles', 'нет ролей')}"
            f"\nВакансия: {row.get('name', '')}"
            f"\nКомпания: {row.get('employer', '')}"
            f"\nЗарплата от {row.get('salary_from', '')} до {row.get('salary_to', '')}"
            f"\n{row.get('schedule', '')}"
            f"\nСсылка:\n<a href=\"{row.get('url', '')}\">{row.get('url', '')}</a>"
        ),
        axis=1
    )

    # Теперь столбец column2 из столбцов: full_description и key_skills
    df['column2'] = df.apply(lambda row: row['full_description'] + '<br>Скилы: ' + row['key_skills'], axis=1)

    html_df = df[['column1', 'column2']].copy()
    #html_df.to_csv(f'hh_{date.today().strftime("%d.%m.%Y")}.csv', index=False)
    print(html_df.shape)

    #преобразуем символ '\n' в html_df в тег br или p
    html_df['column1'] = html_df['column1'].apply(lambda cell: cell.replace('\n', '<p>'))
    html_df['column2'] = html_df['column2'].apply(lambda cell: cell.replace('<p>', ''))
    html_df['column2'] = html_df['column2'].apply(lambda cell: cell.replace('</p>', ''))
    html_df['column2'] = html_df['column2'].apply(lambda cell: cell.replace('<br /><br />', '<br>'))


    #Запись html_df в html файл
    html_table = html_df.to_html(
        index=False, 
        escape=False, 
        classes='vacancy-table'
    )

    # Формат таблицы
    full_html = f'''<html><head><title>Вакансии</title>
        <style>
            .vacancy-table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed; /* Фиксированная ширины */
                cellpadding: 10
                border: 1
            }}
            /* Первый столбец (20%) */
            .vacancy-table th:first-child,
            .vacancy-table td:first-child {{
                width: 20%;
                background-color: #f8f9fa; /* Легкий фон для визуального разделения */
                vertical-align: top;
            }}
            /* Второй столбец (80%) */
            .vacancy-table th:last-child,
            .vacancy-table td:last-child {{
                width: 80%;
                white-space: pre-line; /* Сохраняет переносы строк */
            }}
            /* Чередование строк для лучшей читаемости */
            .vacancy-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            /* Эффект при наведении */
            .vacancy-table tr:hover {{
                background-color: #e8f4f8;
            }}
        </style>
    </head>
    <body>
    {html_table}
    </body></html>'''


    with open(f'vacancies_{date.today()}.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
