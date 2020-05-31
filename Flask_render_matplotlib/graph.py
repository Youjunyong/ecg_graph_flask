import sys, os, random, threading, csv, sqlite3
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation


conn = sqlite3.connect("peak_data.sqlite")   # 저장할 DB파일 이름
curs = conn.cursor()
try :
    curs.execute("CREATE TABLE measures (timestamp INTEGER, measure INTEGER)")  
except sqlite3.OperationalError :
    print("peak 데이터 베이스명 중복")
conn2 = sqlite3.connect("data.sqlite")   # 저장할 DB파일 이름
curs2 = conn2.cursor()
try :
    curs2.execute("CREATE TABLE measures (timestamp INTEGER, measure INTEGER)")  
except sqlite3.OperationalError :
    print("ecg 데이터 베이스명 중복")

peak_1 = 0
heart_rate=0
max_point = 60
max_point2 = 60

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = fig.add_subplot(211, xlim=(0, 110), ylim=(0, 1024))
        self.axes2 = fig.add_subplot(212, xlim=(0, 110), ylim=(0, 1024))

        # self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
    # def compute_initial_figure(self):
    #     pass
class AnimationWidget(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        
        vbox = QVBoxLayout()   #QVBox = 최대 수직 위젯
        self.canvas = MyMplCanvas(self, width=10, height=8, dpi=100)
        vbox.addWidget(self.canvas)  #캔버스는 수직위젯 사용
       


        hbox = QHBoxLayout()  #QHBox = 최대 수평 위젯
        self.start_button = QPushButton("start", self)  #버튼 1 생성
        self.stop_button = QPushButton("stop", self)       #버튼 2 생성
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        
        #라벨 생성
        
        self.label_2 = QLabel("ECG-Graph", self)
        self.label_2.setStyleSheet('color:red; background:blue')
        self.label_1 = QLabel(" Peak-Detect : %s "%peak_1 ,self)
        self.label_1.setStyleSheet('color:blue; background:yellow')
        
        hbox.addWidget(self.label_1)
        hbox.addWidget(self.label_2)

       
        
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.stop_button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        global max_point, max_point2
        #그래프 1
        self.x = np.arange(max_point)
        self.y = np.ones(max_point, dtype=np.float)*np.nan
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)
        #그래프 2
        self.x2 = np.arange(max_point2)
        self.y2 = np.ones(max_point2, dtype=np.float)*np.nan
        self.line2, = self.canvas.axes2.plot(self.x2, self.y2, animated=True,color='red', lw=2)

    def heartRate(self):
        global heart_rate
        heart_rate = peak_1 * 6
        threading.Timer(10, self.heartRate).start()
        self.label_2.setText(" heart rate : %s "%heart_rate)
        return heart_rate

    def update_line(self, i):
        y = random.randint(0,1024)
        if y >= 900:
            y = 800
        else:
            y = 0
        
        def peak() :   # Peak Counting
            if y >=800 :
                global peak_1
                peak_1 += 1
                self.label_1.setText(" Peak-Detect : %s "%peak_1)
        old_y = self.line.get_ydata()
        new_y = np.r_[old_y[1:], y]
        self.line.set_ydata(new_y)
        peak()
        write_data = []
        write_data.append(1577863015 + i*2)
        write_data.append(y)
        with open('./peak_data.csv','a', newline='') as f:
            wt = csv.writer(f)
            wt.writerows([write_data])  #for문 없이 바로쓰기.
            write_data = []
        return [self.line]

    def update_line2(self, i):
        y2 = random.randint(0,1024)
        old_y2 = self.line2.get_ydata()
        new_y2 = np.r_[old_y2[1:], y2]
        self.line2.set_ydata(new_y2)
        write_data2 = []
        write_data2.append(1577863015 + i*2)
        write_data2.append(y2)
        with open('./data.csv','a', newline='') as f:
            wt2 = csv.writer(f)
            wt2.writerows([write_data2])  #for문 없이 바로쓰기.
            write_data2 = []
        return [self.line2]
    
    def on_start(self):
        #interver 숫자 높이면 속도 상승
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line,blit=True, interval=100) 
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.update_line2,blit=True, interval=100)
        
    def on_stop(self):
        self.ani._stop()
        self.ani2._stop()
        reader = csv.reader(open('peak_data.csv', 'r'))   # CSV파일 읽기모드로 열기
        reader2 = csv.reader(open('data.csv', 'r'))
        for row in reader:                             #for 반복문을 통하여 DB에 작성
            to_db = [(row[0]), (row[1])]
            curs.execute("INSERT INTO measures (timestamp, measure) VALUES (?, ?);", to_db)
        for row in reader2:                             #for 반복문을 통하여 DB에 작성
            to_db2 = [(row[0]), (row[1])]
            curs2.execute("INSERT INTO measures (timestamp, measure) VALUES (?, ?);", to_db2)
                
        conn.commit()  #커밋 (쌓아둔 명령 실행)
        conn.close()
        conn2.commit()  #커밋 (쌓아둔 명령 실행)
        conn2.close()
       

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    aw = AnimationWidget()
    aw.show()
    aw.heartRate()
    sys.exit(qApp.exec_())