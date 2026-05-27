import os
import json
import re

from pathlib import Path
from datetime import timedelta

import pandas as pd

from app.utils import (
    clean_name,
    extract_notes,
    build_tx_id,
)

GROUPS_FILE = Path(__file__).resolve().parent/"config"/"groups.json"
RULES_FILE = Path(__file__).resolve().parent/"config"/"group_rules.json"

REPEAT_THRESHOLD = 2

REQUIRED_COLUMNS = {
    "Date",
    "Details",
    "Debit",
    "Credit",
    "Balance",
}


def load_groups():

    if not os.path.exists(GROUPS_FILE):
        return {}

    with open(GROUPS_FILE, "r") as f:
        return json.load(f)


def get_group_maps():

    raw = load_groups()

    paid_to_map = {}
    notes_map = {}

    for group, data in raw.items():

        if isinstance(data, list):

            for item in data:
                paid_to_map[item.strip().lower()] = group

        else:

            for item in data.get("paid_to", []):
                paid_to_map[item.strip().lower()] = group

            for item in data.get("notes", []):
                notes_map[item.strip().lower()] = group

    return paid_to_map, notes_map


def load_rules():

    if not os.path.exists(RULES_FILE):
        return []

    with open(RULES_FILE, "r") as f:
        return json.load(f)


def apply_group_rules(expenses):

    rules = load_rules()

    occurrence_tracker = {}
    assigned = []

    for _, row in expenses.iterrows():

        paid_to = str(row["Paid To"]).strip()
        paid_to_lower = paid_to.lower()

        amt = round(float(row["Debit"]), 2)

        month = (
            row["Date"].to_period("M")
            if pd.notna(row["Date"])
            else None
        )

        key = (paid_to_lower, amt, month)

        occurrence_tracker[key] = (
            occurrence_tracker.get(key, 0) + 1
        )

        occ = occurrence_tracker[key]

        matched = None

        for rule in rules:

            names = [
                str(x).strip().lower()
                for x in rule.get("paid_to", [])
            ]

            paid_to_match = (
                not names
                or paid_to_lower in names
            )

            regex_patterns = rule.get("regex", [])

            regex_match = False

            if regex_patterns:

                for pattern in regex_patterns:

                    if re.search(
                        pattern,
                        paid_to,
                        re.IGNORECASE
                    ):
                        regex_match = True
                        break

            else:
                regex_match = True

            rule_amt = rule.get("amt", None)

            amt_match = (
                rule_amt is None
                or amt == round(float(rule_amt), 2)
            )

            rule_occ = rule.get("occurrence", None)

            occ_match = (
                rule_occ is None
                or occ == int(rule_occ)
            )

            if (
                paid_to_match
                and regex_match
                and amt_match
                and occ_match
            ):
                matched = rule["group"]
                break

        assigned.append(matched)

    return assigned


def process_df(df, match_days=7):

    df.columns = [str(c).strip() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        return {"error": f"Missing columns: {', '.join(missing)}"}

    debit = "Debit"
    credit = "Credit"
    details = "Details"
    date = "Date"
    balance = "Balance"

    df[debit] = pd.to_numeric(df[debit], errors="coerce")
    df[credit] = pd.to_numeric(df[credit], errors="coerce")
    df[date] = pd.to_datetime(df[date], errors="coerce", dayfirst=True)

    expenses = df[df[debit].notna()].copy()
    credits = df[df[credit].notna()].copy()

    if expenses.empty:
        return {"error": "No debit transactions found."}

    matched = []
    keep_rows = []
    carryover_rows = []

    used_credit = set()

    for idx, row in expenses.iterrows():

        debit_amt = round(float(row[debit]), 2)
        dt = row[date]

        if pd.isna(dt):
            keep_rows.append(row)
            continue

        found_match = False

        possible = credits[
            (credits[date] >= dt - timedelta(days=match_days))
            & (credits[date] <= dt + timedelta(days=match_days))
            & (~credits.index.isin(used_credit))
        ]

        for c_idx, c_row in possible.iterrows():

            credit_amt = round(float(c_row[credit]), 2)
            diff = round(debit_amt - credit_amt, 2)

            if abs(diff) >= 1:
                continue

            if not (
                int(debit_amt) == int(credit_amt)
                or int(debit_amt) + 1 == int(credit_amt)
            ):
                continue

            used_credit.add(c_idx)

            matched.append({
                "date": str(c_row[date].date()) if pd.notna(c_row[date]) else "",
                "credited_amt": credit_amt,
                "received_from": clean_name(c_row[details]),
                "cancelled_amt": credit_amt,
                "paid_to": clean_name(row[details]),
            })

            found_match = True

            if diff <= 0:
                break

            carryover = row.copy()

            carryover[debit] = diff
            carryover[details] = "Reimburse Carryover"

            carryover_rows.append(carryover)

            break

        if not found_match:
            keep_rows.append(row)

    kept_df = pd.DataFrame(keep_rows)
    carry_df = pd.DataFrame(carryover_rows)

    expenses = pd.concat(
        [kept_df, carry_df],
        ignore_index=False
    )

    expenses["Paid To"] = expenses[details].apply(clean_name)
    expenses["Notes"] = expenses[details].apply(extract_notes)

    expenses = expenses.reset_index(drop=True)

    paid_to_map, notes_map = get_group_maps()

    counts = expenses["Paid To"].value_counts()

    rule_groups = apply_group_rules(expenses)

    expenses["rule_group"] = rule_groups

    def assign_group(row):

        paid = str(row["Paid To"]).strip().lower()
        notes = str(row["Notes"]).strip().lower()

        if pd.notna(row["rule_group"]) and row["rule_group"]:
            return row["rule_group"]

        for k, group in notes_map.items():
            if k and k in notes:
                return group

        if paid in paid_to_map:
            return paid_to_map[paid]

        if counts.get(row["Paid To"], 0) >= REPEAT_THRESHOLD:
            return row["Paid To"]

        return "Others"

    expenses["Group"] = expenses.apply(assign_group, axis=1)

    records = []

    for idx, row in expenses.iterrows():

        records.append({
            "id": build_tx_id(idx, row[details]),
            "date": str(row[date].date()) if pd.notna(row[date]) else "",
            "paid_to": row["Paid To"],
            "notes": row["Notes"],
            "amt": float(row[debit]),
            "bal": float(row[balance]) if pd.notna(row[balance]) else 0,
            "group": row["Group"],
        })

    total_incoming = float(credits[credit].fillna(0).sum())
    total_outgoing = float(df[debit].fillna(0).sum())
    total_reimbursed = float(sum(x["cancelled_amt"] for x in matched))

    net_expense = total_outgoing - total_reimbursed
    net_income = total_incoming - total_reimbursed
    total_balance = net_income - net_expense

    valid = df["Balance"].dropna()

    current_balance = (
        float(valid.iloc[-1])
        if not valid.empty else 0
    )

    summary = {
        "total_incoming": total_incoming,
        "total_outgoing": total_outgoing,
        "net_income": net_income,
        "net_expense": net_expense,
        "saved": total_balance,
        "current_balance": current_balance,
        "reimbursed": total_reimbursed,
        "transaction_count": len(expenses),
    }

    return {
        "records": records,
        "matched": matched,
        "summary": summary,
    }
