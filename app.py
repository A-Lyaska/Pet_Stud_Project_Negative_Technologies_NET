from flask import Flask, jsonify, render_template, url_for, request, redirect
import database_manager

app = Flask(__name__)

logged = False
user = None

def logged_control(function_to_decorate):
    def wrapper(*args, **kwargs):
        if logged:
            return function_to_decorate(*args, **kwargs)
        else:
            return redirect('/auth')
    wrapper.__name__ = function_to_decorate.__name__
    return wrapper

@app.route('/')
def index():
    if logged:
        return render_template('index.html')
    else:
        return redirect('/auth')
    
@app.route('/main')
def main():
    if logged:
        return render_template('main.html', role=user.role)
    else:
        return redirect('/auth')

@app.route('/auth', methods=['POST', 'GET'])
def auth():
    global logged, user
    if request.method == 'POST':
        login = request.form['floatingInput']
        password = request.form['floatingPassword']
        if not database_manager.auth(login, password):
            return redirect('/auth')
        for e in database_manager.list_employees:
            if e.login == login:
                user = e
        logged = True
        return redirect('/')
    else:
        logged = False
        return render_template('auth.html')


@app.route('/customers', methods=['GET', 'POST'])
@logged_control
def view_customers():
    sort_by = request.args.get('sort_by', 'customer_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if request.method == 'POST':
        email = request.form['email']
        customers = database_manager.search_customers_by_email(email)
    else:
        customers = database_manager.get_customers(sort_by=sort_by)

    total = len(customers)
    customers_paginated = customers[(page-1)*per_page:page*per_page]

    return render_template('customers.html', customers=customers_paginated, sort_by=sort_by, page=page, per_page=per_page, total=total)




@app.route('/customers/change_status/<int:customer_id>/<string:new_status>', methods=['POST'])
@logged_control
def change_customer_status(customer_id, new_status):
    success = database_manager.change_customer_status(customer_id, new_status)
    if success:
        return redirect(url_for('view_customers'))
    else:
        return "Ошибка при изменении статуса клиента", 500


@app.route('/customers/new', methods=['POST', 'GET'])
@logged_control
def add_new_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address_id = request.form['address_id']
        created_at = request.form['created_at']
        tariff_id = request.form['tariff_id']
        success = database_manager.add_new_customer(first_name, last_name, email, phone, address_id, created_at, tariff_id)
        if success:
            return """
                <script>
                    alert('УСПЕШНО');
                    window.location.href = '/customers/new';
                </script>
            """
        else:
            return "Ошибка при добавлении нового клиента", 500
    return render_template('add_new_customer.html')

@app.route('/customer_statistics')
@logged_control
def customer_statistics():
    customer_stats = database_manager.get_customer_statistics()
    return render_template('customer_statistics.html', customer_stats=customer_stats)


@app.route('/equipment')
@logged_control
def all_equipment():
    equipment = database_manager.get_equipment_with_customers()
    return render_template('equipment.html', equipment=equipment)


@app.route('/accounts')
@logged_control
def all_accounts():
    accounts = database_manager.get_accounts_with_tariffs()
    return render_template('accounts.html', accounts=accounts)


@app.route('/accounts/<id>')
@logged_control
def account(id):
    account = database_manager.Account(database_manager.request('SELECT * FROM admin.Accounts WHERE account_id=%s', id))
    return render_template('account.html', account=account)


@app.route('/support', methods=['GET', 'POST'])
@logged_control
def view_support_requests():
    sort_by = request.args.get('sort_by', 'request_id')
    support_requests = database_manager.get_support_requests(sort_by=sort_by)
    return render_template('support_requests.html', support_requests=support_requests, sort_by=sort_by)

@app.route('/support/change_state/<int:request_id>/<string:new_state>', methods=['POST'])
@logged_control
def change_support_state(request_id, new_state):
    success = database_manager.change_support_state(request_id, new_state)
    if success:
        return redirect(url_for('view_support_requests'))
    else:
        return "Ошибка при изменении статуса заявки", 500

@app.route('/employees', methods=['GET'])
@logged_control
def view_employees():
    sort_by = request.args.get('sort_by', 'employee_id')
    employees = database_manager.get_employees(sort_by=sort_by)
    return render_template('employees.html', employees=employees, sort_by=sort_by)

@app.route('/payment', methods=['GET', 'POST'])
@logged_control
def manual_payment():
    if request.method == 'POST':
        account_id = request.form['account_id']
        amount = request.form['amount']
        payment_date = request.form['payment_date']
        success = database_manager.add_payment(account_id, amount, payment_date)
        if success:
            return """
                <script>
                    alert('Платеж успешно добавлен');
                    window.location.href = '/payment';
                </script>
            """
        else:
            return "Ошибка при добавлении платежа", 500
    accounts = database_manager.get_accounts()
    return render_template('manual_payment.html', accounts=accounts)

@app.route('/tariffs/new', methods=['GET', 'POST'])
@logged_control
def add_new_tariff_view():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        success = database_manager.add_new_tariff(name, description, price)
        if success:
            return """
                <script>
                    alert('Тариф успешно добавлен');
                    window.location.href = '/tariffs/new';
                </script>
            """
        else:
            return "Ошибка при добавлении нового тарифа", 500
    return render_template('add_new_tariff.html')



if __name__ == '__main__':
    app.run(debug=True)

