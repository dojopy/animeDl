#!/usr/bin/env python
#coding:utf-8

from __future__ import print_function
from concurrent.futures import ThreadPoolExecutor,wait
from requests import get
from os import getenv,getcwd,path,remove,mkdir,system
from time import sleep
from colored import fg, bg, attr
import logging
import requests
import signal
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning


__autor__ = 'Henry Cristofer Vasquez Conde'
__correo__ = 'cristofer_dev.py@hotmail.com'
__version__ = '1.0'


class FreneticDL(object):
	def __init__(self):
		self.UserAgent = ''
		self.contador = 0
		self.part = 0
		self.segmentos = 50
		self.hilos = 3
		self.reconect = 100
		self.kiloByteDescargados = 0
		self.file_size_Megas = 0
		self.MegaEstado = ''
		self.porcentaje = 0
		self.megas_float = 0
		self.rate = 0
		self.restante = 0
		self.scan = True
		self.finish = False
		self.Intervalo = 0
		self.ListIntervalo = []
		self.abort = False
		self.pause = False
		self.StateFile = 'wait'
		self.abort_stream = False
		self.UrlFaill = False
		self.NetError = False
		self.Lista_Pool = []
		self.cookie = ''
		self.startPorcen = 5
		self.new_len = 0
		self.pwd = ''
		self.Intentos_Segmentos = {}
		self.Temp = r'/tmp/'
		self.NotRangeSupport = False
		self.setColor = lambda c,d: '%s%s %s %s'%(fg(0), bg(c),d, attr('reset'))
		self.verde = lambda d: self.setColor(85,d)
		self.rojo = lambda d: self.setColor(202,d)
		self.akua = lambda d: self.setColor(122,d)
		self.config()
		
	def config(self):
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		logging.basicConfig(level=logging.DEBUG, format=' %(levelname)s : %(message)s',)
		#signal.signal(signal.SIGINT, self.change_estate)

	def change_estate(self,signum, frame):
		if not self.pause:
			self.StateFile = self.rojo('pause')
			self.pause = True
		else:
			self.StateFile = self.verde('run')
			self.pause = False
			

	def Concat(self,filename,ruta):
		try:
			if not path.exists(ruta):
				mkdir(ruta)
				logging.info(self.akua('carpeta creada'))

			self.pwd = path.join(ruta,filename)

			with open(self.pwd,"wb") as file:
				for i in range(self.segmentos):
					with open(path.join(self.Temp,filename+str(i+1)), "rb") as p:
						parte  = p.read()
						file.seek(self.part*i)
						file.tell()
						file.write(parte)
					sleep(0.1)

			if path.exists(self.pwd):
				for i in range(self.segmentos):
					remove(path.join(self.Temp,filename+str(i+1)))
		except Exception as e:
			logging.debug(unicode(e))


	# reproducir videos en stream, mientras se descarga.
	def ConcatPlay(self,filename,ruta):
		try:
			with open(path.join(ruta,filename),"wb") as file:
				for i in range(self.segmentos):
					while True:
						while not path.exists(path.join(ruta,filename+str(i+1))):
							sleep(0.3)
						try:
							with open(path.join(ruta,filename+str(i+1)), "rb") as p:
								parte  = p.read()
								if self.part+1 == len(parte):
									file.seek(self.part*i)
									file.tell()
									file.write(parte)
									break
								if self.abort_stream:
									return
								sleep(0.3)
						except Exception as e:
							logging.debug(unicode(e))
		except Exception as e:
			logging.debug(unicode(e))
		finally:
			remove(path.join(ruta,filename))


	def Handler(self,start, end, url, file_temp):
		intentos = self.Intentos_Segmentos[file_temp]
		self.Intentos_Segmentos[file_temp] = intentos + 1

		try:
			t = 0
			self.StateFile = self.verde('run')
			Newstart = start
			if self.abort:
				return
			if path.exists(path.join(self.Temp,file_temp)):
				with open(path.join(self.Temp,file_temp), "rb") as f:
					t = len(f.read())

					if t == self.part+1:	#Completo#
						logging.debug('utilizando segmento..')
						self.kiloByteDescargados += t
						self.contador += 1
						return
					else:	#parcial#
						logging.debug('continuando descarga...')
						Newstart += t

			logging.debug('download part {0}'.format(file_temp))
			cont_seg = 0
			headers = {'Range': 'bytes=%d-%d' %(Newstart, end),'User-Agent':self.UserAgent,'cookie':self.cookie}
			r = get(url, headers=headers,stream=True,verify=False,timeout=20,allow_redirects=True)

			### VALIDANDO DATA ###
			peso = r.headers['content-range']
			peso = int(peso.split('/')[-1])/(1024*1024)
			if not (peso == self.file_size_Megas):
				raise Exception('peso_no_coincide!:{0}/{1}'.format(peso,self.file_size_Megas))


			with open(path.join(self.Temp,file_temp), "ab+") as f:
				f.seek(Newstart)
				f.tell()
				for chunk in r.iter_content(chunk_size=1024):
					if self.abort:
						return
					while self.pause:
						if self.abort:
							return
						sleep(1)
					if chunk:
						self.kiloByteDescargados += len(chunk)
						cont_seg += len(chunk)
						f.write(chunk)

			with open(path.join(self.Temp,file_temp), "rb") as f:
				tm = len(f.read())
				data = f.read()

			if self.part == end:
				with open(path.join(self.Temp,file_temp)) as f:
					data = f.read()

			if tm == self.part+1:
				self.contador += 1
			elif tm == self.new_len:
				self.contador += 1
			else:
				if (tm > self.part+1):
					remove(path.join(self.Temp,file_temp))
					logging.debug('ELIMINANDO SEGMENTO')
				elif (self.new_len > 0) and (tm > self.new_len):
						remove(path.join(self.Temp,file_temp))
						logging.debug('ELIMINANDO SEGMENTO')
				logging.debug( 'Error segmento no coincide %d/%d /%dreboot segmento!%s '%(tm,self.part,self.new_len,file_temp))
				raise Exception('segmento')

		except Exception as e:
			logging.debug(self.Intentos_Segmentos[file_temp])
			logging.debug(unicode(e))
			if u'content-range' in unicode(e) or u'peso_no_coincide' in unicode(e):
				if self.Intentos_Segmentos[file_temp] == 10:
					self.NotRangeSupport = True
					self.UrlFaill = True
					return
			if self.Intentos_Segmentos[file_temp] == self.reconect:
				self.UrlFaill = True
				return
			sleep(5)
			return self.Handler(start, end, url, file_temp)



	def download_file(self, url, filename, folder, cookie, UserAgent, temp, reconect,threads):
		self.Temp = temp
		self.cookie = cookie
		self.UserAgent = UserAgent
		self.filename = filename
		self.enlace = url
		self.reconect = reconect
		self.hilos = threads
		logging.info(url)
		try:
			headers = {
			'User-Agent':UserAgent,
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language':"en-US,en;q=0.5",
			'Accept-Encoding':"gzip, deflate",
			'Range': 'bytes=0-10000',
			'cookie':self.cookie}
			self.UrlFaill = False
			self.NetError = False
			r = get(url,verify=False,headers=headers,timeout=20,allow_redirects=True)
			file_size = r.headers['content-range']
			file_size = int(file_size.split('/')[-1])
			self.pesoTotalKB = file_size
			self.file_size_Megas = file_size/(1024*1024)
			TipoContenido = r.content
			logging.info('Tamaño: %s M'%(self.file_size_Megas))

			if 'html' in TipoContenido:
				self.UrlFaill = True
				return
			elif not self.file_size_Megas:
				self.UrlFaill = True
				return				
			elif self.file_size_Megas > 300:	# stream de archivos grandes
				self.startPorcen = 2

			self.segmentos = self.file_size_Megas/2

		except Exception as e:
			logging.info(self.rojo('Error: '+ unicode(e)))
			if u'Connection aborted' in unicode(e):
				self.NetError = True
				return
			elif u'content-range' in unicode(e):
				self.NotRangeSupport = True
				return
			else:
				self.UrlFaill = True
				return

		self.part = int(file_size) / (int(self.segmentos))
		logging.debug('tamano por parte: %s M'%(self.part/(1024*1024)))

		exe = ThreadPoolExecutor(1)
		exe.submit(self.EstadoDownload)

		self.Lista_Pool2 = []
		with ThreadPoolExecutor(max_workers=self.hilos) as executor:
			for i in range(self.segmentos):
				while executor._work_queue.qsize() >= self.hilos:
					sleep(0.3)
				if self.abort:
					self.scan = False
					for i in range(self.segmentos):
						try:
							remove(path.join(self.Temp,self.filename+str(i+1)))
						except:
							pass
				start = self.part * i
				end = start + self.part
				self.new_len = 0
				if i == (self.segmentos-1):
					self.new_len = file_size-start
					end  = file_size

				self.Intentos_Segmentos[self.filename+str(i+1)] = 0
				pool = executor.submit(self.Handler,start, end, url, self.filename+str(i+1))
				self.Lista_Pool.append(pool)

		wait(self.Lista_Pool)
		if self.contador == self.segmentos:
			self.finish = True
			self.StateFile = self.verde('completo')
			self.porcentaje = '100'

			unir = ThreadPoolExecutor(1)
			self.Lista_Pool2.append(unir.submit(self.Concat,self.filename,folder))
			wait(self.Lista_Pool2)
			self.scan = False
			sleep(1)
			logging.info(self.akua('%s Descargado con Exito!'%(self.filename)))
			logging.info(self.akua('salida:  %s'%(self.pwd)))

		elif self.NotRangeSupport:
			self.UrlFaill = True
		else:
			self.UrlFaill = True
			self.scan = False


	def EstadoDownload(self):
		self.freezeRate = ''
		self.freezeRestante = ''

		while self.scan:
			try:
				if not self.finish:
					megas = float(self.kiloByteDescargados)/(1024.0*1024.0)
					self.megas_float = format(megas,'.2f')
					self.MegaEstado = '{0}/{1} MB'.format(self.megas_float,self.file_size_Megas)
					self.porcentaje = (float(self.kiloByteDescargados)/float(self.pesoTotalKB))*100.0
					self.barra = self.porcentaje
					self.porcentaje = format(self.porcentaje,'.2f')
				else:
					self.porcentaje = '100' #evitar 99.9
					self.barra = 100
					self.megas_float = str(self.file_size_Megas)

				if len(self.ListIntervalo) == 10:
					self.ListIntervalo.pop(0)

				newBytes = (float(self.kiloByteDescargados) - self.Intervalo)/1024.0
				self.Intervalo = self.kiloByteDescargados
				self.ListIntervalo.append(newBytes)
				self.rate = sum(self.ListIntervalo)

				INF = '%s/%sM \t  Porcentaje: %s'%(self.megas_float,self.file_size_Megas,self.porcentaje)
				self.barra = '[%s%s]'%('#' * int(self.barra), ' '*(100-int(self.barra)))
				self.barra = self.verde(self.barra)
				
				if self.rate > 0:
					self.restante = int((self.pesoTotalKB-self.kiloByteDescargados)/1024/self.rate)
					if self.rate < 1024:
						self.rate = format(self.rate,'.2f')+' kiB/s'
						self.freezeRate = self.rate
					else:
						self.rate = self.rate/1024.0
						self.rate = format(self.rate,'.2f')+ ' MiB/s'
						self.freezeRate = self.rate

					if self.restante > 0:
						if len(str(self.restante))>2:
							self.restante = self.restante/60
							self.restante = str(self.restante) + ' m'
							self.freezeRestante = self.restante
						else:
							self.restante = str(self.restante) + ' s'
							self.freezeRestante = self.restante
					else:
						self.restante = self.freezeRestante
				else:
					self.restante = self.freezeRestante
					self.rate = self.freezeRate

				
				sector1 = ' Enlace: {0} \n Archivo: {1} \n Tamaño: {2}M \n Conexiones(Threads): {3} \n Estado: {4} \t *Presiona Ctrl+C para pausar o continuar. \n {5} \n '.format(
					self.enlace,self.filename,self.file_size_Megas,self.hilos,self.StateFile, self.barra)
				sector2 = '{0} \t Restante: {1}     \t Tasa: {2}'.format(INF,self.restante,self.rate)
				sector2 = self.akua(sector2)

				#system('clear')
				#print(sector1, sector2)
				
			except Exception as e:
				logging.debug(unicode(e))
				self.restante = self.freezeRestante
				self.rate = self.freezeRate
			
			if self.abort:
				return
			while self.pause:
				#system('clear')
				#print(sector1, sector2)
				if self.abort:
					return
				sleep(1)
			sleep(0.1)



