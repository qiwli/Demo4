from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # 这是额外加的
# pip install flask-migrate
from flask_migrate import Migrate

app = Flask(__name__)

# MySQL所在主机名
HOSTNAME = '127.0.0.1'
# MySQL监听的端口号，默认3306
PORT = 3306
# 连接MySQL的用户名
USERNAME = 'root'
# 连接MySQL的密码
PASSWORD = '123456'
# MySQL上创建的数据库名称
DATABASE = 'database_learn'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@' \
                                        f'{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'


# 在app.config中设置好连接数据库的信息
# 然后使用SQLAlchemy(app)创建一个db对象
# SQLAlchemy会自动读取app.config中连接数据库的信息
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# ORM模型映射成表的三步（在Terminal中执行）
# 1. flask db init   只需要执行一次
# 2. flask db migrate  识别ORM模型的改变，生成迁移脚本
# 3. flask db upgrade  运行迁移脚本，同步到数据库中


# # 用来测试数据库是否连接成功
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))  # text是额外加的，不加会报错
#         # 因为select 1不是可执行对象，需要用text()函数转换成一个sql表达式，以成为sqlalchemy中可执行对象
#         print(rs.fetchone())  # 输出(1,)表示数据库连接成功


# ORM模型创建
class User(db.Model):
    __tablename__ = 'user'  # 制定表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)   # primary_key来指定主键,autoincrement表示自动增长
    # varchar,String(100)表示最大长度100,nullable=False表示不能为空
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # articles = db.relationship('Article', back_populates='author')
    email = db.Column(db.String(100))
    signature = db.Column(db.String(100))


class Article(db.Model):
    __tablename__ = 'article'  # 制定表名
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # 添加作者的外键,此处引用的是user表的id字段
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 类型是由引用的表中决定的
    # author = db.relationship('User', back_populates='articles')
    # backref会自动给User模型添加一个articles的属性，用来获取文章列表
    author = db.relationship('User', backref='articles')


# article = Article(title='Flask学习大纲', content='Flaskxxxxx')
# article.author_id = user.id
# user = User.query.get(article.author_id)
# article.author = User.query.get(article.author_id)
# print(article.author)


# # 将模型映射到数据库,此映射方式存在弊端，字段更新时，数据库不会同步,因此一般使用migrate进行映射
# with app.app_context():   # 此行代码为出现上下文问题的解决方法（请求上下文，应用上下文）
#     db.create_all()  # 将所有模型同步到数据库


# # 将一行记录添加到数据库
# user = User(username='张三', password='111111')
# # sql: insert user(username,password) values('张三','111111')


@app.route('/')
def hellow_world():
    return 'Hello World!'


# 使用User模型进行数据的增删改查操作
@app.route('/user/add')  # 添加
def add_user():
    # 1. 创建ORM对象
    user = User(username='张三', password='111111')
    # 2. 将ORM对象添加到db.session中
    db.session.add(user)
    # 3. 将db.session中的改变同步到数据库中
    db.session.commit()
    # 视图函数，必须要有一个返回
    return '用户创建成功！'


@app.route('/user/query')  # 查询
def query_user():
    # # 1. get查找:根据主键查找,返回类型为User
    # user = User.query.get(1)  # query对象由db.Model对象提供
    # print(type(user))
    # print(f'{user.id}:{user.username}-{user.password}')
    # 2. filter_by查找,返回类型为Query
    # Query : 类数组
    users = User.query.filter_by(username='张三')
    print(type(users))
    for user in users:
        print(user.username)
    return '数据查找成功！'


@app.route('/user/update')  # 修改
def update_user():
    user = User.query.filter_by(username='张三').first()  # first和get效果差不多
    user.password = '222222'  # 修改user对象的password为222222
    db.session.commit()  # 同步到数据库中
    return '数据修改成功！'


@app.route('/user/delete')  # 删除
def delete_user():
    user = User.query.get(1)  # 查找
    db.session.delete(user)   # 从db.session中删除
    db.session.commit()       # 同步到数据库
    return '数据删除成功！'


@app.route('/article/add')
def article_add():
    article1 = Article(title='Flask学习大纲', content='Flaskxxxx')
    article1.author = User.query.get(1)
    article2 = Article(title='Django学习大纲', content='Djangoxxxx')
    article2.author = User.query.get(1)

    # 添加到session中
    db.session.add_all([article1, article2])
    # 同步到数据库中
    db.session.commit()
    return '文章添加成功！'


@app.route('/article/query')
def query_article():
    user = User.query.get(1)  # 用户id为1的用户发表的所有文章
    for article in user.articles:
        print(article.title)
        # print(type(user.articles))
        return '文章查找成功！'


if __name__ == '__main__':
    app.run(debug=True)
