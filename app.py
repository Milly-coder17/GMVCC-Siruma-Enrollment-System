from datetime import date, datetime, time, timedelta
from decimal import Decimal

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Kkyle0p0p00pp@",
    "database": "enrollment_system",
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def pick(data, *keys):
    for key in keys:
        if key in data:
            return data.get(key)
    return None

def optional(value):
    return None if value in ("", None) else value

def optional_int(value):
    value = optional(value)
    return int(value) if value is not None else None

def json_value(value):
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        seconds = int(value.total_seconds())
        return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
    if isinstance(value, Decimal):
        return float(value)
    return value

def json_rows(rows):
    return [{key: json_value(value) for key, value in row.items()} for row in rows]

def fetch_all(sql, params=()):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return json_rows(cursor.fetchall())
    finally:
        cursor.close()
        db.close()

def execute(sql, params=(), return_id=False):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        db.commit()
        return cursor.lastrowid if return_id else cursor.rowcount
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()
        db.close()

def db_error(error):
    if getattr(error, "errno", None) == 1062:
        return jsonify({"error": "Duplicate record. Please check unique fields."}), 409
    if getattr(error, "errno", None) in (1451, 1452):
        return jsonify({"error": "Related record is missing or still in use."}), 409
    return jsonify({"error": f"Database error: {error}"}), 500

