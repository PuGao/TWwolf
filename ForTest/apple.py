# -*- coding: utf-8 -*-
import os
import dotenv
dotenv.load_dotenv()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
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

##### google API #####
import sys
import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials as SAC
##### google API #####

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

    # print(body)

    try:
        handler.handle(body, signature)
     
    except InvalidSignatureError:
        abort(400)
    return 'OK'
#########################################################
import time
def first_part(user_input):
    #第一步先進去搜尋結果的頁面抓出兩頁的所有標題跟連結
    title=[]
    title_keyword=[]

    browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
    browser.get("https://www.ltn.com.tw/")
    search_btn = browser.find_element_by_css_selector("a[class*='iconSearch']").click()
    time.sleep(1)
    keyword = browser.find_element_by_css_selector("div[class='ltnsch_show boxTitle boxText'] input[id='cacheSearch']")
    # keyword = browser.find_element_by_id("qs")
    keyword.send_keys(user_input)
    keyword.send_keys(Keys.RETURN)
    print(browser.current_url)#這個列出來的是搜尋結果的網址
    url = requests.get(browser.current_url)
    time.sleep(1)
    nextpage_btn=browser.find_element_by_class_name("p_next")
    nextpage_btn.click()
    time.sleep(1)
    print(browser.current_url)#第二頁搜尋結果的網址
    url2=requests.get(browser.current_url)
    browser.quit()

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
    # choice=""
    finallist=jieba.analyse.extract_tags(new_key,topK=7, withWeight=False, allowPOS=('ng','nr','nrfg','nrt','ns','nt'))    
    for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
        print(finallist[i])#印出三組供使用者選的關鍵字
    return finallist[3:6]
    #     choice+=finallist[i]
    #     choice+="\n"
    # choice+=finallist[5]
 
    # try:
    #     for i in range(3,6):
    #         print(finallist[i])
    # except:
    #     for i in range(0,len(finallist)):
    #         print(finallist[i])
    #     n=3-len(finallist[i])
    #     if n >0:
    #         for i in (0,n):
    #             print(jieba.analyse.extract_tags(new_key,topK=7, withWeight=False)[i])
    #     if n==0:
    #         print(jieba.analyse.extract_tags(new_key,topK=7, withWeight=False)[0])

def second_part(user_input,msg_choose):
    #這邊隨便抓一個關鍵字做測試 之後是根據使用者選的 加上使用者一開始的關鍵字 兩個東西下去搜尋  
    title=[]
    
    browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
    browser.get("https://www.ltn.com.tw/")    
    search_btn = browser.find_element_by_css_selector("a[class*='iconSearch']").click()
    time.sleep(1)
    keyword = browser.find_element_by_css_selector("div[class='ltnsch_show boxTitle boxText'] input[id='cacheSearch']")
    # keyword = browser.find_element_by_id("qs")
    keyword.send_keys(user_input+" "+msg_choose)
    keyword.send_keys(Keys.RETURN)
    # for i in range(0,len(finallist)):
    #     print(finallist[i])
    # print(browser.current_url)
    url_final = requests.get(browser.current_url)
    soup_final = BeautifulSoup(url_final.text, 'html.parser')
    temp_final=soup_final.find('a', class_='tit')
    title.append(temp_final.text)
    temp_ltn_link=temp_final.get('href')
    print("自由時報ltn:")
    print(temp_final.text+":"+temp_ltn_link)
    browser.quit()
    return temp_ltn_link

def third_part(user_input,msg_choose):
    #處理完自由時報並取得關鍵字後進入聯合報搜尋
    browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
    browser.get('https://udn.com/mobile/index')
    browser.maximize_window()
    js = "document.getElementById('searchbox').style.display='block'" #编写JS语句
    browser.execute_script(js) #执行JS
    # keyword = browser.find_element_by_css_selector('a[class*="toprow_search sp"]').click()
    search_btn = browser.find_element_by_class_name("search_kw")
    search_btn.send_keys(user_input+" "+msg_choose)
    search_btn.submit()
    keyword=browser.find_element_by_class_name("search_submit")
    keyword.click()
    # print(browser.current_url)
    url = requests.get(browser.current_url)
    soup = BeautifulSoup(url.text, 'html.parser')
    print("網站內容")
    #print(soup.prettify())
    temp=soup.find('div',{'id':'search_content'}).find('dt')
    temp_udn_link=temp.find('a').get('href')
    print("聯合報udn:")
    print(temp.find('h2').text+':'+temp_udn_link)
    browser.quit()
    return temp_udn_link

