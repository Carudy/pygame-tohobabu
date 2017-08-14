# -*- coding: utf-8 -*-
import pygame
import math
import random
from pygame.locals import *
from sys import exit
import os
import copy
#********************************** global vars **************************
pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.mixer.set_num_channels(25)
_width,_height=1280,740
_size=(_width,_height)
pygame.display.init()
#screen = pygame.display.set_mode(_size,0,32)
screen = pygame.display.set_mode(_size,FULLSCREEN,32)
pygame.display.set_caption("game")
p_img=lambda x,y,z:pygame.transform.scale(pygame.image.load(x).convert_alpha(),(y,z))
j_img=lambda x,y,z:pygame.transform.scale(pygame.image.load(x).convert(),(y,z))
v_dist =lambda x1,y1,x2,y2:(x1-x2)**2+(y1-y2)**2

# display "loading..."
loading=j_img('pics/loading.jpg',_width,_height)
screen.blit(loading,(0,0))
pygame.display.update()

left,right,top,bottom=25,795,20,720		# stage board

# pre load / set
stage=pygame.Surface((770,700))
stage.fill((30,30,30))
diag_board=p_img("pics/diag_board.png",475,110)
bg=p_img("pics/cover0.png",_width,_height)
info=p_img("pics/info0.png",425,700)
menu=p_img("pics/tit.png",770,700)

Paused				=		1
esc_cd				=		0
item_line			=		170
que_max				=		3000
gener_max			=		2
danmu_card			=		range(que_max)	# all danmu generators
card_h,card_t		=		0,0
danmu_geners		=		[]				# all danmus
eners				=		[]				# all enermies
talking 			=		0
animes				=		[]				# all animes
#********************************** defs *************************************************
def re_xy(x,y):
	x=left if x<left else right if x>right else x
	y=top if y<top else bottom-5 if y>bottom-5 else y
	return (x,y)

def ye_xy(x,y):
	return x<=right and x>=left and y>=top and y<=bottom

def vec_mo(x,y,xx,yy):
	return math.sqrt((xx-x)**2+(yy-y)**2)

def vec_1(x,y,xx,yy):
	l=vec_mo(x,y,xx,yy)
	return ((xx-x)/l,(yy-y)/l)
	
def danmu_ins(x):
	global card_t,danmu_card,que_max
	card_t=(card_t+1)%que_max
	danmu_card[card_t]=x
	if danmu_card[card_t].pred==0:
		danmu_card[card_t].pre()

def rota(x,xx,yy):
	x=abs(x*180.0/math.pi)
	#print x
	if xx<=0 and yy<=0:
		return 180-x
	elif xx<=0 and yy>=0:
		return x+180
	elif xx>=0 and yy>=0:
		return 360-x
	else:
		return x

def anime_ins(id,x,y):
	global animes
	n_ani=copy.copy(Ani.an[id])
	n_ani._x,n_ani._y=x,y
	animes.append(n_ani)

def ener_ins(x):
	global eners
	x.pre()
	eners.append(x)

def  power_up(x,y):
	return (x>=64 and y<64)or(x>=32 and y<32)or(x>=8 and y<8)or(x>=127 and y<127)

def sui(x):
	return random.choice(range(x<<1))-x

def cal_dist(x,y,z):
	if z.x0==z.x1:
		if y>z.y0:
			return vec_mo(x,y,z.x0,z.y0)
		elif y<z.y1:
			return vec_mo(x,y,z.x1,z.y1)
		else:
			return abs(x-z.x0)
	else:
		if x<z.x0:
			return vec_mo(x,y,z.x0,z.y0)
		elif x>z.x1:
			return vec_mo(x,y,z.x1,z.y1)
		else:
			return abs(y-z.y0)

#********************************** classes ******************************
class danmu_0():
	def __init__(self,img,x,y,w,h):
		self._x,self._y,self._w,self._h=x,y,w,h
		self.zha,self.pred=1,0
		self.r=min(w,h)*0.5

class danmu_ziji0():
	def __init__(self,x,y,w,h):
		self._x,self._y,self._w,self._h,self.speed=x,y-5,w,h,0.8
		self.r=min(w,h)*0.5
		self.img=p_img("pics/punch.png",w,h)
		self.friend=1
		self.zha=1
		self.harm=1+(3 if Ziji.power==127 else 2 if Ziji.power>63 else 1)
		
	def run(self,timep):
		self._y-=timep*self.speed
		return self.zha==1 and self._y>top

class danmu_ziji2():
	def __init__(self,x,y,w,h):
		self._x,self._y,self.speed=x,y-5,0.3
		self._w,self._h=w,h
		self.r=min(w,h)*0.5
		self.img=p_img("pics/buu.png",w,h)
		self.friend=1
		self.zha=1
		self.harm=4+(3 if Ziji.power==127 else 1 if Ziji.power>63 else 0)
		
	def run(self,timep):
		self._y-=timep*self.speed
		return self.zha==1 and self._y>top

class danmu_quan():
	def __init__(self,x,y):
		self._x,self._y,self.r=x,y-5,22
		self._w,self._h=44,48
		self.img=p_img("pics/quan2.png",self._w,self._h)
		self.friend=3
		self.zha=1
		self.harm=45+(15 if Ziji.power==127 else 8 if Ziji.power>63 else 0)
		self.alt=0
		
	def run(self,timep):
		self.alt+=timep
		self._y-=timep*(0.1 if self.alt<1000 else 0.7)
		return self.zha==1 and self._y>top

class danmu_ziji1():
	def __init__(self,x,y,w,h,d):
		global Ziji
		self._x,self._y,self.speed=x,y-5,1
		self._w,self._h=w,h
		self.r=min(w,h)*0.5
		self.img=p_img("pics/scis.png",w,h)
		self.friend=1
		self.d=d
		self.harm=0.8+(1 if Ziji.power==127 else 0.5 if Ziji.power>63 else 0)
		self.zha=1
		
	def run(self,timep):
		global eners
		if len(eners)>0:
			idx=min(self.d,len(eners)-1)
			nx,ny=eners[idx]._x,eners[idx]._y
			dx,dy=vec_1(self._x,self._y,nx,ny)
			self._x+=dx*timep*self.speed
			self._y+=dy*timep*self.speed
		else:
			self._y-=self.speed*6
		return self.zha==1 and ye_xy(self._x,self._y)

class danmu_coin():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.2
		self.r,self._w,self._h=8,8,8
		self.img=p_img("pics/coin.png",self.r<<1,self.r<<1)
		self.friend=2
		self.fen=100
		self.zz=0
		self.life=0
		self.power=0
		self.boom=0
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[19].play()
			return 0
		if self.zz==0:
			self._y+=timep*self.speed
			return self._y<bottom
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_moto():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.2
		self.r,self._w,self._h=15,15,15
		self.img=p_img("pics/slut17.png",self.r<<1,self.r<<1)
		self.friend=2
		self.fen=10
		self.zz=0
		self.life=0
		self.power=0
		self.boom=0
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[19].play()
			return 0
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_power():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.2
		self.r,self._w,self._h=7,17,21
		self.img=p_img("pics/power.png",self._w,self._h)
		self.friend=2
		self.fen=10
		self.zz=0
		self.life=0
		self.power=1
		self.boom=0
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[19].play()
			return 0
		if self.zz==0:
			self._y+=timep*self.speed
			return self._y<bottom
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_power2():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.15
		self.r,self._w,self._h=7,17,21
		self.img=p_img("pics/power2.png",self._w,self._h)
		self.friend=2
		self.fen=20
		self.zz=0
		self.life=0
		self.power=8
		self.boom=0
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[19].play()
			return 0
		if self.zz==0:
			self._y+=timep*self.speed
			return self._y<bottom
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_heart():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.2
		self.r,self._w,self._h=7,21,21
		self.img=p_img("pics/heart.png",self._w,self._h)
		self.friend=2
		self.fen=50
		self.zz=0
		self.life=1
		self.power=0
		self.boom=0
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[8].play()
			return 0
		if self.zz==0:
			self._y+=timep*self.speed
			return self._y<bottom
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_cir():
	def __init__(self,img,x,y,w,h,rr,speed):
		self._x,self._y,self.speed=x+rr,y,0.2
		self._w,self._h=w,h
		self.r=min(w,h)*0.5
		self.img=p_img(img,w,h)
		self.rr=rr
		self.t0=0
		self.friend=4
		self.speed=speed
		self.ox,self.oy=x,y
		self.pd=0

	def run(self,timep):
		self.t0+=timep*self.speed*0.001
		self._x=self.ox+math.cos(self.t0)*self.rr
		self._y=self.oy+math.sin(self.t0)*self.rr
		return 1

