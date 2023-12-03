# 作者123
# 开发时间：
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
#每次爬取就改变这两个参数  a1='从零开始数的课程位数',n7='你想从哪个数排列你的作业'
a1=input('从零开始数的课程位数')
a1=int(a1)
n7=input('你想从哪个数排列你的作业')
n7=int(n7)



#以下为往登录界面注入课程界面的cookie并跳转到课程界面的代码
# 打开浏览器
wb = webdriver.Chrome()
wb.maximize_window()    #这行代码让浏览器全屏运行
url = "https://sso.icve.com.cn/sso/auth?mode=simple&source=2&redirect=https%3A%2F%2Fuser.icve.com.cn%2Fcms%2F"
wb.get(url)
# a=wb.get_cookies()
# print(a)
time.sleep(5)
wb.delete_all_cookies()
time.sleep(2)
with open('zhihuizhijiao_cookies.txt','r', encoding='utf-8') as f:
    listCookies = json.loads(f.read())
#以下为循环，将获取的课程界面的cookie里的前12个domain的值都改为sso.icve.com.cn（最后一个domain值为.icve.com.cn 若把这个也改了，就会一直卡在一个界面，没发跳转到课程界面。我猜测这个domain值是网页的父url，网站会检测它。这点网上没说，难怪之前把domain值全改了一直卡在界面。），其实应该在cookies文件写入前就做的
n=0
for i in listCookies:
    if n<=11:
        listCookies[n]['domain']='sso.icve.com.cn'
        n+=1
    else:
        break
# 删除cookie里的expiry，不然出错
for cookie in listCookies:
    if 'expiry' in cookie:    #删除expiry与其值
        del cookie['expiry']
    # if 'domain' in cookie:     #替换字典里domain的值,但这里有个大坑，listCookies里的最后一个domain的值不能改
    # 	cookie['domain'] = 'sso.icve.com.cn'
    wb.add_cookie(cookie)
print(listCookies)
time.sleep(2)
wb.refresh()
time.sleep(3)
wb.get('https://user.icve.com.cn/learning/u/student/teaching/index.action')

time.sleep(3)
n1=wb.find_elements(By.XPATH,'//*[@href="javascript:"]')
n1[a1].click()       #这行代码[]里填的是要爬取的课程位数（从零开始数）
# n7=101   n7是方便作业下载完成后排序的
time.sleep(8)
wb.switch_to.window(wb.window_handles[1])
# input('等待回车键结束程序')
# n2=wb.find_element(By.XPATH,'//*[@id="showMenus_stype"]').click() #有的课程不用点这个按钮，报错就加上
time.sleep(3)
n3=wb.find_element(By.XPATH,'//*[@class="coursespace icon-examStroke"]').click()
time.sleep(3)
#以下为下拉到作业目录的最底部
# js="document.documentElement.scrollTop=document.documentElement.scrollHeight"
# wb.execute_script(js)
# js="var action=document.documentElement.scrollTop=10000"
# wb.execute_script(js)
wb.switch_to.window(wb.window_handles[1])
# time.sleep(2)
# input('等待回车键结束程序')
# wb.switch_to.frame('contentIframe')

#智慧职教的“查看作业”按钮是放在两层iframe里的，要一层层进去，才能定位到“查看作业”，以后得在element里多用ctrl+f来看看有无多层iframe嵌套（其实看选中元素看后一层层看他的上层父标签就好了，要注意有无frame之类的标签，不然就定位不到元素。真是个大坑）
iframe = wb.find_element(By.ID,'mainContent')
wb.switch_to.frame(iframe)
iframe = wb.find_element(By.ID,'examIframe')
wb.switch_to.frame(iframe)
#获取list的长度
time.sleep(2)
page_link=wb.find_elements(By.XPATH,'//*[@id="toolBar_pageLink"]')
page_num=len(page_link)
#以下为找到“每页几条”，然后把他设为30条
element1 = wb.find_element(By.XPATH, '//*[@id="pageSize_select"]')
wb.execute_script("arguments[0].scrollIntoView();", element1)
element1.click()
time.sleep(2)
element2 = wb.find_element(By.XPATH, '//*[@id="pageSize_select"]/option[3]')
element2.click()
time.sleep(2)
#以下进入循环爬取作业文本的代码
n5=0
n6=1

while True:
    #进入while后好像会回到默认的窗口，所以这里还要指定一下窗口
    wb.switch_to.window(wb.window_handles[1])  #窗口从零开始数
    iframe = wb.find_element(By.ID, 'mainContent')
    wb.switch_to.frame(iframe)
    iframe = wb.find_element(By.ID, 'examIframe')
    wb.switch_to.frame(iframe)
    homework_num = wb.find_element(By.XPATH, '//*[@id="rowCount"]').text  # 作业条数
    n4 = wb.find_elements(By.XPATH, '//*[@name="viewrecord_btn"]')  #一页中查看作业的按钮列表(这个name值可以获取进行中和已结束的作业列表)
    #以下为找到对应的查看作业按钮并点击
    element =n4[n5]
    wb.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)
    n4[n5].click()
    # input()
    wb.switch_to.window(wb.window_handles[2])  #将目标转向打开的查看作业窗口
    time.sleep(3)
    #以下为获取作业标题和文本并保存
    homework_title = wb.find_element(By.XPATH, '//*[@id="paperTitle"]').text
    homework = wb.find_element(By.XPATH, '//*[@id="paperContent"]').text
    #获取课程名称
    #以下为处理文本
    text=homework
    res1 = re.sub("．\n", ' ', text)
    with open(fr'D:\pythonProject\zhijiaoyun\get_homework\诊断学\{n7}{homework_title}.docx', 'w', encoding='utf-8') as f:
                 f.write(homework_title + res1)
    print(homework_title+'已保存')
    wb.close()   #此行为写入作业后关闭查看作业的页面
    wb.switch_to.window(wb.window_handles[1])
    n5+=1
    n6+=1
    n7+=1
    #一上实现爬取页面所有作业并保存的功能
    if n6 - 1 == homework_num:  #这个if实现翻页功能
        n5=0
        n6=1
        #未施工，这一部分代码要实现点击下一页的功能
        break




        #这一部分代码要判断页数是否到达最大页数，思路为获取页数，放进list中，然后输出有几个元素.不过第一个if里设置一个页面有30条作业，应该够用。不过作业超过30条的话还是得写






