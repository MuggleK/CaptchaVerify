# -*- coding: utf-8 -*-
import sys
from setting import file_path
sys.path.append(file_path+'/captcha/python')
from darknet import load_net, load_meta, detect, classify, load_image
from segment import seg_one_img, load_dtc_module
import os
import time
import random
# 加载模块
def load_classify_module(cfg, weights, data):
    net = load_net(cfg, weights, 0)
    meta = load_meta(data)
    return net, meta


# 破解函数
def crack(img_path, dtc_modu, classify_modu, k):

    # 定位汉字,返回多个矩形框
    print('\n'*2 + '定位汉字' + '\n' + '*'*80)
    d = time.time()
    rets = detect(dtc_modu[0], dtc_modu[1], img_path.encode()) 
    print('定位汉字耗时{}'.format(time.time() - d))
    l = len(rets)
    # 设置阈值
    if l > k:
        return 0


    # 切割图片，返回切割后的汉字图片
    print('\n'*2 + '切割图片' + '\n' + '*'*80)
    s = time.time()
    hanzi_list = seg_one_img(img_path, rets)
    # print(hanzi_list)mmmmmmmmmmmmmm
    print('切割图片耗时{}'.format(time.time() - s))

    # 汉字识别，返回汉字字符串
    print('\n'*2 + '汉字识别' + '\n' + '*'*80)
    hanzis = {}
    for path in hanzi_list: # 对切割的汉字图片进行遍历
        img = load_image(path.encode(), 0 , 0)
        res = classify(classify_modu[0], classify_modu[1], img)
        hanzi = [('\\' + r[0].decode('utf-8')).encode('utf-8').decode('unicode_escape') for r in res[0:10]]
        hanzis[hanzi_list[path]]= hanzi
        os.remove(path)

    return hanzis
def main(img_path, dtc_modu, classify_modu, k,hanzi):
    han_pos =crack(img_path, dtc_modu, classify_modu, k)
    result = match_han(han_pos, hanzi)
    return  result
def match_han(han_pos,hanzi):

    hanzi_list = list(hanzi)
    acc_han_pos = {k:v[0]  for k,v in han_pos.items()}
    new_acc_han_pos = {v: k for k, v in acc_han_pos.items()}
    _pos = {}

    for i in hanzi_list:
        if i in list(new_acc_han_pos.keys()):
            _pos[i] = new_acc_han_pos[i]
            acc_han_pos.pop(new_acc_han_pos[i])
    for j in hanzi_list:
        if j in _pos:
            pass
        else:
            for k,v in han_pos.items():
                if j in v:
                    _pos[j] = k
                    acc_han_pos.pop(k)
    if len(_pos)==2:
        for j in hanzi_list:
            if j in _pos:
                pass
            else:
                _pos[j] = random.choice(list(acc_han_pos.keys()))
    if len(_pos)<2:
        return None
    return _pos
def load_modle():
    file_path_b = file_path.encode()
    dtc_modu = load_dtc_module(file_path_b+b'/captcha/cfg/yolo-origin.cfg',
                                file_path_b+b'/captcha/backup/yolo-origin.backup', file_path_b+b'/captcha/cfg/yolo-origin.data')
    # 加载汉字识别模型
    classify_modu = load_classify_module(file_path_b+b"/captcha/cfg/chinese_character.cfg",
                        file_path_b+b"/captcha/backup/chinese_character.weights", file_path_b+b"/captcha/cfg/chinese.data")

    return dtc_modu,classify_modu
if __name__ == '__main__':
    # 加载汉字定位模型
    dtc_modu = load_dtc_module(b'../cfg/yolo-origin.cfg',
                                b'/home/zsy/class/gsxt_captcha/backup/yolo-origin.backup', b'../cfg/yolo-origin.data')
    # 加载汉字识别模型
    classify_modu = load_classify_module(b"../cfg/chinese_character.cfg",
                        b"/home/zsy/class/gsxt_captcha/backup/chinese_character.weights", b"../cfg/chinese.data")
    line = '/home/zsy/class/gsxt_captcha/python/test/1ab7bf081cca4ded83c28ff7351319e2.jpg'
    han_pos = crack(line,dtc_modu,classify_modu,6)
    acc_han_pos = {k: v[0] for k, v in han_pos.items()}
    match_han(han_pos,'罚韦口')