def fourth_part(udn_link, ltn_link):
    #這個cell是給定三個網址後輸出三篇新聞整理後的摘要
    import requests
    # import codecs
    # from textrank4zh import TextRank4Keyword, TextRank4Sentence
    # from snownlp import SnowNLP
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.summarizers.luhn import LuhnSummarizer
    import re
    #jieba.set_dictionary(r'C:\Users\ASUS\Desktop\dict.txt.big.txt')
    ubn_article=""
    ltn_article=""
    china_article=""
    ubn_url = requests.get(udn_link)
    ltn_url = requests.get(ltn_link)
    #china_url=requests.get('https://www.chinatimes.com/newspapers/20191128000208-260301?chdtv')
    ubn_soup = BeautifulSoup(ubn_url.text, 'html.parser')
    ltn_soup = BeautifulSoup(ltn_url.text, 'html.parser')
    #china_soup= BeautifulSoup(china_url.text, 'html.parser')
    #先處理ubn
    for temp in ubn_soup.find_all('p'):
        #print(temp.text)
        ubn_article+=temp.text
    print("UDN：")
    print(ubn_article)
    # words=jieba.posseg.lcut(ubn_article)
    #for word in words:
        #print(word)
    #print(jieba.analyse.extract_tags(ubn_article,topK=20, withWeight=False, allowPOS=('x')))

    #先處理ltn
    for temp in ltn_soup.find_all('p'):
        #print(temp.text)
        ltn_article+=temp.text
    print("LTN：")
    print(ltn_article)
    # words=jieba.posseg.lcut(ltn_article)
    #for word in words:
        #print(word)
    #print(jieba.analyse.extract_tags(ltn_article,topK=20, withWeight=False, allowPOS=('x')))

    '''
    #處理中時
    for temp in china_soup.find_all('p'):
        #print(temp.text)
        china_article+=temp.text
    print("CHINA：")
    print(china_article)
    words=jieba.posseg.lcut(china_article)
    '''
    #for word in words:
        #print(word)
    #print(jieba.analyse.extract_tags(china_article,topK=20, withWeight=False, allowPOS=('x')))

    # 這邊開始做摘要
    # text = ubn_article+ltn_article+china_article
    # text = codecs.open('../test/doc/01.txt', 'r', 'utf-8').read()
    # text = ubn_article+ltn_article#還沒抓中時 先測聯合跟自由
    
    # tr4w = TextRank4Keyword()
    # tr4w.analyze(text=text, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象


    # tr4s = TextRank4Sentence()
    # tr4s.analyze(text=text, lower=True, source = 'all_filters')
    # print()
    # print( '摘要：' )
    # abstract=""
    # for item in tr4s.get_key_sentences(num=3):
    #     # print(item.sentence)
    #     abstract+=item.sentence
    #     #print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
    #     print(abstract)
    # print(item.sentence)
    article=ubn_article+ltn_article
    parser = PlaintextParser.from_string(article, Tokenizer("chinese"))
    summarizer = LsaSummarizer()
    print("----摘要結果Lsa----\n")
    abstract="" #[]
    for sentence in summarizer(parser.document, 2):
        abstract+=str(sentence)
        # print(sentence_2)
    # abstract=re.sub(r"\s+","", abstract)
    # abstract="".join(map(str, abstract))
    print(abstract)
    return abstract


