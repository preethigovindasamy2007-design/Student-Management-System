import os
import re
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
from database.db import (
    init_db,
    get_db_connection,
    calculate_grade,
    calculate_performance_status
)

app = Flask(__name__)
app.secret_key = "student-management-secret-key-college-demo"

# Initialize database upon startup
init_db()


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def is_valid_email(email):
    """Simple regex email validator."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """Validate 10-digit phone number."""
    cleaned = re.sub(r"[\s\-\+]", "", phone)
    return len(cleaned) >= 10 and cleaned.isdigit()


# ---------------------------------------------------------
# Page Routes
# ---------------------------------------------------------

@app.route("/")
def index():
    """Dashboard / Overview Page."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Departments
    cursor.execute("SELECT COUNT(*) FROM departments")
    total_departments = cursor.fetchone()[0]

    # Average Attendance
    cursor.execute("SELECT AVG(attendance_percentage) FROM attendance")
    avg_attendance_row = cursor.fetchone()[0]
    avg_attendance = round(avg_attendance_row, 1) if avg_attendance_row else 0.0

    # Low Attendance Count (< 75%)
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE attendance_percentage < 75")
    low_attendance_count = cursor.fetchone()[0]

    # Students with Good Attendance (>= 75%)
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE attendance_percentage >= 75")
    good_attendance_count = cursor.fetchone()[0]

    # Performance calculation for all students
    cursor.execute("""
        SELECT s.student_id, s.name, s.department,
               COALESCE(AVG(m.total_mark), 0) AS avg_mark,
               COALESCE(a.attendance_percentage, 0) AS attendance_pct
        FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
    """)
    perf_rows = cursor.fetchall()

    good_performance_count = 0
    for row in perf_rows:
        status = calculate_performance_status(row["avg_mark"], row["attendance_pct"])
        if status in ["Excellent", "Good"]:
            good_performance_count += 1

    # Recent Students (latest 6)
    cursor.execute("""
        SELECT s.*, d.department_name 
        FROM students s
        LEFT JOIN departments d ON s.department = d.department_id
        ORDER BY s.created_at DESC LIMIT 6
    """)
    recent_students = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_departments=total_departments,
        avg_attendance=avg_attendance,
        good_performance_count=good_performance_count,
        low_attendance_count=low_attendance_count,
        good_attendance_count=good_attendance_count,
        recent_students=recent_students
    )


