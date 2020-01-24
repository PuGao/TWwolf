# -*- coding: utf-8 -*-


#這個是目前的終板 114




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
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction ,TemplateSendMessage,
    ButtonsTemplate ,MessageTemplateAction
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
jieba.set_dictionary('/Users/apple/Desktop/dict.txt.big.txt')
jieba.set_dictionary('/Users/apple/Desktop/dict.txt.small.txt')

import requests
# import codecs
# from textrank4zh import TextRank4Keyword, TextRank4Sentence
# from snownlp import SnowNLP
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
import re

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
    try:#如果沒有第二頁
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
        tt=soup.find('a', class_='tit')
        for temp in soup.find_all('a', class_='tit'):
            title.append(temp.text)
            #temp_url=temp.get('href')
            #print(temp.text+"："+temp_url)
        for temp in soup2.find_all('a', class_='tit'):
            title.append(temp.text)
            #temp_url=temp.get('href')
            #print(temp.text+"："+temp_url)
            
        print(title)

        #這邊開始分析標題，將每個標題都抓出一個關鍵字
        total=[]
        for elements in title:
            words = jieba.cut(elements, cut_all=False)
            title_keyword.append(jieba.analyse.extract_tags(elements,topK=1, withWeight=False)[0])
    
            
        new_key_list = list(set(title_keyword))#利用集合刪掉重複的關鍵字

        #下面是因為結巴的語法問題，所以要將剛剛找出的所有關鍵字重組成一個字串
        new_key=""
        for element in new_key_list:
            new_key+=element
            new_key+="，"
        words =pseg.cut(new_key)#然做同樣的事，先切割字串

        print("關鍵字：")#再抓出關鍵字
        origin=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False, allowPOS=('ng','nr','nrfg','nrt','ns','nt'))    
        finallist=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False)
        ttmp=[]
        try:
            print("原本的：")
            for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
                print(origin[i])#印出三組供使用者選的關鍵字
                ttmp=origin
        except:
            print("抓不滿的情況：")
            for i in range(0,len(origin)):
                finallist.append(origin[i])
            print(finallist)
            for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
                print(finallist[i])#印出三組供使用者選的關鍵字
            print(finallist[1],finallist[-1],finallist[-2])
            ttmp.append(finallist[1])
            ttmp.append(finallist[-1])
            ttmp.append(finallist[-2])

        ttmp.append(tt.get('href'))
    except:
        browser.quit()
        print("======================沒有第二頁===================")
        #解析網站抓出標題
        try:#如果都沒有新聞的話
            soup = BeautifulSoup(url.text, 'html.parser')
            #print("網站內容")
            #print(soup.prettify())
            tt=soup.find('a', class_='tit')
            for temp in soup.find_all('a', class_='tit'):
                title.append(temp.text)
                #temp_url=temp.get('href')
                #print(temp.text+"："+temp_url)

                
            print(title)

            #這邊開始分析標題，將每個標題都抓出一個關鍵字
            total=[]
            for elements in title:
                words = jieba.cut(elements, cut_all=False)
                title_keyword.append(jieba.analyse.extract_tags(elements,topK=1, withWeight=False)[0])
        
                
            new_key_list = list(set(title_keyword))#利用集合刪掉重複的關鍵字

            #下面是因為結巴的語法問題，所以要將剛剛找出的所有關鍵字重組成一個字串
            new_key=""
            for element in new_key_list:
                new_key+=element
                new_key+="，"
            words =pseg.cut(new_key)#然做同樣的事，先切割字串

            print("關鍵字：")#再抓出關鍵字
            origin=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False, allowPOS=('ng','nr','nrfg','nrt','ns','nt'))    
            finallist=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False)
            ttmp=[]
            try:
                print("原本的：")
                for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
                    print(origin[i])#印出三組供使用者選的關鍵字
                    ttmp=origin
            except:
                print("抓不滿的情況：")
                for i in range(0,len(origin)):
                    finallist.append(origin[i])
                print(finallist)
                for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
                    print(finallist[i])#印出三組供使用者選的關鍵字
                print(finallist[1],finallist[-1],finallist[-2])
                ttmp.append(finallist[1])
                ttmp.append(finallist[-1])
                ttmp.append(finallist[-2])
            ttmp.append(tt.get('href'))
        except:
            print("====================EMPTY==========================")
            ttmp.append("0000")
        
    


