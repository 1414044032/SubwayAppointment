from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers import SchedulerNotRunningError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from subwayappointment.common.core import people_insert_record
import datetime
import redis
import json

client = redis.Redis(host='localhost', port=6379, decode_responses=True)


def loop_task():
    client.delete('sh_user_station_code')
    enter_data = get_record_data()
    response = client.hgetall('sh_user_access_token')
    response1 = client.hgetall('sh_user_setting')
    for (key, item) in response.items():
        if item:
            for (key1, item1) in response1.items():
                if key == key1:
                    print('存在')
                    print(key)
                    print(enter_data)
                    print(item1)
                    record_status = people_insert_record(item, enter_data, time_solt=item1)
                    # 保存调度结果
                    if record_status != -1:
                        client.hset('sh_user_station_code', str(key),
                                    '@'.join([str(key), str(item), enter_data, str(item1), str(record_status)]))
                        print(record_status)
                    else:
                        client.hset('sh_user_station_error', key, record_status)


def get_record_data():
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    return ''.join(tomorrow.split(' ')[0].split('-'))


def hello_word():
    print(datetime.datetime.now())

# if __name__ == '__main__':
#     # print(loop_task())
#     scheduler = BlockingScheduler()
#     # scheduler.add_job(loop_task, 'date', run_date='2020-05-14 12:00:00')
#     #
#     scheduler.add_job(hello_word, 'cron',  hour=12, second=5, day_of_week='fri')
#     print('开始')
#     scheduler.start()
    # result = client.hget('sh_user_setting','18404976322')
    # result = client.hset('sh_user_setting', '18404975197', '0810-0820')
    # pass
    # result = client.set('sh_user_asdas')
    # pass
