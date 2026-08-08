import pyautogui as au
import ollama as ai
from time import sleep
import pyperclip
import cv2
from skimage.metrics import structural_similarity as ssim
import os
import random as rn
from emoji import replace_emoji

airate, chatcount = 0, 0
MAX_HISTORY_ROUNDS = 4
conversation_history = []
models = {'lite':'qwen2:0.5b', 'normal':'llama3.2:3b', 'pro':'gemma3:4b'}
thinking = []
aimodel = models['normal']
POSITION = {
    'chatreg':(430, 400, 1000, 440),
    'usermsg':{'x':484, 'y':733},
    'msginput':{'x':825, 'y':860},
    'retrybtn':{'x':800, 'y':800},
    'timeoutbtn':{'x':825, 'y':755},
    'setai':{'x':1360, 'y':965},
    'seth':{'x':1180, 'y':965},
    'confirm':{'x':1330, 'y':880},
    'timeoutreg':(1340, 300, 100, 10)
}
PERSONAS = [
    "一个冷漠的人", "一个幽默的人",
    "一个愚蠢的人", "一只猫娘",
    "一个说话可爱的人", "一个高傲的人"
    ]
persona = rn.choice(PERSONAS)
lockpersona = False
suff = f"在接下来的对话中，你需要假装成{persona}，"
SYSMSG = """
但不要让对方察觉你是AI。
尽量用简短的信息交流，
你可以使用"/n"将消息分成几次发送。
"""
def graptxt():
    global POSITION
    au.tripleClick(x=POSITION['usermsg']['x'], y=POSITION['usermsg']['y'])
    sleep(0.1)
    au.hotkey('ctrl', 'c')
    text = pyperclip.paste()
    return text

def compimg(img):
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
    global aimodel, SYSMSG, conversation_history, MAX_HISTORY_ROUNDS, suff, thinking
    conversation_history.append({'role': 'user', 'content': prompt})
    max_messages = 2 * MAX_HISTORY_ROUNDS
    if len(conversation_history) > max_messages:
        conversation_history = conversation_history[-max_messages:]
    messages = [{'role': 'system', 'content': suff + SYSMSG}] + conversation_history
    response = ai.chat(model=aimodel, messages=messages, think=(aimodel in thinking))
    content = response['message']['content']
    content = replace_emoji(content, replace="")
    if len(content) > 25:
        sim = simpfy(content)
        conversation_history.append({'role': 'assistant', 'content': sim})
    else:
        conversation_history.append({'role': 'assistant', 'content': content})
    return content

def sendmsg(msg):
    global POSITION
    pyperclip.copy(msg)
    au.click(x=POSITION['msginput']['x'], y=POSITION['msginput']['y'])
    sleep(0.2)
    au.hotkey("ctrl", "v")
    sleep(0.3)
    au.press('enter')

def lockchoice(choice):
    global POSITION
    if choice == 'ai':
        au.click(x=POSITION['setai']['x'], y=POSITION['setai']['y'])
    else:
        au.click(x=POSITION['seth']['x'], y=POSITION['seth']['y'])
    sleep(1)
    au.click(x=POSITION['confirm']['x'], y=POSITION['confirm']['y'])

