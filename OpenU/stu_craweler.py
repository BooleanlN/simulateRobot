from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import sqlite3
import time
import re

reg = re.compile(r'^[A-Za-z]([.。．\s])*')
def simulate_browser(accounts,course_name=""):

    # n = browser.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
    # print('当前句柄: ', n)  # 会打印所有的句柄
    conn,table_name = model(course_name)
    # browser.switch_to_window(n[-1])
    for username,password in accounts:
        # 登陆跳转
        chromeOptions = webdriver.ChromeOptions()
        browser = webdriver.Chrome(chrome_options=chromeOptions)
        # browser.set_window_position(20, 40)
        # browser.set_window_size(1200, 800)

        browser.implicitly_wait(10)
        browser.maximize_window()
        browser.get("http://student.ouchn.cn/")
        account_input = browser.find_element_by_id("username")
        account_input.send_keys(username)
        password_input = browser.find_element_by_id("password")
        password_input.send_keys(password)
        login_btn = browser.find_element_by_css_selector("button[value='login']")
        login_btn.click()
        time.sleep(3)

        # 找到爬取题目的按钮
        sreach_window = browser.current_window_handle
        course_tds = browser.find_elements_by_css_selector("h3.media-title")
        course_links = browser.find_elements_by_class_name("bg-primary")
        index = 0
        courses = []
        while index < len(course_tds):
            course_title = course_tds[index].get_attribute("innerText").strip()
            print(course_title)
            if course_title != course_name:
                index += 1
                continue
            course_operation = course_links[index]
            course_operation.click()

            #打开形考任务，选择单元自测
            n = browser.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
            print('当前句柄: ', n)  # 会打印所有的句柄
            browser.switch_to_window(n[-1])
            index += 1
            browser.implicitly_wait(1)
            xinkao_btn = browser.find_element_by_css_selector("a[title='形考汇集']")
            xinkao_btn.click()
            browser.implicitly_wait(5)
            nodes = browser.find_elements_by_css_selector(".test")
            btns = [(node.find_element_by_tag_name("a"),node.find_element_by_tag_name("p").get_attribute("innerText"))for node in nodes if "单元自测" in node.get_attribute("innerText")
                    or "Self-test" in node.get_attribute("innerText") ]
            # need_clicks = browser.find_elements_by_css_selector(".section.main.aft")
            # print(len(need_clicks))
            # for need_click in need_clicks:
            #     if '形考任务' in need_click.get_attribute("innerText"):
            #         need_click.click()
            #         break
            # browser.implicitly_wait(10)
            # nodes = browser.find_elements_by_class_name("activityinstance")
            lll = len(btns)
            for xx in range(lll):
                test_name = btns[xx][1]
                time.sleep(3)
                btns[xx][0].click()
                # 考试入口页面
                browser.implicitly_wait(3)
                sreach_window = browser.current_window_handle
                a_btn = browser.find_elements_by_css_selector("td.lastcol")[0].find_element_by_tag_name("a")
                a_btn.click()

                # 试题页面
                try:
                    browser.implicitly_wait(3)
                    # question_num = len(browser.find_elements_by_class_name('.qnbutton')) - 1
                    count = 0
                    questions = browser.find_elements_by_css_selector(".qtext")
                    answers = browser.find_elements_by_class_name("answer")
                    if len(questions) != len(answers):
                        questions = questions[1:]
                    correct_answers = browser.find_elements_by_class_name("correct")
                    jndex = 0
                    kindex = 1
                    result = []
                    while jndex < len(answers):
                        count += 1
                        qtext = questions[jndex].get_attribute("innerHTML")
                        answer = answers[jndex].get_attribute("innerHTML")
                        correct_answer = correct_answers[kindex].get_attribute("innerText").lstrip()[:1]
                        jndex+=1
                        kindex+=2
                        result.append((0, qtext,
                                       answer
                                       ,correct_answer, course_name,
                                       test_name))
                    articles = browser.find_elements_by_class_name("multianswer")
                    # 随机题
                    if len(articles)!= 0:
                        for article in articles:
                            content = article.get_attribute("innerText").strip()
                            if "完型填空" in content:
                                #完型填空
                                print("完形填空")
                                question_type = 8
                                try:
                                    question_texts, question_answers, correct_answers = get_from_type8(article)
                                except Exception as e:
                                    continue
                            elif ( "阅读理解" in content and "从A、B、C三个选项中选出一个最佳选项" in content )or '翻译：' in content or "听力理解：请听下面的对话，根据对话内容从A、B、C三个选项中选出一个最佳选项" in content:
                                # 阅读理解补充对话
                                question_type = 3
                                try:
                                    question_texts, question_answers, correct_answers = get_from_type3(article)
                                except IndexError as e:
                                    continue
                            elif "听力理解：请听下面的对话，根据对话内容填入相应的句子或短语" in content:
                                question_type = 9
                                try:
                                    question_texts, question_answers, correct_answers = get_from_type9(article)
                                except IndexError as e:
                                    continue
                            elif "正确为“T”，错误为“F”" in content or "正确写" in content:
                                #阅读理解判断正误

                                question_type = 4
                                if "请听下面的对话" in content:
                                    questions_items = article.find_elements_by_tag_name("p")
                                    question_texts = []
                                    question_answers = []
                                    for item in questions_items:
                                        if item.get_attribute("id") != '':
                                            question_texts.append(item.get_attribute("innerHTML"))
                                            question_answers.append("TorF")
                                    selects = article.find_elements_by_tag_name("select")
                                    correct_answers = []
                                    for select in selects:
                                        option = select.find_element_by_css_selector("option[selected]")
                                        # correct_answers.append(re.sub(reg, "",, 1))
                                        correct_answers.append(option.get_attribute("innerHTML"))
                                else:
                                    try:
                                        question_texts, question_answers, correct_answers = get_from_type4(article)
                                    except IndexError as e:
                                        continue
                            elif "将对话补充完整" in content:
                                # 选项补充对话
                                question_type = 5
                                try:
                                    question_texts, question_answers, correct_answers = get_from_type5(article)
                                except IndexError as e:
                                    continue
                            else:
                                # UNKNOWN
                                question_type = 7
                                question_texts, question_answers, correct_answers = [],[],[]
                            for qtext,answer,correct_answer in zip(question_texts,question_answers,correct_answers):
                                asss = ''.join(answer)
                                result.append((question_type,qtext,asss,correct_answer, course_name,
                                       test_name))
                    else:
                        try:
                            article = browser.find_element_by_class_name("ddwtos")
                            content = article.find_element_by_class_name("formulation")
                            if "根据文章内容和所给信息将短文补充完整" in content.get_attribute("innerText"):
                                question_type = 6
                                questions_items = content.find_elements_by_css_selector("span.drag")
                                question_texts = []
                                for questions_item in questions_items:
                                    question_texts.append(questions_item.get_attribute("innerText"))
                                answers = content.find_elements_by_css_selector("input[type=hidden]")[1:]
                                correct_answer = []
                                for answer in answers:
                                    val = int(answer.get_attribute("value")) - 1
                                    correct_answers.append(re.sub(reg, "",question_texts[val], 1))
                                    # correct_answer.append(question_texts[val])
                                qtext = "填空题"
                                asss = "填空题"
                                correct_answer = "|".join(correct_answer)
                            else:
                                # UNKNOWN
                                question_type = 7
                                qtext, asss, correct_answer = "", "", ""
                            result.append((question_type, qtext, asss, correct_answer, course_name,
                                           test_name))
                        except Exception as e:
                            print("ERROR2！")
                            pass
                    for record in result:
                        c = conn.cursor()
                        try:
                            c.execute(
                                "INSERT INTO {}('qtype','qtext','answers','correct_answer','course_name','test_name') VALUES (?,?,?,?,?,?)".format(
                                    table_name), record)
                        except sqlite3.IntegrityError as e:
                            continue
                        conn.commit()
                except Exception as e:
                    print("ERROR！")
                    pass
                back_btn = browser.find_element_by_css_selector("a[title='形考汇集']")
                back_btn.click()
                browser.implicitly_wait(3)
                nodes = browser.find_elements_by_css_selector(".test")
                btns = [
                    (node.find_element_by_tag_name("a"), node.find_element_by_tag_name("p").get_attribute("innerText"))
                    for node in nodes if "单元自测" in node.get_attribute("innerText")
                    or "Self-test" in node.get_attribute("innerText")]
                    # need_clicks = browser.find_elements_by_css_selector(".section.main.aft")
                        # print(len(need_clicks))
                        # browser.implicitly_wait(10)
                        # for need_click in need_clicks:
                        #     cc  = need_click.get_attribute("innerText")
                        #     if '形考任务' in cc:
                        #         need_click.click()
                        #         browser.implicitly_wait(10)
                        #         nodes = browser.find_elements_by_class_name("activityinstance")
                        #         break

            browser.close()
            break
