import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from constant import DB_CONNECT_STRING



class MysqlDo(object):

    def connectionMysql(self):
        self.engine = create_engine(DB_CONNECT_STRING, echo=True)
        self.metadata = MetaData(self.engine)

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
        self.metadata.create_all()
        return team_table, article_comment_user_table

    def saveData(self, tableName, data):
        ins = tableName.insert()
        # ins.values(data)
        conn = self.engine.connect()
        result = conn.execute(ins, data)




