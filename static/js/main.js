/**
 * Student Management System - Main Interactive Controller
 * Handles mobile sidebar toggle, live table filtering, modal previews, and alerts
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Sidebar Toggle
  const menuToggleBtn = document.getElementById("menuToggleBtn");
  const sidebar = document.getElementById("sidebar");

  if (menuToggleBtn && sidebar) {
    menuToggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close sidebar on outer click for mobile
    document.addEventListener("click", (e) => {
      if (
        window.innerWidth <= 900 &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(e.target) &&
        !menuToggleBtn.contains(e.target)
      ) {
        sidebar.classList.remove("open");
      }
    });
  }

  // 2. Auto Dismiss Flash Alerts after 5s
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    const closeBtn = alert.querySelector(".alert-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        alert.remove();
      });
    }
    setTimeout(() => {
      alert.style.transition = "opacity 0.4s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  // 3. Client-side Live Table Filter & Search for Student Directory
  const studentSearchInput = document.getElementById("clientSearchInput");
  const deptFilter = document.getElementById("clientDeptFilter");
  const yearFilter = document.getElementById("clientYearFilter");
  const sectionFilter = document.getElementById("clientSectionFilter");
  const studentsTable = document.getElementById("studentsTable");

  if (studentsTable && (studentSearchInput || deptFilter || yearFilter || sectionFilter)) {
    const rows = studentsTable.querySelectorAll("tbody tr");

    const filterTable = () => {
      const searchTerm = (studentSearchInput?.value || "").toLowerCase().trim();
      const selectedDept = deptFilter?.value || "";
      const selectedYear = yearFilter?.value || "";
      const selectedSec = sectionFilter?.value || "";

      let visibleCount = 0;

      rows.forEach((row) => {
        const id = row.getAttribute("data-id") || "";
        const name = row.getAttribute("data-name") || "";
        const dept = row.getAttribute("data-dept") || "";
        const year = row.getAttribute("data-year") || "";
        const sec = row.getAttribute("data-section") || "";
        const textContent = row.textContent.toLowerCase();

        const matchesSearch = !searchTerm || textContent.includes(searchTerm) || id.toLowerCase().includes(searchTerm) || name.toLowerCase().includes(searchTerm);
        const matchesDept = !selectedDept || dept === selectedDept;
        const matchesYear = !selectedYear || year === selectedYear;
        const matchesSec = !selectedSec || sec === selectedSec;

        if (matchesSearch && matchesDept && matchesYear && matchesSec) {
          row.style.display = "";
          visibleCount++;
        } else {
          row.style.display = "none";
        }
      });

      const countBadge = document.getElementById("visibleRecordCount");
      if (countBadge) {
        countBadge.textContent = `${visibleCount} Students`;
      }
    };

    if (studentSearchInput) studentSearchInput.addEventListener("input", filterTable);
    if (deptFilter) deptFilter.addEventListener("change", filterTable);
    if (yearFilter) yearFilter.addEventListener("change", filterTable);
    if (sectionFilter) sectionFilter.addEventListener("change", filterTable);
  }

  // 4. Modal Handlers (View Student Details Modal)
  const detailModal = document.getElementById("studentDetailModal");
  const closeDetailModalBtn = document.getElementById("closeDetailModalBtn");
  const modalCloseCross = document.getElementById("modalCloseCross");

  if (detailModal) {
    const closeModal = () => {
      detailModal.classList.remove("open");
    };

    if (closeDetailModalBtn) closeDetailModalBtn.addEventListener("click", closeModal);
    if (modalCloseCross) modalCloseCross.addEventListener("click", closeModal);

    detailModal.addEventListener("click", (e) => {
      if (e.target === detailModal) closeModal();
    });

    // Attach click listener for "View Student" buttons
    document.querySelectorAll(".btn-view-student").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const studentId = btn.getAttribute("data-id");
        if (!studentId) return;

        try {
          const res = await fetch(`/api/students/${studentId}`);
          const data = await res.json();

          if (data.success && data.student) {
            const s = data.student;
            document.getElementById("modalStudentId").textContent = s.student_id;
            document.getElementById("modalName").textContent = s.name;
            document.getElementById("modalEmail").textContent = s.email;
            document.getElementById("modalPhone").textContent = s.phone;
            document.getElementById("modalGender").textContent = s.gender;
            document.getElementById("modalDob").textContent = s.dob;
            document.getElementById("modalDept").textContent = s.department;
            document.getElementById("modalYear").textContent = s.year;
            document.getElementById("modalSection").textContent = s.section;
            document.getElementById("modalAdmission").textContent = s.admission_year;
            document.getElementById("modalAddress").textContent = s.address || "Not Provided";

            // Marks preview in modal
            const marksContainer = document.getElementById("modalMarksTableBody");
            if (marksContainer) {
              if (data.marks && data.marks.length > 0) {
                marksContainer.innerHTML = data.marks.map((m) => `
                  <tr>
                    <td>${m.subject}</td>
                    <td>${m.internal_mark}</td>
                    <td>${m.external_mark}</td>
                    <td><strong>${m.total_mark}</strong></td>
                    <td><span class="badge badge-${m.grade === 'F' ? 'danger' : 'success'}">${m.grade}</span></td>
                  </tr>
                `).join("");
              } else {
                marksContainer.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#94a3b8;">No marks recorded yet.</td></tr>`;
              }
            }

            // Attendance preview
            const attContainer = document.getElementById("modalAttendanceBox");
            if (attContainer) {
              if (data.attendance) {
                const att = data.attendance;
                const isLow = att.attendance_percentage < 75;
                attContainer.innerHTML = `
                  <div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; padding:12px; border-radius:8px;">
                    <div>Present: <strong>${att.present_days} / ${att.total_days} days</strong></div>
                    <div>Percentage: <strong style="color:${isLow ? '#ef4444' : '#10b981'}">${att.attendance_percentage}%</strong></div>
                    <div>Status: <span class="badge badge-${isLow ? 'warning' : 'success'}">${isLow ? 'Low Attendance' : 'Good'}</span></div>
                  </div>
                `;
              } else {
                attContainer.innerHTML = `<span style="color:#94a3b8;">No attendance record found.</span>`;
              }
            }

            detailModal.classList.add("open");
          }
        } catch (err) {
          console.error("Failed to fetch student details:", err);
        }
      });
    });
  }
});

/**
 * Confirm delete helper
 */
function confirmDelete(studentName, studentId) {
  return confirm(`Are you sure you want to delete ${studentName} (${studentId})?\nThis action will also remove all associated marks and attendance records!`);
}
