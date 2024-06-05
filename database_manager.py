import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(dbname='negative_technologies', user='postgres', password='', host='localhost')
cursor = conn.cursor()

def request(sql_query, *params, count_output=1, fetch=True):
    try:
        cursor.execute(sql_query, params)
        if fetch:
            if count_output == 1:
                return cursor.fetchone()
            elif count_output == 0:
                return cursor.fetchall()
            else:
                return cursor.fetchmany(count_output)
        else:
            conn.commit()
            return None
    except Exception as e:
        print(f'Error executing request: {e}')
        conn.rollback()
        raise


def auth(login, password):
    try:
        login_result = request('SELECT login FROM admin.Employees WHERE login=%s', login)
        if login_result is None:
            return False
        password_result = request('SELECT * FROM admin.Employees WHERE password = crypt(%s, password)', password)
        return password_result is not None
    except Exception as e:
        print(f'Error during authentication: {e}')
        return False


def add_new_customer(first_name, last_name, email, phone, address_id, created_at, tariff_id):
    try:
        cursor.execute(
            'CALL admin.add_new_customer(%s, %s, %s, %s, %s, %s, %s)',
            (first_name, last_name, email, phone, address_id, created_at, tariff_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f'Error adding new customer: {e}')
        conn.rollback()
        return False

def get_equipment_with_customers():
    try:
        equipment_data = request('SELECT * FROM admin.view_equipment_with_customers', count_output=0)
        equipment_list = []
        for item in equipment_data:
            equipment_list.append({
                'equipment_id': item[0],
                'equipment_name': item[1],
                'description': item[2],
                'customer_fullname': f"{item[3]} {item[4]}",
                'installed_at': item[5]
            })
        return equipment_list
    except Exception as e:
        print(f'Error retrieving equipment data: {e}')
        return []
    
def get_accounts_with_tariffs():
    try:
        accounts_data = request('SELECT * FROM admin.view_accounts_with_tariffs', count_output=0)
        accounts_list = []
        for item in accounts_data:
            accounts_list.append({
                'account_id': item[0],
                'customer_fullname': f"{item[1]} {item[2]}",
                'tariff_name': item[3],
                'balance': item[4],
                'created_at': item[5]
            })
        return accounts_list
    except Exception as e:
        print(f'Error retrieving accounts data: {e}')
        return []

def get_customer_statistics():
    try:
        customer_stats_data = request('SELECT * FROM admin.view_customer_statistics', count_output=0)
        customer_stats_list = []
        for item in customer_stats_data:
            customer_stats_list.append({
                'customer_id': item[0],
                'first_name': item[1],
                'last_name': item[2],
                'email': item[3],
                'phone': item[4],
                'tariff_name': item[5],
                'balance': item[6]
            })
        return customer_stats_list
    except Exception as e:
        print(f'Error retrieving customer statistics: {e}')
        return []

def get_support_requests(sort_by='request_id'):
    try:
        if sort_by == 'customer.fullname':
            sort_by_clause = "(SELECT first_name || ' ' || last_name FROM Customers WHERE Customers.customer_id = SupportRequests.customer_id)"
        else:
            sort_by_clause = sort_by
        results = request(f'SELECT * FROM SupportRequests ORDER BY {sort_by_clause}', count_output=10)
        return [SupportRequest(s) for s in results]
    except Exception as e:
        print(f'Error fetching support requests: {e}')
        return []
    
def change_support_state(request_id, new_state):
    try:
        request('UPDATE SupportRequests SET state=%s WHERE request_id=%s', new_state, request_id, fetch=False)
        return True
    except Exception as e:
        print(f'Error changing support status: {e}')
        return False
    
def get_customers(sort_by='customer_id'):
    try:
        if sort_by == 'fullname':
            sort_by_clause = "first_name, last_name"
        else:
            sort_by_clause = sort_by
        results = request(f'SELECT * FROM Customers ORDER BY {sort_by_clause}', count_output=0)
        return [Customer(c) for c in results]
    except Exception as e:
        print(f'Error fetching customers: {e}')
        return []

def change_customer_status(customer_id, new_status):
    try:
        request('UPDATE Customers SET status=%s WHERE customer_id=%s', new_status, customer_id, fetch=False)
        return True
    except Exception as e:
        print(f'Error changing customer status: {e}')
        return False

def search_customers_by_email(email):
    try:
        results = request('SELECT * FROM Customers WHERE email ILIKE %s', f'%{email}%', count_output=10)
        return [Customer(c) for c in results]
    except Exception as e:
        print(f'Error searching customers by email: {e}')
        return []

def get_employees(sort_by='employee_id'):
    try:
        if sort_by == 'fullname':
            sort_by_clause = "first_name, last_name"
        else:
            sort_by_clause = sort_by
        results = request(f'SELECT * FROM admin.Employees ORDER BY {sort_by_clause}', count_output=10)
        return [Employee(e) for e in results]
    except Exception as e:
        print(f'Error fetching employees: {e}')
        return []

def add_payment(account_id, amount, payment_date):
    try:
        cursor.execute(
            'SELECT admin.add_payment(%s, %s, %s)',
            (account_id, amount, payment_date)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f'Error adding payment: {e}')
        conn.rollback()
        return False

def get_accounts():
    try:
        accounts_data = request('SELECT account_id, customer_id, tariff_id, balance, created_at FROM admin.Accounts', count_output=0)
        accounts_list = []
        for item in accounts_data:
            accounts_list.append({
                'account_id': item[0],
                'customer': Customer(request('SELECT * FROM Customers WHERE customer_id=%s', item[1])),
                'tariff': request('SELECT * FROM Tariffs WHERE tariff_id=%s', item[2]),
                'balance': item[3],
                'created_at': item[4]
            })
        return accounts_list
    except Exception as e:
        print(f'Error retrieving accounts data: {e}')
        return []

def add_new_tariff(name, description, price):
    query = "INSERT INTO Tariffs (name, description, price) VALUES (%s, %s, %s)"
    params = (name, description, price)
    try:
        request(query, *params, fetch=False)
        return True
    except Exception as e:
        print(f"Error adding new tariff: {e}")
        return False


class Address:
    def __init__(self, t):
        self.id = t[0]
        self.city_id = t[1]
        self.street = t[2]
        self.house_number = t[3]
        self.apartment_number = t[4]
        self.city = request('SELECT name FROM Cities WHERE city_id=%s', str(self.city_id))[0]
        self.fulladdress = ', '.join([self.city, self.street, self.house_number])
        if self.apartment_number:
            self.fulladdress += ', кв. ' + self.apartment_number

class Customer:
    def __init__(self, t):
        self.customer_id = t[0]
        self.first_name = t[1]
        self.last_name = t[2]
        self.fullname = f"{self.first_name} {self.last_name}"
        self.email = t[3]
        self.phone = t[4]
        self.address = Address(request('SELECT * FROM admin.Addresses WHERE address_id=%s', t[5])).fulladdress
        self.created_at = t[6]
        self.status = t[7] if len(t) > 7 else 'active'

def sort_customers(customer):
    return customer.fullname

list_customers = [Customer(c) for c in request('SELECT * FROM Customers', count_output=10)]
list_customers.sort(key=sort_customers)

class Employee:
    def __init__(self, t):
        self.id = t[0]
        self.first_name = t[1]
        self.last_name = t[2]
        self.fullname = f"{self.first_name} {self.last_name}"
        self.email = t[3]
        self.phone = t[4]
        self.login = t[5]
        self.password = t[6]
        self.role = t[7]
        

list_employees = [Employee(e) for e in request('SELECT * FROM admin.Employees', count_output=10)]

class Account:
    def __init__(self, t):
        self.id = t[0]
        self.customer_id = t[1]
        self.tariff_id = t[2]
        self.balance = t[3]
        self.created_at = t[4]
        self.customer = Customer(request('SELECT * FROM Customers WHERE customer_id=%s', self.customer_id))
        self.tariff = request('SELECT * FROM Tariffs WHERE tariff_id=%s', self.tariff_id)

def sort_accounts(account):
    return account.created_at

list_accounts = [Account(a) for a in request('SELECT * FROM admin.Accounts', count_output=10)]
list_accounts.sort(key=sort_accounts)


class SupportRequest:
    def __init__(self, t):
        self.request_id = t[0]
        self.customer_id = t[1]
        self.issue = t[2]
        self.state = t[3]
        self.created_at = t[4]
        self.updated_at = t[5]
        self.customer = Customer(request('SELECT * FROM Customers WHERE customer_id=%s', self.customer_id))

list_support_requests = [SupportRequest(s) for s in request('SELECT * FROM SupportRequests', count_output=10)]

class Equipment:
    def __init__(self, t):
        self.id = t[0]
        self.name = t[1]
        self.description = t[2]
        self.customer_id = t[3]
        self.installed_at = t[4]
        self.customer = Customer(request('SELECT * FROM Customers WHERE customer_id=%s', self.customer_id))

def sort_equipment(equipment):
    return equipment.installed_at

list_equipment = [Equipment(e) for e in request('SELECT * FROM Equipment', count_output=10)]
list_equipment.sort(key=sort_equipment)
