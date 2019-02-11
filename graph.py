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

def eq_dis(a,b):
    d = (a[0]-b[0])**2 + (a[1]-b[1])**2
    return np.sqrt(d)

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

    if change == 1 and c_at >= 2 and c_at <= 7:# threshold for how long should the change be

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

    #make it a bit loos efor forward backward 
    if change == 1 and c_at >= 2 and c_at <= 8:# threshold for how long should the change be

        if x == 0 and cx == 2: # FL -> BL = MB
            return 2,False
        if x == 0 and cx == 3: # FL -> BR = MB
            return 2,False

        if x == 1 and cx == 2: # FR -> BL = MB
            return 2,False
        if x == 1 and cx == 3: # FR -> BR = MB
            return 2,False

        if x == 2 and cx == 1: # BL -> FR = MA
            return 1,False
        if x == 2 and cx == 0: # BL -> FL = MA
            return 1,False

        if x == 3 and cx == 1: # BR -> FR = MA
            return 1,False
        if x == 3 and cx == 0: # BR -> FL = MA 
            return 1,False

        else:
            return 0,False

    elif change <= 2:
        return 0,False
    else:
        return 5,False


def find_relation(p,q):
    a = p[0] - q[0]
    b = p[1] - q[1]
    th = 0
    if a > th and b > th:
        return 1

    if a > th and b <= th:
        return 0 

    if a <= th and b > th:
        return 3

    if a <= th and b <= th:
        return 2
    else:
        return 1

    print("WTF")
    input()



def read_tracklets(fol,fol2,frame,window=10,rel_dist=720):
    #print("Frame : {} ".format(frame))
    test = np.load(fol + str(frame).zfill(6) + "_tracks.npy")# lanemarkings
    test2 = np.load(fol2 + str(frame).zfill(6) + "_tracks.npy")# lanemarkings
    cars = np.load("./cars_new/" + str(frame).zfill(6) + "_tracks.npy")# cars 
    #cars = np.load("./cars_27/" + str(frame).zfill(6) + "_tracks.npy")# cars 
    lanes = [ i for i in test if len(i) > 0 ] 
    cars = [ i for i in cars if len(i) > 0 ]
    poles = [ i for i in test2 if len(i) > 0 ] 
    #poles = []

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
    pole_idx = list(range(len_lane+len_car,len_lane+len_car+len(poles))) 

    print(pole_idx)

    vv = [ 0 for i in range(len(objects)) ]
    for i in lane_idx:
        vv[i] = 1
    for i in car_idx:
        vv[i] = 0
    for i in pole_idx:
        print(i)
        vv[i] = 2

    GT = [ ]
    GT_n = [ ]
    input_data = []

    GT_labels = {     0 : "No change",
                      1 : "Moved Ahead",
                      2 : "Moved Behind",
                      3 : "Moved across left",
                      4 : "Moved across right",
                      5 : "Fluctuating",
                     -1 : " requires GT "
                      }

    count = 0
    ind_x =[]

    for i in objects:
        ind_x.append(i[0])

    max_dis = False 

    for i,clust in enumerate(objects):
        for j,clust2 in enumerate(objects):
            test = []
            test2 = []

            if i == j or vv[i]*vv[j] > 0: # to get rid of self edges and edges between cars and edges
               continue

            if eq_dis(clust[0],clust2[0]) > rel_dist and  eq_dis(clust[-1],clust2[-1]) > rel_dist:
                max_dis = True

            defi = window - len(clust)
            last = clust[-1]
            for i in range(defi):
                clust.append(last)

            defi = window - len(clust2)
            last = clust2[-1]
            for i in range(defi):
                clust2.append(last)

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

            if gt == 0 and max_dis:
                continue
            
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
    adj = [ np.zeros((num_obj,num_obj)) for i in range(6) ] # because we have five realtions TODO check wehter to use eye or zzeros

    SAVE = False
    GT_labels = { 
                      0 : "No change",
                      1 : "Moved Ahead",
                      2 : "Moved Behind",
                      3 : "Moved across left",
                      4 : "Moved across right",
                      5 : "Fluctuating",
                     -1 : " requires GT "
                }

    stuff = {
              0 : " Cars ",
              1 : " Lane ",
              2 : " Pole ",
            }

    cars = 0
    lanes = 0
    rel_n = [ 0 for i in range(7) ]
    vertex = [ [] for i in range(num_obj)]
  
  
    # read image 
    fol = "./data/Left/"
    im = cv2.imread(fol + str(frame).zfill(6) + ".png")
    im = im/1.5


    vv = np.array(vv)
    GT = np.array(GT)

    cars = len(vv[ vv == 0])
    lanes = len(vv[ vv == 1])

    for i in range(7):
        rel_n[i] = len(GT[ GT == (i-1) ])

    for i,d in enumerate(input_data):
    #    print(d)
        obj = d[0][1]
        sub = d[0][-1] 
        rel = GT[i]
        if rel >= 0:
           adj[rel][obj,sub] = 1
           vertex[obj].append(str(rel) + GT_labels[rel] + stuff[vv[sub]] + str(sub))

