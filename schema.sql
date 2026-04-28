CREATE DATABASE IF NOT EXISTS enrollment_system;
USE enrollment_system;

CREATE TABLE IF NOT EXISTS guardian (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    middle_name VARCHAR(80),
    last_name VARCHAR(80) NOT NULL,
    contact_number VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS program (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_name VARCHAR(120) NOT NULL,
    major VARCHAR(120),
    UNIQUE KEY uq_program_major (program_name, major)
);

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
    program_id INT,
    guardian_id INT,
    relationship_type VARCHAR(60),
    CONSTRAINT fk_student_program
        FOREIGN KEY (program_id) REFERENCES program(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_student_guardian
        FOREIGN KEY (guardian_id) REFERENCES guardian(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS relationship (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    guardian_id INT NOT NULL,
    relationship_type VARCHAR(60) NOT NULL,
    UNIQUE KEY uq_student_guardian_relationship (student_id, guardian_id, relationship_type),
    CONSTRAINT fk_relationship_student
        FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_relationship_guardian
        FOREIGN KEY (guardian_id) REFERENCES guardian(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS subject (
    subject_code VARCHAR(30) PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    units INT NOT NULL,
    prerequisite_code VARCHAR(30),
    CONSTRAINT fk_subject_prerequisite
        FOREIGN KEY (prerequisite_code) REFERENCES subject(subject_code)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS section (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS instructor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    department VARCHAR(120),
    contact_number VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day VARCHAR(30) NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS class_offering (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room VARCHAR(50) NOT NULL,
    section_id INT,
    subject_code VARCHAR(30),
    schedule_id INT,
    instructor_id INT,
    school_year VARCHAR(20) NOT NULL,
    sem VARCHAR(20) NOT NULL,
    CONSTRAINT fk_class_section
        FOREIGN KEY (section_id) REFERENCES section(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_class_subject
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_class_schedule
        FOREIGN KEY (schedule_id) REFERENCES schedule(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_class_instructor
        FOREIGN KEY (instructor_id) REFERENCES instructor(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS class_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    schedule_id INT NOT NULL,
    UNIQUE KEY uq_class_schedule (class_id, schedule_id),
    CONSTRAINT fk_class_schedule_class
        FOREIGN KEY (class_id) REFERENCES class_offering(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_class_schedule_schedule
        FOREIGN KEY (schedule_id) REFERENCES schedule(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS enrollment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    enrollment_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_class_enrollment (student_id, class_id),
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_class
        FOREIGN KEY (class_id) REFERENCES class_offering(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS program_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    program_id INT NOT NULL,
    school_year VARCHAR(20) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    status VARCHAR(40) NOT NULL,
    CONSTRAINT fk_program_history_student
        FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_program_history_program
        FOREIGN KEY (program_id) REFERENCES program(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS curriculum (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT NOT NULL,
    subject_code VARCHAR(30) NOT NULL,
    year_level VARCHAR(20) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    UNIQUE KEY uq_program_subject_term (program_id, subject_code, year_level, semester),
    CONSTRAINT fk_curriculum_program
        FOREIGN KEY (program_id) REFERENCES program(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_curriculum_subject
        FOREIGN KEY (subject_code) REFERENCES subject(subject_code)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_account (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO user_account (username, password)
VALUES ('admin', '123')
ON DUPLICATE KEY UPDATE username = username;
