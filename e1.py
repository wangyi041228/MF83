import ctypes
import string
import subprocess
import win32api
import win32con
import time
import random

user32 = ctypes.windll.LoadLibrary("user32.dll")

cards = "A23456789XJQK"
vals = list(range(1, 11)) + [10, 10, 10]
order = list(range(len(cards)))


def getcard(c):
    i = cards.find(c)
    if i == -1:
        raise ValueError(f"Invalid Card: {c}")

    return ((cards[i], vals[i], order[i]))


def stackstr(s):
    stack = []
    for c in s:
        stack.append(getcard(c))
    return stack


def deal():
    deck = list(zip(list(cards), vals, order)) * 4
    random.shuffle(deck)
    board = [deck[i:i + 13] for i in range(0, 52, 13)]
    return board


def isrun(group):
    srun = sorted([x[2] for x in group])
    for i in range(1, len(srun)):
        if (srun[i - 1] + 1) != srun[i]:
            return False
    return True


def score(stack):
    score = 0
    if len(stack) == 0:
        return score

    if stack[0][0] == "J":
        score += 2

    # get stack total and any sets
    total = 0
    lastcard = " "
    setlen = 0
    for c in stack:
        if lastcard == c[0]:
            setlen += 1
            score += (setlen * 2)
        else:
            setlen = 0
        lastcard = c[0]

        total += c[1]
        if total == 15:
            score += 2
        elif total == 31:
            score += 2

    # get any runs
    for l in range(7, 2, -1):
        if l > len(stack):
            continue
        i = 0
        while i <= (len(stack) - l):
            if i + l > len(stack):
                break
            if isrun(stack[i:i + l]):
                score += l
                stack = stack[:i] + stack[i + l:]
            else:
                i += 1

    return score


maxdepth = 0


def bruteforce2(board, stack=[], scoresofar=0, stacksleft=1, depth=0):
    global maxdepth
    if depth == 0:
        maxdepth = 0
    elif depth > maxdepth:
        maxdepth = depth
        print("DEBUG: At depth", depth)

    # stop it from going too far
    if depth >= 14:
        return (score(stack) + scoresofar, stack, board)

    # just brute force for 1 stack maximum score
    total = sum([c[1] for c in stack])

    pulled = 0
    wins = -1
    winstack = []
    winboard = None
    for i in range(4):
        if len(board[i]) > 0 and (board[i][-1][1] + total) <= 31:
            newboard = []
            for ii in range(4):
                if ii == i:
                    newboard.append(board[ii][:-1])
                else:
                    newboard.append(board[ii][:])
            newstack = stack[:]
            card = board[i][-1]
            card = (card[0], card[1], card[2], (i, len(board[i]) - 1))
            newstack.append(card)
            s, trystack, tryboard = bruteforce2(newboard, newstack, scoresofar, stacksleft, depth + 1)
            if s > wins or (s == wins and len(board[pulled]) < len(board[i])):
                winstack = trystack
                wins = s
                pulled = i
                winboard = tryboard
    if wins == -1:
        # end of a stack
        stackscore = score(stack)
        if stacksleft == 0:
            return (stackscore + scoresofar, stack, board)
        else:
            s, _, _ = bruteforce2(board, [], scoresofar + stackscore, stacksleft - 1, depth + 1)
            return s, stack, board
    else:
        # pass it back up the chain
        return (wins, winstack, winboard)


def bruteforce(board, stack=[]):
    # just brute force for 1 stack maximum score
    total = sum([c[1] for c in stack])

    pulled = 0
    wins = -1
    winstack = []
    winboard = None
    for i in range(4):
        if len(board[i]) > 0 and (board[i][-1][1] + total) <= 31:
            newboard = []
            for ii in range(4):
                if ii == i:
                    newboard.append(board[ii][:-1])
                else:
                    newboard.append(board[ii][:])
            newstack = stack[:]
            card = board[i][-1]
            card = (card[0], card[1], card[2], (i, len(board[i]) - 1))
            newstack.append(card)
            s, trystack, tryboard = bruteforce(newboard, newstack)
            if s > wins or (s == wins and len(board[pulled]) < len(board[i])):
                winstack = trystack
                wins = s
                pulled = i
                winboard = tryboard
    if wins == -1:
        return (score(stack), stack, board)
    else:
        return (wins, winstack, winboard)