class danmu_boo():
	def __init__(self,x,y):
		self._x,self._y,self.speed=x,y,0.2
		self.r,self._w,self._h=10,36,36
		self.img=p_img("pics/boo.png",self._w,self._h)
		self.friend=2
		self.fen=30
		self.zz=0
		self.life=0
		self.power=0
		self.boom=1
		self.eaten=0
		
	def run(self,timep):
		global Koe
		if self.eaten:
			Koe.sd[11].play()
			return 0
		if self.zz==0:
			self._y+=timep*self.speed
			return self._y<bottom
		global Ziji
		if Ziji.dying>0:
			return 0
		dx,dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
		self._x+=dx*timep
		self._y+=dy*timep
		return ye_xy(self._x,self._y)

class danmu_sniper0():	# line danmu
	def __init__(self,img_src,x,y,dx,dy,w,h,rot):
		self.r=min(w,h)*0.5
		self._w,self._h=w,h
		self.img = p_img(img_src,w,h)
		self.img = pygame.transform.rotate(self.img,rot)
		self._x,self._y,self.dx,self.dy=x,y,dx,dy
		self.pd=0
		self.friend=0

	def run(self,timep):
		self._x,self._y=self._x+self.dx,self._y+self.dy
		return ye_xy(self._x,self._y)

	def set_friend(self,x):
		self.friend=x

class danmu_dio():
	def __init__(self,img,x,y):
		self._x,self._y = x,y
		self._w,self._h=26,43
		self.img = p_img(img,self._w,self._h)
		self.r=min(self._w,self._h)*0.5
		self.alt=0
		self.cd=2500
		self.dx,self.dy=0,0
		self.friend=4
		self.speed=1
		self.y_cd=0
		self.pd=0
		self.r_cd=3000

	def run(self,timep):
		global Ziji,Koe,Ziji,danmu_geners,eners
		self.alt+=timep
		self.cd-=min(self.cd,timep)
		self.r_cd-=min(self.r_cd,timep)
		self._x,self._y=re_xy(self._x,self._y)
		if self.r_cd<=0:
			danmu_ins(danmu_randan("pics/slut5.png",self._x,self._y,9,0.0,1,18,18))
			self.r_cd=3000 if self.alt<30000 else 2000 if self.alt<50000 else 1600
		if self.y_cd>0 and Ziji.muteki<=0:
			self.y_cd-=timep
			nx=self._x+self.dx*timep
			ny=self._y+self.dy*timep
			nnx,nny=re_xy(nx,ny)
			if nnx==nx and nny==ny:
				anime_ins(4,self._x-self._w*0.5,self._y-self._h*0.5)
				self._x,self._y=nx,ny
		if self.cd<=0 and Ziji.muteki<=0:
			Koe.sd[17].play()
			self.y_cd=1300.0 if self.alt<60000 else 1100.0
			self.dx,self.dy=vec_1(self._x,self._y,Ziji._x,Ziji._y)
			self.speed=(vec_mo(self._x,self._y,Ziji._x,Ziji._y)*1.3)/(self.y_cd)
			self.speed=max(self.speed,0.5 if self.alt<60000 else 0.6)
			self.dx*=self.speed
			self.dy*=self.speed
			self.cd=2000 if self.alt<60000 else 1800
		return len(eners)>0

class danmu_line():
	def __init__(self,img,x0,y0,x1,y1,w,h,r,dx,dy):
		self.r,self.x0,self.y0,self.x1,self.y1=r,x0,y0,x1,y1
		self._w,self._h=w,h
		self.img=p_img(img,w,h)
		self._x=(self.x0+self.x1)*0.5
		self._y=(self.y0+self.y1)*0.5
		self.dx,self.dy=dx,dy
		self.friend=0
		self.pd=1

	def run(self,timep):
		self.x0+=self.dx
		self.x1+=self.dx
		self.y0+=self.dy
		self.y1+=self.dy
		self._x+=self.dx
		self._y+=self.dy
		return (ye_xy(self.x0,self.y0) or ye_xy(self.x1,self.y1))
		

###########################################
###########################################
############# danmu_card_father############
###########################################
###########################################
class danmu_gener():
	def __init__(self,img,x,y,n,d,speed,w,h):
		self.img,self._x,self._y,self.tot,self.d= img,x,y,n,d
		self.speed=speed
		self.now=0
		self.w,self.h=w,h
		self.pred=0

class danmu_circle(danmu_gener):
	def pre(self):
		self.cd=0

	def run(self,timep,lim):
		global danmu_geners
		self.cd-=min(self.cd,timep)
		re=0
		while self.now<self.tot and re<lim and self.cd<=0:
			self.cd=self.d[1]
			self.now+=1
			re+=1
			danmu_geners.append(danmu_cir(self.img,self._x,self._y,self.w,self.h,self.d[0],self.speed))
		return re

class danmu_fsniper(danmu_gener):
	def pre(self):
		self.cd=0

	def run(self,timep,lim):
		global danmu_geners
		re=0
		self.cd-=timep
		while re<lim and self.now<self.tot and self.cd<=0:
			self.cd=self.d[1]
			mx,my=Ziji._x+sui(self.d[0]),Ziji._y+sui(self.d[0])
			vc=vec_mo(self._x,self._y,mx,my)+0.001
			dx,dy=(mx-self._x)*self.speed/vc,(my-self._y)*self.speed/vc
			danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,0))
			re+=1
			self.now+=1
		return re

class danmu_dsniper(danmu_gener):
	def pre(self):
		self.cd=0

	def run(self,timep,lim):
		global danmu_geners
		re=0
		self.cd-=timep
		while re<lim and self.now<self.tot and self.cd<=0:
			self.cd=self.d[1]
			mx,my=self._x+sui(self.d[0]),800+sui(self.d[0])
			vc=vec_mo(self._x,self._y,mx,my)+0.001
			dx,dy=(mx-self._x)*self.speed/vc,(my-self._y)*self.speed/vc
			danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,0))
			re+=1
			self.now+=1
		return re

class danmu_zhen2(danmu_gener):
	def pre(self):
		self.cd=0
		self.tot=999
	
	def run(self,timep,lim):
		global eners
		if len(eners)<=0:
			self.tot=0
			return 0
		self.cd-=timep
		re=0
		while re<lim and self.now<self.tot and self.cd<=0:
			self.cd=1000
			self.now+=1
			re+=1
			danmu_geners.append(danmu_line(self.img,self._x,self._y,self._x+200,self._y,200,20,2,self.d,0))
		return re

class danmu_zhen3(danmu_gener):
	def pre(self):
		self.cd=0
		self.tot=self.d[1]
	
	def run(self,timep,lim):
		global eners
		if len(eners)<=0:
			self.tot=0
			return 0
		self.cd-=timep
		re=0
		while re<lim and self.now<self.tot and self.cd<=0:
			self.cd=self.d[2]
			self.now+=1
			re+=1
			danmu_geners.append(danmu_line(self.img,self._x+(200 if self.d[1]>100 and self.now&1 else 0),self._y,self._x,self._y-200,20,200,0.5,0,self.d[0]))
		return re

