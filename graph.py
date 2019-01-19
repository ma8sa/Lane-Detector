import numpy as np
import scipy.sparse as sp
import cv2

import os

color = [
       [55, 181, 57],
       [153, 108, 6],
       [112, 105, 191],
       [89, 121, 72],
       [190, 225, 64],
       [206, 190, 59],
       [81, 13, 36],
       [115, 176, 195],
       [161, 171, 27],
       [135, 169, 180],
       [29, 26, 199],
       [102, 16, 239],
       [242, 107, 146],
       [156, 198, 23],
       [49, 89, 160],
       [68, 218, 116],
       [11, 236, 9],
       [196, 30, 8],
       [121, 67, 28],
       [0, 53, 65],
       [146, 52, 70],
       [226, 149, 143],
       [151, 126, 171],
       [194, 39, 7],
       [205, 120, 161],
       [212, 51, 60],
       [211, 80, 208],
       [189, 135, 188],
       [54, 72, 205],
       [103, 252, 157],
       [124, 21, 123],
       [19, 132, 69],
       [195, 237, 132],
       [94, 253, 175],
       [182, 251, 87],
       [90, 162, 242] ]


def get_GT(seq):
    assist = True
    gt = 0
    seq = np.array(seq)
    seq = (seq[:,2])

    
    # case 0
    x = seq[0]
    test =  np.array([seq == x] )

    if test.all():
        return 0,False
    # case 1
    x = seq[0]
    cx = x
    ix = x
    change = 0
    c_at = 0
    for j,i in enumerate(seq):
        if ix != i:
            change += 1
            cx = i
            ix = i
            c_at = j
    if change == 1 and c_at >= 1 and c_at <= 9:# threshold for how long should the change be

        # case 1
        if x == 0 and cx == 1: # FL -> FR = MAR
            return 3,False
        if x == 0 and cx == 2: # FL -> BL = MB
            return 2,False
        if x == 0 and cx == 3: # FL -> BR = MB
            return 2,False

        if x == 1 and cx == 0: # FR -> FL = MAL
            return 4,False
        if x == 1 and cx == 2: # FR -> BL = MB
            return 2,False
        if x == 1 and cx == 3: # FR -> BR = MB
            return 2,False

        if x == 2 and cx == 1: # BL -> FR = MA
            return 1,False
        if x == 2 and cx == 0: # BL -> FL = MA
            return 1,False
        if x == 2 and cx == 3: # BL -> BR = MAR
            return 3,False

        if x == 3 and cx == 1: # BR -> FR = MA
            return 1,False
        if x == 3 and cx == 2: # BR -> BL = MAL
            return 4,False
        if x == 3 and cx == 0: # BR -> FL = MA 
            return 1,False
    else:
        return 0,True


def find_relation(p,q):
    a = p[0] - q[0]
    b = p[1] - q[1]
    if a > 0 and b > 0:
        return 1

    if a > 0 and b <= 0:
        return 0

    if a <= 0 and b > 0:
        return 3

    if a <= 0 and b <= 0:
        return 2

    print("WTF")
    input()



def read_tracklets(fol,frame,window=10):
    #print("Frame : {} ".format(frame))
    test = np.load(fol + str(frame).zfill(6) + "_tracks.npy")# lanemarkings
    cars = np.load("./car_tracks/" + str(frame).zfill(6) + "_tracks.npy")# cars 
    lanes = [ i for i in test if len(i) > 0 ] 
    cars = [ i for i in cars if len(i) > 0 ]
    poles = []

    relations = { 0 : " Forward Left ",
                  1 : " Forward Right ",
                  2 : " Backward Left ",
                  3 : " Backward Right ",
                  }

    stuff = { 0 : " Cars ",
              1 : " Lane ",
              2 : " Pole ",
                 }
    
    objects = lanes + cars + poles


    len_objects = (len(objects))

      
    lane_idx = list(range(len(lanes)))
    len_lane = len(lane_idx) 
    car_idx = list(range(len_lane,len_lane+len(cars))) 
    len_car = len(car_idx)
    pole_idx = list(range(len_lane+len_car+1,len_lane+len_car+1+len(poles))) 

    vv = [ 0 for i in range(len(objects)) ]
    for i in lane_idx:
        vv[i] = 1
    for i in car_idx:
        vv[i] = 0
    for i in pole_idx:
        vv[i] = 2


    GT = [ ]
    GT_n = [ ]
    input_data = []
    GT_labels = { 0 : "No change",
                      1 : "Moved Ahead",
                      2 : "Moved Behind",
                      3 : "Moved across left",
                      4 : "Moved across right",
                     -1 : " requires GT "
                      }

    

    count = 0
    ind_x =[]
    for i in objects:
        ind_x.append(i[0])

    for i,clust in enumerate(objects):
        for j,clust2 in enumerate(objects):
            test = []
            test2 = []

            if i == j or vv[i]*vv[j] > 0: # to get rid of self edges and edges between cars and edges
               continue

           # defi = window - len(clust)
           # last = clust[-1]
           # for i in range(defi):
           #     clust.append(last)

           # defi = window - len(clust2)
           # last = clust2[-1]
           # for i in range(defi):
           #     clust2.append(last)

            for frame in range(window):
                obj = stuff[vv[i]] + str(i).zfill(2)
                sub = stuff[vv[j]] + str(j).zfill(2)
                obj_p = clust[frame]
                sub_p = clust2[frame]

                x = find_relation(obj_p,sub_p)
                
                rel = relations[x]
                


                test.append(obj+rel+sub)
                test2.append([vv[i],i,x,vv[j],j])
                
            gt,assist = get_GT(test2)
            
            if gt < 0:
               for t in test:
                   print(t)

               print(" GT {} , GT_label {} , ASSIST {} ".format(gt,GT_labels[gt],assist))
               input()

            if assist:
                for t in test:
                    print(t)
                print(GT_labels.items())

                x = int(input(" ***********************   enter ground truth for realtions: "))
                #x = -1
                GT.append(GT_labels[x])
                GT_n.append(x)

            else:
                GT.append(GT_labels[gt])
                GT_n.append(gt)

            input_data.append(test2)
    return input_data,GT_n,vv,ind_x
                   

