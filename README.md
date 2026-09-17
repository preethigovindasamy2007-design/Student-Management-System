# Student Management System

A web-based mini project developed with **Python Flask**, **SQLite**, and **Vanilla HTML5/CSS3/JavaScript**.

---

## 1. Project Overview

The **Student Management System (SMS)** is an academic management web application designed for colleges, institutes, and university departments. It simplifies and automates student record management, subject marks grading, daily/semester attendance tracking, holistic student performance evaluation, and executive report generation.

---

## 2. Problem Statement

In many institutions, student data, internal examination marks, and attendance registers are tracked using disparate spreadsheets or manual paper ledgers. This leads to:
- Time-consuming manual calculations for grades and attendance percentages.
- High risk of data duplication and transcription errors.
- Difficulty in quickly identifying struggling students or attendance defaulters (< 75%).
- Cumbersome processes for producing consolidated institutional reports.

The **Student Management System** resolves these challenges by providing a centralized, responsive, and automated platform.

---

## 3. Objectives

- **Centralized Data Storage**: Maintain a single source of truth for student bio-data, departments, marks, and attendance.
- **Automated Grade & Attendance Calculations**: Instantly calculate total marks, letter grades ($A+$, $A$, $B+$, $B$, $C$, $F$), and attendance percentages without manual intervention.
- **Early Defaulter Identification**: Automatically alert administrators about students falling below the mandatory 75% attendance threshold.
- **Visual Analytics**: Provide dynamic charts for department-wise student distribution and attendance status via Chart.js.
- **Zero-Dependency Frontend**: Utilize pure HTML5, modern Vanilla CSS3, and Vanilla JavaScript without bloated frameworks.

---

## 4. Technologies Used

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, Vanilla JavaScript | Custom navy design system, responsive layout, CSS variables, micro-animations |
| **Backend** | Python 3 + Flask 3.x | Lightweight WSGI web framework, REST API endpoints, Jinja2 templating |
| **Database** | SQLite 3 | Embedded, zero-configuration relational database with foreign key support |
| **Data Visualization** | Chart.js (CDN) | Interactive bar and doughnut charts |

> [!NOTE]
> No heavy frontend frameworks (React, Angular, Vue, Bootstrap) or heavy backend platforms (Java, PHP, Node.js) are used, making it lightweight and beginner-friendly.

---

## 5. Main Features & Modules

### 1. Modern Dashboard (`/`)
- KPI summary cards: Total Students, Total Departments, Average Attendance %, Good Performance Count, and Low Attendance (< 75%) Count.
- Department-wise student enrollment chart.
- Attendance health breakdown chart (Good $\ge 75\%$ vs Low $< 75\%$).
- Recent students table with quick action links.

### 2. Student Directory (`/students`)
- Full student listing with searchable Student ID, Name, Department, Year, Section, Contact, and Attendance status.
- Real-time client-side and server-side search.
- Multi-criteria filtering by Department, Year, and Section.
- Interactive **Student Profile Modal** displaying personal details, marks roster, and attendance records.
- Edit and Delete actions with confirmation safety.

### 3. Add & Edit Student (`/add-student`, `/edit-student/<id>`)
- Form validation: Required fields check, email format verification, 10-digit phone verification, and duplicate ID prevention.
- Safe modification without altering primary keys.

### 4. Department Management (`/departments`)
- Department catalog displaying active student enrollment counts.
- Add department form for registering new academic branches.

### 5. Marks Management (`/marks`, `/add-marks`)
- Evaluation tracking for subjects:
  - *Database Management Systems*
  - *Computer Networks*
  - *Operating Systems*
  - *Data Structures*
  - *Computer Architecture*
- Automatic calculation: $\text{Total} = \text{Internal (max 40)} + \text{External (max 60)}$.
- Dynamic Grade Assignment:
  - $90 - 100 \rightarrow \mathbf{A+}$
  - $80 - 89 \rightarrow \mathbf{A}$
  - $70 - 79 \rightarrow \mathbf{B+}$
  - $60 - 69 \rightarrow \mathbf{B}$
  - $50 - 59 \rightarrow \mathbf{C}$
  - Below $50 \rightarrow \mathbf{F}$ (Fail)

