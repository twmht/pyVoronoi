# -*- coding: utf-8 -*-

class ConvexHull:
    def __init__(self,vd):
        self.CH = [0]
        self.length = 0
        self.vd = vd
        self.vertex = []

    @staticmethod
    def cross(po,pa,pb):
        return (pa.x-po.x)*(pb.y-po.y)-(pa.y-po.y)*(pb.x-po.x)

    def make_cw_ccw(self):
        for i in range(0,self.length):
            self.CH[i].ccw = self.CH[(i-1)%self.length]
            self.CH[i].cw = self.CH[(i+1)%self.length]
            self.vertex.append(self.CH[i])

    def Andrew_monotone_chain(self,range_points):
        self.CH = self.CH*(range_points[1]-range_points[0]+1)*2
        m=0
        for i in range(range_points[0],range_points[1]+1):
            while m >= 2 and ConvexHull.cross(self.CH[m-2],self.CH[m-1],self.vd.parent.points[i]) <= 0:
                m = m-1
            self.CH[m] = self.vd.parent.points[i]
            m = m+1

        t = m+1
        for i in range(((range_points[1])+1)-2,range_points[0]-1,-1):
            while m >= t and ConvexHull.cross(self.CH[m-2],self.CH[m-1],self.vd.parent.points[i]) <= 0:
                m = m-1
            self.CH[m] = self.vd.parent.points[i]
            m = m+1
        m = m-1
        #print m
        self.length = m
        self.make_cw_ccw()
        return self
