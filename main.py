import requests
import re
import configparser

# 读取配置文件
cf = configparser.ConfigParser()
cf.read("config.ini", encoding='utf-8')

username = cf.get('config', 'username')
print("用户名为：" + username)
password = cf.get('config', 'password')
print("密码为：" + password)

login_url = 'https://apii.lynu.edu.cn/api-auth/login/'
noon_url = 'https://apii.lynu.edu.cn/v1/noons/?format=api'
morning_url = 'https://apii.lynu.edu.cn/v1/temperatures/?format=api'

req = requests.Session()


def login(login_url, username, password):
    try:
        print("开始登录")
        # 请求头
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.88 Safari/537.36',
            'referer': 'https://apii.lynu.edu.cn/api-auth/login/?next=/v1/noons/'
        }
        # 获取登录页面token(1.登录页面的csrftoken)
        r = req.get(login_url, headers=login_headers, allow_redirects=False)
        reg = r'<input type="hidden" name="csrfmiddlewaretoken" value="(.*)">'
        pattern = re.compile(reg)
        result = pattern.findall(r.content.decode('utf-8'))
        login_token = result[0]
        print("获取到登录页面token：" + login_token)

        # postdata
        my_data = {
            'csrfmiddlewaretoken': login_token,
            'next': '/v1/noons/',
            'username': username,
            'password': password,
            'submit': 'Log in'
        }

        # 登录获取cookie(2.当前用户的csrftoken和sessionid)
        response = req.post(login_url, headers=login_headers, data=my_data, allow_redirects=False)
        response.encoding = response.apparent_encoding
        cookie = requests.utils.dict_from_cookiejar(response.cookies)
        print(f"statusCode = {response.status_code}")
        print("获取到cookie：")
        print(cookie)
        return cookie
    except:
        print("###登录出现错误###")


def noon_sign(cookie):
    print("开始午报打卡")
    # 请求头
    noon_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36',
        'referer': 'https://apii.lynu.edu.cn/v1/noons/'
    }
    # 获取noon页面token
    r = req.get(noon_url, headers=noon_headers, cookies=cookie, allow_redirects=False)
    reg = r'csrfToken: "(.*)"'
    pattern = re.compile(reg)
    result = pattern.findall(r.content.decode('utf-8'))
    noon_token = result[0]
    print("获取到noon页面token：" + noon_token)

    noon_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36',
        'referer': 'https://apii.lynu.edu.cn/v1/noons/',
        'X-CSRFToken': noon_token
    }
    noon_data = {
        'condition': 'A',
        'value': '36.5'
    }
    noon = req.post(noon_url, data=noon_data, headers=noon_headers, cookies=cookie, allow_redirects=False)
    print(f"statusCode = {noon.status_code}")
    if noon.status_code == 201:
        print("===午报打卡成功===")
    else:
        print("###午报打卡出现错误###")


def morning_sign(cookie):
    print("开始晨报打卡")
    # 请求头
    morning_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36',
        'referer': 'https://apii.lynu.edu.cn/v1/temperatures/?format=api'
    }
    # 获取temperatures页面token
    r = req.get(noon_url, headers=morning_headers, cookies=cookie, allow_redirects=False)
    reg = r'csrfToken: "(.*)"'
    pattern = re.compile(reg)
    result = pattern.findall(r.content.decode('utf-8'))
    morning_token = result[0]
    print("获取到morning页面token：" + morning_token)

    morning_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36',
        'referer': 'https://apii.lynu.edu.cn/v1/temperatures/?format=api',
        'X-CSRFToken': morning_token
    }
    morning_data = {
        "value": "36.5",
        "condition": "A",
        "home_condition": "A",
        "watched": 'false',
        "watched_location": "",
        "stayed": 'false',
        "stayed_contacted": 'false',
        "family_conditions": "",
        "is_contacted": 'false',
        "contacted_health": "",
        "personid": ""
    }
    noon = req.post(morning_url, data=morning_data, headers=morning_headers, cookies=cookie, allow_redirects=False)
    print(f"statusCode = {noon.status_code}")
    if noon.status_code == 201:
        print("===晨报打卡成功===")
    else:
        print("###晨报打卡出现错误###")


if __name__ == "__main__":
    coke = login(login_url, username, password)
    noon_sign(coke)
    morning_sign(coke)
    input('Press <Enter>')

