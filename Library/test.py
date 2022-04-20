import datetime
import re
from time import sleep

import main
import Query

if __name__ == '__main__':
    text = """
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>预约结果 :: 空间预约系统</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="keywords" content="利昂系统，利昂软件，空间预约系统，占座系统，私有云网盘开发商"/>
    <meta name="description" content=""/>
    <link rel="shortcut icon" type="image/x-icon" href="/assets/favicon-f803218017f305bf74432131322b3229.ico"/>

    <script type="text/javascript" src="/assets/layouts/pcMain-5343ba5915badde752c91f0b6adb7ae6.js" ></script>
    <link rel="stylesheet" href="/assets/layouts/pcMain-8064cd43a575aa16012542b9f72c1919.css"/>

    
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <meta name="layout" content="pcMain"/>
    <script type="text/javascript" src="/assets/raphael/raphael-min-118264e919b289c21e8e32d7d3fa78d8.js" ></script>
    


    
</head>
<body onselectstart="return&nbsp;false">
<div class="header">
    <h1 class="logo fl"><img src="/setting/siteLogo" width="181" height="51" /></h1>
    <h2 class="logoName fl"><img src="/assets/style/pc/img/logoName-48972341cb6059937b0d2974fc7042f0.png" width="180" height="44"/></h2>
    <div class="userInfor fr">
        <ul>
            <li><i class="timeIcon"></i><span id="currentDate">2013-02-21</span> <span id="currentTime">16:48</span></li>
            <li><i class="renIcon"></i><strong style="vertical-align: middle;"><a href="/user/password">李帅柯</a></strong></li>
        </ul>
    </div>
</div>
<div class="handleBtns" style="display: none">
	<div class="topHandle">
        <ul>
            <li>
                <a id="btnStop" href="#" action="stopUsing">结束使用</a>
            </li>
            <li>
                <a id="btnExtend" href="#" action="getTimeExtend">续约</a>
            </li>
            <li id="awayBlock">
                <a id="btnAway" href="#" action="leave">暂离</a>
            </li>
            <li style="display: none" id="resumeBlock">
                <a id="btnResume" href="#" action="resume" >返回</a>
            </li>
            <li>
                <a id="btnCheckIn" href="#" action="checkIn">签到</a>
            </li>
        </ul>
	</div>
</div>
<!--header end of-->
<div class="warp">
    <div style="display: none;" id="msgBoxDIV" class="msgBoxDIV">
        <span class="msg">
        </span>
    </div>
    
<div class="menu fl">
    <ul>
        
            <li class=""><a href="/self" onFocus="this.blur()"><i class="seat"></i>自选座位</a></li>
            <li class=""><a href="/map" onFocus="this.blur()"><i class="layout"></i>布局选座</a></li>
            <li class=""><a href="/freeBook/fav" onFocus="this.blur()"><i class="layout"></i>常用座位</a></li>
        
        
        <li class=""><a href="/history?type=SEAT" onFocus="this.blur()"><i class="myReserve"></i>我的预约</a></li>
        <li class=""><a href="/user/violations" onFocus="this.blur()"><i class="myViolation"></i>违约记录</a></li>
        <li class=""><a href="/logout" onFocus="this.blur()"><i class="goBack"></i> 退  出</a></li>
    </ul>
</div>
    <!--menu end of-->
    <div class="mainContent fr">
        

<div class="content">
    <div class="layoutSeat">
        <dl>
        
            <dd>预约失败! </dd>
            <dd><span>已有1个有效预约，请在使用结束后再次进行选择</span></dd>
        
        </dl>
    </div>
</div>


    </div>
</div>

<div class="loading2"></div>
<div class="dialog" style="left: 780px; top: 424px;"><i class="loadIcon"></i>数据加载中, 请稍候 ...</div>

<!--签到-->
<div class="ToolTip_show SignIn_show" id="resultMessageDiv">
    <div class="ui_dialog">
    <a href="#" class="closeDIV">关闭</a>
        <div class="resultMessage">签到成功（失败原因）</div>
        <div class="handle">
            <input type="button" value="确定" class="btnOK" />
            <input type="button" value="退出系统" class="btnClose" id="btnExit"/>
        </div>
    </div>
</div>

<!--续约-->
<div class="ToolTip_show Renewal_show" id="extendDiv">
    <div class="ui_dialog">
        <a href="#" class="closeDIV">关闭</a>
        <p class="messageHead">选中下列时段进行续约</p>
        <ul class="renewal_List clear">
            <li>
                <a href="#">05:00</a>
            </li>
            <li>
                <a href="#">06:00</a>
            </li>
        </ul>
        <div class="resultMessage"></div>
        <div class="handle">
            <input type="button" value="确定" class="btnOK" action="extend"/>
        </div>
    </div>
</div>

<div id="spinner" class="spinner" style="display:none;">载入中</div>

<script type="text/javascript">
        setInterval(function(){setDateTime();}, 1000);

        $(function(){
            setDateTime();
            $(".handleBtns").hide();
            var userInfo = '{"currentReservationStatus":"NO_RESERVATION","hasPrevUnStoppedReservation":false,"userCheckedIn":false,"lastIn":null,"wifiAwayDisabled":false,"wifiStopDisabled":false,"softMode":false}';
            userInfo = $.parseJSON(userInfo);

            initializePage(userInfo);
            $("#btnExit").click(function(){
                window.location = "/logout";
            });
            
        });

        function btnClick(btn, param) {
            $(".loading2").css('display','block');
            var actionName = btn.attr("action");
            var paramAll = actionName;
            if (param) {
                paramAll += param;
            }
            $.ajax({
                url: "/user/" + paramAll,
                success: function(data){
                    showResult(actionName, true, data);
                },
                error:function(){
                    showResult(actionName, false, data);
                }
            });
        }

    </script>
</body>
</html>"""
    # compileHad = re.compile("已有2个有效预约，请在使用结束后再次进行选择")
    # compileInvalid = re.compile("Invalid CSRF token")
    # if len(compileHad.findall(text)) > 0:
    #     print("您已预约过，请先取消")
    # else:
    #     print("no")
    seat = "新增11"
    seatId = ''.join([x for x in seat if x.isdigit()])
    sleep(10)
    print(seatId)
