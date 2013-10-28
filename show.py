# -*- coding: utf-8 -*-
from shape import Point,Line
from PyQt4 import QtGui, QtCore
from collections import defaultdict
from operator import attrgetter

def traverse(o, tree_types=list):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value):
                yield subvalue
    else:
        yield o

class IOData:
    def __init__(self,painter):
        self.painter = painter
        self.readPoints = [[],0]
        self._readPoints = [[],0]

    def ReadFile(self,filename = None):
        self.painter.drawDisplay.ClearCanvas()
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename != '':
            f = open(filename,'r')
            self.readPoints = [[],0]
            self._readPoints = [[],0]
            self.painter.points = []
            self.painter.parent.next_data.setEnabled(True)
            while True:
                num = f.readline()
                if len(num) == 0:
                    continue
                elif num[0] == '#' or num[0] == '\n':
                    continue
                elif int(num) == 0:
                    break
                s = set()
                _data = []
                num = int(num)
                for i in range(0,num):
                    #to avoid the comment between input point
                    while True:
                        line =  f.readline()
                        if len(line) == 0:
                            continue
                        elif line[0] == '#' or line[0] == '\n':
                            continue
                        else:
                            break

                    x,y = map(int,line.split())
                    p = Point(x,y)
                    _data.append(p)
                    if p not in s:
                        s.add(p)
                data = []
                for p in s:
                    data.append(p)

                self.readPoints[0].append(data)
                self._readPoints[0].append(_data)

            t = self.readPoints[1]
            self.painter.points.extend(self.readPoints[0][t])
            #for duplicated input data
            self.painter._points.extend(self._readPoints[0][t])
            #need to show original data,not filterd data
            for p in self.painter._points:
                self.painter.drawDisplay.display_points(p)

            self.readPoints[1] = self.readPoints[1]+1
            self._readPoints[1] = self._readPoints[1]+1
            f.close()
            self.painter.update()

    def output_data(self):
        #for debug use...
        f = open('point_output','w')
        f.write(str(len(self.painter._points))+'\n')
        for p in self.painter._points:
            f.write(p+'\n')

        f.write('0\n')

        f.close()

        #completed answer
        filename = QtGui.QFileDialog.getSaveFileName()
        if filename != '':
            f = open(filename,'w')
            f.write(self.painter.parent.output_info.text())
            f.close()



    def read_output(self):
        self.painter.drawDisplay.ClearCanvas()
        filename = QtGui.QFileDialog.getOpenFileName()
        if filename != '':
            f = open(filename,'r')
            lines = f.readlines()
            points = []
            _points = []
            for l in lines:
                t = l.split()
                if t[0] == 'P':
                    #need to create new attribute to save original point set which include duplicates
                    t1 = int(t[1])
                    t2 = int(t[2])
                    p = Point(t1,t2)
                    _points.append(p)
                    if p not in self.painter.points:
                        points.append(p)
                        self.painter.points.add((Point(t1,t2)))
                elif t[0] == 'E':
                    self.painter.lines.append(Line(Point(int(t[1]),int(t[2])),Point(int(t[3]),int(t[4]))))

            self.painter.points = points
            self.painter._points = _points
            for p in _points:
                self.painter.drawDisplay.display_points(p)
            self.painter.drawDisplay.display_output()
            self.painter.update()
            f.close()

    def next_data(self):
        self.painter.drawDisplay.ClearCanvas()
        self.painter.points = []
        self.painter._points = []
        print 'next_data'
        t = self.readPoints[1]
        _t = self._readPoints[1]
        if t == len(self.readPoints[0]):
            self.painter.parent.next_data.setEnabled(False)
            self.painter.drawDisplay.ClearCanvas()
        else:
            self.painter.points.extend(self.readPoints[0][t])
            self.painter._points.extend(self._readPoints[0][_t])
            for p in self.painter._points:
                self.painter.drawDisplay.display_points(p)
            self.readPoints[1] = self.readPoints[1]+1
            self._readPoints[1] = self._readPoints[1]+1
            self.painter.update()

