from datetime import date, datetime, time, timedelta
from decimal import Decimal
import os
import secrets

from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

ACTIVE_SESSIONS = {}
FRONTEND_FILES = {"index.html", "main.html", "LoginStyle.css", "MainStyle.css", "script.js"}
DEFAULT_STUDENT_PASSWORD = "123"
PROGRAM_SEEDS = (
    ("Bachelor of Science in Fisheries", ""),
    ("Bachelor of Science in Entrepreneurship", ""),
    ("Bachelor of Technical Vocational Teacher Education", "Automotive Technology"),
    ("Bachelor of Technical Vocational Teacher Education", "Computer Hardware Servicing"),
    ("Bachelor of Technical Vocational Teacher Education", "Heating, Ventilating, and Airconditioning Technology"),
)
SCHEDULE_SEEDS = (
    ("MW", "07:30", "09:00"),
    ("MW", "09:00", "10:30"),
    ("MW", "10:30", "12:00"),
    ("MW", "13:00", "14:30"),
    ("MW", "14:30", "16:00"),
    ("TTH", "07:30", "09:00"),
    ("TTH", "09:00", "10:30"),
    ("TTH", "10:30", "12:00"),
    ("TTH", "13:00", "14:30"),
    ("TTH", "14:30", "16:00"),
    ("TTHF", "08:00", "09:30"),
    ("TTHF", "09:30", "11:00"),
    ("TTHF", "13:00", "14:30"),
    ("TTHF", "14:30", "16:00"),
    ("F", "08:00", "11:00"),
    ("F", "13:00", "16:00"),
    ("S", "08:00", "11:00"),
    ("S", "13:00", "16:00"),
)
CLASS_OFFERING_SEEDS = (
    ("201A", "ENTREP 1", "GE3", "MW", "07:30", "09:00", "TERESA C. EBONA", "2nd Semester"),
    ("201A", "ENTREP 1", "GE4", "MW", "09:00", "10:30", "NESTOR T. TUAZON", "2nd Semester"),
    ("201A", "ENTREP 1", "GELEC2", "TTH", "07:30", "09:00", "MARITONI C. BORROMEO", "2nd Semester"),
    ("202", "ENTREP 1", "ENTREP3", "MW", "10:30", "12:00", "MAUREN P. AGNA", "2nd Semester"),
    ("202", "ENTREP 1", "ENTREP4", "TTH", "09:00", "10:30", "MAUREN P. AGNA", "2nd Semester"),
    ("Com Lab", "ENTREP 1", "BCom1", "TTH", "10:30", "12:00", "MARICHU F. GUMAL", "2nd Semester"),
    ("202", "ENTREP 2", "ENTREP7", "MW", "13:00", "14:30", "MAUREN P. AGNA", "2nd Semester"),
    ("202", "ENTREP 2", "ENTREP8", "TTH", "13:00", "14:30", "MAUREN P. AGNA", "2nd Semester"),
    ("203", "ENTREP 3", "ENTREP12", "MW", "14:30", "16:00", "MAUREN P. AGNA", "2nd Semester"),
    ("203", "ENTREP 3", "ENTREP13", "TTH", "14:30", "16:00", "MAUREN P. AGNA", "2nd Semester"),
    ("204", "BSFi 1", "GEC 1202", "MW", "07:30", "09:00", "JANICE I. SAN BUENAVENTURA", "2nd Semester"),
    ("204", "BSFi 1", "GEC 1203", "MW", "09:00", "10:30", "BRYAN V. ESCALDERON", "2nd Semester"),
    ("204", "BSFi 1", "Bot", "MW", "10:30", "12:00", "JANICE I. SAN BUENAVENTURA", "2nd Semester"),
    ("204", "BSFi 1", "CHEM 2", "TTH", "07:30", "09:00", "BRYAN V. ESCALDERON", "2nd Semester"),
    ("204", "BSFi 1", "Fi 1201", "TTH", "09:00", "10:30", "JANICE I. SAN BUENAVENTURA", "2nd Semester"),
    ("204", "BSFi 1", "Math 1", "TTH", "10:30", "12:00", "BRYAN V. ESCALDERON", "2nd Semester"),
    ("203", "BSFi2", "Fi 2204", "MW", "13:00", "14:30", "BRYAN V. ESCALDERON", "2nd Semester"),
    ("203", "BSFi2", "Fi 2206", "TTH", "13:00", "14:30", "JANICE I. SAN BUENAVENTURA", "2nd Semester"),
    ("AT Lab", "AT 1", "PROF ED 1", "MW", "07:30", "09:00", "SHEINA P. MAMAY", "2nd Semester"),
    ("AT Lab", "AT 1", "PROF ED 2", "MW", "09:00", "10:30", "MARILYN S.R. ROMERO", "2nd Semester"),
    ("AT Lab", "AT 1", "AT 3", "MW", "10:30", "12:00", "ISIDRO C. AZANA", "2nd Semester"),
    ("AT Lab", "AT 1", "AT 4", "TTH", "07:30", "09:00", "ISIDRO C. AZANA", "2nd Semester"),
    ("AT Lab", "AT 2", "AT 8", "MW", "13:00", "14:30", "ISIDRO C. AZANA", "2nd Semester"),
    ("AT Lab", "AT 2", "AT 9", "TTH", "09:00", "10:30", "ISIDRO C. AZANA", "2nd Semester"),
    ("AT Lab", "AT 2", "AT 10", "TTH", "10:30", "12:00", "ALVIN S.R. LAGARDE", "2nd Semester"),
    ("AT Lab", "AT 3", "AT 13", "TTH", "13:00", "14:30", "ISIDRO C. AZANA", "2nd Semester"),
    ("HVACT Lab", "HVACT 1", "PROF ED 1", "TTHF", "08:00", "09:30", "NESTOR T. TUAZON", "2nd Semester"),
    ("HVACT Lab", "HVACT 1", "PROF ED 2", "TTHF", "09:30", "11:00", "TERESA C. EBONA", "2nd Semester"),
    ("HVACT Lab", "HVACT 1", "HVACT 3", "TTHF", "13:00", "14:30", "ENGR. SAMUEL B. FRONDOZO, JR.", "2nd Semester"),
    ("HVACT Lab", "HVACT 2", "HVACT 5", "F", "08:00", "11:00", "ALVIN S.R. LAGARDE", "2nd Semester"),
    ("HVACT Lab", "HVACT 2", "HVACT 6", "TTHF", "14:30", "16:00", "ALVIN S.R. LAGARDE", "2nd Semester"),
    ("HVACT Lab", "HVACT 2", "HVACT 7", "S", "08:00", "11:00", "ENGR. SAMUEL B. FRONDOZO, JR.", "2nd Semester"),
    ("HVACT Lab", "HVACT 3", "HVACT 11", "S", "13:00", "16:00", "ENGR. SAMUEL B. FRONDOZO, JR.", "2nd Semester"),
)
GENERATED_INSTRUCTOR_REPLACEMENTS = {
    "ENGR. SAMUEL B. FRONDOZO, JR., PME": "ENGR. SAMUEL B. FRONDOZO, JR.",
    "BRYAN V. ESCALDERON, LPT": "BRYAN V. ESCALDERON",
    "JOENITHE A. AVILA, LPT": "JOENITH A. AVILA",
    "MARITONIC T. BORROMEO, MSc": "MARITONI C. BORROMEO",
    "MAUREN P. AGNA, MBA": "MAUREN P. AGNA",
    "MELVYN S.R. ONDIS, J.D.": "MELVIN S.R ONDIS",
    "NESTOR T. TUAZON, MAEd": "NESTOR T. TUAZON",
    "SHEINA P. MAMAY, LPT": "SHEINA P. MAMAY",
    "TERESA C. EBONA, MAEd": "TERESA C. EBONA",
    "VANESSA A. BAQUE, LPT": "VANESSA A. BAQUE",
}
GENERATED_STAFF_INSTRUCTOR_REASSIGNMENTS = {
    "KATHLEEN MAE B. STA. ROSA, MBA": "MAUREN P. AGNA",
}
UNUSED_GENERATED_STAFF_INSTRUCTORS = (
    "LYNIE B. RIN",
    "MARIOSE B. VELARDE, RN, LPT",
    "MARY JOY R. LOZANO",
)
GENERATED_SECTION_REPLACEMENTS = {
    "BSENT-1A": "ENTREP 1",
    "BSENT-2A": "ENTREP 2",
    "BSENT-3A": "ENTREP 3",
    "BSF-1A": "BSFi 1",
    "BSF-2A": "BSFi2",
    "BTVTED-AT-1A": "AT 1",
    "BTVTED-AT-2A": "AT 2",
    "BTVTED-AT-3A": "AT 3",
    "BTVTED-HVACT-1A": "HVACT 1",
    "BTVTED-HVACT-2A": "HVACT 2",
    "BTVTED-HVACT-3A": "HVACT 3",
}
GENERATED_SECTIONS_WITHOUT_LOCAL_MATCH = (
    "BTVTED-CHS-1A",
    "BTVTED-CHS-2A",
    "BTVTED-CHS-3A",
)
OLD_AUTOMOTIVE_SUBJECT_SEEDS = (
    ("ATV101", "Automotive Shop Safety, Tools, and Equipment"),
    ("ATV102", "Basic Automotive Electricity"),
    ("ATV103", "Engine Fundamentals and Preventive Maintenance"),
    ("ATV104", "Automotive Service and Repair Laboratory I"),
    ("ATV201", "Gasoline Engine Tune-up and Emission Control"),
    ("ATV202", "Brake System Service"),
    ("ATV203", "Suspension and Steering Systems"),
    ("ATV204", "Manual Drive Train and Axle Service"),
    ("ATV301", "Automotive Electrical and Electronic Systems"),
    ("ATV302", "Engine Mechanical Diagnosis and Repair"),
    ("ATV303", "Fuel Injection and Engine Management Systems"),
    ("ATV304", "Automotive Airconditioning Servicing"),
    ("ATV401", "Automatic Transmission Service"),
    ("ATV402", "Supervised Industrial Training in Automotive Technology"),
)
BTVTED_CHS_SUBJECT_SEEDS = (
    ("GE 1", "Understanding the Self", 3, None, "1st Year", "1st Semester"),
    ("GE 2", "Readings in the Philippine History", 3, "GE 1", "1st Year", "1st Semester"),
    ("GE 3", "Mathematics in the Modern World", 3, "GE 2", "1st Year", "1st Semester"),
    ("GE 4", "Science, Technology and Society", 3, "GE 3", "1st Year", "1st Semester"),
    ("GE 5", "Purposive Communication", 3, "GE 4", "1st Year", "1st Semester"),
    ("GE 6", "Art Appreciation", 3, "GE 5", "1st Year", "1st Semester"),
    ("CHS 1", "Occupational Health and Safety Practices", 1, None, "1st Year", "1st Semester"),
    ("CHS 2", "Introduction to Computing", 3, "CHS 1", "1st Year", "1st Semester"),
    ("NSTP 1", "Literacy Training Service 1", 3, None, "1st Year", "1st Semester"),
    ("PATHFit 1", "Movement Competency Training", 2, None, "1st Year", "1st Semester"),
    ("PROF ED 1", "The Child and Adolescent Learner and Learning Principles", 3, None, "1st Year", "2nd Semester"),
    ("PROF ED 2", "Foundation of Special and Inclusive Education", 3, "PROF ED 1", "1st Year", "2nd Semester"),
    ("GE 7", "The Contemporary World", 3, "GE 6", "1st Year", "2nd Semester"),
    ("CHS 3", "Knowledge Work Software and Presentation Skills", 3, "CHS 2", "1st Year", "2nd Semester"),
    ("GE 8", "Ethics", 3, "GE 7", "1st Year", "2nd Semester"),
    ("GE 9", "Life and Works of Rizal", 3, "GE 8", "1st Year", "2nd Semester"),
    ("GE ELEC 1", "Living in the Information Technology Era", 3, None, "1st Year", "2nd Semester"),
    ("NSTP 2", "Literacy Training Service 2", 3, "NSTP 1", "1st Year", "2nd Semester"),
    ("PATHFit 2", "Exercise-based Fitness Activities", 2, "PATHFit 1", "1st Year", "2nd Semester"),
    ("PROF ED 3", "The Teaching Profession", 3, "PROF ED 2", "2nd Year", "1st Semester"),
    ("TLE 1", "Introduction to Industrial Arts", 3, None, "2nd Year", "1st Semester"),
    ("TLE 2", "Home Economics Literacy", 3, "TLE 1", "2nd Year", "1st Semester"),
    ("TLE 3", "Teaching Information and Communication Technology as an Exploratory Course", 3, "TLE 2", "2nd Year", "1st Semester"),
    ("CHS 4", "Operating Systems and Its Applications", 3, "CHS 3", "2nd Year", "1st Semester"),
    ("CHS 5", "PC Hardware & Software Troubleshooting and Repair", 4, "CHS 4", "2nd Year", "1st Semester"),
    ("CHS 6", "Computer Networks", 3, "CHS 5", "2nd Year", "1st Semester"),
    ("GE ELEC 2", "Gender and Society", 3, "GE ELEC 1", "2nd Year", "1st Semester"),
    ("PATHFit 3", "Philippine Folkdance & Dancesport", 2, "PATHFit 2", "2nd Year", "1st Semester"),
    ("PROF ED 4", "The Teacher and the Community, School Culture and Organizational Leadership with Focus on the Philippine TVET System", 3, "PROF ED 3", "2nd Year", "2nd Semester"),
    ("PROF ED 5", "The Andragogy of Learning including Principles of Trainer's Methodology 1", 3, "PROF ED 4", "2nd Year", "2nd Semester"),
    ("TLE 4", "Introduction to Agri-Fishery and Arts", 3, "TLE 3", "2nd Year", "2nd Semester"),
    ("TLE 5", "Entrepreneurship", 3, "TLE 4", "2nd Year", "2nd Semester"),
    ("GEC ELEC 3", "Philippine Popular Culture", 3, "GE ELEC 2", "2nd Year", "2nd Semester"),
    ("CHS 7", "Professional Ethics in IT", 3, "CHS 6", "2nd Year", "2nd Semester"),
    ("CHS 8", "Data Communication and Networking", 4, "CHS 7", "2nd Year", "2nd Semester"),
    ("CHS 9", "Advanced PC Repair and Maintenance", 4, "CHS 8", "2nd Year", "2nd Semester"),
    ("PATH Fit 4", "Individual & Dual Sports", 2, "PATHFit 3", "2nd Year", "2nd Semester"),
    ("PROF ED 6", "Facilitating Learner-Centered Teaching: The Learner Centered Approaches with Emphasis on Trainers Methodology 1", 3, "PROF ED 5", "3rd Year", "1st Semester"),
    ("PROF ED 7", "Technology for Teaching and Learning 1", 3, "PROF ED 6", "3rd Year", "1st Semester"),
    ("PROF ED 8", "Assessment of Learning 1", 3, "PROF ED 7", "3rd Year", "1st Semester"),
    ("Research 1", "Technology Research 1 (Methods of Research)", 3, None, "3rd Year", "1st Semester"),
    ("TLE 6", "Teaching the Common Competencies in Industrial Arts", 3, "TLE 5", "3rd Year", "1st Semester"),
    ("TLE 7", "Teaching the Common Competencies in Information and Communication Technology", 3, "TLE 6", "3rd Year", "1st Semester"),
    ("TLE 8", "Teaching Common Competencies in Agri-Fishery and Arts", 3, "TLE 7", "3rd Year", "1st Semester"),
    ("CHS 10", "Network Administration and Maintenance", 4, "CHS 9", "3rd Year", "1st Semester"),
    ("PROF ED 9", "Technology for Teaching and Learning 2", 3, "PROF ED 8", "3rd Year", "2nd Semester"),
    ("PROF ED 10", "Assessment in Learning 2 with Focus on Trainers Methodology 1 & 2", 3, "PROF ED 9", "3rd Year", "2nd Semester"),
    ("PROF ED 11", "Curriculum Development and Evaluation with Emphasis on Trainers Methodology II", 3, "PROF ED 10", "3rd Year", "2nd Semester"),
    ("PROF ED 12", "Building and Enhancing New Literacies Across the Curriculum with Emphasis on the 21st Century", 3, "PROF ED 11", "3rd Year", "2nd Semester"),
    ("PROF ED 13", "Work-Based Learning with Emphasis on Trainers' Methodology", 3, "PROF ED 12", "3rd Year", "2nd Semester"),
    ("Research 2", "Technology Research 2 (Undergraduate Thesis/Research Paper/Research Project)", 3, "Research 1", "3rd Year", "2nd Semester"),
    ("TLE 9", "Teaching Common Competencies in Home Economics", 3, "TLE 8", "3rd Year", "2nd Semester"),
    ("CHS 11", "Windows Service Administration", 4, "CHS 10", "3rd Year", "2nd Semester"),
    ("FS 1", "Observations of Teaching-Learning in Actual School Environment", 3, None, "4th Year", "1st Semester"),
    ("FS 2", "Participation and Teaching Assistantship", 3, "FS 1", "4th Year", "1st Semester"),
    ("SIT", "Supervised Industrial Training", 3, None, "4th Year", "1st Semester"),
    ("PROF ED 14", "Teaching Internship/ Practice Teaching", 6, "PROF ED 13", "4th Year", "2nd Semester"),
)
BTVTED_HVACT_SUBJECT_SEEDS = (
    ("GE 1", "Understanding the Self", 3, None, "1st Year", "1st Semester"),
    ("GE 2", "Readings in the Philippine History", 3, "GE 1", "1st Year", "1st Semester"),
    ("GE 3", "Mathematics in the Modern World", 3, "GE 2", "1st Year", "1st Semester"),
    ("GE 4", "Science, Technology and Society", 3, "GE 3", "1st Year", "1st Semester"),
    ("GE 5", "Purposive Communication", 3, "GE 4", "1st Year", "1st Semester"),
    ("GE 6", "Art Appreciation", 3, "GE 5", "1st Year", "1st Semester"),
    ("HVACT 1", "Occupational Health and Safety Practices", 1, None, "1st Year", "1st Semester"),
    ("HVACT 2", "Instrumentation and Control Devices", 3, "HVACT 1", "1st Year", "1st Semester"),
    ("NSTP 1", "Literacy Training Service 1", 3, None, "1st Year", "1st Semester"),
    ("PATHFit 1", "Movement Competency Training", 2, None, "1st Year", "1st Semester"),
    ("PROF ED 1", "The Child and Adolescent Learner and Learning Principles", 3, None, "1st Year", "2nd Semester"),
    ("PROF ED 2", "Foundation of Special and Inclusive Education", 3, "PROF ED 1", "1st Year", "2nd Semester"),
    ("GE 7", "The Contemporary World", 3, "GE 6", "1st Year", "2nd Semester"),
    ("HVACT 3", "Domestic Refrigeration and Air-Conditioning (DOMRAC) Electrical Circuits", 5, "HVACT 2", "1st Year", "2nd Semester"),
    ("GE 8", "Ethics", 3, "GE 7", "1st Year", "2nd Semester"),
    ("GE 9", "Life and Works of Rizal", 3, "GE 8", "1st Year", "2nd Semester"),
    ("GE ELEC 1", "Living in the Information Technology Era", 3, None, "1st Year", "2nd Semester"),
    ("NSTP 2", "Literacy Training Service 2", 3, "NSTP 1", "1st Year", "2nd Semester"),
    ("PATHFit 2", "Exercise-based Fitness Activities", 2, "PATHFit 1", "1st Year", "2nd Semester"),
    ("PROF ED 3", "The Teaching Profession", 3, "PROF ED 2", "2nd Year", "1st Semester"),
    ("TLE 1", "Introduction to Industrial Arts", 3, None, "2nd Year", "1st Semester"),
    ("TLE 2", "Home Economics Literacy", 3, "TLE 1", "2nd Year", "1st Semester"),
    ("TLE 3", "Teaching Information and Communication Technology as an Exploratory Course", 3, "TLE 2", "2nd Year", "1st Semester"),
    ("HVACT 4", "Domestic Refrigeration and Air-Conditioning (DOMRAC) System Service and Maintenance", 5, "HVACT 3", "2nd Year", "1st Semester"),
    ("HVACT 5", "Soldering, Welding and Joining Operations", 4, "HVACT 4", "2nd Year", "1st Semester"),
    ("GE ELEC 2", "Gender and Society", 3, "GE ELEC 1", "2nd Year", "1st Semester"),
    ("PATHFit 3", "Philippine Folkdance & Dancesport", 2, "PATHFit 2", "2nd Year", "1st Semester"),
    ("PROF ED 4", "The Teacher and the Community, School Culture and Organizational Leadership with Focus on the Philippine TVET System", 3, "PROF ED 3", "2nd Year", "2nd Semester"),
    ("PROF ED 5", "The Andragogy of Learning including Principles of Trainer's Methodology 1", 3, "PROF ED 4", "2nd Year", "2nd Semester"),
    ("TLE 4", "Introduction to Agri-Fishery and Arts", 3, "TLE 3", "2nd Year", "2nd Semester"),
    ("TLE 5", "Entrepreneurship", 3, "TLE 4", "2nd Year", "2nd Semester"),
    ("GE ELEC 3", "Philippine Popular Culture", 3, "GE ELEC 2", "2nd Year", "2nd Semester"),
    ("HVACT 5", "Commercial Refrigeration Equipment (CRE) Installation and Maintenance", 4, "HVACT 4", "2nd Year", "2nd Semester"),
    ("HVACT 6", "Packaged Air-Conditioning Unit (PACU) Installation and Maintenance", 4, "HVACT 5", "2nd Year", "2nd Semester"),
    ("HVACT 7", "Mobile Refrigeration and Air Conditioning", 4, "HVACT 6", "2nd Year", "2nd Semester"),
    ("PATH Fit 4", "Individual & Dual Sports", 2, "PATHFit 3", "2nd Year", "2nd Semester"),
    ("PROF ED 6", "Facilitating Learner-Centered Teaching: The Learner Centered Approaches with Emphasis on Trainers Methodology 1", 3, "PROF ED 5", "3rd Year", "1st Semester"),
    ("PROF ED 7", "Technology for Teaching and Learning 1", 3, "PROF ED 6", "3rd Year", "1st Semester"),
    ("PROF ED 8", "Assessment of Learning 1", 3, "PROF ED 7", "3rd Year", "1st Semester"),
    ("Research 1", "Technology Research 1 (Methods of Research)", 3, None, "3rd Year", "1st Semester"),
    ("TLE 6", "Teaching the Common Competencies in Industrial Arts", 3, "TLE 5", "3rd Year", "1st Semester"),
    ("TLE 7", "Teaching the Common Competencies in Information and Communication Technology", 3, "TLE 6", "3rd Year", "1st Semester"),
    ("TLE 8", "Teaching Common Competencies in Agri-Fishery and Arts", 3, "TLE 7", "3rd Year", "1st Semester"),
    ("HVACT 8", "Refrigeration Plant Designing", 3, "HVACT 7", "3rd Year", "1st Semester"),
    ("HVACT 9", "Air Handling Units Installation, Service and Maintenance", 3, "HVACT 8", "3rd Year", "1st Semester"),
    ("HVACT 10", "Heat Pump Operation", 4, "HVACT 9", "3rd Year", "1st Semester"),
    ("PROF ED 9", "Technology for Teaching and Learning 2", 3, "PROF ED 8", "3rd Year", "2nd Semester"),
    ("PROF ED 10", "Assessment in Learning 2 with Focus on Trainers Methodology 1 & 2", 3, "PROF ED 9", "3rd Year", "2nd Semester"),
    ("PROF ED 11", "Curriculum Development and Evaluation with Emphasis on Trainers Methodology II", 3, "PROF ED 10", "3rd Year", "2nd Semester"),
    ("PROF ED 12", "Building and Enhancing New Literacies Across the Curriculum with Emphasis on the 21st Century", 3, "PROF ED 11", "3rd Year", "2nd Semester"),
    ("PROF ED 13", "Work-Based Learning with Emphasis on Trainers' Methodology", 3, "PROF ED 12", "3rd Year", "2nd Semester"),
    ("Research 2", "Technology Research 2 (Undergraduate Thesis/Research Paper/Research Project)", 3, "Research 1", "3rd Year", "2nd Semester"),
    ("TLE 9", "Teaching Common Competencies in Home Economics", 3, "TLE 8", "3rd Year", "2nd Semester"),
    ("HVACT 11", "Ancillary Equipment Service and Repair", 4, "HVACT 10", "3rd Year", "2nd Semester"),
    ("FS 1", "Observations of Teaching-Learning in Actual School Environment", 3, None, "4th Year", "1st Semester"),
    ("FS 2", "Participation and Teaching Assistantship", 3, "FS 1", "4th Year", "1st Semester"),
    ("SIT", "Supervised Industrial Training", 3, None, "4th Year", "1st Semester"),
    ("PROF ED 14", "Teaching Internship/ Practice Teaching", 6, "PROF ED 13", "4th Year", "2nd Semester"),
)
BTVTED_AUTOMOTIVE_SUBJECT_SEEDS = (
    ("GE 1", "Understanding the Self", 3, None, "1st Year", "1st Semester"),
    ("GE 2", "Readings in the Philippine History", 3, "GE 1", "1st Year", "1st Semester"),
    ("GE 3", "Mathematics in the Modern World", 3, "GE 2", "1st Year", "1st Semester"),
    ("GE 4", "Science, Technology and Society", 3, "GE 3", "1st Year", "1st Semester"),
    ("GE 5", "Purposive Communication", 3, "GE 4", "1st Year", "1st Semester"),
    ("GE 6", "Art Appreciation", 3, "GE 5", "1st Year", "1st Semester"),
    ("AT 1", "Occupational Health and Safety Practices", 1, None, "1st Year", "1st Semester"),
    ("AT 2", "Internal Combustion Engine Servicing, Repair and Maintenance", 4, "AT 1", "1st Year", "1st Semester"),
    ("NSTP 1", "Literacy Training Service 1", 3, None, "1st Year", "1st Semester"),
    ("PATHFit 1", "Movement Competency Training", 2, None, "1st Year", "1st Semester"),
    ("PROF ED 1", "The Child and Adolescent Learner and Learning Principles", 3, None, "1st Year", "2nd Semester"),
    ("PROF ED 2", "Foundation of Special and Inclusive Education", 3, "PROF ED 1", "1st Year", "2nd Semester"),
    ("GE 7", "The Contemporary World", 3, "GE 6", "1st Year", "2nd Semester"),
    ("AT 3", "Preventive Maintenance and Gas/Diesel Engine Tune Up", 3, "AT 2", "1st Year", "2nd Semester"),
    ("AT 4", "Automotive Service Shop Management and Maintenance", 1, "AT 3", "1st Year", "2nd Semester"),
    ("GE 8", "Ethics", 3, "GE 7", "1st Year", "2nd Semester"),
    ("GE 9", "Life and Works of Rizal", 3, "GE 8", "1st Year", "2nd Semester"),
    ("GE ELEC 1", "Living in the Information Technology Era", 3, None, "1st Year", "2nd Semester"),
    ("NSTP 2", "Literacy Training Service 2", 3, "NSTP 1", "1st Year", "2nd Semester"),
    ("PATHFit 2", "Exercise-based Fitness Activities", 2, "PATHFit 1", "1st Year", "2nd Semester"),
    ("PROF ED 3", "The Teaching Profession", 3, "PROF ED 2", "2nd Year", "1st Semester"),
    ("TLE 1", "Introduction to Industrial Arts", 3, None, "2nd Year", "1st Semester"),
    ("TLE 2", "Home Economics Literacy", 3, "TLE 1", "2nd Year", "1st Semester"),
    ("TLE 3", "Teaching Information and Communication Technology as an Exploratory Course", 3, "TLE 2", "2nd Year", "1st Semester"),
    ("AT 5", "Automotive Body Electrical System Service, Repair and Maintenance", 5, "AT 4", "2nd Year", "1st Semester"),
    ("AT 6", "Automotive Air-Conditioning System Servicing Repair and Maintenance", 3, "AT 5", "2nd Year", "1st Semester"),
    ("AT 7", "Basic Driving", 3, "AT 6", "2nd Year", "1st Semester"),
    ("GE ELEC 2", "Gender and Society", 3, "GE ELEC 1", "2nd Year", "1st Semester"),
    ("PATHFit 3", "Philippine Folkdance & Dancesport", 2, "PATHFit 2", "2nd Year", "1st Semester"),
    ("PROF ED 4", "The Teacher and the Community, School Culture and Organizational Leadership with Focus on the Philippine TVET System", 3, "PROF ED 3", "2nd Year", "2nd Semester"),
    ("PROF ED 5", "The Andragogy of Learning including Principles of Trainer's Methodology 1", 3, "PROF ED 4", "2nd Year", "2nd Semester"),
    ("TLE 4", "Introduction to Agri-Fishery and Arts", 3, "TLE 3", "2nd Year", "2nd Semester"),
    ("TLE 5", "Entrepreneurship", 3, "TLE 4", "2nd Year", "2nd Semester"),
    ("GEC ELEC 3", "Philippine Popular Culture", 3, "GE ELEC 2", "2nd Year", "2nd Semester"),
    ("AT 8", "Motor Cycle and Small Engine Servicing, Repairing and Maintenance", 2, "AT 7", "2nd Year", "2nd Semester"),
    ("AT 9", "Automotive Body Repair and Substrate Preparation", 5, "AT 8", "2nd Year", "2nd Semester"),
    ("AT 10", "Metallic and Solid Color Painting Applications and Techniques", 3, "AT 9", "2nd Year", "2nd Semester"),
    ("PATH Fit 4", "Individual & Dual Sports", 2, "PATHFit 3", "2nd Year", "2nd Semester"),
    ("PROF ED 6", "Facilitating Learner-Centered Teaching: The Learner Centered Approaches with Emphasis on Trainers Methodology 1", 3, "PROF ED 5", "3rd Year", "1st Semester"),
    ("PROF ED 7", "Technology for Teaching and Learning 1", 3, "PROF ED 6", "3rd Year", "1st Semester"),
    ("PROF ED 8", "Assessment of Learning 1", 3, "PROF ED 7", "3rd Year", "1st Semester"),
    ("Research 1", "Technology Research 1 (Methods of Research)", 3, None, "3rd Year", "1st Semester"),
    ("TLE 6", "Teaching the Common Competencies in Industrial Arts", 3, "TLE 5", "3rd Year", "1st Semester"),
    ("TLE 7", "Teaching the Common Competencies in Information and Communication Technology", 3, "TLE 6", "3rd Year", "1st Semester"),
    ("TLE 8", "Teaching Common Competencies in Agri-Fishery and Arts", 3, "TLE 7", "3rd Year", "1st Semester"),
    ("AT 11", "Under Chassis Components Servicing, Repairing and Maintenance", 4, "AT 10", "3rd Year", "1st Semester"),
    ("AT 12", "Engine Overhauling and Rebuilding", 5, "AT 11", "3rd Year", "1st Semester"),
    ("PROF ED 9", "Technology for Teaching and Learning 2", 3, "PROF ED 8", "3rd Year", "2nd Semester"),
    ("PROF ED 10", "Assessment in Learning 2 with Focus on Trainers Methodology 1 & 2", 3, "PROF ED 9", "3rd Year", "2nd Semester"),
    ("PROF ED 11", "Curriculum Development and Evaluation with Emphasis on Trainers Methodology II", 3, "PROF ED 10", "3rd Year", "2nd Semester"),
    ("PROF ED 12", "Building and Enhancing New Literacies Across the Curriculum with Emphasis on the 21st Century", 3, "PROF ED 11", "3rd Year", "2nd Semester"),
    ("PROF ED 13", "Work-Based Learning with Emphasis on Trainers' Methodology", 3, "PROF ED 12", "3rd Year", "2nd Semester"),
    ("Research 2", "Technology Research 2 (Undergraduate Thesis/Research Paper/Research Project)", 3, "Research 1", "3rd Year", "2nd Semester"),
    ("TLE 9", "Teaching Common Competencies in Home Economics", 3, "TLE 8", "3rd Year", "2nd Semester"),
    ("AT 13", "Basic Power Conversion System Service, Repair and Maintenance", 3, "AT 12", "3rd Year", "2nd Semester"),
    ("AT 14", "Basic Electronics Engine Management System Operation and Servicing", 3, "AT 13", "3rd Year", "2nd Semester"),
    ("FS 1", "Observations of Teaching-Learning in Actual School Environment", 3, None, "4th Year", "1st Semester"),
    ("FS 2", "Participation and Teaching Assistantship", 3, "FS 1", "4th Year", "1st Semester"),
    ("SIT", "Supervised Industrial Training", 3, None, "4th Year", "1st Semester"),
    ("PROF ED 14", "Teaching Internship/ Practice Teaching", 6, "PROF ED 13", "4th Year", "2nd Semester"),
)
BS_FISHERIES_SUBJECT_SEEDS = (
    ("NSTP 1", "National Service Training Program", 3, None, "1st Year", "1st Semester"),
    ("PE 1", "Swimming for Beginners", 2, None, "1st Year", "1st Semester"),
    ("Zoo", "Fundamentals of Zoology", 5, None, "1st Year", "1st Semester"),
    ("CHEM 1", "Organic Chemistry", 5, None, "1st Year", "1st Semester"),
    ("GEC 1101", "Understanding the Self", 3, None, "1st Year", "1st Semester"),
    ("GEC 1104", "Mathematics in the Modern World", 3, "GEC 1101", "1st Year", "1st Semester"),
    ("GEC 1105", "Purposive Communication", 3, "GEC 1104", "1st Year", "1st Semester"),
    ("GEC 1107", "Science, Technology and Society", 3, "GEC 1105", "1st Year", "1st Semester"),
    ("ICT 1", "Fundamentals of ICT", 3, None, "1st Year", "1st Semester"),
    ("NSTP 2", "National Service Training Program 2", 3, "NSTP 1", "1st Year", "2nd Semester"),
    ("PE 2", "Intermediate Swimming", 2, "PE 1", "1st Year", "2nd Semester"),
    ("GEC 1202", "Readings in Philippine History", 3, "GEC 1101", "1st Year", "2nd Semester"),
    ("GEC 1203", "The Contemporary World", 3, "GEC 1202", "1st Year", "2nd Semester"),
    ("Bot", "Fundamentals of Botany", 5, None, "1st Year", "2nd Semester"),
    ("CHEM 2", "Inorganic Analytical Chemistry", 5, "CHEM 1", "1st Year", "2nd Semester"),
    ("Fi 1201", "Ichthyology", 5, None, "1st Year", "2nd Semester"),
    ("Math 1", "Plane Trigonometry", 3, "GEC 1104", "1st Year", "2nd Semester"),
    ("GECE 1209", "Environmental Science", 3, None, "1st Year", "2nd Semester"),
    ("PE 3", "Advance Swimming and Life Saving", 2, "PE 2", "2nd Year", "1st Semester"),
    ("ICT 2", "Computer Applications in Fisheries", 3, "ICT 1", "2nd Year", "1st Semester"),
    ("CHEM 3", "Biochemistry", 3, "CHEM 2", "2nd Year", "1st Semester"),
    ("GEC 2108", "Ethics", 3, "GEC 1203", "2nd Year", "1st Semester"),
    ("Math 2", "Calculus", 3, "Math 1", "2nd Year", "1st Semester"),
    ("Fi 2102", "Aquatic Ecology and Resources", 5, "Fi 1201", "2nd Year", "1st Semester"),
    ("Fi 2103", "Physiology of Aquatic Organism", 3, "Fi 1201", "2nd Year", "1st Semester"),
    ("MicroBio", "Microbiology", 3, None, "2nd Year", "1st Semester"),
    ("PE 4", "Survival and Boating", 2, "PE 3", "2nd Year", "2nd Semester"),
    ("GECE 2210", "The Entrepreneurial Mind", 3, None, "2nd Year", "2nd Semester"),
    ("Math 3", "Statistics", 3, "Math 2", "2nd Year", "2nd Semester"),
    ("Fi 2204", "Capture Fisheries", 5, "Fi 2102", "2nd Year", "2nd Semester"),
    ("Fi 2205", "Post-Harvest Fisheries", 5, "Fi 2102", "2nd Year", "2nd Semester"),
    ("Fi 2206", "Aquaculture", 5, "Fi 2102", "2nd Year", "2nd Semester"),
    ("Fi 2207", "Fisheries Laws, Policies and Institutions", 3, "Fi 2102", "2nd Year", "2nd Semester"),
    ("Fi 3108", "Oceanography", 3, "Fi 2102", "3rd Year", "1st Semester"),
    ("Fi 3109", "Research Design and Methodologies", 3, "Math 3", "3rd Year", "1st Semester"),
    ("Fi 3110", "Fisheries Meteorology", 3, "GECE 1209", "3rd Year", "1st Semester"),
    ("Fi 3113", "Aquaculture Engineering", 3, "Fi 2206", "3rd Year", "1st Semester"),
    ("FiElec 3101", "Philippine Fishing Ground", 3, "Fi 2204", "3rd Year", "1st Semester"),
    ("FiElec 3102", "Post-harvest Handling Low Temperature Presevation", 3, "Fi 2205", "3rd Year", "1st Semester"),
    ("FiElec 3103", "Minor Fishery Products ann By-Product Processing", 3, "Fi 2205", "3rd Year", "1st Semester"),
    ("GEC 3109", "Life and Works of Rizal", 3, "GEC 2108", "3rd Year", "1st Semester"),
    ("GEC 3206", "Art Appreciation", 3, "GEC 3109", "3rd Year", "2nd Semester"),
    ("Fi 3211A", "Undergraduate Thesis Proposal", 1, "Fi 3109", "3rd Year", "2nd Semester"),
    ("Fi 3212", "Fish Health Management and Nutrition", 3, "Fi 2206", "3rd Year", "2nd Semester"),
    ("Fi 3214", "Fish Genetics and Breeding", 3, "Fi 2206", "3rd Year", "2nd Semester"),
    ("Fi 3220", "Coastal Fisheries Management", 5, "Fi 2204", "3rd Year", "2nd Semester"),
    ("FiElec 3204", "Hatchery Management", 3, "Fi 2206", "3rd Year", "2nd Semester"),
    ("FiElec 3205", "Fishery Economics", 3, "GECE 2210", "3rd Year", "2nd Semester"),
    ("FiElec 3206", "Fish Stock Assessment", 3, "Fi 3108", "3rd Year", "2nd Semester"),
    ("Fi 3211B", "Undergraduate Thesis Proposal", 5, "Fi 3211A", "4th Year", "1st Semester"),
    ("Fi 4119", "Project Development and Management", 3, "Fi 3211A", "4th Year", "1st Semester"),
    ("Fi 4116", "Fisheries Entrepreneurship", 3, "GECE 2210", "4th Year", "1st Semester"),
    ("Fi 4117", "Fisheries Extension", 3, "Fi 2207", "4th Year", "1st Semester"),
    ("Fi 4118", "Fishery Product Safety and Quality", 3, "Fi 2205", "4th Year", "1st Semester"),
    ("Fi 4121", "Seminar", 1, "Fi 3211A", "4th Year", "1st Semester"),
    ("Fi 4200", "On-the-Job Training", 3, "Fi 3211B", "4th Year", "2nd Semester"),
)
BS_ENTREPRENEURSHIP_SUBJECT_SEEDS = (
    ("GE1", "Understanding the Self", 3, None, "1st Year", "1st Semester"),
    ("GE2", "Purposive Communication", 3, "GE1", "1st Year", "1st Semester"),
    ("GELEC1", "Living in the Information Technology Era", 3, None, "1st Year", "1st Semester"),
    ("ENTREP1", "Entrepreneurial Behavior", 3, None, "1st Year", "1st Semester"),
    ("ENTREP2", "Human Resource Management", 3, "ENTREP1", "1st Year", "1st Semester"),
    ("Eng 1", "Public Speaking and Debate", 3, None, "1st Year", "1st Semester"),
    ("NSTP1", "NSTP/Civic Welfare Training Service 1", 3, None, "1st Year", "1st Semester"),
    ("PE1", "Physical Fitness", 2, None, "1st Year", "1st Semester"),
    ("GE3", "Readings in Philippine History", 3, "GE2", "1st Year", "2nd Semester"),
    ("GE4", "Mathematics in the Modern World", 3, "GE3", "1st Year", "2nd Semester"),
    ("GELEC2", "Gender and Society", 3, "GELEC1", "1st Year", "2nd Semester"),
    ("ENTREP3", "Opportunity Seeking", 3, "ENTREP2", "1st Year", "2nd Semester"),
    ("ENTREP4", "Social Entrepreneurship", 3, "ENTREP3", "1st Year", "2nd Semester"),
    ("BCom1", "Computer Business Application", 3, None, "1st Year", "2nd Semester"),
    ("NSTP2", "NSTP/Civic Welfare Training Service 2", 3, "NSTP1", "1st Year", "2nd Semester"),
    ("PE2", "Rhythmic Activities", 2, "PE1", "1st Year", "2nd Semester"),
    ("GE5", "Science, Technology & Society", 3, "GE4", "2nd Year", "1st Semester"),
    ("GELEC3", "Philippine Popular Culture", 3, "GELEC2", "2nd Year", "1st Semester"),
    ("ENTREP5", "Business Law and Taxation with focus on Laws Affecting Micro, Small and Medium Enterprises", 3, "ENTREP4", "2nd Year", "1st Semester"),
    ("ENTREP6", "Innovation Management", 3, "ENTREP5", "2nd Year", "1st Semester"),
    ("ST1", "Horticulture", 3, None, "2nd Year", "1st Semester"),
    ("EC1", "Supply Chain Management", 3, None, "2nd Year", "1st Semester"),
    ("PE3", "Individual/Dual Sports & Games", 2, "PE2", "2nd Year", "1st Semester"),
    ("GE6", "Life and Works of Rizal", 3, "GE5", "2nd Year", "2nd Semester"),
    ("GE7", "Art Appreciation", 3, "GE6", "2nd Year", "2nd Semester"),
    ("ENTREP7", "Financial Management (Financial Analysis for Decision Making)", 3, "ENTREP6", "2nd Year", "2nd Semester"),
    ("ENTREP8", "Market Research & Consumer Behavior", 3, "ENTREP7", "2nd Year", "2nd Semester"),
    ("ST2", "Agricultural Crop Production", 3, "ST1", "2nd Year", "2nd Semester"),
    ("EC2", "Management of Technology", 3, "EC1", "2nd Year", "2nd Semester"),
    ("PE4", "Team Sports and Games", 2, "PE3", "2nd Year", "2nd Semester"),
    ("GE8", "The Contemporary World", 3, "GE7", "3rd Year", "1st Semester"),
    ("ENTREP9", "Microeconomics", 3, "ENTREP8", "3rd Year", "1st Semester"),
    ("ENTREP10", "International Business and Trade", 3, "ENTREP9", "3rd Year", "1st Semester"),
    ("ENTREP11", "Programs and Policies on Enterprise Development", 3, "ENTREP10", "3rd Year", "1st Semester"),
    ("ST3", "Capture Fisheries", 3, "ST2", "3rd Year", "1st Semester"),
    ("EC3", "Venture Finance", 3, "EC2", "3rd Year", "1st Semester"),
    ("GE9", "Ethics", 3, "GE8", "3rd Year", "2nd Semester"),
    ("ENTREP12", "Pricing and Costing", 3, "ENTREP11", "3rd Year", "2nd Semester"),
    ("ENTREP13", "Business Plan Preparation", 3, "ENTREP12", "3rd Year", "2nd Semester"),
    ("CBMEC1", "Operation Management", 3, None, "3rd Year", "2nd Semester"),
    ("ST4", "Post-Harvest Fisheries", 3, "ST3", "3rd Year", "2nd Semester"),
    ("EC4", "Entrepreneurial Marketing Strategies", 3, "EC3", "3rd Year", "2nd Semester"),
    ("ENTREP14", "Business Plan Implementation 1: Product Development and Market Analysis", 5, "ENTREP13", "4th Year", "1st Semester"),
    ("CBMEC2", "Strategic Management", 3, "CBMEC1", "4th Year", "1st Semester"),
    ("ENTREP15", "Business Plan Implementation 2", 5, "ENTREP14", "4th Year", "2nd Semester"),
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Kkyle0p0p00pp@"),
    "database": os.getenv("DB_NAME", "enrollment_system"),
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

def current_school_year(value=None):
    value = value or date.today()
    start_year = value.year if value.month >= 6 else value.year - 1
    return f"{start_year}-{start_year + 1}"

def section_prefix_for_program(program_name, major):
    if program_name == "Bachelor of Science in Entrepreneurship":
        return "ENTREP "
    if program_name == "Bachelor of Science in Fisheries":
        return "BSFi"
    if program_name == "Bachelor of Technical Vocational Teacher Education":
        major_prefixes = {
            "Automotive Technology": "AT ",
            "Computer Hardware Servicing": "CHS ",
            "Heating, Ventilating, and Airconditioning Technology": "HVACT ",
        }
        return major_prefixes.get(major or "", "")
    return ""

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

def current_user():
    return getattr(g, "current_user", None)

def is_admin():
    user = current_user()
    return bool(user and user.get("role") == "admin")

def is_student():
    user = current_user()
    return bool(user and user.get("role") == "student")

def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return request.headers.get("X-Session-Token")

@app.before_request
def require_api_session():
    if request.method == "OPTIONS" or not request.path.startswith("/api/"):
        return None

    if request.path in {"/api/health", "/api/login"}:
        return None

    token = get_bearer_token()
    session = ACTIVE_SESSIONS.get(token or "")
    if not session:
        return jsonify({"error": "Please log in to continue."}), 401

    g.current_user = session

    if session.get("role") == "admin":
        return None

    if session.get("role") == "student":
        allowed = {
            ("GET", "/api/me"),
            ("POST", "/api/logout"),
            ("GET", "/api/class-offerings"),
            ("GET", "/api/subjects"),
            ("GET", "/api/enrollments"),
            ("POST", "/api/enrollments"),
        }
        if (request.method, request.path) in allowed:
            return None
        if request.method == "DELETE" and request.path.startswith("/api/enrollments/"):
            return None

    return jsonify({"error": "You do not have permission to access this resource."}), 403

def sync_student_account(student_id, lrn):
    lrn = optional(lrn)
    if not student_id or not lrn:
        return

    rows = fetch_all(
        "SELECT user_id FROM user_account WHERE role = 'student' AND student_id = %s",
        (student_id,),
    )
    if rows:
        execute(
            "UPDATE user_account SET username = %s, password = %s WHERE user_id = %s",
            (lrn, DEFAULT_STUDENT_PASSWORD, rows[0]["user_id"]),
        )
        return

    execute(
        """
        INSERT INTO user_account (username, password, role, student_id)
        VALUES (%s, %s, 'student', %s)
        ON DUPLICATE KEY UPDATE
            role = IF(role = 'student', 'student', role),
            student_id = IF(role = 'student', VALUES(student_id), student_id),
            password = IF(role = 'student', VALUES(password), password)
        """,
        (lrn, DEFAULT_STUDENT_PASSWORD, student_id),
    )

def guardian_details_from_student_payload(data):
    return {
        "first_name": optional(pick(data, "GuardianFirstName", "guardian_first_name")),
        "middle_name": optional(pick(data, "GuardianMiddleName", "guardian_middle_name")),
        "last_name": optional(pick(data, "GuardianLastName", "guardian_last_name")),
        "contact_number": optional(pick(data, "GuardianContactNumber", "guardian_contact_number")) or "",
    }

def has_guardian_details(details):
    return any(details.values())

def save_guardian_details(details, guardian_id=None):
    if not has_guardian_details(details):
        return guardian_id

    if not details["first_name"] or not details["last_name"]:
        raise ValueError("Guardian first name and last name are required.")

    if guardian_id:
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
                details["first_name"],
                details["middle_name"],
                details["last_name"],
                details["contact_number"],
                guardian_id,
            ),
        )
        return guardian_id

    return execute(
        "INSERT INTO guardian (first_name, middle_name, last_name, contact_number) VALUES (%s, %s, %s, %s)",
        (
            details["first_name"],
            details["middle_name"],
            details["last_name"],
            details["contact_number"],
        ),
        True,
    )

