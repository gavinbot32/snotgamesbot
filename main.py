import twitchio
from twitchio.ext import eventsub, commands
from twitchio.ext import routines
from twitchio.ext.routines import routine

from settings import *
from objects import *
from config import *
import json
import seventv
import time
from datetime import datetime


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=TOKEN, prefix='!', initial_channels=['gavinbot32','marisnot12'])
        # self.defCommands = {"!sginit" : self.gameInit,"!sgend" : self.endGame, "!newteam" : self.newTeam, "!sgjoin" : self.playerJoin, "!sgstart" : self.gameStart, "!sgadd" : self.addPlayer,
        #                     "!sgroster" : self.roster
        #                     }
        self.defCommands = {"!bountyhelp" : self.bountyHelp, "!bountylist":self.bountyList, "!getstream": self.getStream, "!disability" : self.disablitity}
        self.curGame = None
        self.MESSAGES = []
        self.odd = True
        self.bounty = ""
        self.context = None
        self.bountyClaimed = False
        self.targetTime = 0
        #json variables
        self.configDict = set()
        with open("config.json","r") as f:
            self.configDict = json.load(f)
        f.close()

    @routines.routine(seconds=1.5,iterations=0)
    async def messageFunnel(self):
        self.odd = not self.odd
        if(len(self.MESSAGES)>0):
            msgObj= self.MESSAGES.pop(0)
            msg = msgObj.msg
            ctx = msgObj.ctx
            try:
                await ctx.send(msg+('  ' if self.odd else ''))
            except Exception as e:
                self.updateLog("There was an issue sending a message", e)


    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        if "bounty" in self.configDict.keys():
            self.bounty = self.configDict["bounty"]
        if "claimed" in self.configDict.keys():
            self.bountyClaimed = self.configDict["claimed"]
            if self.configDict["claimed"] == None:
                self.bountyClaimed = False
        if "targetTime" in self.configDict.keys():
            if self.configDict["targetTime"] > 0:
                self.targetTime = self.configDict["targetTime"]

        self.messageFunnel.start()

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return
        if message.author.name in BLACKLIST:
            return
        # Print the contents of our message to console...

        if (message.channel.name == "marisnot12"):
            try:
                self.updateStats(message)
            except Exception as e:
                self.updateLog(f"bot had an issue processing {message.author.name} message", e)

        if message.channel.name == "marisnot12":
            self.context = message.channel

        if self.bounty == "" or self.bounty == None:
            if message.channel.name == "marisnot12":
                self.context = message.channel
                await self.newBounty()


        if time.time() >= self.targetTime:
            await self.newBounty()

        print(message.content)

        messageSplit = message.content.split()
        emoteCount = 0
        if not self.bountyClaimed:
            for word in messageSplit:
                if emoteCount >= 5:
                    break
                if emoteClient.isEmote(word):
                    print("is in emote")
                    emoteCount += 1
                    if word == self.bounty:
                        await self.bountyCaught(message)




        args = []
        args = message.content.split(" ")
        for i in args:
            if i in ARGS_IGNORE:
                args = args.remove(i)
        if args[0].lower() in self.defCommands.keys():

            await self.defCommands.get(args[0].lower())(message,args)
        print(args)


    async def disablitity(self,message,args):
        msg = "I was diagnosed with being a streamer but im more than my disability Okey"
        self.newMessage(msg,message.channel)

    async def timeLeft(self,message,args):
        epochRemaining = self.targetTime - time.time()
        msg = time.strftime('%H hours, %M minutes and %S seconds remaining', time.gmtime(epochRemaining))
        print(msg)
        self.newMessage(msg,message.channel)
    def updateStats(self,message):
        stats = []
        userDict = {}
        newUser = True
        id = message.author.id
        with open("stats.json", "r") as f:
            stats = json.load(f)
            if stats != None:
                for user in stats:
                    if "id" in user:
                        if user["id"] == str(id):
                            newUser = False
                            if "username" in user:
                                if user["username"] != message.author.name:
                                    user["username"] = message.author.name
                            userDict = user
                            stats.remove(user)
                            break
            if newUser:
                userDict = {
                    "id": id,
                    "username": message.author.name
                }
            stats.append(userDict)
        f.close()
        if stats != None:
            with open("stats.json", "w") as f:
                f.write(json.dumps(stats, indent=4))
            f.close()


    def updateLog(self,message,exception):
        date = datetime.today()
        message = f"{date} | {message} | {exception}"
        print(message)
        with open("errorLog.txt", "w") as f:
            f.writelines(message+"\n")
        f.close()



    def updateLeaderboard(self,id,username):
        newPlayer = True
        id = id
        username = username.lower()
        leaderboard = []
        playerDict = {}
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
            if leaderboard != None:
                # print(len(leaderboard))
                for i in range(0, len(leaderboard)):
                    # print(i)
                    if "playerID" in leaderboard[i]:
                        # print(i)
                        # print("playerID inside")
                        if leaderboard[i]["playerID"] == str(id):
                            # print("found player")
                            newPlayer = False
                            playerDict = leaderboard[i]
                            leaderboard.remove(leaderboard[i])
                            playerDict["bounties"].append(self.bounty)
                            break
            if newPlayer:
                playerDict = {
                    "playerID": str(id),
                    "username": str(username),
                    "bounties": [self.bounty]
                }

            leaderboard.append(playerDict)
        f.close()
        if leaderboard != None:
            with open("leaderboard.json", "w") as f:
                f.write(json.dumps(leaderboard, indent=4))
            f.close()


    def newMessage(self,msg,ctx):
        x = MessageString(msg,ctx)
        self.MESSAGES.append(x)
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        # await self.handle_commands(message)

    async def gameInit(self, message,args):
        context = message.channel
        if self.curGame != None:
            self.newMessage(f'{message.author.name} there is already a Snot Game going on, to end a snot game type !endGame',context)
            return
        self.curGame = SnotGame(context,self)
        self.curGame.setGM(message.author.name)
        self.newMessage(f'{message.author.name} You have created a new Snot Game, Type !sgJoin to register 4Salute',context)


    async def bountyList(self,message,args):
        #check length of args
        #if args is greater then 2 check leaderboard for args 2 username
        #if args 2 isnt a username send an error message, otherwise send the list of the user
        id = message.author.id
        name = ""
        print(len(args))
        if len(args) > 1:
            with open("stats.json", "r") as f:
                stats = json.load(f)
                for user in stats:
                    if "username" in user:
                        arg = args[1]
                        userLower = user["username"]

                        if arg == userLower:
                            if "id" in user:
                                id = user["id"]
                                name = user["username"]
            f.close()
        else:
            name = message.author.name
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
            msg = (f"I'm sorry the user {name} has not claimed any bounties SAJ ")

            if leaderboard != None:
                for i in leaderboard:
                    if "playerID" in i:
                        if i["playerID"] == str(id):

                            uniqueList = []
                            uniqueCount = {}
                            setOneCount = 0
                            setTwoCount = 0
                            setOneString = ""
                            setTwoString = ""
                            for emote in i["bounties"]:
                                if emote not in uniqueList:
                                    uniqueList.append(emote)
                                    uniqueCount[emote] = 1
                                    if emote in MAR_SET:
                                        setOneCount +=1
                                    if emote in CLEO_SET:
                                        setTwoCount +=1
                                else:
                                    uniqueCount[emote] += 1
                            for emote in uniqueCount:
                                if emote in MAR_SET:
                                    setOneString += f"{emote} {uniqueCount[emote]} "
                                if emote in CLEO_SET:
                                    setTwoString += f"{emote} {uniqueCount[emote]} "
                            print(uniqueCount)
                            print(uniqueList)
                            msg = f"{name} {setOneCount}/{len(MAR_SET)} Mar: {setOneString} | {setTwoCount}/{len(CLEO_SET)} Cleo: {setTwoString}"
        f.close()
        self.newMessage(msg, message.channel)

    async def getStream(self,message,args):
        context = message.channel
        liveList = await self.fetch_streams([MAR_ID], None, None, None, None, "live")
        if liveList != None and len(liveList) > 0:
            print(liveList)
            self.newMessage("They are live", context)
        else:
            self.newMessage("They are not live", context)

    async def bountyHelp(self,message,args):
        context = message.channel

        liveList = await self.fetch_streams([MAR_ID], None, None, None, None, "live")
        if liveList == None or len(liveList) <= 0:
            self.newMessage("Every 3-10 hours a random emote is picked as a bounty, if you type the emote in chat you can claim the bounty and add the emote to your list (!bountyList)."
                            "   Once a bounty is claimed no one else can claim it until it resets once the timer is up."
                            " Note: this is spam proof, so sending paragraphs of emotes isn't going to claim the bounty. So don't make the chat messy with emotes, its not going to get you anywhere smh",context)

    async def newBounty(self):
        self.bountyClaimed = False
        while True:
            bounty = random.choice(BOUNTY_SET)
            if emoteClient.isEmote(bounty):
                self.bounty = bounty
                break
        print(self.bounty)
        # self.newMessage(f"A new emote bounty is up for grabs!",self.context)
        delay = random.randrange(TIMER_DELAY_MIN, TIMER_DELAY_MAX)
        self.targetTime = time.time() + delay
        self.writeToConfig()
    async def bountyCaught(self,message):
        context = message.channel
        self.bountyClaimed = True
        self.newMessage(f"{message.author.name} has claimed the bounty! {self.bounty}", context)
        self.writeToConfig()
        self.updateLeaderboard(message.author.id,message.author.name)


    def writeToConfig(self):
        with open("config.json","w") as outfile:
            outfile.write(json.dumps({"bounty":self.bounty, "claimed": self.bountyClaimed, "targetTime":self.targetTime}, indent=4))
        outfile.close()

    # @routine(seconds=1, iterations=3)
    # async def sendMessage(self,message,context):
    #     print("made it to send message")
    #     print(message)
    #     await context.send(message)
    #     print("Post Message")


    async def addPlayer(self,message,args):
        context = message.channel
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        if message.author.name != self.curGame.gameMaster:
            self.newMessage(f'{message.author.name} you are not the game master for the current game.',context)
            return
        if len(args) != 2:
            self.newMessage(f'{message.author.name} You must include a player name.',context)
            return

        message = self.curGame.playerJoin(args[1])
        self.newMessage(message,context)


    async def playerJoin(self,message,args):
        context = message.channel
        print(context)
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        message = self.curGame.playerJoin(message.author.name)
        self.newMessage(message,context)


    async def gameStart(self,message,args):
        context = message.channel
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        if message.author.name != self.curGame.gameMaster:
            self.newMessage(f'{message.author.name} you are not the game master for the current game.',context)
            return
        if self.curGame.closed:
            self.newMessage(f"Can't start a game that is already going idiot",context)
            return


        self.newMessage(f'Registration is closed, Snot games are starting!!!!',context)
        await self.curGame.startGame()


    async def roster(self,message,args):
        context = message.channel
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        if not self.curGame.closed:
            self.newMessage(
                f"{message.author.name} the game hasn't started yet",context)
            return
        message = self.curGame.getRoster()
        self.newMessage(message,context)

    async def newTeam(self, message, args):
        context = message.channel
        author = message.author.name
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        if message.author.name != self.curGame.gameMaster:
            self.newMessage(f'{message.author.name} you are not the game master for the current game.',context)
            return
        print(len(args)-1)
        if len(args)-1 != self.curGame.teamSize:
            self.newMessage(f'{author} in-valid team size. make teams of {self.curGame.teamSize}',context)
            return

        teamPlayers = []
        for arg in range(len(args)):
            if arg > 0:
                teamPlayers.append(args[arg])
        print("Team Players: ",teamPlayers)

        self.curGame.newTeam(teamPlayers)
        self.newMessage(teamPlayers,context)



    async def endGame(self,message,args):
        context = message.channel
        if self.curGame == None:
            self.newMessage(f'{message.author.name} there is not Snot Game going on idiot , to initiate a snot game type !sgInit Positive',context)
            return
        if message.author.name != self.curGame.gameMaster:
            self.newMessage(f'{message.author.name} you are not the game master for the current game.',context)
            return
        self.curGame = None
        self.newMessage(f'Snot Game Ended',context)


    #
    # @commands.command()
    # async def hello(self, ctx: commands.Context):
    #     # Here we have a command hello, we can invoke our command with our prefix and command name
    #     # e.g ?hello
    #     # We can also give our commands aliases (different names) to invoke with.
    #
    #     # Send a hello back!
    #     # Sending a reply back to the channel is easy... Below is an example.
    #     await ctx.send(f'Hello {ctx.author.name}{ctx.args[0]}!')
    #
    #



emoteClient = seventv.EmoteClient()
emoteClient.connect()

emoteClient.isEmote("marKek")

bot = Bot()
bot.run()