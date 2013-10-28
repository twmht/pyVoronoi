# -*- coding: utf-8 -*-

from __future__ import division
from collections import defaultdict
from operator import attrgetter
from PyQt4 import QtGui,QtCore
from shape import Point,Line
from diagram import VD
from show import IOData,drawDisplay,traverse
from pointToLine import pair
import copy
import time

def savevd(lines,range_points,self,convex):
    line = []
    for l in traverse(lines):
        p1 = copy.deepcopy(l.p1)
        p2 = copy.deepcopy(l.p2)
        t = Line(p1,p2)
        t.avail = l.avail
        line.append(t)
    return VD(line,range_points,self,convex = convex)

class Canvas(QtGui.QWidget):
    edge_painter = (Line(Point(0,0),Point(610,0)),Line(Point(0,0),Point(0,610)),Line(Point(610,0),Point(610,610)),Line(Point(0,610),Point(610,610)))
    def __init__(self,parent = None):
        super(Canvas, self).__init__()
        self.IOData = IOData(self)
        self.drawDisplay = drawDisplay(self)
        self.parent = parent
        self.points = set()
        #used to output original points include duplicate
        self._points = []
        self.lines = []
        self.vd = [[],0]
        self.tangent = [[],0]
        self.hp = [[],0]
        self.isstep_by_step = False
        self.debug_message = [[],0]
        self.msg = ""
        self.vertex = []
        self.setMouseTracking(True)

    def mousePressEvent(self,event):
        p = Point(event.x(),event.y())
        self._points.append(p)
        if p not in self.points:
            self.points.add(p)
        self.drawDisplay.display_points(p)
        self.update()

    def mouseMoveEvent(self, event):
        self.parent.mouse_location.setText("("+event.x().__str__()+","+event.y().__str__()+")")

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        #print 'paintEvent'
        self.drawDisplay.drawPoints(qp)
        self.drawDisplay.drawLines(qp)
        qp.end()

    def Voronoi(self,range_points):

        if (range_points[1]-range_points[0]+1) == 2:
            #print 'len = 2'
            lower = range_points[0]
            upper = range_points[1]
            line = [Line.biSector(self.points[lower],self.points[upper])]
            line[0]._p1 = self.points[lower]
            line[0]._p2 = self.points[upper]
            #hash table for point mapping to related biSector
            self.points[lower].related.append(pair(line[0],self.points[upper]))
            self.points[upper].related.append(pair(line[0],self.points[lower]))
            #Line.intersect_with_edge(line,Canvas.edge_painter,'colinear')
            vd = VD(line,range_points,self)
            return vd

        elif (range_points[1]-range_points[0]+1) == 3:
            #print 'len = 3'
            def clip():
                lower = range_points[0]
                upper = range_points[1]
                lines = []
                dis = []
                t = 0
                mid = []
                for i in range(lower,upper):
                    for j in range(i+1,upper+1):
                        lines.append(Line.biSector(self.points[i],self.points[j]))
                        self.points[i].related.append(pair(lines[-1],self.points[j]))
                        self.points[j].related.append(pair(lines[-1],self.points[i]))
                        lines[-1]._p1 = self.points[i]
                        lines[-1]._p2 = self.points[j]
                        mid.append(((self.points[i]+self.points[j])/2,t))
                        dis.append((t,(self.points[i].x-self.points[j].x)**2+(self.points[i].y-self.points[j].y)**2,Line(self.points[i],self.points[j])))
                        t = t+1

                circumcenter = Line.intersect(lines[0],lines[1])
                if circumcenter is not None:
                    tmp_lines = None
                    dis.sort(key = lambda x : x[1])
                    triangle = 'acute'
                    if dis[0][1]+dis[1][1] == dis[2][1]:
                        triangle = 'right'
                        tmp_lines = dis[0:2]
                    elif dis[0][1]+dis[1][1]<dis[2][1]:
                        triangle = 'obtuse'

                    #print triangle
                    s = dis[2][0]
                    t = 0

                    for i in range(lower,upper):
                        for j in range(i+1,upper+1):
                            ab = (Line(self.points[i],self.points[j]))
                            hl = Line(lines[t].p1,circumcenter)
                            result = Line.intersect(hl,ab)

                            #do not determine the longest side of right triangle in the same way
                            if not (triangle == 'right' and t == s):
                                if result  is  None:
                                    #reverse policy for longest side of obtuse
                                    if not (triangle == 'obtuse' and t == s):
                                        lines[t].p1 = circumcenter
                                    else:
                                        lines[t].p2 = circumcenter
                                else:
                                    if not (triangle == 'obtuse' and t == s):
                                        lines[t].p2 = circumcenter
                                    else:
                                        lines[t].p1 = circumcenter
                            t = t+1
                    #now determine the longest side of right triangle
                    if triangle == 'right':
                        t = dis[2][0]
                        if Line.intersect(Line(lines[t].p1,circumcenter),tmp_lines[0][2])  != None or Line.intersect(Line(lines[t].p1,circumcenter),tmp_lines[1][2]) != None:
                            lines[t].p1,lines[t].p2 = circumcenter,lines[t].p2
                        else:
                            lines[t].p1,lines[t].p2 = circumcenter,lines[t].p1

                    #create circumcenter related points
                    circumcenter.iscircumcenter = True
                    lines[0].connected.append(lines[1])
                    lines[0].connected.append(lines[2])
                    lines[1].connected.append(lines[0])
                    lines[1].connected.append(lines[2])
                    lines[2].connected.append(lines[0])
                    lines[2].connected.append(lines[1])


                else:
                    mid.sort(key = lambda s: attrgetter('x','y')(s[0]))
                    t = mid[1][1]
                    del_line = lines[t]
                    for i in range(lower,upper+1):
                        u = self.points[i].related
                        for j in range(0,len(u)):
                            if u[j].line is del_line:
                                del u[j]
                                break
                    del lines[t]
                    #Line.intersect_with_edge(lines,Canvas.edge_painter,'colinear')

                return lines

            lines = []+clip()
            return VD(lines,range_points,self)

        elif (range_points[1]-range_points[0]+1) == 1:
            return VD([],range_points,self)
        else:
            mid = int((range_points[1]+range_points[0])/2)
            VDL = self.Voronoi((range_points[0],mid))

            if self.isstep_by_step == True:
                #vdl = VD(copy.deepcopy(VDL.lines),copy.deepcopy(VDL.range_points),self)
                vdl = savevd(VDL.lines,VDL.range_points,self,VDL.convex)
                vdl.pos = 'left'
                vdl.color = QtCore.Qt.blue
                self.vd[0].append(vdl)

            VDR = self.Voronoi((mid+1,range_points[1]))

            if self.isstep_by_step == True:
                #vdr = VD(copy.deepcopy(VDR.lines),copy.deepcopy(VDR.range_points),self)
                vdr = savevd(VDR.lines,VDR.range_points,self,VDR.convex)
                vdr.pos = 'right'
                vdr.color = QtCore.Qt.red
                vdr.other = vdl
                vdl.other = vdr
                self.vd[0].append(vdr)

            merge_vd = VD.merge(VDL,VDR,self.tangent)
            self.debug_message[0].append(self.msg)
            self.msg = ""
            return merge_vd

    def prepare(self):
        pset = self.points
        self.points = []
        for p in pset:
            self.points.append(p)
        self.points.sort(key= attrgetter('x','y'))

    def Run(self):
        if self.isstep_by_step == False:
            self.prepare()
            ans = self.Voronoi((0,len(self.points)-1))
            Line.intersect_with_edge(ans.lines,Canvas.edge_painter)
            self.lines = ans.lines
            self.vertex = ans.convex.vertex
            self.drawDisplay.display_output()
            self.update()
        else:
            #current state is step_by_step, switch to run all vd
            while True:
                self.parent.step_button.setEnabled(False)
                self.repaint()
                if self.vd[1] == len(self.vd[0])-1:
                    self.drawDisplay.display_output()
                time.sleep(1)
                self.vd[1] = self.vd[1]+1
                if self.vd[1]  >= len(self.vd[0]):
                    break

            self.vd = [[],0]
            self.hp = [[],0]
            self.isstep_by_step = False

    def step_by_step(self):
        self.parent.step_button.setEnabled(True)
        if not self.isstep_by_step == True:
            self.isstep_by_step = True
            self.prepare()
            final = self.Voronoi((0,len(self.points)-1))
            #for run after step
            self.lines = final.lines
            self.vertex = final.convex.vertex
            Line.intersect_with_edge(final.lines,Canvas.edge_painter)
            #final_vd = VD(copy.deepcopy(final.lines),copy.deepcopy(final.range_points),self)
            final_vd = savevd(final.lines,final.range_points,self,final.convex)
            final_vd.pos = 'final'
            final_vd.color = QtCore.Qt.black
            self.vd[0].append(final_vd)

        self.repaint()
        if self.vd[1] == len(self.vd[0])-1:
            self.drawDisplay.display_output()
        self.vd[1] = self.vd[1]+1
        if self.vd[1]  >= len(self.vd[0]):
            self.parent.step_button.setEnabled(False)
            self.vd = [[],0]
            self.hp = [[],0]
            self.isstep_by_step = False
