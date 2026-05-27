import re

import pdfplumber
import pandas as pd


SKIP_FIRST_PAGES = 2
EXPECTED_COLS = 6

STANDARD_COLUMNS = [
    "Date",
    "Details",
    "Debit",
    "Credit",
    "Balance",
]

IGNORE_PATTERNS = [
    r"customer care",
    r"sbi\.co\.in",
    r"page \d+ of \d+",
    r"date\s+transaction",
    r"ref\.?no",
    r"balance",
    r"visithttps",
]


def normalize_dataframe(df):

    if df is None or df.empty:
        return None

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    keep = [
        c for c in STANDARD_COLUMNS
        if c in df.columns
    ]

    df = df[keep]

    df = df.dropna(how="all")

    return df.reset_index(drop=True)


def clean_cell(cell):

    if cell is None:
        return ""

    return (
        str(cell)
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def is_transaction_row(row):

    if len(row) != EXPECTED_COLS:
        return False

    text = " ".join(row).lower()

    for pattern in IGNORE_PATTERNS:

        if re.search(pattern, text):
            return False

    if not re.match(
        r"\d{2}-\d{2}-\d{2}",
        row[0]
    ):
        return False

    return True


def get_table_crop(page):

    words = page.extract_words()

    table_top = 100

    for word in words:

        txt = word["text"].strip().lower()

        if txt == "date":

            table_top = (
                word["top"] - 10
            )

            break

    return page.crop((
        0,
        table_top,
        page.width,
        page.height - 50
    ))


def merge_multiline_rows(rows):

    merged = []

    for row in rows:

        if re.match(
            r"\d{2}-\d{2}-\d{2}",
            row[0]
        ):

            merged.append(row)

        else:

            if merged:
                merged[-1][1] += (
                    " " + row[1]
                )

    return merged


def pdf_to_dataframe(
    pdf_path,
    password=None
):

    all_rows = []

    try:

        with pdfplumber.open(
            pdf_path,
            password=password
        ) as pdf:

            pages = pdf.pages[
                SKIP_FIRST_PAGES:
            ]

            for page_num, page in enumerate(
                pages,
                start=SKIP_FIRST_PAGES + 1
            ):

                try:

                    cropped = get_table_crop(page)

                    table = cropped.extract_table(
                        table_settings={
                            "vertical_strategy": "text",
                            "horizontal_strategy": "text",
                            "snap_tolerance": 3,
                            "join_tolerance": 3,
                            "intersection_tolerance": 3,
                            "text_x_tolerance": 2,
                            "text_y_tolerance": 2,
                        }
                    )

                    if not table:
                        continue

                    for row in table:

                        if not row:
                            continue

                        cleaned = [
                            clean_cell(cell)
                            for cell in row
                        ]

                        if not any(cleaned):
                            continue

                        if len(cleaned) < EXPECTED_COLS:

                            cleaned += [""] * (
                                EXPECTED_COLS
                                - len(cleaned)
                            )

                        cleaned = cleaned[
                            :EXPECTED_COLS
                        ]

                        if is_transaction_row(cleaned):
                            all_rows.append(cleaned)

                except Exception as e:

                    print(
                        f"PDF page error "
                        f"{page_num}: {e}"
                    )

        if not all_rows:
            return None

        # ---------------- MULTILINE ----------------

        all_rows = merge_multiline_rows(
            all_rows
        )

        # ---------------- DATAFRAME ----------------

        columns = [
            "Date",
            "Details",
            "Ref No",
            "Credit",
            "Debit",
            "Balance"
        ]

        df = pd.DataFrame(
            all_rows,
            columns=columns
        )

        # ---------------- DATE FORMAT ----------------

        df["Date"] = pd.to_datetime(
            df["Date"],
            format="%d-%m-%y",
            errors="coerce"
        ).dt.strftime("%d/%m/%Y")

        df = normalize_dataframe(df)

    # ---------------- EMPTY ZERO VALUES ----------------

        for col in ["Debit", "Credit"]:

            if col in df.columns:

                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )

                df[col] = df[col].apply(
                    lambda x: ""
                    if x in ["0", "0.0", "0.00", ""]
                    else x
                )

        # ---------------- SAVE ----------------
        if df is not None and not df.empty:
            output_path = "debug_pdf.xlsx"
            df.to_excel(output_path, index=False)

        return df

    except Exception as e:

        raise Exception(
            f"PDF extraction failed: {e}"
        )
