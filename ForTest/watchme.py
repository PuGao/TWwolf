# -*- coding: utf-8 -*-


#這個是用來跑資料庫的  目前只跑推薦三個關鍵字的部分 如果如果不推薦的話還沒跑




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
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from snownlp import SnowNLP
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


###################### 初始化 Flask #####################
from flask import Flask, request, abort

############### 初始化 Callback Endpoint ################

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
    browser.close()
    
    onlyme.append(url)


    #解析網站抓出標題
    soup = BeautifulSoup(url.text, 'html.parser')
    soup2 = BeautifulSoup(url2.text, 'html.parser')
    #print("網站內容")
    #print(soup.prettify())
    tt=soup.find('a', class_='tit')
    for temp in soup.find_all('a', class_='tit'):
        try:
            #print(temp.text.split("〉")[1])
            t1=temp.text.split("〉")[1]
            title.append(t1)
        except:
            title.append(temp.text)
            
        #temp_url=temp.get('href')
        #print(temp.text+"："+temp_url)
    for temp in soup2.find_all('a', class_='tit'):
        try:
            #print(temp.text.split("〉")[1])
            t1=temp.text.split("〉")[1]
            title.append(t1)
        except:
            title.append(temp.text)
    OP=[]#我想不到更好的寫法惹先這樣 我不懂為什麼原本一大堆try except的哪有有問題
    for i in range(0,len(title)):
        try:
            t2=title[i].split("》")[1]
            OP.append(t2)
        except:
            OP.append(title[i])
    title=OP
    for yoyo in title:
        print(len(yoyo))
        if (len(yoyo))<6:
            title.remove(yoyo)
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
    origin=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False, allowPOS=('nz','ng','nr','nrfg','nrt','ns','nt'))    
    finallist=jieba.analyse.extract_tags(new_key,topK=20, withWeight=False)
    try:
        origin.remove(user_input)
    except:
        print("無重複字在origin")
    try:
        finallist.remove(user_input)
    except:
        print("無重複字在finallist")
    ttmp=[]
    try:
        print("原本的：")
        for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
            print(origin[i])#印出三組供使用者選的關鍵字
            ttmp=origin
    except:
        ttmp.clear()
        print("抓不滿的情況：")
        for i in range(0,len(origin)):
            finallist.append(origin[i])
        print(finallist)
        for i in range(3,6):#選第3到5個是經驗法則，通常前面的東西都有點奇怪
            print(finallist[i])#印出三組供使用者選的關鍵字
            ttmp.append(finallist[i])
        mid=int((len(finallist))/2)
        print(finallist[mid-1],finallist[mid],finallist[mid+1])
        # ttmp.append(finallist[1])
        # ttmp.append(finallist[-1])
        # ttmp.append(finallist[-2])

    ttmp.append(tt.get('href'))
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
    temp_ltn_link=temp_final.get('href')
    #print("自由時報ltn:")
    #print(temp_final.text+":"+temp_ltn_link)
    #print(title)
    browser.quit()
    #return title
    print("LTN\n",temp_ltn_link)
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
    #print("網站內容")
    #print(soup.prettify())
    temp=soup.find('div',{'id':'search_content'}).find('dt')
    temp_udn_link=temp.find('a').get('href')
    #print("聯合報udn:")
    #print(temp.find('h2').text+':'+temp_udn_link)
    browser.quit()
    print("UBN\n",temp_udn_link)
    return temp_udn_link

def fourth_part(udn_link, ltn_link):#這邊4最新的
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
    print("UＢN：")
    try:
        ubn_article=ubn_article.replace("分享   facebook","")
        ubn_article=ubn_article.split("》")[0]
        ubn_article=ubn_article.split("      ")[1]
        print("整理後",ubn_article)
    except:
        print("沒辦法擋ＵＢＮ")
    
    
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
    print("整理前：\n",ltn_article)
    
    try:
        ltn_article=ltn_article.replace("為達最佳瀏覽效果，建議使用 Chrome、Firefox 或 Microsoft Edge 的瀏覽器。","")
        ltn_article=ltn_article.replace("請繼續往下閱讀...","")
        ltn_article=ltn_article.replace("圖／","")
        ltn_article=ltn_article.split("報導〕")[1]
        ltn_article=ltn_article.split("看更多報導：")[0]
        print("整理後:",ltn_article)
    except:
        print("沒辦法擋掉")
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
    abstract=""
    
    parser = PlaintextParser.from_string(article, Tokenizer("chinese"))
    summarizer = LsaSummarizer()
    print("----摘要結果Lsa----\n")
    for sentence in summarizer(parser.document, 2):
        abstract+=str(sentence)
    print(abstract)
    if len(abstract)<=1:
        tr4s = TextRank4Sentence()
        tr4s.analyze(text=article, lower=True, source = 'all_filters')
        print("摘要結果TEXTRANK:\n")
        for item in tr4s.get_key_sentences(num=2):
            #print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
            print(item.sentence)
            abstract+=str(item.sentence)
    try:
        if abstract.split("。")[0]==abstract.split("。")[1]:
            abstract=abstract.split("。")[0]
    except:
        print("沒有句號")
    return abstract

def fifth_part(content):#這邊是最新的
    
    total=[]
    person = jieba.analyse.extract_tags(content, topK=5, withWeight=False, allowPOS=('n','nt','nz','nr','nrfg','nrt'))
    time = jieba.analyse.extract_tags(content, topK=3, withWeight=False, allowPOS=('t','tg','m'))
    location = jieba.analyse.extract_tags(content, topK=3, withWeight=False, allowPOS=('ns'))
    event = jieba.analyse.extract_tags(content, topK=20, withWeight=False)
    # words=pseg.cut(content)
    # for w in words:
    #     print(w.word,w.flag)
    # print(person)
    # print(time)
    # print(location)
    # print(event)
    total.append(person)
    total.append(time)
    total.append(location)
    abstract="" #[]
    try:
        parser = PlaintextParser.from_string(content, Tokenizer("chinese"))
        summarizer = LsaSummarizer()
        print("----摘要結果Lsa----\n")
        for sentence in summarizer(parser.document, 2):
            abstract+=str(sentence)
            print(abstract)
    except:
            tr4s = TextRank4Sentence()
            tr4s.analyze(text=article, lower=True, source = 'all_filters')
            print("TEXTRANK:\n")
            for item in tr4s.get_key_sentences(num=2):
                #print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重
                print(item.sentence)
                abstract+=str(item.sentence)
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
    print(total)
    return total

STR1=["台灣","中國","兩岸","大選","總統","習近平","韓國瑜","吳斯懷","選舉","國台辦","外交部","美國","貿易戰","脫歐","歐盟","黑鷹"]
STR2=[["中國","大選","美國"],["台灣","國台辦","美國"],["國台辦","貿易","反滲透"],["總統","立委","韓國瑜"],["蔡英文","韓國瑜","宋楚瑜"],["國台辦","貿易戰","協定"],["敗選","高雄","罷免"],["立委","吳敦義","國民黨"],["總統","小英","韓國瑜"],["台灣","九二共識","耿爽"],["記者會","選舉","日本"],["中國","台灣","伊朗"],["中國","協定","台灣"],["強森","歐盟","經濟"],["德國","英國","脫歐"],["蔡英文","國民黨","總長"]]
# # STR1=["台灣","中國"]
# # STR2=[["中國","大選"],["台灣","國台辦"]]
# # link=[]
# # summary=[]
# # keyword=[]
# # for i in range(0,len(STR1)):
# # #for str1 in STR1:
# #     str1=STR1[i]
# #     print("str1:",str1)
# #     three=[]#summary
# #     three2=[]#key
# #     three3=[]#link
# #     for str2 in STR2[i]:    
# #         print("str2:",str2)
# #         totallink="UBN:\n"
# #         A=third_part(str1,str2)
# #         B=second_part(str1,str2)
# #         #str1="中國"
# #         #str2="台灣"
# #         #print("LTN\n",second_part(str1,str2))
# #         #print("UBN\n",third_part(str1,str2))
# #         #print("摘要：\n",fourth_part(third_part(str1,str2),second_part(str1,str2)))
# #         totallink+=A
# #         totallink+="LTN:\n"
# #         totallink+=B
# #         three3.append(totallink)
# #         content=fourth_part(A,B)
# #         three.append(content)
# #         #print("關鍵字：\n",fifth_part(fourth_part(third_part(str1,str2),second_part(str1,str2))))
# #         three2.append(fifth_part(content))
# #     link.append(three3)
# #     summary.append(three)
# #     keyword.append(three2)
# # print("所有連結：",link)
# # print("所有摘要：",summary)
# # print("所有重點：",keyword)
# link=[]
# summary=[]
# keyword=[]
# link=[]
# summary=[]
# keyword=[]
# for i in range(0,len(STR1)):
# #for str1 in STR1:
#     str1=STR1[i]
#     print("str1:",str1)  
#     totallink="UBN:"
#     A=third_part(str1,str1)
#     B=second_part(str1,str1)
#     totallink+=A
#     totallink+="\nLTN:"
#     totallink+=B
#     link.append(totallink)
#     content=fourth_part(A,B)
#     summary.append(content)
#     keyword.append(fifth_part(content))
# print("所有連結：",link)
# print("所有摘要：",summary)
# print("所有重點：",keyword)

