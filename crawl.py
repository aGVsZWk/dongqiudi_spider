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
        self.teamTable, self.article_comment_user_table, self.userTable = self.mysqlDo.createTable()

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
                self.mysqlDo.saveData(self.teamTable, [d])
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
            print("第{}页文章获取完成".format(i+1))
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

    def getUserInfo(self, userId):
        """
        获取某个用户的信息
        :param userId: 用户id
        :return: 用户id，用户名，性别，创建时间，地区id，地区名，球队id，介绍，timeline total，发表数，回复数，被点赞数，关注数，被关注数
        """

        r = requests.get(url='https://api.dongqiudi.com/users/profile/{}'.format(userId),headers=self.headers)
        data = json.loads(r.text)
        d = {}
        d["user_id"] = data['user'].get('user_id',userId)
        d['user_name'] = data['user']['username']
        d['gender'] = data['user'].get('gender', None)
        d['created_at'] = data['user']['created_at']
        d['region_id'] = data['user']['region']['id'] if data['user']['region'] else None
        d['region_phrase'] = data['user']['region']['phrase'] if data['user']['region'] else None
        d['team_id'] = data['user'].get('team_id', None)
        d['introduction'] = data['user']['introduction']
        d['timeline_total'] = data['user']['timeline_total']
        d['post_total'] = data['user']['post_total']
        d['reply_total'] = data['user']['reply_total']
        d['up_total'] = data['user']['up_total']
        d['following_total'] = data['user']['following_total']
        d['followers_total'] = data['user']['followers_total']
        print(d)
        return d




    def writeArticleId(self, pageNum):
        articleIdList = dongqiudi.getArticleId(pageNum)
        # articleIdList = [article for dateArticleList in articleIdList for article in dateArticleList]
        with open('article_id.txt', "wb") as f:
            f.write(str(articleIdList).encode(encoding='utf-8'))




    def writeUserInfo(self):

        with open("article_id.txt","rb") as f:
            d = f.readlines()
        articleIdList = eval(d[0])   # 使用eval, 省去解码

        crawledArticleIdList = []
        count = 0
        totalUsers = 0
        l = []
        for articleId in articleIdList:
            print("正在获取第{}篇文章{}评论用户,".format(count+1,articleId))
            userSet = self.getCommentUser(articleId)
            totalUsers += len(userSet)
            d = dict()
            d["article_id"] = articleId
            d["user_id_set"] = str(userSet)
            l.append(d)
            crawledArticleIdList.append(articleId)
            count += 1

            if count % 20 == 0:
                self.mysqlDo.saveData(self.article_comment_user_table, l)
                l = []
            if count % 50 == 0:
                with open("crawled_article.txt", "wb") as f:
                    f.write(str(crawledArticleIdList).encode(encoding='utf-8'))


            # article_comment_user_table = Table('article_comment_user', self.metadata,
            #                                    Column('id', Integer, primary_key=True),
            #                                    Column('article_id', String(20)),
            #                                    Column('user_id_set', String(10000))
            #                                    )

        # with open('result.txt',"wb") as f:
        #     f.write(str(userIdList).encode('utf-8'))
        #


    def writeUserList(self):
        """
        将待爬取的用户id列表写入 user_id_set.txt
        :return:
        """
        value = self.mysqlDo.showData('select * from article_comment_user;')
        user_id_set = set()
        for i in value:
            d = eval(i[2])
            user_id_set.update(d)
        print("共获取了{}用户".format(user_id_set))

        with open('user_id_set.txt', 'wb') as f:
            f.write(str(list(user_id_set)).encode(encoding='utf-8'))

        # 获取用户信息, 写入user表
        insertData = list()
        count = 0
        crawedUser = []
        for userID in user_id_set:
            try:
                userInfo = self.getUserInfo(userID)
            except:
                continue
            insertData.append(userInfo)
            crawedUser.append(userID)
            count += 1
            if count % 100 ==0:
                self.mysqlDo.saveData(self.userTable, insertData)
                print("正在插入用户数据")
                insertData = list()
                with open('crawed_user.txt',"wb") as f:
                    f.write(str(crawedUser).encode(encoding='utf-8'))



if __name__ == '__main__':

    dongqiudi = DongQiuDiApp()
    dongqiudi.dBDeal()
    # dongqiudi.writeTeamInfo()

    # dongqiudi.writeArticleId(100)
    # dongqiudi.writeUserInfo()
    # dongqiudi.writeUserList()
    # dongqiudi.getUserInfo('5595749')
    # dongqiudi.getUserInfo('1553838')
    dongqiudi.writeUserList()