class danmu_randan(danmu_gener):
	def pre(self):
		pass

	def run(self,timep,lim):
		global danmu_geners
		re=0
		while re<lim and self.now<self.tot:
			theta=random.choice(range(360))*math.pi/180.0
			dx,dy=math.cos(theta)*self.speed,math.sin(theta)*self.speed
			danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,theta))
			re+=1
			self.now+=1
		return re

class danmu_yeqiu(danmu_gener):
	def pre(self):
		self.pred=1
		self.alt=0
		self.ma=100

	def run(self,timep,lim):
		global danmu_geners,Ziji,Koe
		self.alt+=timep
		re=0
		if self.alt>=self.ma and self.now<self.tot:
			self.alt=0
			self.now+=1
			self.ma=300+random.choice(range(120))
			Koe.sd[4].play()
			rdx=Ziji._x+random.choice(range(80))-40
			rdy=Ziji._y+random.choice(range(80))-20
			danmu_geners.append(danmu_quan(rdx,rdy))
			re+=1	
		return re

class danmu_becoin(danmu_gener):
	def pre(self):
		self.pred=1

	def run(self,timep,lim):
		global danmu_geners
		re=0
		while self.now<self.tot and re<lim:
			danmu_geners.append(danmu_moto(self.d[self.now][0],self.d[self.now][1]))
			re+=1
			self.now+=1
		return re

class danmu_zhen(danmu_gener):
	def pre(self):
		self.pred=1
		self.ny=self.d[0]
		self.tot=6

	def run(self,timep,lim):
		global danmu_geners
		nx,w,h,dx,dy=26,20,12,2,0
		re=0
		while self.now<self.tot and re<lim:
			re+=2
			self.now+=1
			self.ny+=self.d[1]
			danmu_geners.append(danmu_sniper0('pics/slut6.png',nx,self.ny,dx,dy,w,h,0))
			self.ny+=self.d[1]
			danmu_geners.append(danmu_sniper0('pics/slut6.png',nx+768,self.ny,-dx,dy,w,h,180))
		return re

class danmu_sniper1(danmu_gener): # generate snipers
	def pre(self):
		global Ziji
		self.theta=math.atan((Ziji._y-self._y)*1.0/(Ziji._x-self._x+0.001))
		self.drt=-1 if self._x>Ziji._x else 1	
		self.t1=self.theta
		self.pred=1
		self.rot=rota(self.theta,Ziji._x-self._x,Ziji._y-self._y)
		self.tt=0

	def run(self,timep,lim):
		global danmu_geners
		re=0
		if self.now==0:
			if self.tot&1==1:	
				dx=self.speed*math.cos(self.theta)*self.drt
				dy=self.speed*math.sin(self.theta)*self.drt
				danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,self.rot))
				re+=1
				self.now=1
				self.tot-=1
			else:
				self.d*=0.5
			if re>=lim:
				return re
			self.tot>>=1
		while self.now<=self.tot and re<lim:
			self.theta+=self.d
			self.t1-=self.d
			self.tt+=self.d*180.0/math.pi
			dx=self.speed*math.cos(self.theta)*self.drt
			dy=self.speed*math.sin(self.theta)*self.drt
			danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,self.rot-self.tt))
			dx=self.speed*math.cos(self.t1)*self.drt
			dy=self.speed*math.sin(self.t1)*self.drt
			danmu_geners.append(danmu_sniper0(self.img,self._x,self._y,dx,dy,self.w,self.h,self.rot+self.tt))
			re+=2
			self.now+=1
		return re
		

#********************************** **** *************************************************
class Sound:
	def __init__(self):
		n=100
		self.sd=[]
		src='sound/sd_'
		for i in range(n):
			if os.path.exists(src+str(i)+'.wav'):
				now=pygame.mixer.Sound(src+str(i)+'.wav')
				now.set_volume(.1)
				self.sd.append(now)
			else:
				break
		self.sd[5].set_volume(.3)
		self.sd[20].set_volume(.3)
		self.sd[19].set_volume(.05)
		self.sd[21].set_volume(.05)
		self.sd[22].set_volume(.2)
		self.sd[16].set_volume(.3)

class Music:
	playing =	0
	musics	=	[]
	tra 	=	0
	bgm		=	pygame.mixer.music
	def __init__(self):
		src='music/m_'
		for i in range(100):
			if os.path.exists(src+str(i)+'.mid'):
				self.musics.append(src+str(i)+'.mid')
			else:
				break

	def change(self,x):
		self.bgm.stop()
		self.tra=x
		self.bgm.load(self.musics[x])
		#self.bgm.set_volume(.75)
		self.bgm.play(-1 if x!=5 else 0)
		self.playing	=	1

	def play(self):
		self.playing	=	1
		self.bgm.play()

	def check(self):
		if self.tra!=5 and self.playing>0 and self.bgm.get_pos()<=0:
			self.bgm.play()

	def pause(self):
		if self.playing==1:
			self.playing=0
			self.bgm.pause()
		else:
			self.playing=1
			self.bgm.unpause()