# link=[['UBN:https://udn.com/news/story/7266/4290265'+'\nLTN:https://news.ltn.com.tw/news/entertainment/breakingnews/3041705', 'UBN:https://udn.com/news/story/6809/4290069'+'\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041598', 'UBN:\nhttps://udn.com/news/story/7238/4290212'+'\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041747'], ['UBN:\nhttps://udn.com/news/story/7266/4290265'+'\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041705', 'UBN:\nhttps://udn.com/news/story/7331/4289866'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:\nhttps://udn.com/news/story/6811/4290397'+'\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563'], ['UBN:\nhttps://udn.com/news/story/7331/4289954'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:\nhttps://udn.com/news/story/7238/4290195'+'\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041099', 'UBN:\nhttps://udn.com/news/story/7331/4289922'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041510'], ['UBN:\nhttps://udn.com/news/story/6809/4290069'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041773', 'UBN:\nhttps://udn.com/news/story/12667/4289981'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041598', 'UBN:\nhttps://udn.com/news/story/12667/4290035'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749'], ['UBN:\nhttps://udn.com/news/story/7314/4290363'+'\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041773', 'UBN:\nhttps://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:\nhttps://udn.com/news/story/12667/4289405\nLTNhttps://news.ltn.com.tw/news/politics/paper/1346152'], ['UBN:\nhttps://udn.com/news/story/12702/4289747\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040852', 'UBN:\nhttps://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/politics/paper/1345335', 'UBN:\nhttps://udn.com/news/story/6809/4288852\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040682'], ['UBN:\nhttps://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041172', 'UBN:\nhttps://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:\nhttps://udn.com/news/story/7327/4289919\nLTNhttps://news.ltn.com.tw/news/life/breakingnews/3040233'], ['UBN:\nhttps://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041396', 'UBN:\nhttps://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041215', 'UBN:\nhttps://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041396'], ['UBN:\nhttps://udn.com/news/story/6809/4290069\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:\nhttps://udn.com/news/story/120920/4289260\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040935', 'UBN:\nhttps://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749'], ['UBN:\nhttps://udn.com/news/story/7331/4289954\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:\nhttps://udn.com/news/story/7331/4289866\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041578', 'UBN:\nhttps://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/opinion/breakingnews/3039159'], ['UBN:\nhttps://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:\nhttps://udn.com/news/story/6656/4289952\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041510', 'UBN:\nhttps://udn.com/news/story/6809/4288539\nLTNhttps://news.ltn.com.tw/news/politics/paper/1346147'], ['UBN:\nhttps://udn.com/news/story/6811/4290397\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:\nhttps://udn.com/news/story/7238/4290212\nLTNhttps://news.ltn.com.tw/news/life/breakingnews/3041745', 'UBN:\nhttps://udn.com/news/story/6809/4290177\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041134'], ['UBN:\nhttps://udn.com/news/story/6811/4290397\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041790', 'UBN:\nhttps://udn.com/news/story/7238/4289218\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041609', 'UBN:\nhttps://udn.com/news/story/7238/4289849\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041604'], ['UBN:\nhttps://udn.com/news/story/6809/4277736\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3039957', 'UBN:\nhttps://udn.com/news/story/6809/4287960\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882', 'UBN:\nhttps://udn.com/news/story/6811/4290356\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882'], ['UBN:\nhttps://udn.com/news/story/6809/4290364\nLTNhttps://news.ltn.com.tw/news/supplement/paper/1346195', 'UBN:\nhttps://udn.com/news/story/120806/4289971\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882', 'UBN:\nhttps://udn.com/news/story/6809/4287960\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882'], ['UBN:\nhttps://udn.com/news/story/10930/4290137\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040949', 'UBN:\nhttps://udn.com/news/story/10930/4288283\nLTNhttps://news.ltn.com.tw/news/politics/paper/1346135', 'UBN:\nhttps://udn.com/news/story/10930/4290137\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041493']]
# summary=[['賈樟柯執導新片《一直游到海水變藍》入選第70屆柏林國際影展特別放映單元。《一直游到海水變藍》在台灣將由佳映娛樂發行，更多資訊請持續關注官方臉書。', '這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。', '台積電表示，公司從未排除在美國設廠生產的可能性，只是目前尚無具體計畫，將依客戶需求考量。公司從未排除赴美國設廠生產的可能性，只是目前還沒有具體計畫。'], ['賈樟柯執導新片《一直游到海水變藍》入選第70屆柏林國際影展特別放映單元。《一直游到海水變藍》在台灣將由佳映娛樂發行，更多資訊請持續關注官方臉書。', '北京當局必須懂得尊重、勇敢面對現實，更須深刻思考這段時間以來，其「一廂情願」與強制打壓都無法改變這個事實。陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。', '耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。'], ['民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '許勝雄指出，目前看起來國、內外的經濟面都不錯，尤其美中要簽第1階段協議，另外美國總統選舉前不會有局勢大變化，全球市場信心可以穩定下來，只要世界好，台灣就一定好，台灣有充沛的人才、環境、國際化布局和國際誠信等條件，有雄厚的實力，樂觀看待2020年（經濟發展）三三會今天中午舉行1月份例會，三三會理事長許勝雄會前受訪表示，美中貿易戰將簽第1階段協議，全球市場信心可以穩定下來，台灣產業有雄厚實力、競爭力，只要世界經濟局勢好，台灣經濟表現就會向上', '「反滲透法」今日公布施行，陸委會表示，已會同內政部、外交部、法務部、中選會及海基會等相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討；未來法案如有研修的需求，將由所涉業管機關視情形領銜修法，再會銜其他機關，依一般法制作業程序來進行。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。'], ['這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。台南1位楊姓男子是蔡英文總統粉絲，他為了慶祝小英連任總統、自掏腰包買1千片雞排與民眾分享，其陳姓友人響應加碼100片，於1月13日晚上在南區水萍塭公園門口發送，吸引人潮排隊領取，但仍有人向隅、沒拿到雞排。', '2020大選落幕，台聯僅獲得0.3%政黨票，黨主席劉一德今天向中執會提出辭呈，但中執委全數不通過；劉一德即日起請假，思考個人未來，請假期間，黨主席職務由前立委周倪安代理。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」'], ['台南1位楊姓男子是蔡英文總統粉絲，他為了慶祝小英連任總統、自掏腰包買1千片雞排與民眾分享，其陳姓友人響應加碼100片，於1月13日晚上在南區水萍塭公園門口發送，吸引人潮排隊領取，但仍有人向隅、沒拿到雞排。林俊憲表示，發放雞排與煎包的時間訂於1月18日 （週六） 晚間7點半（其服務時間結束後），民眾請於這時間點、到南市中西區永華路一段305號領取雞排與煎包。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」', '高雄市長韓國瑜敗選後重回高雄市上班，台北市議員秦慧珠今天繼續發文「2020大選慘敗後感言之四」，她不認為罷韓行動會成功，因為單一罷免案在台灣投票率一向不高，也幾乎沒有成功過，但如果韓粉太過激進，炒熱了罷韓行動，反而會提高投票率，那就有可能會成功，縱使不成功，超高的罷韓選票也會再一次讓韓國瑜難堪，讓社會撕裂。鑑於時代力量不分區立委當選人「小燈泡媽媽」王婉諭遭網友留言恐嚇，大選時擔任親民黨總統候選人宋楚瑜發言人的于美人，昨邀集總統大選各陣營發言人茶敘。'], ['兩岸政策協會理事長譚耀南表示，以和平與對等方式處理兩岸歧見，正視中華民國的存在，對話也是要政府與政府之間對等坐下談，中華民國是台灣人民最大的公約數。台師大政研所教授范世平指出，昨天親中媒體社論談及，希望中共正視蔡英文總統1月11日的談話，且昨天香港中評社的快論，指兩岸關係更趨嚴峻，但並非完全無對話空間，這部分可看出一些端倪。', '風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。', '華府智庫「美國企業研究所」（American Enterprise Institute,AEI）研究員狄森（Marc Thiessen）曾任美國前總統小布希（George W. Bush）文膽，他目前兼任「華盛頓郵報」（Washington Post）專欄作家。他說，台美FTA不只可能促進美國經濟並提高出口，還能增加對中國壓力，並在美國國會獲得跨黨派支持。'], ['國民黨主席吳敦義今天下午率相關黨務主管向中常會提出總辭，同時也就這次總統、立委選舉敗選原因提出檢討報告，其中羅列7大敗因，分別為「討厭民進黨」終不敵「亡國感」﹔兩岸論述未能掌握話語權，無法因應當下變局﹔惡質網軍帶領風向，候選人品牌形象飽受挑戰，難以爭取中間選民認同﹔高雄市長勝選模式無法複製，選戰策略選擇失誤﹔黨內矛盾不團結，輔選力道仍待加強﹔不分區名單未能符合外界期待﹔以及青年參與政治程度高，不受青年選民青睞。國民黨這份報告對於該黨總統候選人韓國瑜有諸多直白的檢討與質疑，包括在這次競選過程中，因為市長就職之後不到半年即宣布參選總統，無法彌平落跑市長的爭議，誠信問題受到質疑，而且過去在高雄市議會備詢跳針式回答、太平島挖石油、迪士尼到高雄、賽馬場、賽車場等極具話題性的政見逐一跳票，能力問題飽受懷疑，再加上失言、歧視語言、違規農舍、豪宅案、麻將照到新莊王小姐案等等事件，私德問題也備受考驗，庶民形象大大削減。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」', '市長韓國瑜敗選返回市府上班，未來他在議會定期大會面對民意監督還有一場硬仗，屆時定期大會的質詢將再成焦點。不過，時代力量市議員林于凱發布新聞稿質疑時程延到4月16日開議是要助韓國瑜躲質詢避出糗，疑與罷免案有關。'], ['吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。', '儘管要求吳斯懷辭立委的浪潮如驚滔駭浪襲捲國民黨，但事實上，要求吳斯懷辭跟「會不會辭」是兩碼子事情。所以，是誰力保吳斯懷得免於外部壓力而辭去立委之職？', '吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。'], ['這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。歐洲議會往年均表達支持台灣的國際參與，也再度呼籲中國避免片面改變現況。', '工商協進會今（15）日舉行公亮紀念講座，邀請財信傳媒集團董事長謝金河，以「全球變動經濟中 台灣三十年的新定位」為題發表演講。蔡英文台南競選總部總幹事黃先柱、主任潘新傳今（15日）偕同地方幹部召開地方組織會議，感謝選戰期間同仁的辛苦付出，讓蔡賴配在台南蟬聯全國最高得票率，拿下67.37%得票佳績，更大贏對手近45萬票；同時提名的6席區域立委也全數高票當選，揮出漂亮全壘打。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」'], ['民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。陸委會強調，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。', '風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。'], ['風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。', '外交部表示，交流過程中，他們都恭賀蔡總統連任，並讚揚台灣人民透過此次選舉，向全世界傳達捍衛民主自由的堅定立場。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。', '至於美國是否在會談中要求南韓派兵荷莫茲海峽一事，康京和表示，美方一直認為與荷莫茲海峽存在經濟利害關係的國家都應做出貢獻，鑑於南韓70%的原油進口依賴該地區，應該對此予以關注南韓聯合新聞通訊社報導，康京和於美國時間14日在舊金山與美國、日本兩國外長舉行雙邊和三邊會談後，會見媒體記者時做上述表示'], ['耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。', '', '「抵抗」是指阿拉伯人和伊朗人反擊美國、以色列及諸如沙烏地阿拉伯、阿拉伯聯合大公國等華府的阿拉伯盟友。《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。'], ['美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。美國總統川普及中國國務院總理劉鶴，預計將在台北時間凌晨00:30正式在白宮簽署第1階段貿易協議，投資人正等待這場延續近2年的貿易戰達成階段性協議，也在觀望簽署後才會釋出的正式協議文本內容。', '許勝雄今天於三三企業交流會會前受訪時表示，全世界經濟上來了，台灣經濟必然可以上來，國際預測機構估2019年全球經濟成長率落在3%左右、2020年有機會達3.4%，台灣經濟受惠於美中貿易戰帶來台商回流、國際企業赴台投資，國內也有政府投資與消費，據主計總處預測，2020年經濟成長率為2.72%，優於2019年的2.64%此外，許勝雄指出，政府應積極爭取加入跨太平洋夥伴全面進步協定（CPTPP）、區域全面經濟夥伴關係協定（RCEP），以及簽訂更多自由貿易協定（FTA），這是攸關台灣國際競爭力的重要議題，否則和韓國、越南、新加坡相比，台灣招商引資的力度會被弱化', '技嘉（2376）已經成立 33年，近幾年公司內逐步啟動世代交替，也嘗試通路、手機、車電、工業電腦等新事業，董事長葉培城說，「我們創辦的這一代，說年輕不年輕、說老不老，公司也要做主機板以外的事，有一些新產品、市場趨勢也需要新思維，像之前做手機的時候，都叫他們（下屬）不要問我\u3000因為我的使用習慣可能跟不一樣，怕誤導他們，這種事一定要讓中生代進來」未來兩岸，林伯豐認為，蔡英文總統連任，第二任的任期空間相對寬闊，也有很多選擇，她要怎麼選，大陸要怎麼回應，雙邊都要有智慧，對方能接受什麼、台灣能接受什麼，都有了解在，這就是願不願意做，做的結果是對台灣好還是不好要好好判斷'], ['英國首相強森則表示，2020完全脫歐是「勢在必行」但願意與歐盟進行友善的合作。分析師Douglas Paxman表示，除非英國、歐盟達成貿易協議，否則無協議脫歐風險無法消除，房產交易量和價格將因此受限。', '在加入歐盟將近50年後，英國預定1月31日脫歐，並開始把外交和經濟關注焦點更轉移到世界其他地區。在父親明仁退位後，59歲的德仁去年5月1日登上「菊花寶座」（Chrysanthemum Throne）。', "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。"], ['不過，檢察官證實明鏡周刊一項消息，即警方今天突襲搜查這3人位於柏林、布魯塞爾、德國巴伐利亞邦（Bavaria）及巴登符騰堡邦（Baden-Wuerttemberg）的住所和辦公室。」爆記者凌美雪／專題報導2020台北國際書展將於農曆年後（2月4日至9日）「閱讀新風景」，主辦單位台北書展基金會昨搶先公布書展重要活動與國內外展館亮點。', '自伊朗去年5月初開始逐步違反核協議規定，以回應美國正式落實其單方面的石油制裁後，英法德三國一直猶豫應否啟動此等程序；到伊朗聖城軍將領蘇萊曼尼（Qassem Soleimani）1月3日遇刺，伊朗決定不再遵守任何協議的核條款，三國才不得不作出回應。說到底，伊朗目前的經濟難局最終還是要靠美伊兩國解決，他國插手在短期內難有可見成果。', '在加入歐盟將近50年後，英國預定1月31日脫歐，並開始把外交和經濟關注焦點更轉移到世界其他地區。在父親明仁退位後，59歲的德仁去年5月1日登上「菊花寶座」（Chrysanthemum Throne）。'], ['今年63歲的黃曙光為海軍官校68年班、國防大學指揮參謀班82年班、國防大學戰略參謀班90年班，曾任國防部作戰及計畫參謀次長室處長、海軍一六八艦隊艦隊長、海軍司令部參謀長、國防部後勤參謀次長室次長、海軍艦隊指揮部指揮官、海軍司令部副司令、海軍司令部司令，明天將接任參謀總長軍方人士指出，潛艦國造政策推行多年，但在總統蔡英文上任以後才真正大有進展，除了黃曙光本身實事求是、按部就班的行事風格外，由於曾任國軍潛艦要職，加上軍事歷練豐富，也具有令人服氣的領導風格，因此脫穎而出，以黃任職司令期間推動的潛艦計畫，未來對於潛艦國造是一大助力', '記者陳正興／攝影國防部昨舉行參謀總長沈一鳴、總士官長韓正宏等八位黑鷹直升機失事殉職將士的聯合公奠典禮，蔡英文總統親自頒授獎章、追晉官階及頒贈褒揚令給將士家屬，致詞時並宣布行政院已核定通過士官長專業加給、空降特戰勤務加給及飛行軍官續服獎助金等三項國軍加給，「希望所有受惠的弟兄姊妹記住，這是沈總長和韓總士官長念茲在茲的事情蔡總統致詞時除了感謝殉職將士、殉職者家屬及外賓外，也特別宣布行政院已核定通過沈一鳴、韓正宏生前努力推動的飛行軍官續服獎助金、士官長專業加給及空降特戰勤務加給共三項加給，希望所有受惠者都記住這是沈、韓念茲在茲的事情，並將他們的精神永存心中', '故參謀總長沈一鳴一級上將因黑鷹直升機失事殉職，國防部今天宣布新總長人事案，由上將之中期別最資深的海軍司令黃曙光上將接任，海軍司令一職則由副參謀總長執行官劉志斌上將繼任今年63歲的黃曙光為海軍官校68年班、國防大學指揮參謀班82年班、國防大學戰略參謀班90年班，曾任國防部作戰及計畫參謀次長室處長、海軍一六八艦隊艦隊長、海軍司令部參謀長、國防部後勤參謀次長室次長、海軍艦隊指揮部指揮官、海軍司令部副司令、海軍司令部司令，明天將接任參謀總長']]
# keyword=[[[['海水', '樟柯', '國際', '單元', '資訊'], ['70'], ['海水', '樟柯', '國際'], '賈樟柯執導新片《一直游到海水變藍》入選第70屆柏林國際影展特別放映單元。《一直游到海水變藍》在台灣將由佳映娛樂發行，更多資訊請持續關注官方臉書。'], [['項決議案', '實質', '區域', '軍事', '現狀'], ['下午'], ['項決議案', '實質', '區域'], '這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。'], [['設廠', '計畫', '台積', '客戶', '公司'], ['目前'], ['設廠', '計畫', '台積'], '台積電表示，公司從未排除在美國設廠生產的可能性，只是目前尚無具體計畫，將依客戶需求考量。公司從未排除赴美國設廠生產的可能性，只是目前還沒有具體計畫。']], [[['海水', '樟柯', '國際', '單元', '資訊'], ['70'], ['海水', '樟柯', '國際'], '賈樟柯執導新片《一直游到海水變藍》入選第70屆柏林國際影展特別放映單元。《一直游到海水變藍》在台灣將由佳映娛樂發行，更多資訊請持續關注官方臉書。'], [['當局', '敢面', '時間', '陸委會', '性思'], [], ['當局', '敢面', '時間'], '北京當局必須懂得尊重、勇敢面對現實，更須深刻思考這段時間以來，其「一廂情願」與強制打壓都無法改變這個事實。陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。'], [['耿爽', '長期', '眼鏡', '言論', '報告'], ['兩個'], ['長期', '眼鏡', '言論'], '耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。']], [[['主權', '國家', '人民', '民進黨', '秘書長'], ['未來', '過去', '2300'], ['主權', '國家', '人民'], '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['經濟', '許勝雄', '階段', '協議', '局勢'], ['三三', '三三會', '會前'], ['經濟', '階段', '協議'], ''], [['陸委會', '內政部', '法務部', '海基會', '單位'], ['未來', '今日'], ['單位', '滲透法', '小組'], '「反滲透法」今日公布施行，陸委會表示，已會同內政部、外交部、法務部、中選會及海基會等相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討；未來法案如有研修的需求，將由所涉業管機關視情形領銜修法，再會銜其他機關，依一般法制作業程序來進行。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。']], [[['總統', '項決議案', '實質', '區域', '軍事'], ['千片', '100', '13'], ['總統', '項決議案', '實質'], '這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。台南1位楊姓男子是蔡英文總統粉絲，他為了慶祝小英連任總統、自掏腰包買1千片雞排與民眾分享，其陳姓友人響應加碼100片，於1月13日晚上在南區水萍塭公園門口發送，吸引人潮排隊領取，但仍有人向隅、沒拿到雞排。'], [['劉一德', '黨主席', '資料', '記者', '廖振輝'], ['0.3', '未來', '下午'], ['黨主席', '資料', '記者'], '（資料照，記者廖振輝攝）〔中央社〕2020大選落幕，台聯僅獲得0.3%政黨票，黨主席劉一德今天向中執會提出辭呈，但中執委全數不通過；劉一德即日起請假，思考個人未來，請假期間，黨主席職務由前立委周倪安代理。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。'], [['市政', '行程', '惜福', '市長', '題發文'], ['今晚', '今日'], ['市政', '行程', '市長'], '']], [[['總統', '民眾', '時間', '蔡英文', '粉絲'], ['千片', '100', '13'], ['總統', '民眾', '時間'], '台南1位楊姓男子是蔡英文總統粉絲，他為了慶祝小英連任總統、自掏腰包買1千片雞排與民眾分享，其陳姓友人響應加碼100片，於1月13日晚上在南區水萍塭公園門口發送，吸引人潮排隊領取，但仍有人向隅、沒拿到雞排。林俊憲表示，發放雞排與煎包的時間訂於1月18日 （週六） 晚間7點半（其服務時間結束後），民眾請於這時間點、到南市中西區永華路一段305號領取雞排與煎包。'], [['市政', '行程', '惜福', '市長', '題發文'], ['今晚', '今日'], ['市政', '行程', '市長'], ''], [['記者', '選人', '投票', '市長', '議員'], ['今天', '一次'], ['記者', '選人', '投票'], '高雄市長韓國瑜敗選後重回高雄市上班，台北市議員秦慧珠今天繼續發文「2020大選慘敗後感言之四」，她不認為罷韓行動會成功，因為單一罷免案在台灣投票率一向不高，也幾乎沒有成功過，但如果韓粉太過激進，炒熱了罷韓行動，反而會提高投票率，那就有可能會成功，縱使不成功，超高的罷韓選票也會再一次讓韓國瑜難堪，讓社會撕裂。爆（圖：記者塗建榮，文：記者陳昀）鑑於時代力量不分區立委當選人「小燈泡媽媽」王婉諭遭網友留言恐嚇，大選時擔任親民黨總統候選人宋楚瑜發言人的于美人，昨邀集總統大選各陣營發言人茶敘。']], [[['協會', '理事長', '譚耀南', '公約', '台師大政研所'], ['11', '昨天', '一些'], ['協會', '理事長', '公約'], '兩岸政策協會理事長譚耀南表示，以和平與對等方式處理兩岸歧見，正視中華民國的存在，對話也是要政府與政府之間對等坐下談，中華民國是台灣人民最大的公約數。台師大政研所教授范世平指出，昨天親中媒體社論談及，希望中共正視蔡英文總統1月11日的談話，且昨天香港中評社的快論，指兩岸關係更趨嚴峻，但並非完全無對話空間，這部分可看出一些端倪。'], [['李淳', '風險', '習政權', '民眾', '選票'], ['四項', '11', '先前'], ['風險', '習政權', '內外'], ''], [['華府', '智庫', '企業', '研究員', '狄森'], ['目前'], ['華府', '智庫', '企業'], '華府智庫「美國企業研究所」（American Enterprise Institute,AEI）研究員狄森（Marc Thiessen）曾任美國前總統小布希（George W. Bush）文膽，他目前兼任「華盛頓郵報」（Washington Post）專欄作家。他說，台美FTA不只可能促進美國經濟並提高出口，還能增加對中國壓力，並在美國國會獲得跨黨派支持。']], [[['市長', '問題', '高雄', '總統', '報告'], ['青年', '諸多', '過去'], ['市長', '問題', '總統'], '（中央社）國民黨主席吳敦義今天下午率相關黨務主管向中常會提出總辭，同時也就這次總統、立委選舉敗選原因提出檢討報告，其中羅列7大敗因，分別為「討厭民進黨」終不敵「亡國感」﹔兩岸論述未能掌握話語權，無法因應當下變局﹔惡質網軍帶領風向，候選人品牌形象飽受挑戰，難以爭取中間選民認同﹔高雄市長勝選模式無法複製，選戰策略選擇失誤﹔黨內矛盾不團結，輔選力道仍待加強﹔不分區名單未能符合外界期待﹔以及青年參與政治程度高，不受青年選民青睞。國民黨這份報告對於該黨總統候選人韓國瑜有諸多直白的檢討與質疑，包括在這次競選過程中，因為市長就職之後不到半年即宣布參選總統，無法彌平落跑市長的爭議，誠信問題受到質疑，而且過去在高雄市議會備詢跳針式回答、太平島挖石油、迪士尼到高雄、賽馬場、賽車場等極具話題性的政見逐一跳票，能力問題飽受懷疑，再加上失言、歧視語言、違規農舍、豪宅案、麻將照到新莊王小姐案等等事件，私德問題也備受考驗，庶民形象大大削減。'], [['市政', '行程', '惜福', '市長', '題發文'], ['今晚', '今日'], ['市政', '行程', '市長'], ''], [['市長', '議會', '大會面', '大會', '焦點'], ['未來', '一場', '16'], ['市長', '議會', '大會面'], '市長韓國瑜敗選返回市府上班，未來他在議會定期大會面對民意監督還有一場硬仗，屆時定期大會的質詢將再成焦點。不過，時代力量市議員林于凱發布新聞稿質疑時程延到4月16日開議是要助韓國瑜躲質詢避出糗，疑與罷免案有關。']], [[['吳斯懷', '資料', '記者', '王藝', '國家'], ['一頓'], ['資料', '記者', '國家'], '（資料照，記者王藝菘攝）吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。'], [['吳斯懷', '滔駭', '碼子', '壓力', '事情'], [], ['滔駭', '碼子', '壓力'], '儘管要求吳斯懷辭立委的浪潮如驚滔駭浪襲捲國民黨，但事實上，要求吳斯懷辭跟「會不會辭」是兩碼子事情。所以，是誰力保吳斯懷得免於外部壓力而辭去立委之職？'], [['吳斯懷', '資料', '記者', '王藝', '國家'], ['一頓'], ['資料', '記者', '國家'], '（資料照，記者王藝菘攝）吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。']], [[['片面', '項決議案', '實質', '區域', '軍事'], ['往年'], ['片面', '項決議案', '實質'], '這2項決議案內文均強調加強東亞及東南亞的實質關係對歐盟具重要利益，注意到區域內軍事力量升高，呼籲相關各方尊重航行自由，透過和平方式解決分歧，並避免片面改變現狀。歐洲議會往年均表達支持台灣的國際參與，也再度呼籲中國避免片面改變現況。'], [['立委', '公亮', '紀念', '財信傳媒集團', '董事長'], ['15', '67.37', '45'], ['立委', '公亮', '紀念'], '工商協進會今（15）日舉行公亮紀念講座，邀請財信傳媒集團董事長謝金河，以「全球變動經濟中 台灣三十年的新定位」為題發表演講。蔡英文台南競選總部總幹事黃先柱、主任潘新傳今（15日）偕同地方幹部召開地方組織會議，感謝選戰期間同仁的辛苦付出，讓蔡賴配在台南蟬聯全國最高得票率，拿下67.37%得票佳績，更大贏對手近45萬票；同時提名的6席區域立委也全數高票當選，揮出漂亮全壘打。'], [['市政', '行程', '惜福', '市長', '題發文'], ['今晚', '今日'], ['市政', '行程', '市長'], '']], [[['主權', '國家', '人民', '民進黨', '秘書長'], ['未來', '過去', '2300'], ['主權', '國家', '人民'], '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['陸委會', '當局', '性思', '關鍵', '基礎'], [], ['當局', '性思', '關鍵'], '陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。陸委會強調，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。'], [['李淳', '風險', '習政權', '民眾', '選票'], ['四項', '11', '先前'], ['風險', '習政權', '內外'], '']], [[['李淳', '風險', '習政權', '民眾', '選票'], ['四項', '11', '先前'], ['風險', '習政權', '內外'], ''], [['過程', '立場', '意圖', '離間', '人民'], [], ['過程', '立場', '意圖'], '外交部表示，交流過程中，他們都恭賀蔡總統連任，並讚揚台灣人民透過此次選舉，向全世界傳達捍衛民主自由的堅定立場。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。'], [['經濟', '於南韓', '地區', '韓聯合新聞通訊社', '報導'], ['70', '14'], ['經濟', '地區', '報導'], '']], [[['耿爽', '長期', '眼鏡', '言論', '報告'], ['兩個'], ['長期', '眼鏡', '言論'], '耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。'], [[], [], [], ''], [['色列', '諸如沙', '聯合大公國等華府', '報導', '經濟'], ['今年'], ['色列', '報導', '經濟'], '「抵抗」是指阿拉伯人和伊朗人反擊美國、以色列及諸如沙烏地阿拉伯、阿拉伯聯合大公國等華府的阿拉伯盟友。《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。']], [[['協議', '階段', '雙方', '平盤', '美國總統川普及中國國務院'], ['00', '30', '凌晨'], ['協議', '階段', '雙方'], '美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。美國總統川普及中國國務院總理劉鶴，預計將在台北時間凌晨00:30正式在白宮簽署第1階段貿易協議，投資人正等待這場延續近2年的貿易戰達成階段性協議，也在觀望簽署後才會釋出的正式協議文本內容。'], [['經濟', '國際', '許勝雄', '企業', '會會'], ['2019', '三三', '3.4'], ['經濟', '國際', '企業'], ''], [['手機', '車電', '工業', '電腦', '事業'], ['2376', '33', '幾年'], ['手機', '車電', '工業'], '']], [[['協議', '森則', '風險', '價格', '交易量'], [], ['協議', '森則', '風險'], '英國首相強森則表示，2020完全脫歐是「勢在必行」但願意與歐盟進行友善的合作。分析師Douglas Paxman表示，除非英國、歐盟達成貿易協議，否則無協議脫歐風險無法消除，房產交易量和價格將因此受限。'], [['明仁', '經濟', '焦點', '地區', '父親'], ['50', '31', '59'], ['經濟', '焦點', '地區'], '在加入歐盟將近50年後，英國預定1月31日脫歐，並開始把外交和經濟關注焦點更轉移到世界其他地區。在父親明仁退位後，59歲的德仁去年5月1日登上「菊花寶座」（Chrysanthemum Throne）。'], [['貝倫堡銀行', '師史', '密丁', '經濟', '黃金'], ['未來', '10', '昨天'], ['師史', '密丁', '經濟'], "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。"]], [[['官證', '鏡周刊', '人位', '於柏林', '符騰堡'], ['一項', '今天'], ['官證', '鏡周刊', '人位'], '不過，檢察官證實明鏡周刊一項消息，即警方今天突襲搜查這3人位於柏林、布魯塞爾、德國巴伐利亞邦（Bavaria）及巴登符騰堡邦（Baden-Wuerttemberg）的住所和辦公室。」爆記者凌美雪／專題報導2020台北國際書展將於農曆年後（2月4日至9日）「閱讀新風景」，主辦單位台北書展基金會昨搶先公布書展重要活動與國內外展館亮點。'], [['協議', '規定', '核條款', '經濟', '難局'], ['去年', '目前'], ['協議', '規定', '核條款'], '自伊朗去年5月初開始逐步違反核協議規定，以回應美國正式落實其單方面的石油制裁後，英法德三國一直猶豫應否啟動此等程序；到伊朗聖城軍將領蘇萊曼尼（Qassem Soleimani）1月3日遇刺，伊朗決定不再遵守任何協議的核條款，三國才不得不作出回應。說到底，伊朗目前的經濟難局最終還是要靠美伊兩國解決，他國插手在短期內難有可見成果。'], [['明仁', '經濟', '焦點', '地區', '父親'], ['50', '31', '59'], ['經濟', '焦點', '地區'], '在加入歐盟將近50年後，英國預定1月31日脫歐，並開始把外交和經濟關注焦點更轉移到世界其他地區。在父親明仁退位後，59歲的德仁去年5月1日登上「菊花寶座」（Chrysanthemum Throne）。']], [[['海軍', '潛艦', '黃曙光', '國防大學', '參謀班'], ['63', '68', '82'], ['海軍', '潛艦', '參謀班'], ''], [['將士', '總長', '沈一鳴', '總士', '官長'], ['三項', '八位'], ['將士', '總長', '總士'], ''], [['總長', '海軍', '國防部', '海軍司', '黃曙光'], ['一級', '63', '68'], ['總長', '海軍', '參謀班'], '']]]
# link2=['UBN:https://udn.com/news/story/7270/4290578\nLTN:https://news.ltn.com.tw/news/sports/breakingnews/3041831', 'UBN:https://udn.com/news/story/7239/4290452\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041810', 'UBN:https://udn.com/news/story/7239/4290390\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813', 'UBN:https://udn.com/news/story/7241/4290457\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/6809/4290508\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/7331/4290090\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041810', 'UBN:https://udn.com/news/story/7327/4290510\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/12667/4289981\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813', 'UBN:https://udn.com/news/story/7327/4290510\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041809', 'UBN:https://udn.com/news/story/7331/4289954\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/120806/4290042\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:https://udn.com/news/story/7270/4290571\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041753', 'UBN:https://udn.com/news/story/7241/4290457\nLTN:https://news.ltn.com.tw/news/business/breakingnews/3041790', 'UBN:https://udn.com/news/story/6811/4290356\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3040882', 'UBN:https://udn.com/news/story/7243/4290405\nLTN:https://news.ltn.com.tw/news/business/breakingnews/3041134', 'UBN:https://udn.com/news/story/10930/4290137\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041829']
# summary2=['2020洛桑冬青奧混合國家奧會三對三冰球賽15日男、女子組金牌戰，中華小將林威宇所屬紅隊以4比10不敵綠隊，女子組張恩婗所屬黑隊以1比6輸給黃隊，皆收下銀牌這次洛桑冬青奧在冰球競賽新增三對三項目，每隊由13名不同國家的冰球選手組成，台灣共有2男3女參加此項目，其中就讀台北內湖高中的張恩婗與瑞士等國家選手組成女子黑隊，就讀台北美國學校的林威宇則與芬蘭等國家選手組成男子紅隊', '「偉人節」系列活動上，一名中國官員宣稱，毛澤東除了是偉大的領袖，也是神，而習近平新時代中國特色社會主義思想核心，就是要維護毛澤東的權威至高性，以傳承共產黨的紅色文化基因相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東', '券商公會理事長賀鳴珩投資眼光精準，對市場敏感度特別高，在2018年10月全球股市大跌時就獨排眾議，看好具高殖利率優勢的台股將走出「台灣行情」，事後果然被印證，在去年挑「高」字做為今年經濟關鍵字，認為台股還會續創新高，看來也會如他預期。台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。', '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。線上電商適合晚間下班無法逛街的消費者，之後線上也會有許多活動，將客人導到實體店。', '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。', '他表示，要看清歷史大勢，保持堅定信心，相信沒有任何力量能夠阻擋香港「一國兩制事業的步伐」。相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東。', '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。', '邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。」邱顯智指出，年改當初光落日條款就經過許多討論，而所謂「背信問題」也早經過大法官解釋處理，若民眾黨要再召開公聽會，時力會尊重，不過國民黨吳斯懷等人的訴求就是「把年改改回來」，他質疑，「讓一切回到原點，民眾黨又是否支持？', '總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。', '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。查瑞夫說，伊朗對外交有興趣，但沒興趣與美國協商；並說，現行核協議是他能想到的「最好協議」之一。', '當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。綜合媒體報導，1976年1月13日，16歲莫拉被發現陳屍路旁，死前一天她曾到麥當勞買飲料，自此再也沒有回家。', '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。', "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。", '《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。據《路透》報導，伊朗外交部長查里夫（Mohammad Javad Zarif）等伊朗官員已取消原定出席行程，對此，世界經濟論壇主席布倫德（BorgeBrende）週二於記者會上表示，在伊朗地區局勢不明朗的情況下，我們必須理解查里夫的缺席。', '現在一名疑似4名憲兵之1的人在臉書粉專投稿，指出這段時間受到大量酸民網路咒罵、霸凌，恐怕無法再承受這些言語壓力。他難過地表示，犧牲許多睡眠時間來練習儀態、擦亮甲鞋、調整甲服、拋光白盔，卻沒人看見，只因為這次事件，就換來許多咒罵，並痛苦說道「我真那麼低賤？」']
# keyword2=[[['冰球', '冬青奧', '林威宇', '紅隊', '國家'], ['15', '10', '三對'], ['冰球', '紅隊', '國家'], ''], [['毛澤東', '人節', '高性', '官員', '領袖'], ['12', '26', '一名'], ['人節', '高性', '官員'], ''], [['台股', '殖利率', '公會', '理事長', '賀鳴珩'], ['10', '萬點', '去年'], ['台股', '殖利率', '公會'], '券商公會理事長賀鳴珩投資眼光精準，對市場敏感度特別高，在2018年10月全球股市大跌時就獨排眾議，看好具高殖利率優勢的台股將走出「台灣行情」，事後果然被印證，在去年挑「高」字做為今年經濟關鍵字，認為台股還會續創新高，看來也會如他預期。台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。'], [['電商', '實體', '客人', '新光三越', '購物'], ['首家', '20', '30'], ['電商', '實體', '客人'], '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。線上電商適合晚間下班無法逛街的消費者，之後線上也會有許多活動，將客人導到實體店。'], [['吳敦義', '代工', '建議', '專心', '選黨'], ['一下', '目前'], ['代工', '建議', '專心'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。'], [['歷史', '大勢', '事業', '人節', '紀念'], ['12', '26', '去年'], ['歷史', '大勢', '事業'], '他表示，要看清歷史大勢，保持堅定信心，相信沒有任何力量能夠阻擋香港「一國兩制事業的步伐」。相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東。'], [['吳敦義', '代工', '建議', '專心', '選黨'], ['一下', '目前'], ['代工', '建議', '專心'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。'], [['邱顯智', '民眾', '黨立場', '輕言', '光落'], ['15', '多個', '當初'], ['民眾', '黨立場', '輕言'], '邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。」邱顯智指出，年改當初光落日條款就經過許多討論，而所謂「背信問題」也早經過大法官解釋處理，若民眾黨要再召開公聽會，時力會尊重，不過國民黨吳斯懷等人的訴求就是「把年改改回來」，他質疑，「讓一切回到原點，民眾黨又是否支持？'], [['民進黨', '總統', '蔡英文', '席立委', '國會'], ['61', '過半', '千萬'], ['總統', '國會', '民進黨'], '總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。'], [['主權', '國家', '人民', '民進黨', '秘書長'], ['未來', '過去', '2300'], ['主權', '國家', '人民'], '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['協議', '查瑞夫', '現行核', '伊朗', '外交部長'], ['今天'], ['協議', '現行核', '外交部長'], '伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。查瑞夫說，伊朗對外交有興趣，但沒興趣與美國協商；並說，現行核協議是他能想到的「最好協議」之一。'], [['技術', '帕梅拉', '綁架', '謎團', '辦案'], ['16', '當年', '近半世紀'], ['技術', '綁架', '謎團'], '當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。綜合媒體報導，1976年1月13日，16歲莫拉被發現陳屍路旁，死前一天她曾到麥當勞買飲料，自此再也沒有回家。'], [['新光三越', '購物', '電商', '重點', '實體'], ['首家', '20', '30'], ['購物', '電商', '重點'], '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。'], [['貝倫堡銀行', '師史', '密丁', '經濟', '黃金'], ['未來', '10', '昨天'], ['師史', '密丁', '經濟'], "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。"], [['報導', '經濟', '論壇', '總理', '馬林'], ['週二', '今年'], ['報導', '經濟', '論壇'], '《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。據《路透》報導，伊朗外交部長查里夫（Mohammad Javad Zarif）等伊朗官員已取消原定出席行程，對此，世界經濟論壇主席布倫德（BorgeBrende）週二於記者會上表示，在伊朗地區局勢不明朗的情況下，我們必須理解查里夫的缺席。'], [['時間', '白盔', '憲兵', '酸民', '網路'], ['許多', '現在', '一名'], ['時間', '白盔', '憲兵'], '現在一名疑似4名憲兵之1的人在臉書粉專投稿，指出這段時間受到大量酸民網路咒罵、霸凌，恐怕無法再承受這些言語壓力。他難過地表示，犧牲許多睡眠時間來練習儀態、擦亮甲鞋、調整甲服、拋光白盔，卻沒人看見，只因為這次事件，就換來許多咒罵，並痛苦說道「我真那麼低賤？」']]

