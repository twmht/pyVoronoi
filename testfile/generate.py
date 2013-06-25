
class Point(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __eq__(self,other):
        return self.x ==  other.x and self.y == other.y
    def __hash__(self):
        return 41*self.x+self.y

if __name__ == '__main__':
    import random
    number = int(raw_input('How many points you want to generated? '))
    data = set()
    while len(data) < number:
        x = random.randint(0,610)
        y = random.randint(0,610)
        data.add(Point(x,y))
    filename = 'input_'+str(number)
    with open('input_'+str(number),'w') as out:
        out.write(str(number)+'\n')
        for p in data:
            out.write(str(p.x)+' '+str(p.y)+'\n')
        out.write('0')
    print filename,'was generated'
