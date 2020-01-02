# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# import os
import requests
import time


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup
import jieba,os,jieba.analyse,requests,time
import jieba.posseg as pseg


title=[]
title_keyword=[]
# options = webdriver.ChromeOptions()
# options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
# options.add_argument("--disable-extensions")
browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
browser.get("https://www.ltn.com.tw/")
# WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='title login_title' and text()='Login']//following::div[1]//input[@class='text header_login_text_box ignore_interaction']"))).send_keys("someemail@email.com")
search_btn = browser.find_element_by_css_selector("a[class*='iconSearch']").click()
time.sleep(3)
keyword = browser.find_element_by_css_selector("div[class='ltnsch_show boxTitle boxText'] input[id='cacheSearch']")
# keyword = browser.find_element_by_id("qs")
keyword.send_keys('韓國瑜')
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


# print("Current session is {}".format(browser.session_id))
# page = ''
# while page == '':
#     try:
#         page = requests.get('https://www.google.com/')
#     except:
#         print("Connection refused by the server..")
#         print("Let me sleep for 5 seconds")
#         print("ZZzzzz...")
#         time.sleep(5)
#         print("Was a nice sleep, now let me continue...")
#         continue

# browser.quit()
# try:
#     s.get("https://www.google.com/") # 你需要的网址
# except Exception as e:
#     print(e)



# try:
#     browser.set_page_load_timeout(1)
#     browser.get("https://www.ltn.com.tw/")
# except TimeoutException as ex:
#     isrunning = 0
#     print("Exception has been thrown. " + str(ex))
#     browser.close()

# browser.switch_to_frame('fb_xdm_frame_https') # by frame id, can also be name or WebElement
# wait=WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@track-element='header-login']")))
# browser.switch_to_default_content()


# wait = WebDriverWait(browser, 10)
# x = 0
# while (x < 3):
#     try:
#         search_btn.wait.until(ExpectedConditions.elementToBeClickable(By.xpath("xpath")))
#         search_btn.click()
#         break
#     except WebDriverException as e:
#         x+=1


# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--no-sandbox")
# browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
######

# browser = webdriver.Chrome(executable_path='/opt/anaconda3/envs/flask/bin/chromedriver')
# browser.get("https://www.ltn.com.tw/")
# search_btn = browser.find_element_by_class_name("ltnSearch")
# search_btn.click()



# assert "Python" in browser.title
# elem = browser.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in browser.page_source
# browser.close()

