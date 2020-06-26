import urllib.request
import requests
import json
from selenium import webdriver
from PIL import Image,ImageEnhance
from pytesseract import image_to_string
import base64
import time
def proxy_pool():
    r = requests.get("http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=e513a5f03aae4e30825af4ec66be2673&count=10&expiryDate=0&format=1&newLine=2")
    proxy_list = []
    if r.status_code == 200:
        msg = json.loads(r.text)
        proxy_list = msg['msg']
    return proxy_list

def request_web(proxy_list):
    host = "http://zzx.ouchn.edu.cn/edu/public/student/#/login"
    url = "api/student/login"
    s = requests.Session()
    data = {
        'username':'13164605700',
        'userpass':'12345678',
        'isCheck':1
    }
    ua_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"
    }
    r = s.post(host + url,data=data,headers=ua_headers)
    student_info = json.loads(r.text)['data']
    print(r.cookies)
    cookie_str = ""
    cookies = []
    for key,value in r.cookies.items():
        cookies.append(key + "=" + value)
    cookie_str = "; ".join(cookies)
    print(cookie_str)
    url_courseList = "api/student/getCourseList"
    data2 = {
        "post_type": 1,
        "token":student_info['token'],
        #"token":"eyJleHBfdGltZSI6NzIwMCwiaG9zdCI6ImVkdS5jbiIsInVzZXJfbmFtZSI6IjQ0MTIyNDE5OTEwNDIxNDg0MyIsInVzZXJfdHlwZSI6InN0dWRlbnQiLCJ0aW1lIjoxNTg2NzkzMTQ2fQ==",
        "username":student_info["username"],
        "usertype":student_info["usertype"]
    }
    print(data2)
    headers = {
        # "Cookie":cookie_str,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Content-type":"application/x-www-form-urlencoded;charset=UTF-8"
    }
    r_courses = s.post(host + url_courseList,data=json.dumps(data2),headers=headers,cookies=r.cookies)

    print(r_courses.text)
