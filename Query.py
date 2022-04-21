import datetime
import re
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup
from requests import Response


class Query():

    def __init__(self, cookie: str):
        # 1. 是否要优先预约喜欢的座位->65+     2.是否需要不选新增开头的座位
        self.isPriority = True
        self.seatLimit = True
        # 上面需要手动设置
        time = self.getTime()
        self.checkInUrl = "https://seat.lib.whu.edu.cn/selfRes"
        self.rootUrl = "https://seat.lib.whu.edu.cn/"
        self.queryUrl = "https://seat.lib.whu.edu.cn/freeBook/ajaxSearch"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chr"
                          "ome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30",
            "Cookie": cookie
        }
        token = self.getToken(requests.get(self.rootUrl, headers=self.headers))
        self.queryParam = {
            "onDate": time[0],
            "building": 1,
            "room": "",
            "hour": "null",
            "startMin": time[1],
            "endMin": time[2],
            "power": "null",
            "window": "null"
        }
        self.checkInParam = {
            "SYNCHRONIZER_TOKEN": token,
            "SYNCHRONIZER_URI": "/",
            "date": time[0],
            "seat": "",
            "start": time[1],
            "end": time[2],
            "authid": -1,
        }
        self.isFind = False
        self.isBooked = False
        self.roomName = {"2w": '二楼西', '2e': '二楼东', '3w': '三楼西', '3e': '三楼东', '4w': '四楼西', '4e': '四楼东'}
        self.queryParamSide = {
            "onDate": time[0],
            "building": 1,
            "room": "",
            "hour": "null",
            "power": "null",
            "startMin": time[1],
            "endMin": time[2],
            "offset": 1
        }

    def getToken(self, resp: Response):
        bs = BeautifulSoup(resp.text, "html.parser")
        token = bs.find("input", attrs={"id": "SYNCHRONIZER_TOKEN"}).attrs['value']
        return token;

    def queryForSeatsResp(self, room):
        self.queryParam["room"] = room
        resp = requests.get(self.queryUrl, headers=self.headers, params=self.queryParam)
        return resp

    def getSeats(self, room):
        """拿取房间的所有座位,key为座位号，value为作为id"""
        try:
            if self.isPriority:
                seats = self.getPrioritySeats(room)
            else:
                seats = self.getCommonSeats(room)
            self.resetOffset()
            return seats
        except KeyError:
            self.keyErrorHandle()
            return self.getSeats(room)

    def parsePrioritySeats(self, html):
        seats = {}
        bs = BeautifulSoup(html, 'html.parser')
        lis = bs.findAll('li')
        for li in lis:
            seatIdStr: str = li.attrs['id']
            seatId = ''.join([x for x in seatIdStr if x.isdigit()])
            seatText = li.find('dt').get_text()
            if self.seatLimit and len(re.findall("新增", seatText)) > 0:
                continue
            seatNum = ''.join([x for x in seatText if x.isdigit()])
            if int(seatNum) >= 65:
                seats[seatText] = seatId
        return seats

    def parseCommonSeats(self, html):
        seats = {}
        bs = BeautifulSoup(html, 'html.parser')
        lis = bs.findAll("li")
        for li in lis:
            seatIdStr = li.attrs["id"]
            seatId = ''.join([x for x in seatIdStr if x.isdigit()])
            seatNum: str = li.find('dt').get_text()
            if self.seatLimit and len(re.findall("新增", seatNum)) > 0:
                continue
            seats[seatNum] = seatId
        return seats

    def getCommonSeats(self, room):
        """seats  key为座位号，value为作为id"""
        resp = self.queryForSeatsResp(room)
        html = resp.json()['seatStr']
        seatsCur = self.parseCommonSeats(html)
        seatsNext = self.pageSlide(room, 1)
        seats = self.mergeDic(seatsCur, seatsNext)
        return seats

    def pageSlide(self, room, offset):
        seats = {}
        resp = self.queryForSlideResp(room, offset)
        html = resp.json()['seatStr']
        bs = BeautifulSoup(html, "html.parser")
        if bs.find('li') is None:
            return seats
        else:
            if self.isPriority:
                seatsCur = self.parsePrioritySeats(html)
                seatNext = self.pageSlide(room, offset + 1)
                return self.mergeDic(seatsCur, seatNext)
            else:
                seatsCur = self.parseCommonSeats(html)
                seatNext = self.pageSlide(room, offset + 1)
                return self.mergeDic(seatsCur, seatNext)

    def queryForSlideResp(self, room, offset):
        self.queryParamSide["room"] = room
        self.queryParamSide["offset"] = offset
        resp = requests.get(self.queryUrl, headers=self.headers, params=self.queryParamSide)
        return resp

    def getPrioritySeats(self, room):
        resp = self.queryForSeatsResp(room)
        seats = {}
        html = resp.json()['seatStr']
        seatsCur = self.parsePrioritySeats(html)
        seatsNext = self.pageSlide(room, 1)
        seats = self.mergeDic(seatsCur, seatsNext)
        return seats

    def getMin(self, time: str):
        list = time.split(":")
        hour = list[0]
        min = list[1]
        return int(hour) * 60 + int(min)

    def getDate(self):
        now = datetime.datetime.now().timetuple()
        if now.tm_hour > 22 or (now.tm_hour == 22 and now.tm_min > 30):
            day = datetime.date.today() + datetime.timedelta(days=1)
            return str(day)
        return str(datetime.date.today())

    def getTime(self):
        print("输入时间 格式例如 12:30")
        start = input("输入开始时间:")
        startMin = self.getMin(start)
        end = input("输入结束时间:")
        endMin = self.getMin(end)
        date = self.getDate()
        if startMin >= endMin:
            print("---时间错误---")
            sys.exit(1)
        Time = (date, str(startMin), str(endMin))
        return Time

    def isCheckIn(self, resp: Response):
        compileHad = re.compile("有效预约")
        compileInvalid = re.compile("Invalid CSRF token")
        compileTimeOut = re.compile("系统可预约时间为")
        if len(compileHad.findall(resp.text)) > 0:
            print("---您已预约过，请先取消---")
            self.isFind = True
            self.isBooked = True
            sys.exit(1)
        elif len(compileInvalid.findall(resp.text)) > 0:
            print("---Invalid CSRF token---")
            self.resetToken()
            return False
        elif len(compileTimeOut.findall(resp.text)) > 0:
            print("---当前时间冲突QWQ---")
            sys.exit(1)
        else:
            self.isFind = True
            return True

    def checkIn(self, room, seatId) -> bool:
        self.resetToken()
        self.checkInParam["seat"] = seatId
        self.checkInParam['room'] = room
        resp = requests.post(self.checkInUrl, data=self.checkInParam, headers=self.headers)
        if len(resp.text) == 0:
            self.keyErrorHandle()
        if self.isCheckIn(resp):
            self.isFind = True
            return True
        else:
            return False

    def resetToken(self):
        token = self.getToken(requests.get(self.rootUrl, headers=self.headers))
        self.checkInParam["SYNCHRONIZER_TOKEN"] = token

    def keyErrorHandle(self):
        print("---被发现了额，睡一会~~~one minute---")
        sleep(60)

    def resetOffset(self):
        self.queryParamSide["offset"] = 1

    def mergeDic(self, seatsCur: dict, seatsNext: dict):
        for key, value in seatsNext.items():
            seatsCur[key] = value
        return seatsCur
