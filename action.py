import cv2
import time
import os
import random
import sys
import mss
import numpy
from PIL import ImageGrab
import config

# 检测系统
if sys.platform == 'darwin':
    scalar = True
else:
    scalar = False

# 截屏起点
a = 0


def screenshot(monitor):
    if scalar:
        # width = int(im.shape[1]/2)
        # height = int(im.shape[0]/2)
        # dim = (width, height)
        monitor2 = (0, 0, 1136, 710)
        screen = ImageGrab.grab(monitor2)
        im = numpy.array(screen)
        resized = cv2.cvtColor(im, cv2.COLOR_RGBA2BGR)
        screen = resized
        # screen = cv2.resize(resized, dim, interpolation = cv2.INTER_AREA)
        # cv2.imshow("Image", screen)
        # print(screen.shape)
        # cv2.waitKey(0)
    else:
        im = numpy.array(get_game_screen(monitor))
        screen = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)

    return screen


# 在背景查找目标图片，并返回查找到的结果坐标列表，target是背景，want是要找目标
def locate(target, want, show=bool(0), msg=bool(0)):
    "在背景查找目标图片，并返回查找到的结果坐标列表，target是背景，want是要找目标"
    loc_pos = []
    want, treshold, c_name = want[0], want[1], want[2]
    result = cv2.matchTemplate(target, want, cv2.TM_CCOEFF_NORMED)
    location = numpy.where(result >= treshold)

    if msg:  # 显示正式寻找目标名称，调试时开启
        print(c_name, 'searching... ')

    h, w = want.shape[:-1]  # want.shape[:-1]

    n, ex, ey = 1, 0, 0
    for pt in zip(*location[::-1]):  # 其实这里经常是空的
        x, y = pt[0] + int(w / 2), pt[1] + int(h / 2)
        if (x - ex) + (y - ey) < 15:  # 去掉邻近重复的点
            continue
        ex, ey = x, y

        cv2.circle(target, (x, y), 10, (0, 0, 255), 3)

        if msg:
            print(c_name, 'we find it !!! ,at', x, y)

        if scalar:
            x, y = int(x) + a, int(y)
        else:
            x, y = int(x) + a, int(y)

        loc_pos.append([x, y])

    if show:  # 在图上显示寻找的结果，调试时开启
        print('Debug: show action.locate')
        cv2.imshow('we get', target)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if len(loc_pos) == 0:
        # print(c_name,'not find')
        pass

    return loc_pos


# 按【文件内容，匹配精度，名称】格式批量聚聚要查找的目标图片，精度统一为0.95，名称为文件名
def load_imgs():
    mubiao = {}
    if scalar:
        path = os.getcwd() + '/png'
    else:
        path = os.getcwd() + '/png'
    file_list = os.listdir(path)
    for file in file_list:
        name = file.split('.')[0]
        file_path = path + '/' + file
        a = [cv2.imread(file_path), 0.95, name]
        mubiao[name] = a

    return mubiao


# 蜂鸣报警器，参数n为鸣叫次数
def alarm(n):
    frequency = 1500
    duration = 500

    if os.name == 'nt':
        import winsound
        winsound.Beep(frequency, duration)


# 裁剪图片以缩小匹配范围，screen为原图内容，upleft、downright是目标区域的左上角、右下角坐标
def cut(screen, upleft, downright):
    a, b = upleft
    c, d = downright
    screen = screen[b:d, a:c]

    return screen


# 随机偏移坐标，防止游戏的外挂检测。p是原坐标，w、n是目标图像宽高，返回目标范围内的一个随机坐标
def cheat(p, w, h):
    k, b = p
    if scalar:
        w, h = int(w / 3 / 2), int(h / 3 / 2)
    else:
        w, h = int(w / 3), int(h / 3)
    c, d = random.randint(-w, w), random.randint(-h, h)
    e, f = k + c, b + d
    y = [e, f]
    print('随机坐标：', p, w, h, y)
    return y


# 随机偏移坐标，防止游戏的外挂检测。
def cheat_jixu(p, w, h):
    "继续是可以点击全屏的，所以随机性大一点更合理"
    l, r = p
    c, d = random.randint(l - 400, l - 100), random.randint(30, 300)
    e, f = l + c, r - d
    y = [e, f]
    print('随机坐标：', p, y)
    return y


# 多个显示器的情况下，获取游戏所在的显示器


def get_game_screen(mp):
    "多个显示器的情况下，获取游戏所在的显示器"
    sct = mss.mss()
    monitors = sct.monitors
    # 如果有第二个显示器，单显示器会有两个，双屏三个，依次类推
    if len(monitors) > 2:
        print('检测到多个显示器，请把游戏放到主显示器左上角')

    # 获取第1个显示器的坐标和尺寸，也就是主显示器
    target_monitor = monitors[config.MAIN_SCREEN_INDEX]
    monitor = {"top": target_monitor["top"], "left": target_monitor["left"], "width": target_monitor["width"],
               "height": target_monitor["height"]}

    sct_img = sct.grab(monitor)
    return sct_img
