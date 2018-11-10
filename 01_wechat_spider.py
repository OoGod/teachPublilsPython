"""
version: 0.集成版本
author: wudilaoshi
date:20181023
func:微信完整版，包括保存好友信息到文件中，好友性别可视化，好友所在省份可视化，所在城市可视化，特殊好友可视化，签名词云化，好友头像集成，人脸识别等功能。
"""

# 获取国家地图
# 黑龙江省地图
# 黑龙江省各市区地图


# 导入各种需要的库
import itchat
import os
import math
import PIL.Image as Image
import matplotlib.pyplot as plt
import random
from wordcloud import WordCloud
import jieba
import re
import pandas as pd
from pandas import DataFrame
import sys
from pylab import *
import numpy as np
from pyecharts import Pie
from pyecharts import Bar
import time
# 导入Counter类，用于统计值出现的次数
from collections import Counter
# 导入Geo组件，用于生成地理坐标类图
from pyecharts import Geo
# 导入腾讯优图，用来实现人脸检测等功能
import TencentYoutuyun

# 编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# 1.登录微信
itchat.auto_login(hotReload=True)
# 2.爬取好友信息，返回一个json文件friends,并给好友发送消息
friends = itchat.get_friends(update=True)
'''
print(friends)#输出完整信息
itchat.send('你好', toUserName='filehelper')
for friend in friends:
    itchat.send("你好，%s" %(friend['DisplayName'] or friend['NickName']), friend['UserName'])
    time.sleep(.5)
'''


# 3定义一个函数，用来获取好友更加详细的信息
def get_var(var):
    variable = []
    for i in friends:
       value = i[var]
       variable.append(value)
    return variable


# 4.性别统计可视化
def create_sex(FSex):
    sex = dict()
    # 4.1提取好友性别信息，从1开始，因为第0个是自己
    for f in FSex[1:]:
        if f == 1:  # 男
            sex["man"] = sex.get("man", 0) + 1
        elif f == 2:  # 女
            sex["women"] = sex.get("women", 0) + 1
        else:  # 未知
            sex["unknown"] = sex.get("unknown", 0) + 1

    # 在屏幕上打印出来
    total = len(friends[1:])

    # 4.2打印出自己的好友性别比例
    print("男性好友： %.2f%%" % (float(sex["man"])/total * 100) + "n" + "女性好友： %.2f%%" % (float(sex["women"]) / total * 100) + "n" +
          " 不明性别好友： %.2f%%" % (float(sex["unknown"]) / total * 100))

    # 4.3柱状图展示好友比例
    for i,key in enumerate(sex):
        plt.bar(key, sex[key])
    plt.savefig("getsex.png")   # 保存图片
    plt.ion()
    plt.pause(5)
    plt.close()   # 图片显示5s，之后关闭

    # 4.4用饼装图显示好友比例

    # ----------设置中文显示-----------------
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    font_size =11 # 字体大小

    # 更新字体大小
    mpl.rcParams['font.size'] = font_size

    # 调节图形大小，宽，高
    plt.figure(figsize=(6,9))

    # 定义饼状图的标签，标签是列表
    labels = [u'男性好友', u'女性好友', u'性别不明']

    # 每个标签占多大，会自动去算百分比
    sizes = [sex["man"],sex["women"],sex["unknown"]]
    colors = ['red','yellowgreen','lightskyblue']

    # 将某部分爆炸出来， 使用括号，将第一块分割出来，数值的大小是分割出来的与其他两块的间隙
    explode = (0.05,0,0)
    patches,l_text,p_text = plt.pie(sizes,explode=explode,labels=labels,colors=colors,labeldistance = 1.1,
                                    autopct = '%3.1f%%',shadow = False, startangle = 90,pctdistance = 0.6)
    for t in l_text:
        t.set_size(30)
    for t in p_text:
        t.set_size(20)

    # 设置x，y轴刻度一致，这样饼图才能是圆的
    plt.axis('equal')
    plt.legend()
    plt.show()

    # 4.5使用echarts饼状图
    attr = ['帅哥', '美女', '未知']
    value = [sex["man"],sex["women"],sex["unknown"]]
    pie = Pie('好友性别比例', '好友总人数：%d' % len(friends), title_pos='center')
    pie.add('', attr, value, radius=[30, 75], rosetype='area', is_label_show=True,is_legend_show=True, legend_top='bottom')
    pie.show_config()
    pie.render('好友性别比例.html')