class ziji():
	def __init__(self):
		self._w=27
		self._h=55
		self.img=p_img("pics/zhujue.png",self._w,self._h)
		self.mu=p_img("pics/zhu_mu.png",self._w,self._h)
		self.center=p_img("pics/point.png",16,16)
		self.refresh()

	def refresh(self):
		self._x=410
		self._y=680
		self.z_cd=0
		self.m_cd=0
		self.dying=0
		self.fen=0
		self.power=0
		self.xi=45
		self.weapon=0
		self.swap_cd=0
		self.wp2_cd=0
		self.life=10
		self.boom=3
		self.muteki=1000
		self.slow=0
		self.speed=0.083
		self._w=27
		self._h=55
		self.x_cd=0
		self.ca=0
		self.booming=0
		self.boom_type=0

	def weapon_go(self):
		if self.power<8:
			return
		if self.weapon==1:
			if  self.wp2_cd>0:
				return
			else:
				self.wp2_cd=300
		if self.power<32:
			if self.weapon==0:
				danmu_geners.append(danmu_ziji1(self._x,self._y,8,10,0))
			else:
				danmu_geners.append(danmu_ziji2(self._x,self._y,10,10))
			return
		if self.power<64:
			if self.weapon==0:
				danmu_geners.append(danmu_ziji1(self._x-6,self._y,8,10,0))
				danmu_geners.append(danmu_ziji1(self._x+6,self._y,8,10,1))
			else:
				danmu_geners.append(danmu_ziji2(self._x+18,self._y,10,10))
				danmu_geners.append(danmu_ziji2(self._x-18,self._y,10,10))
			return
		if self.power<127:
			if self.weapon==0:
				danmu_geners.append(danmu_ziji1(self._x-9,self._y-2,8,10,0))
				danmu_geners.append(danmu_ziji1(self._x+9,self._y-2,8,10,1))
				danmu_geners.append(danmu_ziji1(self._x,self._y+2,8,10,2))
			else:
				danmu_geners.append(danmu_ziji2(self._x+18,self._y-6,10,10))
				danmu_geners.append(danmu_ziji2(self._x-18,self._y-6,10,10))
				danmu_geners.append(danmu_ziji2(self._x,self._y+6,10,10))
			return
		if self.weapon==0:
			danmu_geners.append(danmu_ziji1(self._x-9,self._y-2,8,10,0))
			danmu_geners.append(danmu_ziji1(self._x-9,self._y+2,8,10,1))
			danmu_geners.append(danmu_ziji1(self._x+9,self._y-2,8,10,2))
			danmu_geners.append(danmu_ziji1(self._x+9,self._y+2,8,10,3))
		else:
			danmu_geners.append(danmu_ziji2(self._x-25,self._y-8,10,10))
			danmu_geners.append(danmu_ziji2(self._x-18,self._y+8,10,10))
			danmu_geners.append(danmu_ziji2(self._x+25,self._y-8,10,10))
			danmu_geners.append(danmu_ziji2(self._x+18,self._y+8,10,10))

	def run(self,timep):
		# move
		global danmu_geners,Koe,eners
		self.life=min(self.life,10)
		self.boom=min(self.boom,10)
		self.power=min(self.power,127)
		self.muteki-=min(timep,self.muteki)
		self.swap_cd-=min(timep,self.swap_cd)
		self.dying-=min(timep,self.dying)
		self.wp2_cd-=min(timep,self.wp2_cd)
		self.x_cd-=min(timep,self.x_cd)
		self.booming-=min(timep,self.booming)
		if self.booming>0:
			if self.boom_type==1:
				tod=[]
				for i in filter(lambda x:x.friend==0,danmu_geners):
					tod.append((i._x,i._y))
				danmu_geners=filter(lambda x:x.friend!=0,danmu_geners)
				danmu_ins(danmu_becoin(0,0,0,len(tod),tod,0,0,0))
			else:
				pass
		else:
			if self.xi>=1000:
				self.xi-=1000
			if self.speed<0.05:
				self.speed+=0.06 if self.boom_type==1 else 0.04
		if self.muteki>0:
			self.m_cd=(self.m_cd+timep)%200
		if self.dying>0:
			return
		self.slow=2.5 if keyp[K_LSHIFT] else 5
		dx=(1 if keyp[K_RIGHT] else -1 if keyp[K_LEFT] else 0)
		dy=(1 if keyp[K_DOWN] else -1 if keyp[K_UP] else 0)
		delta=self.speed*timep*self.slow*(1 if (dx==0 or dy==0) else 0.71)
		self._x,self._y=re_xy(self._x+dx*delta,self._y+dy*delta)
		
		# shoot
		if self.swap_cd<=0 and keyp[K_c]:
			self.weapon^=1
			self.swap_cd=150
		self.z_cd-=min(timep,self.z_cd) if self.z_cd>0 else 0
		if(self.z_cd<=0 and keyp[K_z] and self.booming<=0):
			self.z_cd=170
			danmu_geners.append(danmu_ziji0(self._x,self._y-10,24,24))
			Koe.sd[21].play()
			self.weapon_go()

		# boom
		if self.boom>0 and self.x_cd<=0 and keyp[K_x]:
			self.x_cd=1000
			self.boom-=1
			anime_ins(1,25,20)
			if self.slow<=3:
				self.booming=1500 if self.power<64 else 1800 if self.booming<127 else 2000
				self.muteki=3000
				Koe.sd[7].play()
				self.boom_type=1
				anime_ins(2,self._x-25,self._y-25)
				self.xi+=1000
				self.speed-=0.06
				map(lambda x:x.get_harm(14),eners)
			else:
				self.speed-=0.04
				self.booming=2000
				self.muteki=4000
				self.boom_type=2
				nq=5 if self.power<32 else 7 if self.power<80 else 9
				nq+=1 if self.power==127 else 0
				danmu_ins(danmu_yeqiu(0,self._x,self._y,nq,0,0,0,0))

	def kill_boss(self):
		self.booming=1000
		self.xi+=1000
		self.muteki=1000

	def miss(self):
		global Koe,animes,anis,Paused,screen,Diag,Bgm,danmu_geners
		Koe.sd[27].play()
		self.life-=1
		self.power-=min(22,self.power)
		if self.life<=0:
			Paused=1
			screen.blit(menu,(25,20))
			screen.blit(Diag.dead1,(420,240))
			screen.blit(Diag.dead2,(460,283))
			Bgm.change(5)
			return
		danmu_geners.append(danmu_power2(self._x+10,self._y-220))
		danmu_geners.append(danmu_power2(self._x-20,self._y-200))
		self.boom=3
		self.muteki=3500
		self.dying=800
		anime_ins(0,self._x-self._w/2,self._y-self._h/2)
		self._x,self._y=410,680

class diji():
	def __init__(self,img,x,y,life,d,w=0,h=0):
		global Lihui
		self.img,self._x,self._y,self.life,self.d=img,x,y,life,d
		self.h_cd=0
		if w==0:
			self._w=Lihui._w
			self._h=Lihui._h
		else:
			self._w=w
			self._h=h
		self.r=min(self._w,self._h)*0.5


class diji_0(diji):
	def pre(self):
		self.cd=1500
		self.dx=0.4*self.d
		self.dy=-0.1
		self.h_cd=0

	def get_harm(self,x):
		if(self.h_cd>0):
			return
		self.life-=x
		self.img+=1000
		self.h_cd=20

	def run(self,timep):
		if self.life<=0:
			if Ziji.power<127 and random.choice(range(100))<(20 if Ziji.power>=31 else 35):
				danmu_geners.append(danmu_power(self._x,self._y))
			else:
				danmu_geners.append(danmu_coin(self._x,self._y))
			return 0
		if self.img>=1000:
			self.h_cd-=min(self.h_cd,timep)
			if self.h_cd<=0:
				self.img-=1000
		if self.cd<=0:
			self.cd=3000
			Koe.sd[22].play()
			if random.choice(range(100))<50:
				danmu_ins(danmu_randan("pics/slut1.png",self._x,self._y,5,0.25,1.5,20,20))
			else:	
				danmu_ins(danmu_sniper1("pics/slut1.png",self._x,self._y,3,0.2,1.5,20,20))
		else:
			self.cd-=timep
		#self.dx+=timep/1000.0
		self._x+=self.dx
		self._y+=self.dy
		return ye_xy(self._x,self._y)

class diji_1(diji):
	def pre(self):
		self.dx=0.05 if self.d==0 else 0.8*self.d
		if self.d==2:
			self.dx*=0.6
		self.dy=0
		self.h_cd=0
		self.cd=200

	def get_harm(self,x):
		if(self.h_cd>0):
			return
		self.life-=x
		if self.life<=0:
			self.died()
		self.img+=1000
		self.h_cd=20

	def died(self):
		global danmu_geners
		if self.d<2:
			danmu_geners.append(danmu_power2(self._x,self._y))
		else:
			danmu_geners.append(danmu_coin(self._x,self._y))
		if self.d==0:
			for i in range(10):
				danmu_geners.append(danmu_coin(self._x+random.choice(range(60))-30,self._y+random.choice(range(60))-30))
		return 0

	def run(self,timep):
		global Koe
		if self.img>=1000:
			self.h_cd-=min(self.h_cd,timep)
			if self.h_cd<=0:
				self.img-=1000
		self._x+=self.dx
		self.cd-=timep
		if self.cd<=0:
			Koe.sd[22].play()
			self.cd=500 if self.d==0 else 1000
			if self.d<2 or self._x>700 or self._x<20:
				self.dx*=-1
			danmu_ins(danmu_sniper1("pics/slut10.png",self._x,self._y,17,0.3,1.5,20,20))
		return self.life>0

