from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/student_health'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secret key for security
db = SQLAlchemy(app)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255))
    temperature = db.Column(db.Float)
    blood_pressure = db.Column(db.String(20))
    other_details = db.Column(db.Text)

# Define the login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Static user credentials for demonstration purposes
static_username = 'admin'
static_password = 'password'

@app.route('/')
def index():
    query = text("SELECT * FROM health_data")
    records = db.session.execute(query)

    rows = records.fetchall()
    columns = records.keys()
    records_list = [dict(zip(columns, row)) for row in rows]

    return render_template('index.html', records=records_list)

@app.route('/add_record', methods=['POST'])
def add_record():
    if request.method == 'POST':
        student_name = request.form['student_name']
        temperature = float(request.form['temperature'])
        blood_pressure = request.form['blood_pressure']
        other_details = request.form['other_details']

        query = text(f"INSERT INTO health_data (student_name, temperature, blood_pressure, other_details) "
                     f"VALUES ('{student_name}', {temperature}, '{blood_pressure}', '{other_details}')")
        db.session.execute(query)
        db.session.commit()

        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the entered credentials match the static ones
        if username == static_username and password == static_password:
            session['username'] = username
            return redirect(url_for('admin_page'))
        else:
            return render_template('login.html', message='Invalid username or password')

    return render_template('login.html', message='')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/edit_record/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    # Fetch the record with the given id from the database
    record = HealthData.query.get(id)

    if request.method == 'POST':
        # Update the record with the new data from the form
        record.student_name = request.form['student_name']
        record.temperature = float(request.form['temperature'])
        record.blood_pressure = request.form['blood_pressure']
        record.other_details = request.form['other_details']

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('admin_page'))

    return render_template('edit_record.html', record=record)

@app.route('/delete_record/<int:id>')
def delete_record(id):
    # Logic to delete the record with the given id from the database
    record = HealthData.query.get(id)

    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect(url_for('admin_page'))


@app.route('/admin_page')
@login_required
def admin_page():
    # Fetch all records from the database
    records = HealthData.query.all()

    return render_template('admin_page.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
