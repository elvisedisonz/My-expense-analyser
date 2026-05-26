import os
import tempfile

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)

from app.processing import (
    process_df,
    load_groups,
)

from app.extract_excel import excel_to_dataframe
from app.extract_pdf import pdf_to_dataframe

main = Blueprint("main", __name__)

EXCEL_PASSWORD = ""
PDF_PASSWORD = ""


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        })

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "Empty filename"
        })

    days = int(
        request.form.get("match_days", 7)
    )

    uploaded_password = request.form.get(
        "passwd",
        ""
    ).strip()

    filename = file.filename.lower()

    suffix = os.path.splitext(filename)[1]

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            file.save(tmp.name)

            if filename.endswith((".xlsx", ".xls")):

                password = (
                    uploaded_password
                    if uploaded_password
                    else EXCEL_PASSWORD
                )

                df = excel_to_dataframe(
                    tmp.name,
                    password=password
                )

            elif filename.endswith(".pdf"):

                password = (
                    uploaded_password
                    if uploaded_password
                    else PDF_PASSWORD
                )

                df = pdf_to_dataframe(
                    tmp.name,
                    password=password
                )

            else:
                return jsonify({
                    "error": "Unsupported file type"
                })

        os.unlink(tmp.name)

        if df is None or df.empty:
            return jsonify({
                "error": "No transactions found"
            })

    except Exception as e:

        return jsonify({
            "error": f"File processing failed: {e}"
        })

    return jsonify(process_df(df, days))
