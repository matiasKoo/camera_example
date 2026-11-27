import cv2 as cv
import numpy as np
import imgproc_test as imp
from numpy.polynomial.polynomial import Polynomial #lol
import matplotlib.pyplot as plt
#import matplotlib.ticker as tck
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist, squareform
#testing speed
import time
# globals for keeping track of clusters
looped_points_list = []

def polar_to_poly(polars,dims):
    ret = []
    for i in range(len(polars)):
        rho = polars[i][1]
        theta = polars[i][2]

        b = rho/np.sin(theta)
        m = -np.cos(theta)/np.sin(theta)
        ret.append(Polynomial([b,m],domain=[0,dims[1]],window=[0,dims[1]]))

    return ret

def compute_dist(p1,p2):
    global looped_points_list
    # currently just does 1 point pair at a time
    # could be a bottleneck
    # regular distance, pythagoras my goat
    dist1 = np.linalg.norm(p1-p2)
    # "wrapped" distance
    theta_shift = p2[1]+1 if p2[1] < 0.5 else p2[1]-1
    p2_shift = np.array([-p2[0],theta_shift])
    dist2 = np.linalg.norm(p1-p2_shift)

    if dist1 > dist2:
        looped_points_list.append(True)
        return dist2
    else:
        looped_points_list.append(False)
        return dist1

def find_clusters(data):
    # using DBSCAN, find clusters from hough line data
    # problem: near-vertical line clusters dont form neat clusters
    # this is because of theta periodicity and rho sign flip around vertical lines 
    # seems solveable with a precomputed distance matrix
    # which is a N*N matrix for datasets size N, each cell holding distance between point Nx and Ny
    # this should be filled with a method that "wraps around" with mentioned edges
    # 1st try regular distance
    # need to also calculate distance to target shifted by pi AND with flipped rho sign?
    # also normalizing data seems necessary

    ro_min = np.min(data[:,0])
    ro_max = np.max(data[:,0])
    th_max = np.max(data[:,1])
    ro_max_abs = np.maximum(np.abs(ro_min),np.abs(ro_max))
    data_norm = np.zeros(np.shape(data))
    data_norm[:,0] = data[:,0]/ro_max_abs
    data_norm[:,1] = data[:,1]/th_max
    # sort of todo: below distance matrix calculations shouldn't manipulate globals
    # the globals create a bool mask for which data pairs "wrap" around
    # this is bad and easy to break, but it works for now
    distance_matrix = squareform(pdist(data_norm, metric=compute_dist))
    db = DBSCAN(eps=0.1,min_samples=5,metric="precomputed")
    db.fit_predict(distance_matrix)
    ret = dict((
        ("labels",db.labels_),
        ("core_samples",db.core_sample_indices_) #returns indices of non-noise
    ))
    
    return ret

def pos_calc(kp,conts,lin_pol,lin_pts,dims):
    global looped_points_list

    mask = np.zeros(dims,dtype=np.uint8)
    mask = cv.drawKeypoints(mask, kp, np.array([]), (0, 0, 255),
                            cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    kp_arr = cv.KeyPoint.convert(kp)
    for i in range(len(kp_arr)):
        x = int(kp_arr[i][1])
        y = int(kp_arr[i][0])
        mask[x][y] = 255
    #cv.imshow("mask",mask)

    looped_points_list = []
    # this might be unnecessary; just how I managed to plot this
    polys = polar_to_poly(lin_pol,dims)
    clusters = find_clusters(lin_pol[:,1:])
    # the list is a global and the mask is easy to break, be advised
    looped_points_mat = squareform(np.array(looped_points_list,dtype=bool))
    print("cluster labels:",type(clusters["labels"]),np.shape(clusters["labels"]),"\n",clusters["labels"])
    #print("cluster core samples:",clusters["core_samples"])
    print(np.shape(looped_points_mat),"matrix of looped pts\n",looped_points_mat)

    unique_clusters = np.unique(clusters["labels"],True)
    print(unique_clusters)


    ################################################
    # end of script with a bunch of matplotlib stuff
    ################################################
    end_time = time.perf_counter()
    plt.figure(figsize=(16,6))
    ax1 = plt.subplot(1,2,1)
    for i in range(len(polys)):
        x_vals, y_vals = polys[i].linspace(n=50)
        ax1.plot(x_vals,y_vals)
    ax1.set_xlim(left=0,right=320)
    ax1.set_ylim(bottom=0,top=240)

    ax2 = plt.subplot(1,2,2)
    ax2.grid(True)
    ax2.set_xlabel("theta (angle)")
    ax2.set_ylabel("rho (dist)")
    #ax2.xaxis.set_major_formatter(tck.FormatStrFormatter('%g $\pi$'))
    #ax2.xaxis.set_major_locator(tck.MultipleLocator(np.pi / 2)) 
    ax2.autoscale(axis="x",tight=True)
    ax2.scatter(lin_pol[:,2],lin_pol[:,1],c=clusters["labels"],s=8,marker="x")#theta,rho
    plt.show()

    return end_time


if __name__ == '__main__':
    
    imagefile  = cv.imread('img/data/13_50_19_11_26-im_bw.png', cv.IMREAD_GRAYSCALE)
    assert imagefile is not None, "file could not be read, check with os.path.exists()"

    start_time = time.perf_counter()
    # img_proc returns class with keypoints, conts, lines_polar, lines_pts, img_dims
    ret = imp.img_proc(imagefile,showimg=False)
    print(ret.img_dims,type(ret.img_dims))

    end_time = pos_calc(ret.keypoints,ret.conts,ret.lines_polar,ret.lines_pts,ret.img_dims)
    print(type(end_time))
    progtime = end_time - start_time
    print("position_calc.py took :", progtime*(10**3)," ms")
    cv.waitKey(0)
    cv.destroyAllWindows