def create_adj(input_data,GT,vv,idx,frame):
    num_obj = len(vv)
    adj = [ np.zeros((num_obj,num_obj)) for i in range(5) ] # because we have five realtions TODO check wehter to use eye or zzeros

    GT_labels = { 0 : "No change",
                      1 : "Moved Ahead",
                      2 : "Moved Behind",
                      3 : "Moved across left",
                      4 : "Moved across right",
                     -1 : " requires GT "
                      }

    stuff = { 0 : " Cars ",
              1 : " Lane ",
              2 : " Pole ",
                 }
    cars = 0
    lanes = 0
    rel_n = [ 0 for i in range(6) ]
    vertex = [ [] for i in range(num_obj)]
  
  
    # read image 
    fol = "./data/Left/"
    im = cv2.imread(fol + str(frame).zfill(6) + ".png")
    im = im/1.5


    vv = np.array(vv)
    GT = np.array(GT)

    cars = len(vv[ vv == 0])
    lanes = len(vv[ vv == 1])

    for i in range(6):
        rel_n[i] = len(GT[ GT == (i-1) ])

    for i,d in enumerate(input_data):
    #    print(d)
        obj = d[0][1]
        sub = d[0][-1] 
        rel = GT[i]
    #    print(obj,sub,rel)
        if rel >= 0:
           adj[rel][obj,sub] = 1
           vertex[obj].append(str(rel) + GT_labels[rel] + stuff[vv[sub]] + str(sub))

#    for a in adj:
#        print(a)
#        input()

    node_labels = { 0 : "static",
                    1 : "moving forward",
                    2 : "moving back",
                    3 : "changing lane",
                    }
    A = [ sp.csr_matrix(a) for a in adj ]
    print("saving stuff")
    np.save("./Adj/" + str(frame).zfill(6) + "_Adj.npy",A)

    node_GT = [0 if v > 0 else -1 for v in vv]

    for i,_ in enumerate(node_GT):

       if node_GT[i] < 0:
           node_GT[i] = 2
           tmp = []
           for j in vertex[i]:
               tmp.append(int(j[0]))
           tmp = np.array(tmp)
           tmp =  tmp == 0 
           if (tmp.all()):
               x = 0
           else:
               for j in vertex[i]:
                   print(j[1:])
               print(node_labels.items())
               x = int(input(" enter ground truth for this node: "))
           node_GT[i] = x


    np.save("./Adj/" + str(frame).zfill(6) + "_y.npy",node_GT)
    # color the image here
    GT_color = [ 
            (0,0,255),
            (255,0,255),
            (0,255,255),
            (0,255,0)
            ]

    clr = [ tuple(c) for c in color ]
    for i,ii in enumerate(node_GT):
#        print(idx[i])
        cv2.circle(im,(int(idx[i][1]),int(idx[i][0])),7,GT_color[ii],-1)

    for i,d in enumerate(input_data):

        obj = d[0][1]
        sub = d[0][-1] 
        rel = GT[i] + 1

        if obj > sub:
            o =( int(idx[obj][1]) + 2,int(idx[obj][0]) + 2 )
            s =( int(idx[sub][1]) + 2,int(idx[sub][0]) + 2 )

        else:
            o =( int(idx[obj][1]) - 2,int(idx[obj][0]) - 2 )
            s =( int(idx[sub][1]) - 2,int(idx[sub][0]) - 2 )

        cv2.line(im,o,s,clr[rel],2)

    cv2.imwrite("./graph_res/" + str(frame).zfill(6) + ".png",im)
    


    return cars,lanes,rel_n
    # draw the centers


    # first dim the image
    # save



if __name__ == "__main__":
    
    # read the npy
    data = "./tracklets/"
    im = os.listdir(data)

    im = [int(x.strip("_tracks.npy")) for x in im if ".npy" in x ]
    im.sort()
    cars=0
    lanes=0
    rel = np.array([ 0 for i in range(6) ])
    for i in im:
        input_data,GT,vv,idx = read_tracklets(data,i)
        c,l,r = create_adj(input_data,GT,vv,idx,i)

        cars += c
        lanes += l
        t_r = 0
        for j,x in enumerate(r):
            rel[j] += x
            t_r  += rel[j]

        t_r = t_r/100 
        
        print("\n\n Frame {}, cars {}, lanes {}, relations {}\n".format(i,cars,lanes,rel))
    # sxtract number of objects and window length
    # makes list of all the objects pairs to be tracked
    # preview the frame and there relations
    # ask for ground truth( make the ground truth rules for it)
    # make the final graph

    
