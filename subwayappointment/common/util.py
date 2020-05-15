#!/usr/bin/env python
# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
import datetime


def send_sms(mtname):
    client = AcsClient('LTAImDkHGeA9p55u', 'XfVTFrwBYyJQUS8oziMWw6a3LrjAr6', 'cn-hangzhou')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', "18404975197")
    request.add_query_param('SignName', "王刘奇")
    request.add_query_param('TemplateCode', "SMS_190271189")
    # 您的${mtname}已于${submittime}获取成功，特此通知
    TemplateParam = {
        'mtname': mtname,
        'submittime': datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    }
    request.add_query_param('TemplateParam', json.dumps(TemplateParam))

    response = client.do_action(request)
    return str(response, encoding='utf-8')


# if __name__ == '__main__':
#     send_sms('进站码：0850-0900')
