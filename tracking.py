import numpy as np
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

class Cluster:

    def __init__(self,window,frame,load_fol="./pole_res/",save_fol="./pole_tracklets/",verbose=False):

        self.frame = frame
        self.window = window
        self.ver = verbose
        #self.load_fol = load_fol
        #self.save_fol = save_fol
        self.type = "POLE"
        if self.type == "POLE":
            self.load_fol = "./pole_res/"
            self.save_fol = "./pole_tracklets/"
        else:
            self.load_fol = "./res/"
            self.save_fol = "./tracklets/"

        print( "Frame= {}, Window= {} initializing, object {}".format(self.frame,self.window,self.type))
        self.cluster_array = self.create_cluster_array()
        self.flow_array = self.create_flow_array()
        self.cluster_image_array = self.create_image_array()
        self.tracks = self.create_tracklets_array() 
        self.tracklets = self.tracked()
        self.ref_points = self.create_reference_points()

    
    def create_cluster_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = self.load_fol# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = np.load(res_fol + "clusters_" + str(self.frame+i).zfill(6) + ".npy")
            test[i] = test[i][:-1]
        if self.ver:
           print("-----------------      cluster array created") 
           for i in test:
               print(len(i))
           input()
        return test 


    def create_flow_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = self.load_fol# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = np.load( str(self.frame+i) + "_frame.npy")
        if self.ver:
           print("-----------------      flow array created") 