#https://news.ltn.com.tw/search?keyword=%E6%BE%B3%E6%B4%B2%E5%A4%A7%E7%81%AB

    
    return ttmp

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
    title.append(temp_final.get('href'))
    #temp_ltn_link=temp_final.get('href')
    #print("自由時報ltn:")
    #print(temp_final.text+":"+temp_ltn_link)
    print(title)
    browser.quit()
    return title
    #return temp_ltn_link

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
    try:
        print("網站內容")
        #print(soup.prettify())
        temp=soup.find('div',{'id':'search_content'}).find('dt')
        temp_udn_link=temp.find('a').get('href')
        print("聯合報udn:")
        print(temp.find('h2').text+':'+temp_udn_link)
        browser.quit()
    except:
        temp_udn_link=""
        browser.quit()
    return temp_udn_link

def fourth_part(udn_link, ltn_link):
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
    
    #處理ubn
    for temp in ubn_soup.find_all('p'):
        #print(temp.text)
        ubn_article+=temp.text
    print("UDN：")
    
    ubn_article=ubn_article.replace("分享   facebook","")
    ubn_article=ubn_article.split("》")[0]
    ubn_article=ubn_article.split("      ")[1]
    print(ubn_article)
    
    # words=jieba.posseg.lcut(ubn_article)
    #for word in words:
        #print(word)
    #print(jieba.analyse.extract_tags(ubn_article,topK=20, withWeight=False, allowPOS=('x')))
    #先處理ltn
    f_ltn_article=""
    for temp in ltn_soup.find_all('p'):
        #print(temp.text)
        ltn_article+=temp.text
    print("LTN：")
    #print(ltn_article.split("。"))
    for m in range(0,len(ltn_article.split("。"))-1):
        f_ltn_article+=ltn_article.split("。")[m]
        f_ltn_article+="。"
    ltn_article=f_ltn_article
    
    ltn_article=ltn_article.replace("為達最佳瀏覽效果，建議使用 Chrome、Firefox 或 Microsoft Edge 的瀏覽器。","")
    ltn_article=ltn_article.replace("請繼續往下閱讀...","")
    ltn_article=ltn_article.split("報導〕")[1]
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
    print("ARTICLE\n",article)
    parser = PlaintextParser.from_string(article, Tokenizer("chinese"))
    summarizer = LsaSummarizer()
    print("----摘要結果Lsa----\n")
    abstract1="" #[]
    for sentence in summarizer(parser.document, 2):
        abstract1+=str(sentence)
        # print(sentence_2)
    # abstract1=re.sub(r"\s+","", abstract)
    # abstract1="".join(map(str, abstract))
    print(abstract1)
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=article, lower=True, source = 'all_filters')
    abstract=""
    print("TEXTRANK:")
    for item in tr4s.get_key_sentences(num=1):
        #print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
        print(item.sentence)
        abstract+=str(item.sentence)
    return abstract

def fifth_part(content):
    
    total=[]
    person = jieba.analyse.textrank(content, topK=5, withWeight=False, allowPOS=('n','nt','nz','nr'))
    time = jieba.analyse.textrank(content, topK=3, withWeight=False, allowPOS=('t','tg','m'))
    location = jieba.analyse.textrank(content, topK=3, withWeight=False, allowPOS=('ns'))
    event = jieba.analyse.textrank(content, topK=20, withWeight=False)
    words=pseg.cut(content)
    for w in words:
        print(w.word,w.flag)
    print(person)
    print(time)
    print(location)
    print(event)
    total.append(person)
    total.append(time)
    total.append(location)
    
    parser = PlaintextParser.from_string(content, Tokenizer("chinese"))
    summarizer = LsaSummarizer()
    print("----摘要結果Lsa----\n")
    abstract="" #[]
    for sentence in summarizer(parser.document, 1):
        abstract+=str(sentence)
        print(abstract)
    
    total.append(abstract)
    
    # P="人："
    # T="時："
    # L="地："
    # E="事："

    # person = jieba.analyse.textrank(content, topK=20, withWeight=False, allowPOS=('n','nt','nz','nr'))
    # #time = jieba.analyse.textrank(content, topK=20, withWeight=False, allowPOS=('t','tg','m'))
    # location = jieba.analyse.textrank(content, topK=20, withWeight=False, allowPOS=('ns'))
    # event = jieba.analyse.textrank(content, topK=20, withWeight=False)

    # P+=person[0]
    # #T+=time[0]
    # L+=location[0]
    # E+=event[0]

    # #tatal=P+"\n"+T+"\n"+L+"\n"+E
    # total=P+"\n"+L+"\n"+E
    # # total.append(person)
    # # total.append(time)
    # # total.append(location)
    # # total.append(event)
    # print("87878787878")
    return total
