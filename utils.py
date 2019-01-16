import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from constant import DB_CONNECT_STRING

def CreateTable():
    engine = create_engine(DB_CONNECT_STRING, echo=True)
    metadata = MetaData(engine)

    # user_table = Table('user', metadata,
    #                        Column('id', Integer, primary_key=Table),
    #                        Column('name', String(50)),
    #                        Column('fullname', String(100))
    #                     )
    #

    team_table = Table('team', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('avatar', String(100)),
                       Column('name', String(40)),
                       Column('team_id', String(10)),
                       Column('object_id', String(10))
                       )

    article_comment_user_table = Table('article_comment_user', metadata,
                                       Column('id', Integer, primary_key=True),
                                       Column('article_id', String(20)),
                                       Column('user_id_set', String(10000))
                                       )
    metadata.create_all()

if __name__ == '__main__':
    CreateTable()