# for i in range(11,len(STR1)):
#     print(STR1[i],STR2[i])
#     print(link[i])
#     print("摘要",summary[i])
#     print('關鍵',keyword[i])
# A=['UBN:https://udn.com/news/story/7331/4290474\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041578', 'UBN:https://udn.com/news/story/6809/4290069\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3038374', 'UBN:https://udn.com/news/story/7238/4290212\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041747']
# S=['蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。陸委會則呼籲中共首先正視中華民國是主權國家，台灣選舉結果是對未來台海情勢發展釋放堅定明確的信號，北京當局必須懂得尊重、勇敢面對現實。', '台灣總統大選甫落幕，歐洲議會今天在「共同外交暨安全政策」及「共同安全暨防禦政策」2項決議案中納入挺台條文，重申支持台灣參與國際組織。2020年總統暨立委選舉順利結束。選舉結果於昨晚確認後，美日兩國第一時間致賀，外交部今天並表示，目前已有超過60個國家或國際組織以賀電、賀函向我致賀，或政要透過社群網站、簡訊等方式，祝賀我國大選順利完成，也祝賀蔡總統順利連任。', '台積電表示，公司從未排除在美國設廠生產的可能性，只是目前尚無具體計畫，將依客戶需求考量。公司從未排除赴美國設廠生產的可能性，只是目前還沒有具體計畫。']
# K=[[['蔡總統', '北京當局', '馬曉光'], ['勝選之夜', '1/15'], ['兩岸', '國台辦'], '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。'], [['歐洲議會',"外交部","蔡總統"], ['1/15 1/12'], ['台灣',"歐洲"], '台灣總統大選甫落幕，歐洲議會今天在「共同外交暨安全政策」及「共同安全暨防禦政策」2項決議案中納入挺台條文，重申支持台灣參與國際組織。'], [['台積電'], ['1 15'], ['台灣 美國'], '台積電表示，公司從未排除在美國設廠生產的可能性。']]