def ensure_database():
    statements = [
        """
        CREATE TABLE IF NOT EXISTS guardian (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(80) NOT NULL,
            middle_name VARCHAR(80),
            last_name VARCHAR(80) NOT NULL,
            contact_number VARCHAR(30) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS program (
            id INT AUTO_INCREMENT PRIMARY KEY,
            program_name VARCHAR(120) NOT NULL,
            major VARCHAR(120),
            UNIQUE KEY uq_program_major (program_name, major)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS student (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            lrn VARCHAR(30) NOT NULL UNIQUE,
            first_name VARCHAR(80) NOT NULL,
            middle_name VARCHAR(80),
            last_name VARCHAR(80) NOT NULL,
            birthdate DATE,
            gender VARCHAR(20),
            address TEXT,
            contact_no VARCHAR(30),
            program_id INT NULL,
            guardian_id INT NULL,
            relationship_type VARCHAR(60) NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subject (
            subject_code VARCHAR(30) PRIMARY KEY,
            title VARCHAR(160) NOT NULL,
            units INT NOT NULL,
            prerequisite_code VARCHAR(30) NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS section (
            id INT AUTO_INCREMENT PRIMARY KEY,
            section_name VARCHAR(80) NOT NULL UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS instructor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(160) NOT NULL,
            department VARCHAR(120),
            contact_number VARCHAR(30)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS schedule (
            id INT AUTO_INCREMENT PRIMARY KEY,
            day VARCHAR(30) NOT NULL,
            time_start TIME NOT NULL,
            time_end TIME NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS class_offering (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room VARCHAR(50) NOT NULL,
            section_id INT NULL,
            subject_code VARCHAR(30) NULL,
            schedule_id INT NULL,
            instructor_id INT NULL,
            school_year VARCHAR(20) NOT NULL,
            sem VARCHAR(20) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS `relationship` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            guardian_id INT NOT NULL,
            relationship_type VARCHAR(60) NOT NULL,
            UNIQUE KEY uq_student_guardian_relationship (student_id, guardian_id, relationship_type)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS class_schedule (
            id INT AUTO_INCREMENT PRIMARY KEY,
            class_id INT NOT NULL,
            schedule_id INT NOT NULL,
            UNIQUE KEY uq_class_schedule (class_id, schedule_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS enrollment (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            class_id INT NOT NULL,
            enrollment_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_student_class_enrollment (student_id, class_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS program_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            program_id INT NOT NULL,
            school_year VARCHAR(20) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            status VARCHAR(40) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS curriculum (
            id INT AUTO_INCREMENT PRIMARY KEY,
            program_id INT NOT NULL,
            subject_code VARCHAR(30) NOT NULL,
            year_level VARCHAR(20) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            UNIQUE KEY uq_program_subject_term (program_id, subject_code, year_level, semester)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_account (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """,
    ]

    db = get_db()
    cursor = db.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)

        cursor.execute("SHOW COLUMNS FROM student LIKE 'program_id'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE student ADD COLUMN program_id INT NULL")
        cursor.execute("SHOW COLUMNS FROM student LIKE 'guardian_id'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE student ADD COLUMN guardian_id INT NULL")
        cursor.execute("SHOW COLUMNS FROM student LIKE 'relationship_type'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE student ADD COLUMN relationship_type VARCHAR(60) NULL")

        cursor.execute("SHOW COLUMNS FROM subject LIKE 'prerequisite_code'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE subject ADD COLUMN prerequisite_code VARCHAR(30) NULL")

        cursor.execute(
            """
            INSERT INTO user_account (username, password)
            VALUES ('admin', '123')
            ON DUPLICATE KEY UPDATE username = username
            """
        )
        cursor.execute(
            """
            INSERT IGNORE INTO `relationship` (student_id, guardian_id, relationship_type)
            SELECT student_id, guardian_id, COALESCE(NULLIF(relationship_type, ''), 'Guardian')
            FROM student
            WHERE guardian_id IS NOT NULL
            """
        )
        cursor.execute(
            """
            INSERT IGNORE INTO class_schedule (class_id, schedule_id)
            SELECT id, schedule_id
            FROM class_offering
            WHERE schedule_id IS NOT NULL
            """
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()
        db.close()

try:
    ensure_database()
except Error as error:
    print("Database startup check failed:", error)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        fetch_all("SELECT 1 AS ok")
        return jsonify({"status": "ok", "database": "connected"})
    except Error as error:
        return db_error(error)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        rows = fetch_all(
            "SELECT user_id, username FROM user_account WHERE username = %s AND password = %s",
            (data.get("username"), data.get("password")),
        )
        return jsonify({"success": bool(rows), "user": rows[0] if rows else None})
    except Error as error:
        return db_error(error)

@app.route("/api/students", methods=["GET", "POST"])
def students():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            if not pick(data, "LRN", "lrn") or not pick(data, "FirstName", "first_name") or not pick(data, "LastName", "last_name"):
                return jsonify({"error": "LRN, first name, and last name are required."}), 400
            guardian_id = optional_int(pick(data, "GuardianID", "guardian_id"))
            relationship_type = optional(pick(data, "RelationshipType", "relationship_type"))
            student_id = execute(
                """
                INSERT INTO student
                    (lrn, first_name, middle_name, last_name, birthdate, gender, address,
                     contact_no, program_id, guardian_id, relationship_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    pick(data, "LRN", "lrn"),
                    pick(data, "FirstName", "first_name"),
                    optional(pick(data, "MiddleName", "middle_name")),
                    pick(data, "LastName", "last_name"),
                    optional(pick(data, "Birthdate", "birthdate")),
                    optional(pick(data, "Gender", "gender")),
                    optional(pick(data, "Address", "address")),
                    optional(pick(data, "Contact", "contact_no")),
                    optional_int(pick(data, "ProgramID", "program_id")),
                    guardian_id,
                    relationship_type,
                ),
                True,
            )
            if guardian_id and relationship_type:
                execute(
                    "INSERT IGNORE INTO `relationship` (student_id, guardian_id, relationship_type) VALUES (%s, %s, %s)",
                    (student_id, guardian_id, relationship_type),
                )
            return jsonify({"message": "Student added", "student_id": student_id}), 201

        return jsonify(fetch_all(
            """
            SELECT s.student_id, s.lrn, s.first_name, s.middle_name, s.last_name, s.birthdate,
                   s.gender, s.address, s.contact_no, s.program_id, p.program_name, p.major,
                   s.guardian_id,
                   CONCAT_WS(' ', g.first_name, NULLIF(g.middle_name, ''), g.last_name) AS guardian_name,
                   s.relationship_type
            FROM student s
            LEFT JOIN program p ON p.id = s.program_id
            LEFT JOIN guardian g ON g.id = s.guardian_id
            ORDER BY s.student_id
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        data = request.get_json(silent=True) or {}
        guardian_id = optional_int(pick(data, "GuardianID", "guardian_id"))
        relationship_type = optional(pick(data, "RelationshipType", "relationship_type"))
        execute(
            """
            UPDATE student
            SET lrn = %s,
                first_name = %s,
                middle_name = %s,
                last_name = %s,
                birthdate = %s,
                gender = %s,
                address = %s,
                contact_no = %s,
                program_id = %s,
                guardian_id = %s,
                relationship_type = %s
            WHERE student_id = %s
            """,
            (
                pick(data, "LRN", "lrn"),
                pick(data, "FirstName", "first_name"),
                optional(pick(data, "MiddleName", "middle_name")),
                pick(data, "LastName", "last_name"),
                optional(pick(data, "Birthdate", "birthdate")),
                optional(pick(data, "Gender", "gender")),
                optional(pick(data, "Address", "address")),
                optional(pick(data, "Contact", "contact_no")),
                optional_int(pick(data, "ProgramID", "program_id")),
                guardian_id,
                relationship_type,
                student_id,
            ),
        )
        execute("DELETE FROM `relationship` WHERE student_id = %s", (student_id,))
        if guardian_id and relationship_type:
            execute(
                "INSERT IGNORE INTO `relationship` (student_id, guardian_id, relationship_type) VALUES (%s, %s, %s)",
                (student_id, guardian_id, relationship_type),
            )
        return jsonify({"message": "Student updated"})
    except Error as error:
        return db_error(error)


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        execute("DELETE FROM `relationship` WHERE student_id = %s", (student_id,))
        execute("DELETE FROM enrollment WHERE student_id = %s", (student_id,))
        execute("DELETE FROM program_history WHERE student_id = %s", (student_id,))
        execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        return jsonify({"message": "Student deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/guardians", methods=["GET", "POST"])
def guardians():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            guardian_id = execute(
                "INSERT INTO guardian (first_name, middle_name, last_name, contact_number) VALUES (%s, %s, %s, %s)",
                (
                    pick(data, "FirstName", "first_name"),
                    optional(pick(data, "MiddleName", "middle_name")),
                    pick(data, "LastName", "last_name"),
                    pick(data, "ContactNumber", "contact_number") or "",
                ),
                True,
            )
            return jsonify({"message": "Guardian added", "guardian_id": guardian_id}), 201
        return jsonify(fetch_all(
            "SELECT id AS guardian_id, first_name, middle_name, last_name, contact_number FROM guardian ORDER BY id"
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/guardians/<int:guardian_id>", methods=["DELETE"])
@app.route("/api/guardians/<int:guardian_id>", methods=["PUT"])
def update_guardian(guardian_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE guardian
            SET first_name = %s,
                middle_name = %s,
                last_name = %s,
                contact_number = %s
            WHERE id = %s
            """,
            (
                pick(data, "FirstName", "first_name"),
                optional(pick(data, "MiddleName", "middle_name")),
                pick(data, "LastName", "last_name"),
                pick(data, "ContactNumber", "contact_number") or "",
                guardian_id,
            ),
        )
        return jsonify({"message": "Guardian updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/guardians/<int:guardian_id>", methods=["DELETE"])
def delete_guardian(guardian_id):
    try:
        execute("DELETE FROM `relationship` WHERE guardian_id = %s", (guardian_id,))
        execute(
            "UPDATE student SET guardian_id = NULL, relationship_type = NULL WHERE guardian_id = %s",
            (guardian_id,),
        )
        execute("DELETE FROM guardian WHERE id = %s", (guardian_id,))
        return jsonify({"message": "Guardian deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/programs", methods=["GET", "POST"])
def programs():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            program_id = execute(
                "INSERT INTO program (program_name, major) VALUES (%s, %s)",
                (pick(data, "ProgramName", "program_name"), pick(data, "Major", "major") or ""),
                True,
            )
            return jsonify({"message": "Program added", "program_id": program_id}), 201
        return jsonify(fetch_all("SELECT id AS program_id, program_name, major FROM program ORDER BY program_name, major"))
    except Error as error:
        return db_error(error)

@app.route("/api/programs/<int:program_id>", methods=["DELETE"])
@app.route("/api/programs/<int:program_id>", methods=["PUT"])
def update_program(program_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            "UPDATE program SET program_name = %s, major = %s WHERE id = %s",
            (pick(data, "ProgramName", "program_name"), pick(data, "Major", "major") or "", program_id),
        )
        return jsonify({"message": "Program updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/programs/<int:program_id>", methods=["DELETE"])
def delete_program(program_id):
    try:
        execute("DELETE FROM curriculum WHERE program_id = %s", (program_id,))
        execute("DELETE FROM program_history WHERE program_id = %s", (program_id,))
        execute("UPDATE student SET program_id = NULL WHERE program_id = %s", (program_id,))
        execute("DELETE FROM program WHERE id = %s", (program_id,))
        return jsonify({"message": "Program deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/subjects", methods=["GET", "POST"])
def subjects():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            execute(
                "INSERT INTO subject (subject_code, title, units, prerequisite_code) VALUES (%s, %s, %s, %s)",
                (
                    pick(data, "SubjectCode", "subject_code"),
                    pick(data, "Title", "title"),
                    optional_int(pick(data, "Units", "units")),
                    optional(pick(data, "Prerequisite", "prerequisite_code")),
                ),
            )
            return jsonify({"message": "Subject added"}), 201
        return jsonify(fetch_all("SELECT subject_code, title, units, prerequisite_code FROM subject ORDER BY subject_code"))
    except Error as error:
        return db_error(error)

@app.route("/api/subjects/<subject_code>", methods=["DELETE"])
@app.route("/api/subjects/<subject_code>", methods=["PUT"])
def update_subject(subject_code):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE subject
            SET title = %s,
                units = %s,
                prerequisite_code = %s
            WHERE subject_code = %s
            """,
            (
                pick(data, "Title", "title"),
                optional_int(pick(data, "Units", "units")),
                optional(pick(data, "Prerequisite", "prerequisite_code")),
                subject_code,
            ),
        )
        return jsonify({"message": "Subject updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/subjects/<subject_code>", methods=["DELETE"])
def delete_subject(subject_code):
    try:
        execute("DELETE FROM curriculum WHERE subject_code = %s", (subject_code,))
        execute("UPDATE class_offering SET subject_code = NULL WHERE subject_code = %s", (subject_code,))
        execute("UPDATE subject SET prerequisite_code = NULL WHERE prerequisite_code = %s", (subject_code,))
        execute("DELETE FROM subject WHERE subject_code = %s", (subject_code,))
        return jsonify({"message": "Subject deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/sections", methods=["GET", "POST"])
def sections():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            section_id = execute(
                "INSERT INTO section (section_name) VALUES (%s)",
                (pick(data, "SectionName", "section_name"),),
                True,
            )
            return jsonify({"message": "Section added", "section_id": section_id}), 201
        return jsonify(fetch_all("SELECT id AS section_id, section_name FROM section ORDER BY section_name"))
    except Error as error:
        return db_error(error)

@app.route("/api/sections/<int:section_id>", methods=["DELETE"])
@app.route("/api/sections/<int:section_id>", methods=["PUT"])
def update_section(section_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            "UPDATE section SET section_name = %s WHERE id = %s",
            (pick(data, "SectionName", "section_name"), section_id),
        )
        return jsonify({"message": "Section updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/sections/<int:section_id>", methods=["DELETE"])
def delete_section(section_id):
    try:
        execute("UPDATE class_offering SET section_id = NULL WHERE section_id = %s", (section_id,))
        execute("DELETE FROM section WHERE id = %s", (section_id,))
        return jsonify({"message": "Section deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/instructors", methods=["GET", "POST"])
def instructors():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            instructor_id = execute(
                "INSERT INTO instructor (name, department, contact_number) VALUES (%s, %s, %s)",
                (pick(data, "Name", "name"), pick(data, "Department", "department") or "", pick(data, "ContactNumber", "contact_number") or ""),
                True,
            )
            return jsonify({"message": "Instructor added", "instructor_id": instructor_id}), 201
        return jsonify(fetch_all("SELECT id AS instructor_id, name, department, contact_number FROM instructor ORDER BY name"))
    except Error as error:
        return db_error(error)

@app.route("/api/instructors/<int:instructor_id>", methods=["DELETE"])
@app.route("/api/instructors/<int:instructor_id>", methods=["PUT"])
def update_instructor(instructor_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE instructor
            SET name = %s,
                department = %s,
                contact_number = %s
            WHERE id = %s
            """,
            (
                pick(data, "Name", "name"),
                pick(data, "Department", "department") or "",
                pick(data, "ContactNumber", "contact_number") or "",
                instructor_id,
            ),
        )
        return jsonify({"message": "Instructor updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/instructors/<int:instructor_id>", methods=["DELETE"])
def delete_instructor(instructor_id):
    try:
        execute("UPDATE class_offering SET instructor_id = NULL WHERE instructor_id = %s", (instructor_id,))
        execute("DELETE FROM instructor WHERE id = %s", (instructor_id,))
        return jsonify({"message": "Instructor deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/schedules", methods=["GET", "POST"])
def schedules():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            schedule_id = execute(
                "INSERT INTO schedule (day, time_start, time_end) VALUES (%s, %s, %s)",
                (pick(data, "Day", "day"), pick(data, "TimeStart", "time_start"), pick(data, "TimeEnd", "time_end")),
                True,
            )
            return jsonify({"message": "Schedule added", "schedule_id": schedule_id}), 201
        return jsonify(fetch_all("SELECT id AS schedule_id, day, time_start, time_end FROM schedule ORDER BY day, time_start"))
    except Error as error:
        return db_error(error)

@app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
@app.route("/api/schedules/<int:schedule_id>", methods=["PUT"])
def update_schedule(schedule_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE schedule
            SET day = %s,
                time_start = %s,
                time_end = %s
            WHERE id = %s
            """,
            (pick(data, "Day", "day"), pick(data, "TimeStart", "time_start"), pick(data, "TimeEnd", "time_end"), schedule_id),
        )
        return jsonify({"message": "Schedule updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    try:
        execute("DELETE FROM class_schedule WHERE schedule_id = %s", (schedule_id,))
        execute("UPDATE class_offering SET schedule_id = NULL WHERE schedule_id = %s", (schedule_id,))
        execute("DELETE FROM schedule WHERE id = %s", (schedule_id,))
        return jsonify({"message": "Schedule deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/class-offerings", methods=["GET", "POST"])
def class_offerings():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            schedule_id = optional_int(pick(data, "ScheduleID", "schedule_id"))
            class_id = execute(
                """
                INSERT INTO class_offering (room, section_id, subject_code, schedule_id, instructor_id, school_year, sem)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    pick(data, "Room", "room"),
                    optional_int(pick(data, "SectionID", "section_id")),
                    optional(pick(data, "SubjectCode", "subject_code")),
                    schedule_id,
                    optional_int(pick(data, "InstructorID", "instructor_id")),
                    pick(data, "SchoolYear", "school_year"),
                    pick(data, "Sem", "sem"),
                ),
                True,
            )
            if schedule_id:
                execute("INSERT IGNORE INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)", (class_id, schedule_id))
            return jsonify({"message": "Class offering added", "class_offering_id": class_id}), 201
        return jsonify(fetch_all(
            """
            SELECT co.id AS class_offering_id, co.room, co.section_id, sec.section_name,
                   co.subject_code, sub.title AS subject_title, co.schedule_id,
                   sch.day, sch.time_start, sch.time_end, co.instructor_id,
                   ins.name AS instructor_name, co.school_year, co.sem
            FROM class_offering co
            LEFT JOIN section sec ON sec.id = co.section_id
            LEFT JOIN subject sub ON sub.subject_code = co.subject_code
            LEFT JOIN schedule sch ON sch.id = co.schedule_id
            LEFT JOIN instructor ins ON ins.id = co.instructor_id
            ORDER BY co.id
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/class-offerings/<int:class_id>", methods=["DELETE"])
@app.route("/api/class-offerings/<int:class_id>", methods=["PUT"])
def update_class_offering(class_id):
    try:
        data = request.get_json(silent=True) or {}
        schedule_id = optional_int(pick(data, "ScheduleID", "schedule_id"))
        execute(
            """
            UPDATE class_offering
            SET room = %s,
                section_id = %s,
                subject_code = %s,
                schedule_id = %s,
                instructor_id = %s,
                school_year = %s,
                sem = %s
            WHERE id = %s
            """,
            (
                pick(data, "Room", "room"),
                optional_int(pick(data, "SectionID", "section_id")),
                optional(pick(data, "SubjectCode", "subject_code")),
                schedule_id,
                optional_int(pick(data, "InstructorID", "instructor_id")),
                pick(data, "SchoolYear", "school_year"),
                pick(data, "Sem", "sem"),
                class_id,
            ),
        )
        execute("DELETE FROM class_schedule WHERE class_id = %s", (class_id,))
        if schedule_id:
            execute("INSERT IGNORE INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)", (class_id, schedule_id))
        return jsonify({"message": "Class offering updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/class-offerings/<int:class_id>", methods=["DELETE"])
def delete_class_offering(class_id):
    try:
        execute("DELETE FROM class_schedule WHERE class_id = %s", (class_id,))
        execute("DELETE FROM enrollment WHERE class_id = %s", (class_id,))
        execute("DELETE FROM class_offering WHERE id = %s", (class_id,))
        return jsonify({"message": "Class offering deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/relationships", methods=["GET", "POST"])
def relationships():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            relationship_id = execute(
                "INSERT INTO `relationship` (student_id, guardian_id, relationship_type) VALUES (%s, %s, %s)",
                (optional_int(pick(data, "StudentID", "student_id")), optional_int(pick(data, "GuardianID", "guardian_id")), pick(data, "RelationshipType", "relationship_type")),
                True,
            )
            return jsonify({"message": "Relationship added", "relationship_id": relationship_id}), 201
        return jsonify(fetch_all(
            """
            SELECT r.id AS relationship_id, r.student_id,
                   CONCAT_WS(' ', s.first_name, NULLIF(s.middle_name, ''), s.last_name) AS student_name,
                   r.guardian_id,
                   CONCAT_WS(' ', g.first_name, NULLIF(g.middle_name, ''), g.last_name) AS guardian_name,
                   r.relationship_type
            FROM `relationship` r
            JOIN student s ON s.student_id = r.student_id
            JOIN guardian g ON g.id = r.guardian_id
            ORDER BY r.id
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/relationships/<int:relationship_id>", methods=["DELETE"])
@app.route("/api/relationships/<int:relationship_id>", methods=["PUT"])
def update_relationship(relationship_id):
    try:
        data = request.get_json(silent=True) or {}
        student_id = optional_int(pick(data, "StudentID", "student_id"))
        guardian_id = optional_int(pick(data, "GuardianID", "guardian_id"))
        relationship_type = pick(data, "RelationshipType", "relationship_type")
        execute(
            """
            UPDATE `relationship`
            SET student_id = %s,
                guardian_id = %s,
                relationship_type = %s
            WHERE id = %s
            """,
            (student_id, guardian_id, relationship_type, relationship_id),
        )
        execute(
            """
            UPDATE student
            SET guardian_id = %s,
                relationship_type = %s
            WHERE student_id = %s
            """,
            (guardian_id, relationship_type, student_id),
        )
        return jsonify({"message": "Relationship updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/relationships/<int:relationship_id>", methods=["DELETE"])
def delete_relationship(relationship_id):
    try:
        rows = fetch_all("SELECT student_id, guardian_id FROM `relationship` WHERE id = %s", (relationship_id,))
        if rows:
            execute(
                "UPDATE student SET guardian_id = NULL, relationship_type = NULL WHERE student_id = %s AND guardian_id = %s",
                (rows[0]["student_id"], rows[0]["guardian_id"]),
            )
        execute("DELETE FROM `relationship` WHERE id = %s", (relationship_id,))
        return jsonify({"message": "Relationship deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/enrollments", methods=["GET", "POST"])
def enrollments():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            enrollment_id = execute(
                "INSERT INTO enrollment (student_id, class_id) VALUES (%s, %s)",
                (optional_int(pick(data, "StudentID", "student_id")), optional_int(pick(data, "ClassID", "class_id"))),
                True,
            )
            return jsonify({"message": "Enrollment added", "enrollment_id": enrollment_id}), 201
        return jsonify(fetch_all(
            """
            SELECT e.id AS enrollment_id, e.student_id,
                   CONCAT_WS(' ', st.first_name, NULLIF(st.middle_name, ''), st.last_name) AS student_name,
                   e.class_id, co.room, co.subject_code, sub.title AS subject_title,
                   sec.section_name, ins.name AS instructor_name, co.school_year, co.sem,
                   e.enrollment_timestamp
            FROM enrollment e
            JOIN student st ON st.student_id = e.student_id
            JOIN class_offering co ON co.id = e.class_id
            LEFT JOIN subject sub ON sub.subject_code = co.subject_code
            LEFT JOIN section sec ON sec.id = co.section_id
            LEFT JOIN instructor ins ON ins.id = co.instructor_id
            ORDER BY e.id DESC
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/enrollments/<int:enrollment_id>", methods=["DELETE"])
@app.route("/api/enrollments/<int:enrollment_id>", methods=["PUT"])
def update_enrollment(enrollment_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            "UPDATE enrollment SET student_id = %s, class_id = %s WHERE id = %s",
            (optional_int(pick(data, "StudentID", "student_id")), optional_int(pick(data, "ClassID", "class_id")), enrollment_id),
        )
        return jsonify({"message": "Enrollment updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/enrollments/<int:enrollment_id>", methods=["DELETE"])
def delete_enrollment(enrollment_id):
    try:
        execute("DELETE FROM enrollment WHERE id = %s", (enrollment_id,))
        return jsonify({"message": "Enrollment deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/program-history", methods=["GET", "POST"])
def program_history():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            history_id = execute(
                "INSERT INTO program_history (student_id, program_id, school_year, semester, status) VALUES (%s, %s, %s, %s, %s)",
                (
                    optional_int(pick(data, "StudentID", "student_id")),
                    optional_int(pick(data, "ProgramID", "program_id")),
                    pick(data, "SchoolYear", "school_year"),
                    pick(data, "Semester", "semester"),
                    pick(data, "Status", "status"),
                ),
                True,
            )
            return jsonify({"message": "Program history added", "history_id": history_id}), 201
        return jsonify(fetch_all(
            """
            SELECT ph.id AS history_id, ph.student_id,
                   CONCAT_WS(' ', st.first_name, NULLIF(st.middle_name, ''), st.last_name) AS student_name,
                   ph.program_id, p.program_name, p.major, ph.school_year, ph.semester, ph.status
            FROM program_history ph
            JOIN student st ON st.student_id = ph.student_id
            JOIN program p ON p.id = ph.program_id
            ORDER BY ph.id DESC
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/program-history/<int:history_id>", methods=["DELETE"])
@app.route("/api/program-history/<int:history_id>", methods=["PUT"])
def update_program_history(history_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE program_history
            SET student_id = %s,
                program_id = %s,
                school_year = %s,
                semester = %s,
                status = %s
            WHERE id = %s
            """,
            (
                optional_int(pick(data, "StudentID", "student_id")),
                optional_int(pick(data, "ProgramID", "program_id")),
                pick(data, "SchoolYear", "school_year"),
                pick(data, "Semester", "semester"),
                pick(data, "Status", "status"),
                history_id,
            ),
        )
        return jsonify({"message": "Program history updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/program-history/<int:history_id>", methods=["DELETE"])
def delete_program_history(history_id):
    try:
        execute("DELETE FROM program_history WHERE id = %s", (history_id,))
        return jsonify({"message": "Program history deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/curriculums", methods=["GET", "POST"])
def curriculums():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            curriculum_id = execute(
                "INSERT INTO curriculum (program_id, subject_code, year_level, semester) VALUES (%s, %s, %s, %s)",
                (optional_int(pick(data, "ProgramID", "program_id")), pick(data, "SubjectCode", "subject_code"), pick(data, "YearLevel", "year_level"), pick(data, "Semester", "semester")),
                True,
            )
            return jsonify({"message": "Curriculum added", "curriculum_id": curriculum_id}), 201
        return jsonify(fetch_all(
            """
            SELECT c.id AS curriculum_id, c.program_id, p.program_name, p.major,
                   c.subject_code, sub.title AS subject_title, c.year_level, c.semester
            FROM curriculum c
            JOIN program p ON p.id = c.program_id
            JOIN subject sub ON sub.subject_code = c.subject_code
            ORDER BY p.program_name, c.year_level, c.semester, c.subject_code
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/curriculums/<int:curriculum_id>", methods=["DELETE"])
@app.route("/api/curriculums/<int:curriculum_id>", methods=["PUT"])
def update_curriculum(curriculum_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            """
            UPDATE curriculum
            SET program_id = %s,
                subject_code = %s,
                year_level = %s,
                semester = %s
            WHERE id = %s
            """,
            (
                optional_int(pick(data, "ProgramID", "program_id")),
                pick(data, "SubjectCode", "subject_code"),
                pick(data, "YearLevel", "year_level"),
                pick(data, "Semester", "semester"),
                curriculum_id,
            ),
        )
        return jsonify({"message": "Curriculum updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/curriculums/<int:curriculum_id>", methods=["DELETE"])
def delete_curriculum(curriculum_id):
    try:
        execute("DELETE FROM curriculum WHERE id = %s", (curriculum_id,))
        return jsonify({"message": "Curriculum deleted"})
    except Error as error:
        return db_error(error)

@app.route("/api/class-schedules", methods=["GET", "POST"])
def class_schedules():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            class_schedule_id = execute(
                "INSERT INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)",
                (optional_int(pick(data, "ClassID", "class_id")), optional_int(pick(data, "ScheduleID", "schedule_id"))),
                True,
            )
            return jsonify({"message": "Class schedule added", "class_schedule_id": class_schedule_id}), 201
        return jsonify(fetch_all(
            """
            SELECT cs.id AS class_schedule_id, cs.class_id, co.room, co.subject_code,
                   sub.title AS subject_title, sec.section_name, co.school_year, co.sem,
                   cs.schedule_id, sch.day, sch.time_start, sch.time_end
            FROM class_schedule cs
            JOIN class_offering co ON co.id = cs.class_id
            LEFT JOIN subject sub ON sub.subject_code = co.subject_code
            LEFT JOIN section sec ON sec.id = co.section_id
            JOIN schedule sch ON sch.id = cs.schedule_id
            ORDER BY cs.id DESC
            """
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/class-schedules/<int:class_schedule_id>", methods=["DELETE"])
@app.route("/api/class-schedules/<int:class_schedule_id>", methods=["PUT"])
def update_class_schedule(class_schedule_id):
    try:
        data = request.get_json(silent=True) or {}
        execute(
            "UPDATE class_schedule SET class_id = %s, schedule_id = %s WHERE id = %s",
            (optional_int(pick(data, "ClassID", "class_id")), optional_int(pick(data, "ScheduleID", "schedule_id")), class_schedule_id),
        )
        return jsonify({"message": "Class schedule updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/class-schedules/<int:class_schedule_id>", methods=["DELETE"])
def delete_class_schedule(class_schedule_id):
    try:
        execute("DELETE FROM class_schedule WHERE id = %s", (class_schedule_id,))
        return jsonify({"message": "Class schedule deleted"})
    except Error as error:
        return db_error(error)

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
