import requests
import json
import os
import pandas as pd

# ====== LẤY BIẾN MÔI TRƯỜNG ======
FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

if not FORM_UID or not API_TOKEN:
    print("Thiếu FORM_UID hoặc API_TOKEN")
    exit()

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

# ====== GỌI API DATA ======
url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Lỗi khi gọi API:", response.status_code)
    exit()

data = response.json()["results"]

# ====== ĐỌC FILE FIELDS ======
fields_df = pd.read_excel("fields.xlsx")
fields = fields_df.to_dict(orient="records")

# ====== ĐỌC FILE CHOICES ======
choices_df = pd.read_excel("choices.xlsx")

choices_map = {}

for _, row in choices_df.iterrows():

    list_name = row["list_name"]
    name = row["name"]
    label = row["label"]

    if list_name not in choices_map:
        choices_map[list_name] = {}

    choices_map[list_name][name] = label

# ====== META COLUMNS ======
columns_meta = {
    field["field_output"]: field["display_name"]
    for field in fields
}

columns_meta["submission_time"] = "Thời gian nộp"

selected_data = []

# ====== XỬ LÝ DATA ======
for row in data:

    record = {}

    record_id = row["_id"]

    # ===== LẤY ATTACHMENTS =====
    attach_url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/{record_id}/attachments/"
    attach_res = requests.get(attach_url, headers=headers)

    attachments = []

    if attach_res.status_code == 200:
        attachments = attach_res.json()["results"]

    attachment_map = {
        a["filename"]: a["download_url"]
        for a in attachments
    }

    # ===== MAP FIELD =====
    for field in fields:

        field_path = field["field_path"]
        field_output = field["field_output"]
        list_name = field.get("choice_list")

        value = row.get(field_path)

        # ===== map label choices =====
        if list_name in choices_map:
            value = choices_map[list_name].get(value, value)

        # ===== xử lý file upload =====
        if value in attachment_map:
            record[field_output + "_URL"] = attachment_map[value]

        record[field_output] = value

    record["submission_time"] = row.get("_submission_time")

    selected_data.append(record)

# ====== GHI DATA.JSON ======
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

# ====== GHI COLUMNS.JSON ======
with open("columns.json", "w", encoding="utf-8") as f:
    json.dump(columns_meta, f, ensure_ascii=False, indent=2)

print("Xuất data.json và columns.json thành công!")