# A1=['UBN:https://udn.com/news/story/7266/4290265\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041705', 'UBN:https://udn.com/news/story/7331/4289866\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/6811/4290397\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563']
# S1=['蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。陸委會則呼籲中共首先正視中華民國是主權國家，台灣選舉結果是對未來台海情勢發展釋放堅定明確的信號，北京當局必須懂得尊重、勇敢面對現實。', '北京當局必須懂得尊重、勇敢面對現實，更須深刻思考這段時間以來，其「一廂情願」與強制打壓都無法改變這個事實。陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。', '耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。']
# K1=[[['蔡總統', '北京當局', '馬曉光'], ['勝選之夜', '1/15'], ['兩岸', '國台辦'], '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。'], [['北京當局', '陸委會', '蔡總統'], ["1 15"], ["北京","台灣","兩岸"], '陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。'], [['耿爽', '中國 '], ['1 15'], ['中國', '美國'], '因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。']]

# A2=['UBN:https://udn.com/news/story/7331/4289954\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/7238/4290195\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041099', 'UBN:https://udn.com/news/story/7331/4289922\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041510']
# S2=['民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '許勝雄指出，目前看起來國、內外的經濟面都不錯，尤其美中要簽第1階段協議，另外美國總統選舉前不會有局勢大變化，全球市場信心可以穩定下來，只要世界好，台灣就一定好，台灣有充沛的人才、環境、國際化布局和國際誠信等條件，有雄厚的實力，樂觀看待2020年（經濟發展）三三會今天中午舉行1月份例會，三三會理事長許勝雄會前受訪表示，美中貿易戰將簽第1階段協議，全球市場信心可以穩定下來，台灣產業有雄厚實力、競爭力，只要世界經濟局勢好，台灣經濟表現就會向上', '「反滲透法」今日公布施行，陸委會表示，已會同內政部、外交部、法務部、中選會及海基會等相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討；未來法案如有研修的需求，將由所涉業管機關視情形領銜修法，再會銜其他機關，依一般法制作業程序來進行。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。']
# K2=[[['陸委會', '民進黨秘書長 羅文嘉'], ['1\15下午'], ['台灣', '中國'], '陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['三三會理事長許勝雄'], ['1 15', '三三會會前'], ['全球市場'], '三三會理事長許勝雄會前受訪表示，美中貿易戰將簽第1階段協議，全球市場信心可以穩定下來，台灣產業有雄厚實力、競爭力，只要世界經濟局勢好，台灣經濟表現就會向上'], [['陸委會', '內政部', '法務部', '海基會', '中選會'], ['1 15'], ['台灣'], '「反滲透法」今日公布施行，陸委會表示，已會同相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。']]

