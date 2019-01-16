import requests
import json
import time



def get_team_info():
    """
    获取各个球队的信息, 在关注里面, 选择球队
    :return:
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 SE Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 News/182 Android/8.1.0 NewsApp/182 SDK/27 VERSION/6.2.6dongqiudiClientApp",
        "Authorization": "eBV1eHLBiZIvujfciRqFCiKX4S5GQVkdFDRWHZoDfYEFpERwnk6Fw7Wmn1ufRZXa"

    }
    BASE_URL = 'https://api.dongqiudi.com/catalog/channels/2'
    r = requests.get(url=BASE_URL, headers=headers)
    tab_content = json.loads(r.text)
    print(tab_content)



if __name__ == '__main__':

    get_team_info()
