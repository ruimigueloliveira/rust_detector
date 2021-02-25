import cv2
import numpy as np
import sys
import os
from progress.bar import Bar

boundaries = [[ ([58, 57, 101], [76, 95, 162]) ]]
boundaries += [[ ([26, 61, 111], [81, 144, 202]) ]]
boundaries += [[ ([44, 102, 167], [115, 169, 210]) ]]
boundaries += [[ ([0, 20, 50], [50, 70, 150]) ]]

def processImg(img):
    #bar = Bar('Applying masks', max=4)
    output = []
    for b in boundaries:
        for (l, u) in b:
            l = np.array(l, dtype = "uint8")
            u = np.array(u, dtype = "uint8")
            mask = cv2.inRange(img, l, u)
            output += [cv2.bitwise_and(img, img, mask = mask)]
            #bar.next()

    final = output[0]
    for o in output:
        final = cv2.bitwise_or(final, o)
    #bar.finish()
    return final

def getIntensityImg(img):
    bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    totalPixels = img.shape[0] * img.shape[1]
    bar = Bar('Processing', max=totalPixels)
    noRustPixels = 0
    for j in range(img.shape[0]):
        for i in range(img.shape[1]):
            v = img[j,i][0]
            if v == 0:
                noRustPixels += 1
            elif (v <= 256) and (v >= 80):
                img[j,i][0] = 0
                img[j,i][1] = 255
                img[j,i][2] = 255
            elif (v < 80) and (v >= 30):
                img[j,i][0] = 0
                img[j,i][1] = 134
                img[j,i][2] = 255
            elif (v < 30) and (v > 0):
                img[j,i][0] = 0
                img[j,i][1] = 0
                img[j,i][2] = 255
            bar.next()

    percent = (1-(noRustPixels / totalPixels)) * 100
    bar.finish()
    return percent,bw,img


def getPercent(img):
    totalPixels = img.shape[0] * img.shape[1]
    #bar = Bar('Processing', max=totalPixels)
    rustPixels = 0
    for j in range(img.shape[0]):
        for i in range(img.shape[1]):
            if img[j,i][0] != 0 and img[j,i][1] != 0 and img[j,i][2] != 0:
                rustPixels += 1
            #bar.next()
    #bar.finish()
    return (rustPixels / totalPixels) * 100

print("\nRUST DETECTOR")
while(True):

    #cv2.destroyAllWindows()
    path = ''
    choice = ''
    while choice != '1' and choice != '2' and choice != '3':
        print("\nSelect an option:")
        print("1 Detect rust on a single image")
        print("2 Detect rust on several images")
        print("3 Quit")
        choice = input("")

    if choice == '1': # Detect rust on a single image
        choice = ''
        while choice != '1' and choice != '2':
            print("Select the folder where the image is:")
            print("1 Corrosion")
            print("2 No_Corrosion")
            choice = input("")
            if choice == '1':
                path += 'Corrosion/'
            elif choice == '2':
                path += 'No_Corrosion/'

        print('List of files:\n'+str(os.listdir(path)))
        path += input("Insert the image's name: ")
        if not os.path.isfile(path):
            print("Error: Image not found")
            sys.exit()

        rustPercent = None
        img = cv2.imread(path, 1)

        crop = input("Do you want to crop the image ? (y/n)\n")
        if crop == 'y':
            # Select ROI
            r = cv2.selectROI(img)
            # Crop image
            img = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        else:
            cv2.imshow("Original", img)

        rust = processImg(img)
        cv2.imshow("Processed_Image_1", rust)
        rustPercent, bw, final = getIntensityImg(rust)
        cv2.imshow('Black_&_White', bw)

        if rustPercent == None:
            rustPercent = getPercent(final)
        print("Percentage of rust in the image: %.2f%%"%rustPercent)
        # Display cropped image
        cv2.imshow("Processed_Image_2", final)
        # cv2.imshow("final", final)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        #input("")

    elif choice == '2': # Detect rust on several images
        folder = input("Select the folder where the image is:\n") + '/'
        if not os.path.isdir(folder):
            print("Error: Directory not found")
            sys.exit()
        files = os.listdir(folder)
        print(files)
        crop = input("Do you want to set a minimum percentage of rust per image ? (y/n)\n")
        minPercent = 0
        if crop == 'y':
            minPercent = int(input("Insert the minimum percentage\n"))

        finalImgsNames = []
        for f in files:
            img = cv2.imread(folder+f, 1)
            final = processImg(img)
            rustPercent = getPercent(final)
            print(f+" - %.2f%%"%rustPercent)
            if rustPercent >= minPercent:
                finalImgsNames += [f]
        
        print("List of images: ")
        print(finalImgsNames)

    elif choice == '3':
        sys.exit()

            