# A3=['UBN:https://udn.com/news/story/12667/4290460\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041310', 'UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041598', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749']
# S3=['國民黨在2020年總統、立委選舉中大敗，黨內青壯派出現捨棄「九二共識」的聲浪，主張統一立場鮮明的新黨主席郁慕明對此嗆聲，批評為了拿選票而「放棄中心思想」的行為就是「漢奸」。國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。', '2020大選落幕，台聯僅獲得0.3%政黨票，黨主席劉一德今天向中執會提出辭呈，但中執委全數不通過；劉一德即日起請假，思考個人未來，請假期間，黨主席職務由前立委周倪安代理。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」']
# K3=[[['國民黨', '新黨主席郁慕明'], ['1/15昨天'], ['國民黨內'], '國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。'], [['台灣團結聯盟 劉德一',], ['1/15下午'], ['中執會'], '台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。'], [['韓國瑜', '高雄市'], ['1/11今晚'], ['台灣', '高雄'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！']]

# A4=['UBN:https://udn.com/news/story/120932/4290486\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041821', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:https://stars.udn.com/star/story/10088/4283256\nLTN https://news.ltn.com.tw/news/politics/paper/1346152']
# S4=['蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」同時她也表示，中國若侵略台灣將付出很大的代價。這段訪問引發國際間注目，甚至登上美國知名社群媒體「Reddit」的熱門話題，有美國網友諷刺地留言說「台灣大陸（Mainland Taiwan）看到應該不太開心」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」', '于美人選前臨危授命成為總統候選人宋楚瑜發言人，昨天選舉結果出爐，宋陣營敗選，而于美人也卸下發言人身分，回歸日常，她昨深夜開直播分享心路歷程，她說一開始接下這工作，不少人企圖在她「失控廚房」的粉專混淆視聽，但她慶幸粉絲沒有被政治所操弄，她講到這裡忍不住哽咽，「因為我覺得大家太棒了，我們不讓政治干擾我們的生活，而我們做到了。」']
# K4=[[['蔡英文'], ['勝選後'], ['ＢＢＣ'], '蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」'], [['韓國瑜', '高雄市'], ['1/11今晚'], ['台灣', '高雄'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！'], [['宋楚瑜發言人 于美人'], ['1/12'], ['宋陣營'], '鑑於時代力量不分區立委當選人「小燈泡媽媽」王婉諭遭網友留言恐嚇，大選時擔任親民黨總統候選人宋楚瑜發言人的于美人，昨邀集總統大選各陣營發言人茶敘。']]

# link=[]
# summary=[]
# keyword=[]
# a1=['UBN:https://udn.com/news/story/7331/4290474\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041578', 'UBN:https://udn.com/news/story/6809/4290069\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3038374', 'UBN:https://udn.com/news/story/7238/4290212\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041747']
# b1=['蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。陸委會則呼籲中共首先正視中華民國是主權國家，台灣選舉結果是對未來台海情勢發展釋放堅定明確的信號，北京當局必須懂得尊重、勇敢面對現實。', '台灣總統大選甫落幕，歐洲議會今天在「共同外交暨安全政策」及「共同安全暨防禦政策」2項決議案中納入挺台條文，重申支持台灣參與國際組織。2020年總統暨立委選舉順利結束。選舉結果於昨晚確認後，美日兩國第一時間致賀，外交部今天並表示，目前已有超過60個國家或國際組織以賀電、賀函向我致賀，或政要透過社群網站、簡訊等方式，祝賀我國大選順利完成，也祝賀蔡總統順利連任。', '台積電表示，公司從未排除在美國設廠生產的可能性，只是目前尚無具體計畫，將依客戶需求考量。公司從未排除赴美國設廠生產的可能性，只是目前還沒有具體計畫。']
# c1=[[['蔡總統', '北京當局', '馬曉光'], ['勝選之夜', '1/15'], ['兩岸', '國台辦'], '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。'], [['歐洲議會',"外交部","蔡總統"], ['1/15 1/12'], ['台灣',"歐洲"], '台灣總統大選甫落幕，歐洲議會今天在「共同外交暨安全政策」及「共同安全暨防禦政策」2項決議案中納入挺台條文，重申支持台灣參與國際組織。'], [['台積電'], ['1\15'], ['台灣 美國'], '台積電表示，公司從未排除在美國設廠生產的可能性。']]

# a2=['UBN:https://udn.com/news/story/7266/4290265\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041705', 'UBN:https://udn.com/news/story/7331/4289866\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/6811/4290397\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563']
# b2=['蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。陸委會則呼籲中共首先正視中華民國是主權國家，台灣選舉結果是對未來台海情勢發展釋放堅定明確的信號，北京當局必須懂得尊重、勇敢面對現實。', '北京當局必須懂得尊重、勇敢面對現實，更須深刻思考這段時間以來，其「一廂情願」與強制打壓都無法改變這個事實。陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。', '耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。']
# c2=[[['蔡總統', '北京當局', '馬曉光'], ['勝選之夜', '1/15'], ['兩岸', '國台辦'], '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。'], [['北京當局', '陸委會', '蔡總統'], ["1 15"], ["北京","台灣","兩岸"], '陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。'], [['耿爽', '中國 '], ['1\15'], ['中國', '美國'], '因此這些涉華言論、報告，是在「罔顧事實、顛倒黑白，毫無客觀性可言，完全不值一駁」。']]

# a3=['UBN:https://udn.com/news/story/7331/4289954\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/7238/4290195\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041099', 'UBN:https://udn.com/news/story/7331/4289922\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041510']
# b3=['民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '許勝雄指出，目前看起來國、內外的經濟面都不錯，尤其美中要簽第1階段協議，另外美國總統選舉前不會有局勢大變化，全球市場信心可以穩定下來，只要世界好，台灣就一定好，台灣有充沛的人才、環境、國際化布局和國際誠信等條件，有雄厚的實力，樂觀看待2020年（經濟發展）三三會今天中午舉行1月份例會，三三會理事長許勝雄會前受訪表示，美中貿易戰將簽第1階段協議，全球市場信心可以穩定下來，台灣產業有雄厚實力、競爭力，只要世界經濟局勢好，台灣經濟表現就會向上', '「反滲透法」今日公布施行，陸委會表示，已會同內政部、外交部、法務部、中選會及海基會等相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討；未來法案如有研修的需求，將由所涉業管機關視情形領銜修法，再會銜其他機關，依一般法制作業程序來進行。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。']
# c3=[[['陸委會', '民進黨秘書長 羅文嘉'], ['1\15下午'], ['台灣', '中國'], '陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['三三會理事長許勝雄'], ['1\15', '三三會會前'], ['全球市場'], '三三會理事長許勝雄會前受訪表示，美中貿易戰將簽第1階段協議，全球市場信心可以穩定下來，台灣產業有雄厚實力、競爭力，只要世界經濟局勢好，台灣經濟表現就會向上'], [['陸委會', '內政部', '法務部', '海基會', '中選會'], ['1\15'], ['台灣'], '「反滲透法」今日公布施行，陸委會表示，已會同相關單位共同成立「因應反滲透法施行協調小組」，持續追蹤執法狀況並蒐整相關案例，進行滾動式檢討。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。']]

# a4=['UBN:https://udn.com/news/story/12667/4290460\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041310', 'UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041598', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749']
# b4=['國民黨在2020年總統、立委選舉中大敗，黨內青壯派出現捨棄「九二共識」的聲浪，主張統一立場鮮明的新黨主席郁慕明對此嗆聲，批評為了拿選票而「放棄中心思想」的行為就是「漢奸」。國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。', '2020大選落幕，台聯僅獲得0.3%政黨票，黨主席劉一德今天向中執會提出辭呈，但中執委全數不通過；劉一德即日起請假，思考個人未來，請假期間，黨主席職務由前立委周倪安代理。台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」']
# c4=[[['國民黨', '新黨主席郁慕明'], ['1/15昨天'], ['國民黨內'], '國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。'], [['台灣團結聯盟 劉德一',], ['1/15下午'], ['中執會'], '台灣團結聯盟下午召開中執會，劉一德在會中感謝夥伴選戰辛勞，他說，「大家都盡力了」，並提及「現行選制不利小黨」。'], [['韓國瑜', '高雄市'], ['1/11今晚'], ['台灣', '高雄'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！']]

# a5=['UBN:https://udn.com/news/story/120932/4290486\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041821', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:https://stars.udn.com/star/story/10088/4283256\nLTN https://news.ltn.com.tw/news/politics/paper/1346152']
# b5=['蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」同時她也表示，中國若侵略台灣將付出很大的代價。這段訪問引發國際間注目，甚至登上美國知名社群媒體「Reddit」的熱門話題，有美國網友諷刺地留言說「台灣大陸（Mainland Taiwan）看到應該不太開心」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」', '于美人選前臨危授命成為總統候選人宋楚瑜發言人，昨天選舉結果出爐，宋陣營敗選，而于美人也卸下發言人身分，回歸日常，她昨深夜開直播分享心路歷程，她說一開始接下這工作，不少人企圖在她「失控廚房」的粉專混淆視聽，但她慶幸粉絲沒有被政治所操弄，她講到這裡忍不住哽咽，「因為我覺得大家太棒了，我們不讓政治干擾我們的生活，而我們做到了。」']
# c5=[[['蔡英文'], ['勝選後'], ['ＢＢＣ'], '蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」'], [['韓國瑜', '高雄市'], ['1/11今晚'], ['台灣', '高雄'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！'], [['宋楚瑜發言人 于美人'], ['1/12'], ['宋陣營'], '鑑於時代力量不分區立委當選人「小燈泡媽媽」王婉諭遭網友留言恐嚇，大選時擔任親民黨總統候選人宋楚瑜發言人的于美人，昨邀集總統大選各陣營發言人茶敘。']]

# a6=['UBN:https://udn.com/news/story/12702/4289747\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040852', 'UBN:https://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/politics/paper/1345335', 'UBN:https://udn.com/news/story/6809/4288852\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040682']
# b6=['兩岸政策協會理事長譚耀南表示，以和平與對等方式處理兩岸歧見，正視中華民國的存在，對話也是要政府與政府之間對等坐下談，中華民國是台灣人民最大的公約數。台師大政研所教授范世平指出，昨天親中媒體社論談及，希望中共正視蔡英文總統1月11日的談話，且昨天香港中評社的快論，指兩岸關係更趨嚴峻，但並非完全無對話空間，這部分可看出一些端倪。', '風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。', '華府智庫「美國企業研究所」（American Enterprise Institute,AEI）研究員狄森（Marc Thiessen）曾任美國前總統小布希（George W. Bush）文膽，他目前兼任「華盛頓郵報」（Washington Post）專欄作家。他說，台美FTA不只可能促進美國經濟並提高出口，還能增加對中國壓力，並在美國國會獲得跨黨派支持。']
# c6=[[['兩岸政策協會理事長譚耀南', '台師大政研所'], ['1月11日'], ['台灣 中華民國'], '兩岸政策協會理事長譚耀南表示，以和平與對等方式處理兩岸歧見，正視中華民國的存在，對話也是要政府與政府之間對等坐下談，中華民國是台灣人民最大的公約數。'], [['李淳', '川普', '習政權', '蔡英文'], ['11月', '1 15'], ['台灣', '中國', '中華經濟研究院'], '中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。'], [['華府智庫研究員 狄森'], ['1 15'], ['華盛頓郵報', '台美ＦＴＡ'], '華府智庫研究員狄森說，台美FTA不只可能促進美國經濟並提高出口，還能增加對中國壓力，並在美國國會獲得跨黨派支持。']]

# a7=['UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041172', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:https://udn.com/news/story/7327/4289919\nLTNhttps://news.ltn.com.tw/news/life/breakingnews/3040233']
# b7=['國民黨主席吳敦義今天下午率相關黨務主管向中常會提出總辭，同時也就這次總統、立委選舉敗選原因提出檢討報告，其中羅列7大敗因，分別為「討厭民進黨」終不敵「亡國感」﹔兩岸論述未能掌握話語權，無法因應當下變局﹔惡質網軍帶領風向，候選人品牌形象飽受挑戰，難以爭取中間選民認同﹔高雄市長勝選模式無法複製，選戰策略選擇失誤﹔黨內矛盾不團結，輔選力道仍待加強﹔不分區名單未能符合外界期待﹔以及青年參與政治程度高，不受青年選民青睞。國民黨這份報告對於該黨總統候選人韓國瑜有諸多直白的檢討與質疑，包括在這次競選過程中，因為市長就職之後不到半年即宣布參選總統，無法彌平落跑市長的爭議，誠信問題受到質疑，而且過去在高雄市議會備詢跳針式回答、太平島挖石油、迪士尼到高雄、賽馬場、賽車場等極具話題性的政見逐一跳票，能力問題飽受懷疑，再加上失言、歧視語言、違規農舍、豪宅案、麻將照到新莊王小姐案等等事件，私德問題也備受考驗，庶民形象大大削減。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」', '市長韓國瑜敗選返回市府上班，未來他在議會定期大會面對民意監督還有一場硬仗，屆時定期大會的質詢將再成焦點。不過，時代力量市議員林于凱發布新聞稿質疑時程延到4月16日開議是要助韓國瑜躲質詢避出糗，疑與罷免案有關。']
# c7=[[['國民黨主席吳敦義'], ['今天（15號）下午'], ['中常會', '高雄'], '國民黨主席吳敦義今天下午率相關黨務主管向中常會提出總辭，同時也就這次總統、立委選舉敗選原因提出檢討報告，羅列7大敗因'], [['高雄市長韓國瑜'], ['今晚（11號）'], ['高雄市'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！'], [['市長韓國瑜', '時代力量市議員林于凱'], ['1 15', '4月16日'], ['市長', '議會', '大會面'], '市長韓國瑜敗選返回市府上班，未來他在議會定期大會面對民意監督還有一場硬仗，屆時定期大會的質詢將再成焦點。']]

