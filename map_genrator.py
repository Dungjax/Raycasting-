#tap to topleft screen to exit
import pygame
pygame.init()
screen=pygame.display.set_mode((0,0))
black=(0,0,0)
red=(255,0,0)
white=(255,255,255)
font=pygame.font.Font(None,30)
file=open("map.py","w")
class MAP:
	def __init__(self):
		self.arrays=[]
		self.arrays_lenght=0
	def get_pos(self,x,y):
		if [x,y] not in self.arrays:
			self.arrays.append([x,y])
			self.arrays_lenght+=1
	def blit(self):
		for i0 in range(len(self.arrays)):
			pygame.draw.rect(screen,(red),(self.arrays[i0][0]/10,self.arrays[i0][1]/10,10,10))
cmap=MAP()
run=True
xc,yc=None,None
while run:
	screen.fill(black)
	for i in pygame.event.get():
		if i.type==pygame.FINGERDOWN or i.type==pygame.FINGERMOTION:
			xc=i.x*1080
			yc=i.y*2290
			cmap.get_pos(xc//10*100,yc//10*100)
		if i.type==pygame.FINGERUP:
			if xc<100 and yc<100:
				run=False
	cmap.blit()
	pygame.display.update()
	if run==False:
		file.write(f"MAP={cmap.arrays}\nlenght={cmap.arrays_lenght}")
	
