import numpy as np
import cv2
import os


class Cluster:

    def __init__(self,window,frame):

        self.frame = frame
        self.window = window
        print( " intializing tracklets for frame {}, window Length {}".format(self.frame,self.window))
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
        print(" cluster array created") 
        return test 


    def create_flow_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = "./res/"# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = np.load( str(self.frame+i).zfill(5) + "_frame.npy")
        print(" flow array created") 
        return test 


    def create_image_array(self):
        test = [ [] for i in range(self.window) ]
        res_fol = "./res/"# TODO change it to make ti portable
        for i in range(self.window):
            test[i] = cv2.imread( "./res/" + str(self.frame+i).zfill(6) + "_cluster_test.png",cv2.IMREAD_GRAYSCALE)
        print(" image array created") 
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


                a = np.argmax(track_score)
                score = track_score[a]
                scores[f].append(score)
                if score < th:
                    a = -1
                test[f].append(a)

            print(test[f])
            print(scores[f])

        print(" Tracklets created") 
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
        print(" Tracklets tracked") 

        return tracked

        for f,clust in enumerate(self.cluster_array):
            im = np.zeros((720,1280), dtype=np.uint8)
            
            for x in (clust[cur_id]):
                #plot images poiints
                im[x[0],x[1]] = 255
            print(cur_id)
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

        print(" reference points created ") 
        return ref_points


    def save_ref_array(self,viz=True,res_fol="./tracklets/"):# refence points imnages and arrays as npy
        print(" in here ")
        #if not os.path.exists(res_fol):
         #       os.makedirs(res_fol)

        #np.save(res_fol + str(self.frame).zfill(6) + "_tracks.npy",self.ref_points)
          
        print(" saving viziualitaions results ")
        if viz:
            images = [ np.zeros((720,1280,3), dtype=np.uint8) for i in range(self.window) ]

            font                   = cv2.FONT_HERSHEY_SIMPLEX
            fontScale              = 2
            fontColor              = (255,255,255)
            lineType               = 2


            for clust,track in enumerate(self.ref_points):
                for i,ix in enumerate(track):

                      cv2.putText(images[i],str(clust).zfill(2), 
                                  (int(ix[0]),int(ix[1])), 
                                  font, 
                                  fontScale,
                                  fontColor,
                                  lineType)

            for i,im in enumerate(images):

                cv2.imwrite(res_fol + str(self.frame).zfill(6) + "_" + str(i).zfill(2) + ".png",im)





#TODO check if tracking is corrct 
#TODO check if arrays were correctly made

    

if __name__ == "__main__":
     
   tracklet = Cluster(5,17201)
   tracklet.save_ref_array()
