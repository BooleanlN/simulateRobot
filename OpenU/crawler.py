import re

from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import sqlite3
import time
reg = re.compile(r'^[A-Za-z]([.。．\s])*')
dics = {
    '0':'A',
    '1':'B',
    '2':'C',
    '3':'D',
    '4':'E'
}
def simulate_browser(proxy,accounts,course_name="",count=5):
    chromeOptions = webdriver.ChromeOptions()
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    # browser.set_window_position(20, 40)
    # browser.set_window_size(1200, 800)

    browser.implicitly_wait(10)
    browser.maximize_window()
    browser.get("http://www.ouchn.cn")
    time.sleep(3)
    # 登陆跳转
    teacher_btn = browser.find_element_by_css_selector("li[name='教师']")
    teacher_btn.click()
    time.sleep(3)
    n = browser.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
    print('当前句柄: ', n)  # 会打印所有的句柄
    conn,table_name = model(course_name)
    browser.switch_to_window(n[-1])
    for username,password in accounts:
        account_input = browser.find_element_by_id("username")
        account_input.send_keys(username)
        password_input = browser.find_element_by_id("password")
        password_input.send_keys(password)
        login_btn = browser.find_element_by_css_selector("button[value='login']")
        login_btn.click()
        time.sleep(3)
        sreach_window = browser.current_window_handle
        course_tds = browser.find_elements_by_css_selector(".bgcolor")
        index = 0
        courses = []
        while index < len(course_tds):
            course_id = course_tds[index].get_attribute("innerText").strip()
            course_title = course_tds[index + 1].get_attribute("innerText").strip()
            print(course_title)
            if course_title != course_name:
                index += 5
                continue
            course_depart = course_tds[index + 2].get_attribute("innerText").strip()
            course_role = course_tds[index + 3].get_attribute("innerText").strip()
            course_operation = course_tds[index + 4]
            course_operation.click()
            #新页面打开
            n = browser.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
            print('当前句柄: ', n)  # 会打印所有的句柄
            browser.switch_to_window(n[-1])
            # ActionChains(browser).key_down(Keys.CONTROL).send_keys("w").key_up(Keys.CONTROL).perform()
            # course_link = course_tds[index + 4].get_attribute("href")
            index += 5
            # courses.append((course_id,course_title,course_depart,course_role,course_link))
            browser.implicitly_wait(1)
            need_clicks = browser.find_elements_by_css_selector(".section.main.aft")
            print(len(need_clicks))
            xinkaobtns = []
            for need_click in need_clicks:
                if '形考任务' in need_click.get_attribute("innerText"):
                    need_click.click()
                    break
            time.sleep(2)
            fndex = 0
            nodes = browser.find_elements_by_class_name("activityinstance")
            count = len(nodes)
            while fndex < count:
                if "单元自测" in nodes[fndex].get_attribute("innerText"):
                    print(nodes[fndex].get_attribute("innerText"))
                    test_name = nodes[fndex].get_attribute("innerText")
                    nodes[fndex].click()
                    browser.implicitly_wait(3)
                    sreach_window = browser.current_window_handle
                    a_btn = browser.find_elements_by_css_selector(".btn-secondary")[1]
                    a_btn.click()
                    browser.implicitly_wait(3)
                    a_btns = browser.find_elements_by_tag_name("a")
                    for a_btn in a_btns:
                        if a_btn.get_attribute("innerText") == '也显示已自动评分的题目':
                            a_btn.click()
                            break
                    browser.implicitly_wait(3)
                    exam_btns = browser.find_elements_by_css_selector("a.gradetheselink")
                    jndex = 1
                    result = []
                    while jndex < len(exam_btns):
                        exam_btns[jndex].click()
                        questions = browser.find_elements_by_css_selector(".qtext")
                        if len(questions) != 0:
                            # try:
                            block = browser.find_element_by_css_selector(".multichoice")
                            right_answer = block.find_elements_by_tag_name("label")
                            answers = browser.find_elements_by_css_selector(".answer")
                            right_answers = browser.find_elements_by_css_selector(".rightanswer")[0].get_attribute("innerText")[6:]
                            kkk = 0
                            for la in right_answer:
                                if right_answers in la.get_attribute("innerText"):
                                    break
                                else:
                                    kkk += 1
                            result.append((0, questions[0].get_attribute("innerHTML"),
                                           answers[0].get_attribute("innerHTML")
                                           , dics[str(kkk)], course_name,
                                           test_name))
                            # except Exception as e:
                            #     pass
                        else:
                            pass
                            # articles = browser.find_elements_by_class_name("multianswer")
                            # # 随机题
                            # if len(articles) != 0:
                            #     for article in articles:
                            #         content = article.get_attribute("innerText").strip()
                            #         if "完型填空" in content or "完形填空" in content:
                            #             # 完型填空
                            #             print("完形填空")
                            #             question_type = 8
                            #             try:
                            #                 question_texts, question_answers, correct_answers = get_from_type8(
                            #                     article)
                            #             except Exception as e:
                            #                 continue
                            #         elif (
                            #                 "阅读理解：选择题" in content) or '翻译' in content or "听力理解：请听下面的对话，根据对话内容从A、B、C三个选项中选出一个最佳选项" in content:
                            #             # 阅读理解补充对话
                            #             question_type = 3
                            #             try:
                            #                 question_texts, question_answers, correct_answers = get_from_type3(
                            #                     article)
                            #             except IndexError as e:
                            #                 continue
                            #         elif "听力理解：请听下面的对话，根据对话内容填入相应的句子或短语" in content:
                            #             question_type = 9
                            #             try:
                            #                 question_texts, question_answers, correct_answers = get_from_type9(
                            #                     article)
                            #             except IndexError as e:
                            #                 continue
                            #         elif "阅读理解：判断正误题" in content or "阅读理解：判断题" in content or "判断正误" in content:
                            #             # 阅读理解判断正误
                            #
                            #             question_type = 4
                            #             if "听录音，判断正误" in content:
                            #                 questions_items = article.find_elements_by_tag_name("p")
                            #                 question_texts = []
                            #                 question_answers = []
                            #                 for item in questions_items:
                            #                     if item.get_attribute("id") != '':
                            #                         question_texts.append(item.get_attribute("innerHTML"))
                            #                         question_answers.append("TorF")
                            #                 selects = article.find_elements_by_tag_name("select")
                            #                 correct_answers = []
                            #                 for select in selects:
                            #                     option = select.find_element_by_css_selector("option[selected]")
                            #                     # correct_answers.append(re.sub(reg, "",, 1))
                            #                     correct_answers.append(option.get_attribute("innerHTML"))
                            #             else:
                            #                 try:
                            #                     question_texts, question_answers, correct_answers = get_from_type4(
                            #                         article)
                            #                 except IndexError as e:
                            #                     continue
                            #         elif "听录音，完成对话" in content:
                            #             # 选项补充对话
                            #             question_type = 5
                            #             try:
                            #                 question_texts, question_answers, correct_answers = get_from_type5(
                            #                     article)
                            #             except IndexError as e:
                            #                 continue
                            #         else:
                            #             # UNKNOWN
                            #             question_type = 7
                            #             question_texts, question_answers, correct_answers = [], [], []
                            #         for qtext, answer, correct_answer in zip(question_texts, question_answers,
                            #                                                  correct_answers):
                            #             asss = ''.join(answer)
                            #             result.append((question_type, qtext, asss, correct_answer, course_name,
                            #                            test_name))
                            # else:
                                # try:
                                #     article = browser.find_element_by_class_name("ddwtos")
                                #     content = article.find_element_by_class_name("formulation")
                                #     if "根据文章内容和所给信息将短文补充完整" in content.get_attribute("innerText"):
                                #         question_type = 6
                                #         questions_items = content.find_elements_by_css_selector("span.drag")
                                #         question_texts = []
                                #         for questions_item in questions_items:
                                #             question_texts.append(questions_item.get_attribute("innerText"))
                                #         answers = content.find_elements_by_css_selector("input[type=hidden]")[1:]
                                #         correct_answer = []
                                #         for answer in answers:
                                #             val = int(answer.get_attribute("value")) - 1
                                #             correct_answers.append(re.sub(reg, "", question_texts[val], 1))
                                #             # correct_answer.append(question_texts[val])
                                #         qtext = "填空题"
                                #         asss = "填空题"
                                #         correct_answer = "|".join(correct_answer)
                                #     else:
                                #         # UNKNOWN
                                #         question_type = 7
                                #         qtext, asss, correct_answer = "", "", ""
                                #     result.append((question_type, qtext, asss, correct_answer, course_name,
                                #                    test_name))
                                # except Exception as e:
                                #     print("ERROR2！")
                                #     pass
                        browser.back()
                        browser.implicitly_wait(3)
                        exam_btns = browser.find_elements_by_css_selector("a.gradetheselink")
                        jndex += 2
                    print(result)
                    for record in result:
                        print(record)
                        c = conn.cursor()
                        try:
                            c.execute(
                                "INSERT INTO {}('qtype','qtext','answers','correct_answer','course_name','test_name') VALUES (?,?,?,?,?,?)".format(
                                    table_name), record)
                        except sqlite3.IntegrityError as e:
                            continue
                        conn.commit()
                    back_btn = browser.find_elements_by_css_selector("a[title='课程首页']")[0]
                    back_btn.click()
                    time.sleep(3)
                    need_clicks = browser.find_elements_by_css_selector(".section.main.aft")
                    xinkaobtns = []
                    for need_click in need_clicks:
                        if '形考任务' in need_click.get_attribute("innerText"):
                            need_click.click()
                            break
                    nodes = browser.find_elements_by_class_name("activityinstance")
                fndex += 1
def get_users(filepath,course_name):
    data = pd.read_excel(filepath)
    # print(data.head())
    res = [ (item[1][1],item[1][2]) for item in data.iterrows() if item[1][4] == course_name]
    # print(res[0])
    return res
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
        correct_answers.append(re.sub(reg,"",question_answers[sindex][correct_option],1))
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
        correct_answers.append(re.sub(reg, "", question_answers[option], 1))
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
        correct_answers.append(re.sub(reg, "", temp[sindex][correct_option], 1))
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
        correct_answers.append(re.sub(reg,"",question_answers[sindex][correct_option],1))
        if len(correct_answers) == len(question_texts):
            break
    return question_texts,question_answers,correct_answers
def model(course_name):
    conn = sqlite3.connect("./questionDb.db")
    c = conn.cursor()
    table_name = c.execute("select table_name from course_table where course_name=?",(course_name,))
    table_name = table_name.fetchone()
    print(table_name)
    return conn,table_name[0]
if __name__ == '__main__':
    # accounts = get_users("./accouts/其他科目1.xlsx",'理工英语1')
    accounts = [('hsddysm','650710ysm!')]
    simulate_browser([],accounts,course_name="商务英语1")