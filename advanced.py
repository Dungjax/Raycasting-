from pygame import init,display,font,transform,image,gfxdraw,time,fastevent,FINGERDOWN,FINGERMOTION,FINGERUP,mixer,sprite
from pymunk import pygame_util,Space,Body,Circle,Poly,ShapeFilter
from math import sin,cos,tan,radians,sqrt,atan2
from random import randint
from map import MAP,lenght
init()
#screen init
Width=1080
Height=2290
screen=display.set_mode((Width,Height))
options=pygame_util.DrawOptions(screen)
#color
grey=(50,50,50)
red=(255,0,0)
white=(255,255,255)
black=(0,0,0)
green=(0,255,0)
#event
fastevent.init()
joystick_posx,joystick_posy=250,250
shoot_posx,shoot_posy=150,1900
leftfinger_posx,leftfinger_posy=Height/2,Height/2
rightfinger_posx,rightfinger_posy=Height/2,Height/2
rightfingerd_posy=Height/2
tempcamx,tempcamy=0,0
camerax,cameray=0,0
#raycast
Num_ray=200
Fov=radians(180)/3
Ray_step=Fov/Num_ray
Max_depth=10000
Coeff=100000
Scale=1200//Num_ray
LIMIT_X,LIMIT_Y=10000,24000
#sound
shot_sound=mixer.Sound("shot.mp3")
#image
def blit_img_c(name,x,y):
	s=image.load(name).convert()
	s=transform.rotate(s,-90)
	if x!=None or y!=None:
		s=transform.scale(s,(x,y))
	return s
def blit_img_ca(name,x,y):
	s=image.load(name).convert_alpha()
	s=transform.rotate(s,-90)
	if x!=None or y!=None:
		s=transform.scale(s,(x,y))
	return s
def blit_img90(name,x,y):
	s=image.load(name).convert()
	s=transform.rotate(s,-90)
	if x!=None or y!=None:
		s=transform.scale(s,(x,y))
	return s
	
def blit_img(name):
	s=image.load(name).convert()
	return s
bg=blit_img90("bg.png",None,None)
wall1=blit_img90("wall_with_shadow.jpg",None,None)
shot_png=blit_img_ca("cross_hair.png",None,None)
gfxdraw.circle(screen,250,200,20,red)
screen.blit(shot_png,(shoot_posx,shoot_posy))
#font & text
font=font.Font(None,30)
def cre_text(name,x,y):
	t=transform.rotate(font.render(str(name),1,white),-90).convert_alpha()
	screen.blit(t,(x,y))
#time
clock=time.Clock()
#space init
space=Space()
class Enemy_shape(Poly):
	def __init__(self,body,verti,health):
		super().__init__(body,verti)
		self.health=health
