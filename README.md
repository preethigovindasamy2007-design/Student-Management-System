# Student Management System

A web-based college mini project developed using **Python Flask, SQLite, HTML5, CSS3, and Vanilla JavaScript**.

The Student Management System provides a centralized platform to manage student information, departments, academic marks, attendance, performance, and institutional reports.

---

## 1. Project Overview

The **Student Management System (SMS)** is a web-based academic management application designed for colleges, institutes, and university departments.

The system helps administrators and faculty members manage student records efficiently instead of depending on manual registers or separate spreadsheets.

The application provides modules for:

- Student management
- Department management
- Marks management
- Attendance tracking
- Student performance analysis
- Dashboard analytics
- Reports generation
- Student search and filtering

The project is designed as a **college-level mini project** with a simple architecture and beginner-friendly implementation.

---

## 2. Problem Statement

In many educational institutions, student information, examination marks, and attendance records are maintained using paper registers or multiple spreadsheets.

This can result in:

- Time-consuming manual data entry.
- Difficulty in calculating marks and grades.
- Manual attendance percentage calculations.
- Difficulty in identifying students with low attendance.
- Data duplication.
- Difficulty in searching student information.
- Difficulty in generating consolidated reports.
- Lack of a centralized student management platform.

The **Student Management System** addresses these problems by providing a centralized web application for storing and managing student academic information.

---

## 3. Objectives

The main objectives of this project are:

- To create a centralized student information management system.
- To store student records securely using SQLite.
- To provide Add, View, Update, and Delete operations.
- To simplify student searching and filtering.
- To automatically calculate total marks and grades.
- To automatically calculate attendance percentages.
- To identify students with attendance below 75%.
- To provide student performance information.
- To display useful statistics using charts.
- To generate simple institutional reports.
- To provide a simple and user-friendly interface.

---

## 4. Technologies Used

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML5 | Web page structure |
| Styling | CSS3 | Responsive and modern UI |
| Frontend Interaction | Vanilla JavaScript | Search, filtering, modals and interactions |
| Backend | Python Flask | Server-side application and routing |
| Database | SQLite | Store student and academic data |
| Templates | Jinja2 | Dynamic HTML rendering |
| Charts | Chart.js | Dashboard data visualization |

### Technologies Not Used

This project does not use:

- React
- Angular
- Vue
- Node.js
- PHP
- Java
- Bootstrap
- Other frontend frameworks

The project uses a lightweight and beginner-friendly technology stack.

---

# 5. Main Features and Modules

## 5.1 Dashboard

The dashboard is the main page of the application.

It displays:

- Total Students
- Total Departments
- Average Attendance
- Good Performance Students
- Low Attendance Students
- Recent Students
- Department-wise student distribution
- Attendance statistics

The dashboard provides a quick overview of the overall student data.

---

## 5.2 Student Management

The Student Management module allows administrators to manage student information.

### Student Details

Each student record contains:

- Student ID
- Student Name
- Email
- Phone Number
- Gender
- Date of Birth
- Department
- Year
- Section
- Address
- Admission Year

### Operations

The system supports:

- Add Student
- View Student
- Edit Student
- Delete Student
- Search Student
- Filter Student

---

## 5.3 Add Student

The Add Student page provides a form for entering new student information.

The form includes:

- Student ID
- Name
- Email
- Phone
- Gender
- Date of Birth
- Department
- Year
- Section
- Address
- Admission Year

### Validation

The system validates:

- Required fields
- Email format
- Phone number
- Duplicate Student ID
- Duplicate email

Invalid information produces a clear error message instead of crashing the application.

---

## 5.4 Search and Filtering

The Student Directory provides search and filtering functionality.

Students can be searched using:

- Student ID
- Student Name
- Department
- Year

Students can also be filtered by:

- Department
- Year
- Section

This helps administrators quickly locate student records.

---

## 5.5 Department Management

The Department Management module maintains the list of academic departments.

Sample departments include:

- Computer Science and Business Systems
- Computer Science and Engineering
- Information Technology
- Electronics and Communication Engineering
- Mechanical Engineering

The department page displays:

- Department ID
- Department Name
- Number of Students

New departments can also be added when required.

---

# 6. Marks Management

The Marks Management module stores and manages student academic marks.

### Sample Subjects

- Database Management Systems
- Computer Networks
- Operating Systems
- Data Structures
- Computer Architecture

### Marks Structure

The project uses:

- Internal Mark: Maximum 40
- External Mark: Maximum 60
- Total Mark: Maximum 100

The total mark is automatically calculated.

### Formula

```text
Total Mark = Internal Mark + External Mark