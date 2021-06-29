"""
传入flask 创建user resource
"""


def constract_app(app):
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

    @app.route('/update')
    def updateUser():
        conn = get_db()
        c = conn.cursor()
        print("Opened database successfully")

        # 业务逻辑
        c.execute("UPDATE user set username = 'tom' where ID=1")
        conn.commit()
        print("Total number of rows updated :", conn.total_changes)

        print("Records created successfully")
        conn.close()
        return 'update success'

    return None