def delete_guardian_if_unused(guardian_id):
    if not guardian_id:
        return

    rows = fetch_all(
        """
        SELECT
            (SELECT COUNT(*) FROM student WHERE guardian_id = %s) AS student_count,
            (SELECT COUNT(*) FROM `relationship` WHERE guardian_id = %s) AS relationship_count
        """,
        (guardian_id, guardian_id),
    )
    if rows and rows[0]["student_count"] == 0 and rows[0]["relationship_count"] == 0:
        execute("DELETE FROM guardian WHERE id = %s", (guardian_id,))

def schedule_days(day_text):
    value = (day_text or "").upper().replace(" ", "")
    days = set()
    index = 0
    while index < len(value):
        if value.startswith("TH", index):
            days.add("TH")
            index += 2
            continue
        day = value[index]
        if day in {"M", "T", "W", "F", "S"}:
            days.add(day)
        index += 1
    return days

def time_minutes(value):
    if value is None:
        return None
    text = str(value)
    parts = text.split(":")
    if len(parts) < 2:
        return None
    return int(parts[0]) * 60 + int(parts[1])

def schedules_overlap(left, right):
    if not left or not right:
        return False
    if not (schedule_days(left.get("day")) & schedule_days(right.get("day"))):
        return False
    left_start = time_minutes(left.get("time_start"))
    left_end = time_minutes(left.get("time_end"))
    right_start = time_minutes(right.get("time_start"))
    right_end = time_minutes(right.get("time_end"))
    if None in (left_start, left_end, right_start, right_end):
        return False
    return left_start < right_end and right_start < left_end

