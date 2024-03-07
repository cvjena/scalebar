import cv2
import numpy as np

def match(img, pattern, dist_thresh: float=0.75):
    
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    
    # find the keypoints and descriptors with SIFT
    kp1, descriptors1 = sift.detectAndCompute(pattern,None)
    kp2, descriptors2 = sift.detectAndCompute(img,None)

    kp_coords = np.array([kp.pt for kp in kp2], dtype=np.float32)
    
    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    
    # Apply ratio test
    good = []
    kp_idxs = []
    for m,n in matches:
        if m.distance < dist_thresh * n.distance:
            good.append([m])
            kp_idxs.append(m.trainIdx)
    

    # from matplotlib import pyplot as plt
    # # cv.drawMatchesKnn expects list of lists as matches.
    # img3 = cv2.drawMatchesKnn(pattern, kp1, img, kp2,
    #     good, None,
    #     flags=cv2.DrawMatchesFlags_DEFAULT)
    
    # plt.figure(figsize=(16,9))
    # plt.imshow(img3)
    # plt.figure(figsize=(16,9))
    # plt.imshow(img, cmap=plt.cm.gray)
    # plt.gca().add_patch(plt.Rectangle(xy=(x0, y0), width=x1-x0, height=y1-y0, fill=False, linewidth=2))
    
    # plt.show()
    return kp_coords[kp_idxs]

def create(ncols: int, nrows: int, size: int = 20, pad: int = None, dtype=np.uint8, max_value=255):
    h, w = shape = (nrows*size, ncols*size)

    res = np.full(shape, max_value, dtype=dtype)

    for row in range(nrows):
        y0 = row * size
        y1 = y0 + size
        
        for col in range(ncols):
            x0 = col * size
            x1 = x0 + size
            if (row + col) % 2 == 0:
                res[y0:y1, x0:x1] = 0

    if pad is None:
        pad = size // 2

    if pad:
        res = np.pad(res, pad_width=pad, mode="constant", constant_values=max_value)

    return res