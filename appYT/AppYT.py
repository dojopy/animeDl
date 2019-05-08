#!/usr/bin/env python
#coding: utf-8


from PySide import QtGui,QtCore
from threading import Thread
from crawler.crawlerYT import crawlerYT
from UpdateAnime.inspector import inspector
from FreneticDL.freneticDL import FreneticDL
from PySide.QtCore import QThread, QThreadPool, QObject, QRunnable, Signal,Slot
from time import sleep
from re import findall
from os import getenv,getcwd,path,remove,mkdir,sep,listdir
from sys import argv,platform,exit
from GUI.interfaz import Ui_MainWindow
from GUI.dialog import Ui_Dialog
from GUI.config import Preferencias
from cloudflare import bypass
from subprocess import Popen,PIPE
from sqlite3 import connect
from random import choice
import logging
from base64 import urlsafe_b64decode, urlsafe_b64encode,b64encode,b64decode
from functools import partial
from shutil import copyfile
#import qdarkstyle



logging.basicConfig(level=logging.INFO, format=' %(levelname)s : %(message)s :%(module)s:  line:%(lineno)d',)
## Variables Globales ##
UserAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
rutaPrede = ''
GlobalCookie = ''
abort = {}
pausar = {}
Global_Stream = {}
apagarPC = False
DownloadActiva = []
RemoveReg = []
Globales = ''
items_Id = {}
EstadoPing = ''
GoogleRecaptcha = False
Threads = 3
reconect = 100

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

try:
    # variable de entorno windows/linux LANG
    carpeta = 'AnimeYT'
    if platform == 'win32':
        rutaPrede = getenv('USERPROFILE')
        Temp = getenv('temp')
    elif platform == 'linux2':
        rutaPrede = getenv('HOME')
        Temp = r'/tmp/'

    if not path.exists(path.join(rutaPrede,'Downloads',carpeta)):
        mkdir(path.join(rutaPrede,'Downloads',carpeta))

    if not path.exists(path.join(Temp,'AppYT')):
        mkdir(path.join(Temp,'AppYT'))

    rutaPrede = path.join(rutaPrede,'Downloads',carpeta)
    Temp = path.join(Temp,'AppYT')
except Exception as e:
    raise e

