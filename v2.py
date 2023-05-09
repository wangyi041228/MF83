import cProfile
import sys
import time
from ctypes import windll
from functools import lru_cache
from multiprocessing import Pool
from os import cpu_count, sep, listdir
from statistics import mean
from time import sleep

import win32gui
import win32ui
from PIL import Image, ImageChops
from pyautogui import moveTo, mouseDown, mouseUp

char_list = []
CPU_COUNT = cpu_count()
SAMPLE_PATH = sep.join(('img', 'sample'))
dirs = listdir(SAMPLE_PATH)
for dirr in dirs:
    files = listdir(sep.join((SAMPLE_PATH, dirr)))
    for file in files:
        with Image.open(sep.join((SAMPLE_PATH, dirr, file))) as im:
            for zx in range(-1, 2):
                for zy in range(-1, 2):
                    zt = Image.new('RGBA', (32, 40))
                    zt.paste(im, (zx, zy), mask=im)
                    char_list.append([dirr, zt])
# 内部计算按123456789ABCD
# 输入输出按A234567890JQK
c2v = {
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'A': 10,  # 10
    'B': 10,  # J
    'C': 10,  # Q
    'D': 10,  # K
}
# i2c = {
#     'A': '1',
#     '2': '2',
#     '3': '3',
#     '4': '4',
#     '5': '5',
#     '6': '6',
#     '7': '7',
#     '8': '8',
#     '9': '9',
#     '0': 'A',
#     'J': 'B',
#     'Q': 'C',
#     'K': 'D',
# }
# c2i = {v: k for k, v in i2c.items()}
count2score = {0: 0, 1: 0, 2: 2, 3: 6, 4: 12}
len2score = {0: 0, 1: 0, 2: 2, 3: 6, 4: 12}
i2move = {0: '1', 1: '2', 2: '3', 3: '4'}
RR = '123456789ABCD'  # QKA不算顺子 否则后面加1
n_flags = 3
try:
    _win_v = sys.getwindowsversion()
    if _win_v.major == 6 and _win_v.minor == 1:
        n_flags = 1
        windll.user32.SetProcessDPIAware()
    else:
        windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass


def screenshot():
    toplist, winlist = [], []

    def enum_cb(hwnd, _results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)
    window = [(hwnd, title) for hwnd, title in winlist if "Möbius Front '83" == title or
              "The Zachtronics Solitaire Collection" == title]
    if window:
        hwnd = window[0][0]
        box = win32gui.GetClientRect(hwnd)  # win32gui.GetWindowRect(hwnd)
        box_w = box[2]
        box_h = box[3]
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, box_w, box_h)  # 10%
        save_dc.SelectObject(save_bitmap)
        _result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), n_flags)  # 58%
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)  # 19%
        _im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)  # 12%
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        if _result != 0:
            return _im


@ lru_cache()
def score(stack, su, cha) -> int:
    if stack == '':
        if cha == 'B':
            return 2
        return 0
    if su + c2v[cha] in [15, 31]:
        _result = 2
    else:
        _result = 0
    ll = len(stack)
    pin = ll - 1
    same = 1
    while stack[pin] == cha and pin > -1:
        pin -= 1
        same += 1
    _result += count2score[same]
    new_stack = stack + cha
    for mm in range(0, ll - 1):
        if ''.join(sorted(new_stack[mm:])) in RR:
            return _result + ll - mm + 1
    return _result