def time_key(value):
    if isinstance(value, timedelta):
        seconds = int(value.total_seconds())
        return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}"
    if isinstance(value, time):
        return value.strftime("%H:%M")
    parts = str(value).split(":")
    if len(parts) >= 2:
        return f"{int(parts[0]):02}:{int(parts[1]):02}"
    return str(value)

def schedule_for_id(schedule_id):
    if not schedule_id:
        return None
    rows = fetch_all(
        "SELECT id, day, time_start, time_end FROM schedule WHERE id = %s",
        (schedule_id,),
    )
    return rows[0] if rows else None

def class_offering_schedule_conflict(room, section_id, instructor_id, schedule_id, school_year, sem, exclude_class_id=None):
    target_schedule = schedule_for_id(schedule_id)
    if not target_schedule:
        return None

    rows = fetch_all(
        """
        SELECT co.id, co.room, co.section_id, sec.section_name, co.instructor_id,
               ins.name AS instructor_name, sch.day, sch.time_start, sch.time_end
        FROM class_offering co
        JOIN schedule sch ON sch.id = co.schedule_id
        LEFT JOIN section sec ON sec.id = co.section_id
        LEFT JOIN instructor ins ON ins.id = co.instructor_id
        WHERE co.school_year = %s
          AND co.sem = %s
          AND (%s IS NULL OR co.id <> %s)
          AND (
              (%s IS NOT NULL AND co.section_id = %s)
              OR (%s IS NOT NULL AND co.instructor_id = %s)
              OR (%s <> '' AND co.room = %s)
          )
        """,
        (
            school_year,
            sem,
            exclude_class_id,
            exclude_class_id,
            section_id,
            section_id,
            instructor_id,
            instructor_id,
            room or "",
            room or "",
        ),
    )

    for row in rows:
        if schedules_overlap(target_schedule, row):
            if section_id and row.get("section_id") == section_id:
                return f"Schedule conflict: section {row.get('section_name') or section_id} already has a class at that time."
            if instructor_id and row.get("instructor_id") == instructor_id:
                return f"Schedule conflict: instructor {row.get('instructor_name') or instructor_id} already has a class at that time."
            if room and row.get("room") == room:
                return f"Schedule conflict: room {room} is already used at that time."
    return None

