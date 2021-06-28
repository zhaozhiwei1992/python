import os

from flask import Flask


def create_app(test_config=None):
    """
     __name__是当前 Python 模块的名称,应用知道在哪里设置路径。
     instance_relative_config=True相当与告诉应用配置文件相当与实例文件夹(instance folder)的相对地址,实例文件夹放置本地的配置文件
     instance_path实例化目录所在地址
    """
    app = Flask(__name__, instance_relative_config=True, instance_path=os.getcwd())

    # 测试开发配置分离
    if test_config is None:
        # 实例化这个类，读取这个类中的配置
        app.config.from_object('server.configure.DevelopmentConfig')
    else:
        app.config.from_object('server.configure.TestingConfig')

    # 注册数据库初始化
    from server.database import init_app
    init_app(app)

    # a simple page that says hello
    @app.route('/health')
    def health():
        return 'It is ok!'

    from server.database import get_db

    @app.route('/add')
    def addUser():
        conn = get_db()
        c = conn.cursor()
        print("Opened database successfully")

        # 业务逻辑
        c.execute("INSERT INTO user (ID,USERNAME,password) \
              VALUES (1, 'Paul', '12321' )")

        conn.commit()
        print("Records created successfully")
        conn.close()
        return 'add success'

    @app.route('/get')
    def getUser():
        conn = get_db()
        c = conn.cursor()
        print("Opened database successfully")

        # 业务逻辑
        cursor = c.execute("SELECT id, username, password  from user")
        for row in cursor:
            print(row[1])
            print(row["password"])

        print("Records created successfully")
        conn.close()
        return 'get success'

    return app
