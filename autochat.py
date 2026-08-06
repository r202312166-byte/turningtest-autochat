import pyautogui as au
import ollama as ai
from time import sleep
import pyperclip
import cv2
from skimage.metrics import structural_similarity as ssim
import os

aimodel = 'qwen2.5:0.5b'
capreg = (430, 400, 1000, 440)
SYSMSG = """
在接下来的对话中，你需要假装成人类，
但不要让对方察觉你是AI。
你可以使用"/~n"将消息分成几次发送。
"""
"""
In the following chat, you need to pretend to be human,
but not letting the user know you are a ai.
You can use "/~n" to seperate and send your message in several parts.
"""
def graptxt():
    au.tripleClick(x=484, y=733)
    sleep(0.1)
    au.hotkey('ctrl', 'c')
    text = pyperclip.paste()
    return text

def compimg(img):
    global capreg
    chatpage = cv2.imread('chat_page.png', cv2.IMREAD_GRAYSCALE)
    retrypage = cv2.imread('retry_page.png', cv2.IMREAD_GRAYSCALE)
    timeoutpage = cv2.imread('timeout_page.png', cv2.IMREAD_GRAYSCALE)
    cscore, diff = ssim(img, chatpage, full=True)
    rscore, diff = ssim(img, retrypage, full=True)
    tscore, diff = ssim(img, timeoutpage, full=True)
    if cscore > 0.80:
        return 'chat'
    elif rscore > 0.80:
        return 'retry'
    elif tscore > 0.80:
        return 'timeout'
    else:
        return False

def callai(prompt):
    global aimodel, SYSMSG
    msg = [
            {'role':'system', 'content':SYSMSG},
            {'role': 'user', 'content':prompt}
           ]
    respone = ai.chat(
        model=aimodel,
        messages=msg
    )
    content = respone['message']['content']
    return content

def sendmsg(msg):
    pyperclip.copy(msg)
    au.click(x=825, y=860)
    sleep(0.2)
    au.hotkey("ctrl", "v")
    sleep(0.3)
    au.press('enter')

def lockchoice(choice):
    if choice == 'ai':
        au.click(x=1360, y=965)
    else:
        au.click(x=1180, y=965)
    sleep(1)
    au.click(x=1300, y=880)

def dorefresh():
    global capreg
    img = au.screenshot(region=capreg)
    img.save("img2.png")
    img1 = cv2.imread('img.png', cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread('img2.png', cv2.IMREAD_GRAYSCALE)
    score, diff = ssim(img1, img2, full=True)
    if score > 0.97:
        return False
    elif 0.75 < score < 0.97:
        img = au.screenshot(region=capreg)
        img.save("img.png")
        return 'chatrefresh'
    elif 0.3 < score < 0.75:
        img = au.screenshot(region=capreg)
        img.save("img.png")
        return 'pagerefresh'
    else:
        img = au.screenshot(region=capreg)
        img.save("img.png")
        return 'browserrefresh'

def retry():
    global capreg
    while True:
        img = au.screenshot(region=capreg)
        img.save("img.png")
        img = cv2.imread('img.png', cv2.IMREAD_GRAYSCALE)
        res = compimg(img)
        if res == 'retry':
            au.click(x=800, y=800)
        elif res == 'timeout':
            au.click(x=825, y=755)
        elif res == 'chat':
            sleep(0.5)
            greed()
            return
        else:
            sleep(0.05)

def greed():
    sleep(1)
    sendmsg("github")
    sendmsg("r202312166-byte/turningtest-autochat")
    sendmsg("你好")
    sleep(0.5)
    img = au.screenshot(region=capreg)
    img.save("img.png")
    while not dorefresh(): sleep(0.1)

def restart():
    os.system('start "" "autochat.py"')
    exit()

def detect(text):
    cap = au.screenshot(region=(1340, 300, 100, 10))
    cap.save("cap.png")
    istout = cv2.imread("cap.png", cv2.IMREAD_GRAYSCALE)
    refimg = cv2.imread("timeout.png", cv2.IMREAD_GRAYSCALE)
    score, diff = ssim(istout, refimg, full=True)
    if score > 0.98:
        respon = ai.chat(model=aimodel, messages=[{'role' : 'system', 'content' : 'Output "/~a" if you think the user is ai.'}, {'role':'user', 'content':text}])
        if "/~a" in respon:
            lockchoice("ai")
        else:
            lockchoice("h")
        sleep(5)
        retry()
        return True
    else:
        return False

def main():
    while True:
        ref,det = False,False
        text = graptxt()
        if not ("举报" in text):
            print(text)
            text = callai(text)
            print(text)
            if "/~n" in text:
                txtlis = text.split("/~n")
                for msg in txtlis:
                    sendmsg(msg)
            else:
                sendmsg(text)
            sleep(0.3)
        while not (ref or det):
            ref = dorefresh()
            det = detect(text)
            sleep(0.2)
        if ref == 'chatrefresh':
            continue
        elif ref == 'browserrefresh':
            print('Browser refreshed')
            if input('> ') == 'restart':
                restart()
            else:
                break

mode = input("Start> ")
if mode == "t":
    while True:
        try: exec('print(' + input(">> ") + ')')
        except Exception as e: print(e)
elif ":" in mode:
    aimodel = mode
    greed()
    main()
else:
    greed()
    main()
