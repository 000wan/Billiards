## ---------Billiards.py----------
##    by 권영완 (YoungWan Kweon)
##
##    version 0.0 | 2020/7/8 ~ 7/11
##      - 공과 공, 공과 벽 충돌
##      - 큐대 회전 및 힘조절
##
##    version 1.0 | 7/15~7/18
##      - 마우스로 큐대 조작
##      - 공이 충돌할때 겹치는 현상 제거
##      - 배경 이미지 추가
##      - 예외 상황 처리 및 최적화
##
##    version 2.0 | 7/31~8/1
##      - 턴 및 점수 추가
##      - 메인 화면 추가
##      - 승패 결정 및 점수 기록
##
##    version 3.0 | 2022/7/25
##      - 행렬과 좌표변환을 이용한 충돌 모션 개선
##      - 에러 수정
##

import pygame as p
import pygame_gui as pg
from math import sin, cos, atan2, sqrt, degrees
import numpy as np
def arctan(y,x):
    if y==0 and x==0: return 0
    else: return -atan2(y,x)
def rotation_matrix(theta):
    return np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])

#color
WHITE=(255,255,255)
GOLD=(250,218,94)
RED=(255,0,0)

#constant
R,G = 20, 9.8
e,ew,MUE=0.7,1,10
cushion=(30,150)
dv,dl=0.1,1
col_matrix = np.array([[(1-e)/2, 0, (1+e)/2, 0],
                      [0, 1, 0, 0],
                      [(1+e)/2, 0, (1-e)/2, 0],
                      [0, 0, 0, 1]])

#default
col,havcol={},{}
score=[0,0] # p1, p2
pscore=[30,30]
turn,nturn=False,False
gameOver=[False,''] # is gameover, winner

p.init()


class Ball:
    name=''
    v,vx,vy=0,0,0
    a,ax,ay=0,0,0
    deg=0
    obj,moving=False,False
    wall=[False,False] #[x,y]
    col=False
    x,y=0,0

    def __init__(self,x,y,color):
        if color=="white":
            self.obj=p.image.load("img/wb.png")
        elif color=="yellow":
            self.obj=p.image.load("img/yb.png")
        elif color=="red":
            self.obj=p.image.load("img/rb.png")
        self.x,self.y=x,y

    def move(self):
        #Friction
        if self.v>dv:
            self.moving=True
            self.a=MUE*G
            self.ax=-self.a*self.vx/self.v
            self.ay=-self.a*self.vy/self.v
        else:
            self.moving=False
            self.a,self.ax,self.ay=0,0,0

        #collision with wall
        if self.x-R<=dl:
            if not self.wall[0]:
                self.wall[0]=True
                self.vx=-ew*self.vx
            else:
                self.x+=dl  #exception
        elif self.x+R>=1100-dl:
            if not self.wall[0]:
                self.wall[0]=True
                self.vx=-ew*self.vx
            else:
                self.x-=dl
        else: self.wall[0]=False

        if self.y-R<=dl:
            if not self.wall[1]:
                self.wall[1]=True
                self.vy=-ew*self.vy
            else:
                self.y+=dl
        elif self.y+R>=600-dl:
            if not self.wall[1]:
                self.wall[1]=True
                self.vy=-ew*self.vy
            else:
                self.y-=dl
        else: self.wall[1]=False

        #move
        self.x+=self.vx/100
        self.y+=self.vy/100

        self.v=sqrt(self.vx**2+self.vy**2)
        self.deg=arctan(self.vy,self.vx)
        self.vx=self.vx+self.ax/100
        self.vy=self.vy+self.ay/100


def collision(balls): #collision with ball
    for i in range(len(balls)-1):
        for j in range(i+1,len(balls)):
            b1,b2=balls[i],balls[j]
            name=b1.name+b2.name
            if (b1.x-b2.x)**2+(b1.y-b2.y)**2<=4*R**2:
                if not col[name][0]:
                    col[name][0],havcol[name]=True,True
                    col[name][1]=arctan(b2.y-b1.y,b2.x-b1.x) # radian

                    # old version collision
                    '''b1.vx,b2.vx=((1-e)*b1.vx+(1+e)*b2.vx)/2, ((1+e)*b1.vx+(1-e)*b2.vx)/2
                    b1.vy,b2.vy=((1-e)*b1.vy+(1+e)*b2.vy)/2, ((1+e)*b1.vy+(1-e)*b2.vy)/2'''

                    #new version 3.0 collision
                    V = np.array([b1.vx, b1.vy, b2.vx, b2.vy]).T
                    P = np.kron(np.eye(2), rotation_matrix(col[name][1]))
                    P_inv = np.kron(np.eye(2), rotation_matrix(-col[name][1]))
                    # V'=(P^-1AP)V
                    V_later = np.matmul(P_inv, np.matmul(col_matrix, np.matmul(P, V)))
                    b1.vx, b1.vy, b2.vx, b2.vy = tuple(V_later)
            else:
                col[name][0]=False


