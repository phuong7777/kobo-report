import requests
import json
import os
import pandas as pd

# ====== MAP LABEL ======
khu_vuc_nat_map = {
    "bac": "NAT Miền Bắc",
    "trung": "NAT Miền Trung",
    "tay": "NAT Miền Tây"
}

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

# ====== ĐỌC FILE CẤU HÌNH BIẾN ======
fields_df = pd.read_excel("fields.xlsx")
fields = fields_df.to_dict(orient="records")

# Tạo metadata cho header hiển thị
columns_meta = {
    field["field_output"]: field["display_name"]
    for field in fields
}

selected_data = []

for row in data:
    record = {}

    for field in fields:
        field_path = field["field_path"]
        field_output = field["field_output"]

        value = row.get(field_path)

        # Map label nếu là khu_vuc_nat
        if field_output == "khu_vuc_nat":
            value = khu_vuc_nat_map.get(value, value)

        record[field_output] = value

    # luôn thêm submission time
    record["submission_time"] = row.get("_submission_time")
    columns_meta["submission_time"] = "Thời gian nộp"

    selected_data.append(record)

# ====== GHI FILE DATA ======
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(selected_data, f, ensure_ascii=False, indent=2)

# ====== GHI FILE COLUMNS ======
with open("columns.json", "w", encoding="utf-8") as f:
    json.dump(columns_meta, f, ensure_ascii=False, indent=2)

print("Xuất data.json và columns.json thành công!")
