CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lrn VARCHAR(20) UNIQUE NOT NULL,
    program VARCHAR(100),
    full_name VARCHAR(200),
    birthdate DATE,
    gender VARCHAR(10),
    address TEXT,
    contact_number VARCHAR(15)
);

CREATE TABLE programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    type VARCHAR(50)
);

CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE,
    title VARCHAR(200),
    units INT
);

CREATE TABLE instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(200),
    department VARCHAR(100),
    contact VARCHAR(20)
);

CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(200),
    section VARCHAR(50),
    room VARCHAR(50),
    semester VARCHAR(50),
    school_year VARCHAR(50),
    schedule VARCHAR(100),
    instructor_name VARCHAR(200)
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);