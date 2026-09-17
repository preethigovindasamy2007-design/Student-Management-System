import unittest
from app import app
from database.db import get_db_connection, init_db, calculate_grade, calculate_performance_status

class StudentManagementSystemTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()

    def test_database_initialization(self):
        """Verify that tables exist and sample data is seeded."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        self.assertGreaterEqual(student_count, 10, "Should have at least 10 sample students")

        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        self.assertGreaterEqual(dept_count, 5, "Should have at least 5 departments")

        cursor.execute("SELECT COUNT(*) FROM marks")
        marks_count = cursor.fetchone()[0]
        self.assertGreater(marks_count, 0, "Marks records should exist")

        cursor.execute("SELECT COUNT(*) FROM attendance")
        att_count = cursor.fetchone()[0]
        self.assertGreater(att_count, 0, "Attendance records should exist")
        conn.close()

    def test_grade_calculation(self):
        """Verify academic grade assignment."""
        self.assertEqual(calculate_grade(95), "A+")
        self.assertEqual(calculate_grade(85), "A")
        self.assertEqual(calculate_grade(75), "B+")
        self.assertEqual(calculate_grade(65), "B")
        self.assertEqual(calculate_grade(55), "C")
        self.assertEqual(calculate_grade(45), "F")

    def test_performance_status_calculation(self):
        """Verify performance status logic."""
        self.assertEqual(calculate_performance_status(90, 95), "Excellent")
        self.assertEqual(calculate_performance_status(75, 80), "Good")
        self.assertEqual(calculate_performance_status(55, 70), "Average")
        self.assertEqual(calculate_performance_status(40, 60), "Needs Improvement")

    def test_page_routes(self):
        """Verify that all main web pages render with HTTP 200."""
        routes = [
            "/",
            "/students",
            "/add-student",
            "/departments",
            "/marks",
            "/attendance",
            "/performance",
            "/reports",
            "/about"
        ]
        for r in routes:
            response = self.app.get(r)
            self.assertEqual(response.status_code, 200, f"Route {r} failed with status {response.status_code}")

    def test_api_dashboard(self):
        """Verify dashboard JSON API endpoint returns expected schema."""
        response = self.app.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("metrics", data)
        self.assertIn("department_chart", data)
        self.assertIn("attendance_chart", data)

    def test_student_lifecycle(self):
        """Test adding, editing, and deleting a student."""
        # 1. Add student
        new_student = {
            "student_id": "TEST999",
            "name": "Integration Test Student",
            "email": "test999@example.edu",
            "phone": "9876543999",
            "gender": "Male",
            "dob": "2004-01-01",
            "department": "CSE",
            "year": "1st Year",
            "section": "A",
            "address": "99 Test Lane",
            "admission_year": "2024"
        }
        res_add = self.app.post("/add-student", data=new_student, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b"Integration Test Student", res_add.data)

        # 2. Edit student
        updated_data = dict(new_student)
        updated_data["name"] = "Updated Test Student"
        res_edit = self.app.post("/edit-student/TEST999", data=updated_data, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn(b"Updated Test Student", res_edit.data)

        # 3. Delete student
        res_del = self.app.get("/delete-student/TEST999", follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        # Confirm deleted
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = 'TEST999'")
        self.assertIsNone(cursor.fetchone())
        conn.close()

if __name__ == "__main__":
    unittest.main()