def get_from_type3(article):
    """"""
    question_items = article.find_elements_by_tag_name("p")
    items = []
    question_texts = []
    # question_texts = [question_item.get_attribute("innerText")[2:] for question_item in question_items if question_item.id != '']
    for gndex, question_item in enumerate(question_items):
        if question_item.get_attribute("id") != "":
            question_texts.append(question_item.get_attribute("innerHTML"))
            items.append(gndex)
    print(items)
    question_answers = []
    for iindex, item in enumerate(items):
        if iindex != len(items) - 1:
            answers = [xx.get_attribute("innerText") for xx in question_items[items[iindex] + 1:items[iindex + 1]]]
        else:
            answers = [xx.get_attribute("innerText") for xx in question_items[items[iindex] + 1:]]
        question_answers.append(answers)
    selects = article.find_elements_by_tag_name("select")
    correct_answers = []
    for sindex, select in enumerate(selects):
        option = select.find_element_by_css_selector("option[selected]")
        correct_option = int(option.get_attribute("value"))
        correct_answers.append(question_answers[sindex][correct_option].lstrip()[:1])
        # correct_answers.append(re.sub(reg,"",question_answers[sindex][correct_option],1))
    return question_texts,question_answers,correct_answers

def get_from_type4(article):
    """"""
    question_items = article.find_elements_by_tag_name("li")
    question_texts = []
    for item in question_items:
        # 题干
        kktext = item.get_attribute('innerText')
        kx = kktext.find('回答')
        question_texts.append(kktext[:kx])
    # 正误题无选项
    question_answers = ['T/F']*len(question_texts)

    selects = article.find_elements_by_tag_name("select")
    correct_answers = []
    for sindex, select in enumerate(selects):
        # 选项答案
        option = select.find_element_by_css_selector("option[selected]")
        correct_option = option.get_attribute("innerText")

        correct_answers.append(correct_option)
    return question_texts, question_answers, correct_answers

