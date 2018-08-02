# coding: utf-8
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, String, Integer, Text

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Table


engine = create_engine('mysql+mysqldb://root@localhost:3306/blog')
#print(engine)
Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False, index=True)
	password = Column(String(64), nullable=False)
	email = Column(String(64), nullable=False, index=True)
	#artiche 1vs>1 user
	#artiches = relationship('Article', backref='author')
	artiches = relationship('Article')
	#userlist 1vs1
	userinfo = relationship('UserInfo', backref='user', uselist=False)
	
	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.username)

class Article(Base):
	__tablename__ = 'articles'
	id = Column(Integer, primary_key=True)
	title = Column(String(255), nullable=False, index=True)
	content = Column(Text)
	user_id = Column(Integer, ForeignKey('users.id'))
	category_id = Column(Integer, ForeignKey('categories.id'))
	author = relationship('User')
	tags = relationship('Tag', secondary='article_tag', backref='articles')

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.title)

class UserInfo(Base):
	__tablename__ = 'userinfos'
	id = Column(Integer, primary_key=True)
	name = Column(String(64))
	qq = Column(String(11))
	phone = Column(String(11))
	link = Column(String(64))
	user_id = Column(Integer, ForeignKey('users.id'))

class Tag(Base):
	__tablename__ = 'tags'
	
	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False, index=True)
	
	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.name)

class Category(Base):
	__tablename__ = 'categories'

	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False, index=True)
	artiches = relationship('Article', backref='category')
	
	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.name)

article_tag = Table(
	'article_tag', Base.metadata,
	Column('article_id', Integer, ForeignKey('articles.id')),
	Column('tag_id', Integer, ForeignKey('tags.id'))
)

from faker import Factory
from sqlalchemy.orm import sessionmaker
import random

faker = Factory.create()
Session = sessionmaker(bind=engine)
session = Session()

faker_users = [User(
	username = faker.name(),
	password = faker.word(),
	email = faker.email(),
	) for i in range(10)]
session.add_all(faker_users)

faker_categories=[Category(
	name = faker.word()
	) for i in range(5)]
session.add_all(faker_categories)

faker_tags = [Tag(
	name = faker.word()
	) for i in range(20)]
session.add_all(faker_tags)

for i in range(100):
	article = Article(
	title = faker.sentence(),
	content = ' '.join(faker.sentences(nb = random.randint(10, 20))),
	author = random.choice(faker_users),
	category = random.choice(faker_categories)
	)

	#bug
	for tag in random.sample(faker_tags, random.randint(2, 5)):
		article.tags.append(tag)
	session.add(article)

session.commit()

if __name__ == '__main__':
	Base.metadata.create_all(engine)
