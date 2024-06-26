from decimal import Decimal

import util
from util import pdf_read_text


def parse_pdf(pdf_path, info):
    print('开始解析' + pdf_path)
    print(info)
    text = pdf_read_text(pdf_path)
    arr = text.split('\n')

    for item in arr:
        # '贰拾肆圆零柒分 ¥24.07'
        if util.contains_chinese_currency(item):
            rs = util.find_chinese_currency(item)
            info['价税合计_大写'] = rs
            info['价税合计'] = Decimal(util.chinese_to_numerals(rs))
            info['税额'] = info['价税合计'] - info['发票金额']
