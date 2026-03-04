import requests
import json

khu_vuc_nat_map = {
    "bac": "NAT Miền Bắc",
    "trung": "NAT Miền Trung",
    "tay": "NAT Miền Tây"
}

# ====== CẤU HÌNH ======
FORM_UID = "aDtzYakH7kU6dp7eXncupi"
API_TOKEN = "47d6a3779dda02d4fb236b7dc20b6941d3dc2ad7"

url = f"https://kc.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/"
headers = {
    "Authorization": f"Token {API_TOKEN}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()["results"]  # lấy danh sách bản ghi
    
    # Nếu muốn chọn 20–30 biến cụ thể:
    selected_data = []
    for row in data:
        selected_data.append({
	    "id_ho_so": row.get("group_hoso/id_ho_so"),
	    "khu_vuc_nat": khu_vuc_nat_map.get(row.get("group_hoso/khu_vuc_nat"), ""),
            "tinh_tp": row.get("group_hoso/tinh_tp"),
            "quan_huyen": row.get("group_hoso/quan_huyen"),
            "xa_phuong": row.get("group_hoso/xa_phuong"),
            "thon_ap": row.get("group_hoso/thon_ap"),
            "chuho_ten_001": row.get("group_hgd/chuho_ten"),
            "chuho_dia_chi": row.get("group_hgd/chuho_dia_chi"),
            "chuho_toa_do": row.get("group_hgd/chuho_toa_do"),
            "chuho_cmnd": row.get("group_hgd/chuho_cmnd"),
            "chuho_ngay_cap": row.get("group_hgd/chuho_ngay_cap"),
            "chuho_noi_cap": row.get("group_hgd/chuho_noi_cap"),
            "chuho_dien_thoai": row.get("group_hgd/chuho_dien_thoai"),
            "submission_time": row.get("_submission_time")        })
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(selected_data, f, ensure_ascii=False)
    
    print("Xuất data.json thành công!")
else:
    print("Lỗi khi gọi API:", response.status_code)