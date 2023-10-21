#coding:utf-8


import random
from libs.event.qqevent import onkeyword,oncommand
import requests
from libs.Logger import logInfo

firstPlayer=None
lastJoinedPlayer=None
m=None
playL={}
actorid=None
lock=False

class Monster:
    
    def __init__(self,m,n):
        self.hp=100*n
        self.defend=100*m
        self.debuff=0
        self.judu=0
        self.t=1
    
    def beAtt(self,fatt=0,tatt=0):
        
        totall=(fatt+self.debuff)*self.t+self.judu
        
        if fatt==0:
            self.hp-=totall
            r= f"怪物血量降低了{totall}点"
        
        else:
            if self.defend >= totall:
                self.defend-=totall
                r=f"对怪物造成{totall}点伤害 已被护甲值抵消"
                
            else:
                d=totall-defend
                self.defend=0
                self.hp-=d
                r = f"怪物护甲已被击破 血量降低{d}"
        self.reInit()
        return r
        
    def toString(self):
        global m
        return "怪物当前状态：\n血量："+m.hp+"\n防御："+m.defend+"\ndebuff："+m.debuff+"\n剧毒："+m.judu+"\n.受伤倍率："+m.t   
    
    def reInit(self):
        
        self.debuff=0
        self.judu=0
        self.t=1
        

        
class Player:
     
    def __init__(self,id):
        global lastJoinedPlayer
        self.id=id
        self.att=0
        self.diceList=[]
        self.next=lastJoinedPlayer
     
    def createDice(self):
        self.diceList=[random.randint(1, 6) for i in range(3) ] 
        return self.diceList 

    def toString(self):
        return self.id+"当前的攻击力是："+self.att

    def __str__(self):
        return str(self.id)
         
         
def effect(num,m,p):
    r="None!"
    if num==1:
        m.debuff=100
        r="怪物受到伤害提升"
    elif num==2:
        m.judu=150
        r="怪物受到额外伤害"   
    elif  num==3:
        r=m.beAtt(fatt=150)
    elif num==4:
        r=m.beAtt(tatt=200)
    elif num==5:
        m.t*=2
        r=m.beAtt(fatt=200)+"造成伤害翻倍"
    elif num==6:
        p.att+=100
        r=m.beAtt(fatt=p.att)
    return r





@oncommand(promat=["."],cmd=["开龙趴"])
async def newgame(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        global m
        global actorid
        global lock
        m=Monster(40,40)
        if firstPlayer == None:
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="房间里比你的试卷还空！")
            return
        firstPlayer.next=lastJoinedPlayer
        actorid=firstPlayer.id
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="游戏已经在润了")
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=f"当前是{actorid}的回合！")

        lock=True
    except Exception as e:
        logInfo(e)

@oncommand(promat=["."],cmd=["重开"])
async def handleClear(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        global m
        global playL
        global actorid
        global lock
        firstPlayer=None
        lastJoinedPlayer=None
        m=None
        playL={}
        actorid=None
        lock=False
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="旧的游戏像你未来的人生一样重开了")
    except Exception as e:
        logInfo(e)
    
@oncommand(promat=["."],cmd=["龙趴，启动"])
async def handleClear(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        global playL
        if lock:
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="龙趴已开始")
            return
        player=Player(n.netpackage.sender.user_id)    
        playL[n.netpackage.sender.user_id]=player
        lastJoinedPlayer=player
        if firstPlayer == None:
            firstPlayer = player
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="加入成功")
    except Exception as e:
        logInfo(e)
        

    
@oncommand(promat=["."],cmd=["丢骰子"])
async def throw(n):
    global actorid
    global playL
    player = playL[n.netpackage.sender.user_id]
    try:
        if not player.diceList:
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="你已经丢过骰子了！请选择："+str(player.diceList))
        else if actorid == n.netpackage.sender.user_id:
            l = player.createDice()
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=str(l))
        else:   
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=f"当前不是你的回合！现在的玩家是{actorid}")
    except Exception as e:
        logInfo(e)
        
@oncommand(promat=["."],cmd=["选择"])
async def choose(n):
    global playL
    global m
    global actorid
    try:
        #logInfo(str(n.netpackage.arg))
        n.netpackage.arg=n.netpackage.arg.replace(" ","")
        #choice=int(n.netpackage.arg)
        choice=n.netpackage.arg
        player=playL[n.netpackage.sender.user_id]
        if actorid == n.netpackage.sender.user_id:
            """
            bug：查不出来骰子
            """
            if choice in player.diceList:
                await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=effect(choice,m,player)+m.toString())
                if m.hp<=0:
                    await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=f"怪物已被{actorid}打败！")
                    return
                actorid = player.next.id
                await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=f"下一个玩家：{actorid}")
            else:
                await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message="没有这个骰子！")
        else:   
            await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=f"当前不是你的回合！现在的玩家是{actorid}")
    except Exception as e:
        logInfo(e)
        
@oncommand(promat=["."],cmd=["查房"])
async def throw(n):
    global playL
    try:
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=playL)
    except Exception as e:
        logInfo(e)
        
@oncommand(promat=["."],cmd=["怪兽状态"])
async def throw(n):
    global m
    try:
        s=m.toString()
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=s)
    except Exception as e:
        logInfo(e)

@oncommand(promat=["."],cmd=["debug"])
async def debug(n):
    global actorid
    try:
        msg="当前玩家："+str(actorid)
        logInfo(actorid)
        await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=msg)
    except Exception as e:
        logInfo(e)

@oncommand(promat=["."],cmd=["帮助"])
async def help(n):
    try:
        msg="开龙趴-Build a room\n重开-Replay\n龙趴，启动-Start\n丢骰子-Throw dice\n选择-Choose dice\n查房-Player list\n怪兽状态-Dragon state\ndebug-Debug(actorid)"
        test=await n.callAPI("send_group_msg",group_id=n.netpackage.getID(),message=msg)
        logInfo(test)
    except Exception as e:
        logInfo(e)