# a8=['UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041396', 'UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041215', 'UBN:https://udn.com/news/story/12667/4289981\nLTNhttps://news.ltn.com.tw/news/entertainment/breakingnews/3041396']
# b8=['吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。', '儘管要求吳斯懷辭立委的浪潮如驚滔駭浪襲捲國民黨，但事實上，要求吳斯懷辭跟「會不會辭」是兩碼子事情。所以，是誰力保吳斯懷得免於外部壓力而辭去立委之職？', '吳斯懷列入不分區立委名單時外界曾質疑是否會洩露國家機密，也因此讓國民黨民調下滑。吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。']
# c8=[[['吳斯懷'], ['1 15'], ['國民黨', '中華民國'], '吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。'], [['吳斯懷'], ['1 15'], ['國民黨內'], '儘管要求吳斯懷辭立委的浪潮如驚滔駭浪襲捲國民黨，但事實上，要求吳斯懷辭跟「會不會辭」是兩碼子事情。'], [['吳斯懷'], ['1 15'], ['國民黨', '中華民國'], '吳斯懷強調，如果洩密的話，就把他「關進去，關到死」，一頓飯都不吃只喝水，表示不會對不起中華民國。']]

# a9=['UBN:https://udn.com/news/story/6809/4290069\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749', 'UBN:https://udn.com/news/story/120920/4289260\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040935', 'UBN:https://udn.com/news/story/12667/4290035\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041749']
# b9=['國民黨在2020年總統、立委選舉中大敗，黨內青壯派出現捨棄「九二共識」的聲浪，主張統一立場鮮明的新黨主席郁慕明對此嗆聲，批評為了拿選票而「放棄中心思想」的行為就是「漢奸」。國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。', '蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」同時她也表示，中國若侵略台灣將付出很大的代價。這段訪問引發國際間注目，甚至登上美國知名社群媒體「Reddit」的熱門話題，有美國網友諷刺地留言說「台灣大陸（Mainland Taiwan）看到應該不太開心」。', '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧今日韓國瑜表示，他將回歸市政，至於謝票行程，韓國瑜表示，「等各位歡喜過完金鼠年後，會在市政之餘，安排向大家謝票感謝惜福的行程」']
# c9=[[['國民黨', '新黨主席郁慕明'], ['1/15昨天'], ['國民黨內'], '國民黨昨天針對二○二○總統及立委選舉敗選提出檢討報告，臚列七大原因。'], [['蔡英文'], ['勝選後'], ['ＢＢＣ'], '蔡英文總統勝選後接受英國廣播公司（ＢＢＣ）專訪，她表示，「我們已經是一個獨立的國家，我們稱自己是中華民國（台灣）（Republic of China （Taiwan））。」'], [['韓國瑜', '高雄市'], ['1/11今晚'], ['台灣', '高雄'], '總統大選結束，高雄市長韓國瑜回歸市政，今晚他在臉書以「回歸生活，攜手向前」為題發文表示，他理解大家失落的心情，但選舉是一時、團結向前走才是一世，擦乾眼淚後就抬頭望向天空，為這片土地一起努力吧！']]

# a10=['UBN:https://udn.com/news/story/7331/4289954\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/7331/4289866\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041578', 'UBN:https://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/opinion/breakingnews/3039159']
# b10=['民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。陸委會強調，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。', '風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。']
# c10=[[['中共', '陸委會', "民進黨秘書長 羅文嘉"], ['今天下午'], ['台灣'], "民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。"], [["陸委會", "北京當局", "蔡總統"], ["1 15"], ["兩岸"], "陸委會指出，北京當局應理性思考蔡總統提出「和平、對等、民主、對話」的兩岸互動關鍵基礎，才是真正有利於各自發展與人民福祉。"], [["蔡英文", "北京當局", "川普政府"], ["1 15", "11月"], ["台海"], "風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。"]]

# a11=['UBN:https://udn.com/news/story/6839/4288827\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:https://udn.com/news/story/6656/4289952\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041510', 'UBN:https://udn.com/news/story/6809/4288539\nLTNhttps://news.ltn.com.tw/news/politics/paper/1346147']
# b11=['風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。中華經濟研究院WTO及RTA中心副執行長李淳指出，川普政府一向務實且重視農業州選民利益，先前與歐盟、日、韓談判時，都將農產品開放列為優先項目，美國將於11月舉行總統大選，確實可能要求台灣先放寬對美牛、美豬的進口限制，再商討實質議題。', '外交部表示，交流過程中，他們都恭賀蔡總統連任，並讚揚台灣人民透過此次選舉，向全世界傳達捍衛民主自由的堅定立場。中共方面一再惡意扭曲、混淆視聽，意圖對我分化離間，只會讓臺灣人民更加反感，也無助於兩岸關係正面發展。', '至於美國是否在會談中要求南韓派兵荷莫茲海峽一事，康京和表示，美方一直認為與荷莫茲海峽存在經濟利害關係的國家都應做出貢獻，鑑於南韓70%的原油進口依賴該地區，應該對此予以關注南韓。康京和於美國時間14日在舊金山與美國、日本兩國外長舉行雙邊和三邊會談後，會見媒體記者時做上述表示']
# c11=[[['蔡英文', '北京當局', '川普政府'], ['1 15', '11月'], ['台海'], '風險 習政權內外交迫 恐升高台海緊張當台灣民眾明確透過手中選票，拒絕中國的併吞意圖，蔡英文也在勝選記者會上以「和平、對等、民主、對話」四項概念，向北京當局喊話，期望兩岸人民能夠互惠互利、拉近距離。'], [['外交部', '蔡總統', '中共', '台灣人民'], ['1 15'], ['台灣'], '外交部表示，交流過程中，他們都恭賀蔡總統連任，並讚揚台灣人民透過此次選舉，向全世界傳達捍衛民主自由的堅定立場。'], [['美國', '南韓', '康京'], ['美國時間14日'], ['舊金山', '荷莫茲海峽'], '至於美國是否在會談中要求南韓派兵荷莫茲海峽一事，康京和表示，美方一直認為與荷莫茲海峽存在經濟利害關係的國家都應做出貢獻，鑑於南韓70%的原油進口依賴該地區，應該對此予以關注南韓。']] 

# a12=['UBN:https://udn.com/news/story/7331/4283635\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:https://udn.com/news/story/7238/4290212\nLTNhttps://news.ltn.com.tw/news/life/breakingnews/3041745', 'UBN:https://udn.com/news/story/6809/4290177\nLTNhttps://news.ltn.com.tw/news/world/paper/1346189']
# b12=['國際人權組織「人權觀察」、「自由之家」今日發表的今年世界人權報告中皆指出，中國人權意識嚴重低落。耿爽宣稱，以上兩個組織，長期以來一直戴著「有色眼鏡」看待中國。', '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。陸委會則呼籲中共首先正視中華民國是主權國家，台灣選舉結果是對未來台海情勢發展釋放堅定明確的信號，北京當局必須懂得尊重、勇敢面對現實。', '「抵抗」是指阿拉伯人和伊朗人反擊美國、以色列及諸如沙烏地阿拉伯、阿拉伯聯合大公國等華府的阿拉伯盟友。龐皮歐表示，威嚇力的重要性不限於伊朗，美國為了捍衛自由，也會威嚇中國和俄羅斯等其他敵國。']
# c12=[[['耿爽'], ['1 15'], ['中國'], '國際人權組織「人權觀察」、「自由之家」今日發表的今年世界人權報告中皆指出，中國人權意識嚴重低落。'], [['蔡總統', '北京當局', '馬曉光'], ['勝選之夜', '1/15'], ['兩岸', '國台辦'], '蔡英文總統連任後向大陸提出「和平、對等、民主、對話」，稱這八個字是兩岸重啟良性互動、長久穩定發展的關鍵，大陸國台辦發言人馬曉光昨天以四點回應，強調兩岸須堅持「九二共識」的共同政治基礎，「撼山易，撼『九二共識』難」。'], [['龐皮歐'], ['1 13'], ['以色列'], '龐皮歐表示，威嚇力的重要性不限於伊朗，美國為了捍衛自由，也會威嚇中國和俄羅斯等其他敵國。']]

# a13=['UBN:https://udn.com/news/story/6811/4290397\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041790', 'UBN:https://udn.com/news/story/7238/4289218\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041609', 'UBN:https://udn.com/news/story/7238/4289849\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3041604']
# b13=['美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。美國總統川普及中國國務院總理劉鶴，預計將在台北時間凌晨00:30正式在白宮簽署第1階段貿易協議，投資人正等待這場延續近2年的貿易戰達成階段性協議，也在觀望簽署後才會釋出的正式協議文本內容。', '許勝雄今天於三三企業交流會會前受訪時表示，全世界經濟上來了，台灣經濟必然可以上來，國際預測機構估2019年全球經濟成長率落在3%左右、2020年有機會達3.4%，台灣經濟受惠於美中貿易戰帶來台商回流、國際企業赴台投資，國內也有政府投資與消費，據主計總處預測，2020年經濟成長率為2.72%，優於2019年的2.64%此外，許勝雄指出，政府應積極爭取加入跨太平洋夥伴全面進步協定（CPTPP）、區域全面經濟夥伴關係協定（RCEP），以及簽訂更多自由貿易協定（FTA），這是攸關台灣國際競爭力的重要議題，否則和韓國、越南、新加坡相比，台灣招商引資的力度會被弱化', '技嘉（2376）已經成立 33年，近幾年公司內逐步啟動世代交替，也嘗試通路、手機、車電、工業電腦等新事業，董事長葉培城說，「我們創辦的這一代，說年輕不年輕、說老不老，公司也要做主機板以外的事，有一些新產品、市場趨勢也需要新思維，像之前做手機的時候，都叫他們（下屬）不要問我因為我的使用習慣可能跟不一樣，怕誤導他們，這種事一定要讓中生代進來」未來兩岸，林伯豐認為，蔡英文總統連任，第二任的任期空間相對寬闊，也有很多選擇，她要怎麼選，大陸要怎麼回應，雙邊都要有智慧，對方能接受什麼、台灣能接受什麼，都有了解在，這就是願不願意做，做的結果是對台灣好還是不好要好好判斷']
# c13=[[['美國總統川普及中國國務院總理劉鶴'], ['台北時間凌晨00:30'], ['白宮'], '美國總統川普及中國國務院總理劉鶴，預計將在台北時間凌晨00:30正式在白宮簽署第1階段貿易協議，投資人正等待這場延續近2年的貿易戰達成階段性協議，也在觀望簽署後才會釋出的正式協議文本內容。'], [['許勝雄'], ['2019', '2020', '1 15今日'], ['台灣', '國內'], '許勝雄指出，政府應積極爭取加入跨太平洋夥伴全面進步協定（CPTPP）、區域全面經濟夥伴關係協定（RCEP），以及簽訂更多自由貿易協定（FTA），這是攸關台灣國際競爭力的重要議題，否則和韓國、越南、新加坡相比，台灣招商引資的力度會被弱化'], [['技嘉董事長葉培城', '林伯豐', '蔡英文'], ['1 15'], ['兩岸', '台灣'], '林伯豐認為，蔡英文總統連任，第二任的任期空間相對寬闊，也有很多選擇，她要怎麼選，大陸要怎麼回應，雙邊都要有智慧，對方能接受什麼、台灣能接受什麼，都有了解在，這就是願不願意做，做的結果是對台灣好還是不好要好好判斷']]

# a14=['UBN:https://udn.com/news/story/6809/4277736\nLTNhttps://news.ltn.com.tw/news/business/breakingnews/3039957', 'UBN:https://udn.com/news/story/6809/4287960\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3035532', 'UBN:https://udn.com/news/story/6811/4290356\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882']
# b14=['英國首相強森則表示，2020完全脫歐是「勢在必行」但願意與歐盟進行友善的合作。對於脫歐現況，Whitten指出，英國首相強森（Boris Johnson）已排除了無協議硬脫歐的可能性，讓企業和消費者都更加樂觀。英國下議院則已在本月10日通過「脫歐協議法案」（Withdrawal Agreement Bill），若立法程序完成，英國將於1月31日脫歐。', '英國官員今天宣布，日皇德仁接受英國女王伊麗莎白二世邀請，將在未來幾個月內前往英國進行國是訪問，並成為英國脫歐後的首場國是訪問。英國下議院今天以330票贊成、231票反對，多達99票優勢通過脫歐法案，下週將送往上議院，完成接下來的立法程序，確定於1月31日與歐洲聯盟分手。', '貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。']
# c14=[[['強森', 'Whitten'], ['1月31日'], ['英國', '英國下議院', '歐盟'], '英國首相強森則表示，2020完全脫歐是「勢在必行」但願意與歐盟進行友善的合作。'], [['德仁', '伊麗莎白二世'], ['1 10], ["英國下議院"], "英國下議院今天以330票贊成、231票反對，多達99票優勢通過脫歐法案，下週將送往上議院，完成接下來的立法程序，確定於1月31日與歐洲聯盟分手。"], [["貝倫堡銀行（Berenberg bank）分析師史密丁'], ['1 12昨天'], ['德國', '歐元區'], "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。"]]

