import sys
sys.path.append('../pyflow/')
import pyflow
import os
import numpy as np
import cv2

# calculate flow for tracking 

def calculate_flow(im1,im2):
    
    im1 = im1.astype(float) / 255.
    im2 = im2.astype(float) / 255.

    alpha = 0.012
    ratio = 0.75
    minWidth = 20
    nOuterFPIterations = 7
    nInnerFPIterations = 1
    nSORIterations = 30
    colType = 0  # 0 or default:RGB, 1:GRAY (but pass gray image with shape (h,w,1))

    u, v, im2W = pyflow.coarse2fine_flow(
                im1, im2, alpha, ratio, minWidth, nOuterFPIterations, nInnerFPIterations,
                    nSORIterations, colType)

 
    
    flow = np.concatenate((u[..., None], v[..., None]), axis=2)
    np.save(str(frame)+ '_frame.npy', flow)
    return flow,im2W


def save_flow(flow,frame,im,im2W,wrap_im):
    hsv = np.zeros(im.shape, dtype=np.uint8)
    hsv[:, :, 0] = 255
    hsv[:, :, 1] = 255
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite( str(frame).zfill(6) + '_flow.png', rgb)
    #cv2.imwrite( str(frame).zfill(6) + '_wraped.png', im2W[:, :, ::-1] * 255)
    cv2.imwrite( str(frame).zfill(6) + '_wraped.png', im2W[:, :, :] * 255)
    cv2.imwrite( str(frame).zfill(6) + '_wrap.png', wrap_im)

def wrap_image(im1,im2,flow):# to check how flopw works
    
    size = im1.shape
    wrap_im = np.zeros_like(im2)

    for i,x in enumerate(flow):
        for j,y in enumerate(x):
            # i is 720
            # j is 1200
            nx = i + y[1]
            ny = j + y[0]

            if ny < 0 or ny >= 1200 or nx < 0 or nx >= 720:
                continue

            wrap_im[int(nx),int(ny)] = im1[i,j]

             


    return wrap_im
    input()


def cluster():
# assemble them in clusters
# track it using optical flow
# single color coding scheme
# assign reference points to clusters



if __name__ == "__main__":

     data = "./data/Left/"
     result_fol = "./res/"
     im = os.listdir(data)

     im = [int(x.strip(".png")) for x in im]
     im.sort()

     for frame in im[1:]:# bcuz flow is (frame-1) --> (frame)
         im1 = cv2.imread(data + str(frame-1).zfill(6) + ".png")
         im2 = cv2.imread(data + str(frame).zfill(6) + ".png")

         flow,im2W = calculate_flow(im1,im2) 
         wrap_im = wrap_image(im1,im2,flow)
         save_flow(flow,frame,im2,im2W,wrap_im)