# @handler.add(MessageEvent, message=TextMessage)
# def printit(event1):
#     import threading
#     threading.Timer(5.0, printit(event1)).start()
#     return line_bot_api.reply_message(event1.reply_token,TextSendMessage(text=profile.display_name+"啾都媽爹幾類"))



# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_msg_message(event):

    import re
    content=event.message.text
    #global msg #第一部分輸出的list
    #global msg_flag
    #global totallink
    global user_input
    global totallink
    global torf
    global fk
    #totallink =[]
    #msg_flag=[0,0,0]#初始情況是都沒有被點過
    
    if content[0:2] == "熱搜":#觸發條件
        tStart = time.time()
        torf=0
        
        fk=1
        user_input=content[2:10] #剩餘關鍵字,ex:熱搜 韓國瑜
        user_input=re.sub(r"\s+","", user_input)#去除[2:10]之空白格
        global msg #第一部分輸出的list
        global msg_flag
        global onlyme
        onlyme=[]
        totallink =[]
        msg_flag=[0,0,0]#初始情況是都沒有被點過
        flg=first_part(user_input)[0]
        if(flg!="0000"):
            msg=list(first_part(user_input))
            onlyme.append(msg[-1])
            print(onlyme[-1])
            print(type(onlyme[-1]))
            tEnd = time.time()
            ti=tEnd-tStart
            try:
                if ti>28:
                    print("超時惹wwwwwwwwwwwwww")
                    raise Exception
                delta_t=str(round(tEnd-tStart, 2))
                print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='需要提供推薦的關鍵字ㄇ',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(label="不要 我只要搜尋剛剛那個", text="不要 我只要搜尋剛剛那個")
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label="好啊來吧怕你ㄇ", text="好啊來吧怕你ㄇ")
                                ),
                            ]
                        )
                    )
                )     
            except Exception as e:
                print(f'An Error occurred: {e}')
                delta_t=str(round(tEnd-tStart, 2))
                print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='喔ＱＡＱ剛剛出惹點問題 現在正在努力加載中',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(label="沒關係 我等", text="沒關係 我等")
                                ),
                                QuickReplyButton(
                                    action=MessageAction(label="噢不那算惹", text="噢不那算惹")
                                ),
                            ]
                        )
                    )
                )     
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="現在只支援三個月內的事喔喔喔OTZ"))
    if content =="沒關係 我等":
        tStart = time.time()
        msg=list(first_part(user_input))
        onlyme.append(msg[-1])
        print(onlyme[-1])
        print(type(onlyme[-1]))
        tEnd = time.time()
        ti=tEnd-tStart
        delta_t=str(round(tEnd-tStart, 2))
        print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='需要提供推薦的關鍵字ㄇ',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="不要 我只要搜尋剛剛那個", text="不要 我只要搜尋剛剛那個")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="好啊來吧怕你ㄇ", text="好啊來吧怕你ㄇ")
                        ),
                    ]
                )
            )
        )     
    if content =="不要 我只要搜尋剛剛那個":#觸發條件
        tStart = time.time()
        torf=1
        # tEnd = time.time()
        # delta_t=str(round(tEnd-tStart, 2))
        # T=second_part(user_input," ")
        totallink.append(onlyme[-1]) #ltn_link
        #udn_link=third_part(user_input,msg_choose) #udn_link
        #abstract=fourth_part(ltn_link,udn_link) #abstract
        print(totallink[0])
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='接下來需要花點時間呦',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="快結束惹 點我集氣一下", text="快結束惹 點我集氣一下")
                            ),
                        ]
                    )
                )
            ) 

        
        print('===========================here costing: ' + delta_t + ' seconds=====================')    
     
    if content == "好啊來吧怕你ㄇ":#觸發條件
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='相關の關鍵字如下:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="請過目 僅供參考", text="請過目 僅供參考")
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
    
    #下面是對應三個關建字按鈕
    if fk==1:
        if content == msg[0]:
            tStart = time.time()
            
            msg_flag[0]=1

            tEnd = time.time()
            delta_t=str(round(tEnd-tStart, 2))
            T=second_part(user_input,msg[0])
            totallink.append(T[1]) #ltn_link
            #udn_link=third_part(user_input,msg_choose) #udn_link
            #abstract=fourth_part(ltn_link,udn_link) #abstract
            print(totallink[0])
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='是不是在想我怎麼消失惹',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(label="快結束惹 點我集氣一下", text="快結束惹 點我集氣一下")
                                ),
                            ]
                        )
                    )
                ) 

            
            print('===========================here costing: ' + delta_t + ' seconds=====================')

        if content == msg[1]:
            tStart = time.time()

            msg_flag[1]=1

            tEnd = time.time()
            delta_t=str(round(tEnd-tStart, 2))
            T=second_part(user_input,msg[1])
            totallink.append(T[1])  #ltn_link
            #udn_link=third_part(user_input,msg_choose) #udn_link
            #abstract=fourth_part(ltn_link,udn_link) #abstract
            print(totallink[0])
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='是不是在想我怎麼消失惹',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(label="快結束惹 點我集氣一下", text="快結束惹 點我集氣一下")
                                ),
                            ]
                        )
                    )
                ) 

            
            print('===========================here costing: ' + delta_t + ' seconds=====================')

        if content == msg[2]:
            tStart = time.time()
            msg_flag[2]=1

            tEnd = time.time()
            delta_t=str(round(tEnd-tStart, 2))
            T=second_part(user_input,msg[2])
            totallink.append(T[1]) #ltn_link
            #udn_link=third_part(user_input,msg_choose) #udn_link
            #abstract=fourth_part(ltn_link,udn_link) #abstract
            print(totallink[0])
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text='是不是在想我怎麼消失惹',
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(
                                    action=MessageAction(label="快結束惹 點我集氣一下", text="快結束惹 點我集氣一下")
                                ),
                            ]
                        )
                    )
                ) 

            
            print('===========================here costing: ' + delta_t + ' seconds=====================')

    if content=="快結束惹 點我集氣一下":
        tStart = time.time()
        print(torf)
        if torf ==1:
            print("聯合報修正")
            totallink.append(third_part(user_input," ")) #udn_link
        else:
            if msg_flag[0]==1:
                totallink.append(third_part(user_input,msg[0])) #udn_link
            if msg_flag[1]==1:
                totallink.append(third_part(user_input,msg[1])) #udn_link
            if msg_flag[2]==1:
                totallink.append(third_part(user_input,msg[2])) #udn_link
        tEnd = time.time()
        ti=tEnd-tStart
        try:
            if ti>28:
                raise Exception
            delta_t=str(round(tEnd-tStart, 2))
            print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
            buttons_template = TemplateSendMessage(
                alt_text='功能 template',
                template=ButtonsTemplate(
                    title='想幹嘛',
                    text='想幹嘛',
                    thumbnail_image_url='https://i.imgur.com/qKkE2bj.jpg',
                    actions=[
                        MessageTemplateAction(
                            label='有相關新聞嗎',
                            text='有相關新聞嗎'
                        ),
                        MessageTemplateAction(
                            label='我要看摘要',
                            text='我要看摘要'
                        ),
                        MessageTemplateAction(
                            label='說重點',
                            text='說重點'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, buttons_template)

        except Exception as e:
            print(f'An Error occurred: {e}')   
            delta_t=str(round(tEnd-tStart, 2))
            print('time elapsed: ' + delta_t + ' seconds') #27.715998888015747秒 ㄏㄏ #20.58857011795044
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='喔ＱＡＱ剛剛出惹點問題 現在正在努力加載中',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="沒關係 我還可以等", text="沒關係 我還可以等")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="噢不那算惹", text="噢不那算惹")
                            ),
                        ]
                    )
                )
            )     
    if content=="沒關係 我還可以等":
        print(torf)
        if torf ==1:
            print("沒關係我還可以等")
            totallink.append(third_part(user_input," ")) #udn_link
        else:
            if msg_flag[0]==1:
                totallink.append(third_part(user_input,msg[0])) #udn_link
            if msg_flag[1]==1:
                totallink.append(third_part(user_input,msg[1])) #udn_link
            if msg_flag[2]==1:
                totallink.append(third_part(user_input,msg[2])) #udn_link

        buttons_template = TemplateSendMessage(
            alt_text='功能 template',
            template=ButtonsTemplate(
                title='想幹嘛',
                text='想幹嘛',
                thumbnail_image_url='https://i.imgur.com/qKkE2bj.jpg',
                actions=[
                    MessageTemplateAction(
                        label='有相關新聞嗎',
                        text='有相關新聞嗎'
                    ),
                    MessageTemplateAction(
                        label='我要看摘要',
                        text='我要看摘要'
                    ),
                    MessageTemplateAction(
                        label='說重點',
                        text='說重點'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    if content=="有相關新聞嗎":
        if totallink[1]=="":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="聯合報沒有相關新聞\n"+"自由時報ltn:\n"+totallink[0]))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="聯合報udn:\n"+totallink[1]+"\n自由時報ltn:\n"+totallink[0]))
    if content=="說重點":
        tStart = time.time()
        p=""
        t=""
        l=""
        temppp=fifth_part(fourth_part(totallink[0],totallink[1]))
        print(temppp)
        for i in range(0,len(temppp[0])):
            p+=temppp[0][i]
            p+=" "
        for i in range(0,len(temppp[1])):
            t+=temppp[1][i]
            t+=" "
        for i in range(0,len(temppp[2])):
            l+=temppp[2][i]
            l+=" "
        tEnd = time.time()
        delta_t=str(round(tEnd-tStart, 2))
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="人："+p+"\n"+"\n"+"時："+t+"\n"+"\n"+"地："+l+"\n"+"\n"+"事："+temppp[-1]))
        print('=============================here costing: ' + delta_t + ' seconds====================')
        #TextSendMessage(text="人 : "+temppp[0][0]+"\n"+"事 : "+temppp[3][0]+"\n"+"時 : "+temppp[1][0]+"\n"+"地 : "+temppp[2][0]+"\n")
    if content == "我要看摘要":
        tStart = time.time()
        #msg_choose=msg[0]
        abstract=fourth_part(totallink[0],totallink[1]) #abstract
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="摘要:\n"+abstract))
        tEnd = time.time()
        delta_t=str(round(tEnd-tStart, 2))
        print('=============================here costing: ' + delta_t + ' seconds====================')
    if content=="噢不那算惹":
        tStart = time.time()
        torf=1
        # tEnd = time.time()
        # delta_t=str(round(tEnd-tStart, 2))
        # T=second_part(user_input," ")
        totallink.append(onlyme[-1]) #ltn_link
        #udn_link=third_part(user_input,msg_choose) #udn_link
        #abstract=fourth_part(ltn_link,udn_link) #abstract
        print(totallink[0])
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='抱歉啦ＱＡＱ目前還有很多地方需要改進',
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="我知道惹", text="我知道惹")
                            ),
                        ]
                    )
                )
            ) 

        
        print('===========================here costing: ' + delta_t + ' seconds=====================')    

    else:
        if content !="使用說明" and content !="找Ｃ0" and content!="問題回饋":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='🙂🙃'+'說點有意義的話好嗎'+'🙃🙂'))
####################### 執行 Flask ######################
if __name__ == "__main__":
    app.run(debug=True)