### 6. Attendance Tracking (`/attendance`, `/add-attendance`)
- Tracks Total Working Days, Days Present, and Days Absent.
- Automated calculation: $\text{Attendance \%} = \left(\frac{\text{Present Days}}{\text{Total Days}}\right) \times 100$.
- Status categorization:
  - $\ge 90\% \rightarrow \text{Excellent}$
  - $75\% - 89\% \rightarrow \text{Good}$
  - $< 75\% \rightarrow \text{Low Attendance Warning (Alert)}$

### 7. Holistic Student Performance (`/performance`)
- Aggregates average marks across all subjects and correlates them with attendance.
- Assigns holistic performance status:
  - **Excellent**: Average marks $\ge 85$ and Attendance $\ge 85\%$
  - **Good**: Average marks $\ge 70$ and Attendance $\ge 75\%$
  - **Average**: Average marks $\ge 50$ and Attendance $\ge 65\%$
  - **Needs Improvement**: Otherwise

### 8. Institutional Reports & Print (`/reports`)
- Executive summary metrics and department-wise averages.
- Top academic achievers list (marks $\ge 80$).
- Attendance defaulter roster.
- Print-ready stylesheet (`@media print`) for generating PDF reports via browser print (`Ctrl+P` / `window.print()`).

### 9. About Project (`/about`)
- Presentation documentation, architectural breakdown, schema diagrams, and viva interview preparation.

---

## 6. System Architecture

```text
+-------------------------------------------------------------+
|                 Web Browser (Client Layer)                  |
|     HTML5 + Vanilla CSS3 (Navy Theme) + Vanilla JS (ES6)     |
|                Chart.js for Visual Analytics                |
+-------------------------------------------------------------+
                              |
                     HTTP GET / POST / API
                              |
+-------------------------------------------------------------+
|                 Flask Server (Backend Layer)                |
|      - app.py (Routes, Form Handlers, Validation, APIs)     |
|      - Jinja2 Template Engine (base.html, index.html...)    |
|      - Business Logic (Grade, Attendance & Status Helpers)  |
+-------------------------------------------------------------+
                              |
                        sqlite3 driver
                              |
+-------------------------------------------------------------+
|               SQLite Database (Persistence Layer)           |
|                database/student_management.db               |
|         Tables: departments, students, marks, attendance    |
+-------------------------------------------------------------+
```

---

## 7. Database Design & Schema

SQLite database location: `database/student_management.db`

### 1. `departments` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `department_id` | TEXT | PRIMARY KEY | Short code (e.g. `CSBS`, `CSE`, `IT`) |
| `department_name` | TEXT | NOT NULL | Full department title |

### 2. `students` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | TEXT | PRIMARY KEY | Unique ID (e.g. `STU101`) |
| `name` | TEXT | NOT NULL | Student's full name |
| `email` | TEXT | NOT NULL, UNIQUE | Student email address |
| `phone` | TEXT | NOT NULL | Contact number |
| `gender` | TEXT | NOT NULL | Gender |
| `dob` | TEXT | NOT NULL | Date of birth (YYYY-MM-DD) |
| `department` | TEXT | NOT NULL, FK | References `departments(department_id)` |
| `year` | TEXT | NOT NULL | Year of study (e.g. 2nd Year) |
| `section` | TEXT | NOT NULL | Section (A, B, C) |
| `address` | TEXT | NULLABLE | Residential address |
| `admission_year` | TEXT | NOT NULL | Year of enrollment (e.g. 2023) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

### 3. `marks` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `mark_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `student_id` | TEXT | NOT NULL, FK | References `students(student_id)` |
| `subject` | TEXT | NOT NULL | Subject name |
| `internal_mark` | REAL | NOT NULL | Internal test score (0 - 40) |
| `external_mark` | REAL | NOT NULL | Semester exam score (0 - 60) |
| `total_mark` | REAL | NOT NULL | Sum of internal + external |
| `grade` | TEXT | NOT NULL | Calculated grade (A+, A, B+, B, C, F) |

### 4. `attendance` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `attendance_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `student_id` | TEXT | NOT NULL, UNIQUE, FK | References `students(student_id)` |
| `total_days` | INTEGER | NOT NULL | Total semester working days |
| `present_days` | INTEGER | NOT NULL | Days attended |
| `absent_days` | INTEGER | NOT NULL | Days absent ($Total - Present$) |
| `attendance_percentage` | REAL | NOT NULL | Calculated percentage |

---

## 8. Project Structure

