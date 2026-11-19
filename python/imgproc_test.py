import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

class blobparams:
    # what color blobs
    blobColor = 255

    # binarization params
    minThreshold = 10
    maxThreshold = 200
    thresholdStep = 1

    # area 
    filterByArea = True
    minArea = 10

    # circularity
    filterByCircularity = True
    minCircularity = 0.75 

    # convexity
    filterByConvexity = True
    minConvexity = 0.87

    # inertia
    filterByInertia = True
    minInertiaRatio = 0.4 #0.01

    # take contours
    collectContours = True


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
    params = cv.SimpleBlobDetector.Params()
    params.blobColor = blobparams.blobColor
    params.minThreshold = blobparams.minThreshold
    params.maxThreshold = blobparams.maxThreshold
    #params.thresholdStep = blobparams.thresholdStep
    params.filterByArea = blobparams.filterByArea
    params.minArea = blobparams.minArea
    params.filterByCircularity = blobparams.filterByCircularity
    params.minCircularity = blobparams.minCircularity
    params.filterByConvexity = blobparams.filterByConvexity
    params.minConvexity = blobparams.minConvexity
    params.filterByInertia = blobparams.filterByInertia
    params.minInertiaRatio = blobparams.minInertiaRatio
    params.collectContours = blobparams.collectContours

    detector = cv.SimpleBlobDetector.create(params)

    # try adding thresholding pre detections; getBlobContours returns all contours regardless of params?
    # this seems a little doomed. Early testing showed ok results with naive thresholding on 127 cutoff
    # binarizing image that way seems not smart though

    #blur = cv.GaussianBlur(img,(5,5),0)
    #ret_otsu, img_otsu = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

    #plt.plot()
    #plt.imshow(img_otsu)
    #plt.show()

    # detect blobs
    keypoints = detector.detect(img)
    # returns a tuple
    conts = detector.getBlobContours()
    print("conts type:",type(conts))
    #print("conts[0]:",type(conts[0])," conts[1]:",type(conts[1]))
    #print("shape 0:", np.shape(conts[0])," shape 1:",np.shape(conts[1]))

    # Draw blobs as red circles
    output = cv.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                            cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # testing contours
    cv.drawContours(output,conts,-1, (0,255,0), 1)

    mask = np.zeros(img.shape,np.uint8)
    cv.drawContours(mask,conts,-1,255,thickness=cv.FILLED)

    # need to experiment or just figure out what sort of kernel to use. kernel dimensions should be dynamic?
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(10,8))

    mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)

    cv.imshow("mask",mask)

    img_height, img_width = mask.shape
    pixelpoints = cv.findNonZero(mask)
    pixelpoints = pixelpoints[:,np.newaxis,:]

    # returns an array of 3d vectors (votes, rho, theta) that describe lines
    lines_polar = cv.HoughLinesPointSet(
        point=pixelpoints,
        lines_max=houghparams.lines_max,
        threshold=houghparams.threshold,
        min_rho=houghparams.min_rho,
        max_rho=img_height,
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
            slope = 100**100 # avoid undefined with arbitrarily large slope, sign doesnt matter
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
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == '__main__':

    imagefile  = cv.imread('img/leds_far.png', cv.IMREAD_GRAYSCALE)
    assert imagefile is not None, "file could not be read, check with os.path.exists()"
    print("cv.imread tyyppi: ", type(imagefile), np.shape(imagefile))

    img_proc(imagefile)