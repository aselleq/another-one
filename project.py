@ -0,0 +1,16 @@
def days (y1,m1,d1,y2,m2,d2):
    if y2 > y1 :
        return days (y2,m2,d2,y1,m1,d1)
    if d2 > d1 :
        return days (y1,m1-1,d1+30,y2,m2,d2)
    if m2 > m1 :
        return days (y1-1,m1+12,d1,y2,m2,d2)
    return ((y1-y2)*356 + (m1-m2)*30 + (d1-d2))

y1 = input ("enter y1 : ")
m1 = input ("enter m1 : ")
d1 = input ("enter d1 : ")
y2 = input ("enter y2 : ")
m2 = input ("enter m2 : ")
d2 = input ("enter d2 : ")
print (days (y1,m1,d1,y2,m2,d2))