#    for a in adj:
#        print(a)
#        input()

    node_labels = {
                    0 : "parked",
                    1 : "moving towards us",
                    2 : "moving away",
                    3 : "overtaking car",
                    4 : "changing lane",
                  }


    GT_color = [ 
                (0,0,255),
                (255,0,255),
                (0,255,255),
                (0,255,0),
                (255,0,255)
               ]

    A = [ sp.csr_matrix(a) for a in adj ]
    print("saving stuff")
    if not (len(idx) == num_obj) :
       print( " wtf {}, {} ".fomat(len(idx),num_obj))
       input()

    if SAVE:
       cv2.imwrite("./Adj/" + str(frame).zfill(6) + "_im.png",im)

       np.save("./Adj/" + str(frame).zfill(6) + "_Adj.npy",A)
       np.save("./Adj/" + str(frame).zfill(6) + "_IDX.npy",idx)

    node_GT = [0 if v > 0 else -1 for v in vv]
#TODO remove edge/nodes and show indexed image inplace 
    
    for i,ii in enumerate(node_GT):
#        print(idx[i])
        a = int(idx[i][1])
        b = int(idx[i][0])
    
        cv2.circle(im,(a,b),7,GT_color[ii],-1)

        if ii < 0:
           font = cv2.FONT_HERSHEY_SIMPLEX
           cv2.putText(im,str(i).zfill(2),(a,b), font, 2,(255,255,255),2,cv2.LINE_AA)

    #cv2.imwrite("./graph_res/" + str(frame).zfill(6) + "pre.png",im)
    for i,_ in enumerate(node_GT):
       if node_GT[i] < 0:
           node_GT[i] = 2
           tmp = []
           for j in vertex[i]:
               tmp.append(int(j[0]))
           print( " node number : {} ".format(i))
           print( tmp) 
           tmp = np.array(tmp)
           tmp =  tmp == 0 
           if (tmp.all()):
               x = 0
           else:
               #for j in vertex[i]:
               #    print(j[1:])
               print(node_labels.items())
               print( " node number : {} ".format(i))
               x = 2
               #x = int(input(" enter ground truth for this node: "))
           node_GT[i] = x
    if SAVE:
       np.save("./Adj/" + str(frame).zfill(6) + "_y.npy",node_GT)
       np.save("./Adj/" + str(frame).zfill(6) + "_X.npy",vv)
    #np.save("./Adj/" + str(frame).zfill(6) + "_y.npy",Tnode_GT)
    # color the image here
    clr = [ tuple(c) for c in color ]
    for i,ii in enumerate(node_GT):
        cv2.circle(im,(int(idx[i][1]),int(idx[i][0])),7,GT_color[ii],-1)

    print("drawing edges ")
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

        #if not(rel == 1):
        cv2.line(im,o,s,clr[rel],2)

    cv2.imwrite("./graph_res/" + str(frame).zfill(6) + ".png",im)
    


    return cars,lanes,rel_n
    # draw the centers


    # first dim the image
    # save



if __name__ == "__main__":
    
    # read the npy
    data = "./tracklets/"
    data2 = "./pole_tracklets/"
    im = os.listdir(data)

    im = [int(x.strip("_tracks.npy")) for x in im if ".npy" in x ]
    im.sort()

    cars=0
    lanes=0
    rel = np.array([ 0 for i in range(7) ])
    print( " TOTAL FRAME : {} ".format(len(im)))
    st_frame = int(input(" strat frame ")) 
    st_frame = 500 
    for i in im[:500]:
        print("\n\nFRAME : {} \n".format(i))
        input_data,GT,vv,idx = read_tracklets(data,data2,i)
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

    
