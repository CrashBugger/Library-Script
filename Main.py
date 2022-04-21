import sys
from time import sleep

from Query import Query

if __name__ == '__main__':
    cookie = "UM_distinctid=17f77562da1d84-01d33bf3df20e7-56171d58-13c680-17f77562da2abf; Hm_lvt_25f0d400161bc8ffe2bddaa95fdfe46a=1648733761; JSESSIONID=9D3889437AA98EB08BB003D19FFC5102"
    # 输入cookie,
    # 验证码验证准确率太低，打码平台长期用的话还得付费，只能用cookie绕过登录
    # 华丽的分割线-------------------------------------------------
    query = Query(cookie)
    room = {"2w": '6', '2e': '7', '3w': '8', '3e': '10', '4w': '9', '4e': '11'}
    roomName = {"2w": '二楼西', '2e': '二楼东', '3w': '三楼西', '3e': '三楼东', '4w': '四楼西', '4e': '四楼东'}
    while not query.isFind:
        for name, roomId in room.items():
            seats = query.getSeats(roomId)
            if len(seats) > 0:
                for seatNum, seatId in seats.items():
                    check_in = query.checkIn(roomId, seatId)
                    if check_in:
                        print("---" + roomName[name] + seatNum + "预约成功---")
                        sys.exit(1)
            else:
                print("---" + roomName[name] + "未找到座位" + "---")
        # 歇一会，防止对服务器造成堵塞
        print("----下一轮搜索一分钟后开始---------------")
        sleep(60)