def enrollment_conflict(student_id, class_id, exclude_enrollment_id=None):
    if not student_id or not class_id:
        return "Student and class offering are required."

    duplicate_rows = fetch_all(
        """
        SELECT id
        FROM enrollment
        WHERE student_id = %s
          AND class_id = %s
          AND (%s IS NULL OR id <> %s)
        LIMIT 1
        """,
        (student_id, class_id, exclude_enrollment_id, exclude_enrollment_id),
    )
    if duplicate_rows:
        return "This student is already enrolled in this class offering."

    target_rows = fetch_all(
        """
        SELECT co.id, co.subject_code, co.school_year, co.sem,
               sch.day, sch.time_start, sch.time_end
        FROM class_offering co
        LEFT JOIN schedule sch ON sch.id = co.schedule_id
        WHERE co.id = %s
        """,
        (class_id,),
    )
    if not target_rows:
        return "Class offering not found."

    target = target_rows[0]
    existing_rows = fetch_all(
        """
        SELECT e.id AS enrollment_id, co.id AS class_id, co.subject_code,
               sch.day, sch.time_start, sch.time_end
        FROM enrollment e
        JOIN class_offering co ON co.id = e.class_id
        LEFT JOIN schedule sch ON sch.id = co.schedule_id
        WHERE e.student_id = %s
          AND co.school_year = %s
          AND co.sem = %s
          AND (%s IS NULL OR e.id <> %s)
        """,
        (student_id, target.get("school_year"), target.get("sem"), exclude_enrollment_id, exclude_enrollment_id),
    )

    for row in existing_rows:
        if target.get("subject_code") and row.get("subject_code") == target.get("subject_code"):
            return "This student is already enrolled in this subject for the selected term."
        if schedules_overlap(target, row):
            return "Schedule conflict: this student already has an enrolled class at that time."
    return None

