/**
 * Student Management System - Dynamic Chart.js Analytics Controller
 * Renders department distributions, attendance health, and academic performance charts
 */

document.addEventListener("DOMContentLoaded", () => {
  const deptChartCanvas = document.getElementById("deptChart");
  const attendanceChartCanvas = document.getElementById("attendanceChart");
  const gradeChartCanvas = document.getElementById("gradeChart");

  if (!deptChartCanvas && !attendanceChartCanvas && !gradeChartCanvas) {
    return; // Not on dashboard page
  }

  fetch("/api/dashboard")
    .then((response) => response.json())
    .then((data) => {
      if (!data.success) return;

      // 1. Department-wise Students Bar Chart
      if (deptChartCanvas && data.department_chart) {
        const ctx = deptChartCanvas.getContext("2d");
        new Chart(ctx, {
          type: "bar",
          data: {
            labels: data.department_chart.labels,
            datasets: [
              {
                label: "Enrolled Students",
                data: data.department_chart.data,
                backgroundColor: [
                  "rgba(37, 99, 235, 0.85)",   // Royal Blue
                  "rgba(16, 185, 129, 0.85)",  // Emerald
                  "rgba(14, 165, 233, 0.85)",  // Sky Blue
                  "rgba(245, 158, 11, 0.85)",  // Amber
                  "rgba(139, 92, 246, 0.85)"   // Purple
                ],
                borderColor: [
                  "#2563eb",
                  "#10b981",
                  "#0ea5e9",
                  "#f59e0b",
                  "#8b5cf6"
                ],
                borderWidth: 1.5,
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: "#0f172a",
                padding: 10,
                cornerRadius: 6
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { stepSize: 1, color: "#64748b" },
                grid: { color: "#f1f5f9" }
              },
              x: {
                ticks: { color: "#64748b" },
                grid: { display: false }
              }
            }
          }
        });
      }

      // 2. Attendance Status Doughnut Chart
      if (attendanceChartCanvas && data.attendance_chart) {
        const ctx = attendanceChartCanvas.getContext("2d");
        new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: data.attendance_chart.labels,
            datasets: [
              {
                data: data.attendance_chart.data,
                backgroundColor: [
                  "rgba(16, 185, 129, 0.9)", // Green: Good
                  "rgba(239, 68, 68, 0.9)"    // Red: Low (<75%)
                ],
                borderColor: ["#ffffff", "#ffffff"],
                borderWidth: 2,
                hoverOffset: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  color: "#334155",
                  boxWidth: 14,
                  padding: 16,
                  font: { size: 12, weight: "500" }
                }
              },
              tooltip: {
                backgroundColor: "#0f172a",
                padding: 10,
                cornerRadius: 6
              }
            },
            cutout: "68%"
          }
        });
      }

      // 3. Academic Grade Distribution Chart (if canvas present)
      if (gradeChartCanvas && data.grade_chart) {
        const ctx = gradeChartCanvas.getContext("2d");
        const labels = Object.keys(data.grade_chart);
        const values = Object.values(data.grade_chart);

        new Chart(ctx, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [
              {
                label: "Grades Awarded",
                data: values,
                backgroundColor: "rgba(37, 99, 235, 0.75)",
                borderColor: "#2563eb",
                borderWidth: 1.5,
                borderRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: { backgroundColor: "#0f172a" }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { stepSize: 1, color: "#64748b" },
                grid: { color: "#f1f5f9" }
              },
              x: {
                ticks: { color: "#64748b" },
                grid: { display: false }
              }
            }
          }
        });
      }
    })
    .catch((err) => {
      console.error("Error loading dashboard chart analytics:", err);
    });
});
