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
│   ├── __init__.py
│   ├── routes.py
│   ├── processing.py
│   ├── utils.py
│   ├── extract_excel.py
│   ├── extract_pdf.py
│   ├── templates
│   │   └── index.html
│   ├── static
│   │   ├── script.js
│   │   └── style.css
│   └── config
│         ├── groups.json
│         └── group_rules.json
├── requirements.txt
└── run.py
```
## Screenshots

<img width="1269" height="546" alt="image" src="https://github.com/user-attachments/assets/546dce5d-cae3-430f-b5e4-ee85ce5e9428" />
<img width="1269" height="546" alt="image" src="https://github.com/user-attachments/assets/6af94b4f-70a7-462c-a3a2-b5e54ac8acd0" />
<img width="1269" height="546" alt="image" src="https://github.com/user-attachments/assets/ee20fbd4-026b-40ae-9f6e-225744f09e98" />
<img width="1269" height="546" alt="image" src="https://github.com/user-attachments/assets/86d2cb26-a348-4787-bea2-06ac10f02a75" />
<img width="1269" height="546" alt="image" src="https://github.com/user-attachments/assets/417f7e09-8a25-4c10-a5c3-b02f1176bc39" />

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