def printstate(board, stack):
    i = 0
    print("---------+-" + "--" * len(board))
    while True:
        printed = False
        s = " "
        x, y = " ", "  "
        b = [" "] * len(board)
        if i < len(stack):
            s = stack[i][0]
            x = str(stack[i][3][0])
            y = str(stack[i][3][1]).zfill(2)

            printed = True
        for bi in range(len(board)):
            if i < len(board[bi]):
                b[bi] = board[bi][i][0]
                printed = True

        print(f"{s} @ {x} {y} | " + " ".join(b))

        if not printed:
            break

        i += 1
    print("---------+-" + "--" * len(board))


def playbrute(board, stack):
    printstate(board, stack)

    while True:
        score, winstack, nextboard = bruteforce(board, stack)
        printstate(nextboard, winstack)
        print(f"@{score}\n")
        if nextboard == board:
            break
        board = nextboard
        stack = []


def getprogrec():
    callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_ulonglong, ctypes.c_ulonglong)
    buf = (ctypes.c_byte * 0x400)()

    pos = None

    def enumfunc(hwnd, param):
        user32.GetWindowTextW(hwnd, buf, len(buf) // 2)
        bbuf = bytes(buf)
        end = bbuf.find(b"\0\0")
        if (end & 1) == 1:
            end += 1
        title = bbuf[:end]
        stitle = str(title, "UTF_16_LE")
        if "Möbius Front '83" != stitle and 'The Zachtronics Solitaire Collection' != stitle:
            return True

        rect = (ctypes.c_long * 4)()
        user32.GetWindowRect(hwnd, rect)
        nonlocal pos
        pos = list(rect)
        return True

    user32.EnumWindows(callback(enumfunc), 0)

    if pos is None:
        print("Error, unable to find game coordinates")
        return None
    if min(pos) < 0:
        print("Target is offscreen")
        return None
    return pos


def getcardpos(rect, x, y):
    l, t, r, b = rect
    w = r - l
    h = b - t
    left = w * 0.439
    xstep = w * 0.142
    top = h * 0.1
    ystep = h * 0.0475

    xp = int(l + left + xstep * x)
    yp = int(t + top + ystep * y)

    return (xp, yp)


import PIL.ImageGrab
import PIL.Image
import pytesseract

tmppath = r"temp.png"


# This is less reliable than the memory method
# but still fun
def getboard_fromscreen():
    pos = getprogrec()
    if pos is None:
        return None
    print(pos)

    # screen cap
    screenshot = PIL.ImageGrab.grab(pos)
    w, h = screenshot.size

    xs = int(w * 0.011)
    ys = int(h * 0.024)

    okay = string.ascii_letters + string.digits
    board = []
    for xi in range(4):
        board.append([])
        for yi in range(13):
            w, h = screenshot.size
            x, y = getcardpos((0, 0, w, h), xi, yi)
            s = screenshot.crop((x - xs, y - ys, x + xs, y + ys))

            s = s.getchannel("G")

            s.save(tmppath)
            c = pytesseract.image_to_string(tmppath, config='--psm 10')
            c = ''.join([x for x in c if x in okay])
            c = c.lower()

            # print(c)
            board[xi].append(c)

    # translate failures and sanity check every card is there
    # try to translate common failures
    # if it has a 0, it is probably 10
    # if it is i, it is probably 7?
    missing = cards * 4
    fixed = []
    for xi in range(len(board)):
        for yi in range(len(board[xi])):
            c = board[xi][yi].upper()
            if len(c) > 1:
                if "10" in c:
                    c = "X"
                elif c.startswith("1") and c[1] in cards:
                    c = c[1]
                    fixed.append((xi, yi))
                else:
                    c = c[0]
                    fixed.append((xi, yi))
            else:
                if c == "1" or c == "i":
                    print(f"{c} @ {xi} {yi} is 7?")
                    c = "7"
                    fixed.append((xi, yi))
                if c == "0":
                    c = "Q"

            board[xi][yi] = c

            i = missing.find(c)
            if i == -1:
                # uh oh
                print(f"Too many {c}")
            else:
                missing = missing[:i] + missing[i + 1:]

    boarderr = False

    if len(set(missing)) > 1 or len(fixed) < len(missing):
        print(f"Too many missing cards: {missing}. Saw as:")
        boarderr = True
    elif len(fixed) == len(missing):
        for x, y in fixed:
            if board[x][y] != missing[0]:
                print(f"Misguessed {board[x][y]}? Resetting as {missing[0]}")
                board[x][y] = missing[0]
    elif len(missing) > 0:
        print(f"Too many missing cards: {missing}")
        boarderr = True

    if not boarderr:
        missing = cards * 4
        for xi in range(len(board)):
            for yi in range(len(board[xi])):
                c = board[xi][yi].upper()

                i = missing.find(c)
                if i == -1:
                    # uh oh
                    print(f"On check found too many {c}")
                    boarderr = True
                    break
                else:
                    missing = missing[:i] + missing[i + 1:]

        if len(missing) > 0:
            print(f"Missing on check {missing}")
            boarderr = True

    if boarderr:
        print("Got error for board seen as:")
        for yi in range(len(board[0])):
            out = ""
            for xi in range(len(board)):
                out += board[xi][yi] + " "
            print(out)
        return None

    realboard = []
    for xi in range(len(board)):
        realboard.append([])
        for yi in range(len(board[xi])):
            realboard[xi].append(getcard(board[xi][yi]))
    return realboard


dumpcardspath = "./dumpcards/bin/Release/netcoreapp3.1/dumpcards.exe"


def getboard_clrmd():
    p = subprocess.run([dumpcardspath], capture_output=True, encoding="ascii")
    if len(p.stdout) == 0:
        print("Error getting cards: \n" + p.stderr)
        return None
    b = []
    for x in range(4):
        b.append([])
        for y in range(13):
            b[x].append(None)

    for l in p.stdout.strip().split('\n'):
        ll = l.split()
        c = cards[int(ll[0]) - 1]
        card = getcard(c)
        x = int(ll[1])
        y = int(ll[2])
        b[x][y] = card

    for x in range(4):
        for y in range(13):
            if b[x][y] is None:
                print("Didn't get all the cards")
                return None
    return b


def clickat(xp, yp, sleepamt=0.42, midsleep=0.03):
    win32api.SetCursorPos((xp, yp))
    time.sleep(midsleep)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, xp, yp)
    time.sleep(midsleep)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, xp, yp)
    time.sleep(sleepamt)