class AppYT(QtGui.QMainWindow,Ui_MainWindow,crawlerYT,inspector):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.ThreadPool = list()

        self.pushButton_3.clicked.connect(self.QHilocrawler)
        self.pushButton_5.clicked.connect(self.SelectCarpeta)
        self.pushButton.clicked.connect(self.startDownload)
        self.pushButton_9.clicked.connect(self.WindowListaCap)

        self.pushButton_12.clicked.connect(self.HiloPlayVideo)
        self.pushButton_7.clicked.connect(self.threadSearch)

        self.lineEdit_3.returnPressed.connect(self.pushButton_7.click)
        self.lineEdit.returnPressed.connect(self.pushButton_3.click)

        self.cancelar.clicked.connect(self.abort)
        self.cancelar_todo.clicked.connect(self.abort_all)

        self.pausar.clicked.connect(self.pausarDownload)
        self.renaudar.clicked.connect(self.renaudarDownload)
        self.treeWidget.clicked.connect(self.showButton)
        self.checkBox_5.clicked.connect(self.CheckOpcion5)
        self.pushButton_11.clicked.connect(self.AnimesEmision)


        self.iconWait = QtGui.QIcon()
        self.iconWait.addPixmap(QtGui.QPixmap(_fromUtf8("img/wait.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconCheck = QtGui.QIcon()
        self.iconCheck.addPixmap(QtGui.QPixmap(_fromUtf8("img/check.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconRun = QtGui.QIcon()
        self.iconRun.addPixmap(QtGui.QPixmap(_fromUtf8("img/run.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.iconNull = QtGui.QIcon()
        self.iconNull.addPixmap(QtGui.QPixmap(_fromUtf8("img/null.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        openFile = QtGui.QAction('configuracion', self)
        openFile.setShortcut('Ctrl+c')
        openFile.setStatusTip('realizar algunos cambios')
        openFile.triggered.connect(self.Configure)
        self.menuOpciones.addAction(openFile)

        self.pushButton_13.clicked.connect(self.HiloOpenFile)

        self.pushButton_25.clicked.connect(self.AddFavoritos)
        self.pushButton_26.clicked.connect(self.RemoveFavoritos)
        # self.RandomUserAgent()

        self.listaUrl = list()
        self.rutaSave = rutaPrede
        self.filename= str()
        self.label_ruta.setText(_translate("MainWindow", "{0}".format(self.rutaSave), None))

        self.get_thread_3 = CreateBaseData()
        self.get_thread_3.signals.test.connect(self.Favoritos)
        self.get_thread_3.start()
        self.ThreadPool.append(self.get_thread_3)

        # self.get_thread_2 = SetCookie(firewall=False)
        # self.connect(self.get_thread_2, SIGNAL("showAnime"), self.showAnime)
        # self.get_thread_2.start()
        # self.ThreadPool.append(self.get_thread_2)

        self.pausar.setVisible(False)
        self.renaudar.setVisible(False)
        self.cancelar.setEnabled(True)
        self.cancelar.setVisible(False)
        self.pushButton.setEnabled(True)
        self.pushButton.setVisible(True)
        self.cancelar_todo.setVisible(True)
        self.cancelar_todo.setEnabled(True)
        self.pushButton_26.setVisible(False)

        #MONITOR DE TRABAJOS#######
        self.Multi_ = MultiThreads(Temp) ###ruta en sqlite
        self.Multi_.signals.startProgresBar.connect(self.startProgresBar)
        self.Multi_.signals.AddNewFiles.connect(self.AddNewFiles)
        self.Multi_.signals.cancelar.connect(self.Cancelar)
        self.Multi_.signals.StartDownloadGrap.connect(self.StartDownloadGrap)
        self.Multi_.start()
        self.ThreadPool.append(self.Multi_)
        ####################################

        # movie = QtGui.QMovie("img/load.gif")
        # self.label_49.setMovie(movie)
        # movie.start()
        self.imagesPerRow = 3   #imagenes por fila
        self.size=QtCore.QSize(190,280)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.scrollArea_2)
        self.gLayoutScroll = QtGui.QGridLayout(self.scrollAreaWidgetContents_2)
        self.row ,self.col = 0,0

        self.verticalLayout_2 = QtGui.QVBoxLayout(self)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.gLayoutScroll_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.row_ ,self.col_ = 0,0

        self.get_thread_ = PingHilo()
        self.get_thread_.signals.setPing.connect(self.setPing)
        self.get_thread_.start()
        self.ThreadPool.append(self.get_thread_)


        # self.other = HILO()
        # self.other.start()
        # self.other.check.emit()
        # self.ThreadPool.append(self.other)


    def AnimesEmision(self):
        self.remRow(widget=1)
        self.get_thread3 = threadSearch(temp=Temp)
        self.pushButton_11.setEnabled(False)
        self.connect(self.get_thread3, SIGNAL("Search"), self.Search)
        self.connect(self.get_thread3, SIGNAL("finish"), self.cargaCompleta)
        self.get_thread3.start()
        self.ThreadPool.append(self.get_thread3)

    def cargaCompleta(self):
        self.pushButton_11.setEnabled(True)



    def showAnime(self):
        url = 'http://www.animeyt.tv/dragon-ball-super'
        self.lineEdit.setText(_translate("MainWindow", "{0}".format(url), None))
        self.QHilocrawler()


    def RemoveFavoritos(self):
        try:
            if self.Name in self.MiListAnime:
                filename = b64encode(self.Name)
                con = connect(path.join(getcwd(),'database','BaseMiList.db'))
                cursor = con.cursor()
                values = (filename,)
                cursor.execute('DELETE FROM AppYT WHERE filename=?',values)
                con.commit()
                cursor.close()
                con.close()
                img = self.imagen.split(sep)[-1]
                destino = path.join(getcwd(),'img','Favoritos',img)
                remove(destino)
                self.remRow(widget=2)
                self.Favoritos()
                self.pushButton_26.setVisible(False)
                self.pushButton_25.setVisible(True)
        except Exception as e:
            logging.warning(unicode(e))


    def AddFavoritos(self):
        con = connect(path.join(getcwd(),'database','BaseMiList.db'))
        cursor = con.cursor()
        cursor.execute("SELECT * FROM AppYT")
        ide = 0
        try:
            origen = self.imagen
            name = origen.split(sep)[-1]
            destino = path.join(getcwd(),'img','Favoritos',name)
            copyfile(origen, destino)
        except Exception as e:
            logging.warning(unicode(e))

        while True:
            if cursor.execute("SELECT * FROM AppYT WHERE id = {0}".format(ide)).fetchone() == None:
                try:
                    filename = b64encode(self.Name)
                    url = urlsafe_b64encode(self.url)
                    rutaIMG = b64encode(destino)
                    cursor.execute("INSERT INTO AppYT VALUES ({0},'{1}','{2}','{3}')".format(ide,filename,url,rutaIMG))
                    ide += 1
                except Exception as e:
                    logging.warning(unicode(e))
                break
            ide += 1
        con.commit()
        cursor.close()
        con.close()
        self.remRow(widget=2)
        self.Favoritos()
        self.pushButton_26.setVisible(True)
        self.pushButton_25.setVisible(False)
        self.tabWidget.setCurrentIndex(3)


    def Favoritos(self):
        try:
            self.MiListImg,self.MiListAnime,self.MiListUrl = [],[],[]

            con = connect(path.join(getcwd(),'database','BaseMiList.db'))
            cursor = con.cursor()
            cursor.execute("SELECT * FROM AppYT")
            for number,registro in enumerate(cursor):
                filename = b64decode(registro[1])
                self.MiListAnime.append(filename)
                url = b64decode(registro[2])
                self.MiListUrl.append(url)
                rutaIMG = b64decode(registro[3])
                self.MiListImg.append(rutaIMG)
            cursor.close()
            con.close()

            variable = 50
            for img in self.MiListImg:
                if self.gLayoutScroll_2.count() > 3 or len(self.MiListImg) > 3:
                    variable = 0
                thumb = QtGui.QLabel("object_%d-%d"%(self.row_,self.col_))
                pixmap = QtGui.QPixmap(img)
                pixmap = pixmap.scaled(self.size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
                pixmap = pixmap.scaled(self.size)
                thumb.setPixmap(pixmap)
                thumb.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

                title = QtGui.QGroupBox(thumb)
                title.setGeometry(QtCore.QRect(0, variable, 190, 300))    #0,3 al inicio
                index = self.MiListImg.index(img)
                titleAnime = self.MiListAnime[index]
                title.setTitle(_fromUtf8(titleAnime))
                self.gLayoutScroll_2.addWidget(thumb, self.row_, self.col_)
                self.col_ +=1
                if self.col_ % self.imagesPerRow == 0:
                    self.row_ += 1
                    self.col_ = 0
                title.mousePressEvent = partial(self.GetObject, source_object=title,Favoritos=True)
        except Exception as e:
            logging.warning(unicode(e))


    def ResultSearch(self):
        try:
            variable = 45
            for img in self.List_Animes_img:
                if self.gLayoutScroll.count() > 3 or len(self.List_Animes_img) > 3:
                    variable = 0
                thumb = QtGui.QLabel("object%d-%d"%(self.row,self.col))
                pixmap = QtGui.QPixmap(img)
                pixmap = pixmap.scaled(self.size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
                pixmap = pixmap.scaled(self.size)
                thumb.setPixmap(pixmap)
                thumb.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                title = QtGui.QGroupBox(thumb)
                title.setGeometry(QtCore.QRect(0, variable, 190, 300))    #0,3 al inicio
                index = self.List_Animes_img.index(img)
                titleAnime = self.List_Animes_name[index]
                title.setTitle(_fromUtf8(titleAnime))
                self.gLayoutScroll.addWidget(thumb, self.row, self.col)
                self.col +=1
                if self.col % self.imagesPerRow == 0:
                    self.row += 1
                    self.col = 0
                title.mousePressEvent = partial(self.GetObject, source_object=title,Favoritos=False)
        except Exception as e:
            logging.warning(unicode(e))


    def GetObject(self, event, source_object=None,Favoritos=False):
        if not Favoritos:
            name = source_object.title()
            index = self.List_Animes_name.index(name)
            self.lineEdit.setText(_translate("MainWindow", "{0}".format(self.List_Animes_url[index]), None))
        else:
            name = source_object.title()
            index = self.MiListAnime.index(name)
            self.lineEdit.setText(_translate("MainWindow", "{0}".format(self.MiListUrl[index]), None))

        self.QHilocrawler()
        self.tabWidget.setCurrentIndex(0)


    def remRow(self,widget=None):
        try:
            if widget == 1:
                self.row, self.col = 0,0
                while self.gLayoutScroll.count():
                    item = self.gLayoutScroll.takeAt(0)
                    widget = item.widget()
                    widget.deleteLater()
            elif widget == 2:
                self.row_ ,self.col_ = 0,0
                while self.gLayoutScroll_2 .count():
                    item = self.gLayoutScroll_2.takeAt(0)
                    widget = item.widget()
                    widget.deleteLater()
        except:
            pass


    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Up:
            self.showButton()
        elif key == QtCore.Qt.Key_Down:
            self.showButton()


    def Configure(self):
        pre = Preferencias(self)
        self.connect(pre, SIGNAL("setItem"), self.setItem)
        self.connect(pre, SIGNAL("SelectCarpeta"), self.SelectCarpeta)
        pre.setupUi()
        pre.exec_()


    def WindowListaCap(self):
        try:
            ui = Ui_Dialog(self)
            ui.signals.setItem.connect(self.setItem)
            ui.setupUi(self.listaNameCap)
            # ui.show()
            ui.exec_()
        except:
            pass

    def SaveConfig(self):
        pass
        #seteas datos en variabees globales y guardar en sql



    def setItem(self,filename):
        n,u = list(),list()
        i = self.listaNameCap.index(filename)
        n.append(self.listaNameCap[i])
        u.append(self.listaUrl[i])
        subcarpeta = self.Name
        self.AddNewFiles()
        ruta = path.join(self.rutaSave,subcarpeta)
        self.startProgresBar(0,'','',self.listaNameCap[i]+'.mp4','','','False','wait',ruta)
        self.obj = AddWorks(n,u,ruta)
        self.obj.start()
        self.ThreadPool.append(self.obj)


    def RandomUserAgent(self):
        global UserAgent
        l = ['Mozilla/5.0 (X11; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0',
            'Mozilla/5.0 (Windows NT 5.1; rv:26.0) Gecko/20100101 Firefox/26.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20130331 Firefox/21.0']
        UserAgent = choice(l)


    def showButton(self):
        try:
            if self.treeWidget.currentItem().text(2) == str() and len(self.treeWidget.currentItem().text(0)) > 0:
                self.clearData(0)
                self.cancelar.setEnabled(True)
                self.cancelar.setVisible(True)
                self.pausar.setVisible(False)
                self.renaudar.setVisible(False)
            elif self.treeWidget.currentItem().text(0) == str():
                self.clearData(0)
                self.cancelar.setVisible(False)
                self.pausar.setVisible(False)
                self.renaudar.setVisible(False)
            elif self.treeWidget.currentItem().text(2) == str(100):
                self.clearData(100)
                self.cancelar.setVisible(False)
                self.pausar.setVisible(False)
                self.renaudar.setVisible(False)
                self.pushButton_12.setEnabled(True)
                self.pushButton_12.setVisible(True)
        except:
            pass


    def clearData(self,value):
        self.progressBar.setProperty("value", value)
        self.label_53.setText(_translate("MainWindow", "Transcurrido: {0}".format(''), None))
        self.label_47.setText(_translate("MainWindow", "Tasa: {0}".format(''), None))
        self.label_49.setText(_translate("MainWindow", "MB/cap: {0}".format(''), None))
        self.label_51.setText(_translate("MainWindow", "Finaliza en: {0}".format(''), None))
        self.label_52.setText(_translate("MainWindow", "cap: {0}".format(''), None))


    def abort_all(self):
        global abort,pausar,items_Id,Global_Stream
        root = self.treeWidget.invisibleRootItem()
        number_items = root.childCount()
        if number_items > 0:
            pausar = dict()
            items_Id = dict()
            Global_Stream = dict()
            for i in range(int(number_items)):
                try:
                    abort[str(self.treeWidget.topLevelItem(i).text(0))] = True
                except:
                    pass
            self.treeWidget.clear()
            if path.exists(path.join(getcwd(),'database','BaseTemp.db')):
                remove(path.join(getcwd(),'database','BaseTemp.db'))
                con = connect(path.join(getcwd(),'database','BaseTemp.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , filename text UNIQUE , enlace text ,ruta text)'
                cursor.execute(query)
                cursor.close()
                con.close()


    def closeEvent(self,evento):
        try:
            if len(DownloadActiva) > 0:
                flags = QtGui.QMessageBox.Yes
                flags |= QtGui.QMessageBox.No
                r = QtGui.QMessageBox.information(self,'alerta','Descarga en proceso desea cancelar y salir?',flags)
                if r == QtGui.QMessageBox.Yes:
                    for x in xrange(len(self.ThreadPool)):
                        # print 'kill thread'
                        x.terminate()
                elif r == QtGui.QMessageBox.No:
                    evento.ignore()
            else:
                files = listdir(Temp)
                if len(files) > 0:
                    for x in files:
                        remove(path.join(Temp,x))

                for x in xrange(len(self.ThreadPool)):
                    # print 'kill thread'
                    x.terminate()

        except:
            pass


    def CheckOpcion5(self):
        global apagarPC
        if self.checkBox_5.isChecked:
            apagarPC = True
        else:
            apagarPC = False

    def setPing(self,ping,estado):
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:8pt;\">{0} ms</span></p></body></html>".format(ping), None))
        if estado == 'estable':
            self.PING.setStyleSheet(_fromUtf8("border-image: url(img/boton_azul.png);"))
        elif estado == 'inestable':
            self.PING.setStyleSheet(_fromUtf8("border-image: url(img/boton_amari.png);"))
        elif estado == 'off':
            self.PING.setStyleSheet(_fromUtf8("border-image: url(img/button_red.png);"))


    def HiloPlayVideo(self):
        global Global_Stream
        self.item = self.treeWidget.currentItem()
        if self.item.text(2) == str(100):
            ruta = str(self.item.text(6))
            name = str(self.item.text(0))
            r = path.join(ruta,name)
            if platform == 'linux2':
                cmd = 'vlc "{0}"'.format(r)
            elif platform == 'win32':
                # wmplayer = path.join(getenv('PROGRAMFILES') ,'Windows Media Player' ,'wmplayer.exe')
                vlc = path.join(getenv('PROGRAMFILES') ,'VideoLAN', 'VLC','vlc.exe')
                cmd = '"{0}" "{1}"'.format(vlc, path.join(ruta,name))

            proc = Popen(cmd, shell=True)

        else:
            key = str(self.item.text(0))
            Global_Stream[key] = True


    def HiloOpenFile(self):
        self.get_thread4 = OpenFile(self.rutaSave)
        self.get_thread4.start()
        self.ThreadPool.append(self.get_thread4)


    def threadSearch(self):
        nameAnime = str(self.lineEdit_3.text())
        if nameAnime is str():
            return
        self.remRow(widget=1)
        self.get_thread3 = threadSearch(nameAnime,temp=Temp)
        self.get_thread3.signals.Search.connect(self.Search)
        self.get_thread3.start()
        self.ThreadPool.append(self.get_thread3)

    def Search(self,List_Animes_img,List_Animes_url,List_Animes_name):
        self.activeSearch = True
        self.List_Animes_img = List_Animes_img
        self.List_Animes_url = List_Animes_url
        self.List_Animes_name = List_Animes_name
        self.remRow(widget=1)
        self.ResultSearch()


    def QHilocrawler(self):
        self.url = str(self.lineEdit.text())
        self.url = self.url.replace('\n','').strip(' ')
        self.thread12 = Hilocrawler(self.url,temp=Temp)
        self.thread12.signals.crawler.connect(self.crawler)
        self.thread12.start()
        self.ThreadPool.append(self.thread12)

    def crawler(self,name,seri_info,img,number_cap,next_cap,fecha,estado,list_gen,listNameCap,lurl,UltimoCap,CapMayor):
        self.Name = name
        self.listaNameCap = listNameCap
        self.listaUrl = lurl
        self.SerieInfo = seri_info
        self.imagen  = img
        self.NumberCapis = number_cap
        self.NextCap = next_cap
        self.Fecha = fecha
        self.Estado = estado
        self.listGenero = list_gen
        self.UltimoCap = UltimoCap
        self.CapMayor = CapMayor

        ######### seteando datos en App #############
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600; color:#0099ff;\">{0}</span></p></body></html>".format(self.Name), None))
        self.textBrowser.setHtml(_translate("MainWindow", "<html><style type=\"text/css\">\n""p, li { white-space: pre-wrap; }\n""</style></head><body style=\" font-family:\'URW Gothic L\'; font-size:9pt; font-weight:56; font-style:normal;\">\n""<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s</p></body></html>"%(self.SerieInfo) , None))
        self.label_6.setPixmap(QtGui.QPixmap(_fromUtf8("{0}".format(self.imagen))))
        self.label_36.setText(_translate("MainWindow", "Capitulos actuales: <span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.NumberCapis), None))
        self.label_34.setText(_translate("MainWindow", "Siguiente Cap: <span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.NextCap), None))
        self.label_37.setText(_translate("MainWindow", "Fecha de estreno:<span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.Fecha), None))
        self.label_33.setText(_translate("MainWindow", "Estado: <span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.Estado), None))
        self.label_38.setText(_translate("MainWindow", "Genero: <span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.listGenero), None))
        self.label_35.setText(_translate("MainWindow", "Ultimo cap: <span style=\" font-family:'Roboto'; font-size:10pt; color:#0099ff;\">{0}</span>".format(self.UltimoCap), None))
        self.checkBox_6.setText(_translate("MainWindow", "Actualizar Carpeta: {0}".format(self.Name), None))

        if self.Name in self.MiListAnime:
            self.pushButton_25.setVisible(False)
            self.pushButton_26.setVisible(True)
        else:
            self.pushButton_26.setVisible(False)
            self.pushButton_25.setVisible(True)



    def SelectCarpeta(self):
        self.rutaSave = str(QtGui.QFileDialog.getExistingDirectory(None, "Carpeta de Almacenamiento Principal",'.'))
        self.label_ruta.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-weight:400; text-decoration: underline;\">{0}</span></p></body></html>".format(self.rutaSave), None))



    def startDownload(self):
        selecc = False
        listUrl = list()
        listName = list()
        subcarpeta = str()
        # extrayendo line-edit y parsing
        url = str(self.lineEdit.text())

        if '/ver/' in url:
            if 'sub' in url:
                # http://www.animeyt.tv/ver/one-piece-759-sub-espanol
                self.Number_Cap_download = findall('-([\d]{1,5})-sub-espanol',url)[0]
                deleSub = '-'+str(self.Number_Cap_download)+'-sub-espanol'
                ###limpieza de Name###
                self.Name = url.split('/')[-1]
                self.Name = self.Name.strip(' ')
                self.Name = self.Name.replace(deleSub,'')
                self.Name = self.Name.replace('\n','')
                self.url_info = url.replace('/ver','')
                self.url_info = self.url_info.replace(deleSub,'')
        else:
            self.url_info = url
            #self.Name = 'life.mp4'  #solo prueba
            self.Name = self.Name.strip(' ')
            self.Name = self.Name.replace('\n','')

        subcarpeta = self.Name
        # comprobando check1 activado
        if self.checkBox_3.isChecked():
            self.Number_Cap_download = self.lineEdit_2.text()
            if len(self.Number_Cap_download) > 0:
                selecc = True
                pag = 'http://www.animeyt.tv/ver/'+str(self.url_info.split('/')[-1])+'-'+str(self.Number_Cap_download)+'-sub-espanol'
                pag = pag.replace('\n','')
                pag = pag.strip(' ')
                self.Name = self.Name.strip(' ')
                self.nombre = self.Name +' '+str(self.Number_Cap_download)
                self.nombre = self.nombre.replace('\n','')
                listUrl.append(pag)
                listName.append(self.nombre)


        #ACTUALIZANDO VIDEOTECA DE ANIMES
        elif self.checkBox_6.isChecked():
            ruta = path.join(self.rutaSave,self.Name)
            inspector.start(self,ruta,self.CapMayor)
            if len(self.listActualizar) > 0:
                flags = QtGui.QMessageBox.Yes
                flags |= QtGui.QMessageBox.No
                r = QtGui.QMessageBox.information(self,'Detalles...','Carpeta Local: %s. \n\nCapitulos actuales desde AnimeYT: %s. \n\nCapitulos en carpeta:\n %s. \n\nSe actualizaran los cap:\n %s.'%(str(self.dir_anime),str(self.totalCapAnime),str(self.newLis),str(self.listActualizar)),flags)
                if r == QtGui.QMessageBox.Yes:
                    selecc = True
                    for x in self.listActualizar:
                        pag = 'http://www.animeyt.tv/ver/'+str(self.url_info.split('/')[-1])+'-'+str(x)+'-sub-espanol'
                        pag = pag.replace('\n','')
                        pag = pag.strip(' ')
                        self.Name = self.Name.strip(' ').replace('\n','')
                        self.nombre = self.Name +' '+str(x)
                        listUrl.append(pag)
                        listName.append(self.nombre)

                elif r == QtGui.QMessageBox.No:
                    pass
            else:
                QtGui.QMessageBox.about(self, "Estado",'LA CARPETA %s ESTA ACTUALIZADA!!'%(str(self.dir_anime)))


        #comprobando check2 acitivado
        elif self.checkBox_4.isChecked():
            self.inicio = self.lineEdit_4.text()
            self.final = self.lineEdit_5.text()
            if len(self.inicio) > 0:
                self.inicio = int(self.lineEdit_4.text())
            if len(self.final) > 0:
                self.final = int(self.lineEdit_5.text())
            else:
                self.final = self.NumberCapis

            if (self.final > self.inicio):
                selecc = True
                for capitulo in range(self.inicio,self.final+1):
                    pag = 'http://www.animeyt.tv/ver/'+str(self.url_info.split('/')[-1])+'-'+str(capitulo)+'-sub-espanol'
                    pag = pag.replace('\n','')
                    listUrl.append(pag)
                    self.Name = self.Name.strip(' ')
                    self.nombre = self.Name +' '+str(capitulo)
                    listName.append(self.nombre.replace('\n',''))


        elif self.checkBox.isChecked():
            selecc = True
            self.listaNameCap.reverse()
            self.listaUrl.reverse()
            listName = self.listaNameCap
            listUrl = self.listaUrl


        else:
            QtGui.QMessageBox.about(self, "Estado",'Seleccione una opcion!')

        ruta = path.join(self.rutaSave,subcarpeta)
        for i in listName:
            self.AddNewFiles()
            self.startProgresBar(0,'','',i+'.mp4','','','False','wait',ruta)
        self.obj = AddWorks(listName,listUrl,ruta)
        self.obj.start()
        self.ThreadPool.append(self.obj)


    def StartDownloadGrap(self):
        self.progressBar.setValue(0)
        self.cancelar.setVisible(True)
        self.pausar.setVisible(True)
        self.pausar.setEnabled(True)


    def pausarDownload(self):
        global pausar
        try:
            self.pausar.setVisible(False)
            self.renaudar.setVisible(True)
            self.renaudar.setEnabled(True)
            self.item = self.treeWidget.currentItem()
            key = str(self.item.text(0))
            pausar[key] = True
        except:
            pass


    def renaudarDownload(self):
        global pausar
        self.renaudar.setVisible(False)
        self.pausar.setVisible(True)
        self.pausar.setEnabled(True)
        self.item = self.treeWidget.currentItem()
        key = str(self.item.text(0))
        pausar[key] = False


    Slot(str)
    def Cancelar(self,filename):
        global abort
        try:
            self.renaudar.setVisible(False)
            self.pausar.setVisible(False)
            self.cancelar.setVisible(False)
            self.startProgresBar(0,'','',str(filename),'','','False','abort','')
            self.clearData(0)
            self.item = self.treeWidget.currentItem()
            key = self.item.text(0)
            if abort.get(key,False):    abort.pop(key)
            self.showButton()
        except Exception as e:
            logging.warning(unicode(e))


    def AddNewFiles(self):
        QtGui.QTreeWidgetItem(self.treeWidget)

    def startProgresBar(self,porcentaje,MegaEstado,rate,filename,time_rest,cronometro,video_stream,StateFile,ruta):
        global items_Id

        self.filename = str(filename)
        active_stream = str(video_stream)
        self.porcentaje = float(porcentaje)
        root = self.treeWidget.invisibleRootItem()
        number_items = root.childCount()

        if items_Id.get(self.filename,None) != None:
            Id = items_Id[self.filename]
        else:
            for x in range(int(number_items)):   #setear casilla
                try:
                    Id = x
                    self.item_check = self.treeWidget.topLevelItem(Id)
                    if len(str(self.item_check.text(0))) == 0:   #nueva casillla
                        items_Id[self.filename] = Id
                        break
                    elif len(str(self.item_check.text(0))) > 1:
                        continue
                except Exception as e:
                    logging.warning(unicode(e))

        try:
            if self.porcentaje == 0:
                porcentaje = str()
            if StateFile == 'abort':
                self.filename = str()
                self.treeWidget.topLevelItem(Id).setIcon(0, self.iconNull)


            self.treeWidget.topLevelItem(Id).setText(0, _translate("MainWindow", str(self.filename), None))
            self.treeWidget.topLevelItem(Id).setText(1, _translate("MainWindow", str(rate), None))
            self.treeWidget.topLevelItem(Id).setText(2, _translate("MainWindow", str(porcentaje), None))
            self.treeWidget.topLevelItem(Id).setText(3, _translate("MainWindow", str(MegaEstado), None))
            self.treeWidget.topLevelItem(Id).setText(4, _translate("MainWindow", str(time_rest), None))
            self.treeWidget.topLevelItem(Id).setText(5, _translate("MainWindow", str(cronometro), None))
            self.treeWidget.topLevelItem(Id).setText(6, _translate("MainWindow", str(ruta), None))

            ###set img Estado####
            if StateFile == 'run':
                self.treeWidget.topLevelItem(Id).setIcon(0, self.iconRun)
            elif StateFile == 'wait':
                self.treeWidget.topLevelItem(Id).setIcon(0, self.iconWait)
            elif StateFile == 'completo':
                self.treeWidget.topLevelItem(Id).setIcon(0, self.iconCheck)

        except Exception as e:
            logging.warning(unicode(e))

        #seteando InterfazPrincipal
        try:
            self.item = self.treeWidget.topLevelItem(Id).text(0)

            # self.item = self.treeWidget.currentItem()
            # if self.item == None:
            #     self.item = self.treeWidget.topLevelItem(Id).text(0)
            # else:
            #     self.item = self.item.text(0)

            if self.item == self.filename:
                self.progressBar.setProperty("value", self.porcentaje)
                self.label_53.setText(_translate("MainWindow", "Transcurrido: {0}".format(cronometro), None))
                self.label_47.setText(_translate("MainWindow", "Tasa: {0}".format(str(rate)), None))
                self.label_49.setText(_translate("MainWindow", "MB/cap: {0}".format(MegaEstado), None))
                self.label_51.setText(_translate("MainWindow", "Finaliza en: {0}".format(time_rest), None))
                self.label_52.setText(_translate("MainWindow", "cap: {0}".format(filename), None))

                if pausar.get(str(self.filename),False):
                    self.pausar.setVisible(False)
                    self.renaudar.setVisible(True)
                    self.renaudar.setEnabled(True)
                    self.cancelar.setVisible(True)
                    self.cancelar.setEnabled(True)
                else:
                    self.renaudar.setVisible(False)
                    self.pausar.setVisible(True)
                    self.pausar.setEnabled(True)
                    self.cancelar.setVisible(True)
                    self.cancelar.setEnabled(True)
                if active_stream == 'True':
                    self.pushButton_12.setEnabled(True)
                    self.pushButton_12.setVisible(True)

                else:
                    self.pushButton_12.setVisible(True)
                    self.pushButton_12.setEnabled(False)
            elif self.item == '':
                self.pausar.setVisible(False)
                self.renaudar.setVisible(False)
                self.cancelar.setVisible(False)
                self.progressBar.setProperty("value", 0)
                self.label_53.setText(_translate("MainWindow", "Transcurrido: {0}".format(''), None))
                self.label_47.setText(_translate("MainWindow", "Tasa: {0}".format(''), None))
                self.label_49.setText(_translate("MainWindow", "MB/cap: {0}".format(''), None))
                self.label_51.setText(_translate("MainWindow", "Finaliza en: {0}".format(''), None))
                self.label_52.setText(_translate("MainWindow", "cap: {0}".format(''), None))

        except Exception as e:
            logging.warning(unicode(e))


    def abort(self):
        global abort
        name = self.treeWidget.currentItem().text(0)
        abort[str(name)] = True
        self.startProgresBar(0,'','',str(name),'','','False','abort','')


class DownloadHilo(QRunnable,FreneticDL,crawlerYT):
    def __init__(self,url,name,ruta,temp):
        super(DownloadHilo, self).__init__()
        self.signals = Communicate()
        self.url = url
        self.name = name
        self.ruta = ruta
        self.filename = str()
        self.estate = True
        self.rate = str()
        self.porcentaje = 0
        self.MegaEstado = str()
        self.restante = str()
        self.cronometro = str()
        self.abort = False
        self.pause = False
        self.total_cap = len(url)
        self.video_stream = True
        self.startPorcen = 5
        self.Firewall = False
        self.NetError = False
        self.StateFile = 'wait'

    def VideoStream(self):
        global Global_Stream
        if Global_Stream[self.filename] and (self.porcentaje >= self.startPorcen):
            self.activo = True
            self.abort_stream = False
            file_temp = self.filename
            #file_temp = file_temp.replace(' ','_')
            __t = Thread(target=FreneticDL.ConcatPlay,args=(self,file_temp,Temp))
            __t.setDaemon(True)
            __t.start()

            if platform == 'linux2':
                #totem,vlc,dragon
                cmd = 'vlc "{0}"'.format(path.join(getcwd(),Temp,file_temp))
            elif platform == 'win32':
                # wmplayer = path.join(getenv('PROGRAMFILES') ,'Windows Media Player' ,'wmplayer.exe')
                vlc = path.join(getenv('PROGRAMFILES') ,'VideoLAN', 'VLC','vlc.exe')
                cmd = '"{0}" "{1}"'.format(vlc, path.join(getcwd(),Temp,file_temp))

            proc = Popen(cmd, shell=True)
            proc.wait()
            sleep(3)
            self.abort_stream = True
            Global_Stream[self.filename] = False
            self.activo = False

    def enviar(self):
        try:
            self.activo = False
            while self.estate:
                if self.StateFile == 'wait':
                    sleep(1)
                    continue

                self.abort = abort.get(self.filename,False)
                self.pause = pausar.get(self.filename,False)

                if self.abort:
                    self.signals.cancelar.emit(self.filename)
                    break
                else:
                    self.signals.startProgresBar.emit(str(self.porcentaje),str(self.MegaEstado),str(self.rate),str(self.filename),str(self.restante),str(self.cronometro),str(self.video_stream),str(self.StateFile.split()[1]),self.ruta)
                if (self.porcentaje) >= self.startPorcen:
                    self.video_stream = True
                if Global_Stream.get(self.filename,False) and not self.activo:
                    __t = Thread(target=self.VideoStream)
                    __t.setDaemon(True)
                    __t.start()
                if self.StateFile.split()[1] == 'completo':
                    self.signals.startProgresBar.emit(str(100),'Finalizado!',str(),str(self.filename),str(0),str(self.cronometro),str(self.video_stream),str(self.StateFile.split()[1]),self.ruta)
                    break
                sleep(0.3)
        except Exception as e:
            logging.warning(unicode(e))
            return

    def run(self):
        global abort,pausar,DownloadActiva,RemoveReg

        if not (self.url is None):
            try:
                self.filename = self.name
                if abort.get(self.filename,False):
                    RemoveReg.append(self.filename)
                    return

                ######## buscando capitulo en la carpeta #########
                if path.exists(path.join(self.ruta,self.filename)):
                    self.signals.cancelar.emit(self.filename)
                    self.signals.startProgresBar.emit(str(100),str(self.MegaEstado),str(),str(self.filename),str(0),str(self.cronometro),str(self.video_stream),'completo',self.ruta)
                    self.signals.AddNewFiles.emit()
                    RemoveReg.append(self.filename)
                    return
                else:
                    DownloadActiva.append(self.filename)

                crawlerYT.__init__(self)

                crawlerYT.ExtraerUrlVideo(self,self.url,GlobalCookie,UserAgent,GoogleRecaptcha=GoogleRecaptcha)
                #self.listaUrl = ['http://127.0.0.1/video']

                if self.NetError:
                    crawlerYT.ExtraerUrlVideo(self,self.url,GlobalCookie,UserAgent,GoogleRecaptcha=GoogleRecaptcha)
                    if self.NetError:
                        DownloadActiva.remove(self.filename)
                        return
                elif self.Firewall:
                    setCookie = SetCookie(url=self.url,firewall=True)
                    setCookie.start()
                    setCookie.wait()
                    crawlerYT.ExtraerUrlVideo(self,self.url,GlobalCookie,UserAgent,GoogleRecaptcha=GoogleRecaptcha)


                try:
                    _t = Thread(target=self.enviar)
                    _t.setDaemon(True)
                    _t.start()
                    self.signals.StartDownloadGrap.emit()       #chekar
                    FreneticDL.__init__(self)
                    for i in range(len(self.listaUrl)):
                        FreneticDL.download_file(self,self.listaUrl[i],self.filename,self.ruta,self.sesi[i],UserAgent,Temp,reconect,Threads)

                        if self.UrlFaill or self.NotRangeSupport:
                            crawlerYT.ExtraerUrlVideo(self,self.url,GlobalCookie,UserAgent,GoogleRecaptcha=GoogleRecaptcha)
                            FreneticDL.__init__(self)
                            FreneticDL.download_file(self.listaUrl[i],self.filename,self.ruta,self.sesi[i],UserAgent,Temp,reconect,Threads)
                            if self.UrlFaill or self.NotRangeSupport:
                                continue
                        elif self.NetError:
                            return

                        elif self.abort:
                            RemoveReg.append(self.filename)
                            DownloadActiva.remove(self.filename)
                            break

                        elif self.StateFile.split()[1] == 'completo':
                            self.signals.startProgresBar.emit(str(100),str(self.MegaEstado),str(),str(self.filename),str(0),str(self.cronometro),str(self.video_stream),str(self.StateFile),self.ruta)
                            DownloadActiva.remove(self.filename)
                            RemoveReg.append(self.filename)
                            break
                        elif abort.get(self.filename,False):
                            RemoveReg.append(self.filename)
                            DownloadActiva.remove(self.filename)
                            break
                except Exception as e:
                    logging.warning(unicode(e))
                    DownloadActiva.remove(self.filename)

            except Exception as e:
                logging.warning(unicode(e))
                DownloadActiva.remove(self.filename)
            finally:
                self.estate = False
                key =  self.filename
                if abort.get(key,False):  abort.pop(key)
                if pausar.get(key,False):  pausar.pop(key)



class PingHilo(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.LOOP = True
        self.signals = Communicate()

    def __del__(self):
        self.wait()
    def kill(self):
        self.LOOP = False
    def run(self):
        global EstadoPing
        while self.LOOP:
            try:
                ping = 0
                rpt = list()
                Int_rpt = list()

                if platform == 'linux2':
                    cmd = 'ping -c 5 8.8.8.8'
                elif platform == 'win32':
                    cmd = 'ping -n 5 8.8.8.8'

                proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
                rpt = proc.stdout.read()
                rpt += proc.stderr.read()
                if platform == 'linux2':
                    rpt = findall('time=([.\d]{2,20}) ms',str(rpt))
                    rpt += findall('tiempo=([.\d]{2,20})ms',str(rpt))
                elif platform == 'win32':
                    rpt = findall('tiempo=([.\d]{2,20})ms',str(rpt))
                    rpt += findall('time=([.\d]{2,20})ms',str(rpt))
                if len(rpt) > 0:
                    for i in rpt:
                        i = float(i)
                        i = int(i)
                        Int_rpt.append(i)
                        ping = sum(Int_rpt)/len(rpt)
                    if ping < 500:
                        EstadoPing = 'estable'
                    else:
                        EstadoPing = 'inestable'
                elif len(rpt) == 0:
                    EstadoPing = 'off'
                    ping = 0
                try:
                    self.signals.setPing.emit(str(ping),EstadoPing)

                except Exception as e:
                    pass
                self.sleep(1)
            except:
                pass

class Hilocrawler(QThread,crawlerYT):
    def __init__(self,url,temp):
        QThread.__init__(self)
        crawlerYT.__init__(self)
        self.signals = Communicate()
        self.url = url
        self.Firewall = False

    def __del__(self):
        self.wait()

    def run(self):
        try:
            crawlerYT.start(self,self.url,GlobalCookie,UserAgent,Temp,GoogleRecaptcha)

            if self.Firewall:
                setCookie = SetCookie(url=self.url ,firewall=True)
                setCookie.start()
                setCookie.wait()
            if self.Name is not str():
                self.signals.crawler.emit(self.Name,self.SerieInfo,self.imagen,self.NumberCapis,self.NextCap,self.Fecha,self.Estado,self.listGenero,self.listaNameCap,self.listaUrl,self.UltimoCap,self.CapMayor)
        except Exception as e:
            logging.warning(unicode(e))


class threadSearch(QThread,crawlerYT):
    def __init__(self,name=None,temp=None):
        QThread.__init__(self)
        self.signals = Communicate()
        self.Temp = temp
        self.name = name
        self.Pool = True
        self.List_Animes_url = list()
        self.List_Animes_img = list()
        self.List_Animes_name = list()
        self.save = 0

    def __del__(self):
        self.wait()

    def enviar(self):
        actual = int()
        while self.Pool:
            actual = len(self.List_Animes_img)
            if actual > self.save:
                self.signals.Search.emit(self.List_Animes_img,self.List_Animes_url,self.List_Animes_name)
                self.save = len(self.List_Animes_img)
                if len(self.List_Animes_img) == len(self.List_Animes_url):
                    break
            sleep(0.5)
    def run(self):
        _t = Thread(target=self.enviar)
        _t.setDaemon(True)
        _t.start()
        if not GoogleRecaptcha:
            crawlerYT.searchAnime(self,anime=self.name,cookie=GlobalCookie,UserAgent=UserAgent,temp=self.Temp,GoogleRecaptcha=False)
        else:
            crawlerYT.searchAnime(self,anime=self.name,cookie=GlobalCookie,UserAgent=UserAgent,temp=self.Temp,GoogleRecaptcha=True)
        sleep(5)
        self.Pool = False
        self.signals.finish.emit()




class SetCookie(QThread):
    def __init__(self,url='http://www.animeyt.tv/',firewall=False):
        QThread.__init__(self)
        self.url = url
        self.state = None
        self.firewall = firewall

    def __del__(self):
        self.wait()

    def saveCookie(self):
        con = connect(path.join(getcwd(),'database','cookie.db'))
        cursor = con.cursor()
        cookieEncode = b64encode(self.cookie)
        if not self.firewall:
            cursor.execute("INSERT INTO AppYT VALUES ({0},'{1}')".format(0,cookieEncode))
        else:
            cursor.execute("UPDATE AppYT set cookie = '{0}' where id=0".format(cookieEncode))
        con.commit()
        cursor.close()
        con.close()

    def loadCookie(self):
        global GlobalCookie
        con = connect(path.join(getcwd(),'database','cookie.db'))
        cursor = con.cursor()
        id = (0,)
        cursor.execute("SELECT * FROM AppYT WHERE id=?", id)

        for x in cursor:
            GlobalCookie = b64decode(x[1])
            self.state = True
            break
        else:
            self.state = False

    def run(self):
        global GlobalCookie,GoogleRecaptcha
        self.sleep(3)
        try:
            if not self.firewall:
                self.loadCookie()
                if not self.state:
                    self.cookie = bypass.get_cookie_string(self.url,user_agent=UserAgent)[0]
                    GlobalCookie = self.cookie
                    self.saveCookie()
            else:
                self.cookie = bypass.get_cookie_string(self.url,user_agent=UserAgent)[0]
                GlobalCookie = self.cookie
                self.saveCookie()
            self.emit(SIGNAL('showAnime'))
        except Exception as e:
            logging.warning(unicode(e))
            if '403 Client Error' in str(e):
                GoogleRecaptcha = True
                # print 'Google Recaptcha Activo'
                return
            sleep(1)
            self.run()


class CreateBaseData(QThread):
    def __init__(self, parent = None):
        self.signals = Communicate()
        QThread.__init__(self, parent)

    def __del__(self):
        self.wait()

    def BaseData1(self):
        try:
            if not path.exists(path.join(getcwd(),'database','BaseTemp.db')):
                con = connect(path.join(getcwd(),'database','BaseTemp.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , filename text UNIQUE , enlace text ,ruta text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            else:
                con = connect(path.join(getcwd(),'database','BaseTemp.db'))
                cursor = con.cursor()
                cursor.execute("SELECT * FROM AppYT")
                cursor.close()
                con.close()
        except Exception as e:
            if path.exists(path.join(getcwd(),'database','BaseTemp.db')):
                remove(path.join(getcwd(),'database','BaseTemp.db'))
                con = connect(path.join(getcwd(),'database','BaseTemp.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , filename text UNIQUE , enlace text , ruta text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            logging.warning(unicode(e))
    def BaseData2(self):
        try:
            if not path.exists(path.join(getcwd(),'database','BaseMiList.db')):
                con = connect(path.join(getcwd(),'database','BaseMiList.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , filename text UNIQUE , enlace text ,rutaIMG text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            else:
                con = connect(path.join(getcwd(),'database','BaseMiList.db'))
                cursor = con.cursor()
                cursor.execute("SELECT * FROM AppYT")
                cursor.close()
                con.close()
        except Exception as e:
            if path.exists(path.join(getcwd(),'database','BaseMiList.db')):
                remove(path.join(getcwd(),'database','BaseMiList.db'))
                con = connect(path.join(getcwd(),'database','BaseMiList.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , filename text UNIQUE , enlace text , rutaIMG text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            logging.warning(unicode(e))
    def BaseData3(self):
        try:
            if not path.exists(path.join(getcwd(),'database','cookie.db')):
                con = connect(path.join(getcwd(),'database','cookie.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , cookie text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            else:
                con = connect(path.join(getcwd(),'database','cookie.db'))
                cursor = con.cursor()
                cursor.execute("SELECT * FROM AppYT")
                cursor.close()
                con.close()
        except Exception as e:
            if path.exists(path.join(getcwd(),'database','cookie.db')):
                remove(path.join(getcwd(),'database','cookie.db'))
                con = connect(path.join(getcwd(),'database','cookie.db'))
                cursor = con.cursor()
                query = 'CREATE TABLE AppYT (id int UNIQUE , cookie text)'
                cursor.execute(query)
                cursor.close()
                con.close()
            logging.warning(unicode(e))


    def run(self):
        self.BaseData3()
        self.BaseData1()
        self.BaseData2()
        self.signals.test.emit()



class OpenFile(QThread):
    def __init__(self,ruta):
        QThread.__init__(self)
        self.rutaSave = ruta
    def __del__(self):
        self.wait()
    def run(self):
        try:
            #nautilus
            if platform == 'linux2':
                cmd = 'dolphin "{0}"'.format(self.rutaSave)
            elif platform == 'win32':
                cmd = 'explorer "{0}"'.format(self.rutaSave)
            Popen(cmd, shell=True)
        except Exception as e:
            logging.warning(unicode(e))
            pass




class AddWorks(QThread):
    def __init__(self,ListFiles,ListUrls,ruta):
        QThread.__init__(self)
        self.ListFiles = ListFiles
        self.ListUrls = ListUrls
        self.ruta = ruta
    def __del__(self):
        self.wait()
    def run(self):
        con = connect(path.join(getcwd(),'database','BaseTemp.db'))
        cursor = con.cursor()
        cursor.execute("SELECT * FROM AppYT")
        ide = 0
        for i,f in enumerate(self.ListFiles):
            while True:
                if cursor.execute("SELECT * FROM AppYT WHERE id = {0}".format(ide)).fetchone() == None:
                    try:
                        filename = b64encode(self.ListFiles[i]+'.mp4')
                        url = urlsafe_b64encode(self.ListUrls[i])
                        ruta = b64encode(self.ruta)
                        cursor.execute("INSERT INTO AppYT VALUES ({0},'{1}','{2}','{3}')".format(ide,filename,url,ruta))
                        ide += 1
                    except Exception as e:
                        logging.warning(unicode(e))
                    break
                ide += 1
        con.commit()
        cursor.close()
        con.close()



class Communicate(QObject):
    startProgresBar = Signal(str,str,str,str,str,str,str,str,str)
    cancelar = Signal(str)
    StartDownloadGrap = Signal()
    AddNewFiles = Signal()
    test = Signal()
    setPing = Signal(str,str)
    crawler = Signal(str,unicode,unicode,int,unicode,unicode,str,unicode,list,list,str,int)
    finish = Signal()
    Search = Signal(list,list,list)

class MultiThreads(QThread):
    def __init__(self,temp):
        QThread.__init__(self)
        self.signals = Communicate()
        self.pool = QThreadPool.globalInstance()
        self.threads = 1
        self.pool.setMaxThreadCount(self.threads)  #cantidad max de descargas simultaneas#
        self.LOOP = True

    def __del__(self):
        self.wait()
    def kill(self):
        self.LOOP = False

    def deletReg(self):
        global RemoveReg
        for filename in RemoveReg:
            filename = b64encode(filename)
            con = connect(path.join(getcwd(),'database','BaseTemp.db'))
            cursor = con.cursor()
            values = (filename,)
            cursor.execute('DELETE FROM AppYT WHERE filename=?',values)
            con.commit()
        cursor.close()
        con.close()
        RemoveReg = list()

    def ShowWorkWait(self):
        con = connect(path.join(getcwd(),'database','BaseTemp.db'))
        cursor = con.cursor()
        cursor.execute("SELECT * FROM AppYT")
        for number,registro in enumerate(cursor):
            filename = b64decode(registro[1])
            ruta = b64decode(registro[3])
            self.signals.AddNewFiles.emit()
            self.signals.startProgresBar.emit(str(0),str(),str(),filename,str(),str(),str(),'wait',ruta)
        cursor.close()
        con.close()

    def run(self):
        global DownloadActiva,abort,pausar
        sleep(1)
        self.ShowWorkWait()
        sleep(10)
        while self.LOOP:
            # while EstadoPing == 'off':
            #     logging.info('Conexion Indisponible..')
            #     sleep(1)

            con = connect(path.join(getcwd(),'database','BaseTemp.db'))
            cursor = con.cursor()
            cursor.execute("SELECT * FROM AppYT")
            for number,registro in enumerate(cursor):
                filename = b64decode(registro[1])
                ruta = b64decode(registro[3])
                url = b64decode(registro[2])
                if str(filename) in DownloadActiva:
                    continue
                elif str(filename) in RemoveReg:
                    self.deletReg()
                    continue

                self.hilo = DownloadHilo(str(url),str(filename),str(ruta),Temp)
                self.hilo.signals.startProgresBar.connect(self.Enviar)
                self.hilo.signals.cancelar.connect(self.cancelar)
                self.hilo.signals.AddNewFiles.connect(self.addFile)
                self.hilo.signals.StartDownloadGrap.connect(self.StartDownloadGrap)
                self.pool.start(self.hilo)
                sleep(0.5)
            else:
                if apagarPC and (self.pool.activeThreadCount() == 0):
                    if platform == 'linux2':
                        cmd = 'sudo shutdown -P'
                    elif platform == 'win32':
                        cmd = 'shutdown /S /F'  #add time 60s
                    Popen(cmd, shell=True)
                    break
                elif self.pool.activeThreadCount() == 0:
                    pausar = dict()
                    abort = dict()
                    DownloadActiva = list()

            cursor.close()
            con.close()
            while self.pool.activeThreadCount() == self.threads:
                if len(RemoveReg)>0:
                    self.deletReg()
                sleep(0.5)
            if len(RemoveReg)>0:
                self.deletReg()
            sleep(0.5)


    def Enviar(self,porcentaje,MegaEstado,rate,filename,restante,cronometro,video_stream,StateFile,ruta):
        self.signals.startProgresBar.emit(str(porcentaje),str(MegaEstado),str(rate),str(filename),str(restante),str(cronometro),str(video_stream),str(StateFile),ruta)
    def addFile(self):
        self.signals.AddNewFiles.emit()
    def cancelar(self,filename):
        self.signals.cancelar.emit(filename)
    def StartDownloadGrap(self):
        self.signals.StartDownloadGrap.emit()


if __name__ == "__main__":
    app = QtGui.QApplication(argv)
    with open('GUI/style.css') as f:
        style = f.read()
    #qdarkstyle.load_stylesheet()
    app.setStyleSheet(style)
    ui = AppYT()
    ui.show()
    exit(app.exec_())
