import random

equipment_names = [
    "Роутер", "Модем", "Антенна", "Коммутатор", "Сервер", "Маршрутизатор", "Хаб", "Кабель", "Провод", "Усилитель сигнала",
    "Контроллер", "Сплиттер", "Модуль", "Спутниковая антенна", "Маршрутизатор Wi-Fi", "Приемник", "Микротик", "Мост",
    "Конвертер", "Пассивное оборудование"
]
equipment_descriptions = [
    "Модель X", "Модель Y", "Модель Z", "Сетевое устройство", "Высокоскоростной", "Для дома", "Для офиса", "Компактный",
    "Мощный", "Беспроводной", "Современный", "Универсальный", "Профессиональный", "Экономичный", "Эргономичный", "Надежный",
    "Инновационный", "Супербыстрый", "Сверхнадежный", "Многофункциональный"
]

sql_insert_template = "INSERT INTO Equipment (name, description, customer_id, installed_at) VALUES\n"
values = []

for i in range(1, 601):
    equipment_name = random.choice(equipment_names)
    equipment_description = random.choice(equipment_descriptions)
    customer_id = i
    installed_at = f"'2024-{i % 12 + 1:02d}-01 10:00:00'"
    values.append(f"('{equipment_name}', '{equipment_description}', {customer_id}, {installed_at})")

sql_insert_template += ",\n".join(values) + ";"

with open("insert_equipment.sql", "w", encoding="utf-8") as file:
    file.write(sql_insert_template)
