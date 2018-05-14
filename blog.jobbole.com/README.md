# JobBolePostsSpider

#### 项目介绍
一个利用HAipproxy代理池实现的完整的爬取伯乐在线所有文章的爬虫

#### 软件架构
软件架构说明


#### 安装教程

```
pip install mysql-connector-python
pip install Pillow
pip install PyMySQL
pip install redis
pip install Scrapy
pip install scrapyd
pip install scrapyd-client
pip install SQLAlchemy
pip install pymongo
```

#### 使用说明
**前置条件，第一条连接的内容必须操作完毕，第二条连接的内容作为下面步骤的参考**

- [一个用Python实现的高可用低延迟的高匿IP代理池 -- HAipproxy的使用](https://blog.csdn.net/u011726984/article/details/80279792)

- [使用Scrapyd部署爬虫](https://www.jianshu.com/p/f0077adb74bb)

1、 启动服务

在远程服务器上运行启动Scrapyd服务：

```
scrapyd -l /var/log/scrapyd.log&
```

2、 发布


安装完 `scrapyd-client`模块后在Python脚本目录`D:\Program Files\Python36\Scripts`下新建`scrapyd-deploy.bat`，内容：

```
@echo off
python "D:\Program Files\Python36\Scripts\scrapyd-deploy"
```

设置`scrapy.cfg`文件：
```
[settings]
default = jobbole.settings

[deploy]
#url = http://127.0.0.1:80/
url = http://40.125.175.187:80/
project = jobbole
username = yidasanqian
password = yidasanqian.
```

在本地环境进入到爬虫项目目录下运行部署命令：

```
scrapyd-deploy
```

[windows下的scrapyd-deploy无法运行的解决办法](https://blog.csdn.net/weixin_41004350/article/details/78491036)

3、 调度

[windows环境下 curl 安装和使用](https://blog.csdn.net/qq_21126979/article/details/78690960?locationNum=10&fps=1)

本地：
```
curl http://127.0.0.1:80/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```
远程（利用Nginx做HTTP验证）

[Nginx中使用htpasswd配置Http认证](https://blog.csdn.net/a_bang/article/details/72630578)


```
curl -u yidasanqian:yidasanqian. http://40.125.175.187:80/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```

#### 参与贡献

1. Fork 本项目
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request