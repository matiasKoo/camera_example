import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

class blobparams:
    params = cv.SimpleBlobDetector.Params()
    # what color blobs
    params.blobColor = 255

    # binarization params
    params.minThreshold = 10
    params.maxThreshold = 250
    params.thresholdStep = 1

    # area 
    params.filterByArea = True
    params.minArea = 6

    # circularity
    params.filterByCircularity = True
    params.minCircularity = 0.60

    # convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.90 #0.01

    # take contours
    params.collectContours = True


class houghparams:

    lines_max=20
    threshold=1
    min_rho=0
    max_rho=240 # this is usually gotten from img dimensions
    rho_step=1
    min_theta=0
    max_theta=np.pi/2
    theta_step=np.pi/360


# probably stupid? idk it works
def line_func(func_slope,func_x,func_b):
    ret = func_slope*func_x+func_b
    return ret


def img_proc(img):
    print("rcv img: ",np.shape(img),type(img))

    detector = cv.SimpleBlobDetector.create(blobparams.params)

    # detect blobs
    keypoints = detector.detect(img)
    conts = detector.getBlobContours()
    print("conts type:",type(conts))
    print("conts: ",conts)

    # Draw blobs as red circles
    output = cv.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                            cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # draw contours as found by detector
    cv.drawContours(output,conts,-1, (0,255,0), 1)

    # bitmask to which we also draw contours for further processing
    mask = np.zeros(img.shape,np.uint8)
    cv.drawContours(mask,conts,-1,255,thickness=cv.FILLED)

    # need to experiment or just figure out what sort of kernel to use. kernel dimensions should be dynamic?
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5))

    # open first "shrinks" and then "grows" all light pixels
    mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)

    cv.imshow("mask",mask)

    img_height, img_width = mask.shape
    # TODO: no error handling here causes problems if no blobs are detected
    pixelpoints = cv.findNonZero(mask)
    pixelpoints = pixelpoints[:,np.newaxis,:]

    # returns an array of 3d vectors (votes, rho, theta) that describe lines
    lines_polar = cv.HoughLinesPointSet(
        point=pixelpoints, # needs to be matlike with (x,1,y) dimensions (the middle "empty" dimension is for colour channels or sth)
        lines_max=houghparams.lines_max,
        threshold=houghparams.threshold,
        min_rho=houghparams.min_rho,
        max_rho=img_height, # this is in houghparams class as well but probably just worth doing here
        rho_step=houghparams.rho_step,
        min_theta=houghparams.min_theta,
        max_theta=houghparams.max_theta,
        theta_step=houghparams.theta_step
    )

    print("LINES BE LIKE:-------------------")
    print(type(lines_polar), type(lines_polar[0][0]))
    print(lines_polar[0],np.shape(lines_polar))
    print("---------------------------------")

    for i in range(len(lines_polar)):
        votes = lines_polar[i][0]
        rho = lines_polar[i][1]
        theta = lines_polar[i][2]

        # start with getting a point on the line, x0 = rho*cos(theta), y0 = rho*sin(theta)
        x0 = rho*np.cos(theta)
        y0 = rho*np.sin(theta)

        # y-intercept is found at y1-m*x1 (b = y-mx)
        # slope is simply -1/tan(theta)
        if np.tan(theta) == 0:
            slope = 0   # hackerman way of avoiding dividing by zero
        elif theta == np.pi/2:
            slope = 10**10 # avoid undefined with arbitrarily large slope, sign doesnt matter
        else:
            slope = -1/np.tan(theta)
        y_intercept = y0-slope*x0

        #draw lines
        x1 = -img_width
        y1 = line_func(slope,x1,y_intercept)
        pt1 = (int(x1),int(y1))
        x2 = img_width
        y2 = line_func(slope,x2,y_intercept)
        pt2 = (int(x2),int(y2))

        cv.line(output,pt1,pt2,(0,255,0),1)


    cv.imshow("blobs detected",output)
    wait_ret = cv.waitKey(0)
    cv.destroyAllWindows()

    if wait_ret == 32: # wait_ret is 32 if spacebar was pressed during waitKey

        date = dt.datetime.now()
        date_str = date.strftime("%y-%m-%d_%H-%M")
        print(date_str, type(date_str))
        bw_str = "img/data/" + date_str + "-im_bw.png"
        line_str = "img/data/" + date_str + "-im_line.png"
        mask_str = "img/data/" + date_str + "-im_mask.png"
        cv.imwrite(bw_str, img)
        cv.imwrite(line_str, output)
        cv.imwrite(mask_str, mask)
        print("saved images to img/data/")

    

if __name__ == '__main__':
    
    imagefile  = cv.imread('img/leds_far.png', cv.IMREAD_GRAYSCALE)
    assert imagefile is not None, "file could not be read, check with os.path.exists()"
    print("cv.imread tyyppi: ", type(imagefile), np.shape(imagefile))
    cv.imshow("blobs detected",imagefile)

    img_proc(imagefile)