from flask import Blueprint, request, jsonify
import logging
from subwayappointment.common.core import send_code, sh_login, sh_login_response_format, people_insert_record, \
    get_station_code
from subwayappointment import redis_client
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from subwayappointment.common.util import send_sms, send_inform_sms

api = Blueprint(name="api", import_name=__name__)

# redis存储库声明
# 用户
sh_user = 'sh_user'
# 用户 accesstoken
sh_user_access_token = 'sh_user_access_token'
# 用户 setting  用户以及区间
sh_user_setting = 'sh_user_setting'
# 验证码 存储库
sh_user_check_code = 'sh_user_check_code'
# 保存进站码
sh_user_station_code = 'sh_user_station_code'
# 失败状态
sh_user_station_error = 'sh_user_station_error'
# 设置最大用户数
sh_user_count = 'sh_user_count'

scheduler_logging = logging.getLogger(__name__)
scheduler_logging.setLevel(logging.DEBUG)

log_fmt = "%(asctime)s - %(levelname)s: %(message)s"
formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")

scheduler_logging_filename = "logging.log"
file_handler = logging.FileHandler(scheduler_logging_filename)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

scheduler_logging.addHandler(stream_handler)
scheduler_logging.addHandler(file_handler)


def loop_task():
    # 清空已获取的进站码hash
    redis_client.delete(sh_user_station_code)
    # 进站日期
    enter_data = get_record_data()
    # 凭证
    response = redis_client.hgetall(sh_user_access_token)
    # 设置
    response1 = redis_client.hgetall(sh_user_setting)
    for (key, item) in response.items():
        if item:
            for (key1, item1) in response1.items():
                if key == key1:
                    try:
                        # 获取进站码
                        scheduler_logging.info("开始获取进站码：[{}] [{}]==>{}".format(
                            str(key), item, item1))
                        station, time_solt = item1.split('@@@')
                        record_status = people_insert_record(item, enter_data, station=station, time_solt=time_solt)
                        # 保存调度结果
                        if record_status != -1:
                            # 不等于-1就是成功（成功分两种一种是只有码，另一种是返回accesstoken）
                            redis_client.hset(sh_user_station_code, str(key),
                                              '@'.join(
                                                  [str(key), str(item), enter_data, str(item1), str(record_status)]))
                            scheduler_logging.info("获取进站码：[{}][{}] {}-{} => {}".format(
                                str(key), str(item), enter_data, str(item1), str(record_status)))
                            # 发送短信
                            sms_status = send_sms('进站码：' + str(item1), str(key))
                            scheduler_logging.info("发送短信：[{}][{}]=> {}".format(
                                str(key), str(item1), sms_status))
                            # 更新access
                            if type(record_status) == tuple:
                                new_accesstoken = record_status[1]
                                new_refreshtoken = record_status[2]
                                # 保存最新的access_token
                                # redis_client.
                                redis_client.hset(sh_user_access_token, key, new_accesstoken + '@@@' + new_refreshtoken)
                        else:
                            scheduler_logging.error("未取到进站码：[{}][{}] {}-{} => {}".format(
                                str(key), str(item), enter_data, str(item1), str(record_status)))
                            redis_client.hset(sh_user_station_error, key, record_status)
                        break
                    except Exception as e:
                        scheduler_logging.error("### Error: {}".format(e))


def loop_task1():
    response = redis_client.hgetall(sh_user_setting)
    for (key, item) in response.items():
        sms_status = send_inform_sms(key)
        scheduler_logging.info("发送短信：[{}][{}]=> {}".format(
            str(key), str(item), sms_status))


def get_record_data():
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    return ''.join(tomorrow.split(' ')[0].split('-'))


scheduler = BackgroundScheduler()
# scheduler.add_job(loop_task, 'date', run_date='2020-05-17 12:00:05')
scheduler.add_job(loop_task, 'cron', hour=12, minute=0, second=10, day_of_week='mon,tue,wed,thu,sun')
scheduler.add_job(loop_task, 'cron', hour=12, minute=0, second=10, day_of_week='sat')
print('开始')
scheduler.start()


