import os
import dotenv
dotenv.load_dotenv()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
)

#這邊是我要用到的所有import
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
import jieba,os,jieba.analyse,requests,time
import jieba.posseg as pseg
# from gensim import corpora,models,similarities


line_bot_api = LineBotApi(os.getenv('LINE_BOT_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_BOT_SECRET'))

###################### 初始化 Flask #####################
from flask import Flask, request, abort

app = Flask(__name__)
############### 初始化 Callback Endpoint ################
@app.route("/", methods=['POST'])
def callback():
    # if request.method == "POST":
    #     update = .Update.de_json(request.get_json(force=True), bot)
    #     dispatcher.process_update(update)
    # return 'ok'

    # 這一段可以不需要理解，這是 Line 官方在 Line Bot Python SDK 使用說明裡
    # 提供的程式碼：https://github.com/line/line-bot-sdk-python

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
     
    except InvalidSignatureError:
        abort(400)
    return 'OK'
#########################################################
import time
def first_ltn(inputstr):
    #第一步先進去搜尋結果的頁面抓出兩頁的所有標題跟連結
    title=[]
    title_keyword=[]

    browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
    browser.get("https://www.ltn.com.tw/")
    # WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='title login_title' and text()='Login']//following::div[1]//input[@class='text header_login_text_box ignore_interaction']"))).send_keys("someemail@email.com")
    search_btn = browser.find_element_by_css_selector("a[class*='iconSearch']").click()
    time.sleep(1)
    keyword = browser.find_element_by_css_selector("div[class='ltnsch_show boxTitle boxText'] input[id='cacheSearch']")
    # keyword = browser.find_element_by_id("qs")
    keyword.send_keys(inputstr)
    keyword.send_keys(Keys.RETURN)
    print(browser.current_url)#這個列出來的是搜尋結果的網址
    url = requests.get(browser.current_url)
    
    nextpage_btn=browser.find_element_by_class_name("p_next")
    nextpage_btn.click()
    time.sleep(3)
    print(browser.current_url)#第二頁搜尋結果的網址
    url2=requests.get(browser.current_url)


    #解析網站抓出標題
    soup = BeautifulSoup(url.text, 'html.parser')
    soup2 = BeautifulSoup(url2.text, 'html.parser')
    #print("網站內容")
    #print(soup.prettify())
    for temp in soup.find_all('a', class_='tit'):
        title.append(temp.text)
        #temp_url=temp.get('href')
        #print(temp.text+"："+temp_url)
    for temp in soup2.find_all('a', class_='tit'):
        title.append(temp.text)
        #temp_url=temp.get('href')
        #print(temp.text+"："+temp_url)
        
    #print(title)

    #這邊開始分析標題，將每個標題都抓出一個關鍵字
    total=[]
    for elements in title:
        words = jieba.cut(elements, cut_all=False)
        title_keyword.append(jieba.analyse.extract_tags(elements,topK=1, withWeight=False)[0])
        #print(jieba.analyse.extract_tags(elements,topK=1, withWeight=False))
        '''
        for word in words:
            #print (word)
            total.append(word)
        '''
    new_key_list = list(set(title_keyword))#利用集合刪掉重複的關鍵字
    print(new_key_list)#列出整理後的關鍵字

    #下面是因為結巴的語法問題，所以要將剛剛找出的所有關鍵字重組成一個字串
    new_key=""
    for element in new_key_list:
        new_key+=element
        new_key+="，"
    words =pseg.cut(new_key)#然做同樣的事，先切割字串
    '''
    for w in words:
        print(w)
    '''
    print("關鍵字：")#再抓出關鍵字
    choice=""
    finallist=jieba.analyse.extract_tags(new_key,topK=7, withWeight=False, allowPOS=('ng','nr','nrfg','nrt','ns','nt'))
    for i in range(3,5):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
        print(finallist[i])#印出三組供使用者選的關鍵字
        choice+=finallist[i]
        choice+="\n"
    choice+=finallist[5]
    return choice

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text[0:2] == "熱搜":#觸發條件
        inputstr=event.message.text[2:10]
        msg=first_ltn(inputstr)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='搜尋結果為：\n'+msg)
        )

'''
    if event.message.text == "A":
        msg = "狗"
    elif event.message.text == "B":
        msg = "貓"
    elif event.message.text == "C":
        msg = "獅子"
    elif event.message.text == "C0":
        msg = "幹林老師"
    elif event.message.text == "福利熊":
        msg = "我比較喜歡頂好la~"
    elif event.message.text == "VVN":
        msg = "幹老師"
    else:
        msg = "吼～～～\n"+event.message.text+"尼77777777"
    message = TextSendMessage(text=msg)
    line_bot_api.reply_message(event.reply_token, message)
'''

####################### 執行 Flask ######################
if __name__ == "__main__":
    app.run(debug=True)