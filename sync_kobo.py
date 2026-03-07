import requests
import json
import os
import pandas as pd

FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

# ===== LẤY DATA =====
url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Lỗi API:", response.status_code)
    exit()

data = response.json()["results"]

# ===== ĐỌC FIELDS =====
fields_df = pd.read_excel("fields.xlsx")
fields = fields_df.to_dict(orient="records")

# ===== ĐỌC CHOICES =====
choices_df = pd.read_excel("choices.xlsx")

choices_map = {}

for _, row in choices_df.iterrows():

    var = row["variable"]
    value = row["value"]
    label = row["label"]

    if var not in choices_map:
        choices_map[var] = {}

    choices_map[var][value] = label

# ===== META COLUMN =====
columns_meta = {
    f["field_output"]: f["display_name"]
    for f in fields
}

columns_meta["submission_time"] = "Thời gian nộp"

selected_data = []

# ===== LOOP RECORD =====
for row in data:

    record = {}
    record_id = row["_id"]

    # ===== LẤY ATTACHMENT =====
    attach_api = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/{record_id}/attachments/"
    attach_res = requests.get(attach_api, headers=headers)

    attachments = []

    if attach_res.status_code == 200:
        attachments = attach_res.json()["results"]

    # ===== PROCESS FIELD =====
    for field in fields:

        field_path = field["field_path"]
        field_output = field["field_output"]

        value = row.get(field_path)

        # ===== MAP LABEL =====
        if field_output in choices_map:
            value = choices_map[field_output].get(value, value)

        record[field_output] = value

        # ===== FILE ATTACHMENT =====
        for a in attachments:

            if a["filename"] == value:

                record[field_output + "_URL"] = a.get(
                    "download_large_url",
                    a.get("download_medium_url")
                )

    record["submission_time"] = row.get("_submission_time")

    selected_data.append(record)

# ===== SAVE DATA =====
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

# ===== SAVE COLUMN META =====
with open("columns.json", "w", encoding="utf-8") as f:
    json.dump(columns_meta, f, ensure_ascii=False, indent=2)

print("Xuất data.json + columns.json thành công")
