from flask import Flask, request, Response
import requests
import os
import re

app = Flask(__name__)

FORM_UID = os.getenv("FORM_UID")
API_TOKEN = os.getenv("API_TOKEN")

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

@app.route("/file")
def get_file():
    attachment_id = request.args.get("attachment_id")
    record_id = request.args.get("record_id")

    url = f"https://kf.kobotoolbox.org/api/v2/assets/{FORM_UID}/data/{record_id}/attachments/{attachment_id}/"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return "Error", 500

    return Response(
        res.content,
        content_type=res.headers.get("Content-Type"),
        headers={
            "Content-Disposition": res.headers.get("Content-Disposition", "")
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
