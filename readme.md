### 依赖库
Flask（接口服务） ，FlaskRedis（连接Redis），requests（网络请求），apscheduler（定时任务）
### 依赖软件
Redis
### 运行
python app.py
### 注意事项
提供了对地铁预约服务接口的封装，以及定时预约的实现。
（登录后用户信息保存到redis才能实现定时预约）