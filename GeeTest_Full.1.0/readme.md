##python三方库安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
## 该接口依赖redis,node环境
## step1
配置好所有设置参数
## step2 
运行 rush/rush.py 导入缓存，默认db=4

- test.py 这个文件有这个接口请求例子，之前公示系统爬虫上得请求方式也可以用，支持get/post两种请求

- Api.py 接口文件，使用时，启动这个接口就行

- main.py 这个是主程序文件，所有得调度逻辑都是这个