def work_in_pool(states):
    _new_states = []
    for _state in states:
        ok = True
        for _i in range(4):
            if _state[_i]:
                _c = _state[_i][-1]
                new_sum = _state[5] + c2v[_c]
                if new_sum < 32:
                    # this_state = _state.copy()
                    # this_state[_i] = this_state[_i][:-1]
                    # this_state[6] += score(this_state[4], _state[5], _c)
                    # this_state[4] += _c
                    # this_state[5] = new_sum
                    # this_state[7] += i2move[_i]

                    s6 = score(_state[4], _state[5], _c) + _state[6]
                    s4 = _c + _state[4]
                    s7 = _state[7] + i2move[_i]
                    if _i == 0:
                        this_state = (_state[0][:-1], _state[1], _state[2], _state[3], s4, new_sum, s6, s7)
                    elif _i == 1:
                        this_state = (_state[0], _state[1][:-1], _state[2], _state[3], s4, new_sum, s6, s7)
                    elif _i == 2:
                        this_state = (_state[0], _state[1], _state[2][:-1], _state[3], s4, new_sum, s6, s7)
                    else:
                        this_state = (_state[0], _state[1], _state[2], _state[3][:-1], s4, new_sum, s6, s7)

                    _new_states.append(this_state)
                    ok = False
        if ok:
            for _i in range(4):
                if _state[_i]:
                    _c = _state[_i][-1]
                    new_sum = c2v[_c]
                    if new_sum < 32:
                        # this_state = _state.copy()
                        # this_state[_i] = this_state[_i][:-1]
                        # if _c == 'B':
                        #     this_state[6] += 2
                        # this_state[4] = _c
                        # this_state[5] = new_sum
                        # this_state[7] += f'_{i2move[_i]}'

                        s6 = _state[6] + 2 if _c == 'B' else _state[6]
                        s4 = _c
                        s7 = _state[7] + f'_{i2move[_i]}'
                        if _i == 0:
                            this_state = (_state[0][:-1], _state[1], _state[2], _state[3], s4, new_sum, s6, s7)
                        elif _i == 1:
                            this_state = (_state[0], _state[1][:-1], _state[2], _state[3], s4, new_sum, s6, s7)
                        elif _i == 2:
                            this_state = (_state[0], _state[1], _state[2][:-1], _state[3], s4, new_sum, s6, s7)
                        else:
                            this_state = (_state[0], _state[1], _state[2], _state[3][:-1], s4, new_sum, s6, s7)

                        _new_states.append(this_state)
    return _new_states


def get_cards():
    screen = screenshot()
    b_base = [817, 1093, 1369, 1645]
    y_base = [57 + mmm * 54 for mmm in range(13)]
    count = 1
    chars = ['', '', '', '']
    for idx, x in enumerate(b_base):
        for y in y_base:
            new_x, new_y = x + 3, y + 4
            for z in range(3):
                cr0 = screen.crop((new_x, new_y, new_x + 32, new_y + 40))
                # cr0.save(f'img\\{str(count)}_{str(z)}a.png')
                cr1 = cr0.point(lambda n: 0 if n < 80 else 255).convert('L').convert(
                    'RGBA').point(lambda n: 0 if n < 200 else 255).convert('L')
                # cr1.save(f'img\\{str(count)}_{str(z)}b.png')
                image_load = cr1.load()
                image_x = []
                image_y = []
                s_x, s_y = cr1.size
                for xx in range(s_x):
                    for yy in range(s_y):
                        if image_load[xx, yy] == 0:
                            image_x.append(xx)
                            image_y.append(yy)
                mx = int(round(mean(image_x), 0)) if image_x else 16
                my = int(round(mean(image_y), 0)) if image_y else 20
                new_x += mx - 16
                new_y += my - 20

            cr = screen.crop((new_x, new_y, new_x + 32, new_y + 40))
            # cr.save(f'img\\{str(count)}a.png')
            crl = cr.point(lambda n: 0 if n < 80 else 255).convert('L').convert(
                'RGBA').point(lambda n: 0 if n < 200 else 255)
            crl.save(f'img\\{str(count)}.png')

            dif = [[iim[0], ImageChops.difference(crl, iim[1]).point(
                                            lambda n: 0 if n < 40 else 255).convert('L'), 0] for iim in char_list]

            for iim in dif:
                mm = iim[1].load()
                mmx, mmy = iim[1].size
                for ssx in range(mmx):
                    for ssy in range(mmy):
                        if mm[ssx, ssy] == 0:
                            iim[2] += 1
                # if count in [40]:
                #     iim[1].save(f'img\\{str(count)}_{iim[0]}.png')
            dif.sort(key=lambda zzx: zzx[2], reverse=True)
            chars[idx] += dif[0][0]
            print(count, dif[0][0], f'({round(dif[0][2] / 12.8, 2)}%)')
            count += 1
    return chars


