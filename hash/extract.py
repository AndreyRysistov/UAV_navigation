import numpy as np
import cv2
from image import Image
from hash.phash import PHash

"""
  Extracts sub images and hashes from an image
"""


def subImages(img, keypoints, krange=(0, 20), attempts=100, multiples=8):
    result = []
    height, width, channel = img.shape
    kp = keypoints
    Z = []
    for k in kp:
        Z.append([k.pt[0], k.pt[1]])
    Z = np.float32(Z)
    for clustersCount in range(krange[0], krange[1]):
        if clustersCount == 0:
            result.append(img.parent(img, 0, 0))
            continue
        ret, label, center = cv2.kmeans(Z, K=clustersCount,
                                        bestLabels=None,
                                        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10),
                                        attempts=attempts, flags=cv2.KMEANS_PP_CENTERS)
        for k in range(clustersCount):
            centroid = center[k]
            img = img
            cluster = Z[label.ravel() == k]

            miX = miY = 99999
            maX = maY = 0
            for v in cluster:
                x = int(v[0])
                y = int(v[1])
                if x < miX:
                    miX = x
                if y < miY:
                    miY = y
                if x > maX:
                    maX = x
                if y > maY:
                    maY = y
            dmiX = int(centroid[0] - miX)
            dmiY = int(centroid[1] - miY)
            dmaX = int(centroid[0] + maX)
            dmaY = int(centroid[1] + maY)
            while dmiX % multiples != 0:
                dmiX -= 1
            while dmaX % multiples != 0:
                dmaX += 1
            while dmiY % multiples != 0:
                dmiY -= 1
            while dmaY % multiples != 0:
                dmaY += 1
            miX = dmiX
            maX = dmaX
            miY = dmiY
            maY = dmaY
            cropped = img.crop(miX, miY, maX, maY)
            if not cropped or cropped.width < 32 or cropped.height < 32:
                continue
            result.append(cropped)
    return result


def binImages(keypoints, descriptors=[]):
    result = []
    desc = descriptors
    kps = keypoints
    if (descriptors is None):
        return []
    for di in range(len(desc)):
        ds = desc[di]
        kp = kps[di]
        x = kp.pt[0]
        y = kp.pt[1]
        rows = []
        for i in range(0, len(ds), 2):
            d = ds[i:i + 2]
            r = ''.join(str(1 & int(d[0]) >> i) for i in range(8)[::-1]) + ''.join(
                str(1 & int(d[1]) >> i) for i in range(8)[::-1])
            rows.append(list(r))
        im = np.float32(rows)
        img = Image(im)
        img.parent(x=x, y=y)
        result.append(img)
    return result


def get_hashes(imgs, checkDuplicates=True):
    result = []
    for i in imgs:
        hash = PHash(i)
        found = False
        if checkDuplicates:
            for sh in result:
                if sh == hash:
                    found = True
                    break
        if not found:
            result.append(hash)
    return result