def student_class_allowed(student_id, class_id):
    rows = fetch_all(
        """
        SELECT p.program_name, p.major, sec.section_name
        FROM student st
        JOIN program p ON p.id = st.program_id
        JOIN class_offering co ON co.id = %s
        JOIN curriculum c ON c.program_id = st.program_id
                         AND c.subject_code = co.subject_code
        LEFT JOIN section sec ON sec.id = co.section_id
        WHERE st.student_id = %s
        LIMIT 1
        """,
        (class_id, student_id),
    )
    if not rows:
        return False

    prefix = section_prefix_for_program(rows[0].get("program_name"), rows[0].get("major"))
    section_name = rows[0].get("section_name") or ""
    return not prefix or section_name.startswith(prefix)

def dedupe_programs(cursor):
    cursor.execute("UPDATE program SET major = '' WHERE major IS NULL")
    cursor.execute(
        """
        SELECT program_name, major, MIN(id) AS canonical_id
        FROM program
        GROUP BY program_name, major
        HAVING COUNT(*) > 1
        """
    )
    duplicate_groups = cursor.fetchall()

    for program_name, major, canonical_id in duplicate_groups:
        cursor.execute(
            """
            SELECT id
            FROM program
            WHERE program_name = %s
              AND major = %s
              AND id <> %s
            ORDER BY id
            """,
            (program_name, major, canonical_id),
        )
        duplicate_ids = [row[0] for row in cursor.fetchall()]

        for duplicate_id in duplicate_ids:
            cursor.execute("UPDATE student SET program_id = %s WHERE program_id = %s", (canonical_id, duplicate_id))
            cursor.execute("UPDATE program_history SET program_id = %s WHERE program_id = %s", (canonical_id, duplicate_id))
            cursor.execute(
                "SELECT id, subject_code, year_level, semester FROM curriculum WHERE program_id = %s",
                (duplicate_id,),
            )
            curriculum_rows = cursor.fetchall()

            for curriculum_id, subject_code, year_level, semester in curriculum_rows:
                cursor.execute(
                    """
                    SELECT id
                    FROM curriculum
                    WHERE program_id = %s
                      AND subject_code = %s
                      AND year_level = %s
                      AND semester = %s
                    LIMIT 1
                    """,
                    (canonical_id, subject_code, year_level, semester),
                )
                if cursor.fetchone():
                    cursor.execute("DELETE FROM curriculum WHERE id = %s", (curriculum_id,))
                else:
                    cursor.execute("UPDATE curriculum SET program_id = %s WHERE id = %s", (canonical_id, curriculum_id))

            cursor.execute("DELETE FROM program WHERE id = %s", (duplicate_id,))

    cursor.execute("SHOW INDEX FROM program WHERE Key_name = 'uq_program_major'")
    if not cursor.fetchall():
        cursor.execute("ALTER TABLE program ADD UNIQUE KEY uq_program_major (program_name, major)")

