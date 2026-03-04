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

# ====== CẤU HÌNH ======
FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"
headers = {
    "Authorization": f"Token {API_TOKEN}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:

    data = response.json()["results"]

    # ====== ĐỌC FILE CẤU HÌNH BIẾN ======
    fields_df = pd.read_excel("fields.xlsx")
    fields = fields_df.to_dict(orient="records")

    # Lưu metadata cho frontend
    metadata = {f["field_output"]: f["display_name"] for f in fields} 

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

        selected_data.append(record)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(selected_data, f, ensure_ascii=False, indent=2)

    print("Xuất data.json thành công!")

else:
    print("Lỗi khi gọi API:", response.status_code)