def dorefresh():
    global POSITION
    img = au.screenshot(region=POSITION['chatreg'])
    img.save("img2.png")
    img1 = cv2.imread('img.png', cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread('img2.png', cv2.IMREAD_GRAYSCALE)
    score, diff = ssim(img1, img2, full=True)
    if score > 0.97:
        return False
    elif 0.75 < score < 0.97:
        img = au.screenshot(region=POSITION['chatreg'])
        img.save("img.png")
        return 'chatrefresh'
    elif 0.3 < score < 0.75:
        img = au.screenshot(region=POSITION['chatreg'])
        img.save("img.png")
        return 'pagerefresh'
    else:
        img = au.screenshot(region=POSITION['chatreg'])
        img.save("img.png")
        return 'browserrefresh'

def retry():
    global POSITION, persona, PERSONAS, suff, lockpersona
    while True:
        img = au.screenshot(region=POSITION['chatreg'])
        img.save("img.png")
        img = cv2.imread('img.png', cv2.IMREAD_GRAYSCALE)
        res = compimg(img)
        if res == 'retry':
            au.click(x=POSITION['retrybtn']['x'], y=POSITION['retrybtn']['y'])
        elif res == 'timeout':
            au.click(x=POSITION['timeoutbtn']['x'], y=POSITION['timeoutbtn']['y'])
        elif res == 'chat':
            sleep(0.5)
            if not lockpersona:
                persona = rn.choice(PERSONAS)
                suff = f"在接下来的对话中，你需要假装成{persona}，"
            greet()
            return
        else:
            sleep(0.05)

def greet():
    global POSITION, conversation_history, persona
    sleep(1)
    sendmsg(rn.choice(['嗨', '嗯', '哈喽', '早上好', '下午好', '晚上好', '刚连上', '纯路人', '终于匹配到了']))
    sendmsg("你好")
    sleep(0.5)
    img = au.screenshot(region=POSITION['chatreg'])
    img.save("img.png")
    while not dorefresh(): sleep(0.1)
    conversation_history = []
    print(persona)

def startup():
        global models, aimodel
        print('Start up')
        ai.generate(model=models['lite'], prompt='hi')
        ai.generate(model=aimodel, prompt='hi')

def restart():
    os.system('start "" "autochat.py"')
    exit()

def detect():
    global models, airate, chatcount, POSITION
    cap = au.screenshot(region=POSITION['timeoutreg'])
    cap.save("cap.png")
    istout = cv2.imread("cap.png", cv2.IMREAD_GRAYSCALE)
    refimg = cv2.imread("timeout.png", cv2.IMREAD_GRAYSCALE)
    score, diff = ssim(istout, refimg, full=True)
    if score > 0.98:
        res = airate/chatcount
        if res > 0.4:
            lockchoice("ai")
        else:
            lockchoice("h")
        print(res)
        sleep(5)
        retry()
        return True
    else:
        return False

def determine(txt):
    global airate, chatcount
    AIMSG = [
            "哼", "喵", "哈哈", "您", 
            "刚连上", "匹配", "纯路人", 
            "（", "）", "！", "。",
            "zdjd", "kskbl"
    ]
    if txt in AIMSG:
        airate += 1
    chatcount += 1

def simpfy(txt):
    global models
    if mode == 'text':
        sim = ai.generate(
            model=models['lite'],
            prompt=f"简化为20个字以下：{txt}"
        )
        return sim['response']

def main():
    global chatcount, POSITION
    while True:
        ref,det = False,False
        text = graptxt()
        if not ("举报" in text):
            print(text)
            determine(text)
            if len(text) > 25:
                text = simpfy(text)
            text = callai(text)
            print(text)
            if "/n" in text:
                txtlis = text.split("/n")
                for msg in txtlis:
                    sendmsg(msg.replace("/", ""))
            else:
                sendmsg(text.replace("/", ""))
            sleep(0.4)
        img = au.screenshot(region=POSITION['chatreg'])
        img.save("img.png")
        while not (ref or det):
            ref = dorefresh()
            det = detect()
            sleep(0.2)
        if ref == 'chatrefresh':
            continue
        elif ref == 'browserrefresh':
            print('Browser refreshed')
            if input('> ') == 'restart':
                restart()
            else:
                break

startup()
mode = input("Start> ")
if mode == "test":
    while True:
        try: exec('print(' + input(">> ") + ')')
        except Exception as e: print(e)
elif mode == "config":
    edit = '_'
    while edit != 'start':
        print("""=====Config=====
1.Lock persona
2.Persona(use)
3.Model
4.Max memory
5.Add/Remove Persona
""")
        edit = input("Edit: ")
        if edit == '1':
                    print(lockpersona)
                    print(persona)
                    lockpersona = bool(input('(True/False)New: '))
        elif edit == '2':
            print(persona)
            persona = input('New: ')
        elif edit == '3':
            print(models)
            aimodel = models[input('Use: ')]
            print('Start up model')
            ai.generate(model=aimodel, prompt='hi')
        elif edit == '4':
            print(MAX_HISTORY_ROUNDS)
            MAX_HISTORY_ROUNDS = int(input('(Round)New: '))
        elif edit == '5':
            print(PERSONAS)
            act = input("Add/Remove (a/b): ")
            if act == "a":
                PERSONAS += (input("Add: ")).split(' ')
            elif act == "b":
                PERSONAS = list(set(PERSONAS) - set(input("Remove: ").split(' ')))
        os.system('cls')
    greet()
    main()
else:
    greet()
    main()