def turnOver(balls,p1,p2):
    global turn, nturn, score, havcol, gameOver

    #minus points
    if any([havcol['ybwb'], havcol[nturn.name+'rb1'], havcol[nturn.name+'rb2']]) or not any([havcol[turn.name+'rb1'], havcol[turn.name+'rb2']]):
        score[balls.index(turn)]-=10
        turn,nturn=nturn,turn
    #plus points
    elif havcol['rb1rb2'] or all([havcol[turn.name+'rb1'], havcol[turn.name+'rb2']]):
        score[balls.index(turn)]+=10
    #no points
    else:
        turn,nturn = nturn,turn

    for i in range(len(balls)-1):
        for j in range(i+1,len(balls)):
            havcol[balls[i].name+balls[j].name]=False

    if score[0]>pscore[0]: gameOver=[True,p1]
    elif score[1]>pscore[1]: gameOver=[True,p2]

def record(p1,p2):
    with open('record.txt','r') as f:
        lines=f.read().split('\n')
        for i,line in enumerate(lines):
            if line.split(':')[0]==p1:
                if score[0]>int(line.split(':')[1]):
                    lines[i]=p1+':'+str(score[0])
            elif line.split(':')[0]==p2:
                if score[1]>int(line.split(':')[1]):
                    lines[i]=p2+':'+str(score[1])

    with open('record.txt','w') as f:
        f.write('\n'.join(lines))


manager = pg.UIManager((1100,600))

timer=p.time.Clock()

