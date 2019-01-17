import requests
import json
import time

from utils import MysqlDo

BASE_URL = 'https://api.dongqiudi.com'

class DongQiuDiApp(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 SE Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 News/182 Android/8.1.0 NewsApp/182 SDK/27 VERSION/6.2.6dongqiudiClientApp",
            "Authorization": "eBV1eHLBiZIvujfciRqFCiKX4S5GQVkdFDRWHZoDfYEFpERwnk6Fw7Wmn1ufRZXa"
        }



    def dBDeal(self):
        self.mysqlDo = MysqlDo()
        self.mysqlDo.connectionMysql()
        self.teamTable, self.article_comment_user_table = self.mysqlDo.createTable()

    def writeTeamInfo(self):
        """
        获取各个球队的信息, 在关注里面, 选择球队
        :return:
        """

        urlCategories = BASE_URL + '/catalogs'
        r = requests.get(url=urlCategories, headers=self.headers)
        tabContent = json.loads(r.text)
        # [{'id': 1, 'title': '热门', 'total': 27}, {'id': 17, 'title': '世界杯', 'total': 35}, {'id': 12, 'title': '中超', 'total': 16}, {'id': 2, 'title': '英超', 'total': 20}, {'id': 3, 'title': '意甲', 'total': 20}, {'id': 4, 'title': '西甲', 'total': 20}, {'id': 5, 'title': '德甲', 'total': 18}, {'id': 6, 'title': '法甲', 'total': 20}, {'id': 7, 'title': '国内', 'total': 20}, {'id': 8, 'title': '国家队', 'total': 10}, {'id': 9, 'title': '球员', 'total': 84}, {'id': 10, 'title': '教练', 'total': 24}]
        team_data = list()
        for item in tabContent:
            if item['id'] in (1, 17, 9, 10):
                continue
            urlCategory = BASE_URL + '/catalog/channels/'+ str(item['id'])
            r = requests.get(url=urlCategory, headers=self.headers)
            content = json.loads(r.text)
        #     {'title': '中超', 'total': 16, 'data': [{'id': '475', 'name': '广州恒大淘宝', 'followed': False, 'type': 'team', 'avatar': 'https://img.dongqiudi.com/data/pic/6648.png', 'color': '#ffeeaa3f', 'object_id': '6648'}, {'id': '1520', 'name': '山东鲁能泰山', 'followed': False, 'type': 'team', 'avatar': 'https://img.dongqiudi.com/data/pic/434.png', 'color': '#ffFF8000', 'object_id': '434'}]}
            team_data.append(content)

        for league_data in team_data:
            d = dict()
            # d = {'id':'xxx', 'league':'xxx', 'avatar':'xxx', 'name': 'xxx', 'team_id':'xxx', 'object_id':'xxx'}
            # team_table = Table('team', self.metadata,
            #                    Column('id', Integer, primary_key=True),
            #                    Column('avatar', String(100)),
            #                    Column('name', String(40)),
            #                    Column('team_id', String(10)),
            #                    Column('object_id', String(10))
            #                    )

            d['league'] = league_data['title']
            for team in league_data['data']:
                d['avatar'] = team['avatar']
                d['name'] = team['name']
                d['team_id'] = team['id']
                d['object_id'] = team['object_id']
                self.mysqlDo.saveData(self.teamTable, d)
                print(d)

    def getArticleId(self, pageNum):
        """
        获取前pageNum页的article id
        :param pageNum:
        :return:
        """
        urlArticleFirstPage = BASE_URL + '/app/tabs/android/1.json' # 不爬取首页, 因为其中有置顶的文章
        r = requests.get(url=urlArticleFirstPage, headers=self.headers)
        data = json.loads(r.text)
        urlArticleNextPage = data['next']
        l = list()
        # d = {""}
        for i in range(pageNum):
            r = requests.get(url=urlArticleNextPage,headers=self.headers)
            data = json.loads(r.text)
            for article in data['articles']:
               l.append(article['id'])
            urlArticleNextPage = data['next']
            print("第{}页获取完成".format(i+1))
        return l

    def getCommentUser(self, article_id):
        """
        获取某article下评论区的用户id(去重)
        :param article_id:
        :return: 用户id set
        """
        try:
            r = requests.get(url="https://api.dongqiudi.com/v2/article/{}/comment".format(article_id), headers=self.headers)
            data = json.loads(r.text)
        except:
            data = {'data':{}}
        if 'data' not in data.keys():
            return set([])
        userList = list()
        for user in data['data'].get('user_list', []):
            userList.append(user.get('id', ''))
        nextUrl = data['data'].get('next', '')
        count = 0
        while nextUrl:
            print("正在获取{}的第{}页的用户".format(article_id,count))
            try:
                r = requests.get(url=nextUrl,headers=self.headers)
                data = json.loads(r.text)
            except:
                data = {'data':{}}
            if 'data' not in data.keys():
                break
            for user in data['data'].get('user_list', []):
                userList.append(user.get('id', ''))
            count += 1
            nextUrl = data['data'].get('next', '')
        userSet = set(userList)
        userSet.discard('0')
        userSet.discard('99999999')
        return userSet


    def writeUserInfo(self):
        articleIdList = dongqiudi.getArticleId(1)
        # articleIdList = [article for dateArticleList in articleIdList for article in dateArticleList]

        with open('article_id.txt', "wb") as f:
            f.write(str(articleIdList).encode(encoding='utf-8'))

        userIdList = []
        crawledArticleIdList = []
        for articleId in articleIdList:
            print("正在获取文章{}评论用户".format(articleId))
            userSet = self.getCommentUser(articleId)
            userIdList.append([articleId, str(userSet)])
            crawledArticleIdList.append(articleId)

        with open('result.txt',"wb") as f:
            f.write(str(userIdList).encode('utf-8'))

if __name__ == '__main__':

    dongqiudi = DongQiuDiApp()
    # dongqiudi.dBDeal()
    # dongqiudi.getTeamInfo()
    # art =
    # dongqiudi.getArticleCommentUser()
    # s = dongqiudi.getCommentUser(896482)
    # print(s)
    dongqiudi.writeUserInfo()