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

**前提：python已配置在环境变量里**

安装完 `scrapyd-client`模块后在Python脚本目录`D:\Program Files\Python36\Scripts`下新建`scrapyd-deploy.bat`，内容：

```
@echo off
python "D:\Program Files\Python36\Scripts\scrapyd-deploy" %1 %2 %3 %4 %5 %6 %7 %8 %9
```

设置`scrapy.cfg`文件：
```
[settings]
default = jobbole.settings

[deploy:local-scrapyd]
project = jobbole
url = http://127.0.0.1:80/
version= 1.3.0
```

在本地环境进入到爬虫项目目录下运行部署命令：

```
scrapyd-deploy local-scrapyd -d -p jobbole
```

[windows下的scrapyd-deploy无法运行的解决办法](https://blog.csdn.net/weixin_41004350/article/details/78491036)

**发布到远程服务器，利用Nginx做HTTP验证**

[Nginx中使用htpasswd配置Http认证](https://blog.csdn.net/a_bang/article/details/72630578)

配置`/etc/nginx/nginx.conf `文件：
```
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    upstream scrapyd {
        server localhost:6800;         
    }
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    gzip  on;
    # Scrapyd local proxy for basic authentication.
    # https://blog.csdn.net/a_bang/article/details/72630578
    # Don't forget iptables rule.
    # iptables -A INPUT -p tcp --destination-port 6800 -s ! 127.0.0.1 -j DROP

    server {
        listen 80;

        location ~ /\.ht {
                deny all;
        }

        location /scrapyd/ {
                proxy_pass            http://scrapyd/;
		proxy_set_header Host $host;  
	        proxy_set_header X-Real-IP $remote_addr;  
	        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                auth_basic            "Restricted";
                auth_basic_user_file  /etc/nginx/conf.d/.htpasswd;
        }
    }

    include /etc/nginx/conf.d/*.conf;
}

```

设置`scrapy.cfg`文件：
```
[settings]
default = jobbole.settings

[deploy:remote-scrapyd]
url = http://40.125.175.187:80/scrapyd/
project = jobbole
version = 1.3.0
username = yidasanqian
password = yidasanqian.
```

在本地环境进入到爬虫项目目录下运行部署命令：

```
scrapyd-deploy remote-scrapyd -d -p jobbole
```

>Note:如果配置了Nginx反向代理需要修改scrapyd的website.py模块的源码，将html的a标签的href的反斜杠“/”删除。

3、 调度

[windows环境下 curl 安装和使用](https://blog.csdn.net/qq_21126979/article/details/78690960?locationNum=10&fps=1)

本地：
```
curl http://127.0.0.1:80/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```
远程

```
curl -u yidasanqian:yidasanqian. http://40.125.175.187:80/scrapyd/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```

#### 参与贡献

1. Fork 本项目
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request