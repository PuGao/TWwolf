# -*- coding: utf-8 -*-
################## 初始化 Line Bot API ##################
import os
import dotenv
dotenv.load_dotenv()
# import configparser
# import logging
# from pydispatch import Dispatcher
# from nlp.olami import Olami
# config = configparser.ConfigParser()
# config.read("config.ini")

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    # MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage
)
from linebot.models import *
import requests

line_bot_api = LineBotApi(os.getenv('LINE_BOT_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_BOT_SECRET'))

# if channel_secret is None or channel_access_token is None:
#     print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
#     sys.exit(1)

# line_bot_api = LineBotApi(channel_access_token)
# handler = WebhookHandler(channel_secret)
#########################################################



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
import random
import json
################### 接收並處理文字訊息 ##################

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # if event.message.text == "你好":
    # # text = update.message.text
    # # user_id = update.message.from_user.id
    # # reply = Olami().nli(text, user_id)
    # # update.message.reply_text(reply)
    #     line_bot_api.reply_message(event.reply_token,TexTSendMessage(text=Olami().nli(event.message.text,event.source.user_id))    
    
    today_keywords=[
        "貿易戰",
        "總統大選",
        "韓國瑜",
        "小英",
        "吳斯懷",
        "黃國昌",
        "豬瘟",
        "川普",
        "金正恩",
        "彭博",
        "馬克宏",
        "反送中",
        "翁山蘇姬",
        "環保少女",
        "小燈泡",
        "館長",
        "宋楚瑜",
        "柯文哲",
        "李佳芬",
        "丁守中"
    ]
    today_keywords_choice=[
        ['川普', '中國', '中貨', '南韓', '川普'], 
        ['中貨', '南韓', '柯媽'], 
        ['中貨', '南韓', '柯媽'], 
        ['柯媽媽', '朱立倫', '藍營'], 
        ['張選', '朱立倫', '南韓'], 
        ['張選', '藍黃', '朱立倫'], 
        ['小英', '張選', '藍黃'], 
        ['小英', '拜登', '張選'], 
        ['吳怡', '小英', '安倍'], 
        ['美國', '吳怡', '安巴'], 
        ['中國', '美國', '吳怡'], 
        ['中國', '美國', '吳怡'], 
        ['北韓', '中國', '美國'], 
        ['北韓', '中國', '美國'], 
        ['北韓', '國民黨', '中國'], 
        ['北韓', '國民黨', '中國'], 
        ['北韓', '國民黨', '中國'], 
        ['北韓', '國民黨', '中國'], 
        ['蘇貞昌', '北韓', '國民黨'], 
        ['中國', '北韓', '吳怡']
    ]
    abstract=[
    ['謝金河說，今年在美中貿易戰衝擊下，台灣成為轉單效應受益者，前10個月對美國出口成長17.7%，今年三個季度台灣的GDP表現都優於南韓，而南韓出口從去年12月迄今，每月都出現衰退，今年11月衰退14.3%，台灣出口則逆勢成長3.3%，台灣和南韓經濟出現了新的轉折，這當中有幾個變數值得注意三是南韓以大企業為主，這次在貿易戰中受到很大影響，三星電子的記憶體首當其衝，今年三星的營業利益減半，剛公布的12月前20天，南韓半導體出口仍衰退16.7%，而船舶出口減少51.2%，南韓的石化，鋼鐵，造船產業今年都面臨很大壓力', '儘管今年業績走緩，不過沈國榮表示，公司仍規劃明年4月調薪，在年報出來後，依據今年獲利情況、並參考明年第1季成長趨勢調薪和大董事長沈國榮表示，明年業績可回溫，未來電動車業績占比拚5成，員工年終獎金平均可到1.5個月，明年4月續調薪', '（作者為前華府喬治城大學外交學院講座教授，曾任國防部副部長）爆〔編譯楊芙宜／綜合報導〕彭博報導，美國對中國產品加徵高關稅後，中國供應商透過越南撕掉「中國製造」標籤來洗產地越來越普遍，耶誕燈飾就是一例越南海關總署海關監管部門主管歐英俊表示，遏制非法貨物進入是個難題，該部一直在和越南計畫投資部合作，對來自中國和香港的FDI展開全面篩檢，將檢查外來投資計畫生產的商品是否要繳納美國關稅，並判斷投資者是否打算「僅僅找個地方組裝他們從中國帶來的所有零件」'], 
    ['謝金河說，今年在美中貿易戰衝擊下，台灣成為轉單效應受益者，前10個月對美國出口成長17.7%，今年三個季度台灣的GDP表現都優於南韓，而南韓出口從去年12月迄今，每月都出現衰退，今年11月衰退14.3%，台灣出口則逆勢成長3.3%，台灣和南韓經濟出現了新的轉折，這當中有幾個變數值得注意三是南韓以大企業為主，這次在貿易戰中受到很大影響，三星電子的記憶體首當其衝，今年三星的營業利益減半，剛公布的12月前20天，南韓半導體出口仍衰退16.7%，而船舶出口減少51.2%，南韓的石化，鋼鐵，造船產業今年都面臨很大壓力', '美國商業環境風險評估公司（BERI） 發布今年第3次「投資環境風險評估報告」，台灣的投資環境風險評比排名居全球第4名，與加拿大同名，總分則為63分》自營商進出明細\xa0\xa0》外資持股增減排行》即時選股找重點\xa0\xa0》漲跌幅即時排行》即時選股找重點\xa0\xa0》漲跌幅即時排行爆BERI發布今年第3次「投資環境風險評估報告」，台灣的投資環境風險評比排名居全球第4名', '（記者歐素美攝）〔記者歐素美／台中報導〕郭台銘為台灣民眾紙台中市立委候選人謝文卿站台，第一句話就是向柯文哲母親何瑞英道歉，因自己未遵守與神明的約定及柯媽、柯爸的支持退選，他並表示，總統不會投蔡英文，希望立委第三勢力能最極大化，不要讓一黨在國會獨大，以免造成權力的獨裁郭台銘與柯媽今晚同時為民眾黨台中市第五選區立委候選人謝文卿站台助選，郭台銘一到就致贈自家美國農場生產的人蔘給柯媽，還向柯媽道歉，因為今年9月中秋節前送月餅去新竹，柯媽及柯爸支持他參選總統，他也和柯文哲到城隍廟擲筊，與神明約定參選，結果因考慮94歲媽媽洗腎，身體狀況不好及中美貿易戰，台灣經濟困難而退選'], 
    ['（歐新社檔案照）自由時報聯合國報告：美中貿易戰最大贏家 台對美出口增千億聯合國貿易暨發展會議（ＵＮＣＴＡＤ）週二公布研究報告指出，美中貿易戰後，美國對中貨加徵多波關稅，使得今年上半年美國自中國進口大減逾四分之一（三五○億美元），台灣則成為貿易移轉效應最大受惠者，上半年對美國出口增加四十二億美元（約一二七五億台幣）謝金河說，今年在美中貿易戰衝擊下，台灣成為轉單效應受益者，前10個月對美國出口成長17.7%，今年三個季度台灣的GDP表現都優於南韓，而南韓出口從去年12月迄今，每月都出現衰退，今年11月衰退14.3%，台灣出口則逆勢成長3.3%，台灣和南韓經濟出現了新的轉折，這當中有幾個變數值得注意', '（記者方賓照攝）〔中央社〕美國媒體今天報導，香港示威浪潮讓台灣「天然獨」的千禧世代堅信「一國兩制」不可能適用於台灣香港的情勢除了動搖台灣人對與中國往來的看法，也幫助千禧世代向父母輩解釋他們的恐懼，也更清楚堅定他們對獨立台灣的渴望', '爆蔡總統質疑，國民黨還說要叫網軍去肉搜人，那這樣是怎樣的網軍，（記者方賓照攝）〔記者陳鈺馥／台北報導〕針對國民黨祭?100萬元賞金要尋找「卡神」楊蕙如，總統蔡英文今日出席電視政見發表會後受訪表示，這案子已經進入司法程序，不適宜多做評論，倒是國民黨要講清楚，曾永權在韓國瑜競選總部建的網軍，是什麼樣的網軍請繼續往下閱讀...對於柯文哲後援會會長說要支持韓國瑜，但柯媽媽說她這一票要投給蔡英文，蔡總統指出，「我們都尊重」，台灣社會很多元，一個家庭裡面成員都有不同的投票傾向'], 
    ['（記者楊金城攝）〔記者楊金城／台南報導〕台北市長柯文哲的爸爸柯承發、媽媽何瑞英，今天上午一早到新營菜市場為台灣民眾黨和台南市第一選區立委候選人顏耀星助選拉票，柯媽媽說，總統蔡英文卡古意，過去的感情還在，她會投票選給小英，她又不認識韓國瑜，並認為蔡英文會當選連任柯媽爆：他絕對會投蔡英文台灣民眾黨主席柯文哲選不選2024總統 柯媽媽這麼說', '高敏裕分析，這次邱厝里應該會是民進黨蔡英文贏，因為雖然一年前國民黨在縣市長選舉大勝，但韓國瑜施政讓人看破手腳，再加上反送中議題，他覺得邱厝里小英會勝出，而如果全國的投票結果也是如此，邱厝里就會再次成為台中的「選情章魚哥」（記者唐在馨攝）〔記者唐在馨／台中報導〕每次重大選舉，各地都有一些里投開票所會認為自己是該縣市的「選情章魚哥」，台中北區邱厝里里長高敏裕統計自己里內近3次總統及2次市長的重大選舉開票結果，都和大選結果吻合，而總統大選倒數計時，他估計，邱厝里應該是民進黨蔡英文贏，如果趨勢符合，全國也應該是蔡英文會贏', '（本報資照照片）〔記者李欣芳／台北報導〕中國處心積慮滲透台灣，蔡英文總統日前宣示民進黨團所提「反滲透法草案」本月底一定要通過，連日來引發藍營大反彈，獨派大老、總統府資政吳澧培今天接受本報訪問時強調，中國對台滲透問題相當嚴重，反滲透法早就該立法通過，這個月底一定要三讀通過，他呼籲蔡英文「免驚」，對這項立法要所有堅持，莫因國民黨的嚇唬、反彈而退縮吳澧培抨擊國民黨說，執政黨從今年4月就提出相關修法，要規範中國滲透問題，但國民黨不願與民進黨好好討論、協調，到現在都還杯葛「反滲透法草案」，問題出在國民黨一直杯葛立法'], 
    ['（記者張議晨攝）〔記者張議晨／宜蘭報導〕總統、立委大選進入最後倒數，民進黨青年軍跟上夾娃娃機熱潮，推出護國保台夾娃娃機，機台內放上吳斯懷、邱毅等親中立委候選人照片，號召年輕人將他們「夾出」立法院，大玩選舉創意謝金河說，今年在美中貿易戰衝擊下，台灣成為轉單效應受益者，前10個月對美國出口成長17.7%，今年三個季度台灣的GDP表現都優於南韓，而南韓出口從去年12月迄今，每月都出現衰退，今年11月衰退14.3%，台灣出口則逆勢成長3.3%，台灣和南韓經濟出現了新的轉折，這當中有幾個變數值得注意', '反滲透法立法，就是為了防制中共勢力滲透台灣、避免中華民國被粉身碎骨，你們卻與中共一起反反滲透法，也就是要把台灣、把中華民國，送進中共專制政權的粉碎機中碾成齏粉而且，藍軍除了與中共聯軍反反滲透法，同聲狠罵綠色恐怖、民主倒退之外，對反滲透法內容根本就不去了解，就只是在喊反、反、反', '外媒指近日冒著生命危險逃到澳洲的中國間諜，「威廉．王」（音譯「王立強」，Wang 「William」 Liqiang），在接受澳洲《時代報》（The Age）、《雪梨晨鋒報》（The Sydney Morning Herald）和節目《60分鐘》（60 Minutes） 等媒體訪問中提到，他曾經利用偽造的南韓護照進入台灣，幫助中國有系統性的滲透台灣政治體系，包括指揮「網軍」和台灣間諜介入2018年的地方選舉，並金援兩千萬人民幣給韓國瑜選高雄市長，而中國目前正在制定干擾台灣2020年總統大選的計劃（圖擷取自《雪梨晨鋒報》）王立強表示，他所在的情報部門正在與媒體高層聯繫，以影響台灣的政治體系，這是北京推翻總統蔡英文的系統性選舉干預行動，間諜透過行動支持國民黨總統參選人韓國瑜'], 
    ['（資料照）〔即時新聞／綜合報導〕新北市第12選區現任立委時代力量黃國昌未尋求連任，改派辦公室主任賴嘉倫接棒參選，民進黨則徵召年僅27歲的「太陽花女戰神」賴品妤，形成太陽花內戰，賴品妤日前在臉書透露選情告急，許多網友紛紛留言打氣，但卻被發現時力北市議員林穎孟也留言加油，遭網質疑「忘了自己的黨也有派人嗎」貼文一出，立刻湧入許多網友留言打氣，但卻赫見時力北市議員林穎孟也在底下留言喊加油，引發網友質疑，有網友酸想跳船快說，「大姐，你是忘了自己的黨也有參選人嗎，還是臥底來不及切帳號啊 笑死」、「難怪時力被稱小綠，就是會有這種豬隊友」，也有人難掩失望表示曾幫林穎孟拉過票，但未來不會再支持她', '鄭宏輝陣營也針對時代力量與國民黨的抹黑指出， 他曾來不做違法之事，一切都禁得起社會檢驗，但對於時代力量及國民黨的持續抹黑，不再忍耐，更質疑鄭正鈐的正能量和高鈺婷的新政治，就是抹黑他人救選情鄭宏輝陣營指出，3天前國民黨與時代力量同一天開記者會抹黑鄭宏輝，今天再次同一時間，一個在台北市開記者會，一個在臉書直播貼不實內容，藍黃聯手攻擊鄭宏輝，因此合理懷疑資料來源根本就是同一個，質疑國民黨與時代力量已站在一起，難道這是鄭正鈐的「正能量」，或時代力量的「新政治」', '郭台銘表示，他在中秋節前後到新竹送月餅給柯媽媽，原本準備參選總統，後來考慮到自己媽媽的身體，擔心參選無法分身照顧媽媽，加上中美貿易衝突讓台灣比較困難而未參選，一直想要找時間向柯媽媽說抱歉，原本想約今天到新竹，柯媽媽說不用到新竹，來幫謝文卿站台就好了反滲透法立法，就是為了防制中共勢力滲透台灣、避免中華民國被粉身碎骨，你們卻與中共一起反反滲透法，也就是要把台灣、把中華民國，送進中共專制政權的粉碎機中碾成齏粉'], 
    ['●九月卅日美國非營利的「皮尤研究中心」（Pew Research Center）發表對全球各大洲共卅二國人民的民調「你喜歡中國與否韓辦怒轟 蔡睜眼說瞎話蔡英文總統限立院黨團31日完成《反滲透法》立法，引發大反彈', '經濟部表示，台灣在BERI此次評比等級下調至1C，分數下滑1分，主要受政治風險影響，展望2020年排名可能下滑至全球第5名，評分61分請繼續往下閱讀...蘇貞昌表示，行政院長工作繁忙，從台灣頭顧到台灣尾，從蚊子管到豬隻，光是登革熱防疫工作，政府今年補助高雄市長韓國瑜8200多萬元', '0'], 
    ['現在美國兩黨、媒體、智庫乃至社會，對中國崛起的想像由正轉負，國民黨還繼續跟習近平跳交際舞，其結果不僅是「穿著旗袍跳現代舞」之彆扭而已，恐怕還將自陷於小黨化、泡沫化的存亡危機偏偏國民黨的上層結構，仍奉行「連胡會」以來的聯共制台，也就是，聯合專制中國力量，抵銷台灣民主活力', '經濟部表示，台灣在BERI此次評比等級下調至1C，分數下滑1分，主要受政治風險影響，展望2020年排名可能下滑至全球第5名，評分61分（美聯社）〔財經頻道／綜合報導〕美國總統大選明年登場，美媒CNBC公佈第4季百萬美元富翁調查顯示，美國總統川普是百萬美元富翁最喜愛的個別候選人，但若明年選舉是川普對決前副總統拜登（Joe Biden），川普將會落敗', '賴清德今天參加蔡英文台中市競選總部舉辦的「台中市小英姐妹會幹部培訓營」，他說，國民黨提名罵香港人及學生是暴民，以及到中國參加國慶、聽習近平訓話的人為不分區立委，而且還在安全名單，這是大錯誤賴清德說，香港爭取自由民主，下多大決心，一次遊行超過上百萬人，警方拿槍對著學生，學生都不怕，區議員選舉高投票率，泛民主派還獲得高席次，美國參、眾兩院，通過香香港人權與民主法案，川普今天還簽署，美國是如此支持香港，國民黨竟提名一個批香港人民及學生是暴民為不分區立委，而且是安全名單，他聽下去'], 
    ['0', '0', '郭台銘原本要參選總統並受到台北市長柯文哲的媽媽支持，結果最後未參選，而對柯媽媽感到抱歉，今晚他與柯媽媽到第5選區（北、北屯區）立委參選人謝文卿競選總部，一起送上好彩頭與粽子表達支持，郭董並同意借將永齡基金會顧問郭昕宜幫忙謝文卿郭台銘表示，他在中秋節前後到新竹送月餅給柯媽媽，原本準備參選總統，後來考慮到自己媽媽的身體，擔心參選無法分身照顧媽媽，加上中美貿易衝突讓台灣比較困難而未參選，一直想要找時間向柯媽媽說抱歉，原本想約今天到新竹，柯媽媽說不用到新竹，來幫謝文卿站台就好了'], 
    ['（作者為前華府喬治城大學外交學院講座教授，曾任國防部副部長）爆特斯拉證實首批中國製Model 3電動轎車將於下週一交車，正式向中國本土電動車廠宣戰（路透）〔編譯楊芙宜／台北報導〕彭博報導，美國電動車大廠特斯拉（Tesla）下週一（30 日）首批中國製Model 3電動轎車將交車，為推進中國市場創下里程碑', '0', '郭台銘原本要參選總統並受到台北市長柯文哲的媽媽支持，結果最後未參選，而對柯媽媽感到抱歉，今晚他與柯媽媽到第5選區（北、北屯區）立委參選人謝文卿競選總部，一起送上好彩頭與粽子表達支持，郭董並同意借將永齡基金會顧問郭昕宜幫忙謝文卿郭台銘表示，他在中秋節前後到新竹送月餅給柯媽媽，原本準備參選總統，後來考慮到自己媽媽的身體，擔心參選無法分身照顧媽媽，加上中美貿易衝突讓台灣比較困難而未參選，一直想要找時間向柯媽媽說抱歉，原本想約今天到新竹，柯媽媽說不用到新竹，來幫謝文卿站台就好了'], 
    ['請繼續往下閱讀...另外，德國第3大報紙發行商「馮克媒體集團」（Funke Mediengruppe）委託「凱度」市場研究公司（Institut Kantar）調查德國人對德、美、英、法等7國領導人信任度，法國總統馬克宏最受信任，高過德國總理梅克爾，57%受訪者相當高度信任馬克宏、32%不太信任德意志新聞社（DPA）25日公佈委託民調公司「網路輿觀」（YouGov）針對2024名德國人的民調，41%的受訪者認為，川普是這5人中最有害世界自由，其次是金正恩，17%說他最威脅自由，認為是普廷、哈米尼的比例均為8%，7%認為習近平對世界自由的威脅最大', '香港的情勢除了動搖台灣人對與中國往來的看法，也幫助千禧世代向父母輩解釋他們的恐懼，也更清楚堅定他們對獨立台灣的渴望美國媒體今天報導，香港示威浪潮讓台灣「天然獨」的千禧世代堅信「一國兩制」不可能適用於台灣', '0'], 
    ['中媒《環球時報》今日（27日）公布最新的民調顯示，有69.7%的中國民眾認為中國近年來的國際形象越來越好，至於何種因素導致中國形象變差，第一名是「部分官員的貪污腐敗」，高於「不遵守規則，擾亂貿易秩序」調查顯示，有69.7%的中國民眾認為中國近年來的國際形象越來越好，僅有12.3%的人認為變差', '歷屆大選得票數比較韓國瑜全國競選總部主委朱立倫（左）傍晚到第六選區國民黨候選人李中競選總部打氣，他幫李中錄影60秒、錄音30秒推薦「五告讚」影片，爭取台中藍營立委席次過半行政院前院長、也是民進黨不分區立委候選人「水牛伯」游錫?也來台中，陪同第六選區現任立委黃國書在西區向上市場徒步掃街拜票，「水牛伯」魅力驚人，民眾爭相合照留影，將原本就熱鬧的市場擠得水洩不通', '爆北市第三選區〔記者蔡思培／台北報導〕台北市立委第三選區「雙帥火線對決」後勁十足，國民黨現任立委蔣萬安原本被看好能連任，但民進黨候選人吳怡農勤跑基層與媒體經營，加上志願從軍以保家衛國所散發的男子氣概，人氣快速攀升，甚至躍為民進黨候選人爭相要求合作的「小母雞」，反觀蔣陣營這次選戰策略趨於保守，吳怡農遂從大幅落後一路追趕到最新民調差距僅剩○．八％，逆勢成長的吳怡農構成蔣萬安連任之路的嚴厲挑戰吳怡農今年八月被民進黨徵召時名氣不高，支持度遠遠不及蔣萬安，但吳投入選戰後積極與選民互動，上網路節目、參加活動示範武術、上台玩音樂唱歌，展現各種才藝，三個月內快速竄紅，人氣飆升，其吸睛度已成為同黨候選人爭相邀約的「小母雞」'], 
    ['0', '（路透）在「三殿之儀」儀式結束之後，「即位禮正殿之儀」將於當地時間今日下午1點在皇居正殿「松之間」舉行，德仁天皇將身穿傳統裝束「黃櫨染御袍」登上寶座「高御座」，發表講話（美聯社）綜合日媒報導，德仁與皇后雅子今上午在皇居「宮中三殿」舉行「三殿之儀」儀式，德仁天皇會身穿純白「帛御袍」，而雅子皇后則會穿上傳統的「十二單衣」進行儀式', '（路透）在「三殿之儀」儀式結束之後，「即位禮正殿之儀」將於當地時間今日下午1點在皇居正殿「松之間」舉行，德仁天皇將身穿傳統裝束「黃櫨染御袍」登上寶座「高御座」，發表講話（美聯社）綜合日媒報導，德仁與皇后雅子今上午在皇居「宮中三殿」舉行「三殿之儀」儀式，德仁天皇會身穿純白「帛御袍」，而雅子皇后則會穿上傳統的「十二單衣」進行儀式'], 
    ['0', '（法新社）〔即時新聞／綜合報導〕《時代》雜誌2019年度風雲人物出爐，由瑞典環保少女童貝里（Greta Thunberg）擊敗美國總統川普、中國國家主席習近平等人中選，川普卻在推特上嘲諷童貝里情緒管理有問題，要她想辦法冷靜」請繼續往下閱讀...童貝里不直接正面回擊川普，而是將她的推特自我介紹更改為，「一名正在努力管理憤怒情緒的青少年，最近相當冷靜，還和朋友去看了一部好的老片', '記者蘇健忠／攝 分享   facebook     爆近十年來，ESG概念興起，成為當今華爾街、法人投資圈最熱門的英文縮寫，注意到ESG題材投資潮流，柏瑞投信突破傳統債券投資思維，創新推出境內首檔、台灣唯一以「ESG因子+量化策略」 的全球投資級債券基金412人角逐72席次 完整名單一次看鴻海集團創辦人郭台銘（左）與台北市長柯文哲（右）上午出席「BioX智慧健康與生技產業趨勢論壇」暨「與市長有約」活動，兩人一起比讚合影'], 
    ['0', '前總統馬英九今天南下為台南立委第一選區候選人蔡育輝助選時，再次將矛頭指向蔡英文總統，抨擊急欲在年底要通過「反滲透法」，一旦草率通過 ，台灣恐淪為「特務治國」爆〔記者洪美秀、黃美珠／新竹報導〕時代力量新竹市立委候選人高鈺婷昨天指出，這兩天遭網友范振揆留言恐嚇，范圈出她競選看板上兩個女兒的照片問：「這兩個小孩是誰', '在國防部確定將與館長合作後，王國強再度在臉書發文表示，相信現在的國軍特勤隊及特戰部隊，在各項訓練方面仍有不少需要改善進步的空間請繼續往下閱讀...無黨籍鳳山區立委候選人葉鳳強今與多名社區媽媽站出來，一同聲援小燈泡母親王婉諭，表達媽媽們的憤怒，希望如此不公不義的司法審判不該再發生，讓小燈泡亮起來，台灣需要一點光'], 
    ['0', '（記者方賓照攝）〔記者涂鉅旻／台北報導〕中選會舉辦的第三場總統政見發表會今晚落幕，親民黨總統候選人宋楚瑜在會後受訪時，重申反對「反滲透法」草案的立場，對於民進黨候選人蔡英文、國民黨候選人韓國瑜在會中互稱「韓總機」和「讀稿機」，宋楚瑜表示：「我只希望台灣不要當機」，盼民眾能選個能為開創台灣生機者總統政見會3》蔡酸韓總機、韓批讀稿機 兩人激烈攻防總統政見會3》重申只做一任撥亂反正 宋楚瑜：推動兩岸貿易交流台中科技人瘋搶\u3000這個推案區含金量最高總統政見會3》批蔡兩岸、基層照顧不好 宋楚瑜講到香蕉痛哭總統政見會3》遭酸「韓總機」 韓國瑜反嗆蔡英文「讀稿機」麗寶微風天地創洲子洋人氣指標總統政見會3》蔡英文嗆韓：選總統不是「選總機」 你的分機是633總統政見會3》穿博士服嗆小英 宋楚瑜：我自首犯反滲透法總統政見會3》韓國瑜自誇政治奇才 蔡英文：很奇怪的奇才總統政見會3》韓國瑜稱絕不原諒酒駕的人 鄉民噓爆：自我打臉', '（記者方賓照攝）〔記者涂鉅旻／台北報導〕中選會舉辦的第三場總統政見發表會今晚落幕，親民黨總統候選人宋楚瑜在會後受訪時，重申反對「反滲透法」草案的立場，對於民進黨候選人蔡英文、國民黨候選人韓國瑜在會中互稱「韓總機」和「讀稿機」，宋楚瑜表示：「我只希望台灣不要當機」，盼民眾能選個能為開創台灣生機者在國防部確定將與館長合作後，王國強再度在臉書發文表示，相信現在的國軍特勤隊及特戰部隊，在各項訓練方面仍有不少需要改善進步的空間'], 
    ['（記者呂伊萱攝）〔記者呂伊萱／台北報導〕韓國駐台代表姜永勳今天表示，台灣與韓國都支持自由公平的貿易秩序，在保護主義擴散等趨勢領域上，台韓有許多可合作的空間記者張曼蘋／攝影 分享   facebook     行政院長蘇貞昌今晚再到新北市板橋替子弟兵、第6選區立委候選人張宏陸站台', '爆深媒體人王瑞德認為，蔡、韓兩人表現都不錯，也點出韓國瑜缺乏政見、使用錯誤資料等致命問題（擷取自王瑞德臉書）〔即時新聞／綜合報導〕2020總統候選人第3場電視政見發表會今晚（27日）登場，3名候選人蔡英文、韓國瑜與宋楚瑜同台交鋒，其中，蔡、韓2人數度就「韓總機」與「讀稿機」等議題激烈攻防', '請繼續往下閱讀...陸委會強調，宋楚瑜是受蔡總統委託出席國際會議，與中國大陸領導人的會面是正常的國際交流活動，並將相關談話內容轉知蔡總統，既無受境外敵對勢力指示、委託、資助的「滲透作為」，也無從事「反滲透法草案」所定5種「不法行為」，怎麼會有依「反滲透法草案」處罰的問題在國防部確定將與館長合作後，王國強再度在臉書發文表示，相信現在的國軍特勤隊及特戰部隊，在各項訓練方面仍有不少需要改善進步的空間'], 
    ['看各黨提名名單●何謂政黨票台灣目前的立法委員選舉制度是採用「單一選區兩票制」，也就是每個選民會拿到兩張選票，分別可以投「區域立委」以及「不分區立委」兩票，一票投給人，另一票則投給政黨，投給政黨以決定不分區立委席次的選票，稱之為「政黨票」在制度設計上，不分區立委就是各政黨推出的專業領域、弱勢代表、以及可代表黨意的人選，因為很多各領域專業人士，不容易透過區域選舉進入立法院，不分區立委就提供這樣一個機會，這些人能不受地區限制，更兼顧全國利益來問政、修法', '黃國昌表示，我們允許與中國大陸正常交往，但台灣現在面臨中國的文攻武嚇和經濟上的統戰，台灣人民的權益必須得到保障，跟中國彼此之間協議的監督機制已經刻不容緩，別再一而再再而三的延宕，難道過去處理服貿、貨貿的經驗還不夠慘烈嗎爆蔡總統質疑，國民黨還說要叫網軍去肉搜人，那這樣是怎樣的網軍，（記者方賓照攝）〔記者陳鈺馥／台北報導〕針對國民黨祭?100萬元賞金要尋找「卡神」楊蕙如，總統蔡英文今日出席電視政見發表會後受訪表示，這案子已經進入司法程序，不適宜多做評論，倒是國民黨要講清楚，曾永權在韓國瑜競選總部建的網軍，是什麼樣的網軍', '柯文哲喊出民眾黨要成為第一大黨 主導台灣未來政治發展台中科技人瘋搶\u3000這個推案區含金量最高評施政民調墊底  柯Ｐ：中國官員素質比台灣好民眾黨成參選2024包袱（記者吳佳穎攝）〔即時新聞／綜合報導〕卓越雜誌日前公布六都市長施政表現滿意度調查，台北市長柯文哲排名墊底，柯今（27）天回應，「兔子跟烏龜比游泳沒淹死就不錯了'], 
    ['看各黨提名名單●何謂政黨票台灣目前的立法委員選舉制度是採用「單一選區兩票制」，也就是每個選民會拿到兩張選票，分別可以投「區域立委」以及「不分區立委」兩票，一票投給人，另一票則投給政黨，投給政黨以決定不分區立委席次的選票，稱之為「政黨票」在制度設計上，不分區立委就是各政黨推出的專業領域、弱勢代表、以及可代表黨意的人選，因為很多各領域專業人士，不容易透過區域選舉進入立法院，不分區立委就提供這樣一個機會，這些人能不受地區限制，更兼顧全國利益來問政、修法', '黃國昌表示，我們允許與中國大陸正常交往，但台灣現在面臨中國的文攻武嚇和經濟上的統戰，台灣人民的權益必須得到保障，跟中國彼此之間協議的監督機制已經刻不容緩，別再一而再再而三的延宕，難道過去處理服貿、貨貿的經驗還不夠慘烈嗎立法院內政委員會今舉行「兩岸協議監督機制法制化」公聽會，國民黨立委黃昭順表示，當初民進黨當初杯葛服貿要求「先立法再審查」，但5年過去了行政院卻未有版本，根本是在打假球', '」（圖取自自由電子報YouTube）〔即時新聞／綜合報導〕國民黨總統候選人韓國瑜今（27）日出席第3次總統電視政見會，在第3輪政見發表中自稱絕對不會原諒「酒後駕車」的人，PTT鄉民認為這番用字遣詞是在自我打臉，砲轟「腦袋到底在想什麼賴嘉倫接受中央社記者採訪時表示，選民已沒那麼根深蒂固的選黨觀念，會看參選人特色，過去幾次選舉，游移選票仍占不少比例，這是他要把握的族群之一'], 
    ['看各黨提名名單●何謂政黨票台灣目前的立法委員選舉制度是採用「單一選區兩票制」，也就是每個選民會拿到兩張選票，分別可以投「區域立委」以及「不分區立委」兩票，一票投給人，另一票則投給政黨，投給政黨以決定不分區立委席次的選票，稱之為「政黨票」在制度設計上，不分區立委就是各政黨推出的專業領域、弱勢代表、以及可代表黨意的人選，因為很多各領域專業人士，不容易透過區域選舉進入立法院，不分區立委就提供這樣一個機會，這些人能不受地區限制，更兼顧全國利益來問政、修法', '0', '胡采蘋分析，柯文哲滿意度比高雄市長韓國瑜還低，不滿意度冠絕六都，然後還要請假輔選，重點是柯自己沒有參選，到底憑什麼請假，還媽祖遶境，到處污辱小黨女性、香港人、西藏人，請問一下是誰跟我說罷免柯文哲很難，「這種市長就是應該罷免，我個人支持簡余晏補選台北市長胡采蘋昨天在臉書上表示，實務上來說，罷柯一定是比罷韓容易，台北市立委候選人蔣萬安或吳怡農任何一個人若落選，群眾受傷的心情再聽到這類嘴砲，真的很容易一觸即發啟動「wesupercare」，蔣萬安出馬，丁守中帶頭復仇，綠營派高嘉瑜或鄭麗君，連黃國昌都會摩拳擦掌出來參加補選，到時候大家都會覺得超有意義']
]
    today_keywords_link_udn=[
        ['https://udn.com/news/story/7238/4252547', 'https://udn.com/news/story/7241/4253376', 'https://udn.com/news/story/7340/4199214', 'https://udn.com/news/story/7238/4252547', 'https://udn.com/news/story/7240/4253854'], 
        ['https://udn.com/news/story/7340/4199214', 'https://udn.com/news/story/7238/4252472', 'https://udn.com/news/story/7548/4253506'], 
        ['https://udn.com/news/story/7340/4199214', 'https://udn.com/news/story/6656/4251494', 'https://udn.com/news/story/7548/4253506'], 
        ['https://udn.com/news/story/6656/4253077', 'https://udn.com/news/story/7548/4250868', 'https://udn.com/news/story/6656/4253077'], 
        ['https://udn.com/news/story/7548/4241260', 'https://udn.com/news/story/6656/4242502', 'https://udn.com/news/story/10930/4185585'], 
        ['https://udn.com/news/story/7548/4235671', 'https://udn.com/news/story/6656/3756713', 'https://udn.com/news/story/7548/4241790'], 
        ['https://udn.com/news/story/12702/4207460', 'https://udn.com/news/story/7548/4240630', '0'], 
        ['https://udn.com/news/story/7339/4237817', 'https://udn.com/news/story/6813/4250043', 'https://global.udn.com/global_vision/story/8662/4235891'], 
        ['0', 'https://udn.com/news/story/9637/3951461', 'https://udn.com/news/story/6809/4244467'], 
        ['https://udn.com/news/story/7240/4253158', 'https://udn.com/news/story/12702/4243664', 'https://udn.com/news/story/6811/4246367'], 
        ['https://udn.com/news/story/7269/4234369', 'https://udn.com/news/story/6904/4251461', '0'], 
        ['https://udn.com/news/story/7241/4253376', 'https://udn.com/news/story/7241/4253376', 'https://udn.com/news/story/12702/4246513'], 
        ['https://global.udn.com/global_vision/story/8662/3405616', 'https://udn.com/news/story/6809/4224185', 'https://global.udn.com/global_vision/story/8663/4220387'], 
        ['https://udn.com/news/story/120764/4096180', 'https://udn.com/news/story/6809/4250981', 'https://ubrand.udn.com/ubrand/story/12117/4252602'], 
        ['https://opinion.udn.com/opinion/story/10043/2507512', 'https://udn.com/umedia/story/12755/4249858', 'https://udn.com/news/story/12702/4233621'], 
        ['https://opinion.udn.com/opinion/story/11664/4185750', 'https://udn.com/news/story/12702/4253835', 'https://udn.com/news/story/6656/4250287'], 
        ['https://udn.com/news/story/12702/4248294', 'https://udn.com/news/story/12702/4253835', 'https://udn.com/news/story/120863/4253798'], 
        ['https://udn.com/news/story/12702/4174827', 'https://udn.com/news/story/6656/4253776', 'https://udn.com/news/story/6656/4252743'], 
        ['https://udn.com/news/story/12702/4242861', 'https://udn.com/news/story/12702/4094855', 'https://udn.com/news/story/12702/4253598'], 
        ['https://udn.com/news/story/6656/4239936', 'https://udn.com/news/story/120525/3846842', 'https://udn.com/news/story/6837/3327334']
    ]
    today_keywords_link_ltn=[
        ['https://news.ltn.com.tw/news/business/breakingnews/3021748', 'https://news.ltn.com.tw/news/business/breakingnews/3022705', 'https://news.ltn.com.tw/news/business/paper/1341872', 'https://news.ltn.com.tw/news/business/breakingnews/3022643', 'https://news.ltn.com.tw/news/business/breakingnews/3021748'], 
        ['https://news.ltn.com.tw/news/business/paper/1339136', 'https://news.ltn.com.tw/news/business/breakingnews/3022187', 'https://news.ltn.com.tw/news/politics/breakingnews/3022551'], 
        ['https://news.ltn.com.tw/news/life/breakingnews/2969912', 'https://news.ltn.com.tw/news/politics/breakingnews/3021610', 'https://news.ltn.com.tw/news/politics/breakingnews/3022666'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/3021845', 'https://news.ltn.com.tw/news/politics/breakingnews/3021708', 'https://news.ltn.com.tw/news/politics/breakingnews/3022258'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/3017553', 'https://news.ltn.com.tw/news/opinion/breakingnews/3021689', 'https://news.ltn.com.tw/news/opinion/breakingnews/2987385'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/3004411', 'https://news.ltn.com.tw/news/politics/breakingnews/3022087', 'https://news.ltn.com.tw/news/opinion/breakingnews/3021689'], 
        ['https://news.ltn.com.tw/news/life/breakingnews/3020609', 'https://news.ltn.com.tw/news/politics/breakingnews/3009471', '0'], 
        ['https://news.ltn.com.tw/news/opinion/paper/1341854', 'https://news.ltn.com.tw/news/business/breakingnews/3020692', 'https://news.ltn.com.tw/news/politics/breakingnews/2992744'], 
        ['0', '0', 'https://news.ltn.com.tw/news/world/paper/1340925'], 
        ['https://news.ltn.com.tw/news/business/breakingnews/3022709', '0', 'https://news.ltn.com.tw/news/business/breakingnews/3018734'], 
        ['https://news.ltn.com.tw/news/world/breakingnews/3021655', 'https://news.ltn.com.tw/news/world/breakingnews/3021655', '0'], 
        ['https://news.ltn.com.tw/news/world/breakingnews/3022280', 'https://news.ltn.com.tw/news/world/breakingnews/3022280', 'https://news.ltn.com.tw/news/politics/paper/1341865'], 
        ['0', 'https://news.ltn.com.tw/news/world/breakingnews/2953408', 'https://news.ltn.com.tw/news/world/breakingnews/2953408'], 
        ['0', 'https://news.ltn.com.tw/news/world/breakingnews/3007651', 'https://news.ltn.com.tw/news/business/breakingnews/3021480'], 
        ['0', 'https://news.ltn.com.tw/news/politics/paper/1340424', 'https://news.ltn.com.tw/news/politics/breakingnews/3020277'], 
        ['0', 'https://news.ltn.com.tw/news/politics/breakingnews/3022664', 'https://news.ltn.com.tw/news/politics/breakingnews/3022664'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/2933215', 'https://news.ltn.com.tw/news/politics/breakingnews/3022692', 'https://news.ltn.com.tw/news/politics/breakingnews/3022694'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/2934119', 'https://news.ltn.com.tw/news/politics/breakingnews/3022666', 'https://news.ltn.com.tw/news/politics/breakingnews/3022419'], 
        ['https://news.ltn.com.tw/news/politics/breakingnews/3016660', 'https://news.ltn.com.tw/news/entertainment/breakingnews/3012386', 'https://news.ltn.com.tw/news/politics/breakingnews/3022617'], 
        ['https://news.ltn.com.tw/news/politics/paper/1335444', '0', 'https://news.ltn.com.tw/news/politics/breakingnews/3019446']
    ]
    content = event.message.text

    # if content == '傳送':
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(
    #             text='請選擇',
    #             quick_reply=QuickReply(
    #                 items=[
    #                     QuickReplyButton(
    #                         action=PostbackAction(label="label1", data="data1")
    #                     ),
    #                     QuickReplyButton(
    #                         action=MessageAction(label="label2", text="text2")
    #                     ),
    #                     QuickReplyButton(
    #                         action=DatetimePickerAction(label="label3",
    #                                                     data="data3",
    #                                                     mode="date")
    #                     ),
    #                     QuickReplyButton(
    #                         action=CameraAction(label="label4")
    #                     ),
    #                     QuickReplyButton(
    #                         action=CameraRollAction(label="label5")
    #                     ),
    #                     QuickReplyButton(
    #                         action=LocationAction(label="label6")
    #                     ),
    #                 ])))
    if content == '你好':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    if content == '我好':
        bubble_string = """
        {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "image",
                "url": "https://line-objects-dev.com/flex/bg/eiji-k-1360395-unsplash.jpg",
                "position": "relative",
                "size": "full",
                "aspectMode": "cover",
                "aspectRatio": "1:1",
                "gravity": "center"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "Brown Hotel",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                      },
                      {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                          },
                          {
                            "type": "text",
                            "text": "4.0",
                            "size": "sm",
                            "color": "#d6d6d6",
                            "margin": "md",
                            "flex": 0
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "¥62,000",
                        "color": "#a9a9a9",
                        "decoration": "line-through",
                        "align": "end"
                      },
                      {
                        "type": "text",
                        "text": "¥42,000",
                        "color": "#ebebeb",
                        "size": "xl",
                        "align": "end"
                      }
                    ]
                  }
                ],
                "position": "absolute",
                "offsetBottom": "0px",
                "offsetStart": "0px",
                "offsetEnd": "0px",
                "backgroundColor": "#00000099",
                "paddingAll": "20px"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "SALE",
                    "color": "#ffffff"
                  }
                ],
                "position": "absolute",
                "backgroundColor": "#ff2600",
                "cornerRadius": "20px",
                "paddingAll": "5px",
                "offsetTop": "10px",
                "offsetEnd": "10px",
                "paddingStart": "10px",
                "paddingEnd": "10px"
              }
            ],
            "paddingAll": "0px"
          }
        }
        """
        message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble_string))
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    if content == '推':
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text='推推推!'),
            ]
        )
    if content == '掰掰':
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='天線寶寶該說再見了')
            )
            line_bot_api.leave_group(event.source.group_id)
    if content == '福利熊':
        confirm_template = ConfirmTemplate(
                text='福利熊～熊福利～', 
                actions=[
                    MessageAction(label='one two 福利', text='one two 福利'),
                    MessageAction(label='請支援收銀', text='請支援收銀'),
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    if content == '我比較想看c0':
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,[
            ImageSendMessage(
                original_content_url='https://i.imgur.com/hCT0dQa.jpg',
                preview_image_url='https://i.imgur.com/hCT0dQa.jpg',
            ),
            TextSendMessage(
                text=profile.display_name
            ),           
            TextSendMessage(
                text='看完覺得?_?',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='我本來想斥責的,可是...', text='谷歌表單')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='根本成大田馥甄', text='谷歌表單')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='直接end，填表單', text='谷歌表單')
                        ),
                    ]
                )
            )
        ])
    if content == '喵':
        # 擷取 thecatapi.com 取得隨機的貓圖
        data = requests.get('https://api.thecatapi.com/v1/images/search?mime_types=jpg').json()
        # 取得回傳資料中的貓圖 URL
        cat_url = data[0]['url']
        line_bot_api.reply_message(
            event.reply_token,
            # 以圖片的方式回訊息
            ImageSendMessage(
                original_content_url=cat_url,
                preview_image_url=cat_url,
            ),
        )
    if content == '汪':
        # 擷取 thedogapi.com 取得隨機的狗圖
        data = requests.get('https://api.thedogapi.com/v1/images/search?mime_types=jpg').json()
        dog_url = data[0]['url']
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=dog_url,
                preview_image_url=dog_url,
            ),
        )
    # if content == 'buttons':
    #     buttons_template = ButtonsTemplate(
    #         title='My buttons sample', text='Hello, my buttons', actions=[
    #             URIAction(label='Go to line.me', uri='https://line.me'),
    #             PostbackAction(label='ping', data='ping'),
    #             PostbackAction(label='ping with text', data='ping', text='ping'),
    #             MessageAction(label='Translate Rice', text='米')
    #         ])
    #     template_message = TemplateSendMessage(
    #         alt_text='Buttons alt text', template=buttons_template)
    #     line_bot_api.reply_message(event.reply_token, template_message)
    ### 第一層-random ####
    if content == "熱搜":
        global total
        total=list(zip(today_keywords, today_keywords_choice, abstract, today_keywords_link_udn, today_keywords_link_ltn))
        random.shuffle(total)
        buttons_template = TemplateSendMessage(
            alt_text='新聞',
            template=ButtonsTemplate(
                title='選擇服務',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/2VLgoMk.jpg',
                actions=[
                    MessageTemplateAction(
                        label=total[0][0],
                        text=total[0][0]
                    ),
                    MessageTemplateAction(
                        label=total[1][0],
                        text=total[1][0]
                    ),
                    MessageTemplateAction(
                        label=total[2][0],
                        text=total[2][0]
                    ),
                    MessageTemplateAction(
                        label=total[3][0],
                        text=total[3][0]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        
        ####  第二層total-0 ####
    if content == total[0][0]:
        # random.seed(3)
        line_bot_api.reply_message(
            event.reply_token,[
            ImageSendMessage(
                original_content_url='https://i.imgur.com/tQikhCP.png',
                preview_image_url='https://i.imgur.com/tQikhCP.png',
            ),
            TextSendMessage(
                text='相關の關鍵字如下:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label=total[0][1][0], text=total[0][1][0])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=total[0][1][1], text=total[0][1][1])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=total[0][1][2], text=total[0][1][2])
                        ),
                    ]
                )
            )
        ])
        ####  第三層total-0 ####
    if content == total[0][1][0]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total[0][2][0]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total[0][3][0]+"\n自由時報ltn:\n"+total[0][4][0],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )
        ])
        ####  第三層total-1 ####
    if content == total[0][1][1]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total[0][2][1]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total[0][3][1]+"\n自由時報ltn:\n"+total[0][4][1],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )            
        ])
        ####  第三層total-2 ####
    if content == total[0][1][2]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total[0][2][2]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total[0][3][2]+"\n自由時報ltn:\n"+total[0][4][2],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )
        ])
        #### 如果不喜歡-random ####
    if content =="下一組":
        global total_2
        total_2=list(zip(today_keywords, today_keywords_choice, abstract, today_keywords_link_udn, today_keywords_link_ltn))
        random.shuffle(total_2)
        buttons_template = TemplateSendMessage(
            alt_text='新聞',
            template=ButtonsTemplate(
                title='選擇服務',
                text='請選擇',
                thumbnail_image_url='https://i.imgur.com/qKkE2bj.jpg',
                actions=[
                    MessageTemplateAction(
                        label=total_2[0][0],
                        text=total_2[0][0]
                    ),
                    MessageTemplateAction(
                        label=total_2[1][0],
                        text=total_2[1][0]
                    ),
                    MessageTemplateAction(
                        label=total_2[2][0],
                        text=total_2[2][0]
                    ),
                    MessageTemplateAction(
                        label=total_2[3][0],
                        text=total_2[3][0]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        ####  第二層total_2-0 ####
    if content == total_2[0][0]:
        # random.seed(3)
        line_bot_api.reply_message(
            event.reply_token,[
            ImageSendMessage(
                original_content_url='https://i.imgur.com/tQikhCP.png',
                preview_image_url='https://i.imgur.com/tQikhCP.png',
            ),
            TextSendMessage(
                text='相關の關鍵字如下:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label=total_2[0][1][0], text=total_2[0][1][0])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=total_2[0][1][1], text=total_2[0][1][1])
                        ),
                        QuickReplyButton(
                            action=MessageAction(label=total_2[0][1][2], text=total_2[0][1][2])
                        ),
                    ]
                )
            )
        ])
        ####  第三層total_2-0 ####
    if content == total_2[0][1][0]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total_2[0][2][0]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total_2[0][3][0]+"\n自由時報ltn:\n"+total_2[0][4][0],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )
        ])
        ####  第三層total_2-1 ####
    if content == total_2[0][1][1]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total_2[0][2][1]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total_2[0][3][1]+"\n自由時報ltn:\n"+total_2[0][4][1],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )            
        ])
        ####  第三層total_2-2 ####
    if content == total_2[0][1][2]:
        line_bot_api.reply_message(
            event.reply_token,[
            TextSendMessage(
                text="摘要:\n"+total_2[0][2][2]
            ),
            TextSendMessage(
                text="聯合報udn:\n"+total_2[0][3][2]+"\n自由時報ltn:\n"+total_2[0][4][2],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label='修但幾類', text='我比較想看c0')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='哈哈哈～單身狗', text='汪')
                        ),
                        QuickReplyButton(
                            action=MessageAction(label='讓我吸一張貓', text='喵')
                        ),
                    ]
                )
            )
        ])
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='🙂🙃'+'說點有意義的話好嗎'+'🙃🙂'))

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)

####################### 執行 Flask ######################
if __name__ == "__main__":
    app.run(debug=True)