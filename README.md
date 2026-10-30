# 🎓 StudentPulse — Student Performance Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg)](https://plotly.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Pytest-23%20Passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT%2FAcademic-informational.svg)](LICENSE)

An interactive, CPU-friendly, Dockerized academic performance analytics dashboard built for educators, department coordinators, and academic mentors.

- **Developer:** Navya M
- **GitHub Repository:** https://github.com/marripatinavya0408-debug/mini_project7
- **Project directory:StudentPulse

---

## Table of Contents
1. [Project Abstract](#1-project-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Existing Limitations & Proposed Solution](#5-existing-limitations--proposed-solution)
6. [Technology Stack](#6-technology-stack)
7. [System Architecture](#7-system-architecture)
8. [Data Flow](#8-data-flow)
9. [Key Features](#9-key-features)
10. [Dataset Format & Specification](#10-dataset-format--specification)
11. [Installation Instructions](#11-installation-instructions)
12. [Local Execution](#12-local-execution)
13. [Docker Build & Run Instructions](#13-docker-build--run-instructions)
14. [Automated Testing Instructions](#14-automated-testing-instructions)
15. [Application Interface Walkthrough](#15-application-interface-walkthrough)
16. [Key Advantages](#16-key-advantages)
17. [Limitations](#17-limitations)
18. [Future Enhancements](#18-future-enhancements)
19. [Developer Contributions](#19-developer-contributions)

---

## 1. Project Abstract
**StudentPulse** is a lightweight, responsive academic analytics application engineered using Python, Streamlit, Pandas, and Plotly, packaged inside a portable Docker container. It empowers academic institutions to explore student examination marks and attendance metrics dynamically. Operating on arbitrary uploaded institutional CSV data or bundled synthetic records, the dashboard computes cohort KPIs, plots interactive distributions, audits data hygiene, and flags students who may benefit from early academic counseling through transparent, configurable heuristic rules.

---

## 2. Introduction
In higher education, monitoring student performance and identifying academic distress early in the semester is critical for maintaining retention and improving graduation outcomes. However, faculty members often manage scores and attendance records across disparate spreadsheets, resulting in delayed interventions and manual calculation errors. **StudentPulse** bridges this gap by providing an intuitive, web-based visualization cockpit that runs locally or as a containerized microservice without requiring extensive software engineering background to operate.

---

## 3. Problem Statement
Educational institutions struggle with three core challenges during routine academic evaluations:
- **Static Spreadsheets:** Standard spreadsheet software lacks interactive filtering, requires manual formula construction, and fails to offer real-time visual cohort comparisons.
- **Environment Inconsistency:** Analytical code frequently encounters dependency incompatibilities across different operating systems ("works on my machine" syndrome).
- **Opaque Automated Labeling:** Commercial academic predictive tools frequently use opaque black-box machine learning algorithms that can introduce bias or make misleading claims regarding student failure.

---

## 4. Objectives
- **Interactive Visualizations:** Implement dynamic, interactive Plotly visualizations for score distributions, course comparisons, attendance vs. score correlations, and academic grading tiers.
- **Adaptive Ingestion:** Support flexible CSV uploads with automated column role heuristics (marks, attendance, subject, semester, class section) and encoding fallbacks.
- **Transparent Support Rules:** Establish an instructor-configurable heuristic rule engine to flag students requiring additional academic guidance.
- **Data Integrity & Non-Destructive Cleaning:** Preserve original raw files untouched while offering downloadable cleaned and filtered datasets.
- **Portability via Containerization:** Provide a production-grade Dockerfile and Docker Compose configuration with non-root security and health monitoring.
- **Comprehensive Verification:** Ensure 100% test pass rate across unit, boundary, and edge-case test suites using Pytest.

---

## 5. Existing Limitations & Proposed Solution

| Dimension | Existing Institutional Approach | StudentPulse Proposed Solution |
| :--- | :--- | :--- |
| **Interface** | Static Microsoft Excel / CSV spreadsheets | Responsive, interactive Streamlit web application |
| **Data Ingestion** | Rigid template requirements | Heuristic column role auto-detection with manual override |
| **Analytics** | Manual recalculation of means and pass rates | Real-time, reactive dynamic KPI derivation |
| **Early Intervention** | Post-semester manual review | Configurable, pre-exam heuristic alert triggers |
| **Deployment** | Complex multi-step Python environment setup | Single-command Docker and Docker Compose execution |
| **Data Safety** | Accidental overwriting of raw data files | Strictly non-destructive processing with separate export |

---

## 6. Technology Stack

- **Core Programming Language:** Python 3.11 / 3.12
- **Web Application Framework:** Streamlit (v1.35+)
- **Data Processing & Analytics Engine:** Pandas (v2.1+), NumPy (v1.26+)
- **Interactive Data Visualization:** Plotly Express & Plotly Graph Objects (v5.20+)
- **Testing Framework:** Pytest (v8.0+)
- **Containerization Platform:** Docker Engine, Docker Compose (Linux `python:3.11-slim`)
- **Version Control:** Git & GitHub

---

## 7. System Architecture

StudentPulse employs a decoupled three-tier architectural model:

```
+-----------------------------------------------------------------+
|                       Client Web Browser                        |
|                     http://localhost:8501                       |
+--------------------------------+--------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------+
|                 Streamlit Presentation Layer (app.py)           |
|                                                                 |
|   +-------------------+  +-------------------+  +------------+  |
|   | Overview & KPIs   |  | Plotly Visualizer |  | Alerts Tab |  |
|   +-------------------+  +-------------------+  +------------+  |
|   +------------------------------------------+  +------------+  |
|   | Data Explorer & Quality Audit            |  | Viva Guide |  |
|   +------------------------------------------+  +------------+  |
+--------------------------------+--------------------------------+
                                 |
        +------------------------+------------------------+
        v                                                 v
+-----------------------------+             +---------------------+
|  src/data_validation.py     |             |  src/analytics.py   |
|  - Multi-encoding CSV reader|             |  - Dynamic metrics  |
|  - Role heuristic detector  |             |  - Support flags    |
|  - Non-destructive cleaner  |             |  - Correlation & r  |
+-----------------------------+             +---------------------+
```

For complete architectural diagrams and component specifications, consult [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 8. Data Flow
1. **Ingestion:** User selects the synthetic sample dataset or uploads an institutional CSV file.
2. **Decoding:** `load_dataset()` attempts UTF-8, UTF-8-BOM, and Latin-1 decoding.
3. **Inspection:** `inspect_dataframe()` scans for row counts, missing data, and duplicate rows.
4. **Role Mapping:** `detect_column_roles()` suggests columns for marks, attendance, subject, etc.
5. **Filtering:** User applies active sidebar filters (subject, class, score ranges).
6. **Analytics:** `calculate_overview_metrics()` and `flag_academic_support()` execute dynamically.
7. **Rendering:** Plotly charts and metric cards update reactively.

---

## 9. Key Features

### Feature 1: Dynamic KPI Overview
- Computes total students, overall average score, average attendance, and pass percentage based strictly on the loaded and filtered data.
- **Never displays hardcoded statistics.**

### Feature 2: Flexible CSV Ingestion
- Upload arbitrary student CSV files with automatic detection of column types and candidate roles.
- Supports files with missing optional columns (e.g. datasets without attendance or class sections).

### Feature 3: Interactive Visual Analytics
- **Score Distribution:** Histogram with mean and pass threshold reference lines plus box plot marginals.
- **Subject Mastery:** Grouped bar charts ranking subjects by average, highest, and lowest marks.
- **Attendance vs. Marks:** Scatter plot with quadrant alert lines and Pearson correlation $r$.
- **Performance Tiers:** Interactive donut chart categorizing students into Distinction, First Class, Second Class, Pass Class, and Remedial.
- **Cohort Comparisons:** Box plots comparing performance across semesters or sections.

### Feature 4: Transparent Academic Support Rules
- Configurable sliders for Minimum Passing Score, Academic Review Score, and Attendance Threshold.
- Explicit pedagogical disclaimers explaining that alerts are heuristic mentoring aids, not punitive grades.

### Feature 5: Data Explorer & Quality Audit
- Interactive searchable data table.
- Summary descriptive statistics (`describe()`).
- Missing-value audit and duplicate-row audit.
- One-click downloads for filtered data, support alert rosters, and non-destructively cleaned datasets.

---

## 10. Dataset Format & Specification

StudentPulse supports standard CSV files. Recommended columns include:

| Column Name | Recommended Type | Description |
| :--- | :--- | :--- |
| `student_id` | String / Integer | Unique student identifier |
| `student_name`| String (Optional) | Student display name |
| `class_section`| String (Optional)| Section or branch (e.g., CS-A, CS-B) |
| `semester` | String (Optional)| Semester term (e.g., Semester 3) |
| `subject` | String (Optional)| Course or module title |
| `marks` | Float / Numeric | Examination marks / percentage (0–100) |
| `attendance_percentage` | Float / Numeric | Attendance percentage (0–100%) |

> **Sample Dataset Notice:**  
> The bundled `data/sample_students.csv` file contains 64 synthetic records for 20 fictional students. It is documented in [data/README.md](data/README.md) and provided strictly for software demonstration.

---

## 11. Installation Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- Git installed.

### Setup Steps
```bash
# 1. Clone the repository
git clone https://github.com/drx2k06/miniproject7.git
cd miniproject7

# 2. Create a virtual environment (recommended)
python -m venv .venv

# 3. Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 12. Local Execution

Run the Streamlit application locally:
```bash
streamlit run app.py
```
Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 13. Docker Build & Run Instructions

Docker packages the application into an isolated, self-contained container, eliminating OS-specific configuration issues.

### 13.1 Build the Docker Image
```bash
docker build -t studentpulse:latest .
```

### 13.2 Run the Docker Container
```bash
docker run -d --name studentpulse-app -p 8501:8501 studentpulse:latest
```

Open your browser to:
```
http://localhost:8501
```

### 13.3 Test Container Health Endpoint
```bash
# Query the container health status
docker inspect --format='{{json .State.Health.Status}}' studentpulse-app
```
*Expected Output:* `"healthy"`

### 13.4 Run via Docker Compose (Recommended)
```bash
# Start container with Compose
docker compose up --build -d

# View live container logs
docker compose logs -f

# Stop container
docker compose down
```

For complete containerization concepts and troubleshooting, refer to [docs/DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md).

---

## 14. Automated Testing Instructions

The project includes an automated test suite implemented with Pytest.

### Run All Tests
```bash
python -m pytest -v
```

### Run Quick Quiet Mode
```bash
python -m pytest -q
```

### Test Coverage Highlights
- Valid and empty CSV input parsing.
- Missing expected columns and non-numeric value coercion.
- Non-destructive deduplication and range clipping.
- Pass-rate calculations at boundary extremes (0% and 100%).
- Four-quadrant academic support indicator rules.
- End-to-end execution of bundled synthetic sample data.

Detailed test results and matrix are documented in [docs/TEST_REPORT.md](docs/TEST_REPORT.md).

---

## 15. Application Interface Walkthrough

```
+---------------------------------------------------------------------------------+
| 🎓 StudentPulse — Student Performance Analytics Dashboard                       |
| Developer: Daniel Richard Xavier | Framework: Streamlit, Pandas, Plotly | Docker|
+---------------------------------------------------------------------------------+
| [Overview & Key Metrics] [Interactive Analytics] [Support Alerts] [Data Explorer]|
+---------------------------------------------------------------------------------+
| Total Students: 20   | Avg Score: 65.4   | Avg Attendance: 79.2% | Pass Rate:88%|
+---------------------------------------------------------------------------------+
| [Score Distribution Histogram]       | [Academic Performance Tiers (Pie Chart)] |
| - Binned marks with mean marker      | - Distinction, 1st Class, 2nd, Remedial  |
+--------------------------------------+------------------------------------------+
| [Subject-wise Average Marks]         | [Attendance vs. Marks Scatter Plot]      |
| - Ranked horizontal/vertical bars    | - Quadrant lines & non-causation notice  |
+---------------------------------------------------------------------------------+
```

---

## 16. Key Advantages
1. **Zero-Configuration Deployment:** Dockerized image ensures instant cross-platform reproducibility.
2. **Non-Destructive Processing:** Ingestion and cleaning never alter the original uploaded dataset.
3. **Transparent Heuristic Logic:** Support flags are intuitive, instructor-configurable rules rather than biased black-box algorithms.
4. **Decoupled Architecture:** Analytical business logic is isolated in `src/`, allowing complete headless testing.
5. **Secure Container Design:** Runs under an unprivileged `appuser` (UID 1000) with container health polling.

---

## 17. Limitations
- **File Format:** Currently restricted to delimited CSV files (Excel `.xlsx` requires conversion to CSV).
- **Single-File Session:** Analytics are performed in-memory during active sessions; persistent historical database storage is not currently implemented.
- **Client-Side Scalability:** Optimized for typical departmental cohorts (<10,000 records). Extremely large enterprise datasets (>100,000 records) require server-side database pagination.

---

## 18. Future Enhancements
- **Multi-Semester Longitudinal Tracking:** Visualize student progress trajectories over consecutive semesters.
- **Automated Grade Sheet Generation:** One-click generation of personalized student progress PDF report cards.
- **LMS API Integration:** Direct synchronization with Canvas, Moodle, or Google Classroom.
- **Role-Based Access Control (RBAC):** Differentiated access views for students, mentors, and departmental heads.

---

## 19. Developer Contributions
- **Project Concept & Architecture:** Navya M
- **UI/UX Design & Streamlit Implementation:** Navya M
- **Analytics & Validation Engine:** Navya M
- **Dockerization & Container Health Setup:** Navya M
- **Automated Pytest Test Suite:** Navya M
- **Documentation & College Reports:** Navya M


