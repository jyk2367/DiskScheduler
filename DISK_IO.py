from tkinter import Tk, Frame,TRUE,FALSE,NONE
from tkinter.ttk import Label,Treeview
from tkinter.simpledialog import askinteger
from random import randint
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class Tracer:
    counter=1
    def __init__(self,jobPosition,jobMovement,accumulateTime,rotationalTime=NONE):
        self.jobNumber=Tracer.counter
        self.jobPosition=jobPosition
        self.jobMovement=jobMovement
        self.accumulateTime=accumulateTime
        self.rotationalTime=rotationalTime
        Tracer.counter+=1


    def __str__(self):
        return "jobNumber : {}, jobPosition : {}, jobMovement : {}, accumulateTime : {}, rotationalTime : {}".format(
            self.jobNumber,self.jobPosition,self.jobMovement, self.accumulateTime,self.rotationalTime
        )

class Policy:
    def __init__(self,diskQueue,initialPoint,initialSector=NONE):
        self.diskQueue=diskQueue            # 디스크 큐
        self.initialPoint=initialPoint      # 트랙 시작지점(초기 위치)

        # Rotational
        self.SectorQ=dict()
        for i in range(8):
            self.SectorQ[i]=list()
        cnt=0
        for i in range(len(self.diskQueue)):
            if(cnt>7):
                cnt=0
            self.SectorQ[cnt].append(self.diskQueue[i])
            cnt+=1

        self.initialSector=initialSector    # Sector 시작지점


    def SSTF(self):
        tr=[]                         # Tracer 리스트
        currentCur=self.initialPoint  # 현재 디스크 arm 트랙 위치
        acc=0                         # 누적 값
        while(len(self.diskQueue)>0):
            sst=dict()                    # shortest seek time 리스트
            for dq in self.diskQueue:
                sst[str(dq)]=dq-currentCur

            sst=sorted(sst.items(),key=lambda x: abs(x[1]))       # 현재 current와 가까운 point 순으로 정렬

            nextCur=int(sst[0][0])
            self.diskQueue.remove(int(sst[0][0]))
            movement=nextCur-currentCur         # seek time : 디스크 arm이 트랙을 옮기는 시간(=거리)
            acc+=abs(movement)
            currentCur=nextCur
            tr.append(Tracer(currentCur,movement,acc))    # 위치, 거리, 누적

        return tr
            

    def SCAN(self):
        SP=0                          # 시작점
        EP=400                        # 끝점
        tr=[]                         # Tracer 리스트

        currentCur=self.initialPoint  # 현재 디스크 arm 트랙 위치
        lastCur=self.initialPoint     # 디스크 arm 이전 트랙 위치

        direction=1                   # 디스크 arm 움직이는 방향
        acc=0                         # 누적 값
        
        while(len(self.diskQueue)>0):
            lastCur+=direction

            for dq in self.diskQueue:
                if lastCur==dq:
                    nextCur=dq
                    self.diskQueue.remove(dq)
                    movement=nextCur-currentCur         # seek time : 디스크 arm이 트랙을 옮기는 시간(=거리)
                    acc+=abs(movement)
                    currentCur=nextCur
                    tr.append(Tracer(currentCur,movement,acc))    # 위치, 거리, 누적

            if lastCur>=400:
                direction=-1
            elif lastCur<=0:
                direction=1
        
        return tr

    # sector 8개
    def SPTF(self):
        tr=[]                         # Tracer결과 저장용 리스트
        currentCur=self.initialPoint  # 현재 디스크 arm 트랙 위치
        currentSec=self.initialSector # 현재 디스크 arm 섹터 위치
        rotationalTime=0              # rotational time : 디스크 arm이 섹터를 옮기는 시간
        acc=0                         # 누적 값
        while(len(self.diskQueue)>0):
            spt=dict()               
            sector=0
            for dq in self.diskQueue:
                # (Positioning Time) : 현재 디스크 arm 섹터를 옮기는 시간(rotational time)+ 트랙을 옮기는 시간(seek time)
                for i in range(len(self.SectorQ)):
                    if dq in self.SectorQ[i]:
                        sector=i
                        break
                spt[str(dq)]=((20*abs(currentSec-sector)),dq-currentCur,(20*abs(currentSec-sector))+dq-currentCur)

            spt=sorted(spt.items(),key=lambda x: (abs(x[1][2])))

            rotationalTime=spt[0][1][0]            # rotational time : 디스크 arm이 섹터를 옮기는 시간
            nextCur=int(spt[0][0])
            self.diskQueue.remove(int(spt[0][0]))
            movement=nextCur-currentCur                         # seek time : 디스크 arm이 트랙을 옮기는 시간(=거리)
            acc+=abs(movement)
            currentCur=nextCur
            currentSec+=1
            if currentSec==8:
                currentSec=0
            tr.append(Tracer(currentCur,movement,acc,rotationalTime))    # 위치, 거리, 누적, rotational Time
    
        return tr

