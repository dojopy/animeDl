#!/usr/bin/env python
#coding: utf-8
from requests import get,post
from re import findall,sub,compile
from bs4 import BeautifulSoup
from time import sleep
from concurrent.futures import ThreadPoolExecutor,wait
from os import path,getenv
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import logging
logging.basicConfig(level=logging.INFO, format=' %(levelname)s : %(message)s :%(module)s:  line:%(lineno)d',)
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class crawlerYT(object):
	def __init__(self):
		self.Name = ''
		self.SerieInfo = ''
		self.imagen = ''
		self.NumberCapis = ''
		self.NextCap = ''
		self.Fecha = ''
		self.Estado = ''
		self.listGenero = []
		self.listaUrl = []
		self.listaNameCap = []
		self.UltimoCap = ''
		self.CapMayor = 0
		self.UserAgent = ''
		self.sesi = ['']


	def start(self,url,cookie='', UserAgent='',temp='',GoogleRecaptcha=False):
		self.Temp = temp
		self.UserAgent = UserAgent

		if '/ver/' in url:
			self.url_cap = url
			if 'sub' in url:
				self.Number_Cap_download = findall(r'-([\d]{1,5})-sub-espanol',url)[0]
				deleSub = '-'+str(self.Number_Cap_download)+'-sub-espanol'
				self.url_info = url.replace('/ver','')
				self.url_info = self.url_info.replace(deleSub,'')
		else:
			self.url_info = url

		self.header = {'User-Agent':self.UserAgent,
						'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Language':"en-US,en;q=0.5",
						'Accept-Encoding':"gzip, deflate",
						'Referer':'http://www.animeyt.tv/',
						'Cookie':cookie}
		try:
			if True:	#googlerecopachra
				r = get(self.url_info,headers=self.header,timeout=15).content
			else:
				pass
				# r = self.SimpleBypassCloudflare(self.url_info,self.UserAgent,1)

			if r.find('5 seconds') > 0:
				self.Firewall = True
				return
		except Exception as e:
			logging.debug(unicode(e))
			return

		listCapis = []
		html = BeautifulSoup(r,'html.parser')
		ListInfo = html.find_all('div',{'class':'serie-header'})
		ListFecha = html.find_all('div', {'class' : 'serie-header__fecha'})
		ListCap = html.find_all('div',{'class':'serie-capitulos__list__item'})
		ListName = html.find_all('div',{'class':'serie-header__data'})
		for i in ListName:
			self.Name = i.find('h1', {'class' : 'serie-header__title'}).getText().lower().encode('ascii', 'ignore')
			self.Name = self.Name.lower().replace('\n','').replace('sub espaol','').strip(' \t\n\r')
			self.Name = self.ParserName(self.Name)
			self.Name = self.Name
			Temporada = sub("\D", '', self.Name)

		for i in ListFecha:
			if 'Fecha' in str(i):
				self.Fecha = i.getText().replace('\n','').strip(' \t\n\r').split(':')[-1].encode('ascii', 'ignore')



		for i in  ListCap:
			url = str(i.find('a').get('href')).lower()
			self.listaUrl.append(url)
			nameCap = i.find('a').getText().encode('ascii', 'ignore')
			nameCap = nameCap.lower().replace('sub espaol','').replace('\n','').strip(' \t\n\r')
			self.listaNameCap.append(nameCap)

			new = str(sub("\D", '', nameCap))
			new = new.replace(' ','')
			new = new.replace('\n','')

			if Temporada:
				if new[0:len(Temporada)] == Temporada:
					new = new[len(Temporada):]
					if new != '':
						listCapis.append(int(new))
					else:
						listCapis.append(None)
			else:
				if new != '':
					listCapis.append(int(new))
				else:
					listCapis.append(None)

		self.NumberCapis = len(self.listaUrl)
		self.listaNameCap = map(self.ParserName,self.listaNameCap)

		self.UltimoCap = self.listaNameCap[0].strip(' \t\n\r').lower()

		try:
			self.CapMayor =  max(listCapis)
			if not (self.CapMayor-1 in listCapis) and self.NumberCapis != 1:
				listCapis.remove(self.CapMayor)
				self.CapMayor =  max(listCapis)
		except Exception as e:
			logging.debug(unicode(e))


		for i in ListInfo:
			try:
				LinkImg = i.find('img', {'class' : 'serie-header__img'}).get('src')
				r2  = get(LinkImg,headers=self.header,timeout=15).content
				name = LinkImg.split('/')[-1].encode('ascii', 'ignore')
				self.imagen = path.join(self.Temp,name)
				with open(self.imagen,'wb') as f:
				    f.write(r2)
			except:
				self.imagen = ''

			self.SerieInfo = i.find('p', {'class' : 'serie-description'}).getText().strip(' \t\n\r').encode('ascii', 'ignore')

			GeneroInfo = i.find('ul',{'class':'serie-header__genero'})
			if GeneroInfo:
				for i in GeneroInfo:
					if i.find('a') != -1 and i.find('a') != None:
						Genero = i.find('a').getText().replace('\n','')
						self.listGenero.append(Genero)


		if str(ListInfo).find('Emisión') > 0 or str(ListInfo).find('emision') > 0:
			self.Estado = 'Emision'
			ListEmision = html.find_all('div', {'class' : 'emision'})
			for i in ListEmision:
				self.NextCap = i.getText().replace('\n','').strip(' \t\n\r').encode('ascii', 'ignore')

		else:
			self.Estado = 'Finalizado'

		self.listGenero = ' '.join(self.listGenero).encode('ascii', 'ignore')


	def dailymotion(self,url,agente):
		self.header = { 'User-Agent':agente,
						'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Language':"en-US,en;q=0.5",
						'Accept-Encoding':"gzip, deflate"
						}

		self.header2 = { 'User-Agent':agente,
						'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Language':"en-US,en;q=0.5",
						'Accept-Encoding':"gzip, deflate",
						'Range': 'bytes=0-1000'
						}

		try:
			session = requests.Session()
			html = session.get(url,headers=self.header,timeout=10)
			sess = html.cookies.get_dict()
			qualitys = ['1280x720','848x480']
			patrones = lambda quality:	r'dailymotion.com\\/cdn\\/H264-%s\\/video\\/([\w\-\.\?\=]+)\"\}'%(quality)
			for q in qualitys:
				ur = patrones(q)
				server = findall(ur,html.content)[0]
				server = 'http://www.dailymotion.com/cdn/H264-{0}/video/{1}'.format(q,server)
				res = session.get(server,headers=self.header2,timeout=10,allow_redirects=True)
				self.sesi.append(res.request.headers['cookie'])
				self.listaUrl.append(res.url)
			#print '\n \n',self.listaUrl,'\n',self.sesi

		except Exception as e:
			self.NetError = True
			logging.debug(unicode(e))
			return

	def ExtraerUrlVideo(self,url,cookie='',UserAgent='',GoogleRecaptcha=False):
		self.UserAgent = UserAgent
		header = {'User-Agent':self.UserAgent,
						'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Language':"en-US,en;q=0.5",
						'Accept-Encoding':"gzip, deflate",
						'Referer':'http://www.animeyt.tv/',
						'Cookie':cookie}
		try:
			html = get(url,headers=header,timeout=10).content
		except Exception as e:
			self.NetError = True
			logging.debug(unicode(e))
			return

		self.EnlacesDl = set()
		patron = r'https?://www.dailymotion.com/embed/video/([\w]+)\?autoPlay=1'

		server = findall(patron,html)[0]
		server = 'http://www.dailymotion.com/embed/video/{0}?autoPlay=0'.format(server)
		self.dailymotion(server,self.UserAgent)



	def searchAnime(self,anime=None,cookie='',UserAgent='',temp='',GoogleRecaptcha=False):
		self.Temp = temp
		self.Lista_Pool= []
		self.UserAgent = UserAgent
		header = {'User-Agent':self.UserAgent,
				'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Language':"en-US,en;q=0.5",
				'Accept-Encoding':"gzip, deflate",
				'Referer':'http://www.animeyt.tv/',
				'Cookie':cookie}

		if anime != None:
			url = 'http://www.animeyt.tv/busqueda?terminos=%s'%(anime)
		else:
			url = 'http://www.animeyt.tv/emision'

		try:
			s = get(url,headers=header).content
		except Exception as e:
			logging.debug(unicode(e))
			return
		html = BeautifulSoup(s,'html.parser')
		ListAnimes = html.find_all('a',{'class':'anime__img-container'})
		self.List_Animes_url = []
		self.List_Animes_name = []
		self.urlIMG = []
		self.List_Animes_img = []

		for x in ListAnimes:
			self.List_Animes_url.append(str(x.get('href')))
			self.urlIMG.append(str(x.find('img').get('src')))
			x = x.find('img').get('alt').encode('ascii', 'ignore')
			self.List_Animes_name.append(x)

		for url in self.urlIMG:
			with ThreadPoolExecutor(max_workers=10) as executor:
				pool = executor.submit(self.GetImages,url,header,self.Temp)
				self.Lista_Pool.append(pool)

		wait(self.Lista_Pool)

	def GetImages(self,url,header,temp):
		try:
			name = url.split('/')[-1]
			img = get(url,headers=header).content
			ruta = path.join(temp,name)

			with open(ruta,'wb') as data:
				data.write(img)
			self.List_Animes_img.append(ruta)
		except Exception as e:
			logging.debug(unicode(e))


	def ParserName(self,filename):
		pat = compile(r"[\= \$ \' \" \# \% \* \: < > \? \/ \\\ \| \. \+ \- \_ \~ \{ \} \& \[ \] \`]+")
		return pat.sub(' ',filename)



# crawlerYT().start('http://www.animeyt.tv/dragon-ball-super',"__cfduid=d9878a0507db264f0381fe13f43125c741508422476; cf_clearance=b29d05ae49e9a62c10b709996252a44719a5cada-1508675907-3600",'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36')
# crawlerYT().searchAnime(anime=None,cookie=str(),UserAgent=str())
#crawlerYT().ExtraerUrlVideo('http://www.animeyt.tv/ver/dragon-ball-super-123-sub-espanol',UserAgent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36')
# metodo = crawlerYT().ParserName
# print crawlerYT().SimpleBypassCloudflare('http://s2.animeyt.tv/naruto.php?id=3164&file=6.5.mp4',2)