def get_from_type5(article):
    """"""
    question_items = article.find_elements_by_tag_name("p")
    question_texts = []
    # question_texts = [question_item.get_attribute("innerText")[2:] for question_item in question_items if question_item.id != '']
    question_answers = []
    for gndex, question_item in enumerate(question_items):
        if question_item.get_attribute("id") != "":
            question_texts.append(question_item.get_attribute("innerHTML"))
        if gndex >= len(question_items) - 5:
            # 收集答案
            question_answers.append(question_item.get_attribute("innerHTML")[2:])
    inputs = article.find_elements_by_css_selector("input.correct")
    correct_answers = []
    for sindex, input in enumerate(inputs):
        option = ord(input.get_attribute("value")) - ord('A')
        # correct_answers.append(question_answers[option])
        # correct_answers.append(re.sub(reg, "", question_answers[option], 1))
        correct_answers.append(question_answers[option].lstrip()[:1])
    return question_texts, question_answers, correct_answers
def get_from_type8(article):
    question_items = article.find_elements_by_tag_name("p")
    selects = article.find_elements_by_tag_name("select")
    numbers = len(selects)
    question_answers = []
    question_texts = []
    kkk = -1
    temp = []
    xfdfd = ""
    for gndex, question_item in enumerate(question_items):
        if question_item.get_attribute("id") != "":
            xfdfd = question_item.get_attribute("innerHTML")
            break
    for gndex in range(numbers):
        dsf = question_items[kkk - gndex].get_attribute('innerText')[1:].replace(" ","")
        index1 = dsf.find('A.')
        index2 = dsf.find('B.')
        index3 = dsf.find('C.')
        temp.append([dsf[index1:index2],dsf[index2:index3],dsf[index3:]])
        question_answers.append(question_items[kkk - gndex].get_attribute('innerText'))
        question_texts.append(xfdfd)

    correct_answers = []
    for sindex, select in enumerate(selects):
        option = select.find_element_by_css_selector("option[selected]")
        correct_option = int(option.get_attribute("value"))
        # correct_answers.append(re.sub(reg, "", temp[sindex][correct_option], 1))
        correct_answers.append(temp[sindex][correct_option].lstrip()[:1])
    return question_texts, question_answers, correct_answers

def get_from_type9(article):
    """听力理解"""
    question_items = article.find_elements_by_tag_name("p")
    question_texts = []
    question_answers = []
    kndex = 0
    for iindex in range(len(question_items)-1,-1,-1):
        if(question_items[iindex].get_attribute("id") ==  "" and question_items[iindex].get_attribute("innerText") != " "):
            question_answers.append(question_items[iindex].get_attribute("innerText"))
        else:
            kndex = iindex
            break
    while kndex >= 0:
        if(question_items[kndex].get_attribute("id")!="" and question_items[kndex].get_attribute("innerText") != " "):
            question_texts.append(question_items[kndex].get_attribute("innerHTML"))
        kndex += 1
    selects = article.find_elements_by_tag_name("select")
    correct_answers = []

    for sindex in range(len(selects)-1,-1,-1):
        option = selects[sindex].find_element_by_css_selector("option[selected]")
        correct_option = 5 - int(option.get_attribute("value"))
        # correct_answers.append(re.sub(reg,"",question_answers[sindex][correct_option],1))
        correct_answers.append( question_answers[sindex][correct_option].lstrip()[:1])
        if len(correct_answers) == len(question_texts):
            break
    return question_texts,question_answers,correct_answers
def get_users(filepath,course_name,count=5):
    """获取count个用户"""
    data = pd.read_excel(filepath)
    # print(data.head())
    res = [ (item[1][1],item[1][2]) for item in data.iterrows() if item[1][4] == course_name]
    # print(res[0])
    return res[:count]
def model(course_name):
    conn = sqlite3.connect("./questionDb.db")
    c = conn.cursor()
    table_name = c.execute("select table_name from course_table where course_name=?",(course_name,))
    table_name = table_name.fetchone()
    print(table_name)
    return conn,table_name[0]
if __name__ == '__main__':
    users = get_users("./accounts.xlsx","人文英语1")
    print("账号：",users)
    simulate_browser(users,"人文英语1")