def main():
    in_main=True

    window=p.display.set_mode((1100,600))
    title=p.image.load("img/title.png").convert_alpha()
    font = p.font.SysFont(None, 25)

    start_button=pg.elements.UIButton(relative_rect=p.Rect((450, 500), (200, 60)), text='Start', manager=manager)
    warn1=font.render('Empty Name', True, RED)
    warn2=font.render('Names should be different.', True, RED)
    p1_name=pg.elements.UITextEntryLine(relative_rect=p.Rect((300, 450), (200, 70)), manager=manager)
    p2_name=pg.elements.UITextEntryLine(relative_rect=p.Rect((600, 450), (200, 70)), manager=manager)
    p1_name.set_text('Player1 Name')
    p1_name.set_text_length_limit(12)
    p2_name.set_text('Player2 Name')
    p2_name.set_text_length_limit(12)


    while in_main:
        time_delta=timer.tick(100)/1000

        window.fill(WHITE)
        window.blit(title,(0,0))

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                return
            if event.type == p.USEREVENT:
                if event.user_type == pg.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        if p1_name.get_text()!=p2_name.get_text():
                            in_main = False

            manager.process_events(event)

        manager.update(time_delta)
        if p1_name.get_text()=='' or p2_name.get_text()=='':
            window.blit(warn1,(550-warn1.get_width()//2,560))
        elif p1_name.get_text()==p2_name.get_text():
            window.blit(warn2,(550-warn2.get_width()//2,560))

        manager.draw_ui(window)
        p.display.flip()

    start_button.kill()
    p1_name.kill()
    p2_name.kill()
    game(p1_name.get_text(), p2_name.get_text())

def game(p1,p2):
    global turn, nturn, pscore

    lines=[]
    players=[p1,p2]
    with open('record.txt','r') as f:
        lines=f.readlines()
        for line in lines:
            if line.split(':')[0]==p1:
                players.remove(p1)
                pscore[0]=int(line.split(':')[1])
            elif line.split(':')[0]==p2:
                players.remove(p2)
                pscore[1]=int(line.split(':')[1])
    with open('record.txt','a') as f:
        for pl in players:
            f.write('\n'+pl+':30\n')


    running=True
    deg,dist,mdist,cr=0,30,150,1
    click,up=False,False
    stop=True
    rcxy=[]

    canvas=p.display.set_mode([1100+2*cushion[0],600+cushion[0]+cushion[1]])
    font = p.font.SysFont(None, 40)

    yb=Ball(275,375,"yellow")
    wb=Ball(962.5,300,"white")
    rb1=Ball(275,300,"red")
    rb2=Ball(825,300,"red")
    yb.name='yb'
    wb.name='wb'
    rb1.name='rb1'
    rb2.name='rb2'
    balls=[yb,wb,rb1,rb2]
    for i in range(len(balls)-1):
        for j in range(i+1,len(balls)):
            col[balls[i].name+balls[j].name] = [False,0] # collision bool, degree
            havcol[balls[i].name+balls[j].name] = False

    turn, nturn = yb, wb # yb start
    check=True

    rcue = False
    cue=p.image.load("img/cue.png").convert_alpha()
    bg=p.image.load("img/background.png").convert_alpha()

    while running:
        time_delta=timer.tick(100)/1000
        canvas.fill(WHITE)
        canvas.blit(bg,(0,0))

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                running = False
            if stop:
                if event.type == p.MOUSEBUTTONDOWN:
                    click = True
                elif event.type == p.MOUSEBUTTONUP:
                    click,up = False,True
            manager.process_events(event)
        manager.update(time_delta)

        collision(balls)

        stop=all([not i.moving for i in balls]) #is stop?

        mxy=list(p.mouse.get_pos())
        if stop:
            if mxy[0]-cushion[0]<=cr: mxy[0]=cushion[0]+cr
            elif mxy[0]-cushion[0]>=1100-cr: mxy[0]=1100+cushion[0]-cr
            if mxy[1]-cushion[1]<=cr: mxy[1]=cushion[1]+cr
            elif mxy[1]-cushion[1]>=600-cr: mxy[1]=600+cushion[1]-cr
            mxy=list(map(int,mxy))

            if not check: # 1turn finished
                turnOver(balls,p1,p2)
                check=True


            p.draw.line(canvas,WHITE,[int(turn.x+cushion[0]),int(turn.y+cushion[1])],mxy,1)
            if click:
                if dist<=mdist:
                    turn.v+=4.2
                    dist+=(mdist-30)/300 # 3 seconds
                    cr+=(R-1)/300
                p.draw.circle(canvas,WHITE,mxy,int(cr),1)
            elif up:
                if dist<=2*R:
                    dist,cr=30,1
                    up=False
                    check=False
                    turn.moving=True
                    turn.vx=turn.v*mx/md
                    turn.vy=turn.v*my/md
                else:
                    dist-=turn.v/50
        else:
            for i in balls: i.move()

        #draw cue
        for i in balls:
            canvas.blit(i.obj,(int(i.x-R+cushion[0]),int(i.y-R+cushion[1])))
        if stop:
            #mouse distance
            mx,my=mxy[0]-cushion[0]-turn.x, mxy[1]-cushion[1]-turn.y
            md=sqrt(mx**2+my**2)

            if md:
                rcue=p.transform.rotate(cue,degrees(arctan(my,mx)))
                rcxy=[ int(cushion[0] + turn.x - rcue.get_width()/2 - (dist + cue.get_width()/2)*mx/md ), int(cushion[1] + turn.y - rcue.get_height()/2 - (dist + cue.get_width()/2)*my/md ) ]
            canvas.blit(rcue,rcxy)

        p1_name=font.render(p1, True, GOLD)
        p2_name=font.render(p2, True, WHITE)
        p1_high=font.render('Highscore: %d' % pscore[0], True, GOLD)
        p2_high=font.render('Highscore: %d' % pscore[1], True, WHITE)
        p1_score=font.render('Score: %d' % score[0], True, GOLD)
        p2_score=font.render('Score: %d' % score[1], True, WHITE)

        canvas.blit(p1_name,(2*cushion[0],30-p1_name.get_height()//2))
        canvas.blit(p2_name,(1100-p2_name.get_width(),30-p1_name.get_height()//2))
        canvas.blit(p1_high,(2*cushion[0],75-p1_high.get_height()//2))
        canvas.blit(p2_high,(1100-p2_high.get_width(),75-p1_name.get_height()//2))
        canvas.blit(p1_score,(2*cushion[0],120-p1_name.get_height()//2))
        canvas.blit(p2_score,(1100-p2_score.get_width(),120-p1_score.get_height()//2))

        #Game Over
        if gameOver[0]:
            winner=font.render(gameOver[1]+' Wins!', True, WHITE)
            print(gameOver[1]+' Wins!')
            canvas.blit(winner,(550-winner.get_width()//2,300-winner.get_height()//2))
            running=False

        manager.draw_ui(canvas)
        p.display.flip()

    record(p1, p2)
    return

main()
