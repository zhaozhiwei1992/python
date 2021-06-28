import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    获取与数据库的连接
    g是一个特殊的对象，独立与每一个请求。它会在处理请求中把多个连接、多个函数所用到的数据存储其中，
    反复使用，不需要每次调用该函数都要重新创建新的链接
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            # 数据库连接地址，从配置信息中读取
            current_app.config['DATABASE'],
            # 类型检测
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 告诉连接返回类似于字典的行，这样可以通过列名称来操作数据。
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
     通过检查g.db来确定连接是否已经建立。如果连接已建立，那么就关闭连接。
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """数据库初始化，创建表"""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    """初始化数据"""
    # with current_app.open_resource('data.sql') as f:
    #     db.executescript(f.read().decode('utf8'))


"""
export FLASK_APP=run
flask init-db 或者python -m flash init-db
输出, 数据库初始化已完成, 并生辰db.sqlite3
"""


@click.command('init-db')  # 添加新的命令
@with_appcontext
def init_db_command():
    """清除已经存在的表创建新的表"""
    init_db()
    click.echo('数据库初始化已完成')


def init_app(app):
    app.teardown_appcontext(close_db)  # 告诉flask在返回响应后进行清理的时候调用此函数。
    app.cli.add_command(init_db_command)  # 添加数据库表初始化命令
