from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Kkyle0p0p00pp@",
    "database": "gmvcc_db"
}

def fetch_all(table_name):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    if request.method == 'POST':
        data = request.json
        full_name = f"{data['fname']} {data['mname']} {data['lname']}".strip()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "INSERT INTO students (lrn, program, full_name, birthdate, gender, address, contact_number) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (data['lrn'], data['program'], full_name, data['bday'], data['gender'], data['address'], data['contact']))
        conn.commit(); conn.close()
        return jsonify({"message": "Student saved!"}), 201
    return fetch_all("students")

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"})

@app.route('/api/programs', methods=['GET', 'POST'])
def handle_programs():
    if request.method == 'POST':
        data = request.json
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO programs (name, description, type) VALUES (%s, %s, %s)", (data['name'], data['desc'], data['type']))
        conn.commit(); conn.close()
        return jsonify({"message": "Program saved!"}), 201
    return fetch_all("programs")

@app.route('/api/subjects', methods=['GET', 'POST'])
def handle_subjects():
    if request.method == 'POST':
        data = request.json
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (code, title, units) VALUES (%s, %s, %s)", (data['code'], data['title'], data['units']))
        conn.commit(); conn.close()
        return jsonify({"message": "Subject saved!"}), 201
    return fetch_all("subjects")

@app.route('/api/instructors', methods=['GET', 'POST'])
def handle_instructors():
    if request.method == 'POST':
        data = request.json
        full_name = f"{data['fname']} {data['mname']} {data['lname']}".strip()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO instructors (full_name, department, contact) VALUES (%s, %s, %s)", (full_name, data['dept'], data['contact']))
        conn.commit(); conn.close()
        return jsonify({"message": "Instructor saved!"}), 201
    return fetch_all("instructors")

@app.route('/api/classes', methods=['GET', 'POST'])
def handle_classes():
    if request.method == 'POST':
        data = request.json
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = """INSERT INTO classes (subject_name, section, room, semester, school_year, schedule, instructor_name) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (data['subject'], data['section'], data['room'], 
                  data['semester'], data['school_year'], data['schedule'], data['instructor'])
        cursor.execute(sql, values)
        conn.commit(); conn.close()
        return jsonify({"message": "Class saved!"}), 201
    return fetch_all("classes")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    if username == "admin" and password == "123":
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students 
        SET full_name = %s, program = %s
        WHERE id = %s
    """, (data['full_name'], data['program'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

@app.route('/api/programs/<int:id>', methods=['DELETE'])
def delete_program(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM programs WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route('/api/subjects/<int:id>', methods=['DELETE'])
def delete_subject(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})
@app.route('/api/subjects/<int:id>', methods=['PUT'])
def update_subject(id):
    data = request.json

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE subjects 
        SET code=%s, title=%s, units=%s
        WHERE id=%s
    """, (data['code'], data['title'], data['units'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

@app.route('/api/instructors/<int:id>', methods=['DELETE'])
def delete_instructor(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instructors WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route('/api/instructors/<int:id>', methods=['PUT'])
def update_instructor(id):
    data = request.json

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE instructors 
        SET full_name=%s, department=%s, contact=%s
        WHERE id=%s
    """, (data['full_name'], data['department'], data['contact'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

@app.route('/api/classes/<int:id>', methods=['DELETE'])
def delete_class(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM classes WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route('/api/classes/<int:id>', methods=['PUT'])
def update_class(id):
    data = request.json

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE classes 
        SET section=%s, room=%s, schedule=%s
        WHERE id=%s
    """, (data['section'], data['room'], data['schedule'], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)