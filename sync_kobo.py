import requests
import json
import os
import pandas as pd

FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

# =====================
# GET DATA FROM KOBO
# =====================

url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/?format=json"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("API error", response.status_code)
    exit()

data = response.json()["results"]

# =====================
# LOAD FIELDS
# =====================

fields_df = pd.read_excel("fields.xlsx")
fields = fields_df.to_dict(orient="records")

# =====================
# LOAD CHOICES
# =====================

choices_df = pd.read_excel("choices.xlsx")

choices_map = {}

for _, row in choices_df.iterrows():

    list_name = row["list_name"]
    name = row["name"]
    label = row["label"]

    if list_name not in choices_map:
        choices_map[list_name] = {}

    choices_map[list_name][name] = label

# =====================
# META COLUMN
# =====================

columns_meta = {}

for f in fields:
    columns_meta[f["field_output"]] = f["display_name"]

columns_meta["submission_time"] = "Thời gian nộp"

# =====================
# PROCESS DATA
# =====================

selected_data = []

for row in data:

    record = {}

    record_id = row["_id"]

    for field in fields:

        field_path = field["field_path"]
        field_output = field["field_output"]

        value = row.get(field_path)

        # ===== MAP LABEL =====
        if field_path in choices_map:
            value = choices_map[field_path].get(value, value)

        record[field_output] = value

        # ===== FILE DOWNLOAD =====
        if value and "." in str(row.get(field_path,"")):

            filename = row.get(field_path)

            download_url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/{record_id}/attachments/{filename}"

            record[field_output + "_URL"] = download_url

    record["submission_time"] = row.get("_submission_time")

    selected_data.append(record)

# =====================
# SAVE FILE
# =====================

with open("data.json","w",encoding="utf-8") as f:
    json.dump(selected_data,f,ensure_ascii=False,indent=2)

with open("columns.json","w",encoding="utf-8") as f:
    json.dump(columns_meta,f,ensure_ascii=False,indent=2)

print("Export success")