def dedupe_instructors(cursor):
    cursor.execute(
        """
        SELECT MIN(id)
        FROM instructor
        WHERE name = 'KATHLEEN MAE B. STA. ROSA, MBA'
        """
    )
    kathleen_row = cursor.fetchone()
    kathleen_canonical_id = kathleen_row[0] if kathleen_row else None
    if kathleen_canonical_id:
        cursor.execute(
            """
            UPDATE class_offering
            SET instructor_id = %s
            WHERE instructor_id IN (
                SELECT id
                FROM instructor
                WHERE name = 'KATHLEEN MAE B. STA. ROSA'
            )
            """,
            (kathleen_canonical_id,),
        )
    cursor.execute(
        """
        DELETE old_row
        FROM instructor old_row
        JOIN instructor canonical
          ON canonical.name = 'KATHLEEN MAE B. STA. ROSA, MBA'
        WHERE old_row.name = 'KATHLEEN MAE B. STA. ROSA'
        """
    )
    cursor.execute(
        """
        SELECT name, MIN(id) AS canonical_id
        FROM instructor
        GROUP BY name
        HAVING COUNT(*) > 1
        """
    )
    duplicate_groups = cursor.fetchall()

    for name, canonical_id in duplicate_groups:
        cursor.execute(
            "SELECT id FROM instructor WHERE name = %s AND id <> %s ORDER BY id",
            (name, canonical_id),
        )
        duplicate_ids = [row[0] for row in cursor.fetchall()]

        for duplicate_id in duplicate_ids:
            cursor.execute("UPDATE class_offering SET instructor_id = %s WHERE instructor_id = %s", (canonical_id, duplicate_id))
            cursor.execute("DELETE FROM instructor WHERE id = %s", (duplicate_id,))

    cursor.execute("SHOW INDEX FROM instructor WHERE Key_name = 'uq_instructor_name'")
    if not cursor.fetchall():
        cursor.execute("ALTER TABLE instructor ADD UNIQUE KEY uq_instructor_name (name)")

def cleanup_generated_instructors(cursor):
    cursor.execute("SELECT id, name FROM instructor")
    instructors = {name: instructor_id for instructor_id, name in cursor.fetchall()}

    for generated_name, local_name in GENERATED_INSTRUCTOR_REPLACEMENTS.items():
        generated_id = instructors.get(generated_name)
        local_id = instructors.get(local_name)
        if not generated_id or not local_id:
            continue
        cursor.execute(
            "UPDATE class_offering SET instructor_id = %s WHERE instructor_id = %s",
            (local_id, generated_id),
        )
        cursor.execute("DELETE FROM instructor WHERE id = %s", (generated_id,))

    cursor.execute("SELECT id, name FROM instructor")
    instructors = {name: instructor_id for instructor_id, name in cursor.fetchall()}
    for staff_name, replacement_name in GENERATED_STAFF_INSTRUCTOR_REASSIGNMENTS.items():
        staff_id = instructors.get(staff_name)
        replacement_id = instructors.get(replacement_name)
        if not staff_id or not replacement_id:
            continue
        cursor.execute(
            "UPDATE class_offering SET instructor_id = %s WHERE instructor_id = %s",
            (replacement_id, staff_id),
        )
        cursor.execute("DELETE FROM instructor WHERE id = %s", (staff_id,))

    cursor.executemany(
        """
        DELETE ins
        FROM instructor ins
        LEFT JOIN class_offering co ON co.instructor_id = ins.id
        WHERE ins.name = %s
          AND co.id IS NULL
        """,
        [(name,) for name in UNUSED_GENERATED_STAFF_INSTRUCTORS],
    )

def dedupe_schedules(cursor):
    cursor.execute(
        """
        SELECT day, time_start, time_end, MIN(id) AS canonical_id
        FROM schedule
        GROUP BY day, time_start, time_end
        HAVING COUNT(*) > 1
        """
    )
    duplicate_groups = cursor.fetchall()

    for day, time_start, time_end, canonical_id in duplicate_groups:
        cursor.execute(
            """
            SELECT id
            FROM schedule
            WHERE day = %s
              AND time_start = %s
              AND time_end = %s
              AND id <> %s
            ORDER BY id
            """,
            (day, time_start, time_end, canonical_id),
        )
        duplicate_ids = [row[0] for row in cursor.fetchall()]

        for duplicate_id in duplicate_ids:
            cursor.execute("UPDATE class_offering SET schedule_id = %s WHERE schedule_id = %s", (canonical_id, duplicate_id))
            cursor.execute(
                """
                UPDATE IGNORE class_schedule
                SET schedule_id = %s
                WHERE schedule_id = %s
                """,
                (canonical_id, duplicate_id),
            )
            cursor.execute("DELETE FROM class_schedule WHERE schedule_id = %s", (duplicate_id,))
            cursor.execute("DELETE FROM schedule WHERE id = %s", (duplicate_id,))

    cursor.execute("SHOW INDEX FROM schedule WHERE Key_name = 'uq_schedule_slot'")
    if not cursor.fetchall():
        cursor.execute("ALTER TABLE schedule ADD UNIQUE KEY uq_schedule_slot (day, time_start, time_end)")

def dedupe_sections(cursor):
    cursor.execute(
        """
        SELECT section_name, MIN(id) AS canonical_id
        FROM section
        GROUP BY section_name
        HAVING COUNT(*) > 1
        """
    )
    duplicate_groups = cursor.fetchall()

    for section_name, canonical_id in duplicate_groups:
        cursor.execute(
            "SELECT id FROM section WHERE section_name = %s AND id <> %s ORDER BY id",
            (section_name, canonical_id),
        )
        duplicate_ids = [row[0] for row in cursor.fetchall()]
        for duplicate_id in duplicate_ids:
            cursor.execute("UPDATE class_offering SET section_id = %s WHERE section_id = %s", (canonical_id, duplicate_id))
            cursor.execute("DELETE FROM section WHERE id = %s", (duplicate_id,))

    cursor.execute("SHOW INDEX FROM section WHERE Key_name IN ('section_name', 'uq_section_name')")
    if not cursor.fetchall():
        cursor.execute("ALTER TABLE section ADD UNIQUE KEY uq_section_name (section_name)")

def cleanup_generated_sections(cursor):
    cursor.execute("SELECT id, section_name FROM section")
    sections = {name: section_id for section_id, name in cursor.fetchall()}

    for generated_name, local_name in GENERATED_SECTION_REPLACEMENTS.items():
        generated_id = sections.get(generated_name)
        local_id = sections.get(local_name)
        if generated_id and local_id:
            cursor.execute("UPDATE class_offering SET section_id = %s WHERE section_id = %s", (local_id, generated_id))
            cursor.execute("DELETE FROM section WHERE id = %s", (generated_id,))

    for generated_name in GENERATED_SECTIONS_WITHOUT_LOCAL_MATCH:
        generated_id = sections.get(generated_name)
        if not generated_id:
            continue
        cursor.execute("SELECT id FROM class_offering WHERE section_id = %s", (generated_id,))
        class_ids = [row[0] for row in cursor.fetchall()]
        if class_ids:
            cursor.executemany("DELETE FROM class_schedule WHERE class_id = %s", [(class_id,) for class_id in class_ids])
            cursor.executemany("DELETE FROM enrollment WHERE class_id = %s", [(class_id,) for class_id in class_ids])
            cursor.executemany("DELETE FROM class_offering WHERE id = %s", [(class_id,) for class_id in class_ids])
        cursor.execute("DELETE FROM section WHERE id = %s", (generated_id,))

