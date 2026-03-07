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

# ====== GỌI API KOBO ======
url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"
headers = {
    "Authorization": f"Token {API_TOKEN}"
}

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

# Tạo dictionary mapping
choices_map = {}

for _, row in choices_df.iterrows():
    var = row["list_name"]
    val = row["name"]
    label = row["label"]

    if var not in choices_map:
        choices_map[var] = {}

    choices_map[var][val] = label

# ====== TẠO META COLUMNS ======
columns_meta = {
    field["field_output"]: field["display_name"]
    for field in fields
}

selected_data = []

# ====== XỬ LÝ DATA ======
for row in data:

    record = {}

    for field in fields:

        field_path = field["field_path"]
        field_output = field["field_output"]

        value = row.get(field_path)

        # ===== xử lý file attachment =====
        if value and "_attachments" in row:
        
            for att in row["_attachments"]:
        
                if att.get("filename") == value:
                    record[field_output + "_URL"] = att.get("download_url")
                    
        # Map label nếu có trong choices
        if field_output in choices_map:
            value = choices_map[field_output].get(value, value)

        record[field_output] = value

    # luôn thêm submission time
    record["submission_time"] = row.get("_submission_time")
    columns_meta["submission_time"] = "Thời gian nộp"

    selected_data.append(record)

# ====== GHI DATA.JSON ======
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

# ====== GHI COLUMNS.JSON ======
with open("columns.json", "w", encoding="utf-8") as f:
    json.dump(columns_meta, f, ensure_ascii=False, indent=2)

print("Xuất data.json và columns.json thành công!")