def clicknextstack(rect):
    # could just click a bunch in the whole column?
    # could track last card we sent to stack, and go to it's location?
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = int(w * 0.317)
    n = 18
    start = 0.48
    end = 0.84
    step = (end - start) / n
    for i in range(n):
        clickat(rect[0] + x, rect[1] + int(h * (start + (step * i))), 0.01, 0.01)


def clicknextgame(rect):
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = int(w * 0.69)
    n = 3
    start = 0.69
    end = 0.81
    step = (end - start) / n
    for i in range(n):
        clickat(rect[0] + x, rect[1] + int(h * (start + (step * i))), 0.01, 0.01)


def playstack(stack, rect):
    # focus window
    return
    clickat(rect[0] + 6, rect[1] + 6)
    for c in stack:
        x, y = c[3]
        xp, yp = getcardpos(rect, x, y)
        print(f"DEBUG: trying to click {c[0]} at {x},{y} ({xp},{yp})")
        clickat(xp, yp)


def playone():
    rect = getprogrec()
    # if rect is None:
    #     print("Failed to get program bounds")
    #     return False
    # board = getboard_clrmd()
    board0 = [['7', '5', 'A', 'Q', 'J', '9', 'Q', '5', '7', '2', '3', 'Q', '9'],
             ['2', '2', 'K', '5', 'A', '2', '8', '8', 'K', 'X', 'K', 'J', 'X'],
             ['7', 'J', '5', 'X', 'A', 'A', 'K', '6', '8', '8', '4', 'J', '6'],
             ['X', '6', '4', '3', '9', '9', 'Q', '7', '3', '4', '6', '4', '3']]
    board = []
    for line0 in board0:
        line = []
        for x0 in line0:
            if x0 == 'A':
                x = ('A', 1, 1, (0, 0))
            elif x0 == '2':
                x = ('2', 2, 2, (0, 0))
            elif x0 == '3':
                x = ('3', 3, 3, (0, 0))
            elif x0 == '4':
                x = ('4', 4, 4, (0, 0))
            elif x0 == '5':
                x = ('5', 5, 5, (0, 0))
            elif x0 == '6':
                x = ('6', 6, 6, (0, 0))
            elif x0 == '7':
                x = ('7', 7, 7, (0, 0))
            elif x0 == '8':
                x = ('8', 8, 8, (0, 0))
            elif x0 == '9':
                x = ('9', 9, 9, (0, 0))
            elif x0 == 'X':
                x = ('X', 10, 10, (0, 0))
            elif x0 == 'J':
                x = ('J', 10, 11, (0, 0))
            elif x0 == 'Q':
                x = ('Q', 10, 12, (0, 0))
            elif x0 == 'K':
                x = ('K', 10, 13, (0, 0))
            else:
                x = ('K', 10, 13, (0, 0))
            line.append(x)
        board.append(line)

    if board is None:
        print("Failed while getting board")
        return False
    stack = []
    printstate(board, stack)

    while True:
        print("DEBUG starting solve")
        _, winstack, nextboard = bruteforce2(board, stack, scoresofar=0, stacksleft=1)
        # _, winstack, nextboard = bruteforce(board, stack)
        print("DEBUG decided on moves")
        if nextboard == board:
            break
        printstate(nextboard, winstack)
        playstack(winstack, rect)
        clicknextstack(rect)
        board = nextboard
        stack = []
    return True


