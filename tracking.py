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

    def __init__(self,window,frame,verbose=False):

        self.frame = frame
        self.window = window
        self.ver = verbose
        print( "Frame= {}, Window= {} initializing".format(self.frame,self.window))
        self.cluster_array = self.create_cluster_array()
        self.flow_array = self.create_flow_array()
        self.cluster_image_array = self.create_image_array()
        self.tracks = self.create_tracklets_array() 
        self.tracklets = self.tracked()
        self.ref_points = self.create_reference_points()

    
    def create_cluster_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = "./res/"# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = np.load(res_fol + "clusters_" + str(self.frame+i).zfill(6) + ".npy")
            test[i] = test[i][:-1]
        if self.ver:
           print("-----------------      cluster array created") 
        return test 


    def create_flow_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = "./res/"# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = np.load( str(self.frame+i).zfill(5) + "_frame.npy")
        if self.ver:
           print("-----------------      flow array created") 
        return test 


    def create_image_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = "./res/"# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = cv2.imread( "./res/" + str(self.frame+i).zfill(6) + "_cluster_test.png",cv2.IMREAD_GRAYSCALE)
        if self.ver:
           print("-----------------      image array created") 
        return test 


    # TODO Add reverse flow functionality
    def create_tracklets_array(self,th=10):# flow is frame1 + flow2 --> frame2
        test = [ [] for i in range(self.window -1)]
        scores = [ [] for i in range(self.window -1)]
        
        for f,clust in enumerate(self.cluster_array[:-1]):
            for i,x in enumerate(clust):
                flow = self.flow_array[f+1]
                clust_img = self.cluster_image_array[f+1]

                no_of_clusters = len(self.cluster_array[f+1])
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
                    print(track_score)
                    print(" cluster {} , frame {} , frame id {}".format(i,f,self.frame))
                else:
                    a = np.argmax(track_score)

                    score = track_score[a]
                    scores[f].append(score)
                if score < th:
                    a = -1
                test[f].append(a)



        if self.ver:
           print("-----------------      Tracklets created") 
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
               if f < self.window-1:
                  cur_id = self.tracks[f][cur_id]

               if cur_id == (-1):
                  valid = False
                  break

            if valid:
                tracked.append(test)


            #if valid
            #add to list
        if self.ver:
           print("-----------------      Tracklets tracked") 

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
                count = 0.
                for p in clust:
                    rx += p[0]
                    ry += p[1]
                    count += 1

                rx = (rx/count)
                ry = (ry/count)
                test.append([rx,ry])
            ref_points.append(test)

        if self.ver:
           print("-----------------      reference points created ") 
        return ref_points


    def save_ref_array(self,viz=True,res_fol="./tracklets/"):# refence points imnages and arrays as npy
        #if not os.path.exists(res_fol):
         #       os.makedirs(res_fol)

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

   for frame in im[1:]:

       tracklet = Cluster(window,frame)
       tracklet.save_ref_array()
       del tracklet