# Zhong Ling
class diji_2(diji):
	def pre(self):
		global Diag
		self.card_n=3
		self.alt=0
		self.dx=0.4
		self.dy=0.2
		self.cd=100
		self.h_cd=3000
		self.m_cd=2000
		self.i_cd=0
		self.cc=0
		self.mlife=self.life
		self.zh=0
		self.jpt=60000
		self.fy=0
		Diag.carn=u'【红晕紫霞】'

	def get_harm(self,x):
		global Koe,Story,Diag
		if(self.h_cd>0):
			return
		self.life-=max(1,x-self.fy)
		if self.life<=0 or self.alt>self.jpt:
			self.card_n-=1
			self.mlife=200 if self.card_n==2 else 420
			self.jpt=60000 if self.card_n==2 else 90000
			self.fy=2 if self.card_n==1 else 0
			self.life=self.mlife
			if self.card_n<=0:
				self.died()
			else:
				Diag.carn=u'【钟灵毓秀】' if self.card_n==2 else u'【闪电貂】'
				Story.clo=Story.clo0[:]
				self.h_cd+=4000
				Koe.sd[5].play()
				self.cd=1500
				self.alt=0
		self.img+=1000
		self.h_cd+=50
		self.i_cd=100

	def died(self):
		global danmu_geners,Koe
		Koe.sd[7].play()
		danmu_geners.append(danmu_power2(self._x+5,self._y-5))
		danmu_geners.append(danmu_power2(self._x-5,self._y+5))
		for i in range(20):
			danmu_geners.append(danmu_coin(self._x+sui(120),self._y+sui(100)))
		return 0
	
	def run(self,timep):
		global Koe,talking,Story,danmu_geners
		if talking:
			return 1
		self.alt+=timep
		if self.alt>=self.jpt:
			self.get_harm(0)
		if self.alt>30000:
			self.fy=0
		self.i_cd-=min(self.h_cd,timep)
		self.h_cd-=min(self.h_cd,timep)
		self.m_cd-=min(self.m_cd,timep)
		if self.i_cd<=0 and self.img>=1000:
			self.img-=1000
		Story.p=(self.life+0.01)/self.mlife
		Story.djs=max(0,int((self.jpt-self.alt)/1000))
		if self.img>=1000 and self.h_cd<=0:
			self.img-=1000
		if self.m_cd<=0:
			if self.cc&1:
				self.dx*=-1
			else:
				self.dy*=-1
			self.cc^=1
			self.m_cd=2000
		self._x+=self.dx
		self._y+=self.dy
		self.cd-=timep
		if self.cd<=0:
			if self.card_n==3:
				Koe.sd[23].play()
				self.cd=2200
				danmu_ins(danmu_fsniper("pics/slut2.png",self._x,self._y,13,(80,120),3,25,25))
				danmu_ins(danmu_randan("pics/slut13.png",self._x+sui(50),self._y+sui(50),9,0,1.5,20,20))
			elif self.card_n==2:
				danmu_ins(danmu_fsniper("pics/slut2.png",self._x,self._y,15,(80,120),3,25,25))
				danmu_ins(danmu_randan("pics/slut13.png",self._x+sui(20),self._y+sui(20),7,0,1.2,20,20))
				self.cd=1900
				Koe.sd[23].play()
			else:
				Koe.sd[23].play()
				if sui(50)<0:
					danmu_ins(danmu_randan("pics/slut2.png",self._x,self._y,13,0,1,20,20))
				else:
					danmu_ins(danmu_randan("pics/slut13.png",self._x,self._y,13,0,1,20,20))
				self.cd=1600
				if self.zh==0:
					self.zh=1
					danmu_geners.append(danmu_dio('pics/slut3.png',self._x+5,self._y+5))
		return self.card_n>0

# Wan Qing
class diji_3(diji):
	def pre(self):
		global Diag
		self.card_n=4
		self.alt=0
		self.dx,self.dy=0,0
		self.cd,self.cd2=1000,0
		self.h_cd,self.m_cd,self.i_cd=3000,3000,0
		self.cc=1
		self.mlife=self.life
		self.jpt=45000
		self.fy=0
		self.f1,self.f2=0,0
		self.hana=0
		Diag.carn=u'【寒光长剑】'

	def get_harm(self,x):
		global Koe,Story,danmu_geners,Diag
		if(self.h_cd>0):
			return
		self.life-=max(1,x-self.fy)
		if self.life<=0 or self.alt>self.jpt:
			self.card_n-=1
			self.mlife=350 if self.card_n==3 else 550
			self.jpt=60000 if self.card_n==3 else 45000 if self.card_n==2 else 90000
			self.fy=3 if self.card_n==1 else 1
			self.life=self.mlife
			if self.card_n<=0:
				self.died()
			else:
				if self.card_n==1:
					danmu_geners=filter(lambda x:x.friend!=0 and x.friend!=4,danmu_geners)
				Diag.carn=u'【剧毒暗箭】' if self.card_n==3 else u'【幽谷佳人】' if self.card_n==2 else u'【婉兮清扬】'
				Story.clo=Story.clo0[:]
				self.h_cd+=4000
				Koe.sd[5].play()
				self.cd=2000
				self.alt=0
				self.cd2=3000
				if self.card_n<=2:
					self._x=400
		self.img+=1000
		self.h_cd+=50
		self.i_cd=100

	def died(self):
		global danmu_geners,Koe
		Koe.sd[7].play()
		danmu_geners.append(danmu_power2(self._x+5,self._y-5))
		danmu_geners.append(danmu_power2(self._x-5,self._y+5))
		danmu_geners.append(danmu_power2(self._x,self._y))
		for i in range(20):
			danmu_geners.append(danmu_coin(self._x+sui(120),self._y+sui(100)))
		return 0

	def run(self,timep):
		global Koe,talking,Story,danmu_geners,Ziji
		if talking:
			return 1
		self.alt+=timep
		if self.alt>=self.jpt:
			self.get_harm(0)
		if self.alt>30000:
			self.fy=0
		self.i_cd-=min(self.h_cd,timep)
		self.h_cd-=min(self.h_cd,timep)
		self.m_cd-=min(self.m_cd,timep)
		self.hana-=min(self.hana,timep)
		self.cd-=min(self.cd,timep)
		self.cd2-=min(self.cd2,timep)
		if self.i_cd<=0 and self.img>=1000:
			self.img-=1000
		Story.p=(self.life+0.01)/self.mlife
		Story.djs=max(0,int((self.jpt-self.alt)/1000))
		if self.img>=1000 and self.h_cd<=0:
			self.img-=1000
		if self.m_cd<=0:
			self.dx=2
			self.cc=0-self.cc
			self.m_cd=2000 if self.card_n==4 else 5000 if self.card_n==3 else 8000
		if self.card_n>2 and self.dx!=0:
			self._x+=self.dx*self.cc*timep
			if self.hana<=0:
				anime_ins(5,self._x+25*self.cc,self._y-45)
				self.hana=30
			self.dx-=min(self.dx,0.005*timep)
		if self.cd<=0 and Ziji.booming<=0:
			if self.card_n==4:
				Koe.sd[23].play()
				self.cd=2000
				danmu_ins(danmu_fsniper("pics/slut8.png",self._x,self._y,25,(150,100),2.5,20,20))
			elif self.card_n==3:
				Koe.sd[24].play()
				self.cd=450
				dd=(-20 if self.alt<30000 else 50,120 if self.alt<30000 else 65)
				danmu_ins(danmu_zhen("pics/slut6.png",0,0,0,dd,0,0,0))
				if self.cd2<=0:
					self.cd2=2500 if self.alt<30000 else 2200
					danmu_ins(danmu_fsniper("pics/slut5.png",self._x,self._y,17,(200,100),2,20,20))
			elif self.card_n==2:
				self.cd=5000
				if self.alt>3000:
					danmu_ins(danmu_dsniper("pics/slut16.png",300,30,20,(400,300),0.8,20,20))
					danmu_ins(danmu_dsniper("pics/slut16.png",500,30,20,(400,300),0.8,20,20))
					danmu_ins(danmu_dsniper("pics/slut16.png",700,30,20,(400,300),0.8,20,20))
					danmu_ins(danmu_dsniper("pics/slut16.png",100,30,20,(400,300),0.8,20,20))
				if self.f1==0:
					self.f1=1
					danmu_ins(danmu_circle("pics/slut9.png",400,350,12,(100,500),1,18,18))
					danmu_ins(danmu_circle("pics/slut9.png",400,350,12,(240,500),-1,18,18))
					danmu_ins(danmu_circle("pics/slut9.png",400,350,12,(360,500),1,18,18))
			else:
				self.cd=5000
				sx=Ziji._x-20
				danmu_ins(danmu_dsniper("pics/slut16.png",200,self._y-180,33,(400,300),0.6,20,20))
				danmu_ins(danmu_dsniper("pics/slut16.png",600,self._y-180,33,(400,300),0.6,20,20))
				danmu_ins(danmu_zhen3("pics/slut12.png",sx,25,0,(6,5,400),0,0,0))
				danmu_ins(danmu_zhen3("pics/slut12.png",sx+120,25,0,(6,5,400),0,0,0))
				if self.f2==0:
					self.f2=1
					for i in range(8):
						sx=-150 if i&1 else 770
						vd=2 if i&1 else -2
						danmu_ins(danmu_zhen2("pics/slut11.png",sx,10+i*90,0,vd,0,0,0))
					danmu_ins(danmu_zhen3("pics/slut12.png",40,25,0,(1,999,2850),0,0,0))
					danmu_ins(danmu_zhen3("pics/slut12.png",280,25,0,(1,999,2850),0,0,0))
					danmu_ins(danmu_zhen3("pics/slut12.png",520,25,0,(1,999,2850),0,0,0))
					danmu_ins(danmu_zhen3("pics/slut12.png",770,25,0,(1,999,2850),0,0,0))
		return self.card_n>0