@app.route("/students")
def students_view():
    """Student Directory with search & filters."""
    search = request.args.get("search", "").strip()
    dept_filter = request.args.get("department", "").strip()
    year_filter = request.args.get("year", "").strip()
    section_filter = request.args.get("section", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.*, d.department_name,
               COALESCE(a.attendance_percentage, 0) as attendance_pct
        FROM students s
        LEFT JOIN departments d ON s.department = d.department_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (s.student_id LIKE ? OR s.name LIKE ? OR s.email LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    if dept_filter:
        query += " AND s.department = ?"
        params.append(dept_filter)

    if year_filter:
        query += " AND s.year = ?"
        params.append(year_filter)

    if section_filter:
        query += " AND s.section = ?"
        params.append(section_filter)

    query += " ORDER BY s.student_id ASC"

    cursor.execute(query, params)
    students_list = cursor.fetchall()

    # Get department list for filter dropdown
    cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
    departments = cursor.fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students_list,
        departments=departments,
        search=search,
        selected_dept=dept_filter,
        selected_year=year_filter,
        selected_section=section_filter
    )


@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    """Add a new student with validation."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        dob = request.form.get("dob", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        section = request.form.get("section", "").strip()
        address = request.form.get("address", "").strip()
        admission_year = request.form.get("admission_year", "").strip()

        # Validation
        if not all([student_id, name, email, phone, gender, dob, department, year, section, admission_year]):
            flash("All fields marked with an asterisk are required!", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("add_student.html", departments=departments, form=request.form)

        if not is_valid_email(email):
            flash("Please provide a valid email address (e.g., student@college.edu).", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("add_student.html", departments=departments, form=request.form)

        if not is_valid_phone(phone):
            flash("Phone number should be at least 10 valid digits.", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("add_student.html", departments=departments, form=request.form)

        # Check for duplicate student_id or email
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if cursor.fetchone():
            flash(f"Student ID '{student_id}' is already registered! Please use a unique ID.", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("add_student.html", departments=departments, form=request.form)

        cursor.execute("SELECT email FROM students WHERE email = ?", (email,))
        if cursor.fetchone():
            flash(f"Email '{email}' is already associated with another student.", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("add_student.html", departments=departments, form=request.form)

        # Insert new student
        try:
            cursor.execute("""
                INSERT INTO students (student_id, name, email, phone, gender, dob, department, year, section, address, admission_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, email, phone, gender, dob, department, year, section, address, admission_year))

            # Initialize a default attendance entry (e.g. 0/0 or standard 90/90)
            cursor.execute("""
                INSERT INTO attendance (student_id, total_days, present_days, absent_days, attendance_percentage)
                VALUES (?, 90, 85, 5, 94.44)
            """, (student_id,))

            conn.commit()
            conn.close()
            flash(f"Student '{name}' ({student_id}) has been added successfully!", "success")
            return redirect(url_for("students_view"))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f"Database error while saving student: {str(e)}", "error")
            return redirect(url_for("add_student"))

    cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
    departments = cursor.fetchall()
    conn.close()
    return render_template("add_student.html", departments=departments, form={})