# a15=['UBN:https://udn.com/news/story/6813/4290687\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040421 ', 'UBN:https://udn.com/news/story/120806/4289971\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882', 'UBN:https://udn.com/news/story/6809/4287960\nLTNhttps://news.ltn.com.tw/news/world/breakingnews/3040882']
# b15=['英國、法國、德國等歐洲強國今（14）日宣布，將啟動2015年《伊朗核協議》中的糾紛調解機制，限期各締約方15日內達成共識，這是歐洲自伊朗收回核武承諾後，所採取最大動作的回應。正式啟動核協議的爭端解決機制後，等於正式指控伊朗違反協議條款，並且可能促使聯合國重新啟動對伊朗的制裁。', '美、英、法、德、俄、中6國及歐盟於2015年與伊朗達成核子協議，伊朗承諾限制發展核武，換取各國解除對伊朗的制裁。但川普於2017年上任後對伊朗轉趨強硬，繼而於2018年退出協議，恢復對伊朗的制裁，伊朗則接連違反核子協議承諾。', '英國官員今天宣布，日皇德仁接受英國女王伊麗莎白二世邀請，將在未來幾個月內前往英國進行國是訪問，並成為英國脫歐後的首場國是訪問。英國下議院今天以330票贊成、231票反對，多達99票優勢通過脫歐法案，下週將送往上議院，完成接下來的立法程序，確定於1月31日與歐洲聯盟分手。']
# c15=[[['英國、法國、德國等歐洲強國'], ['今（14）日'], ['歐洲'], '正式啟動核協議的爭端解決機制後，等於正式指控伊朗違反協議條款，並且可能促使聯合國重新啟動對伊朗的制裁。'], [['川普'], ['1 15'], ['歐盟'], '但川普於2017年上任後對伊朗轉趨強硬，繼而於2018年退出協議，恢復對伊朗的制裁，伊朗則接連違反核子協議承諾。'], [['德仁', '伊麗莎白二世'], ['1 10'], ["英國下議院"], '英國下議院今天以330票贊成、231票反對，多達99票優勢通過脫歐法案，下週將送往上議院，完成接下來的立法程序，確定於1月31日與歐洲聯盟分手。']]

# a16=['UBN:https://udn.com/news/story/10930/4290137\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3040949', 'UBN:https://udn.com/news/story/10930/4288283\nLTNhttps://news.ltn.com.tw/news/politics/paper/1346135', 'UBN:https://udn.com/news/story/10930/4290137\nLTNhttps://news.ltn.com.tw/news/politics/breakingnews/3041493']
# b16=['今年63歲的黃曙光為明天將接任參謀總長，軍方人士指出，潛艦國造政策推行多年，但在總統蔡英文上任以後才真正大有進展，除了黃曙光本身實事求是、按部就班的行事風格外，由於曾任國軍潛艦要職，加上軍事歷練豐富，也具有令人服氣的領導風格，因此脫穎而出，以黃任職司令期間推動的潛艦計畫，未來對於潛艦國造是一大助力', '國防部昨舉行參謀總長沈一鳴、總士官長韓正宏等八位黑鷹直升機失事殉職將士的聯合公奠典禮，蔡英文總統親自頒授獎章、追晉官階及頒贈褒揚令給將士家屬，致詞時並宣布行政院已核定通過士官長專業加給、空降特戰勤務加給及飛行軍官續服獎助金等三項國軍加給', '國防部今天宣布新總長人事案，由上將之中期別最資深的海軍司令黃曙光上將接任']
# c16=[[['蔡英文', '黃曙光'], ['蔡英文上任以後'], ['國防部'], '除了黃曙光本身實事求是、按部就班的行事風格外，由於曾任國軍潛艦要職，加上軍事歷練豐富，也具有令人服氣的領導風格，因此脫穎而出'], [['蔡英文', '沈一鳴', '韓正宏'], ['1 13'], ['國防部'], '國防部昨舉行參謀總長沈一鳴、總士官長韓正宏等八位黑鷹直升機失事殉職將士的聯合公奠典禮，蔡英文總統親自頒授獎章、追晉官階及頒贈褒揚令給將士家屬'], [['黃曙光'], ['1 14'], ['國防部'], '國防部今天宣布新總長人事案，由上將之中期別最資深的海軍司令黃曙光上將接任']]

# link.append(a1)
# link.append(a2)
# link.append(a3)
# link.append(a4)
# link.append(a5)
# link.append(a6)
# link.append(a7)
# link.append(a8)
# link.append(a9)
# link.append(a10)
# link.append(a11)
# link.append(a12)
# link.append(a13)
# link.append(a14)
# link.append(a15)
# link.append(a16)
# summary.append(b1)
# summary.append(b2)
# summary.append(b3)
# summary.append(b4)
# summary.append(b5)
# summary.append(b6)
# summary.append(b7)
# summary.append(b8)
# summary.append(b9)
# summary.append(b10)
# summary.append(b11)
# summary.append(b12)
# summary.append(b13)
# summary.append(b14)
# summary.append(b15)
# summary.append(b16)
# keyword.append(c1)
# keyword.append(c2)
# keyword.append(c3)
# keyword.append(c4)
# keyword.append(c5)
# keyword.append(c6)
# keyword.append(c7)
# keyword.append(c8)
# keyword.append(c9)
# keyword.append(c10)
# keyword.append(c11)
# keyword.append(c12)
# keyword.append(c13)
# keyword.append(c14)
# keyword.append(c15)
# keyword.append(c16)
# print(link)
# print(summary)
# print(keyword)

# link2=['UBN:https://udn.com/news/story/7270/4290578\nLTN:https://news.ltn.com.tw/news/sports/breakingnews/3041831', 'UBN:https://udn.com/news/story/7239/4290452\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041810', 'UBN:https://udn.com/news/story/7239/4290390\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813', 'UBN:https://udn.com/news/story/7241/4290457\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/6809/4290508\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/7331/4290090\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041810', 'UBN:https://udn.com/news/story/7327/4290510\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819', 'UBN:https://udn.com/news/story/12667/4289981\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813', 'UBN:https://udn.com/news/story/7327/4290510\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041809', 'UBN:https://udn.com/news/story/7331/4289954\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041730', 'UBN:https://udn.com/news/story/120806/4290042\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041563', 'UBN:https://udn.com/news/story/7270/4290571\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3041753', 'UBN:https://udn.com/news/story/7241/4290457\nLTN:https://news.ltn.com.tw/news/business/breakingnews/3041790', 'UBN:https://udn.com/news/story/6811/4290356\nLTN:https://news.ltn.com.tw/news/world/breakingnews/3040882', 'UBN:https://udn.com/news/story/7243/4290405\nLTN:https://news.ltn.com.tw/news/business/breakingnews/3041134', 'UBN:https://udn.com/news/story/10930/4290137\nLTN:https://news.ltn.com.tw/news/politics/breakingnews/3041829']
# summary2=['圖／取自IG爆〔中央社〕2020洛桑冬青奧混合國家奧會三對三冰球賽15日男、女子組金牌戰，中華小將林威宇所屬紅隊以4比10不敵綠隊，女子組張恩婗所屬黑隊以1比6輸給黃隊，皆收下銀牌這次洛桑冬青奧在冰球競賽新增三對三項目，每隊由13名不同國家的冰球選手組成，台灣共有2男3女參加此項目，其中就讀台北內湖高中的張恩婗與瑞士等國家選手組成女子黑隊，就讀台北美國學校的林威宇則與芬蘭等國家選手組成男子紅隊', '「偉人節」系列活動上，一名中國官員宣稱，毛澤東除了是偉大的領袖，也是神，而習近平新時代中國特色社會主義思想核心，就是要維護毛澤東的權威至高性，以傳承共產黨的紅色文化基因相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東', '券商公會理事長賀鳴珩投資眼光精準，對市場敏感度特別高，在2018年10月全球股市大跌時就獨排眾議，看好具高殖利率優勢的台股將走出「台灣行情」，事後果然被印證，在去年挑「高」字做為今年經濟關鍵字，認為台股還會續創新高，看來也會如他預期。台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。', '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。線上電商適合晚間下班無法逛街的消費者，之後線上也會有許多活動，將客人導到實體店。', '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。', '他表示，要看清歷史大勢，保持堅定信心，相信沒有任何力量能夠阻擋香港「一國兩制事業的步伐」。相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東。', '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。', '邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。」邱顯智指出，年改當初光落日條款就經過許多討論，而所謂「背信問題」也早經過大法官解釋處理，若民眾黨要再召開公聽會，時力會尊重，不過國民黨吳斯懷等人的訴求就是「把年改改回來」，他質疑，「讓一切回到原點，民眾黨又是否支持？', '總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。', '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。', '伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。查瑞夫說，伊朗對外交有興趣，但沒興趣與美國協商；並說，現行核協議是他能想到的「最好協議」之一。', '當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。綜合媒體報導，1976年1月13日，16歲莫拉被發現陳屍路旁，死前一天她曾到麥當勞買飲料，自此再也沒有回家。', '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。', "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。", '《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。據《路透》報導，伊朗外交部長查里夫（Mohammad Javad Zarif）等伊朗官員已取消原定出席行程，對此，世界經濟論壇主席布倫德（BorgeBrende）週二於記者會上表示，在伊朗地區局勢不明朗的情況下，我們必須理解查里夫的缺席。', '現在一名疑似4名憲兵之1的人在臉書粉專投稿，指出這段時間受到大量酸民網路咒罵、霸凌，恐怕無法再承受這些言語壓力。他難過地表示，犧牲許多睡眠時間來練習儀態、擦亮甲鞋、調整甲服、拋光白盔，卻沒人看見，只因為這次事件，就換來許多咒罵，並痛苦說道「我真那麼低賤？']
# keyword2=[[['冰球', '冬青奧', '林威宇', '紅隊', '國家'], ['15', '10', '三對'], ['冰球', '紅隊', '國家'], ''], [['毛澤東', '人節', '高性', '官員', '領袖'], ['12', '26', '一名'], ['人節', '高性', '官員'], ''], [['台股', '殖利率', '公會', '理事長', '賀鳴珩'], ['10', '萬點', '去年'], ['台股', '殖利率', '公會'], '券商公會理事長賀鳴珩投資眼光精準，對市場敏感度特別高，在2018年10月全球股市大跌時就獨排眾議，看好具高殖利率優勢的台股將走出「台灣行情」，事後果然被印證，在去年挑「高」字做為今年經濟關鍵字，認為台股還會續創新高，看來也會如他預期。台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。'], [['電商', '實體', '客人', '新光三越', '購物'], ['首家', '20', '30'], ['電商', '實體', '客人'], '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。線上電商適合晚間下班無法逛街的消費者，之後線上也會有許多活動，將客人導到實體店。'], [['吳敦義', '代工', '建議', '專心', '選黨'], ['一下', '目前'], ['代工', '建議', '專心'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。'], [['歷史', '大勢', '事業', '人節', '紀念'], ['12', '26', '去年'], ['歷史', '大勢', '事業'], '他表示，要看清歷史大勢，保持堅定信心，相信沒有任何力量能夠阻擋香港「一國兩制事業的步伐」。相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東。'], [['吳敦義', '代工', '建議', '專心', '選黨'], ['一下', '目前'], ['代工', '建議', '專心'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。'], [['邱顯智', '民眾', '黨立場', '輕言', '光落'], ['15', '多個', '當初'], ['民眾', '黨立場', '輕言'], '邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。」邱顯智指出，年改當初光落日條款就經過許多討論，而所謂「背信問題」也早經過大法官解釋處理，若民眾黨要再召開公聽會，時力會尊重，不過國民黨吳斯懷等人的訴求就是「把年改改回來」，他質疑，「讓一切回到原點，民眾黨又是否支持？'], [['民進黨', '總統', '蔡英文', '席立委', '國會'], ['61', '過半', '千萬'], ['總統', '國會', '民進黨'], '總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。'], [['主權', '國家', '人民', '民進黨', '秘書長'], ['未來', '過去', '2300'], ['主權', '國家', '人民'], '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。'], [['協議', '查瑞夫', '現行核', '伊朗', '外交部長'], ['今天'], ['協議', '現行核', '外交部長'], '伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。查瑞夫說，伊朗對外交有興趣，但沒興趣與美國協商；並說，現行核協議是他能想到的「最好協議」之一。'], [['技術', '帕梅拉', '綁架', '謎團', '辦案'], ['16', '當年', '近半世紀'], ['技術', '綁架', '謎團'], '當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。綜合媒體報導，1976年1月13日，16歲莫拉被發現陳屍路旁，死前一天她曾到麥當勞買飲料，自此再也沒有回家。'], [['新光三越', '購物', '電商', '重點', '實體'], ['首家', '20', '30'], ['購物', '電商', '重點'], '新光三越購物電商「美麗台」線上和線下整合，也是今年發展重點，目標是20至30歲的客人；他說，3月將針對美麗台開出首家實體店，今年至少會開出三家，首家將位於台中中港店內，販售的商品和一般美妝專櫃會有50％得不同。美中雙方即將在今天稍晚正式簽署第1階段貿易協議，投資人等待進一步消息，美股開盤維持平盤。'], [['貝倫堡銀行', '師史', '密丁', '經濟', '黃金'], ['未來', '10', '昨天'], ['師史', '密丁', '經濟'], "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。"], [['報導', '經濟', '論壇', '總理', '馬林'], ['週二', '今年'], ['報導', '經濟', '論壇'], '《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。據《路透》報導，伊朗外交部長查里夫（Mohammad Javad Zarif）等伊朗官員已取消原定出席行程，對此，世界經濟論壇主席布倫德（BorgeBrende）週二於記者會上表示，在伊朗地區局勢不明朗的情況下，我們必須理解查里夫的缺席。'], [['時間', '白盔', '憲兵', '酸民', '網路'], ['許多', '現在', '一名'], ['時間', '白盔', '憲兵'], '現在一名疑似4名憲兵之1的人在臉書粉專投稿，指出這段時間受到大量酸民網路咒罵、霸凌，恐怕無法再承受這些言語壓力。他難過地表示，犧牲許多睡眠時間來練習儀態、擦亮甲鞋、調整甲服、拋光白盔，卻沒人看見，只因為這次事件，就換來許多咒罵，並痛苦說道「我真那麼低賤？']]

