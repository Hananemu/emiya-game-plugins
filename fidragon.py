#coding:utf-8


import random
from libs.event.qqevent import onkeyword,oncommand
import requests

BASEURL = "http://127.0.0.1:5700"
firstPlayer=None
lastJoinedPlayer=None
def send(gid: int, text: str):
    d = {"message": text, "group_id": gid}
    requests.post(f"{BASEURL}/send_group_msg", data=d)

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
     
     def creatDice(self):
         self.diceList=[random.randint(1, 6) for i in range(3) ] 
         return self.diceList 
         
         
def effect(num,m,p):
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


m=None
playL={}
actorid=None
lock=False



@oncommand(promat=["."],cmd=["开始游戏"])
def newgame(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        m=Monster(40,40)
        if firstPlayer == None:
            send(gid=n.group_id,text="房间内没有玩家！")
            return
        firstPlayer.next=lastJoinedPlayer
        actorid=firstPlayer.id
        send(gid=n.group_id,text="游戏已经开始")
        lock=True
    except Exception as e:
        print(e)

@oncommand(promat=["."],cmd=["新建游戏"])
def handleClear(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        firstPlayer=None
        lastJoinedPlayer=None
        m=None
        playL={}
        actorid=None
        lock=False
        send(gid=n.group_id,text="旧的游戏已删除 新游戏已创建")
    except Exception as e:
        print(e)
    
@oncommand(promat=["."],cmd=["加入游戏"])
def handleClear(n):
    try:
        global firstPlayer
        global lastJoinedPlayer
        if lock:
            send(gid=n.group_id,text="对局已开始")
            return
        player=Player(n.sender.user_id)    
        playL[n.sender.user_id]=player
        lastJoinedPlayer=player
        if firstPlayer == None:
            firstPlayer = player
        send(gid=n.group_id,text="加入成功")
    except Exception as e:
        print(e)
        

    
@oncommand(promat=["."],cmd=["丢骰子"])
def throw(n):  
    try:
        if actorid == n.sender.user_id:
            list = playL[n.sender.user_id].createDice()
            send(gid=n.group_id,text=f"{actorid}击败恶龙")
        else:   
            send(gid=n.group_id,text="当前不是你的回合！")
    except Exception as e:
        print(e)
        
@oncommand(promat=["."],cmd=["选择"])
def throw(n):  
    try:
        n.arg=n.arg.replace(" ")
        n.arg=int(n.arg)
        player=playL[n.sender.user_id]
        if actorid == n.sender.user_id:
            if n.arg in player.diceList:
                send(gid=n.group_id,text=effect(n.arg,m,player)+m)
                if m.hp<=0:
                    send(gid=n.group_id,text="怪物已被打败！")
                    return
                actorid = player.next.id
            else:
                send(gid=n.group_id,text="没有这个骰子！")
        else:   
            send(gid=n.group_id,text="当前不是你的回合！")
    except Exception as e:
        print(e)
        
@oncommand(promat=["."],cmd=["玩家列表"])
def throw(n):  
    try:
        send(gid=n.group_id,text=playL)
    except Exception as e:
        print(e)
        
@oncommand(promat=["."],cmd=["怪兽状态"])
def throw(n):  
    try:
        s=m.toString()
        send(gid=n.group_id,text=s)
    except Exception as e:
        print(e)
