import siftFlann as sift
import cv2 as cv
import json
import hough
import numpy as np
import csvWriter
import specialFunctions

import cProfile
import re

import pstats, io
from pstats import SortKey

validationSetJsonPath = "./raspiCamTrainingSet.json"

confusionIndexTable = {0: 0, 5: 1, 10: 2, 20: 3, 50: 4, 100: 5}
confusionMatrix = np.zeros((6, 6), dtype=np.uint)

def HoughDetect(inputImage ,values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector):
    
    return -1

if __name__ == "__main__":
    (values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector) = sift.houghLoadValidationSet("./validation.json", 1)

    appendedFeatures = []

    for feature in frontFeatures:
        appendedFeatures.append(feature)
    for feature in backFeatures:
        appendedFeatures.append(feature)

    hough.SetUp(appendedFeatures)

    jsonFile = open(validationSetJsonPath)
    jsonObj = json.load(jsonFile)

    correctValues = 0
    incorrectValues = 0

    featureArray = []
    nextFeatureAray = []
    realValueArray = []
    detectedValueArray = []
    totalFeatures = []
    confidence = []
    dbFeaturesArray = []

    pr = cProfile.Profile()
    pr.enable()

    for entry in jsonObj:
        path = entry["path"]

        image = cv.imread(path)
        value = entry["value"]

        # print(value)

        (keypoints, features) = sift.houghGetSIFTFeatures(image)
        (detectedValue, featureCount, nextMost, dbFeatures) = hough.GetBillValue(keypoints, features, values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector, True)

        print("Detected Value: " + str(detectedValue) + " Real Value: " + str(value) + " Features: " + str(featureCount))

        featureArray.append(featureCount)
        nextFeatureAray.append(nextMost)
        realValueArray.append(value)
        detectedValueArray.append(detectedValue)
        totalFeatures.append(len(features))
        dbFeaturesArray.append(dbFeatures)

        p = 0.04 * 0.085 * 0.5 / 14
        k = featureCount
        n = len(features)
        prob = specialFunctions.ibeta(k, n-k+1, p)
        # print(prob)

        confidence.append(0.01 / (0.01 + prob))

        detectedValueIndex = confusionIndexTable[detectedValue]
        realValueIndex = confusionIndexTable[value]
        confusionMatrix[detectedValueIndex][realValueIndex] = confusionMatrix[detectedValueIndex][realValueIndex] + 1

        if detectedValue == value:
            correctValues = correctValues + 1
        else:
            incorrectValues = incorrectValues + 1
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    
    print(correctValues)
    print(incorrectValues)
    print(confusionMatrix)

    csvWriter.Write("SiftHough.csv", featureArray, nextFeatureAray, realValueArray, detectedValueArray, totalFeatures, confidence, dbFeaturesArray)