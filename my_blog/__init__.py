"""
在该类中配置 MySQL 的数据库:
    因为这是初始化类,项目一加载就会执行该类,此时我们将连接数据库;
"""
import pymysql

"""
    如果不加 version_info 会报错如下:
        django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3
"""
pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()