def seed_class_offerings(cursor):
    school_year = current_school_year()

    cursor.execute("SELECT id, section_name FROM section")
    sections = {name: section_id for section_id, name in cursor.fetchall()}

    cursor.execute("SELECT id, name FROM instructor")
    instructors = {name: instructor_id for instructor_id, name in cursor.fetchall()}

    cursor.execute("SELECT id, day, time_start, time_end FROM schedule")
    schedules = {
        (day, time_key(time_start), time_key(time_end)): schedule_id
        for schedule_id, day, time_start, time_end in cursor.fetchall()
    }

    cursor.execute(
        """
        SELECT co.id, co.room, co.section_id, co.instructor_id, co.sem,
               sch.day, sch.time_start, sch.time_end
        FROM class_offering co
        JOIN schedule sch ON sch.id = co.schedule_id
        WHERE co.school_year = %s
        """,
        (school_year,),
    )
    existing_offerings = [
        {
            "id": row[0],
            "room": row[1],
            "section_id": row[2],
            "instructor_id": row[3],
            "sem": row[4],
            "day": row[5],
            "time_start": row[6],
            "time_end": row[7],
        }
        for row in cursor.fetchall()
    ]

    for room, section_name, subject_code, day, time_start, time_end, instructor_name, sem in CLASS_OFFERING_SEEDS:
        section_id = sections.get(section_name)
        instructor_id = instructors.get(instructor_name)
        schedule_id = schedules.get((day, time_start, time_end))
        if not section_id or not instructor_id or not schedule_id:
            continue

        cursor.execute("SELECT subject_code FROM subject WHERE subject_code = %s", (subject_code,))
        if cursor.fetchone() is None:
            continue

        cursor.execute(
            """
            SELECT id, schedule_id
            FROM class_offering
            WHERE section_id = %s
              AND subject_code = %s
              AND school_year = %s
              AND sem = %s
            LIMIT 1
            """,
            (section_id, subject_code, school_year, sem),
        )
        duplicate = cursor.fetchone()
        if duplicate:
            cursor.execute(
                "INSERT IGNORE INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)",
                (duplicate[0], duplicate[1]),
            )
            continue

        target_schedule = {"day": day, "time_start": time_start, "time_end": time_end}
        has_conflict = any(
            row.get("sem") == sem
            and (
                row.get("section_id") == section_id
                or row.get("instructor_id") == instructor_id
                or row.get("room") == room
            )
            and schedules_overlap(target_schedule, row)
            for row in existing_offerings
        )
        if has_conflict:
            continue

        cursor.execute(
            """
            INSERT INTO class_offering
                (room, section_id, subject_code, schedule_id, instructor_id, school_year, sem)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (room, section_id, subject_code, schedule_id, instructor_id, school_year, sem),
        )
        class_id = cursor.lastrowid
        cursor.execute(
            "INSERT IGNORE INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)",
            (class_id, schedule_id),
        )
        existing_offerings.append(
            {
                "id": class_id,
                "room": room,
                "section_id": section_id,
                "instructor_id": instructor_id,
                "sem": sem,
                "day": day,
                "time_start": time_start,
                "time_end": time_end,
            }
        )

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
            sem VARCHAR(30) NOT NULL
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
            status VARCHAR(40) NOT NULL DEFAULT 'Enrolled',
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
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'admin',
            student_id INT NULL
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

        cursor.execute("SHOW COLUMNS FROM enrollment LIKE 'status'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE enrollment ADD COLUMN status VARCHAR(40) NOT NULL DEFAULT 'Enrolled'")

        cursor.execute("ALTER TABLE instructor MODIFY department VARCHAR(180) NULL")
        cursor.execute("ALTER TABLE class_offering MODIFY sem VARCHAR(30) NOT NULL")
        cursor.execute(
            """
            UPDATE class_offering
            SET sem = CASE
                WHEN sem IN ('1', '1st', '1st Sem') THEN '1st Semester'
                WHEN sem IN ('2', '2nd', '2nd Sem') THEN '2nd Semester'
                ELSE sem
            END
            """
        )

        cursor.execute("SHOW COLUMNS FROM user_account LIKE 'role'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE user_account ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'")
        cursor.execute("SHOW COLUMNS FROM user_account LIKE 'student_id'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE user_account ADD COLUMN student_id INT NULL")

        dedupe_programs(cursor)
        dedupe_instructors(cursor)
        cleanup_generated_instructors(cursor)
        dedupe_schedules(cursor)
        dedupe_sections(cursor)
        cleanup_generated_sections(cursor)
        cursor.executemany(
            "INSERT IGNORE INTO program (program_name, major) VALUES (%s, %s)",
            PROGRAM_SEEDS,
        )
        cursor.executemany(
            "INSERT IGNORE INTO schedule (day, time_start, time_end) VALUES (%s, %s, %s)",
            SCHEDULE_SEEDS,
        )
        cursor.executemany(
            "DELETE FROM curriculum WHERE subject_code = %s",
            [(code,) for code, _ in OLD_AUTOMOTIVE_SUBJECT_SEEDS],
        )
        cursor.executemany(
            "UPDATE class_offering SET subject_code = NULL WHERE subject_code = %s",
            [(code,) for code, _ in OLD_AUTOMOTIVE_SUBJECT_SEEDS],
        )
        cursor.executemany(
            "UPDATE subject SET prerequisite_code = NULL WHERE prerequisite_code = %s",
            [(code,) for code, _ in OLD_AUTOMOTIVE_SUBJECT_SEEDS],
        )
        cursor.executemany(
            "DELETE FROM subject WHERE subject_code = %s AND title = %s",
            OLD_AUTOMOTIVE_SUBJECT_SEEDS,
        )
        for program_name, major, subject_seeds in (
            ("Bachelor of Science in Entrepreneurship", "", BS_ENTREPRENEURSHIP_SUBJECT_SEEDS),
            ("Bachelor of Science in Fisheries", "", BS_FISHERIES_SUBJECT_SEEDS),
            ("Bachelor of Technical Vocational Teacher Education", "Automotive Technology", BTVTED_AUTOMOTIVE_SUBJECT_SEEDS),
            ("Bachelor of Technical Vocational Teacher Education", "Computer Hardware Servicing", BTVTED_CHS_SUBJECT_SEEDS),
            ("Bachelor of Technical Vocational Teacher Education", "Heating, Ventilating, and Airconditioning Technology", BTVTED_HVACT_SUBJECT_SEEDS),
        ):
            cursor.executemany(
                """
                INSERT IGNORE INTO subject (subject_code, title, units, prerequisite_code)
                VALUES (%s, %s, %s, %s)
                """,
                [(code, title, units, prerequisite) for code, title, units, prerequisite, _, _ in subject_seeds],
            )
            cursor.executemany(
                """
                UPDATE subject
                SET prerequisite_code = %s
                WHERE subject_code = %s
                  AND title = %s
                """,
                [(prerequisite, code, title) for code, title, _, prerequisite, _, _ in subject_seeds],
            )
            cursor.executemany(
                """
                INSERT IGNORE INTO curriculum (program_id, subject_code, year_level, semester)
                SELECT p.id, %s, %s, %s
                FROM program p
                WHERE p.program_name = %s
                  AND p.major = %s
                """,
                [(code, year_level, semester, program_name, major) for code, _, _, _, year_level, semester in subject_seeds],
            )
        seed_class_offerings(cursor)
        cursor.execute(
            """
            INSERT INTO user_account (username, password, role, student_id)
            VALUES ('admin', '123', 'admin', NULL)
            ON DUPLICATE KEY UPDATE role = 'admin', student_id = NULL
            """
        )
        cursor.execute(
            """
            INSERT IGNORE INTO user_account (username, password, role, student_id)
            SELECT s.lrn, %s, 'student', s.student_id
            FROM student s
            WHERE s.lrn IS NOT NULL
              AND s.lrn <> ''
            """,
            (DEFAULT_STUDENT_PASSWORD,),
        )
        cursor.execute(
            """
            UPDATE user_account ua
            JOIN student s ON s.lrn = ua.username
            SET ua.role = 'student',
                ua.student_id = s.student_id,
                ua.password = %s
            WHERE ua.username <> 'admin'
            """,
            (DEFAULT_STUDENT_PASSWORD,),
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
            """
            SELECT ua.user_id, ua.username, ua.role, ua.student_id,
                   CONCAT_WS(' ', st.first_name, NULLIF(st.middle_name, ''), st.last_name) AS student_name
            FROM user_account ua
            LEFT JOIN student st ON st.student_id = ua.student_id
            WHERE ua.username = %s AND ua.password = %s
            """,
            (data.get("username"), data.get("password")),
        )
        if not rows:
            return jsonify({"success": False, "user": None})

        user = rows[0]
        user["role"] = user.get("role") or "admin"
        token = secrets.token_urlsafe(32)
        ACTIVE_SESSIONS[token] = user
        return jsonify({"success": True, "token": token, "user": user})
    except Error as error:
        return db_error(error)

@app.route("/api/me", methods=["GET"])
def me():
    return jsonify({"user": current_user()})

@app.route("/api/logout", methods=["POST"])
def logout():
    token = get_bearer_token()
    if token:
        ACTIVE_SESSIONS.pop(token, None)
    return jsonify({"message": "Logged out"})

@app.route("/api/students", methods=["GET", "POST"])
def students():
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            if not pick(data, "LRN", "lrn") or not pick(data, "FirstName", "first_name") or not pick(data, "LastName", "last_name"):
                return jsonify({"error": "LRN, first name, and last name are required."}), 400
            guardian_id = optional_int(pick(data, "GuardianID", "guardian_id"))
            guardian_id = save_guardian_details(guardian_details_from_student_payload(data), guardian_id)
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
            sync_student_account(student_id, pick(data, "LRN", "lrn"))
            return jsonify({"message": "Student added", "student_id": student_id}), 201

        return jsonify(fetch_all(
            """
            SELECT s.student_id, s.lrn, s.first_name, s.middle_name, s.last_name, s.birthdate,
                   s.gender, s.address, s.contact_no, s.program_id, p.program_name, p.major,
                   s.guardian_id,
                   CONCAT_WS(' ', g.first_name, NULLIF(g.middle_name, ''), g.last_name) AS guardian_name,
                   g.first_name AS guardian_first_name,
                   g.middle_name AS guardian_middle_name,
                   g.last_name AS guardian_last_name,
                   g.contact_number AS guardian_contact_number,
                   s.relationship_type
            FROM student s
            LEFT JOIN program p ON p.id = s.program_id
            LEFT JOIN guardian g ON g.id = s.guardian_id
            ORDER BY s.student_id
            """
        ))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Error as error:
        return db_error(error)

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        data = request.get_json(silent=True) or {}
        rows = fetch_all("SELECT guardian_id FROM student WHERE student_id = %s", (student_id,))
        if not rows:
            return jsonify({"error": "Student not found."}), 404

        current_guardian_id = rows[0]["guardian_id"]
        submitted_guardian_id = optional_int(pick(data, "GuardianID", "guardian_id"))
        guardian_id = submitted_guardian_id or current_guardian_id
        guardian_id = save_guardian_details(guardian_details_from_student_payload(data), guardian_id)
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
        if current_guardian_id and current_guardian_id != guardian_id:
            delete_guardian_if_unused(current_guardian_id)
        sync_student_account(student_id, pick(data, "LRN", "lrn"))
        return jsonify({"message": "Student updated"})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Error as error:
        return db_error(error)


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        rows = fetch_all("SELECT guardian_id FROM student WHERE student_id = %s", (student_id,))
        guardian_id = rows[0]["guardian_id"] if rows else None
        execute("DELETE FROM user_account WHERE role = 'student' AND student_id = %s", (student_id,))
        execute("DELETE FROM `relationship` WHERE student_id = %s", (student_id,))
        execute("DELETE FROM enrollment WHERE student_id = %s", (student_id,))
        execute("DELETE FROM program_history WHERE student_id = %s", (student_id,))
        execute("DELETE FROM student WHERE student_id = %s", (student_id,))
        delete_guardian_if_unused(guardian_id)
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
        if is_student():
            user = current_user()
            student_id = user.get("student_id") if user else None
            if not student_id:
                return jsonify([])
            return jsonify(fetch_all(
                """
                SELECT sub.subject_code, sub.title, sub.units, sub.prerequisite_code,
                       c.year_level, c.semester, c.program_id, p.program_name, p.major
                FROM student st
                JOIN curriculum c ON c.program_id = st.program_id
                JOIN program p ON p.id = c.program_id
                JOIN subject sub ON sub.subject_code = c.subject_code
                WHERE st.student_id = %s
                ORDER BY
                    CASE c.year_level
                        WHEN '1st Year' THEN 1
                        WHEN '2nd Year' THEN 2
                        WHEN '3rd Year' THEN 3
                        WHEN '4th Year' THEN 4
                        ELSE 99
                    END,
                    CASE c.semester
                        WHEN '1st Semester' THEN 1
                        WHEN '2nd Semester' THEN 2
                        ELSE 99
                    END,
                    c.id
                """,
                (student_id,),
            ))
        return jsonify(fetch_all(
            """
            SELECT subject_code, title, units, prerequisite_code
            FROM subject
            ORDER BY
                CASE
                    WHEN SUBSTRING_INDEX(subject_code, ' ', -1) REGEXP '^[0-9]+$'
                    THEN TRIM(SUBSTRING(subject_code, 1, LENGTH(subject_code) - LENGTH(SUBSTRING_INDEX(subject_code, ' ', -1))))
                    ELSE subject_code
                END,
                CASE
                    WHEN SUBSTRING_INDEX(subject_code, ' ', -1) REGEXP '^[0-9]+$'
                    THEN CAST(SUBSTRING_INDEX(subject_code, ' ', -1) AS UNSIGNED)
                    ELSE 0
                END,
                subject_code
            """
        ))
    except Error as error:
        return db_error(error)

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
            room = pick(data, "Room", "room")
            section_id = optional_int(pick(data, "SectionID", "section_id"))
            instructor_id = optional_int(pick(data, "InstructorID", "instructor_id"))
            school_year = pick(data, "SchoolYear", "school_year")
            sem = pick(data, "Sem", "sem")
            conflict = class_offering_schedule_conflict(room, section_id, instructor_id, schedule_id, school_year, sem)
            if conflict:
                return jsonify({"error": conflict}), 409
            class_id = execute(
                """
                INSERT INTO class_offering (room, section_id, subject_code, schedule_id, instructor_id, school_year, sem)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    room,
                    section_id,
                    optional(pick(data, "SubjectCode", "subject_code")),
                    schedule_id,
                    instructor_id,
                    school_year,
                    sem,
                ),
                True,
            )
            if schedule_id:
                execute("INSERT IGNORE INTO class_schedule (class_id, schedule_id) VALUES (%s, %s)", (class_id, schedule_id))
            return jsonify({"message": "Class offering added", "class_offering_id": class_id}), 201
        extra_join = ""
        where_clause = ""
        params = ()
        if is_student():
            user = current_user()
            student_id = user.get("student_id") if user else None
            program_rows = fetch_all(
                """
                SELECT p.program_name, p.major
                FROM student st
                JOIN program p ON p.id = st.program_id
                WHERE st.student_id = %s
                """,
                (student_id,),
            )
            prefix = section_prefix_for_program(
                program_rows[0].get("program_name") if program_rows else "",
                program_rows[0].get("major") if program_rows else "",
            )
            extra_join = """
            JOIN student current_student ON current_student.student_id = %s
            JOIN curriculum current_curriculum
              ON current_curriculum.program_id = current_student.program_id
             AND current_curriculum.subject_code = co.subject_code
            """
            where_clause = "WHERE (%s = '' OR sec.section_name LIKE %s)"
            params = (student_id, prefix, f"{prefix}%")
        return jsonify(fetch_all(
            f"""
            SELECT co.id AS class_offering_id, co.room, co.section_id, sec.section_name,
                   co.subject_code, sub.title AS subject_title, co.schedule_id,
                   sch.day, sch.time_start, sch.time_end, co.instructor_id,
                   ins.name AS instructor_name, co.school_year, co.sem
            FROM class_offering co
            LEFT JOIN section sec ON sec.id = co.section_id
            LEFT JOIN subject sub ON sub.subject_code = co.subject_code
            LEFT JOIN schedule sch ON sch.id = co.schedule_id
            LEFT JOIN instructor ins ON ins.id = co.instructor_id
            {extra_join}
            {where_clause}
            ORDER BY co.id
            """,
            params,
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/class-offerings/<int:class_id>", methods=["PUT"])
def update_class_offering(class_id):
    try:
        data = request.get_json(silent=True) or {}
        schedule_id = optional_int(pick(data, "ScheduleID", "schedule_id"))
        room = pick(data, "Room", "room")
        section_id = optional_int(pick(data, "SectionID", "section_id"))
        instructor_id = optional_int(pick(data, "InstructorID", "instructor_id"))
        school_year = pick(data, "SchoolYear", "school_year")
        sem = pick(data, "Sem", "sem")
        conflict = class_offering_schedule_conflict(room, section_id, instructor_id, schedule_id, school_year, sem, class_id)
        if conflict:
            return jsonify({"error": conflict}), 409
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
                room,
                section_id,
                optional(pick(data, "SubjectCode", "subject_code")),
                schedule_id,
                instructor_id,
                school_year,
                sem,
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
            user = current_user()
            student_id = user.get("student_id") if user and user.get("role") == "student" else optional_int(pick(data, "StudentID", "student_id"))
            if not student_id:
                return jsonify({"error": "Student account is not linked to a student record."}), 400
            class_id = optional_int(pick(data, "ClassID", "class_id"))
            if user and user.get("role") == "student" and not student_class_allowed(student_id, class_id):
                return jsonify({"error": "This class offering is not part of your curriculum."}), 403
            conflict = enrollment_conflict(student_id, class_id)
            if conflict:
                return jsonify({"error": conflict}), 409
            enrollment_id = execute(
                "INSERT INTO enrollment (student_id, class_id, status) VALUES (%s, %s, %s)",
                (
                    student_id,
                    class_id,
                    optional(pick(data, "Status", "status")) or "Enrolled",
                ),
                True,
            )
            return jsonify({"message": "Enrollment added", "enrollment_id": enrollment_id}), 201

        params = ()
        where_clause = ""
        user = current_user()
        if user and user.get("role") == "student":
            where_clause = "WHERE e.student_id = %s"
            params = (user.get("student_id"),)

        return jsonify(fetch_all(
            """
            SELECT e.id AS enrollment_id, e.student_id,
                   CONCAT_WS(' ', st.first_name, NULLIF(st.middle_name, ''), st.last_name) AS student_name,
                   e.class_id, co.room, co.subject_code, sub.title AS subject_title,
                   sec.section_name, ins.name AS instructor_name, co.school_year, co.sem,
                   sch.day, sch.time_start, sch.time_end, e.status, e.enrollment_timestamp
            FROM enrollment e
            JOIN student st ON st.student_id = e.student_id
            JOIN class_offering co ON co.id = e.class_id
            LEFT JOIN subject sub ON sub.subject_code = co.subject_code
            LEFT JOIN section sec ON sec.id = co.section_id
            LEFT JOIN instructor ins ON ins.id = co.instructor_id
            LEFT JOIN schedule sch ON sch.id = co.schedule_id
            {where_clause}
            ORDER BY e.id DESC
            """.format(where_clause=where_clause),
            params,
        ))
    except Error as error:
        return db_error(error)

@app.route("/api/enrollments/<int:enrollment_id>", methods=["PUT"])
def update_enrollment(enrollment_id):
    try:
        data = request.get_json(silent=True) or {}
        student_id = optional_int(pick(data, "StudentID", "student_id"))
        class_id = optional_int(pick(data, "ClassID", "class_id"))
        conflict = enrollment_conflict(student_id, class_id, enrollment_id)
        if conflict:
            return jsonify({"error": conflict}), 409
        execute(
            "UPDATE enrollment SET student_id = %s, class_id = %s, status = %s WHERE id = %s",
            (
                student_id,
                class_id,
                optional(pick(data, "Status", "status")) or "Enrolled",
                enrollment_id,
            ),
        )
        return jsonify({"message": "Enrollment updated"})
    except Error as error:
        return db_error(error)

@app.route("/api/enrollments/<int:enrollment_id>", methods=["DELETE"])
def delete_enrollment(enrollment_id):
    try:
        if is_student():
            rows = fetch_all("SELECT student_id FROM enrollment WHERE id = %s", (enrollment_id,))
            if not rows:
                return jsonify({"error": "Enrollment not found."}), 404
            if rows[0]["student_id"] != current_user().get("student_id"):
                return jsonify({"error": "You can only change your own enrollment."}), 403
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
            ORDER BY p.program_name,
                     p.major,
                     CASE c.year_level
                         WHEN '1st Year' THEN 1
                         WHEN '2nd Year' THEN 2
                         WHEN '3rd Year' THEN 3
                         WHEN '4th Year' THEN 4
                         ELSE 99
                     END,
                     CASE c.semester
                         WHEN '1st Semester' THEN 1
                         WHEN '2nd Semester' THEN 2
                         ELSE 99
                     END,
                     c.id
            """
        ))
    except Error as error:
        return db_error(error)

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

@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>", methods=["GET"])
def serve_frontend_file(filename):
    if filename in FRONTEND_FILES:
        return send_from_directory(".", filename)
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
        use_reloader=False,
    )
