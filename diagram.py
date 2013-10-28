# -*- coding: utf-8 -*-

from shape import Line,Point
from ch import ConvexHull
from collections import defaultdict
from pointToLine import pair
import copy

class VD:
    def __init__(self,lines,range_points,parent = None,convex = None):
        self.parent = parent
        self.lines = lines
        self.range_points = range_points
        if convex is None:
            self.convex = self.find_convex()
        else:
            self.convex = convex
        self.color = None
        self.pos = None
        self.other = None
    @staticmethod
    def merge(VDL,VDR,tangent):

        clip_lines = []
        #used to record ray which intersect with dividing chain
        #using hash table
        ray_list = set()
        def discard_edges(ray,circumcenter,side,SG_bisector):

            def recursive_discard_edge(ray,other_point,base_point,side):
                #want to delete left remaining line
                for candidate in ray.connected:
                    if candidate.avail == True and candidate not in ray_list:
                        next_base_point = None
                        next_other_point = None
                        #catch base point
                        if(candidate.p1 is base_point or candidate.p2 is base_point):
                            if candidate.p1 is base_point:
                                next_base_point = candidate.p2
                                next_other_point = candidate.p1
                            else:
                                next_base_point = candidate.p1
                                next_other_point = candidate.p2

                            if side == 'right':
                                if ConvexHull.cross(base_point,next_base_point,other_point) > 0:
                                    candidate.avail = False
                                    recursive_discard_edge(candidate,next_other_point,next_base_point,'right')
                            elif side == 'left':
                                if ConvexHull.cross(base_point,next_base_point,other_point) < 0:
                                    candidate.avail = False
                                    recursive_discard_edge(candidate,next_other_point,next_base_point,'left')

            if side == 'right':
                #clear the edges extend to the left of HP
                #Line(hole,ray.p1) or Line(hole,ray.p2) must cw to Line(hole,bisector.p1)
                if ConvexHull.cross(circumcenter,ray.p1,SG_bisector.p1)>0:
                    #this means p1 is left to circumcenter,so replace p1 with circumcenter
                    if ray.p1.iscircumcenter == True:
                        recursive_discard_edge(ray,circumcenter,ray.p1,'right')
                    ray.p1 = circumcenter
                else:
                    if ray.p2.iscircumcenter == True:
                        recursive_discard_edge(ray,circumcenter,ray.p2,'right')
                    ray.p2 = circumcenter
            elif side == "left":
                #clear the edges extend to the right of HP
                #Line(hole,ray.p1) or Line(hole,ray.p2) must ccw to Line(hole,bisector.p1)
                if ConvexHull.cross(circumcenter,ray.p1,SG_bisector.p1)<0:
                    #this means p1 is right to circumcenter,so replace p1 with circumcenter
                    if ray.p1.iscircumcenter == True:
                        recursive_discard_edge(ray,circumcenter,ray.p1,'left')
                    ray.p1 = circumcenter
                else:

                    if ray.p2.iscircumcenter == True:
                        recursive_discard_edge(ray,circumcenter,ray.p2,'left')
                    ray.p2 = circumcenter
            else:
                #clear both side
                #clear the edges extend to the right of HP
                #Line(hole,ray.p1) or Line(hole,ray.p2) must ccw to Line(hole,bisector.p1)
                if ConvexHull.cross(circumcenter,ray[0].p1,SG_bisector.p1)<0:
                    #this means p1 is right to circumcenter,so replace p1 with circumcenter
                    if ray[0].p1.iscircumcenter == True:
                        recursive_discard_edge(ray[0],circumcenter,ray[0].p1,'left')
                    ray[0].p1 = circumcenter
                else:
                    if ray[0].p2.iscircumcenter == True:
                        recursive_discard_edge(ray[0],circumcenter,ray[0].p2,'left')
                    ray[0].p2 = circumcenter

                #clear the edges extend to the left of HP
                if ConvexHull.cross(circumcenter,ray[1].p1,SG_bisector.p1)>0:
                    #this means p1 is left to circumcenter,so replace p1 with circumcenter
                    if ray[1].p1.iscircumcenter == True:
                        recursive_discard_edge(ray[1],circumcenter,ray[1].p1,'right')
                    ray[1].p1 = circumcenter
                else:
                    if ray[1].p2.iscircumcenter == True:
                        recursive_discard_edge(ray[1],circumcenter,ray[1].p2,'right')
                    ray[1].p2 = circumcenter

        def nextPoint(pool,SG_bisector):
            ans = None
            first = True
            for candidate in pool:
                if candidate.line.avail== True and SG_bisector.p1 is not candidate.line.hole:
                    result = Line.intersect(candidate.line,SG_bisector)
                    if result is not None:
                        t = (result,candidate.point,candidate.line)
                        if first ==  True:
                            ans = t
                            first = False
                        else:
                            if t[0].y <= ans[0].y:
                                ans = t
            return ans

        upper_tangent,lower_tangent = VD.find_tangent(VDL,VDR)
        ul = (upper_tangent,lower_tangent)
        tangent[0].append(ul)

        HP = []
        SG = upper_tangent
        px = SG.p1
        py = SG.p2
        #p1 of upper_tangent belongs to VDL, and p2 belongs to VDR
        SG_bisector = Line.biSector(SG.p1,SG.p2)
        SG_bisector._p1 = SG.p1
        SG_bisector._p2 = SG.p2

        HP.append(SG_bisector)
        circumcenter = None

        firsttime = True
        newpl = defaultdict(list)

        while not (SG  == lower_tangent):
            #step4 as textBook

            #p1 of SG_bisector is fixed to upper position than p2
            if SG_bisector.p1.y > SG_bisector.p2.y:
                SG_bisector.p1,SG_bisector.p2 = SG_bisector.p2,SG_bisector.p1
            elif abs((SG_bisector.p1.y)-(SG_bisector.p2.y)) <= 0.00005:
                if SG_bisector.p1.x<SG_bisector.p2.x:
                    SG_bisector.p1,SG_bisector.p2 = SG_bisector.p2,SG_bisector.p1

            newpl[SG.p1].append(pair(SG_bisector,SG.p2))
            newpl[SG.p2].append(pair(SG_bisector,SG.p1))

            #orginally p1 is very far from painter,so we need to fix p1 to previous circumcenter
            if firsttime == False and circumcenter is not None:
                SG_bisector.p1 = circumcenter

            pll = px.related
            prl = py.related

            result_l = nextPoint(pll,SG_bisector)
            result_r = nextPoint(prl,SG_bisector)

            side = None
            ray = None
            #with biSector of pyz2 first,that is,VDR first
            if result_l is not None and result_r is not None:
                if abs(result_l[0].x-result_r[0].x) <= 0.05 and abs(result_l[0].y-result_r[0].y) <= 0.05:
                    #VDL.parent.msg = VDL.parent.msg+'both cd'+'\n'
                    SG = Line(result_l[1],result_r[1]);
                    circumcenter = result_l[0]
                    ray = (result_l[2],result_r[2])
                    side = 'both'
                elif result_l[0].y > result_r[0].y:
                    #VDL.parent.msg = VDL.parent.msg+'cd VDR'+'\n'
                    SG = Line(px,result_r[1])
                    circumcenter = result_r[0]
                    ray = result_r[2]
                    side = 'right'
                elif result_l[0].y < result_r[0].y:
                    #VDL.parent.msg = VDL.parent.msg+'cd VDL'+'\n'
                    SG = Line(result_l[1],py)
                    circumcenter = result_l[0]
                    ray = result_l[2]
                    side = 'left'
                else:
                    print 'confused...'
                    #print result_l,result_r
            else:
                if result_l is not None and result_r is None:
                    #VDL.parent.msg = VDL.parent.msg+'VDR is None,cd VDL'+'\n'
                    SG = Line(result_l[1],py)
                    circumcenter = result_l[0]
                    ray = result_l[2]
                    side = 'left'
                elif result_r is not None and result_l is None:
                    #VDL.parent.msg = VDL.parent.msg+'VDL is None,cd VDR'+'\n'
                    SG = Line(px,result_r[1])
                    circumcenter = result_r[0]
                    #print 'circumcenter',(circumcenter.x,circumcenter.y)
                    ray = result_r[2]
                    side = 'right'
                else:
                    #VDL.parent.msg = VDL.parent.msg+'both are None'+'\n'
                    #let SG be lower_tangent
                    SG = lower_tangent
                    SG_bisector = Line.biSector(SG.p1,SG.p2)
                    SG_bisector._p1 = SG.p1
                    SG_bisector._p2 = SG.p2
                    HP.append(SG_bisector)
                    continue

            if ray is not None:
                if not isinstance(ray,tuple):
                    ray.hole = circumcenter
                    t = (ray,SG_bisector,side,circumcenter)
                    if ray not in ray_list:
                        ray_list.add(ray)
                    clip_lines.append(t)
                else:
                    for r in ray:
                        r.hole = circumcenter
                        ray_list.add(r)
                    t = (ray,SG_bisector,side,circumcenter)
                    clip_lines.append(t)

            if circumcenter is not None:
                circumcenter.iscircumcenter = True
                #lower point is replaced by circumcenter
                SG_bisector.p2 = circumcenter


            #new SG
            px = SG.p1
            py = SG.p2
            SG_bisector = Line.biSector(SG.p1,SG.p2)
            SG_bisector._p1 = SG.p1
            SG_bisector._p2 = SG.p2

            HP.append(SG_bisector)
            firsttime = False
            #the end of while loop for HP


        if SG_bisector.p1.y > SG_bisector.p2.y:
            SG_bisector.p1,SG_bisector.p2 = SG_bisector.p2,SG_bisector.p1
        elif abs((SG_bisector.p1.y)-(SG_bisector.p2.y)) <= 0.00005:
            if SG_bisector.p1.x<SG_bisector.p2.x:
                SG_bisector.p1,SG_bisector.p2 = SG_bisector.p2,SG_bisector.p1


        newpl[SG.p1].append(pair(SG_bisector,SG.p2))
        newpl[SG.p2].append(pair(SG_bisector,SG.p1))

        for p in newpl.keys():
            for t in newpl[p]:
                p.related.append(t)

        if circumcenter is not None:
            SG_bisector.p1 = circumcenter


        #clip the unwanted lines
        VDL.parent.msg = VDL.parent.msg+ 'clip lines'+'\n'
        for t in clip_lines:
            ray = t[0]
            circumcenter = t[3]
            SG_bisector = t[1]
            side = t[2]
            discard_edges(ray,circumcenter,side,SG_bisector)

        #add new connected line
        s = 0
        for t in range(0,len(HP)-1):
            #need to add the intersected dividing chain
            HP[t].connected.append(HP[t+1])
            HP[t+1].connected.append(HP[t])
            #need to add the intersected ray
            if s  !=  len(clip_lines):
                if not isinstance(clip_lines[s][0],tuple):
                    HP[t].connected.append(clip_lines[s][0])
                    clip_lines[s][0].connected.append(HP[t])
                    HP[t+1].connected.append(clip_lines[s][0])
                    clip_lines[s][0].connected.append(HP[t+1])
                else:
                    r = clip_lines[s][0]
                    HP[t].connected.append(r[0])
                    r[0].connected.append(HP[t])
                    HP[t+1].connected.append(r[0])
                    r[0].connected.append(HP[t+1])

                    HP[t].connected.append(r[1])
                    r[1].connected.append(HP[t])
                    HP[t+1].connected.append(r[1])
                    r[1].connected.append(HP[t+1])

                    r[1].connected.append(r[0])
                    r[0].connected.append(r[1])
            s = s+1




        lines = []
        #lines = VDR.lines+VDL.lines+HP
        lines.append(VDR.lines)
        lines.append(VDL.lines)
        lines.append(HP)
        if VDL.parent.isstep_by_step == True:
            hp = []
            for h in HP:
                hp.append(Line(Point(h.p1.x,h.p1.y),Point(h.p2.x,h.p2.y)))
            VDR.parent.hp[0].append(hp)
        #VDR.parent.hp[0].append(copy.deepcopy(HP))
        range_points = (VDL.range_points[0],VDR.range_points[1])
        return VD(lines,range_points,VDR.parent)
        #return VD(lines,points)

    @staticmethod
    def find_tangent(VDL,VDR):
        pl = VDL.parent.points[VDL.range_points[1]]
        pr = VDR.parent.points[VDR.range_points[0]]

        #handle collinear point
        while not (VD.isupper_tangent(pl,pr,'left') and VD.isupper_tangent(pl,pr,'right')):
            while not VD.isupper_tangent(pl,pr,'left'):
                pl = pl.ccw
            while not VD.isupper_tangent(pl,pr,'right'):
                pr = pr.cw

        upper_tangent = Line(pl,pr)

        #VDL.parent.msg = VDL.parent.msg + 'upper_tangent = '+upper_tangent.p1.display+' '+upper_tangent.p2.display+'\n'

        pl = VDL.parent.points[VDL.range_points[1]]
        pr = VDR.parent.points[VDR.range_points[0]]

        while not (VD.islower_tangent(pl,pr,'left') and VD.islower_tangent(pl,pr,'right')):
            while not VD.islower_tangent(pl,pr,'left'):
                pl = pl.cw
            while not VD.islower_tangent(pl,pr,'right'):
                pr = pr.ccw


        lower_tangent = Line(pl,pr)

        #VDL.parent.msg =  VDL.parent.msg+'lower_tangent = '+lower_tangent.p1.display+' '+lower_tangent.p2.display+'\n'


        return (upper_tangent,lower_tangent)

    def find_convex(self):
        return ConvexHull(self).Andrew_monotone_chain(self.range_points)

    @staticmethod
    def isupper_tangent(pl,pr,pos):
        if pos == 'left':
            #because y is reverse in canvas,so we need to reverse the clockwise/clock,debug this is so diffcult...
            return ConvexHull.cross(pr,pl,pl.ccw) <= 0
        else:
            return ConvexHull.cross(pl,pr,pr.cw) >= 0
    @staticmethod
    def islower_tangent(pl,pr,pos):
        if pos == 'left':
            return ConvexHull.cross(pr,pl,pl.cw) >= 0
        else:
            return ConvexHull.cross(pl,pr,pr.ccw) <= 0
