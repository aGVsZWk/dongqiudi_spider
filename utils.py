import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from constant import DB_CONNECT_STRING



class MysqlDo(object):

    def connectionMysql(self):
        self.engine = create_engine(DB_CONNECT_STRING, echo=True)
        self.metadata = MetaData(self.engine)
        self.conn = self.engine.connect()


    def createTable(self):
        team_table = Table('team', self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('league', String(20)),
                           Column('avatar', String(100)),
                           Column('name', String(40)),
                           Column('team_id', String(10)),
                           Column('object_id', String(10))
                           )

        article_comment_user_table = Table('article_comment_user', self.metadata,
                                           Column('id', Integer, primary_key=True),
                                           Column('article_id', String(20)),
                                           Column('user_id_set', String(100000))
                                           )


        user_table = Table('user', self.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', String(20)),
                     Column('user_name', String(40)),
                     Column('gender', String(10)),
                     Column('created_at', String(50)),
                     Column('region_id', String(20)),
                     Column('region_phrase', String(20)),
                     Column('team_id', String(20)),
                     Column('introduction', String(100)),
                     Column('timeline_total', String(20)),
                     Column('post_total', String(20)),
                     Column('reply_total', String(20)),
                     Column('up_total', String(20)),
                     Column('following_total', String(20)),
                     Column('followers_total', String(20))
                     )


        self.metadata.create_all()
        return team_table, article_comment_user_table, user_table

    def saveData(self, tableName, data):
        ins = tableName.insert()
        # ins.values(data)
        result = self.conn.execute(ins, data)


    def showData(self, sqlword):
        cur = self.conn.execute(sqlword)
        res = cur.fetchall()
        return res
