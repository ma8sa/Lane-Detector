import os
import cv2
import numpy as np
from sklearn.cluster import DBSCAN

def color_array(size=25):

    color = [ list(np.random.choice(range(256), size=3)) for i in range(size) ]
    return np.array(color)


def mask_out(frame_no,th=80,path="./data/",mask_color=[153,153,153]):

    img = path + "Left/" + str(frame).zfill(6) + ".png"
    s_img = path + "17200/" + str(frame).zfill(6) + ".png"

    image = cv2.imread(img)
    seg_image = cv2.imread(s_img)

    mask = seg_image[:,:] == mask_color
    mask = mask[:,:,0] & mask[:,:,1] & mask[:,:,2]
    
    seg_image2 = np.zeros(mask.shape,dtype=np.uint8)
    seg_image2[mask] = 255 
    image[~mask] = [0,0,0]
    seg_image[~mask] = [0,0,0]

    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #image_grey[ image_grey[:,:] < th ] = 0
    #mx_c = np.amax(image_grey)
    #image_grey[image_grey[:,:] == 0] = 255 

    #mn_c = np.amin(image_grey)
    #image_grey[image_grey[:,:] == 255] = mn_c 
    
    #dif = mx_c - mn_c
    #factor = int(255/dif)

    #image_grey = (image_grey[:,:] - mn_c) * factor
    
    #th = 140
    #image_grey[ image_grey[:,:] > th ] = 255
    

    #blur = cv2.GaussianBlur(image_grey,(5,5),0)
    #ret3,th_image = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    return image,seg_image2,seg_image
    #return image,th_image,seg_image


def cluster_c(th_image,eps_=8,min_samples_=75):
    # larger eps means larger search radius meaning bigger cluster size
    #convert images to array of ones
    X = th_image == 255
    size = th_image.shape  
    X = [   [i,j]  for i,Y in enumerate(X) for j, x in enumerate(Y) if x  ]

    X = np.array(X)

    labels = DBSCAN(eps=eps_, min_samples=min_samples_).fit_predict(X)
    #labels = DBSCAN(eps=eps_ ).fit_predict(X)
    num_labels = np.amax(labels)

    clr_image = np.zeros((size[0],size[1],3), np.uint8)
    clus_image = np.zeros((size[0],size[1]), np.uint8)
    clr = color_array()
    mni=10

    for i,x in enumerate(X):
        if labels[i] == -1:
            continue
        mni = min(labels[i],mni)
        c = clr[labels[i]]
        clr_image[x[0],x[1]] = c
        clus_image[x[0],x[1]] = 255 - labels[i]



    for i in range(num_labels):
        y = 40
        y_l = 20
        x = i*20 + 10
        x_l = 10

        clr_image[x:x+x_l,y:y+y_l] = clr[i]


    return clr_image,clus_image



if __name__ == "__main__":
    
    data = "./data/Left"
    result_fol = "./pole_res/"
    im = os.listdir(data)

    im = [int(x.strip(".png")) for x in im]
    im.sort()

    for frame in im:

        print(" Processing frame : {}".format(frame))
        im,t_im,s_im=mask_out(frame)
        c_im,cls_im = cluster_c(t_im)
        cv2.imwrite( result_fol + str(frame).zfill(6) + "_m_test.png",im)
        cv2.imwrite( result_fol + str(frame).zfill(6) + "_s_test.png",s_im)
        cv2.imwrite( result_fol + str(frame).zfill(6) + "_c_test.png",c_im)
        cv2.imwrite( result_fol + str(frame).zfill(6) + "_cluster_test.png",cls_im)

        cv2.imwrite( result_fol + str(frame).zfill(6) +  "_b_test.png",t_im)
