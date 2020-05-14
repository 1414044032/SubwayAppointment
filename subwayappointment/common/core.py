import requests
import json
import urllib3

"""
https://webui.mybti.cn/#/login
"""
# 禁用安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

default_header = {
    'Host': 'webapi.mybti.cn',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://webui.mybti.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1295.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
    'Referer': 'https://webui.mybti.cn/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
}

header = {
    'Host': 'webapi.mybti.cn',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://webui.mybti.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1295.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
    'Authorization': 'NmY3ZjRhNzktMWY2Yy00MGZjLWI3NTQtOTkxZDRlYmZjYjNiLDE1OTAwNTk5OTUzNjYsWGdDN3dLcG1aQW92Y2h4Y1NTZ0R3UHBTeTVvPQ==',
    'Referer': 'https://webui.mybti.cn/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
}

# 发送验证码
send_code_uri = "https://webapi.mybti.cn/User/SendVerifyCode"
send_code_params = {
    "phoneNumber": None,
    "clientid": "7e80a759-5bf3-4504-bfab-71572b025005"
}

# 登录接口
sh_login_uri = "https://webapi.mybti.cn/User/SignUp"
sh_login_params = {
    "clientId": "7e80a759-5bf3-4504-bfab-71572b025005",
    "openId": "",
    "phoneNumber": None,
    "verifyCode": None
}

# 预约接口
sh_record_uri = "https://webapi.mybti.cn/Appointment/CreateAppointment"
sh_record_parms = {
    "lineName": "昌平线",
    "snapshotWeekOffset": 0,
    "stationName": "沙河站",
    "enterDate": "20200310",
    "snapshotTimeSlot": "0630-0930",
    "timeSlot": "0900-0910"}

# 判断是否预约
sh_check_record_uri = "https://webapi.mybti.cn/AppointmentRecord/GetAppointmentList?status=0&lastid="


def people_insert_record(accesstoken, enter_date, time_solt='0900-0910', ):
    request_header = {
        'Host': 'webapi.mybti.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://webui.mybti.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1295.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.5 WindowsWechat',
        'Authorization': accesstoken,
        'Referer': 'https://webui.mybti.cn/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4'
    }
    data = {
        "lineName": "昌平线",
        "snapshotWeekOffset": 0,
        "stationName": "沙河站",
        "enterDate": enter_date,
        "snapshotTimeSlot": "0630-0930",
        "timeSlot": time_solt
    }
    if check_record(request_header):
        result = requests.post(sh_record_uri, json=data, headers=request_header,
                               verify=False)
        response_dict = json.loads(result.text, encoding='utf-8')
        return response_dict['balance']
    else:
        return -1


# 查看结果
def check_record(header):
    result = requests.get("https://webapi.mybti.cn/AppointmentRecord/GetAppointmentList?status=0&lastid=",
                          headers=header,
                          verify=False)
    response_dict = json.loads(result.text, encoding='utf-8')
    if response_dict:
        return False
    else:
        return True
    # allowCancelStatus = response_dict['allowCancelStatus']
    # arrivalStatus = response_dict['arrivalStatus']
    # newStatus = response_dict['newStatus']


# 预约进站
def insert_record():
    url = "https://webapi.mybti.cn/Appointment/CreateAppointment"
    data = {"lineName": "昌平线", "snapshotWeekOffset": 0, "stationName": "沙河站", "enterDate": "20200310",
            "snapshotTimeSlot": "0630-0930", "timeSlot": "0900-0910"}
    result = requests.post(url, json=data, headers=header,
                           verify=False)
    print(result.text)


# 取消进站
def delete_record(id):
    url = "https://webapi.mybti.cn/AppointmentRecord/CancelAppointment?id={}".format(id)
    result = requests.get(url, headers=header,
                          verify=False)
    print(result.text)


def get_auth():
    result = requests.get("https://webapi.mybti.cn/User/GetWXUserInfoAndUpdate?code=071SATlf12DUNt0cYTmf1BVQlf1SATlf",
                          headers=header,
                          verify=False)
    print(result.text)


# 发送验证码
def send_code(phone):
    send_code_params['phoneNumber'] = phone
    requests.get(send_code_uri, params=send_code_params, headers=default_header,
                 verify=False)
    return True


# 登录
def sh_login(phone, check_code):
    sh_login_params['phoneNumber'] = phone
    sh_login_params['verifyCode'] = check_code
    response = requests.post(url=sh_login_uri, json=sh_login_params, headers=default_header,
                             verify=False)

    return response.status_code, response.text


# 解析登录响应
def sh_login_response_format(response):
    response_dict = json.loads(response, encoding='utf-8')
    accesstoken = response_dict['accesstoken']
    refreshtoken = response_dict['refreshtoken']
    headimgUrl = response_dict['userInfo']['headimgUrl']
    return 0, accesstoken, refreshtoken, headimgUrl
