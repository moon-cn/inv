import os
from decimal import Decimal

import cv2  # opencv包


import util
from util import pdf_read_text

import consts


def do_parse(pdf_path):
    img_path = util.pdf_to_img(pdf_path)
    info = read_qr_code(img_path)
    os.remove(img_path)

    if info['发票类型'] == '区块链电子发票':
        parse_shenzhen(pdf_path, info)

    parse_total(pdf_path, info)

    info['发票类型_中文'] = consts.INV_TYPE_DICT.get(info['发票类型'])

    return info


def read_qr_code(img_path):
    """
    读取图片中的二维码
    :param img_path:图片路径
    :type img_path:str
    :return:识别的内容
    :rtype:tuple
    """
    detector = cv2.wechat_qrcode_WeChatQRCode()  # 微信贡献的代码，很好用
    img = cv2.imread(img_path)
    if img is None:
        return {"状态": '没有二维码'}  # 没有二维码
    res, _ = detector.detectAndDecode(img)
    if res is None or len(res) == 0:
        return {"状态”:“解析二维码为空"}

    # 深圳电子发票
    if res[0].startswith("https://bcfp.shenzhen.chinatax.gov.cn"):
        url = res[0]
        print(url)

        return {
            "发票类型": "区块链电子发票"
        }

    res = res[0].split(',')
    if res[0] != '01':  # 第1个属性值，固定01
        raise ValueError("发票二维码第一个应该是固定01")
    info = {
        "发票类型": res[1],  # 发票种类代码
        "发票代码": res[2],
        "发票号码": res[3],
        "发票金额": Decimal(res[4]),
        "开票日期": res[5],
        "校验码": res[6],
    }

    return info


def parse_total(pdf_path, info):
    print('开始解析' + pdf_path)
    lines = pdf_read_text(pdf_path)

    total_flag = find_line(lines, '价税合计',True)
    if total_flag is None:
        info['状态'] = '获取价税合计失败'
        return


    x0, y0, x1, y1, text = total_flag
    text_center_y = y0 + (y1 - y0) / 2
    print('价税合计', total_flag)
    for line in lines:
        _x0, _y0, _x1, _y1, _text = line
        if _y0 < text_center_y < _y1:
            print('文字和价税合计在同一行', _text)
            numbers = util.find_numbers(_text)
            if len(numbers) > 0:
                n = numbers[0]
                info['价税合计'] = Decimal(n)
                if info['发票金额']:
                    info['税额'] = info['价税合计'] - info['发票金额']
                    info['税率'] = round(info['税额'] / info['发票金额'], 2)
                break


def parse_shenzhen(path, info):
    print('开始解析深圳发票')
    lines = pdf_read_text(path)
    for line in lines:
        print(line)
    info['发票代码'] = find_first_text_after_text(lines, '发票代码')
    info['发票号码'] = find_first_text_after_text(lines, '发票号码')
    info['开票日期'] = find_first_text_after_text(lines, '开票日期')
    info['校验码'] = find_first_text_after_text(lines, '校验码')

    amt = find_first_text_after_text(lines, '计')
    amt = util.find_numbers(amt)
    if len(amt) > 0:
        info['发票金额'] = Decimal(amt[0])
    print(info)


def find_line(lines, text, use_contains=False):
    for line in lines:
        if use_contains:
            if text in line[4]:
                return line
        else:
            if line[4] == text:
                return line

    return None;


def find_same_line_after(lines, target):
    x0, y0, x1, y1, text = target
    text_center_y = y0 + (y1 - y0) / 2

    rs = []
    for line in lines:
        _x0, _y0, _x1, _y1, _text = line
        if _y0 < text_center_y < _y1 and _x0 > x1:
            rs.append(line)

    return rs


def find_same_line_after_text(lines, text):
    target = find_line(lines, text)
    x0, y0, x1, y1, text = target
    text_center_y = y0 + (y1 - y0) / 2

    list = []
    for line in lines:
        _x0, _y0, _x1, _y1, _text = line
        if _y0 < text_center_y < _y1 and _x0 > x1:
            list.append(line)

    return list


def find_first_text_after_text(lines, text):
    target = find_line(lines, text)
    if target is None:
        return None
    x0, y0, x1, y1, text = target
    text_center_y = y0 + (y1 - y0) / 2

    for line in lines:
        _x0, _y0, _x1, _y1, _text = line
        if _y0 < text_center_y < _y1 and _x0 > x1:
            return _text