def playx(x=5):
    rect = getprogrec()
    for i in range(x):
        if not playone():
            return False
        else:
            clicknextgame(rect)
    return True


def main():
    playone()


if __name__ == "__main__":
    main()

'''
不够好
https://github.com/svajoklis-1/mobius-front-solitaire-solver
Deal #0001
---------+---------
  @      | 7 2 7 X
  @      | 5 2 J 6
  @      | A K 5 4
  @      | Q 5 X 3
  @      | J A A 9
  @      | 9 2 A 9
  @      | Q 8 K Q
  @      | 5 8 6 7
  @      | 7 K 8 3
  @      | 2 X 8 4
  @      | 3 K 4 6
  @      | Q J J 4
  @      | 9 X 6 3
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG: At depth 12
DEBUG: At depth 13
DEBUG decided on moves
---------+---------
9 @ 0 12 | 7 2 7 X
Q @ 0 11 | 5 2 J 6
3 @ 3 12 | A K 5 4
3 @ 0 10 | Q 5 X 3
4 @ 3 11 | J A A 9
2 @ 0 09 | 9 2 A 9
  @      | Q 8 K Q
  @      | 5 8 6 7
  @      | 7 K 8 3
  @      |   X 8 4
  @      |   K 4 6
  @      |   J J  
  @      |   X 6  
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG decided on moves
---------+---------
6 @ 2 12 | 7 2 7 X
6 @ 3 10 | 5 2 J 6
4 @ 3 09 | A K 5 4
7 @ 0 08 | Q 5 X 3
3 @ 3 08 | J A A 9
5 @ 0 07 | 9 2 A 9
  @      | Q 8 K Q
  @      |   8 6 7
  @      |   K 8  
  @      |   X 8  
  @      |   K 4  
  @      |   J J  
  @      |   X    
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG decided on moves
---------+---------
J @ 2 11 | 7 2 7 X
X @ 1 12 | 5 2 J 6
4 @ 2 10 | A K 5 4
7 @ 3 07 | Q 5 X 3
  @      | J A A 9
  @      | 9 2 A 9
  @      | Q 8 K Q
  @      |   8 6  
  @      |   K 8  
  @      |   X 8  
  @      |   K    
  @      |   J    
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG decided on moves
---------+---------
J @ 1 11 | 7 2 7 X
Q @ 0 06 | 5 2 J 6
Q @ 3 06 | A K 5 4
  @      | Q 5 X 3
  @      | J A A 9
  @      | 9 2 A 9
  @      |   8 K  
  @      |   8 6  
  @      |   K 8  
  @      |   X 8  
  @      |   K    
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG decided on moves
---------+---------
9 @ 0 05 | 7 2 7 X
9 @ 3 05 | 5 2 J 6
9 @ 3 04 | A K 5 4
3 @ 3 03 | Q 5 X  
  @      | J A A  
  @      |   2 A  
  @      |   8 K  
  @      |   8 6  
  @      |   K 8  
  @      |   X 8  
  @      |   K    
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG decided on moves
---------+---------
J @ 0 04 | 7 2 7 X
K @ 1 10 | 5 2 J 6
Q @ 0 03 |   K 5 4
A @ 0 02 |   5 X  
  @      |   A A  
  @      |   2 A  
  @      |   8 K  
  @      |   8 6  
  @      |   K 8  
  @      |   X 8  
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG decided on moves
---------+---------
X @ 1 09 | 7 2 7 X
5 @ 0 01 |   2 J 6
K @ 1 08 |   K 5  
4 @ 3 02 |   5 X  
  @      |   A A  
  @      |   2 A  
  @      |   8 K  
  @      |   8 6  
  @      |     8  
  @      |     8  
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG: At depth 12
DEBUG decided on moves
---------+---------
7 @ 0 00 |   2 7 X
8 @ 2 09 |   2 J 6
8 @ 2 08 |   K 5  
8 @ 1 07 |   5 X  
  @      |   A A  
  @      |   2 A  
  @      |   8 K  
  @      |     6  
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG: At depth 11
DEBUG: At depth 12
DEBUG: At depth 13
DEBUG decided on moves
---------+---------
6 @ 2 07 |   2 7 X
8 @ 1 06 |   2 J 6
K @ 2 06 |   K 5  
2 @ 1 05 |   5 X  
A @ 2 05 |        
A @ 1 04 |        
A @ 2 04 |        
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG: At depth 8
DEBUG: At depth 9
DEBUG: At depth 10
DEBUG decided on moves
---------+---------
X @ 2 03 |   2 7 X
5 @ 1 03 |   2 J  
5 @ 2 02 |   K    
6 @ 3 01 |        
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG: At depth 3
DEBUG: At depth 4
DEBUG: At depth 5
DEBUG: At depth 6
DEBUG: At depth 7
DEBUG decided on moves
---------+---------
J @ 2 01 |       X
K @ 1 02 |        
2 @ 1 01 |        
2 @ 1 00 |        
7 @ 2 00 |        
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG: At depth 2
DEBUG decided on moves
---------+---------
X @ 3 00 |        
  @      |        
---------+---------
DEBUG starting solve
DEBUG: At depth 1
DEBUG decided on moves
'''