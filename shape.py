# -*- coding: utf-8 -*-
#Designer:
#Name: Ming-Hsuan Tu
from __future__ import division
class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

        self.iscircumcenter = False

        self.cw = None
        self.ccw = None

        self.related = []

    def __repr__(self):
        return str((int(self.x)))+" "+str((int(self.y)))
    def __add__(self,other):
        return Point(self.x+other.x,self.y+other.y)
    def __sub__(self,other):
        return Point(self.x-other.x,self.y-other.y)
    def __truediv__(self,other):
        return Point(self.x/other,self.y/other)
    def __mul__(self,other):
        return Point(self.x*other,self.y*other)
    def __eq__(self,other):
        if not isinstance(other,Point):
            return False
        return (self.x == other.x and self.y == other.y) or (self is other)
    def __gt__(self,other):
        if self.x == other.x:
            return self.y>other.y
        return self.x>other.x
    def __hash__(self):
        return 41*(41+self.x)+self.y

class Line:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

        #which two point contribute to  the biSector
        self._p1 = None
        self._p2 = None

        self.hole = None

        self.connected = []
        self.avail = True
    def __repr__(self):
        return repr(self.p1)+" "+repr(self.p2)

    def __setattr__(self, name, value):
        if not name in self.__dict__:
            self.__dict__[name] = value
        elif name == 'p1' or name == 'p2':
            self.__dict__[name] = value
        else:
            self.__dict__[name] = value
    @staticmethod
    def intersect(line1,line2):
        x1 = line1.p1.x
        y1 = line1.p1.y
        x2 = line1.p2.x
        y2 = line1.p2.y

        x3 = line2.p1.x
        y3 = line2.p1.y
        x4 = line2.p2.x
        y4 = line2.p2.y

        a = x1
        b = x2-x1
        c = y1
        d = y2-y1

        f = x4-x3
        h = y4-y3
        if b*h-d*f != 0:
            t = ((y4-y3)*(x3-x1)+(x4-x3)*(y1-y3))/((x2-x1)*(y4-y3)-(y2-y1)*(x4-x3))
            s = ((y2-y1)*(x3-x1)+(x2-x1)*(y1-y3))/((x2-x1)*(y4-y3)-(y2-y1)*(x4-x3))
            if t >= 0 and t <= 1 and s >= 0 and s <= 1:
                x = a+b*t
                y = c+d*t
                return Point(x,y)
            else:
                return None
        else:
            return None


    @staticmethod
    def biSector(p1,p2):
        mid = (p1+p2)/2
        vec = vector(p1,p2)
        p1 = (vec.nv*(100000))+mid
        p2 = (vec.nv*(-100000))+mid
        return Line(p1,p2)


    def __eq__(self,other):
        if not isinstance(other,Line):
            return False
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

    @staticmethod
    def intersect_with_edge(lines,edge_painter):
        def traverse(o, tree_types=list):
            if isinstance(o, tree_types):
                for value in o:
                    for subvalue in traverse(value):
                        yield subvalue
            else:
                yield o

        for l in traverse(lines):
            if not(l.avail == False):
                p = None
                s = []
                for edge in edge_painter:
                    p = Line.intersect(edge,l)
                    if p is not None:
                        s.append(p)
                if len(s)>0:
                    p1 = l.p1
                    p2 = l.p2
                    if (p1.x >= 0 and p1.x<=610) and (p1.y >= 0 and p1.y <= 610):
                        l.p2 = s[0]
                    elif (p2.x >= 0 and p2.x<=610) and (p2.y >= 0 and p2.y <= 610):
                        l.p1 = s[0]
                    else:
                        l.p1 = s[0]
                        l.p2 = s[1]
    def __hash__(self):
        return (41*(41+self._p1.x)+self._p1.y)+(41*(41+self._p2.x)+self._p2.y)

class vector:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2
        self.v = p2-p1
        self.nv = self.normal_vector()
    def normal_vector(self):
        x,y = self.v.y,self.v.x
        x = x*-1
        return Point(x,y)