# for i in range(0,len(STR1)):
#     print(STR1[i])
#     print(link2[i])
#     print(summary2[i])
#     print(keyword2[i])    


link=[]
summary=[]
keyword=[]

a1="UBN: https://udn.com/news/story/7331/4289954\nLTN: https://news.ltn.com.tw/news/politics/breakingnews/3042844"
b1="大陸國台辦今（15）日舉行例行記者會，全場聚焦陸方如何解讀台灣大選的結果，陸委會傍晚表示，台灣從來都不是中華人民共和國的一部分，台灣前途只有台灣2,300萬人民有權決定。台灣總統大選落幕，美國智庫戰略暨國際研究中心（CSIS）亞洲事務資深顧問葛來儀（Bonnie Glaser）日前提到，她不認為中國除了對台動武外無選擇，未來4年對台會加大政治、經濟、軍事壓力，她今天（16日）接受媒體電訪指出，武統不是習近平近期目標，而中方希望民進黨下次落敗，所以接下來會尋找潛在合作對象，可能來自國民黨或是柯文哲、郭台銘。"
c1=[['陸委會', '美國智庫戰略暨國際研究中心（CSIS）亞洲事務資深顧問葛來儀'], ['今（15）日'], ['中國', '台灣'], '大陸國台辦今（15）日舉行例行記者會，全場聚焦陸方如何解讀台灣大選的結果，陸委會傍晚表示，台灣從來都不是中華人民共和國的一部分，台灣前途只有台灣2,300萬人民有權決定。']

a2="UBN:https://udn.com/news/story/7239/4290452LTN:https://news.ltn.com.tw/news/world/breakingnews/3041810"
b2="「偉人節」系列活動上，一名中國官員宣稱，毛澤東除了是偉大的領袖，也是神，而習近平新時代中國特色社會主義思想核心，就是要維護毛澤東的權威至高性，以傳承共產黨的紅色文化基因相關影片請見中國江西省上饒市市民在去年12月26日的「偉人節」系列活動上獻舞，以紀念毛澤東"
c2=[['毛澤東', '習近平 '], ['12月26日 偉人節 '], ['中國江西省上饒市'], '毛澤東除了是偉大的領袖，也是神，而習近平新時代中國特色社會主義思想核心，就是要維護毛澤東的權威至高性']

a3="UBN:https://udn.com/news/story/7239/4290390LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813"
b3="券商公會理事長賀鳴珩投資眼光精準，對市場敏感度特別高，在2018年10月全球股市大跌時就獨排眾議，看好具高殖利率優勢的台股將走出「台灣行情」，事後果然被印證，在去年挑「高」字做為今年經濟關鍵字，認為台股還會續創新高，看來也會如他預期。台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。"
c3=[['券商公會理事長賀鳴珩'], ['今年'], ['台股', '殖利率', '公會'], '台股在金豬年開紅盤後重返萬點，至今未曾再跌破，吸引外資回補的主因之一就是高殖利率。']

a4="UBN: https://udn.com/news/story/12667/4287849\nLTN: https://news.ltn.com.tw/news/politics/breakingnews/3042948"
b4="國民黨立委陳學聖突破盲腸說，拿掉黨名「中國」兩字已討論過很多次，民進黨沒在黨名加「台灣」，大家一樣認為是本土政黨；新黨沒加「中國」，卻被大家覺得是統派，證明有沒有冠上這兩個字不重要，重要的是黨的內涵。民黨在2020選戰中大敗，同樣在本次選戰中爭取立委連任失利的陳學聖表示，這次大選他就是要看韓國瑜的選情，「他起來，我就起來；他沒起來，我也掛了」。"
c4=[['國民黨立委陳學聖', '韓國瑜'], ['1 17', '1 14'], ['台灣'], '國民黨立委陳學聖突破盲腸說，拿掉黨名「中國」兩字已討論過很多次，民進黨沒在黨名加「台灣」，大家一樣認為是本土政黨；新黨沒加「中國」，卻被大家覺得是統派，證明有沒有冠上這兩個字不重要，重要的是黨的內涵。']

a5="UBN:https://udn.com/news/story/6809/4290508LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819"
b5="謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。"
c5=[['國民黨', '前主席吳敦義', '謝金河'], ['選後'], ['高雄'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。']

a6="UBN: https://udn.com/news/story/12667/4291690\nLTN: https://news.ltn.com.tw/news/politics/breakingnews/3042571"
b6="台北市議員戴錫欽、李明賢、李柏毅、張斯綱昨前往馬英九基金會拜訪馬前總統，向馬英九請教「92共識」的真正內涵，以及日後有沒有調整的空間。馬英九認為，92共識不是不能調整，但是怎麼調整都必須符合中華民國憲法、民意支持，以及北京方面能夠接受做為雙方交流的共識，還有國際能夠理解等四個前提，賦予92共識新意涵。"
c6=[['台北市議員戴錫欽、李明賢、李柏毅、張斯綱', '馬英九'], ['1 15'], ['台灣', '北京'], '馬英九認為，92共識不是不能調整，但是怎麼調整都必須符合中華民國憲法、民意支持，以及北京方面能夠接受做為雙方交流的共識，還有國際能夠理解等四個前提，賦予92共識新意涵。']

a7="UBN:https://udn.com/news/story/7327/4290510LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041819"
b7="謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。至於國民黨剛辭職的前主席吳敦義，謝金河則直言「吳敦義該退休，有點老年癡呆症了」；而過去在初選對決韓國瑜的鴻海創辦人郭台銘，謝金河則直呼郭是這次輸最慘的，幫親民黨助選卻無法過5％門檻，他認為，郭要選總統時很有氣勢，但後來一下找民眾黨、一下找親民黨，就像代工找客戶，「代工政治」沒有中心思想。"
c7=[['國民黨', '前主席吳敦義', '謝金河'], ['選後'], ['高雄'], '謝金河建議，韓國瑜目前應該要顧好高雄，專心在市政上，「若去選黨主席一定會被罷免」。']

a8="UBN:https://udn.com/news/story/12667/4289981LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041813"
b8="邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。」邱顯智指出，年改當初光落日條款就經過許多討論，而所謂「背信問題」也早經過大法官解釋處理，若民眾黨要再召開公聽會，時力會尊重，不過國民黨吳斯懷等人的訴求就是「把年改改回來」，他質疑，「讓一切回到原點，民眾黨又是否支持？"
c8=[['邱顯智', '民眾黨', '國民黨吳斯懷'], ['15日'], ['台灣'], '邱顯智15日再度說明想法，舉出多個不清楚民眾黨立場的例子，要求「與其輕言聯盟，不如就事論事」。']

a9="UBN: https://udn.com/news/story/6656/4291279LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041809"
b9="總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。不過，知名主持人謝震武表示，他在選舉看到的結果是，政黨票只有3分之1的人投票給民進黨。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。"
c9=[['民進黨', '總統蔡英文', '謝震武'], ['2020總統大選'], ['總統', '國會', '民進黨'], '總統蔡英文贏得2020總統大選成功連任，民進黨也獲得61席立委，達到「國會過半」目標。他提醒民進黨「千萬不要囂張」，這也是接下來民進黨要被檢驗的地方。']

a10="UBN:https://udn.com/news/story/7331/4289954LTN:https://news.ltn.com.tw/news/politics/breakingnews/3041730"
b10="民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。陸委會也呼籲，中共必須首先正視中華民國是主權國家、台灣從來都不是中華人民共和國一部分的事實；認清台灣前途只有台灣2300萬人民有權決定，任何威脅利誘都不會撼動我們對維護國家主權與民主自由的堅定信念。"
c10=[['民進黨秘書長羅文嘉', '陸委會', '中共'], ['今天（12號）下午'], ['台灣'], '民進黨秘書長羅文嘉今天下午強調，這次台灣人民用選票告訴中共和全世界，對未來發展的看法就是「反一國兩制」，並向中國喊話「活在過去並不助於兩岸未來的和平發展」。']

a11="UBN:https://udn.com/news/story/120806/4290042\nLTN: https://ec.ltn.com.tw/article/breakingnews/3041915"
b11="伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。針對烏克蘭航空客機墜毀事件，伊朗官方終於承認為自家軍方所為，外交部長查里夫（Mohammad Javad Zarif）週三也首度承認伊朗的「謊言」，指出官方欺騙伊朗人民好幾天，是為了穩定民心。"
c11=[['伊朗外交部長查瑞夫', '美國總統川普'], ['今天（15號）'], ['伊朗'], '伊朗外交部長查瑞夫今天表示，伊朗與世界強國達成的現行核協議還沒失靈，但若要跟美國總統川普達成新核武協議，他不確定能否持久。']

a12="UBN:https://udn.com/news/story/7270/4290571LTN:https://news.ltn.com.tw/news/world/breakingnews/3041753"
b12="當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。綜合媒體報導，1976年1月13日，16歲莫拉被發現陳屍路旁，死前一天她曾到麥當勞買飲料，自此再也沒有回家。"
c12=[['帕梅拉·莫拉'], ['1 15'], ['美國伍德裏奇'], '當年伍德裏奇（Woodridge）的16歲女孩帕梅拉·莫拉（Pamela Maurer）被綁架謀殺，謎團懸宕近半世紀，當初因為辦案技術不足而遲遲無法破案，但現在靠新的DNA鑑識技術，警方終於找到嫌犯，只可惜兇嫌早在1981年就過世。']

a13="UBN: https://udn.com/news/story/12639/4292499\nLTN: https://ec.ltn.com.tw/article/breakingnews/3042731"
b13="美中今（16）日簽署第一階段協議。過去1年來，受惠於美中貿易爭端，台灣迎來轉單效應、台商回流等利多，相關效應是否隨美中貿易緊張情勢緩解而消失；台經院景氣中心副主任邱達生分析，這次協議內容，美方仍保留對中國價值3700億商品關稅，未來若中方履約生變，美方仍可隨時加徵關稅，對廠商而言，不確定因素仍在，因此供應鏈轉移、台商回流效應等仍將持續進行。"
c13=[['台經院景氣中心副主任邱達生'], ['今（16）日'], ['美中'], '美中今（16）日簽署第一階段協議。']

a14="UBN:https://udn.com/news/story/6811/4290356LTN:https://news.ltn.com.tw/news/world/breakingnews/3040882"
b14="貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。不過，國際債信評等公司穆迪（Moody's）昨天示警，全球環境惡化將在2020年對歐元區成員國的開放經濟體成長帶來壓力。"
c14=[['貝倫堡銀行分析師史密丁'], ['昨天（14號）'], ['德國'], "貝倫堡銀行（Berenberg bank）分析師史密丁（Holger Schmieding）表示，展望未來，德國經濟成長的黃金10年已逐漸接近尾聲。"]

a15="UBN:https://udn.com/news/story/7243/4290405LTN:https://news.ltn.com.tw/news/business/breakingnews/3041134"
b15="《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。據《路透》報導，伊朗外交部長查里夫（Mohammad Javad Zarif）等伊朗官員已取消原定出席行程，對此，世界經濟論壇主席布倫德（BorgeBrende）週二於記者會上表示，在伊朗地區局勢不明朗的情況下，我們必須理解查里夫的缺席。"
c15=[['世界經濟論壇主席布倫德'], ['週二'], ['世界經濟論壇'], '《CNBC》報導顯示，今年出席世界經濟論壇的大人物包括：芬蘭總理馬林（Sanna Marin）、歐盟執委會主席范德萊恩（Ursula von der Leyen）、歐洲央行總裁拉加德（Christine Lagarde）、瑞典環保少女貝里（Greta Thunberg）、華為創辦人任正非。']

a16="UBN: https://udn.com/news/story/10930/4292872\nLTN: https://news.ltn.com.tw/news/politics/breakingnews/3041906"
b16="日前黑鷹殉職將士移靈儀式中，有憲兵因左右轉失靈遭致後憲網友非議，甚至有當事官兵壓力過大上網求援。曾擔任憲兵司令的駐丹麥大使李翔宙今日透過昔日幕僚表示，他除了感嘆，有更多不捨與心疼，而沒有人不會犯錯，關鍵在憲兵是否全軍官兵團結凝聚，坦然認錯、勇於改過。他呼籲後憲們能共同支持，讓線上憲兵恢復榮譽與自信。"
c16=[['曾擔任憲兵司令的駐丹麥大使李翔宙'], ['1 16'], ['日前黑鷹殉職將士移靈儀式中'], '日前黑鷹殉職將士移靈儀式中，有憲兵因左右轉失靈遭致後憲網友非議，甚至有當事官兵壓力過大上網求援。']

link.append(a1)
link.append(a2)
link.append(a3)
link.append(a4)
link.append(a5)
link.append(a6)
link.append(a7)
link.append(a8)
link.append(a9)
link.append(a10)
link.append(a11)
link.append(a12)
link.append(a13)
link.append(a14)
link.append(a15)
link.append(a16)
summary.append(b1)
summary.append(b2)
summary.append(b3)
summary.append(b4)
summary.append(b5)
summary.append(b6)
summary.append(b7)
summary.append(b8)
summary.append(b9)
summary.append(b10)
summary.append(b11)
summary.append(b12)
summary.append(b13)
summary.append(b14)
summary.append(b15)
summary.append(b16)
keyword.append(c1)
keyword.append(c2)
keyword.append(c3)
keyword.append(c4)
keyword.append(c5)
keyword.append(c6)
keyword.append(c7)
keyword.append(c8)
keyword.append(c9)
keyword.append(c10)
keyword.append(c11)
keyword.append(c12)
keyword.append(c13)
keyword.append(c14)
keyword.append(c15)
keyword.append(c16)




print(link)
print(summary)
print(keyword)