def MakeWindow(result,policy,initialPoint,diskQueue):
    
    window = Tk()
    window.wm_title("Disk IO")
    frame = Frame(window)
    frame.pack()
    x=[]
    for r in result:
        x.append(r.jobPosition)
    y=np.linspace(0,400,len(result),dtype=int)
    fig=plt.Figure(figsize=(8,4),dpi=100)
    ax = fig.add_subplot(1, 1, 1)
    ax.xaxis.set_ticks_position('top')
    ax.yaxis.grid(linestyle = '-', color = 'gray')
    ax.invert_yaxis()
    ax.plot(x, y, "r-",x,y,"ro", linewidth = 1)

    canvas =FigureCanvasTkAgg(fig,master=window)

    Label(frame,width=20, text = 'Policy',relief="solid").grid(row=0, column=0)
    Label(frame,width=20, text = policy,relief="solid" ).grid(row=1, column=0)
    Label(frame,width=20, text='초기 위치',relief="solid").grid(row=0, column=1)
    Label(frame,width=20, text=initialPoint,relief="solid").grid(row=1, column=1)
    Label(frame,width=80, text="디스크 큐",relief="solid").grid(row=0, column=2)
    for i in range(len(diskQueue)):
        diskQueue[i]=str(diskQueue[i])
    dq=", ".join(diskQueue)
    Label(frame,text=dq,width=80,relief="solid").grid(row=1, column=2)

    canvas.get_tk_widget().pack(side='bottom')

    treeview1 = Treeview(window, columns=["one", "two", "three", "four","five"], displaycolumns=[
                             "one", "two", "three", "four","five"])
    treeview1.column("#0", width=80, anchor="center",stretch=TRUE)
    treeview1.heading("#0", text="번호", anchor="center")

    treeview1.column("#1", width=120, anchor="center",stretch=TRUE)
    treeview1.heading("one", text="위치", anchor="center")

    treeview1.column("#2", width=130, anchor="center",stretch=TRUE)
    treeview1.heading("two", text="seek time(트랙 거리)", anchor="center")

    treeview1.column("#3", width=120, anchor="center",stretch=TRUE)
    treeview1.heading("three", text="누적", anchor="center")

    treeview1.column("#4", width=120, anchor="center",stretch=TRUE)
    treeview1.heading("four", text="rotation Time(섹터 거리)", anchor="center")

    treeview1.column("#5", width=120, anchor="center",stretch=TRUE)
    treeview1.heading("five", text="Positioning Time", anchor="center")

    i = 0
    for r in result:
        treeview1.insert('', 'end', text=r.jobNumber, values=[
                         r.jobPosition, r.jobMovement, r.accumulateTime, 
                         r.rotationalTime if r.rotationalTime!=NONE else "X", 
                         r.rotationalTime+abs(r.jobMovement) if r.rotationalTime!=NONE else "X"
                         ], iid=str(i)+"번")
        i += 1
    
    treeview1.pack(side='bottom',fill='both')

    window.mainloop()



if __name__=="__main__":
    diskQueue=list()
    initialPoint=50
    initialSector=randint(0,7)
    count=randint(8,20)

    diskQueue=[
        55,58,32,22,90,11
    ]
    # for i in range(count):
    #     diskQueue.append(randint(0,400))
    copyQueue=diskQueue.copy()                             # window 출력용
    p=Policy(diskQueue,initialPoint,initialSector)
    diskQueue=copyQueue                                    # 헷갈리니까 다시 바꿈

    Menu = Tk()
    Menu.withdraw()
    MENU = askinteger("Menu","1.SSTF 2.SCAN 3.SPTF",minvalue=1,maxvalue=3)
    Menu.destroy()

    if MENU==1:
        policy="SSTF"
        result=p.SSTF()
    elif MENU==2:
        policy="SCAN"
        result=p.SCAN()
    elif MENU==3:
        policy="SPTF"
        result=p.SPTF()
    
    MakeWindow(result,policy,initialPoint,diskQueue)