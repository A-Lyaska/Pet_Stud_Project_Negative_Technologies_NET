import random

sql_insert_template = "INSERT INTO admin.Accounts (customer_id, tariff_id, balance, created_at) VALUES\n"
values = []

for i in range(1, 601):
    tariff_id = random.randint(1, 3)
    balance = round(random.uniform(0, 1000), 2)
    created_at = f"'2024-{i % 12 + 1:02d}-01 10:00:00'"
    values.append(f"({i}, {tariff_id}, {balance}, {created_at})")

sql_insert_template += ",\n".join(values) + ";"

with open("insert_accounts.sql", "w", encoding="utf-8") as file:
    file.write(sql_insert_template)
