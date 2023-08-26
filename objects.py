import asyncio
from twitchio.ext import routines

from twitchio.ext import commands

import random

from settings import *
import math
class SnotGame():

    def __init__(self,context,bot):
        self.gameMaster = ""
        self.teams = []
        self.players = []
        self.deadPlayers = []
        self.closed = False
        self.context = context
        self.bot = bot
        self.update = 0
    def setGM(self, name):
        self.gameMaster = name

    def newTeam(self, teamPlayers):
        self.teams.append(teamPlayers)
        self.curTeam += 1

    def playerJoin(self, playerName):
        message = (f"{playerName} You've been added to the roster")
        if self.closed:
            message = (f'{playerName} Registeration has been closed SAJ')
            return message
        if playerName in BLACKLIST:
            message = (f"{playerName} You've been blacklisted pepeCringe")
            return message
        for i in self.players:
            if i.name == playerName:
                message = (f"{playerName} You've already been added to the roster idiot")
                return message
        self.players.append(Player(playerName))
        return message

    async def startGame(self):
        print("start Game")
        self.closed = True
        tempPlayers = []
        for i in self.players:
            tempPlayers.append(i)
        print(len(tempPlayers))
        print(self.players)

        teamNum = math.ceil(len(tempPlayers) / 2)
        print("teamnum",teamNum)
        for i in range(0,teamNum):
            print(i)
            if(tempPlayers != None):
                if len(tempPlayers) > 0:
                    team = []
                    x =random.choice(tempPlayers)
                    team.append(x)
                    tempPlayers.remove(x)
                    if len(tempPlayers) >= 2:
                        z = random.choice(tempPlayers)
                        team.append(z)
                        tempPlayers.remove(z)
                    print(team)
                    self.teams.append(team)
        print(self.context)
        rosterMsg = "Roster- "
        for i in range(len(self.teams)):
            rosterMsg += str("Team "+ str(i+1)+ " ")
            for x in self.teams[i]:
                rosterMsg += x.name + " "

        self.bot.newMessage(rosterMsg, self.context)
        self.updateGame()
    def updateGame(self):
        self.update+=1

        self.dayEvents()
        # Day-Night-Day-Night-Day-Event-Night

        # if self.update ==1 or self.update==3 or self.update==5:
        #     #day events
        # elif self.update == 2 or self.update == 4 or self.update == 7:
        #     # night events
        # elif self.update == 6:
        #     #event
        # elif self.update == 0:
        #     #bloodbath
        # else:
        #     self.update == 1




    def dayEvents(self):
        playerLeft = []
        for player in self.players:
            playerLeft.append(player)
        for player in playerLeft:
            playerLeft = self.filler(player, playerLeft)


    def filler(self, player,playersLeft):
        ret = []
        playersLeft.remove(player)
        event = random.choice(DAY_FILLER)
        playerNum = 0
        for i in event:
            if i == "|":
                playerNum += 1
        event = event.replace("|","")
        if i == 1:
            event = format(event,player.name)
        elif i == 2:
            x = random.choice(playersLeft)
            playersLeft.remove(x)

            event = format(event,player.name,x.name)
        elif i == 3:
            playersIn = []
            for x in range(i-1):
                x = random.choice(playersLeft)
                playersIn.append(x)
                playersLeft.remove(x)
            event = format(event, player.name, playersIn[0].name,playersIn[1].name)
        elif i == 4:
            playersIn = []
            for x in range(i - 1):
                x = random.choice(playersLeft)
                playersIn.append(x)
                playersLeft.remove(x)
            event = format(event, player.name, playersIn[0].name, playersIn[1].name,playersIn[2].name)
        elif i == 5:
            playersIn = []
            for x in range(i - 1):
                x = random.choice(playersLeft)
                playersIn.append(x)
                playersLeft.remove(x)
            event = format(event, player.name, playersIn[0].name, playersIn[1].name,playersIn[2].name,playersIn[3].name)
        print(event)
        self.bot.newMessage(event, self.context)
        return playersLeft

    def supplies(self,player):
        pass
    def steal(self, player):
        pass
    def spare(self, player):
        pass
    def die(self,player):
        pass
    def kill(self,player):
        pass

    def getRoster(self):
        message = "Roster: \n"
        for i in self.players:
            message += i.name + " "
        message += "\n Dead :"
        for i in self.deadPlayers:
            message += i.name + " "
        return message



class Player():

    def __init__(self, name):
        self.name = name
        self.killCount = 0


class MessageString():

    def __init__(self,msg,ctx):
        self.msg = msg
        self.ctx = ctx