import os
import sqlite3

# Define database directory and path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_management.db")


def get_db_connection():
    """Returns a SQLite connection with row factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def calculate_grade(total_mark):
    """Calculate academic grade based on total score out of 100."""
    if total_mark >= 90:
        return "A+"
    elif total_mark >= 80:
        return "A"
    elif total_mark >= 70:
        return "B+"
    elif total_mark >= 60:
        return "B"
    elif total_mark >= 50:
        return "C"
    else:
        return "F"


def calculate_performance_status(avg_marks, attendance_pct):
    """Determine performance status using academic marks and attendance."""
    if avg_marks >= 85 and attendance_pct >= 85:
        return "Excellent"
    elif avg_marks >= 70 and attendance_pct >= 75:
        return "Good"
    elif avg_marks >= 50 and attendance_pct >= 65:
        return "Average"
    else:
        return "Needs Improvement"


def init_db():
    """Creates tables if they don't exist and seeds initial sample records."""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Departments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id TEXT PRIMARY KEY,
            department_name TEXT NOT NULL
        )
    """)

    # 2. Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            section TEXT NOT NULL,
            address TEXT,
            admission_year TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department) REFERENCES departments (department_id) ON UPDATE CASCADE
        )
    """)

    # 3. Marks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            internal_mark REAL NOT NULL,
            external_mark REAL NOT NULL,
            total_mark REAL NOT NULL,
            grade TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    """)

    # 4. Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            total_days INTEGER NOT NULL,
            present_days INTEGER NOT NULL,
            absent_days INTEGER NOT NULL,
            attendance_percentage REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # Check if sample data already exists
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    if student_count == 0:
        seed_sample_data(conn)

    conn.close()


def seed_sample_data(conn):
    """Populates departments, 12 realistic students, marks, and attendance."""
    cursor = conn.cursor()

    # Sample Departments
    departments = [
        ("CSBS", "Computer Science and Business Systems"),
        ("CSE", "Computer Science and Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics and Communication Engineering"),
        ("MECH", "Mechanical Engineering")
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO departments (department_id, department_name) VALUES (?, ?)",
        departments
    )

    # 12 Realistic Students
    sample_students = [
        ("STU101", "Aarav Sharma", "aarav.sharma@example.edu", "9876543210", "Male", "2004-05-14", "CSBS", "2nd Year", "A", "14 Anna Nagar, Chennai", "2023"),
        ("STU102", "Priya Sundaram", "priya.sundaram@example.edu", "9876543211", "Female", "2004-08-22", "CSE", "2nd Year", "B", "28 Gandhipuram, Coimbatore", "2023"),
        ("STU103", "Kavya Ramesh", "kavya.ramesh@example.edu", "9876543212", "Female", "2005-01-11", "IT", "1st Year", "A", "45 KK Nagar, Madurai", "2024"),
        ("STU104", "Rohan Verma", "rohan.verma@example.edu", "9876543213", "Male", "2003-11-29", "ECE", "3rd Year", "A", "12 Race Course Road, Trichy", "2022"),
        ("STU105", "Dinesh Kumar", "dinesh.kumar@example.edu", "9876543214", "Male", "2003-03-18", "MECH", "3rd Year", "B", "88 Gandhi Road, Salem", "2022"),
        ("STU106", "Ananya Krishnan", "ananya.k@example.edu", "9876543215", "Female", "2004-09-05", "CSBS", "2nd Year", "A", "19 T. Nagar, Chennai", "2023"),
        ("STU107", "Vignesh Murugan", "vignesh.m@example.edu", "9876543216", "Male", "2002-12-14", "CSE", "4th Year", "A", "5 Velachery Main Rd, Chennai", "2021"),
        ("STU108", "Sneha Patel", "sneha.patel@example.edu", "9876543217", "Female", "2005-04-30", "IT", "1st Year", "B", "31 RS Puram, Coimbatore", "2024"),
        ("STU109", "Mohamed Irfan", "mohamed.irfan@example.edu", "9876543218", "Male", "2003-07-21", "ECE", "3rd Year", "B", "77 Thillai Nagar, Trichy", "2022"),
        ("STU110", "Siddharth Menon", "siddharth.m@example.edu", "9876543219", "Male", "2002-10-09", "MECH", "4th Year", "A", "102 Crosscut Rd, Coimbatore", "2021"),
        ("STU111", "Deepika Balaji", "deepika.b@example.edu", "9876543220", "Female", "2004-02-17", "CSE", "2nd Year", "A", "63 Besant Nagar, Chennai", "2023"),
        ("STU112", "Karthik Rajan", "karthik.rajan@example.edu", "9876543221", "Male", "2004-06-25", "CSBS", "2nd Year", "B", "42 Perur Road, Coimbatore", "2023")
    ]

    cursor.executemany(
        """INSERT INTO students 
           (student_id, name, email, phone, gender, dob, department, year, section, address, admission_year) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        sample_students
    )

    # Sample Marks
    # Subjects: Database Management Systems, Computer Networks, Operating Systems, Data Structures, Computer Architecture
    marks_records = [
        # STU101 (CSBS) - High Performer
        ("STU101", "Database Management Systems", 38, 56),  # 94 -> A+
        ("STU101", "Data Structures", 36, 52),              # 88 -> A
        ("STU101", "Computer Networks", 35, 51),            # 86 -> A
        
        # STU102 (CSE) - Excellent
        ("STU102", "Operating Systems", 39, 58),            # 97 -> A+
        ("STU102", "Database Management Systems", 38, 57),  # 95 -> A+
        ("STU102", "Data Structures", 37, 55),              # 92 -> A+

        # STU103 (IT) - Average
        ("STU103", "Data Structures", 25, 41),              # 66 -> B
        ("STU103", "Computer Networks", 22, 38),            # 60 -> B
        ("STU103", "Operating Systems", 20, 34),            # 54 -> C

        # STU104 (ECE) - Good
        ("STU104", "Computer Architecture", 32, 48),        # 80 -> A
        ("STU104", "Computer Networks", 30, 46),            # 76 -> B+
        ("STU104", "Operating Systems", 33, 49),            # 82 -> A

        # STU105 (MECH) - Needs Improvement / Below
        ("STU105", "Computer Architecture", 18, 28),        # 46 -> F
        ("STU105", "Data Structures", 20, 31),              # 51 -> C
        ("STU105", "Database Management Systems", 19, 29),  # 48 -> F

        # STU106 (CSBS) - Good
        ("STU106", "Database Management Systems", 34, 49),  # 83 -> A
        ("STU106", "Computer Networks", 31, 45),            # 76 -> B+

        # STU107 (CSE) - Excellent
        ("STU107", "Operating Systems", 38, 54),            # 92 -> A+
        ("STU107", "Computer Architecture", 37, 52),        # 89 -> A

        # STU108 (IT) - Average
        ("STU108", "Data Structures", 24, 38),              # 62 -> B
        ("STU108", "Operating Systems", 26, 42),            # 68 -> B

        # STU109 (ECE) - Low/Struggling
        ("STU109", "Computer Architecture", 17, 27),        # 44 -> F
        ("STU109", "Computer Networks", 21, 35),            # 56 -> C

        # STU110 (MECH) - Good
        ("STU110", "Data Structures", 33, 47),              # 80 -> A
        ("STU110", "Computer Architecture", 30, 45),        # 75 -> B+

        # STU111 (CSE) - Excellent
        ("STU111", "Database Management Systems", 39, 57),  # 96 -> A+
        ("STU111", "Operating Systems", 36, 53),            # 89 -> A

        # STU112 (CSBS) - Good
        ("STU112", "Data Structures", 32, 46),              # 78 -> B+
        ("STU112", "Computer Networks", 33, 48)             # 81 -> A
    ]

    for student_id, subject, internal, external in marks_records:
        total = round(internal + external, 2)
        grade = calculate_grade(total)
        cursor.execute(
            """INSERT INTO marks (student_id, subject, internal_mark, external_mark, total_mark, grade)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (student_id, subject, internal, external, total, grade)
        )

    # Attendance Records
    # Format: (student_id, total_days, present_days)
    attendance_records = [
        ("STU101", 90, 84),  # 93.3% -> Excellent
        ("STU102", 90, 88),  # 97.8% -> Excellent
        ("STU103", 90, 62),  # 68.9% -> Low Attendance (Warning)
        ("STU104", 90, 77),  # 85.6% -> Good
        ("STU105", 90, 58),  # 64.4% -> Low Attendance (Warning)
        ("STU106", 90, 81),  # 90.0% -> Excellent
        ("STU107", 90, 86),  # 95.6% -> Excellent
        ("STU108", 90, 72),  # 80.0% -> Good
        ("STU109", 90, 60),  # 66.7% -> Low Attendance (Warning)
        ("STU110", 90, 78),  # 86.7% -> Good
        ("STU111", 90, 87),  # 96.7% -> Excellent
        ("STU112", 90, 79)   # 87.8% -> Good
    ]

    for student_id, total_days, present_days in attendance_records:
        absent_days = total_days - present_days
        percentage = round((present_days / total_days) * 100, 2)
        cursor.execute(
            """INSERT INTO attendance (student_id, total_days, present_days, absent_days, attendance_percentage)
               VALUES (?, ?, ?, ?, ?)""",
            (student_id, total_days, present_days, absent_days, percentage)
        )

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
