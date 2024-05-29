import base64
import json
import time

from flask import Flask, request, render_template

import parse
import parse_pdf
from consts import INV_KEYS

app = Flask(__name__, static_url_path="")
app.secret_key = 'zhrmghgws'
app.json.ensure_ascii = False  # 解决中文乱码问题


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("files")
    list = []
    for file in files:
        pdf_path = "uploads/" + str(time.time())
        file.save(pdf_path)

        file_path = parse.pdf_to_img(pdf_path)
        info = parse.read_qr_code(file_path)
        parse_pdf.parse_pdf(pdf_path, info)

        info['文件名称'] = file.filename
        list.append(info)




    return render_template("result.html",
                           list=list,
                           cols = json.dumps(INV_KEYS,ensure_ascii=False),
                           data=json.dumps(list, ensure_ascii=False)
                           )



if __name__ == '__main__':
    app.run(host='0.0.0.0')