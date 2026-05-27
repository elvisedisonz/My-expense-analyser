# 💰 Expense Analyzer

A full-stack **finance analytics web app** that processes bank statements (PDF/Excel), automatically categorizes transactions, detects reimbursements, and visualizes spending patterns through interactive charts and dashboards.

---

## 🚀 Features

### 📊 Smart Expense Analysis
- Upload **bank statements (PDF / Excel)**
- Automatic parsing of:
- Debit / Credit transactions
- Balance tracking
- Net income, savings, and expense calculations

### 🤖 Intelligent Categorization
- Rule-based grouping engine
- Custom grouping via UI
- Frequency-based merchant grouping
- Notes + merchant matching

### 🔁 Reimbursement Detection
- Automatically matches debit ↔ credit transactions
- Handles partial reimbursements
- Time-window based matching (configurable)

### 📈 Interactive Dashboard
- Expense distribution (Pie Chart)
- Top spending categories (Bar Chart)
- Top individual transactions
- Live summary cards

### 🧾 Transaction Management
- Searchable + sortable DataTable
- Multi-select transactions
- Custom group creation
- Persistent group rules (JSON-based storage)

---

## 🏗️ Tech Stack

### Backend
- Python
- Flask
- Pandas
- Regex-based parsing engine

### Frontend
- HTML5 + CSS3
- Vanilla JavaScript
- Chart.js (visualizations)
- DataTables (table UI)

### File Processing
- Excel parsing (`xlsx`, `xls`)
- PDF parsing (custom extractor module)

---

## 📁 Main Project Structure
```bash
.
├── app
│   ├── config
│   │   ├── group_rules.json
│   │   └── groups.json
│   ├── extract_excel.py
│   ├── extract_pdf.py
│   ├── __init__.py
│   ├── processing.py
│   ├── routes.py
│   ├── static
│   │   ├── script.js
│   │   └── style.css
│   ├── templates
│   │   └── index.html
│   └── utils.py
├── requirements.txt
├── run.py
```
## Screenshots

(add screenshots)

## Installation & Running

Step 1: If you want to run in contained python virtual env then:
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
Or you can skip Step 1, Proceed further
Step 2:
```bash
pip install -r requirements.txt
```
Step 3:
```bash
python run.py # To run using debug flask server
gunicorn -w 2 -b 0.0.0.0:5000 run:app # To run using prod server
```
Step 4:
Open in browser:
http://localhost:5000

## 📤 How It Works

1. Upload bank statement
2. Extract transactions
3. Match reimbursements
4. Apply grouping rules
5. View dashboard + charts

---

## 🔁 API Endpoints

POST /upload → Upload statement
POST /save_group → Save custom group
POST /delete_group → Delete group

---

## 📊 Highlights

- Reimbursement matching within time window
- Smart merchant name cleaning
- Rule-based + manual grouping system
- Real-time dashboard updates

---

## ⚠️ Notes

- Works best with structured bank statements
- PDF parsing depends on format consistency

---

## 👨‍💻 Authored By

Elvis M E

Web App built with Flask + JavaScript for personal finance tracking.