#           for i in test:
#               print(i)
#               print(len(i))
#               input()
#
        return test 


    def create_image_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = self.load_fol# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = cv2.imread( self.load_fol + str(self.frame+i).zfill(6) + "_cluster_test.png",cv2.IMREAD_GRAYSCALE)
        if self.ver:
           print("-----------------      image array created") 
            
         #  for i in test:
         #      print(i)
         #      print(len(i))
         #      input()
        return test 


    # TODO Add reverse flow functionality
    def create_tracklets_array(self,th=5):# flow is frame1 + flow2 --> frame2
        test = [ [] for i in range(self.window -1)]
        scores = [ [] for i in range(self.window -1)]
        valid = [ [] for i in range(self.window -1)] # valid if true means that the net noe is a pseudo node

        
        for f,clust in enumerate(self.cluster_array[:-1]):

            clust = self.cluster_array[f]

            pseudo = False
            no_of_clusters = len(self.cluster_array[f+1])
            flow = self.flow_array[f+1]
            clust_img = self.cluster_image_array[f+1]

            for i,x in enumerate(clust):

                pseudo = False
                track_score = np.zeros(no_of_clusters)
                for y in x:
                    fx,fy = flow[y[0],y[1]]
                    # TODO not sure about this 
                    nx = int(y[0] + fy + 1)
                    ny = int(y[1] + fx + 1) 
                    
                    if nx < 0 or nx >= 720 or ny < 0 or ny >=1280:
                        continue

                    label = 255 - clust_img[nx,ny]

                    if label >= 255:
                        continue
                    else:
                        track_score[label] += 1



                score = -1
                if not len(track_score):
                    a = -1
                else:
                    a = np.argmax(track_score)

                    score = track_score[a]
                    scores[f].append(score)

                if score < th:
                    a = -1

                if a ==(-1):

                    # TODO add pseudo node 
                    new_x = []
                    for y in x:

                        fx,fy = flow[y[0],y[1]]
                        # TODO not sure about this 
                        nx = int(y[0] + fy + 1)
                        ny = int(y[1] + fx + 1) 
                        
                        if nx < 0 or nx >= 720 or ny < 0 or ny >=1280:
                            continue

                        new_x.append([nx,ny])

                    if len(new_x) > th:
                       a = len(self.cluster_array[f+1])
                       if no_of_clusters == 0:
                          self.cluster_array[f+1] = [new_x ]
                          #self.cluster_array[f+1] = np.append(self.cluster_array[f+1],[[1]])
                       else:
                          self.cluster_array[f+1] = np.append(self.cluster_array[f+1],[[1]])
                          self.cluster_array[f+1][-1] = new_x
                       #self.cluster_array[f+1] = np.append(self.cluster_array[f+1],new_x)
                       # Copy x to next frame
                       # update a 
                       # 
                       pseudo = True 

                test[f].append(a)
                valid[f].append(pseudo)
            

        if self.ver:
           print("-----------------      Tracklets created") 
           count = 0
           for i,j,k in zip(test,valid,scores):
               print("___________: ",count) 
               print(i)
               print(j)
               print(k)
               print(len(i))
               count += 1
               input()

        for i,x in enumerate(test[0]):# iterating over clusters
                st = i
                cur = st
                pseudo_count = 0

                for f in range(self.window-1):
                   # print(f,cur)
                    if valid[f][cur]:
                       pseudo_count += 1

                    cur = test[f][cur]
                if pseudo_count > 3:
                    test[0][st] = -1





        if self.ver:
           print("-----------------      Tracklets created") 
           for i in test:
               print(i)
               print(len(i))
               input()
        return test

    def tracked(self): # return perfect list with all the valid tracked clusters

        cur_id = 4
        tracked = [ [] for i in range(self.window )]
        
        for i,clust in enumerate(self.cluster_array[0]):

            # see if valid or not 

            valid = True
            cur_id = i
            test = []
            for f,clust in enumerate(self.cluster_array):
               test.append(clust[cur_id])

               if len(clust[cur_id]) == 0:
                   print("tracked")
                   print(f,cur_id)
                   input()
               if f < self.window-1:
                  cur_id = self.tracks[f][cur_id]

               if cur_id == (-1):
                  valid = False
                  break
            # TODO handle occlusion here
            if valid:
                tracked.append(test)


            #if valid
            #add to list
        if self.ver:
           print("-----------------      Tracklets tracked") 
           for i in tracked:
               print(i)
               print(len(i))
               input()

        return tracked

        for f,clust in enumerate(self.cluster_array):
            im = np.zeros((720,1280), dtype=np.uint8)
            
            for x in (clust[cur_id]):
                #plot images poiints
                im[x[0],x[1]] = 255
            if f < self.window-1:
               cur_id = self.tracks[f][cur_id]
            cv2.imwrite(str(f).zfill(3) + "_test.png",im)
        
    def create_reference_points(self):
        ref_points = [ [] for i in range(self.window) ]

        for i in self.tracklets:
            test = []
            for clust in i:
                rx = 0.
                ry = 0.
                mx = 0
                my = 0
                mnx = 10000
                mny = 10000
                count = 0.
                for p in clust:
                    rx += p[0]
                    ry += p[1]
                    count += 1
                    mx = max(p[0],mx)
                    my = max(p[1],my)
                    mnx = min(p[0],mnx)
                    mny = min(p[1],mny)

                rx = (rx/count)
                ry = (ry/count)
                # TODO change here , add a switch statement based on type of object
               # print(mx,mnx)
               # print(my,mny)
               # input()
                a = mx-mnx
                b = my-mny
                l = max(a,b)
                b = min(a,b)
              #  print(l,b,l/b)
              #  input()
                if self.type == "POLE":
                    test.append([mx,ry])
                else:
                    test.append([rx,ry])
            ref_points.append(test)

        if self.ver:
           print("-----------------      reference points created ") 
           for i in ref_points:
               print(i)
               print(len(i))
               input()
        return ref_points


    def save_ref_array(self,viz=True):# refence points imnages and arrays as npy
        #if not os.path.exists(res_fol):
         #       os.makedirs(res_fol)
        res_fol = self.save_fol
        np.save(res_fol + str(self.frame).zfill(6) + "_tracks.npy",np.array(self.ref_points))
        if self.ver: 
           print("-----------------      saving viziualitaions results ")
        if viz:
            images = [ np.zeros((720,1280,3), dtype=np.uint8) for i in range(self.window) ]
            ln_images = [ np.zeros((720,1280,3), dtype=np.uint8) for i in range(self.window) ]

            font                   = cv2.FONT_HERSHEY_SIMPLEX
            fontScale              = 1
            fontColor              = (255,255,255)
            lineType               = 2

            for clust,track in enumerate(self.tracklets):
                for i,p in enumerate(track):

                    for px in p:
                        ln_images[i][px[0],px[1]] = color[clust]

            for clust,track in enumerate(self.ref_points):
                for i,ix in enumerate(track):

                      cv2.putText(images[i],str(clust), 
                                  (int(ix[1]),int(ix[0])), 
                                  font, 
                                  fontScale,
                                  fontColor,
                                  lineType)

            for i,im in enumerate(images):

                cv2.imwrite(res_fol + str(self.frame).zfill(6) + "_" + str(i).zfill(2) + "cn.png",images[i])
                cv2.imwrite(res_fol + str(self.frame).zfill(6) + "_" + str(i).zfill(2) + "ln.png",ln_images[i])





#TODO check if tracking is corrct 
#TODO check if arrays were correctly made
#TODO add argparse
#TODO add reverse flow
#TODO add oclusion and cluster breaking issues
#TODO add points in tracked tracking images 
#TODO make sure directional oreder is correct while saveing images
if __name__ == "__main__":
   window = 10
   data = "./data/Left"
   im = os.listdir(data)

   im = [int(x.strip(".png")) for x in im]
   im.sort()
   #TODO add argparse
   for frame in im[1169:1800]:
       tracklet = Cluster(window,frame)
       tracklet.save_ref_array()
       del tracklet