def simulate_browser(proxy,username,password,result,num=10):
    print('num:',num)
    """模拟浏览器行为"""
    chromeOptions = webdriver.ChromeOptions()
    count = 0
    if proxy is not None:
        chromeOptions.add_argument("--proxy-server=http://{}:{}".format(proxy['ip'], proxy['port']))
    browser = webdriver.Chrome(chrome_options=chromeOptions)
    #browser.set_window_position(20, 40)
    # browser.set_window_size(1200, 800)

    browser.implicitly_wait(10)
    browser.maximize_window()
    browser.get("http://zzx.ouchn.edu.cn/edu/public/student")
    # print(browser.page_source)
    time.sleep(3)
    verifycode = capture_img(browser)
    #登录
    username_input = browser.find_element_by_css_selector("input[placeholder='账号/用户名/手机号']")
    username_input.send_keys(username)
    pass_input = browser.find_element_by_css_selector("input[type=password]")
    pass_input.send_keys(password)
    element = browser.find_element_by_css_selector("input[name=password]")
    # inp = input("输入验证码：")
    element.send_keys(str(verifycode))
    btn = browser.find_element_by_class_name("logC_btn")
    btn.click()
    time.sleep(3)

    # 个人页面
    sreach_window = browser.current_window_handle
    studys = browser.find_elements_by_class_name("study")
    # progresss = browser.find_elements_by_css_selector("span.jdb")
    # for progress in range(1,len(progresss)):
    #     if(progresss[progress].get_attribute("innerText")[:-1]=='100'):
    #         print(progress-1)
    #         studys.pop(progress-1)
    length = len(studys)
    print("未完成的课程数：{}".format(length))
    if(length == 0):
        while length == 0:
            verifycode = capture_img(browser)
            element.clear()
            element.send_keys(str(verifycode))
            time.sleep(3)
            btn.click()
            time.sleep(3)
            sreach_window = browser.current_window_handle
            studys = browser.find_elements_by_class_name("study")
            # progresss = browser.find_elements_by_css_selector("span.jdb")
            # for progress in range(1, len(progresss)):
            #     if (progresss[progress].get_attribute("innerText")[:-1] == '100'):
            #         studys.pop(progress - 1)
            length = len(studys)
            print("未完成的课程数：{}".format(length))
    for study_index in range(length):
        sreach_window = browser.current_window_handle
        studys = browser.find_elements_by_class_name("study")
        # progresss = browser.find_elements_by_css_selector("span.jdb")
        # for progress in range(1, len(progresss)):
        #    # print((progresss[progress].get_attribute("innerText")[:-1]))
        #     if (progresss[progress].get_attribute("innerText")[:-1] == '100'):
        #         studys.pop(progress - 1)
        study_btn = studys[study_index]
        study_btn.click()
        time.sleep(3)
        # 学习页面
        sreach_window = browser.current_window_handle
        need_study_items = browser.find_elements_by_class_name("video_process")
        for item in need_study_items:
            progress = int(item.get_attribute("innerText")[:-1])
            #print(progress)
            if progress == 100:
                continue
            #print(item)
            print("开始学习。。。")
            show_chapter = browser.find_element_by_css_selector(".icon_chapter")
            show_chapter.click()
            titles = browser.find_elements_by_class_name("title")
            for title in titles[:-1]:
                title.click()
            time.sleep(3)
            item.click()
            time.sleep(3)
            sreach_window = browser.current_window_handle
            rights = browser.find_elements_by_class_name("see")
            for right in rights:
                right.click()
            time.sleep(3)
            # 答题
            answers = browser.find_elements_by_css_selector(".right_key > div > span")
            answer_texts = [tag2num(answer.text[-1:]) for answer in answers]
            ans_items = browser.find_elements_by_class_name("answer")
            print(len(ans_items))
            for index in range(len(answer_texts)):
                print(answer_texts[index] + 3 * index)
                if answer_texts[index] + 3 * index < len(ans_items):
                    ans_items[answer_texts[index] + 3 * index].click()
            # 播放下一个
            video = browser.find_element_by_id("myVideo")
            duration = float(video.get_attribute("duration"))
            time.sleep(30)
            sreach_window = browser.current_window_handle
            while True:
                try:
                    sreach_window = browser.current_window_handle
                    next = browser.find_element_by_class_name("nextbtn")
                    next.click()
                    break
                except Exception as e:
                    print("播放中....")
                    for index in range(len(answer_texts)):
                        print(answer_texts[index] + 3 * index)
                        if answer_texts[index] + 3 * index < len(ans_items):
                            ans_items[answer_texts[index] + 3 * index].click()
                    time.sleep(30)
                    continue
            # print(next)
            # while next==None:
            #     time.sleep(100)
            # next.click()
            count+=1
            result[username]+=1
            print("结束学习，学习视频+1")
            if count > num:
                print(count,num)
                print("已完成此次学习任务")
                return count
            time.sleep(3)
        browser.back()
    return count
def tag2num(char):
    if char == 'A':
        return 0
    elif char == 'B':
        return 1
    return 2
def capture_img(browser):
    """截取验证码图片"""
    browser.get_screenshot_as_file('screenshot.png')
    element = browser.find_element_by_id('verifyCanvas')
    left = int(element.location['x'])
    top = int(element.location['y'])
    right = int(element.location['x'] + element.size['width'])
    bottom = int(element.location['y'] + element.size['height'])
    width = int(element.size['height'])
    height = int(element.size['height'])
    im = Image.open('screenshot.png')
    im = im.crop((1900, 800, 2200,900))
    im.save('code.png')
    code = Image.open("code.png")
    sharp_img = ImageEnhance.Contrast(code).enhance(2.0)
    sharp_img.save("code_sharp.png")
    sharp_img.load()
    verifycode = recognize_cap('code_sharp.png')['words_result'][0]['words']
    return verifycode
def recognize_cap(imgsrc):
    """百度接口识别验证码"""
    img = Image.open(imgsrc)
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=yzGXBg6ZZVQgPvPf3cvGhgxA&client_secret=kOxz14WN53OS5xPsDbEaw6GZ2qfYNiK2'
    response = requests.get(host)
    token = response.json()['access_token']
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(imgsrc, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}
    access_token = token
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        print(response.json())
    return response.json()
if __name__ == '__main__':
   #proxy_list = proxy_pool()
   # simulate_browser(None)
   request_web(None)
   #recognize_cap()