# 5.生成用户所在省份可视化数据
def create_province(Provinces):
    a ={}
    for i in Provinces:
        a[i] = Provinces.count(i)
    b = sorted(a.items(), key=lambda item: item[1])
    attrs = []
    values = []
    j = 0
    while j < len(b):
        attr = b[j][0]
        value = b[j][1]
        attrs.append(attr)
        values.append(value)
        j += 1

    # 开始绘图
    bar = Bar("好友所在的城市")
    bar.add("城市",attrs,values,is_stack=True,is_datazoon_show=True)
    bar.render('好友省份比例.html')


# 6.生成用户所在城市可视化数据
def create_city(cities):
    fc=[]
    for v in cities:
        if v != '' and v != '海淀' and v != '延边':
            fc.append(v)
    # 统计每个城市出现的次数
    data = Counter(fc).most_common(5)   # 使用Counter类统计出现的次数，并转换为元组列表
    print(data)
    # 根据城市数据生成地理坐标图
    geo = Geo('好友位置分布', '', title_color='#fff', title_pos='center', width=1200, height=600,background_color='#404a59')
    attr, value = geo.cast(data)
    print(attr)
    print(value)
    geo.add('', attr, value,visual_text_color='#fff', symbol_size=15,is_visualmap=True, is_piecewise=True)
    geo.render('好友位置分布.html')
    # 根据城市数据生成柱状图
    data_top10 = Counter(fc).most_common(10)   # 返回出现次数最多的20条
    bar = Bar('好友所在城市TOP10', '', title_pos='center', width=1200, height=600)
    attr, value = bar.cast(data_top10)
    bar.add('', attr, value, is_visualmap=True, visual_text_color='#fff', is_more_utils=True, is_label_show=True)
    bar.render('好友所在城市TOP10.html')


# 7.获取个性签名，并做清洗后，保存到签名文件中
def getSignature():
    file = open('sign.txt', 'a', encoding='utf-8')
    for f in friends:   # 个性签名（处理签名内容换行的情况）
        signature = f["Signature"].strip().replace("emoji", "").replace("span", "").replace("class", "")
        rec = re.compile("1f\d+\w*|[<>/=]")
        signature = rec.sub("", signature)
        file.write(signature + "\n")
    file.Close()


# 8.生成签名的词云图
def create_word_cloud(filename):
    # 读取文件内容
    text = open("{}.txt".format(filename), encoding='utf-8').read()
    # 注释部分采用结巴分词
    wordlist = jieba.cut(text, cut_all=True)
    wl = " ".join(wordlist)
    # 自定义图片
    coloring = np.array(Image.open( "D:/testpy/back1.png"))
    # 设置词云
    wc = WordCloud(
        # 设置背景颜色
        background_color="white",
        # 设置最大显示的词云数
        max_words=2000,
        # 这种字体都在电脑字体中，window在C:\Windows\Fonts\下，mac下可选/System/Library/Fonts/PingFang.ttc 字体
        font_path='C:\\Windows\\Fonts\\simfang.ttf', height=500, width=500,
        # 设置字体最大值
        max_font_size=60,
        # 设置有多少种随机生成状态，即有多少种配色方案
        random_state=30,mask=coloring ,
    )
    myword = wc.generate(wl)  # 生成词云 如果用结巴分词的话，使用wl 取代 text， 生成词云图
    # 展示词云图
    plt.imshow(myword)
    plt.axis("off")
    plt.show()
    wc.to_file('signature.png')  # 把词云保存下

    # 保存图片 并发送到手机
    # myword.to_file(os.path.join(d, "wechat_cloud.png"))
    # itchat.send_image("wechat_cloud.png", 'filehelper')


# 9.获取头像
def headImg():
    # 在当前位置创建一个用于存储头像的目录img
    base_path = 'img'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    for count, f in enumerate(friends):
        # 根据userName获取头像
        img = itchat.get_head_img(userName=f["UserName"])
        img_name = f['RemarkName'] if f['RemarkName'] != '' else f['NickName']
        img_file = os.path.join(base_path, img_name + str(count) +'.jpg')
        imgFile = open(img_file, "wb")
        imgFile.write(img)
        imgFile.close()


# 10.头像拼接图
def createImg():
    x = 0
    y = 0
    imgs = os.listdir("img")
    # random.shuffle(imgs)
    # 创建640*640的图片用于填充各小图片
    newImg = Image.new('RGBA', (640, 640))
    # 以640*640来拼接图片，math.sqrt()开平方根计算每张小图片的宽高，
    width = int(math.sqrt(640 * 640 / len(imgs)))
    # 每行图片数
    numLine = int(640 / width)
    for i in imgs:
        try:
            img = Image.open("img/" + i)
            # 缩小图片
            img = img.resize((width, width), Image.ANTIALIAS)
            # 拼接图片，一行排满，换行拼接
            newImg.paste(img, (x * width, y * width))
            x += 1
            if x >= numLine:
                x = 0
                y += 1
        except IOError:
            print("img/ %s can not open"%(i))
    newImg.save("all.png")


