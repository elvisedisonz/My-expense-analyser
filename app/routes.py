import json
import os
import tempfile

from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request

from app.extract_excel import excel_to_dataframe
from app.extract_pdf import pdf_to_dataframe
from app.processing import GROUPS_FILE, load_groups, process_df

main = Blueprint("main", __name__)
load_dotenv()

EXCEL_PASSWORD = os.getenv("default_excel_password", "")
PDF_PASSWORD = os.getenv("default_pdf_password", "")


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Empty filename"})

    days = int(request.form.get("match_days", 7))
    uploaded_password = request.form.get("passwd", "").strip()

    filename = file.filename.lower()
    suffix = os.path.splitext(filename)[1]

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp.name)

            if filename.endswith((".xlsx", ".xls")):
                password = uploaded_password or EXCEL_PASSWORD
                df = excel_to_dataframe(tmp.name, password=password)

            elif filename.endswith(".pdf"):
                password = uploaded_password or PDF_PASSWORD
                df = pdf_to_dataframe(tmp.name, password=password)

            else:
                return jsonify({"error": "Unsupported file type"})

        os.unlink(tmp.name)

        if df is None or df.empty:
            return jsonify({"error": "No transactions found"})

    except Exception as e:
        return jsonify({"error": f"File processing failed: {e}"})

    return jsonify(process_df(df, days))


@main.route("/save_group", methods=["POST"])
def save_group():
    data = request.json

    group_name = data["group"].strip()
    entities = [e.strip().lower() for e in data["entities"]]
    mode = data.get("mode", "paid_to")

    groups = load_groups()

    if group_name not in groups:
        groups[group_name] = {
            "paid_to": [],
            "notes": [],
        }

    if isinstance(groups[group_name], list):
        groups[group_name] = {
            "paid_to": groups[group_name],
            "notes": [],
        }

    target_list = groups[group_name][mode]
    existing = {x.lower() for x in target_list}

    for entity in entities:
        if entity and entity not in existing:
            target_list.append(entity)

    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)

    return jsonify({"success": True})


@main.route("/delete_group", methods=["POST"])
def delete_group():
    data = request.json
    group_name = data["group"]

    groups = load_groups()

    if group_name in groups:
        del groups[group_name]

    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)

    return jsonify({"success": True})
