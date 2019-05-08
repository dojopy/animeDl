#coding:utf-8
from re import sub,compile
from os import listdir

class inspector(object):
	def start(self,ruta,totalCapAnime=None):
		self.DIR = ruta
		pat = compile("\.(avi|AVI|MP4|mp4|FLV|flv|mpg|MPG|mkv|MKV)$")

		listvideos = list()
		self.totalCapAnime = int(totalCapAnime)
		total = list()
		#for root,dirs,names in os.walk(self.DIR)
		for name in listdir(self.DIR):
			cd = pat.sub('',name)
			total.append(cd)

		lis = list()
		for name in listdir(self.DIR):
			if pat.search(name):
				listvideos.append(name)
				cadena = pat.sub('', name)
				# print cadena
				Newcadena = sub("\D", ".", cadena).split('.')
				# print Newcadena
				for i in Newcadena:
					if i.isdigit():
						lis.append(int(i))

		lis = list(set(lis))
		self.newLis = list()
		self.listActualizar = list()

		for i  in lis:
			if i <= self.totalCapAnime:
				self.newLis.append(i)
		for i in range(self.totalCapAnime):
			index = i+1
			if index in self.newLis:
				pass
			else:
				self.listActualizar.append(index)

		self.dir_anime = ruta.split('/')[-1]
		# print 'carpeta local:',self.dir_anime
		# print 'capitulos actuales en web', self.totalCapAnime
		# print 'capitulos en carpeta',self.newLis
		# print 'se actualizar los cap.', self.listActualizar

				
#os.remove(os.path.join(root,name))
# os.path.isdir(names)
		
# inspector().start('/home/tenxuts/Animes/bungou_stray_dogs_2nd_season',10)