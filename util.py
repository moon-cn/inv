import re
from datetime import datetime

import pdfplumber


def find_first_num(text):
    match = re.search(r'\d+(\.\d+)?', text)

    if match:
        first_number = match.group()
        print(f"找到的第一个数字是：{first_number}")
        return first_number
    else:
        print("没有找到数字。")


def find_second_num(text):
    pattern = r'\d+(\.\d+)?'
    match = re.search(pattern, text)
    if match:
        first_number = match.group()
        print(f"找到的第一个数字是：{first_number}")

        # 从第一个数字的末尾继续搜索下一个数字
        start_index = match.end()
        match = re.search(pattern, text[start_index:])

        if match:
            second_number = match.group()
            print(f"找到的第二个数字是：{second_number}")
            return second_number
        else:
            print("没有找到第二个数字。")
    else:
        print("没有找到数字。")


def pdf_read_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

    return text


def now_str():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    print("date and time:", date_time)
    return date_time


# 是否中文大写金额
def is_chinese_currency(text):
    pattern = re.compile(r"^(?:[零壹贰叁肆伍陆柒捌玖]|\d)+(?:[元角分])+$")
    return bool(pattern.match(text))


def contains_chinese_currency(text):
    pattern = re.compile(r"(?:[零壹贰叁肆伍陆柒捌玖]|\d)+(?:[元角分])")
    return bool(pattern.search(text))


def find_chinese_currency(text):
    pattern = r'[\u4e00-\u9fa5]+'

    chinese_amount = re.findall(pattern, text)
    rs = chinese_amount[0] if chinese_amount else None

    return rs


def chinese_to_numerals(chinese_str):
    chinese_numerals = {'零': 0, '壹': 1, '贰': 2, '叁': 3, '肆': 4,
                        '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9}
    chinese_units = {'圆': 1, '角': 0.1, '分': 0.01}

    num = 0
    temp = 0  # 临时存储中间结果

    for char in chinese_str:
        if char in chinese_units:
            unit = chinese_units[char]
            num += temp * unit
            temp = 0
        elif char in chinese_numerals:
            temp += chinese_numerals[char]
        elif char == '拾':
            temp *= 10
        elif char == '佰':
            temp *= 100
        elif char == '仟':
            temp *= 1000
        elif char == '万':
            temp *= 10000
        elif char == '亿':
            temp *= 100000000

    return num