class Player:
	def __init__(self):
		super().__init__()
		w=10000
		self.body=Body(w,w*100)
		self.body.position=540,1200
		self.shape=Poly.create_box(self.body,(50,50))
		self.shape.filter=ShapeFilter(1)
		self.shape.collision_type=1
		space.add(self.body,self.shape)
		self.is_shoot=0
		self.shoot_animate=[blit_img_ca(f"s{i}.png",800,690) for i in range(9)]
		self.reload_animate=[blit_img_ca(f"reload{i}.png",800,690) for i in range(17)]
		self.current_state=self.shoot_animate
		self.shoot_index=0
		self.ammo=10
	def update(self,lf_posx,lf_posy,rf_posx,rf_posy,tempy,camy):
		#moving & rotating
		self.body.angle=radians(tempcamy+cameray)/5
		pangle=atan2(lf_posx-joystick_posx,lf_posy-joystick_posx)-radians(90)
		if lf_posy<Height/2:
			self.body.position+=-10*sin(self.body.angle-pangle),10*cos(self.body.angle-pangle)
		#shooting
		
		if rf_posx>=shoot_posx and 					rf_posx<=shoot_posx+200 and rf_posy>=shoot_posy and rf_posy<=shoot_posy+200:
			self.is_shoot=1
		self.current_state=self.shoot_animate if self.ammo>0 else self.reload_animate
		if self.is_shoot==1:
			self.shoot_index+=1 if self.current_state==self.shoot_animate else 0.5
			if self.shoot_index==1:
				shot_sound.play()
				Bullet(self.body.position,self.body.angle)
				self.ammo-=1
			if self.shoot_index>=len(self.current_state):
				self.shoot_index=0
				if rf_posy==Height/2:
					self.is_shoot=0
				if self.ammo<=0:
					self.ammo=10
		#raycast
		start_angle=self.body.angle-Fov/2
		angle=self.body.angle
		x,y=self.body.position
		seg_query=[space.segment_query_first((x,y),(x-Max_depth*sin(start_angle+i*Ray_step),y+Max_depth*cos(start_angle+i*Ray_step)),1,ShapeFilter(1)) for i in range(Num_ray)]
		#sprite first collum
		enemy_fc=0
		for ray in range(Num_ray):
			if seg_query[ray]!=None:
				#depth
				depth=sqrt(abs(seg_query[ray].point.x-x)**2+(seg_query[ray].point.y-y)**2)*cos(angle-start_angle)
				depth_v=abs((seg_query[ray].point.x-x)/sin(start_angle))
				depth_h=abs((seg_query[ray].point.y-y)/cos(start_angle))
				#wall collide_type 
				offset=(seg_query[ray].point.x-50)%100 if depth_v<depth_h else (seg_query[ray].point.y-50)%100
				proj_h=int(Coeff/depth) if Coeff/depth<2500 else 2500
				w1=transform.scale(wall1.subsurface(0,offset,200,1),(proj_h*2,Scale))
				screen.blit(w1,((camerax-tempcamx)*2+(540-proj_h//2-proj_h),490+ray*Scale))  
				
			start_angle+=Ray_step
		#shoot	
		gfxdraw.filled_circle(screen,540,1093,5,green)
		screen.blit(self.current_state[int(self.shoot_index)],(0,1000))
		cre_text(self.ammo,1000,1200)
class Bullet:
	def __init__(self,res_pos,res_angle):
		self.body=Body(1,455)
		self.body.position=res_pos
		self.body.angle=res_angle
		self.body.apply_impulse_at_local_point((0,8000))
		shape=Poly.create_box(self.body,(10,50))
		#shape.collision_type=2
		shape.filter=ShapeFilter(0)
		space.add(self.body,shape)
class Enemy(sprite.Sprite):
	def __init__(self,x,y):
		super().__init__()
		self.body=Body(100,45500)
		self.body.position=x,y
		s=25
		self.shape=Enemy_shape(self.body,((-s,-s),(s,-s),(s,s),(-s,s)),100)
		self.shape.collision_type=3
		space.add(self.body,self.shape)
	def update(self):
		self.body.velocity=0,0#randint(-1000,1000),randint(-1000,1000)
def Tile_wall(x,y):
	w=randint(1,100)
	body=Body(w,w*100,Body.KINEMATIC)
	body.position=x,y
	shape=Poly.create_box(body,(100,100))
	shape.elasticity=0.5
	shape.friction=0.75
	space.add(body,shape)
def Wall(x,y,w,h):
	body=Body(1,100,Body.KINEMATIC)
	body.position=x,y
	shape=Poly.create_box(body,(w,h))
	shape.elasticity=0.5
	shape.friction=0.75
	space.add(body,shape)
for i in range(lenght):
	Tile_wall(MAP[i][0],MAP[i][1])
Wall(LIMIT_X/2,0,LIMIT_X,100)
Wall(LIMIT_X/2,LIMIT_Y,LIMIT_X,100)
Wall(0,LIMIT_Y/2,100,LIMIT_Y)
Wall(LIMIT_X,LIMIT_Y/2,100,LIMIT_Y)
#player
player=Player()
#bullet
#enemy
enemy_group=sprite.Group()
for i in range(100):
	enemy=Enemy(randint(0,100)*100,randint(0,100)*100)
	enemy_group.add(enemy)
def b_c_e(arbiter,space,data):
	space.remove(arbiter.shapes[0],arbiter.shapes[0].body)
	s=arbiter.shapes[1]
	cre_text(s.health,1000,1000)
	s.health-=50
	if s.health<=0:
		space.remove(s,s.body)
	return True	
while 1:
	space.add_collision_handler(2,3).begin=b_c_e
	FPS=clock.get_fps()
	clock.tick()
	screen.blit(bg,(-540,490))
	
	for ev in fastevent.get():
		#down
		if ev.type==FINGERDOWN:
			if ev.y*Height>Height/2:
				rightfingerd_posy=ev.y*Height
		#move
		if ev.type==FINGERDOWN or ev.type==FINGERMOTION:
			#left
			if ev.y*Height<Height/2:
				leftfinger_posx=ev.x*Width
				leftfinger_posy=ev.y*Height
			#right
			if ev.y*Height>Height/2:
				rightfinger_posx=ev.x*Width
				rightfinger_posy=ev.y*Height
				tempcamy=rightfinger_posy-rightfingerd_posy
		
		#up
		if ev.type==FINGERUP:
			if ev.y*Height<Height/2:
				leftfinger_posx,leftfinger_posy=Height/2,Height/2
			if ev.y*Height>Height/2:
				cameray+=tempcamy
				tempcamy=0
				rightfinger_posx,rightfinger_posy=Height/2,Height/2
				rightfingerd_posy=Height/2
	#update
	player.update(leftfinger_posx,leftfinger_posy,rightfinger_posx,rightfinger_posy,tempcamy,cameray)
	enemy_group.update()
	###draw
	cre_text(FPS,1000,600)
	space.step(1/80)
	#space.debug_draw(options)
	display.update()
