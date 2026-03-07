import requests
import json
import os
import pandas as pd

FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

# =========================
# GET DATA
# =========================

url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/?format=json"

response = requests.get(url, headers=headers)

data = response.json()["results"]

# =========================
# LOAD FIELDS
# =========================

fields_df = pd.read_excel("fields.xlsx")
fields = fields_df.to_dict(orient="records")

# =========================
# LOAD CHOICES
# =========================

choices_df = pd.read_excel("choices.xlsx")

choices_map = {}

for _, row in choices_df.iterrows():

    list_name = row["list_name"]
    name = row["name"]
    label = row["label"]

    if list_name not in choices_map:
        choices_map[list_name] = {}

    choices_map[list_name][name] = label

# =========================
# COLUMN META
# =========================

columns_meta = {f["field_output"]: f["display_name"] for f in fields}
columns_meta["submission_time"] = "Thời gian nộp"

selected_data = []

# =========================
# PROCESS DATA
# =========================

for row in data:

    record = {}
    record_id = row["_id"]

    # lấy attachment
    attach_api = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/{record_id}/attachments/"

    attach_res = requests.get(attach_api, headers=headers)

    attachments = []

    if attach_res.status_code == 200:
        attachments = attach_res.json()["results"]

    # map file
    file_map = {}

    for a in attachments:

        filename = a.get("filename", "")

        url = a.get("download_large_url") or a.get("download_medium_url")

        file_map[filename] = url

    # map field
    for field in fields:

        field_path = field["field_path"]
        field_output = field["field_output"]

        value = row.get(field_path)

        # map label
        if field_path in choices_map:
            value = choices_map[field_path].get(value, value)

        record[field_output] = value

        # tìm file attachment
        if value:
            for fname, furl in file_map.items():

                if fname.endswith(value):
                    record[field_output + "_URL"] = furl

    record["submission_time"] = row.get("_submission_time")

    selected_data.append(record)

# =========================
# SAVE JSON
# =========================

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

with open("columns.json", "w", encoding="utf-8") as f:
    json.dump(columns_meta, f, ensure_ascii=False, indent=2)

print("Export success")
