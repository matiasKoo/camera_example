import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

'''
luodaan 320 x 240 resoluutioinen kuva np-taulukolla.
0=musta, 1=valkone
kuvaan tulee keskelle pystyyn ja keskelle vaakaan sopivan välimatkan välein palloja.
40px välein.
5 pystyyn 7 vaakaan
blopin halkasija: 7-10px
jatkokehitys: blop-risti generoidaan eri paikkoihin.
'''

img = np.zeros([24,32], dtype=int)


mid_col=[]
count=0
for x in img[1]:
    if(count!=15):
        mid_col.append(0)
    else:
        mid_col.append(1)
    count+=1
#mid_col=np.array(mid_col, dtype=int)   # 0,0,...,1,...,0,0 -rivi


count=0
mid_row=[]
for x in img[1]:
    if(count!=3):
        mid_row.append(0)
    else:
        mid_row.append(1)
        count=-1
    count+=1
#mid_row=np.array(mid_row, dtype=int)

count=0
other_c=0

#print(mid_row,'\n',mid_col,'\n\n')

for i in img:
    if(count==11):
        np.copyto(img[count],mid_row)
        other_c= 0
    elif(other_c==3):
        np.copyto(img[count],mid_col)
        other_c= 0
    else:
        other_c+=1
    count+=1


img=np.array(img)
print(img)