@app.route("/edit-student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    """Edit student details."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        flash(f"Student with ID '{student_id}' not found.", "error")
        return redirect(url_for("students_view"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        gender = request.form.get("gender", "").strip()
        dob = request.form.get("dob", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        section = request.form.get("section", "").strip()
        address = request.form.get("address", "").strip()
        admission_year = request.form.get("admission_year", "").strip()

        if not all([name, email, phone, gender, dob, department, year, section, admission_year]):
            flash("All fields marked with an asterisk are required!", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("edit_student.html", student=student, departments=departments)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("edit_student.html", student=student, departments=departments)

        if not is_valid_phone(phone):
            flash("Please enter a valid phone number (at least 10 digits).", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("edit_student.html", student=student, departments=departments)

        # Check if email changed and is taken
        cursor.execute("SELECT student_id FROM students WHERE email = ? AND student_id != ?", (email, student_id))
        if cursor.fetchone():
            flash(f"Email '{email}' is already in use by another student.", "error")
            cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
            departments = cursor.fetchall()
            conn.close()
            return render_template("edit_student.html", student=student, departments=departments)

        try:
            cursor.execute("""
                UPDATE students
                SET name = ?, email = ?, phone = ?, gender = ?, dob = ?,
                    department = ?, year = ?, section = ?, address = ?, admission_year = ?
                WHERE student_id = ?
            """, (name, email, phone, gender, dob, department, year, section, address, admission_year, student_id))
            conn.commit()
            conn.close()
            flash(f"Details for student '{name}' ({student_id}) updated successfully!", "success")
            return redirect(url_for("students_view"))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f"Error updating student: {str(e)}", "error")
            return redirect(url_for("edit_student", student_id=student_id))

    cursor.execute("SELECT * FROM departments ORDER BY department_name ASC")
    departments = cursor.fetchall()
    conn.close()
    return render_template("edit_student.html", student=student, departments=departments)


@app.route("/delete-student/<student_id>", methods=["GET", "POST"])
def delete_student(student_id):
    """Delete a student and cascading records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        flash(f"Student ID '{student_id}' does not exist.", "error")
        return redirect(url_for("students_view"))

    student_name = student["name"]
    try:
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()
        flash(f"Student '{student_name}' ({student_id}) and related records deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        conn.close()
        flash(f"Failed to delete student: {str(e)}", "error")

    return redirect(url_for("students_view"))


@app.route("/departments", methods=["GET", "POST"])
def departments_view():
    """Department listing and addition."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        dept_id = request.form.get("department_id", "").strip().upper()
        dept_name = request.form.get("department_name", "").strip()

        if not dept_id or not dept_name:
            flash("Both Department Code and Department Name are required.", "error")
        else:
            cursor.execute("SELECT department_id FROM departments WHERE department_id = ?", (dept_id,))
            if cursor.fetchone():
                flash(f"Department code '{dept_id}' already exists!", "error")
            else:
                try:
                    cursor.execute("INSERT INTO departments (department_id, department_name) VALUES (?, ?)", (dept_id, dept_name))
                    conn.commit()
                    flash(f"Department '{dept_name}' ({dept_id}) added successfully!", "success")
                except Exception as e:
                    conn.rollback()
                    flash(f"Database error: {str(e)}", "error")

    cursor.execute("""
        SELECT d.department_id, d.department_name, COUNT(s.student_id) as student_count
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department
        GROUP BY d.department_id, d.department_name
        ORDER BY d.department_name ASC
    """)
    departments = cursor.fetchall()
    conn.close()

    return render_template("departments.html", departments=departments)


@app.route("/marks", methods=["GET"])
def marks_view():
    """Marks overview and entry page."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all marks with student info
    cursor.execute("""
        SELECT m.*, s.name as student_name, s.department, s.year, s.section
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        ORDER BY s.student_id ASC, m.subject ASC
    """)
    marks_list = cursor.fetchall()

    # Fetch students for dropdown in add marks modal/form
    cursor.execute("SELECT student_id, name, department FROM students ORDER BY student_id ASC")
    students = cursor.fetchall()

    conn.close()
    return render_template("marks.html", marks=marks_list, students=students)


@app.route("/add-marks", methods=["POST"])
def add_marks():
    """Add or update marks for a student."""
    student_id = request.form.get("student_id", "").strip()
    subject = request.form.get("subject", "").strip()
    internal_str = request.form.get("internal_mark", "").strip()
    external_str = request.form.get("external_mark", "").strip()

    if not all([student_id, subject, internal_str, external_str]):
        flash("All fields are required to record marks.", "error")
        return redirect(url_for("marks_view"))

    try:
        internal_mark = float(internal_str)
        external_mark = float(external_str)

        if internal_mark < 0 or internal_mark > 40:
            flash("Internal mark must be between 0 and 40.", "error")
            return redirect(url_for("marks_view"))

        if external_mark < 0 or external_mark > 60:
            flash("External mark must be between 0 and 60.", "error")
            return redirect(url_for("marks_view"))

        total_mark = round(internal_mark + external_mark, 2)
        grade = calculate_grade(total_mark)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if mark record already exists for this student and subject
        cursor.execute("SELECT mark_id FROM marks WHERE student_id = ? AND subject = ?", (student_id, subject))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE marks
                SET internal_mark = ?, external_mark = ?, total_mark = ?, grade = ?
                WHERE mark_id = ?
            """, (internal_mark, external_mark, total_mark, grade, existing["mark_id"]))
            flash(f"Marks for {subject} updated successfully! Total: {total_mark}, Grade: {grade}", "success")
        else:
            cursor.execute("""
                INSERT INTO marks (student_id, subject, internal_mark, external_mark, total_mark, grade)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, subject, internal_mark, external_mark, total_mark, grade))
            flash(f"Marks for {subject} recorded successfully! Total: {total_mark}, Grade: {grade}", "success")

        conn.commit()
        conn.close()
    except ValueError:
        flash("Please enter valid numeric marks.", "error")
    except Exception as e:
        flash(f"Error saving marks: {str(e)}", "error")

    return redirect(url_for("marks_view"))


@app.route("/delete-mark/<int:mark_id>", methods=["GET", "POST"])
def delete_mark(mark_id):
    """Delete a marks entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM marks WHERE mark_id = ?", (mark_id,))
    conn.commit()
    conn.close()
    flash("Mark record deleted successfully.", "success")
    return redirect(url_for("marks_view"))


@app.route("/attendance", methods=["GET"])
def attendance_view():
    """Attendance management page."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.*, s.name as student_name, s.department, s.year, s.section
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.attendance_percentage ASC
    """)
    attendance_records = cursor.fetchall()

    cursor.execute("SELECT student_id, name, department FROM students ORDER BY student_id ASC")
    students = cursor.fetchall()

    conn.close()
    return render_template("attendance.html", attendance_records=attendance_records, students=students)


@app.route("/add-attendance", methods=["POST"])
def add_attendance():
    """Add or update attendance record."""
    student_id = request.form.get("student_id", "").strip()
    total_days_str = request.form.get("total_days", "").strip()
    present_days_str = request.form.get("present_days", "").strip()

    if not all([student_id, total_days_str, present_days_str]):
        flash("All fields are required to update attendance.", "error")
        return redirect(url_for("attendance_view"))

    try:
        total_days = int(total_days_str)
        present_days = int(present_days_str)

        if total_days <= 0:
            flash("Total working days must be greater than 0.", "error")
            return redirect(url_for("attendance_view"))

        if present_days < 0 or present_days > total_days:
            flash("Present days cannot be negative or exceed total working days!", "error")
            return redirect(url_for("attendance_view"))

        absent_days = total_days - present_days
        percentage = round((present_days / total_days) * 100, 2)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT attendance_id FROM attendance WHERE student_id = ?", (student_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE attendance
                SET total_days = ?, present_days = ?, absent_days = ?, attendance_percentage = ?
                WHERE student_id = ?
            """, (total_days, present_days, absent_days, percentage, student_id))
            flash(f"Attendance updated: {present_days}/{total_days} days ({percentage}%).", "success")
        else:
            cursor.execute("""
                INSERT INTO attendance (student_id, total_days, present_days, absent_days, attendance_percentage)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, total_days, present_days, absent_days, percentage))
            flash(f"Attendance recorded: {present_days}/{total_days} days ({percentage}%).", "success")

        conn.commit()
        conn.close()
    except ValueError:
        flash("Days must be valid integers.", "error")
    except Exception as e:
        flash(f"Error saving attendance: {str(e)}", "error")

    return redirect(url_for("attendance_view"))


@app.route("/performance")
def performance_view():
    """Holistic Student Performance module."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.student_id, s.name, s.department, s.year, s.section,
               COUNT(m.mark_id) as subjects_evaluated,
               COALESCE(AVG(m.total_mark), 0) as avg_marks,
               COALESCE(a.attendance_percentage, 0) as attendance_pct
        FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
        ORDER BY avg_marks DESC
    """)
    rows = cursor.fetchall()

    performance_data = []
    for r in rows:
        avg_m = round(r["avg_marks"], 1)
        att_p = round(r["attendance_pct"], 1)
        grade = calculate_grade(avg_m) if r["subjects_evaluated"] > 0 else "N/A"
        status = calculate_performance_status(avg_m, att_p) if r["subjects_evaluated"] > 0 else "Incomplete"
        performance_data.append({
            "student_id": r["student_id"],
            "name": r["name"],
            "department": r["department"],
            "year": r["year"],
            "section": r["section"],
            "subjects_evaluated": r["subjects_evaluated"],
            "avg_marks": avg_m,
            "attendance_pct": att_p,
            "grade": grade,
            "status": status
        })

    conn.close()
    return render_template("performance.html", performance=performance_data)


@app.route("/reports")
def reports_view():
    """Printable Reports page with consolidated statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Overall Summary Metrics
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM departments")
    total_departments = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(attendance_percentage) FROM attendance")
    avg_att_row = cursor.fetchone()[0]
    avg_attendance = round(avg_att_row, 1) if avg_att_row else 0.0

    cursor.execute("SELECT AVG(total_mark) FROM marks")
    avg_marks_row = cursor.fetchone()[0]
    avg_marks = round(avg_marks_row, 1) if avg_marks_row else 0.0

    # Department-wise breakdown
    cursor.execute("""
        SELECT d.department_id, d.department_name,
               COUNT(DISTINCT s.student_id) as student_count,
               COALESCE(AVG(a.attendance_percentage), 0) as dept_avg_att,
               COALESCE(AVG(m.total_mark), 0) as dept_avg_mark
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department
        LEFT JOIN attendance a ON s.student_id = a.student_id
        LEFT JOIN marks m ON s.student_id = m.student_id
        GROUP BY d.department_id, d.department_name
        ORDER BY d.department_name ASC
    """)
    dept_summary = cursor.fetchall()

    # Top Achievers
    cursor.execute("""
        SELECT s.student_id, s.name, s.department,
               ROUND(AVG(m.total_mark), 1) as avg_mark,
               COALESCE(a.attendance_percentage, 0) as attendance_pct
        FROM students s
        JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
        HAVING AVG(m.total_mark) >= 80
        ORDER BY avg_mark DESC
        LIMIT 5
    """)
    top_performers = cursor.fetchall()

    # Low Attendance List
    cursor.execute("""
        SELECT s.student_id, s.name, s.department, s.phone,
               a.total_days, a.present_days, a.absent_days, a.attendance_percentage
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE a.attendance_percentage < 75
        ORDER BY a.attendance_percentage ASC
    """)
    low_attendance_students = cursor.fetchall()

    conn.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_departments=total_departments,
        avg_attendance=avg_attendance,
        avg_marks=avg_marks,
        dept_summary=dept_summary,
        top_performers=top_performers,
        low_attendance_students=low_attendance_students
    )


@app.route("/about")
def about_view():
    """About Project & College Presentation Guide."""
    return render_template("about.html")


# ---------------------------------------------------------
# REST API Endpoints (JSON Responses)
# ---------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    """Returns analytics data for dashboard charts and metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Counts
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM departments")
    total_departments = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(attendance_percentage) FROM attendance")
    avg_att_row = cursor.fetchone()[0]
    avg_attendance = round(avg_att_row, 1) if avg_att_row else 0.0

    # Department-wise distribution
    cursor.execute("""
        SELECT d.department_id, d.department_name, COUNT(s.student_id) as count
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department
        GROUP BY d.department_id, d.department_name
        ORDER BY d.department_id ASC
    """)
    dept_rows = cursor.fetchall()
    dept_labels = [row["department_id"] for row in dept_rows]
    dept_counts = [row["count"] for row in dept_rows]

    # Attendance distribution (Good >= 75 vs Low < 75)
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE attendance_percentage >= 75")
    good_att = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE attendance_percentage < 75")
    low_att = cursor.fetchone()[0]

    # Grade distribution from marks
    cursor.execute("""
        SELECT grade, COUNT(*) as count 
        FROM marks 
        GROUP BY grade 
        ORDER BY grade ASC
    """)
    grade_rows = cursor.fetchall()
    grade_data = {row["grade"]: row["count"] for row in grade_rows}

    conn.close()

    return jsonify({
        "success": True,
        "metrics": {
            "total_students": total_students,
            "total_departments": total_departments,
            "average_attendance": avg_attendance,
            "good_attendance_count": good_att,
            "low_attendance_count": low_att
        },
        "department_chart": {
            "labels": dept_labels,
            "data": dept_counts
        },
        "attendance_chart": {
            "labels": ["Good Attendance (≥75%)", "Low Attendance (<75%)"],
            "data": [good_att, low_att]
        },
        "grade_chart": grade_data
    })


@app.route("/api/students", methods=["GET", "POST"])
def api_students():
    """Fetch students or create a new student via API."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        data = request.get_json() or {}
        required = ["student_id", "name", "email", "phone", "gender", "dob", "department", "year", "section", "admission_year"]
        for field in required:
            if not data.get(field):
                conn.close()
                return jsonify({"success": False, "error": f"Field '{field}' is required."}), 400

        student_id = data["student_id"].strip().upper()
        email = data["email"].strip().lower()

        cursor.execute("SELECT student_id FROM students WHERE student_id = ? OR email = ?", (student_id, email))
        if cursor.fetchone():
            conn.close()
            return jsonify({"success": False, "error": "Student ID or Email already exists."}), 409

        cursor.execute("""
            INSERT INTO students (student_id, name, email, phone, gender, dob, department, year, section, address, admission_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, data["name"].strip(), email, data["phone"].strip(),
            data["gender"].strip(), data["dob"].strip(), data["department"].strip(),
            data["year"].strip(), data["section"].strip(), data.get("address", "").strip(),
            data["admission_year"].strip()
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Student created successfully.", "student_id": student_id}), 201

    # GET request with optional query filtering
    search = request.args.get("search", "")
    dept = request.args.get("department", "")
    year = request.args.get("year", "")

    query = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        query += " AND (student_id LIKE ? OR name LIKE ? OR email LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if dept:
        query += " AND department = ?"
        params.append(dept)
    if year:
        query += " AND year = ?"
        params.append(year)

    cursor.execute(query, params)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "count": len(students), "data": students})