@api.route('/login', methods=["POST"])
def login():
    phone = request.json.get("phone", "")
    check_code = request.json.get("checkCode", "")
    phone = phone.strip()
    check_code = check_code.strip()
    response_body = {
        "status": 0,
        "info": None
    }
    if not all([phone, check_code]):
        response_body["status"] = 1
        response_body["info"] = '参数非法'
    else:
        #  获取响应结果进行处理
        try:
            # 请求登录
            status_code, response = sh_login(phone, check_code)
            if status_code == 200:
                # 登录响应解析
                status, accesstoken, refreshtoken, headimgUrl = sh_login_response_format(response)
                scheduler_logging.info("执行登录：[{}][{}] {}-{} => {}".format(
                    phone, check_code, status, accesstoken, refreshtoken))
                # 判断是否有头像，作为是否绑定微信的依据
                # if len(headimgUrl) < 6:
                #     response_body["status"] = status
                #     response_body["info"] = 'login'
                # else:
                response_body["status"] = status
                response_body["info"] = {
                    "accesstoken": accesstoken,
                    "refreshtoken": refreshtoken
                }
                redis_client.sadd(sh_user, phone)
                redis_client.hset(sh_user_access_token, phone, accesstoken + '@@@' + refreshtoken)
            elif status_code == 500:
                response_body["status"] = 1
                response_body["info"] = "验证码已过期"
            else:
                response_body["status"] = 1
                response_body["info"] = "未知状态码"
        except Exception as e:
            scheduler_logging.error("### Error: {}".format(e))
            response_body["status"] = 1
            response_body["info"] = "服务器错误"
    return response_body


@api.route('/SendVerifyCode', methods=["GET"])
def send_verify_code():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": '发送成功'
    }
    try:
        # 判断验证码有效期
        if len(phone) == 11 and (redis_client.get('code_' + phone) is None):
            if send_code(phone):
                redis_client.set('code_' + phone, 'code', ex=60)
                scheduler_logging.info("发送验证码：{}".format(phone))
        else:
            response_body['status'] = 1
            response_body['info'] = '手机号不对，或者验证码请求时间太短'
    except Exception as e:
        scheduler_logging.error("### Error: {}".format(e))
        response_body['status'] = 1
        response_body['info'] = '服务器异常'
    return jsonify(response_body)


@api.route('/setSetting', methods=['POST'])
def set_setting():
    phone = request.json.get("phone", "")
    station = request.json.get("station", "")
    time_solt = request.json.get("timeSolt", "")
    phone = phone.strip()
    time_solt = time_solt.strip()
    response_body = {
        "status": 0,
        "info": '成功'
    }
    try:
        redis_client.hset(sh_user_setting, phone, station + '@@@' + time_solt)
    except Exception as e:
        scheduler_logging.error("### Error: {}".format(e))
        response_body['status'] = 1
        response_body['info'] = '服务器错误'
    return jsonify(response_body)


@api.route('/getSetting', methods=['GET'])
def get_setting():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": '未找到你的调度设置'
    }
    result = redis_client.hget(sh_user_setting, phone)
    if result:
        response_body['info'] = result
    else:
        response_body['status'] = 1
    return jsonify(response_body)


@api.route('/getCode', methods=['GET'])
def get_code():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": None
    }
    result = redis_client.hget(sh_user_access_token, phone)
    if result:
        # 获取access—token
        access_token = result.split('@@@')[0]
        result = get_station_code(access_token)
        response_body['info'] = result
    else:
        response_body['status'] = 1
    return jsonify(response_body)


@api.route('/delSetting', methods=['GET'])
def del_setting():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": '删除成功'
    }
    result = redis_client.hdel(sh_user_setting, phone)
    if result:
        response_body['info'] = result
    else:
        response_body['status'] = 1
        response_body['info'] = '服务器错误'
    return jsonify(response_body)


@api.route('/checkLogin', methods=['GET'])
def check_login():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": '存在'
    }
    if redis_client.sismember(sh_user, phone):
        pass
    else:
        response_body['status'] = 1
        response_body['info'] = '用户后台不存在，请登录'

    return jsonify(response_body)


@api.route('/checkPassCode', methods=['GET'])
def check_passcode():
    phone = request.args.get("phone", "")
    phone = phone.strip()
    response_body = {
        "status": 0,
        "info": ''
    }
    result = redis_client.hget(sh_user_station_code, phone)
    if result:
        response_body['info'] = result
    else:
        response_body['status'] = 1
        response_body['info'] = '未找到有效的进站码'
    return jsonify(response_body)


@api.route('/checkUserCount', methods=['GET'])
def check_usercount():
    result = redis_client.scard(sh_user)
    result_count = redis_client.get(sh_user_count)
    response_body = {
        "status": 0,
        "info": {
            "new": result,
            "count": None
        }
    }
    if result_count:
        response_body["info"]["count"] = int(result_count)
    else:
        redis_client.set(sh_user_count, 50)
        response_body["info"]["count"] = 50
    return jsonify(response_body)