class diji_4(diji):
	def pre(self):
		self.cd=1500
		self.dx=0.5*self.d
		self.dy=-0.1
		self.h_cd=0

	def get_harm(self,x):
		if(self.h_cd>0):
			return
		self.life-=x
		if self.life<=0:
			if Ziji.power<127 and random.choice(range(100))<(20 if Ziji.power>=31 else 35):
				danmu_geners.append(danmu_power(self._x,self._y))
			else:
				danmu_geners.append(danmu_coin(self._x,self._y))
			return 0
		self.img+=1000
		self.h_cd=20

	def run(self,timep):	
		if self.img>=1000:
			self.h_cd-=min(self.h_cd,timep)
			if self.h_cd<=0:
				self.img-=1000
		if self.cd<=0:
			self.cd=3000
			Koe.sd[22].play()
			if random.choice(range(100))<30:
				danmu_ins(danmu_randan("pics/slut1.png",self._x,self._y,9,0,1,20,20))
			else:	
				danmu_ins(danmu_fsniper("pics/slut10.png",self._x,self._y,5,(200,100),1.5,25,25))
		else:
			self.cd-=timep
		#self.dx+=timep/1000.0
		self._x+=self.dx
		self._y+=self.dy
		return self.life>0 and ye_xy(self._x,self._y)
		
class diji_5(diji):
	def pre(self):
		self.cd=1500
		self.dx=0
		self.dy=0.6
		self.h_cd=0

	def get_harm(self,x):
		if(self.h_cd>0):
			return
		self.life-=x
		if self.life<=0:
			danmu_geners.append(danmu_power2(self._x,self._y))
			danmu_geners.append(danmu_coin(self._x,self._y))
			return 0
		self.img+=1000
		self.h_cd=20

	def run(self,timep):	
		if self.img>=1000:
			self.h_cd-=min(self.h_cd,timep)
			if self.h_cd<=0:
				self.img-=1000
		if self.cd<=0:
			self.cd=200
			Koe.sd[22].play()
			danmu_ins(danmu_sniper1("pics/slut14.png",self._x,self._y,3,0,3,25,25))
		else:
			self.cd-=timep
		#self.dx+=timep/1000.0
		self._x+=self.dx
		self._y+=self.dy
		return self.life>0 and ye_xy(self._x,self._y)

class diji_stone(diji):
	def pre(self):
		self.cd=1500
		self.dx=0
		self.dy=0
		self.h_cd=0

	def get_harm(self,x):
		global Ziji,danmu_geners
		if(self.h_cd>0):
			return
		self.life-=x
		if self.life<=0:
			Koe.sd[26].play()
			Ziji.fen+=10000 if Ziji.booming<=0 else 100
			if self.d!=1:
				danmu_geners.append(danmu_heart(self._x,self._y))
				danmu_ins(danmu_randan("pics/slut15.png",self._x,self._y,11+sui(5),0,4,20,20))
				danmu_ins(danmu_dsniper("pics/slut15.png",self._x,self._y,15,(400,10),3,30+sui(10),30+sui(10)))
			else:
				danmu_geners.append(danmu_power(self._x,self._y))
				danmu_ins(danmu_randan("pics/slut15.png",self._x,self._y,7+sui(5),0,4,20,20))
				danmu_ins(danmu_dsniper("pics/slut15.png",self._x,self._y,8,(400,10),3,30+sui(10),30+sui(10)))
			return 0
		self.img+=1000
		self.h_cd=20

	def run(self,timep):
		if self.img>=1000:
			self.h_cd-=min(self.h_cd,timep)
			if self.h_cd<=0:
				self.img-=1000
		self.dy+=timep*0.003 if self.d==1 else 0.002
		self._y+=self.dy
		return ye_xy(self._x,self._y) and self.life>0
		
###############################################
class monji():
	def __init__(self):
		self.font=pygame.font.Font("font/hanyi.ttf", 23)
		self.font2=pygame.font.Font("font/yuwei.ttf", 32)
		self.font3=pygame.font.Font("font/hanyi.ttf", 29)
		self.conts=open("diag.txt","r").readlines()
		self.conts=map(lambda x:unicode(x,"utf8"),self.conts)
		self.color=(0,0,0)
		self.now=0
		self.cd=200
		self.ca=0
		self.al=self.cd
		self.dead1=self.font2.render(u'胜败乃兵家常事',True,(255,20,20))
		self.dead2=self.font2.render(u'大侠请重新来过',True,(255,20,20))
		self.boss=u'叼叼'
		self.carn=u'野球拳'
		self.guan=u'青山磊落险峰行'

	def re_bo(self,x,y):
		global Story
		c1=self.font.render(self.boss,True,(255,0,0))
		c2=pygame.Surface((670*x,10))
		c2.fill((255,10,0))
		c3=self.font.render(str(y),True,(255,240,240))
		#if Story.bossing:
		c4=self.font3.render(self.carn,True,(255,100,55))
		return (c1,c2,c3,c4)

	def re_cal(self):
		global Ziji
		c1=self.rd2(u'得分：'+str(Ziji.fen))
		c2=self.rd2(u'残机：'+str(Ziji.life))
		c3=self.rd2(u'野球拳：'+str(Ziji.boom))
		c4=self.rd2(u'功力：'+str(Ziji.power))
		c5=self.rd2(u'擦弹：'+str(Ziji.ca))
		c6=self.font3.render(u'章回：'+self.guan,True,(255,40,20))
		return (c1,c2,c3,c4,c5,c6)

	def rd(self,x):
		return self.font.render(x,True,self.color)

	def rd2(self,x):
		return self.font2.render(x,True,self.color)

	def run(self,timep):
		if self.al<=0 and keyp[K_z]:
			self.now+=2
			self.al=self.cd
		else:
			self.al-=timep
		tmp=self.conts[self.now]
		if(tmp[0]=='#'):
			self.now+=1
			return '###'
		self.now+=1
		say=self.conts[self.now]
		self.now-=1
		say=say.split('#')
		say[1]=say[1][:len(say[1])-1]
		if len(say[1])>18:
			self.two_line=1
			return (int(tmp),self.rd(say[0]),self.rd(say[1][:18]),self.rd(say[1][18:]))
		else:
			self.two_line=0
			return (int(tmp),self.rd(say[0]),self.rd(say[1]))