def operate(_operations):
    x_y_count = {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0
    }
    x_y = [[(940 + j * 276, 867 - i * 55) for i in range(13)] for j in range(4)]
    cn = 0
    x_y_new = {
        3: (608, 611),
        4: (608, 673),
        5: (608, 733),
        6: (608, 795),
        7: (608, 854),
        8: (608, 870),
        9: (608, 885),
        10: (608, 895),
        11: (608, 905),
        12: (608, 915),
        13: (608, 920),  # (1+2+3)*4+4=28
    }
    moveTo((100, 100), duration=0.2)
    mouseDown()
    sleep(0.1)
    mouseUp()
    for ch in _operations:
        if ch != '_':
            xxyy = int(ch) - 1
            moveTo(x_y[xxyy][x_y_count[ch]], duration=0.2)
            x_y_count[ch] += 1
            cn += 1
            mouseDown()
            sleep(0.1)
            mouseUp()
        else:
            moveTo(x_y_new[cn], duration=0.2)
            mouseDown()
            sleep(0.1)
            mouseUp()
            cn = 0
        sleep(0.5)
    moveTo((1329, 785), duration=0.2)
    mouseDown()
    sleep(0.1)
    mouseUp()
    sleep(6)


def solve(_cards=None):
    if _cards is None:
        _cards = get_cards()
    init_state = [
        _cards[0],
        _cards[1],
        _cards[2],
        _cards[3],
        '', 0, 0, ''
    ]
    text = ''.join(init_state[:4])
    input_error = False
    for c in c2v:
        if text.count(c) != 4:
            print(f'数据错误，有{text.count(c)}个{c}')
            input_error = True
    if input_error:
        exit(0)
    print('_'.join(init_state[:4]))
    time_0 = time.perf_counter()
    old_states = [init_state]
    moves = 0
    while moves < 52:
        time_1 = time.perf_counter()
        len_old = len(old_states)
        if len_old > 500000:

            # new_states = []
            # state_c = 0
            # results = []
            # p = Pool(CPU_COUNT)
            # new_states = []
            # state_c = 0
            # results = []
            # p = Pool(CPU_COUNT)
            # for i in range(1, CPU_COUNT + 1):
            #     i0 = int(len_old * i / CPU_COUNT)
            #     states_p = old_states[state_c:i0]
            #     state_c = i0
            #     if states_p:
            #         results.append(p.apply_async(work_in_pool, (states_p, )))
            # p.close()
            # p.join()
            # for result in results:
            #     new_states.extend(result.get())

            new_states = []
            state_c = 0
            p = Pool(CPU_COUNT)
            fdata = []
            for i in range(1, CPU_COUNT + 1):
                i0 = int(len_old * i / CPU_COUNT)
                states_p = old_states[state_c:i0]
                state_c = i0
                fdata.append(states_p)
            results = p.map(work_in_pool, fdata)
            p.close()
            p.join()
            for result in results:
                new_states.extend(result)

        else:
            new_states = work_in_pool(old_states)
        new_states.sort(key=lambda x: x[6], reverse=True)
        new_s = []
        new_set = set()
        for state in new_states:
            t = f'{state[0]}_{state[1]}_{state[2]}_{state[3]}_{state[4]}'
            if t in new_set:
                pass
            else:
                new_set.add(t)
                new_s.append(state)

        # if len(new_s) > 100000:  # 足够好
        #     b = sorted([x[6] for x in new_s], reverse=True)[100000]
        #     old_states = [x for x in new_s if x[6] >= b]
        # else:
        #     old_states = new_s

        old_states = new_s  # 必须有16G内存

        moves += 1
        print('MOVE', moves, len(old_states), f'{time.perf_counter() - time_1:.3f}')
    print(old_states[0][6], old_states[0][7], f'{time.perf_counter() - time_0:.3f}')
    operations = old_states[0][7]
    # operate(operations)
    print()


def main():
    # while 1:
    #     solve()
    cards = ['751CB9C5723C9', '22D51288DADBA', '7B5A11D6884B6', 'A64399C734643']
    # cards = ['B6B672582883A', '4C55767DD9611', '2443A2C1DA19C', 'C4B3BD78959A3']  # 最快 45/150/170s
    # cards = ['A211753D89C78', '44D5B359AAC4B', '6387656B4C16D', '22A9132D98B7C']  # 最慢 50/630/700s
    solve(_cards=cards)


def test():
    with cProfile.Profile() as pr:
        main()
        pr.print_stats()


if __name__ == '__main__':
    test()
    # main()