```text
Student Management system/
│
├── app.py                      # Flask routes, API endpoints and application entry
├── requirements.txt            # Python dependencies (Flask)
├── README.md                   # Complete documentation and viva guide
│
├── database/
│   ├── db.py                   # DB connection, schema creation and seed script
│   └── student_management.db   # SQLite database file (auto-generated)
│
├── static/
│   ├── css/
│   │   └── style.css           # Vanilla CSS responsive design system
│   └── js/
│       ├── main.js             # Live search, filters, modals, mobile drawer
│       └── charts.js           # Chart.js analytics controller
│
└── templates/
    ├── base.html               # Shared layout, sidebar navigation, top bar
    ├── index.html              # Modern dashboard with KPI cards and charts
    ├── students.html           # Student directory, search & preview modal
    ├── add_student.html        # Add student form with validation
    ├── edit_student.html       # Edit student details form
    ├── departments.html        # Department catalog and registration
    ├── marks.html              # Academic marks entry and grade calculation
    ├── attendance.html         # Attendance tracking and warning alerts
    ├── performance.html        # Holistic student performance analysis
    ├── reports.html            # Printable institutional reports
    └── about.html              # Architecture & viva presentation guide
```

---

## 9. Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your machine.
- Web browser (Chrome, Firefox, Edge, Safari).

### Step 1: Clone or Navigate to Project Directory
```bash
cd "Student Management system"
```

### Step 2: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

> [!TIP]
> The database and sample data are initialized automatically on first startup. You will immediately see 12 sample students across CSBS, CSE, IT, ECE, and MECH departments with marks, attendance records, and dashboard charts!

---

## 10. REST API Endpoints

| Method | Endpoint | Description | Response Type |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard` | KPI metrics, department distribution, attendance breakdown | JSON |
| `GET` | `/api/students` | Get all students (supports `?search=`, `?department=`, `?year=`) | JSON |
| `POST` | `/api/students` | Create student record | JSON |
| `GET` | `/api/students/<id>` | Get single student details with marks & attendance | JSON |
| `PUT` | `/api/students/<id>` | Update student information | JSON |
| `DELETE` | `/api/students/<id>` | Delete student and cascading marks/attendance | JSON |
| `GET` | `/api/departments` | List all departments with student enrollment counts | JSON |
| `GET` | `/api/marks/<id>` | Get marks list for student | JSON |
| `GET` | `/api/attendance/<id>` | Get attendance record for student | JSON |

---

## 11. Viva Voce Questions & Answers

### Q1: What architecture does this application follow?
**Answer**: It follows the **MVC (Model-View-Controller)** pattern.
- **Model**: SQLite database tables managed via `database/db.py`.
- **View**: Jinja2 templates (`templates/*.html`) rendered with modern CSS.
- **Controller**: Python Flask route functions in `app.py` that handle HTTP requests, validate input, perform calculations, and return responses.

### Q2: Why choose SQLite over MySQL or PostgreSQL for this mini project?
**Answer**: SQLite is serverless, zero-configuration, lightweight, and stores the entire database in a single disk file (`student_management.db`). This makes the project portable and ideal for college demonstrations without requiring external database servers to be installed or running.

### Q3: How is data integrity maintained when deleting a student?
**Answer**: The database schema uses Foreign Keys with `ON DELETE CASCADE`. In addition, SQLite foreign keys are explicitly enabled via `PRAGMA foreign_keys = ON;`. Deleting a student automatically removes their associated marks and attendance records.

### Q4: How is attendance percentage and warning calculated?
**Answer**:
$$\text{Attendance Percentage} = \frac{\text{Present Days}}{\text{Total Working Days}} \times 100$$
If the percentage is below $75\%$, a warning badge and alert are triggered, highlighting the student on the dashboard and report pages.

### Q5: How are duplicate records prevented?
**Answer**:
- `student_id` is defined as a `PRIMARY KEY`.
- `email` has a `UNIQUE` constraint.
- Flask validates the presence of existing IDs/emails before issuing SQL `INSERT` statements, flashing clear error notifications to the user without crashing the app.

---

## 12. Future Enhancements

- **User Authentication**: Add Role-Based Access Control (Admin, Faculty, and Student login portals).
- **Batch CSV/Excel Import**: Enable bulk student enrollment via Excel/CSV file upload.
- **Automated Email / SMS Notifications**: Automatically send email or SMS alerts to parents when attendance drops below $75\%$.
- **Fee Management Module**: Track tuition, lab fees, and fee payment receipts.
