import sys
import argparse
import asyncio

from PyQt5.QtWidgets import QSystemTrayIcon,QMenu,QApplication,QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread,pyqtSignal

from mcrcon import MCRcon
from mcstatus import JavaServer

from data.icons_rc import *

class AsyncThread(QThread):
    status_signal = pyqtSignal(dict)
    def __init__(self,server,interval):
        super().__init__()
        self.interval = interval
        self.server = server
        self.running = False

    async def run_async(self):
        while self.running :
            data = {"status":"offline"}
            try:
                status = await self.server.async_status(timeout=1)
                data["status"]="online"
                data["online_players"] = status.players.online
                data["max_players"] = status.players.max
                data["version"] = status.version.name
                data["latency"] = status.latency
                self.status_signal.emit(status)
            except Exception as e:
                self.status_signal.emit(data)
            await asyncio.sleep(self.interval)

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

        self.async_timer = AsyncThread(self.server,2)
        self.async_timer.status_signal.connect(self.fill)

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

    def fill(self,status):
        if status["status"]=="online":
            self.notificated = False
            if self.is_open == False :
                self.is_open = True
                self.showMessage("Appcraft","server is online",QIcon(":/icons/online.ico"))
                self.setIcon(QIcon(":/icons/online.ico"))

            online_players = status["online_players"]
            
            if self.players != online_players :
                diff = online_players - self.players
                if diff>0:
                    if online_players == 1 :
                        self.showMessage("Appcraft","1 player online",QIcon(":/icons/player_joined.ico"))
                    else :
                        if self.player_init == False :
                            self.showMessage("Appcraft","{} players online".format(online_players),QIcon(":/icons/player_joined.ico"))
                        else :
                            self.showMessage("Appcraft","{} player(s) joind and {} players online".format(diff,online_players),QIcon(":/icons/player_joined.ico"))
                else :
                    self.showMessage("Appcraft","{} player(s) left and {} players online".format(diff*(-1),online_players),QIcon(":/icons/player_joined.ico"))
                self.players = online_players
                self.player_init = True
                

            version = status["version"]
            max_players = status["max_players"]
            latency = status["latency"]

            self.serverStateAction.setText("Online")
            self.playersOnlineAction.setText("Players online {}/{}".format(online_players,max_players))
            self.versionAction.setText("Version : {}".format(version))
            self.latencyAction.setText("Latency : {}".format(int(latency)))
            self.setInVisible(self.errorActionLabel)
            for action in self.actions :
                self.setVisible(action)

        elif status["status"] == "offline" :
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