# @handler.add(MessageEvent, message=TextMessage)
# def printit(event1):
#     import threading
#     threading.Timer(5.0, printit(event1)).start()
#     return line_bot_api.reply_message(event1.reply_token,TextSendMessage(text=profile.display_name+"啾都媽爹幾類"))



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_msg_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    import re
    content=event.message.text
    # tStart=time.time()
    # if time.time()-tStart > 10:
    #     line_bot_api.push_message(
    #         event.source.user_id, [
    #                 TextSendMessage(text=profile.display_name+"啾都媽爹幾類")
    #         ]
    #     )
    if content[0:2] == "熱搜":#觸發條件
        tStart = time.time()
        global user_input
        user_input=content[2:10] #剩餘關鍵字,ex:熱搜 韓國瑜
        user_input=re.sub(r"\s+","", user_input)#去除[2:10]之空白格
        global msg
        msg=list(first_part(user_input))
        tEnd = time.time()
        delta_t=str(round(tEnd-tStart, 2))
        print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='相關の關鍵字如下:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="我花了"+delta_t+"秒", text="我花了"+delta_t+"秒")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=msg[0], text=msg[0])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=msg[1], text=msg[1])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=msg[2], text=msg[2])
                        ),
                    ]
                )
            )
        )            
    ####  第二層total-0 ####
    if content == msg[0]:
        tStart = time.time()
        msg_choose=msg[0]
        ltn_link=second_part(user_input,msg_choose) #ltn_link
        udn_link=third_part(user_input,msg_choose) #udn_link
        #abstract=fourth_part(ltn_link,udn_link) #abstract
        tEnd = time.time()
        delta_t=str(round(tEnd-tStart, 2))
        print('time elapsed: ' + delta_t + ' seconds')

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="聯合報udn:\n"+udn_link+"\n自由時報ltn:\n"+ltn_link))

    ####  第二層total-1 ####
    if content == msg[1]:
        tStart = time.time()
        msg_choose=msg[1]
        ltn_link=second_part(user_input,msg_choose) #ltn_link
        udn_link=third_part(user_input,msg_choose) #udn_link
        #abstract=fourth_part(ltn_link,udn_link) #abstract
        tEnd = time.time()
        delta_t=str(round(tEnd-tStart, 2))
        print('time elapsed: ' + delta_t + ' seconds')

        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                #text="摘要:\n"+abstract
                text="87878"
            )
        ])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='🙂🙃'+'說點有意義的話好嗎'+'🙃🙂'))

'''
googlesheet
    # msg = event.message.text
    # if msg != "":
    #     #GDriveJSON就輸入下載下來Json檔名稱
    #     #GSpreadSheet是google試算表名稱
    #     GDriveJSON = 'MyBot-5894d9f87218.json'
    #     GSpreadSheet = 'final-news'
    #     GSpreadSheet_ID="5894d9f87218e4a8e9f64102290c2265b4334fa6"
    #     try:
    #         scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    #         key = SAC.from_json_keyfile_name(GDriveJSON, scope)
    #         gc = gspread.authorize(key)
    #         sh = gc.open(GSpreadSheet)
    #         worksheet = sh.sheet1
    #     except Exception as ex:
    #         print('無法連線Google試算表', ex)
    #         sys.exit(1)
    #     list_of_lists = worksheet.get_all_values()
    #     list_of_lists_2=list(map(list, zip(*list_of_lists)))
        
    #     # matching = [s for s in list_of_lists_2[0] if msg in s]
    #     # print(s)    

    #     for positions, items in enumerate(list_of_lists_2[0]):
    #         if items == msg:
    #             # print(positions)
    #             print(list_of_lists_2[1][positions])
    #     line_bot_api.reply_message(event.reply_token,[TextSendMessage(text='記錄成功'),])
        
        可用:
        # for item in list_of_lists_2[0]:
        #     if item.find(msg) != -1:
        #         print(item)


        # values_col_list = worksheet.col_values(1)
        # cell = values_col_list[0].items()
        # print(list_of_lists_2[0])
        # list_of_cells = sheet.findall(msg)
        # for cell in list_of_cells:
        #     cell.value= msg
        # result = cell.iter_rows(msg).get(spreadsheetId=GSpreadSheet_ID,range=GSpreadSheet).execute()
        # values = result.get('values', [])

        # if not values:
        #     print('No data found.')
        # else:
        #     print('Name, Major:')
        #     for row in values:
        #         # Print columns A and E, which correspond to indices 0 and 4.
        #         print('%s, %s' % (row[0], row[4]))
        # textt="我叫做"+msg
        # sheet.append_row(('hi', textt,'8+9'))
        # print('新增一列資料到試算表' ,GSpreadSheet)
        # list_of_cells= sheet.findall(msg)
        # for cell in list_of_cells:
        #    cell.value=msg
        # print(sheet.acell(msg).value)
        # print(wks_list)
        


        # print('新增一列資料到試算表' ,GSpreadSheet)
        # print(sheet.get_all_records())
        # sheet.append_row(['4','this is not a book.'])
        # list_of_cells = sheet.findall('banggg')
        # for cell in list_of_cells:
        #     cell.value= 'banggg'
        # sheet.update_cells(list_of_cells)
'''


####################### 執行 Flask ######################
if __name__ == "__main__":
    app.run(debug=True)