class juben:
	def __init__(self):
		self.event=0
		self.t=0
		self.alt=0
		self.bossing=0
		self.p=1
		self.cd=0
		self.clo0=[0,0,0,0,0,0,0,0,0,0,0]
		self.clo=[0,0,0,0,0,0,0,0,0,0,0]
		self.djs=100

	def bli(self):
		global screen,stage,Diag
		screen.blit(info,(818,20))
		infos=Diag.re_cal()
		screen.blit(infos[0],(845,30))
		screen.blit(infos[1],(845,63))
		screen.blit(infos[2],(845,96))
		screen.blit(infos[3],(845,129))
		screen.blit(infos[4],(845,162))
		screen.blit(infos[5],(845,220))
		if self.bossing:
			now_boss=Diag.re_bo(self.p,self.djs)
			screen.blit(now_boss[0],(26,15))
			screen.blit(now_boss[1],(92,20))
			screen.blit(now_boss[2],(770,17))
			screen.blit(now_boss[3],(770-len(Diag.carn)*30,37))
			if self.djs<=10 and self.clo[self.djs]==0:
				self.clo[self.djs]=1
				Koe.sd[16].play()
		screen.blit(bg,(0,0))

	def run(self,timep):
		global Koe,talking,stage,Diag,Bgm
		screen.blit(stage,(22,18))

		if self.event==0:
			self.bossing=0
			stage=j_img('pics/stage_00.jpg',775,705)
			talking=1
			self.event+=1
			Bgm.change(4)
			return

		if self.event==1:
			self.event+=1  if talking==0 else 0
			self.c=16
			return

		# M1
		if self.event==2:
			if self.c<=0 and len(eners)<=0:
				Koe.sd[5].play()
				self.event+=1
				return
			if self.t<=0 and self.c>0:
				if self.c&1:
					n_ener=diji_0(1,50,300,10,1)
				else:
					n_ener=diji_0(1,750,300,10,-1)
				n_ener.pre()
				eners.append(n_ener)
				self.c-=1
				self.t=2000
			else:
				self.t-=timep

		if self.event==3:
			n_ener=diji_1(1,450,200,130,0)
			n_ener.pre()
			eners.append(n_ener)
			self.alt=0
			self.event+=1

		if self.event==4:
			self.alt+=timep
			if self.alt>13000 or len(eners)<=0:
				self.event+=1

		if self.event==5:
			n_ener=diji_1(1,180,200,40,1)
			n_ener.pre()
			eners.append(n_ener)
			n_ener=diji_1(1,720,200,40,-1)
			n_ener.pre()
			eners.append(n_ener)
			self.alt=0
			self.event+=1

		if self.event==6:
			if len(eners)<=0:
				self.alt+=timep
			if self.alt>1000:
				self.event+=1
				self.c=16
				self.alt=0
				n_ener=diji_1(1,30,200,120,2)
				n_ener.pre()
				eners.append(n_ener)

		if self.event==7:
			self.alt+=timep
			if self.alt>1500 and self.c>0:
				self.alt=0
				if self.c&1:
					n_ener=diji_0(1,30,300,15,1)
					n_ener.pre()
				else:
					n_ener=diji_0(1,750,400,15,-1)
					n_ener.pre()
				self.c-=1
				eners.append(n_ener)
			if self.c<=0 and len(eners)<=0:
				self.alt=0
				Diag.al=800
				self.event+=1

		if self.event==8:
			self.alt+=timep
			if self.alt>3000:
				Diag.boss=u'钟灵'
				n_ener=diji_2(3,420,200,280,0)
				n_ener.pre()
				eners.append(n_ener)
				self.event+=1
				self.clo=self.clo0[:]
				talking=1

		if self.event==9:
			if talking==0:
				self.bossing=1
				self.event+=1
				Bgm.change(2)

		# M1 half
		if self.event==10:
			if len(eners)<=0:
				self.bossing=0
				Ziji.booming=1000
				Ziji.xi+=1000
				self.event+=1
				Ziji.muteki=1000
				self.alt=0

		if self.event==11:
			self.alt+=timep
			if self.alt>5000:
				self.event+=1
				Diag.al=800
				talking=1

		if self.event==12:
			if talking==0:
				self.event+=1
				stage=j_img('pics/stage_11.jpg',775,705)
				self.alt=0
				self.cd=0
				self.cd2=0
				self.c=5
				Bgm.change(8)

		# M1 after half
		if self.event==13:
			self.alt+=timep
			self.cd-=timep
			self.cd2-=timep
			if self.alt>=58000:
				self.alt=0
				self.cd2=2000
				self.c=8
				self.event+=1
			if self.alt>7000 and self.c>0 and self.cd2<=0:
				if len(eners)<=0:
					self.cd2=2000
					self.c-=1
					n_ener=diji_1(1,400,200,150,0)
					n_ener.pre()
					eners.append(n_ener)

			if self.alt>2000 and self.cd<=0:
				self.cd=1500
				nx=26
				ny=-20
				w=18
				h=12
				dx=1
				dy=0
				Koe.sd[24].play()
				for i in range(5):
					ny+=70
					danmu_geners.append(danmu_sniper0('pics/slut6.png',nx,ny,dx,dy,w,h,0))
					ny+=70
					danmu_geners.append(danmu_sniper0('pics/slut6.png',nx+768,ny,-dx,dy,w,h,180))

		if self.event==14:
			self.alt+=timep
			self.cd-=timep
			self.cd2-=timep
			if self.c<=0 and self.alt>40000:
				self.event+=1
				self.alt=0
				danmu_geners.append(danmu_boo(400,100))
			if self.alt>5000 and self.c>0 and self.cd2<=0:
				self.c-=1
				self.cd2=4000
				danmu_ins(danmu_fsniper("pics/slut8.png",400,100,32,(100,100),3.2,20,20))
			if self.alt>3500 and self.cd<=0:
				self.cd=500
				nx=26
				ny=-20
				w=20
				h=12
				dx=2
				dy=0
				Koe.sd[24].play()
				for i in range(5):
					ny+=120
					danmu_geners.append(danmu_sniper0('pics/slut6.png',nx,ny,dx,dy,w,h,0))
					ny+=120
					danmu_geners.append(danmu_sniper0('pics/slut6.png',nx+768,ny,-dx,dy,w,h,180))

		if self.event==15:
			self.alt+=timep
			if self.alt>=4500:
				self.event+=1
				#danmu_ins(danmu_fsniper("pics/slut8.png",400,100,32,(100,100),3.2,20,20))
				Diag.boss=u'木婉清'
				n_ener=diji_3(6,650,220,200,0)
				n_ener.pre()
				eners.append(n_ener)
				self.clo=self.clo0[:]
				talking=1

		if self.event==16:
			if talking==0:
				Bgm.change(9)
				self.bossing=1
				self.event+=1

		if self.event==17:
			if len(eners)<=0:
				self.event+=1
				self.bossing=0
				Ziji.kill_boss()
				self.alt=0

		if self.event==18:
			self.alt+=timep
			if self.alt>4000:
				talking=1
				self.event+=1
		# M2
		if self.event==19:
			if talking==0:
				Diag.guan=u'马疾香幽,崖高人远'
				Bgm.change(10)
				stage=j_img('pics/stage_2.jpg',775,705)
				Ziji.muteki=3000
				self.event+=1
				self.alt=0
				self.cd=0
				self.cd2=0
				self.c=0

		if self.event==20:
			self.alt+=timep
			self.cd-=timep
			self.cd2-=timep
			if self.alt>3500 and self.cd<=0 and self.c<35:
				self.cd=1200 if self.alt<7000 else 1000
				self.c+=1
				if self.c&2:
					n_ener=diji_4(7 if sui(10)>0 else 1,750,300,10,-1)
				else:
					n_ener=diji_4(7 if sui(10)>0 else 1,50,200,10,1)
				n_ener.pre()
				eners.append(n_ener)
			if self.alt>10000 and self.c>24 and self.cd2<=0 and len(eners)<4:
				self.cd2=5500 if self.alt<20000 else 3000
				n_ener=diji_5(7,450,100,40,1)
				n_ener.pre()
				eners.append(n_ener)
			if self.alt>70000:
				self.event+=1
				self.alt=0
				self.cd=0
				self.cd2=0

		if self.event==21:
			self.alt+=timep
			self.cd-=timep
			self.cd2-=timep
			if self.alt>60000:
				self.alt=0
				self.cd=0
				self.event+=1
			if self.alt>6000 and self.cd<=0:
				self.cd=1000 if self.alt<30000 else 600
				n_ener=diji_stone(8,sui(300)+350,50,7,1,120+sui(30),120+sui(30))
				n_ener.pre()
				Koe.sd[25].play()
				eners.append(n_ener)
			if self.alt>6000 and self.cd2<=0:
				self.cd2=3000 if self.alt<35000 else 1500	
				danmu_ins(danmu_dsniper("pics/slut15.png",330+sui(300),30,30,(700,20),3.5,20,20))

		if self.event==22:
			self.alt+=timep
			if self.alt>3500 and self.cd<=0:
				self.cd=1
				ener_ins(diji_stone(8,400,30,12,2,200,200))
				Koe.sd[25].play()
			if self.alt>9000:
				self.event+=1
				talking=1				

