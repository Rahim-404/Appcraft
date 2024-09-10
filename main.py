import sys
import argparse
import asyncio

from PyQt5.QtWidgets import QSystemTrayIcon,QMenu,QApplication,QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread,pyqtSignal

from mcrcon import MCRcon
from mcstatus import JavaServer

from data.icons_rc import *

class AsyncTimer(QThread):
    signal = pyqtSignal()
    def __init__(self,interval):
        super().__init__()
        self.interval = interval
        self.running = False

    async def run_async(self):
        while self.running :
            await asyncio.sleep(self.interval)
            self.signal.emit()

    def run(self):
        self.running = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_async())

    def stop(self):
        self.running = False


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon,host,port,parent=None):
        #self.mcron = MCRcon(host=host,port=port,password=password)
        QSystemTrayIcon.__init__(self, icon, parent)
        
        self.host = host
        self.port = port 

        self.server = JavaServer.lookup("{}:{}".format(host,port))

        self.async_timer = AsyncTimer(2)
        self.async_timer.signal.connect(self.fill)

        self.messageClicked.connect(self.messageCleared)
        self.activated.connect(self.activatedCb)

        self.players = 0
        self.player_init = False
        self.is_open = False
        self.notificated = False
        self.menu = QMenu(parent)
        
        self.hostAction = self.menu.addAction("{}:{}".format(host,port))

        self.menu.addSeparator()
        self.errorActionLabel = self.menu.addAction("Could not find server")
        self.setInVisible(self.errorActionLabel)

        self.serverStateAction = self.menu.addAction("Offline")
        self.playersOnlineAction = self.menu.addAction("")
        
        self.versionAction = self.menu.addAction("")
        self.latencyAction =self.menu.addAction("")

        self.actions = [self.playersOnlineAction,self.versionAction,self.latencyAction]
        
        self.menu.addSeparator()

        exitAction = self.menu.addAction("Exit")
        exitAction.triggered.connect(self.destroy_app)

        self.setContextMenu(self.menu)
        for action in self.actions :
            self.setInVisible(action)

        self.async_timer.start()

    def activatedCb(self):
        print("activated")

    def messageCleared(self):
        print("Cleared")

    def copyHost(self):
        data = "{}:{}".format(self.host,self.port)
        pass

    def fill(self):
        try :
            status = self.server.status()

            self.notificated = False
            if self.is_open == False :
                self.is_open = True
                self.showMessage("Appcraft","server is online",QIcon(":/icons/online.ico"))
                self.setIcon(QIcon(":/icons/online.ico"))

            players_online = status.players.online

            """
            players = status.players.sample

            if players != None :
                max_palyers = 3
                index = 0
                players_count = len(players)
                players_string = ""
                for player in players :
                    players_string += player.name
                    if not (players[:-1] == player):
                        players_string += ","
                    index +=1
                    if index == max_palyers :
                        break
                
                if len(players) > max_palyers :
                    players_string = " and others"
                
                self.playersOnlineAction.setToolTip(players_string)
            else :
                self.playersOnlineAction.setToolTip("No player connected")
            """
            
            if self.players != players_online :
                diff = players_online - self.players
                if diff>0:
                    if players_online == 1 :
                        self.showMessage("Appcraft","1 player online",QIcon(":/icons/player_joined.ico"))
                    else :
                        if self.player_init == False :
                            self.showMessage("Appcraft","{} players online".format(players_online),QIcon(":/icons/player_joined.ico"))
                        else :
                            self.showMessage("Appcraft","{} player(s) joind and {} players online".format(diff,players_online),QIcon(":/icons/player_joined.ico"))
                else :
                    self.showMessage("Appcraft","{} player(s) left and {} players online".format(diff*(-1),players_online),QIcon(":/icons/player_joined.ico"))
                self.players = players_online
                self.player_init = True
                

            version = status.version.name
            max_players = status.players.max
            latency = status.latency

            self.serverStateAction.setText("Online")
            self.playersOnlineAction.setText("Players online {}/{}".format(players_online,max_players))
            self.versionAction.setText("Version : {}".format(version))
            self.latencyAction.setText("Latency : {}".format(int(latency)))
            self.setInVisible(self.errorActionLabel)
            for action in self.actions :
                self.setVisible(action)

        except :
            self.is_open = False
            if self.notificated == False:
                self.showMessage("Appcraft","server is offline",QIcon(":/icons/offline.ico"))
                self.setIcon(QIcon(":/icons/offline.ico"))
                self.notificated = True
            self.setVisible(self.errorActionLabel)
            self.serverStateAction.setText("Offline")
            for action in self.actions :
                self.setInVisible(action)

    def setVisible(self,widget):
        if widget.isVisible() == False:
            widget.setVisible(True)
    
    def setInVisible(self,widget):
        if widget.isVisible():
            widget.setVisible(False)
    

    def destroy_app(self):
        self.async_timer.stop()
        #QApplication.quit()
        sys.exit()

def get_parser():
    parser = argparse.ArgumentParser(
        description="connect to and get server status",
        add_help=False
    )
    parser.add_argument(
        "-h", 
        "--host", 
        metavar="HOST",
        dest="host",
        required=True, 
        help='Host to connect to'
    )

    parser.add_argument(
        "-p",
        "--port",
        metavar="PORT",
        dest="port",
        type=int,
        default=25565,
        help="Port to connect to",
    )

    return parser.parse_args()

def main(args):
    app = QApplication(sys.argv)

    w = QWidget()
    w.setWindowTitle("Minecraft status")
    trayIcon = SystemTrayIcon(QIcon(":/icons/icon.ico"),host=args.host,port=args.port, parent=w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    args = get_parser()
    main(args)