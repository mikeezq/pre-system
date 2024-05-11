import re
from docx import Document


def extract_pattern_from_docx(file_path):
    # Загрузка документа
    doc = Document(file_path)

    # Регулярное выражение для поиска паттерна
    pattern = r'\[\d+\]'

    # Проход по каждому параграфу в документе
    index = 0
    patterns = []
    for paragraph in doc.paragraphs:
        # Поиск всех совпадений в параграфе
        matches = re.findall(pattern, paragraph.text)
        # Вывод найденных совпадений
        for match in matches:
            if match not in patterns:
                index += 1
            print(f"{match} - [{index}]")
            patterns.append(match)


# Путь к файлу
file_path = '/Users/korn-m/Documents/diplom/docs/Корнилов_М_А_ВКР8_sem_v2.docx'

# Вызов функции
extract_pattern_from_docx(file_path)