@app.route("/api/students/<student_id>", methods=["GET", "PUT", "DELETE"])
def api_student_detail(student_id):
    """Retrieve, update, or delete a specific student via API."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"success": False, "error": "Student not found."}), 404

    if request.method == "GET":
        cursor.execute("SELECT * FROM marks WHERE student_id = ?", (student_id,))
        marks = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
        attendance_row = cursor.fetchone()
        attendance = dict(attendance_row) if attendance_row else None

        conn.close()
        return jsonify({
            "success": True,
            "student": dict(student),
            "marks": marks,
            "attendance": attendance
        })

    elif request.method == "PUT":
        data = request.get_json() or {}
        cursor.execute("""
            UPDATE students
            SET name = COALESCE(?, name),
                email = COALESCE(?, email),
                phone = COALESCE(?, phone),
                department = COALESCE(?, department),
                year = COALESCE(?, year),
                section = COALESCE(?, section),
                address = COALESCE(?, address)
            WHERE student_id = ?
        """, (
            data.get("name"), data.get("email"), data.get("phone"),
            data.get("department"), data.get("year"), data.get("section"),
            data.get("address"), student_id
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Student updated successfully."})

    elif request.method == "DELETE":
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Student '{student_id}' deleted."})


@app.route("/api/marks/<student_id>", methods=["GET"])
def api_student_marks(student_id):
    """Get marks list for a specific student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM marks WHERE student_id = ?", (student_id,))
    marks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "student_id": student_id, "marks": marks})


@app.route("/api/attendance/<student_id>", methods=["GET"])
def api_student_attendance(student_id):
    """Get attendance record for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"success": True, "student_id": student_id, "attendance": dict(row)})
    return jsonify({"success": False, "error": "Attendance record not found."}), 404


@app.route("/api/departments", methods=["GET"])
def api_departments():
    """Get department list with headcount."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.department_id, d.department_name, COUNT(s.student_id) as student_count
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department
        GROUP BY d.department_id, d.department_name
        ORDER BY d.department_name ASC
    """)
    departments = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "departments": departments})


# ---------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template("base.html", not_found=True), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", internal_error=True), 500


if __name__ == "__main__":
    print("===============================================================")
    print("[SMS] Student Management System Running on http://127.0.0.1:5000")
    print("===============================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
