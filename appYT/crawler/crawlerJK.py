import requests
import re
from bs4 import BeautifulSoup


class crawlerJK():
	def start(self,url):
		# url = self.url

		header1 = {'Host':'jkanime.net',
		        'User-Agent':' Mozilla/5.0 (X11; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0',
		        'Accept-Language':"en-US,en;q=0.5",
		        'Accept-Encoding':"gzip, deflate",
		        'Referer':"http://jkanime.net/touken-ranbu-hanamaru/1/",
		        'Cookie':"__cfduid=d43e9b86db01be9dcdf70c1d8abd538061475454583; cf_clearance=69410903592c67d3f7071ecfd59a90047d4b4e8b-1475454677-604800; ci_session=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%224886f95892a5450456ee8a2607e11c43%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22190.237.183.113%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A66%3A%22Mozilla%2F5.0+%28X11%3B+Linux+i686%3B+rv%3A45.0%29+Gecko%2F20100101+Firefox%2F45.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1475464259%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7Df20adb4266199780b113ff211d720f00; ccoo=9; ccoo_ex=1475492709"}
		header2 = {'Host':'cdn.jkanime.net',
		        'User-Agent':' Mozilla/5.0 (X11; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0',
		        'Accept-Language':"en-US,en;q=0.5",
		        'Accept-Encoding':"gzip, deflate",
		        'Referer':"http://jkanime.net/touken-ranbu-hanamaru/1/",
		        'Cookie':"__cfduid=d43e9b86db01be9dcdf70c1d8abd538061475454583; cf_clearance=69410903592c67d3f7071ecfd59a90047d4b4e8b-1475454677-604800; ci_session=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%224886f95892a5450456ee8a2607e11c43%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22190.237.183.113%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A66%3A%22Mozilla%2F5.0+%28X11%3B+Linux+i686%3B+rv%3A45.0%29+Gecko%2F20100101+Firefox%2F45.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1475464259%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7Df20adb4266199780b113ff211d720f00; ccoo=9; ccoo_ex=1475492709"}
		        
		r1  = requests.get(url,headers=header1,timeout=120,verify=False).content
		print r1

		urlIMG = re.findall('src="(http://cdn.jkanime.net/assets/images/animes/image/[0-9A-Za-z-.]{5,})" alt=',r1)[0]
		print urlIMG
		
		r2  = requests.get(urlIMG,headers=header2,timeout=120,verify=False).content
		with open('imagen.jpg','wb') as f:
		    f.write(r2)
		self.imagen = 'imagen.jpg'

		infoAnime = r1.find('<p> ')
		_infoAnime = r1.find(' </p>')
		self.info = r1[infoAnime+3:_infoAnime]
		

		html = BeautifulSoup(r1)
		Listinfo = html.find_all('div',{'class':'separedescrip'})
		numbercap = html.find_all('div',{'class':'listnavi'})
		title = html.find_all('div',{'class':'sinopsis_title title21'})


		for i in  Listinfo[1] :
			i = str(i)
			if 'Tipo' in i:
				self.tipo = re.findall('px;">(.+)</span>',i)[0]
				# print tipo
			elif 'Genero'in i:
				self.genero = re.findall('href="http://jkanime.net/genero/(\w{3,20})/',i)
				# print genero
			elif 'Episodios' in i:
				self.Episodios = re.findall('5px;">(\w+)</span>',i)[0]
				# print Episodios
			elif 'Duracion' in i:
				self.Duracion = re.findall('5px;">(.+)</span>',i)[0]
				# print Duracion

			elif 'Emitido'in i:
				self.Emitido = re.findall('5px;">(.+)</span>',i)[0]
				# print Emitido
			elif 'Estado' in i:
				self.Estado = re.findall('5px;">(.+)</span>',i)[0]
				# print Estado

		for enum,i in enumerate(numbercap):
			i = list(i)
			fin = str(i[-2])
			CapiActuales = re.findall('>([-\s\d.]+)</a',fin)
			self.CapiActuales = max(CapiActuales).split('-')[1]

		if 'sinopsis_title' in str(title):
			self.title = re.findall('>(.+)<',str(title))[0]
		else:
			self.title = 'AppJKanime'

	def extraer_url(self,url):
		header1 = {'Host':'jkanime.net',
		        'User-Agent':' Mozilla/5.0 (X11; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0',
		        'Accept-Language':"en-US,en;q=0.5",
		        'Accept-Encoding':"gzip, deflate",
		        'Referer':"http://jkanime.net/touken-ranbu-hanamaru/1/",
		        'Cookie':"__cfduid=d43e9b86db01be9dcdf70c1d8abd538061475454583; cf_clearance=69410903592c67d3f7071ecfd59a90047d4b4e8b-1475454677-604800; ci_session=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%224886f95892a5450456ee8a2607e11c43%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A15%3A%22190.237.183.113%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A66%3A%22Mozilla%2F5.0+%28X11%3B+Linux+i686%3B+rv%3A45.0%29+Gecko%2F20100101+Firefox%2F45.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1475464259%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7Df20adb4266199780b113ff211d720f00; ccoo=9; ccoo_ex=1475492709"}
		r1  = requests.get(url,headers=header1,timeout=120,verify=False).content
		parser = BeautifulSoup(r1)
		html = parser.find_all('iframe',{'class':'player_conte'})

		self.listaServer = list()
		for  i in html:
			url = re.findall('src="(.+)/"',str(i))[0]
			url = url.replace('jk.php?u=','')
			self.listaServer.append(url)


# crawlerJK().start('http://jkanime.net/kuma-miko-specials/')
# crawlerJK().extraer_url('http://jkanime.net/one-punch-man/2/')