import random

first_names = [
    "Ivan", "Petr", "Sergey", "Alexey", "Nikolay", "Dmitry", "Maxim", "Andrey", "Vladimir", "Mikhail", "Anna", 
    "Maria", "Ekaterina", "Olga", "Natalya", "Elena", "Anastasia", "Yulia", "Tatyana", "Svetlana", "Irina", "Victoria",
    "Alexandra", "Darya", "Ksenia", "Veronika", "Polina", "Margarita", "Nadezhda", "Lyubov", "Zoya", "Sofia", "Elizaveta"
]
last_names = [
    "Ivanov", "Petrov", "Sergeev", "Alekseev", "Nikolaev", "Dmitriev", "Maximov", "Andreev", "Vladimirov", "Mikhailov", 
    "Kuznetsova", "Smirnova", "Popova", "Lebedeva", "Kozlova", "Novikova", "Morozova", "Pavlova", "Sokolova", "Volkova",
    "Zaitseva", "Borisova", "Frolova", "Guseva", "Vinogradova", "Tikhomirova", "Belova", "Komarova", "Orlova", "Kiseleva"
]
domains = ["example.com", "test.com", "email.com", "mail.com", "demo.com"]

def generate_random_phone():
    return f"89{random.randint(100000000, 999999999)}"

def generate_random_email(first_name, last_name, i, j):
    domain = random.choice(domains)
    return f"{first_name.lower()}.{last_name.lower()}.{i}{j}@{domain}"

sql_insert_template = "INSERT INTO Customers (first_name, last_name, email, phone, address_id, created_at) VALUES\n"
values = []

for i in range(1, 61):
    for j in range(10):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = generate_random_email(first_name, last_name, i, j)
        phone = generate_random_phone()
        address_id = (j + 1) % 20 + 1
        created_at = f"'2024-{(j+i) % 12 + 1:02d}-01 10:00:00'"
        values.append(f"('{first_name}', '{last_name}', '{email}', '{phone}', {address_id}, {created_at})")

sql_insert_template += ",\n".join(values) + ";"

with open("insert_customers.sql", "w", encoding="utf-8") as file:
    file.write(sql_insert_template)