class anime():
	def __init__(self,x):
		src='pics/ani_'+str(x)+'_'
		self.num=1
		self.tu=[]
		self.al=0
		self.now=0
		self._x,self._y=0,0
		while os.path.exists(src+self.cal(self.num)+'.png'):
			self.tu.append(pygame.image.load(src+self.cal(self.num)+'.png').convert_alpha())
			self.num+=1
		self.num-=1

	def next(self,timep):
		self.al+=timep
		if self.al>=83:
			self.al=0
			self.now+=1
		return self.now<self.num

	def cal(self,x):
		if x<10:
			return '000'+str(x)
		elif x<100:
			return '00'+str(x)
		elif x<1000:
			return '0'+str(x)
		else:
			return str(x)

class anis():
	def __init__(self):
		self.an=[]
		for i in range(6):
			self.an.append(anime(i))		

class lihui():
	def __init__(self):
		n=100
		self.li=[]
		src='pics/lh_'
		for i in range(n):
			if os.path.exists(src+str(i)+'.png'):
				self.li.append(p_img(src+str(i)+'.png',300,400))
			else:
				break

		self._w,self._h=35,55
		n=100
		self.di=range(3000)
		src='pics/zab_'
		for i in range(n):
			if os.path.exists(src+str(i)+'.png'):
				self.di[i]=(p_img(src+str(i)+'.png',self._w,self._h))
				self.di[i+1000]=(p_img(src+str(i+1000)+'.png',self._w,self._h))
			else:
				break

class guize():
	def run(self,timep):
		global danmu_geners,danmu_card,card_h,card_t,gener_max,Diag,talking
		global Lihui,eners,animes
		if talking==0:
			Ziji.run(timep)
		if Ziji.dying<=0:
			if Ziji.muteki>0 and Ziji.m_cd>100:
				screen.blit(Ziji.mu,(1+Ziji._x-Ziji._w*0.5,Ziji._y-Ziji._h*0.5))
			else:
				screen.blit(Ziji.img,(1+Ziji._x-Ziji._w*0.5,Ziji._y-Ziji._h*0.5))
			if Ziji.slow<3:
				screen.blit(Ziji.center,(Ziji._x-8,Ziji._y-8))
		
		# deal with diji
		eners=filter(lambda x:x.run(timep),eners)
		for i in eners:
			if i._w==Lihui._w:
				screen.blit(Lihui.di[i.img],(i._x-i._w*0.5,i._y-i._h*0.5))
			else:
				screen.blit(pygame.transform.scale(Lihui.di[i.img],(i._w,i._h)),(i._x-i._w*0.5,i._y-i._h*0.5))
			if vec_mo(i._x,i._y,Ziji._x,Ziji._y)<i.r-2 and Ziji.muteki<=0:
				Ziji.miss()

		# deal with ani
		animes=filter(lambda x:x.next(timep),animes)
		map(lambda x:screen.blit(x.tu[x.now],(x._x,x._y)),animes)

		# deal with danmu
		cnt=0
		card_pt=card_h
		while card_h!=card_t and cnt<gener_max:
			card_h=(card_h+1)%que_max
			#print card_h,card_t
			cnt+=danmu_card[card_h].run(timep,gener_max-cnt)
			if card_pt<0 and danmu_card[card_h].now<danmu_card[card_h].tot:
				card_pt=(card_h-1)%que_max
				if card_pt<0:
					card_pt+=que_max
		if card_pt>0:
			card_h=card_pt

		danmu_geners=filter(lambda x:x.run(timep),danmu_geners)
		map(lambda i:screen.blit(i.img,(i._x-i._w*0.5,i._y-i._h*0.5)),danmu_geners)
		if Ziji.dying<=0 and talking==0:
			for i in danmu_geners:
				if i.friend==0 or i.friend==4:
					if i.pd==0:
						dist=vec_mo(i._x,i._y,Ziji._x,Ziji._y)	
					else:
						dist=cal_dist(Ziji._x,Ziji._y,i)
					if Ziji.muteki<=0 and dist<i.r+1:
							Ziji.miss()
					elif dist<i.r+16:
						Ziji.ca+=1
						Ziji.fen+=int(i.r+16-dist)
						Koe.sd[18].play()

				elif i.friend==2:
					dist=vec_mo(i._x,i._y,Ziji._x,Ziji._y)
					if dist<i.r+10:
						i.eaten=1
						Ziji.fen+=i.fen
						Ziji.life+=i.life
						Ziji.boom+=i.boom
						o_p=Ziji.power
						Ziji.power+=i.power
						if power_up(Ziji.power,o_p):
							Koe.sd[20].play()
						#print Ziji.fen
					elif Ziji._y<=item_line or ((Ziji.slow<3 or Ziji.booming>0) and dist<i.r+Ziji.xi):
						i.zz=1
		for i in filter(lambda x:x.friend==1 or x.friend==3,danmu_geners):
			for j in eners:
				if(vec_mo(i._x,i._y,j._x,j._y)<i.r+Lihui._w):
					j.get_harm(i.harm)
					anime_ins(3,j._x-35,j._y)
					i.harm=0 if i.friend==1 else i.harm>>1
					i.zha=0
		ke_danmu=filter(lambda x:x.friend==3,danmu_geners)
		if len(ke_danmu)>0:
			di_danmu=filter(lambda x:x.friend==0,danmu_geners)
			danmu_geners=filter(lambda x:x.friend!=0,danmu_geners)
			#print len(ke_danmu)
			for j in di_danmu:
				for i in filter(lambda x:x.friend==3,danmu_geners):
					if vec_mo(i._x,i._y,j._x,j._y)>i.r+j.r+70:
						danmu_geners.append(j)
						break

		#print len(danmu_geners)
		

		# deal with dialogues
		if talking:
			now=Diag.run(timep)
			if now[0]=='#':
				talking=0
			else:
				idx=now[0]
				if idx%100<99:
					screen.blit(Lihui.li[idx%100],(0,350))
				idx/=100
				if idx<99:
					screen.blit(Lihui.li[idx],(500,350))
				screen.blit(diag_board,(172,550))
				screen.blit(now[1],(192,565))
				screen.blit(now[2],(192,589))
				if Diag.two_line:
					screen.blit(now[3],(192,613))



#********************************** main *************************************************
Ziji 		= 	ziji()
clock 		= 	pygame.time.Clock()
Story		=	juben()
Rule		=	guize()
Diag		=	monji()
Lihui 		=	lihui()
Koe 		=	Sound()
Ani 		=	anis()
Bgm 		= 	Music()

Bgm.change(0)

screen.blit(info,(818,20))
screen.blit(bg,(0,0))
screen.blit(menu,(25,20))
pygame.display.update()
menu=p_img("pics/menu.png",770,700)
pygame.mouse.set_visible(0)
rec_list=[((25,20),(795,720)),((820,20),(1240,720))]
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()

	keyp=pygame.key.get_pressed()
	time_pass = clock.tick(120)
	#Bgm.check()

	esc_cd-=min(esc_cd,time_pass)
	if Paused:	
		if Ziji.life>0 and keyp[K_z]:
			Paused=0
		elif keyp[K_x]:
			Paused=0
			Ziji.refresh()
			Story.event=0
			card_h=card_t
			Diag.now=0
			danmu_geners=[]
			eners=[]
		elif keyp[K_c]:
			exit()			
		continue
	
	if Paused==0 and keyp[K_ESCAPE] and esc_cd<=0:
		screen.blit(menu,(25,20))
		pygame.display.update()
		Paused=1
		esc_cd=300
		continue
	#print time_pass
	Story.run(time_pass)
	Rule.run(time_pass)
	Story.bli()

	#screen.blit(Lihui.di[0],(200,200))
	pygame.display.update()