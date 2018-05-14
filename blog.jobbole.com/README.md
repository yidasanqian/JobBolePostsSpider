# JobBolePostsSpider

#### 项目介绍
一个利用HAipproxy代理池实现的完整的爬取伯乐在线所有文章的爬虫

#### 软件架构
软件架构说明


#### 安装教程

1. xxxx
2. xxxx
3. xxxx

#### 使用说明

https://www.jianshu.com/p/f0077adb74bb

https://blog.csdn.net/a_bang/article/details/72630578

1、 启动服务

```
scrapyd -l /var/log/scrapyd.log&
```
2、 发布

```
scrapyd-deploy
```

windows下的scrapyd-deploy无法运行的解决办法：

https://blog.csdn.net/weixin_41004350/article/details/78491036

3、 调度

本地：
```
curl http://127.0.0.1:80/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```
远程（利用Nginx做HTTP验证）
```
curl -u yidasanqian:yidasanqian. http://40.125.175.187:80/schedule.json -d project=jobbole -d spider=JobBolePostsSpider
```

#### 参与贡献

1. Fork 本项目
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request