if __name__ == '__main__':
	agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url", help="Enlace de descarga", type=str, required=False)
	parser.add_argument("-o", "--output", help="nombre del archivo salida", type=str, default='',  required=False)	
	parser.add_argument("-f", "--folder", help="carpeta de salida", type=str, default='./',  required=False)	
	parser.add_argument("-t", "--threads", help="Nº de conexiones paralelas", type=int, default=3, required=False)
	parser.add_argument("-a", "--agent", help="User-Agent del dispositivo", type=str, default=agent,required=False)
	parser.add_argument("-c", "--cookie", help="datos de sesion", type=str, default='', required=False)
	parser.add_argument("-tm", "--tmp", help="carpeta temporal", type=str, default=r'/tmp/', required=False)
	parser.add_argument("-r", "--reconect", help="Nº de reintentos por conexion", type=int, default=100, required=False)
	parser.add_argument("-v", "--version", help="version del modulo", action="store_true")
	args = parser.parse_args()
	color = lambda d: '%s%s %s %s'%(fg(0), bg(85),d, attr('reset'))

	if args.version:
		print(color(__version__))
	elif args.url:
		if not args.output:
			args.output = args.url.split('/')[-1]
		FreneticDL().download_file(args.url, args.output, args.folder, args.cookie, args.agent, args.tmp,args.reconect, args.threads)
	else:
		print(color('FreneticDL V.%s \n -u   Ingrese una URL.  \n -h   Informacion y posibles parametros'%(__version__)))