# 11.头像分析
def analyse_data():
    # 向腾讯优图平台申请的开发密钥，此处需要替换为自己的密钥
    appid = '10151047'
    secret_id = 'AKID59AA4pi1Sis5GIS2tdCe1b7W2T2asTjr'
    secret_key = 'N5mMxsiO6zjIk7Kj3DIPPLG4mOvOjvpk'
    userid = '924271966'
    end_point = TencentYoutuyun.conf.API_YOUTU_END_POINT # 优图开放平台
    youtu = TencentYoutuyun.YouTu(appid, secret_id, secret_key, userid, end_point)
    use_face = 0
    not_use_face = 0
    base_path = 'img'
    for file_name in os.listdir(base_path):
        result = youtu.DetectFace(os.path.join(base_path, file_name)) # 人脸检测与分析
        print(result) # 参考 https://open.youtu.qq.com/legency/#/develop/api-face-analysis-detect
        # 判断是否使用人像
        if result['errorcode'] == 0: # errorcode为0表示图片中存在人像
            use_face += 1
            gender = '男' if result['face'][0]['gender'] >= 50 else '女'
            age = result['face'][0]['age']
            beauty = result['face'][0]['beauty'] # 魅力值
            glasses = '不戴眼镜 ' if result['face'][0]['glasses'] == 0 else '戴眼镜'
            # print(file_name[:-4], gender, age, beauty, glasses, sep=',')
            with open('header.txt', mode='a', encoding='utf-8') as f:
                f.write('%s,%s,%d,%d,%s' % (file_name[:-4], gender, age, beauty, glasses))
        else:
            not_use_face += 1
    attr = ['使用人脸头像', '未使用人脸头像']
    value = [use_face, not_use_face]
    pie = Pie('好友头像分析', '', title_pos='center')
    pie.add('', attr, value, radius=[30, 75], is_label_show=True,
    is_legend_show=True, legend_top='bottom')
    # pie.show_config()
    pie.render('好友头像分析.html')


# 12.特殊好友可视化
# 定义一个函数，用来爬取好友星标信息
def create_starf(NickName,StarFriend,ContactFlag):
    star_list = []   # 星标朋友
    deny_see_list = []   # 不让他看我的朋友圈
    no_see_list = []   # 不看他的朋友圈
    for sid,val in enumerate(StarFriend):
        if val==1:
            star_list.append(NickName[sid])
    for sid,val in enumerate(ContactFlag[1:]):
        if val in ['259', '33027', '65795']:
            deny_see_list.append(NickName[sid])
        if val in ['65539', '65795']:
            no_see_list.append(NickName[sid])
    print('星标好友：', star_list)
    print('不让他看我的朋友圈：', deny_see_list)
    print('不看他的朋友圈：', no_see_list)
    attr = ['星标朋友', '不让他看我的朋友圈', '不看他的朋友圈']
    value = [len(star_list), len(deny_see_list), len(no_see_list)]
    bar = Bar('特殊好友分析', '', title_pos='center')
    bar.add('', attr, value, is_visualmap=True, is_label_show=True)
    bar.render('特殊好友分析.html')


# 13.调用函数得到各变量，并把数据存到csv文件中，保存到桌面
NickName = get_var("NickName")    # 昵称
# print(str(NickName))
Sex = get_var('Sex')   # 性别：1男，2女，0未设置
Province = get_var('Province')   # 省份
City = get_var('City')   # 城市
Signature = get_var('Signature')    # 好友签名
RemarkName = get_var('RemarkName')    # 好友备注
StarFriend = get_var('StarFriend')   # 星标好友：1是，0否
ContactFlag = get_var('ContactFlag')    # 好友类型及权限：1和3好友，259和33027不让他看我的朋友圈，65539不看他的朋友圈，65795两项设置全禁止
# data = {'NickName': NickName , 'Sex': Sex , 'Province': Province ,'City': City , 'Signature': Signature}
# frame = DataFrame(data)
# frame.to_csv('data.csv', index= True,encoding="utf_8")
# 3个性签名统计
# getSignature()
# create_word_cloud("sign")
# 6.执行主程序，得到所有好友性别可视化显示
# create_sex(Sex)
# 好友省份统计
# create_province(Province)
# 好友城市统计
# create_city(City)
# 微信好友头像拼接
# headImg()
# createImg()
# 特殊好友可视化
# create_starf(NickName,StarFriend,ContactFlag)
analyse_data()