class drawDisplay:
    def __init__(self,painter):
        self.painter = painter

    def display_points(self,p):
        info = self.painter.parent.data_info.text()+"P "+repr(p)+"\n"
        self.painter.parent.data_info.setText(info)
        self.painter.parent.point_num.setText(str(len(self.painter._points)))

    def display_output(self):
        info = ""
        output_lines = []
        for line in traverse(self.painter.lines):
            if line.avail == True:
                if line.p1.x >= 0 and line.p1.x <= 610 and line.p1.y >= 0 and line.p2.y <= 610:
                    if line.p1.x > line.p2.x:
                        line.p1,line.p2 = line.p1,line.p2
                    elif line.p1.x == line.p2.x:
                        if line.p1.y > line.p2.y:
                            line.p1,line.p2 = line.p1,line.p2
                    output_lines.append(line)

        output_lines.sort(key=lambda line: (line.p1.x,line.p1.y,line.p2.x,line.p2.y))

        self.painter._points.sort(key = attrgetter('x','y'))
        for point in self.painter._points:
            info = info+"P "+repr(point)+"\n"

        for line in output_lines:
            info = info +"E "+repr(line)+"\n"

        self.painter.parent.output_info.setText(info)

    def drawPoints(self, qp):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setColor(QtCore.Qt.black)
        qp.setPen(pen)
        for p in self.painter.points:
            qp.drawPoint(p.x,p.y)

        if self.painter.isstep_by_step == True:
            #print 'in drawPoint',self.painter.vd
            t = self.painter.vd[1]
            vd = self.painter.vd[0][t]
            pen.setColor(vd.color)
            qp.setPen(pen)
            for i in range(vd.range_points[0],vd.range_points[1]+1):
                qp.drawPoint(self.painter.points[i].x,self.painter.points[i].y)

            if vd.pos == 'right':
                vdl = vd.other
                pen.setColor(vdl.color)
                qp.setPen(pen)
                for i in range(vdl.range_points[0],vdl.range_points[1]+1):
                    qp.drawPoint(self.painter.points[i].x,self.painter.points[i].y)


    def drawConvexHull(self,qp,convexHull):
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.darkYellow)
        qp.setPen(pen)
        vertex = convexHull.vertex
        if len(vertex) >= 2:
            for i in range(0,len(vertex)-1):
                p1 = vertex[i]
                p2 = vertex[i+1]
                qp.drawLine(p1.x,p1.y,p2.x,p2.y)

            p1 = vertex[0]
            p2 = vertex[-1]
            qp.drawLine(p1.x,p1.y,p2.x,p2.y)

    def drawLines(self,qp):

        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.black)
        qp.setPen(pen)
        if self.painter.isstep_by_step == False:
            for l in traverse(self.painter.lines):
                if l.avail == True:
                    qp.drawLine(l.p1.x,l.p1.y,l.p2.x,l.p2.y)

            pen = QtGui.QPen()
            pen.setColor(QtCore.Qt.darkYellow)
            qp.setPen(pen)

            if len(self.painter.vertex) >= 2:
                for i in range(0,len(self.painter.vertex)-1):
                    p1 = self.painter.vertex[i]
                    p2 = self.painter.vertex[i+1]
                    qp.drawLine(p1.x,p1.y,p2.x,p2.y)

                p1 = self.painter.vertex[0]
                p2 = self.painter.vertex[-1]
                qp.drawLine(p1.x,p1.y,p2.x,p2.y)

        elif self.painter.isstep_by_step== True:
            t = self.painter.vd[1]
            vd = self.painter.vd[0][t]
            pen.setColor(vd.color)
            qp.setPen(pen)
            for l in traverse(vd.lines):
                if l.avail == True:
                    qp.drawLine(l.p1.x,l.p1.y,l.p2.x,l.p2.y)
            self.drawConvexHull(qp,vd.convex)
            if vd.pos == 'right':
                vdl = vd.other
                pen.setColor(vdl.color)
                qp.setPen(pen)
                for l in traverse(vdl.lines):
                    if l.avail == True:
                        qp.drawLine(l.p1.x,l.p1.y,l.p2.x,l.p2.y)

                self.drawConvexHull(qp,vdl.convex)

                s = self.painter.tangent[1]
                tangent = self.painter.tangent[0][s]
                pen.setColor(QtCore.Qt.gray)
                qp.setPen(pen)
                for l in tangent:
                    if l.avail == True:
                        qp.drawLine(l.p1.x,l.p1.y,l.p2.x,l.p2.y)
                self.painter.tangent[1] = self.painter.tangent[1]+1

                pen.setColor(QtCore.Qt.darkMagenta)
                qp.setPen(pen)
                w = self.painter.hp[1]
                hp = self.painter.hp[0][w]
                for l in hp:
                    qp.drawLine(l.p1.x,l.p1.y,l.p2.x,l.p2.y)
                self.painter.hp[1] = self.painter.hp[1]+1


    def ClearCanvas(self):
        self.painter.points = set()
        self.painter._points = []
        self.painter.lines = []
        self.painter.parent.point_num.setText("0")
        self.painter.parent.data_info.clear()
        self.painter.parent.output_info.clear()
        self.painter.vd = [[],0]
        self.hp = [[],0]
        self.painter.isstep_by_step = False
        self.painter.tangent = [[],0]
        self.painter.vertex = []
        self.painter.parent.step_button.setEnabled(True)
        self.painter.repaint()
