import argparse
from datetime import datetime, timedelta
import math
import sys

import simple_minimizer as sm
from peaks_objective import PeaksObjective
from peak_finder import PeakFinder

mapConvergenceReasons = {-1: "Exceeded iteration limit", 1: "Closest points indistinguishable", 
                                                 2: "Met fractional tolerance", 3:"Minimum scale achieved"}

def fitPeaks(strFilename, nMaxDay=-1):
    # find peaks
    pPeakFinder = PeakFinder(strFilename, nMaxDay)
    lstPeaks, bExtrapolated = pPeakFinder.findPeaks()

    # set up minimizer
    nFittedPeaks = len(lstPeaks)
    if bExtrapolated:
        nParameters = 1 + 3*(len(lstPeaks)-1) # do not included extrapolated peak (fits badly)
        nFittedPeaks -= 1 # do not fit last peak
    else:
        nParameters = 1 + 3*len(lstPeaks) # linear ramp plus width/area/position of each peak
    pMinimizer = sm.SimpleMinimizer(nParameters)
    pObjective = PeaksObjective(strFilename, nMaxDay)
    pMinimizer.setObjective(pObjective)
    pMinimizer.setMinimumScale(1E-6) # the minimum is pretty well defined

    nYear, nMonth, nDay = map(int, pObjective.strStartDate.split("-"))
    pStartDate = datetime(nYear, nMonth, nDay)

    lstStarts = [0.1]
    lstScales = [0.01]
    nPeak = 1
    print("Starting parameters: (Position, Size Width)")
    for fPosition, fSize in lstPeaks[0:nFittedPeaks]:
        print(nPeak, fPosition, fSize, math.sqrt(1800))
        nPeak += 1
        lstStarts.append(fSize)
        lstStarts.append(fPosition)
        lstStarts.append(1800) # all peaks about 30 days sdev => w = 2*sdev**2 = 1800
        lstScales.extend([10, 1000, 10]) # reasonable default for scales

    pMinimizer.setStarts(lstStarts)
    pMinimizer.setScales(lstScales)

    print("Fitting... this may take a minute or two...")
    nCount, pResult, nReason = pMinimizer.minimize()
    lstVertex = pResult.getVertex()

    print("Iterations:", nCount)
    print("Reason for termination:", mapConvergenceReasons[nReason])
    print("Residual RMS Error: ",pResult.getValue())
    print("Peak Position Size Width")
    for nI in range(0, len(lstVertex[1:]), 3):
        pDate = pStartDate+timedelta(days=lstVertex[nI+2])
        print(int(nI/3)+1, pDate, lstVertex[nI+2], lstVertex[nI+1], math.sqrt(lstVertex[nI+3]))

    print("")
    strOutputFile = strFilename.replace(".csv", "_fit.csv")
    strDiffFile = strFilename.replace(".csv", "_diff.csv")
    strParameterFile = strFilename.replace(".csv", "_parameters.csv")
    with open(strParameterFile, "w") as outFile:
        outFile.write("# slope: "+str(lstVertex[0])+"\n")
        outFile.write("# Peak Date Day SDev Area\n")
        nCount = 1
        for nPeak in range(1, nParameters, 3): # 1, 17, 3 for 6 peaks
        #    print(lstVertex[nPeak:nPeak+3])
            fSDev = math.sqrt(lstVertex[nPeak+2]/2)
            fArea = lstVertex[nPeak]*math.sqrt(2*math.pi)*fSDev
            pDate = pStartDate+timedelta(days=lstVertex[nPeak+1])
            outFile.write(" ".join(map(str, (nCount, pDate.date(), lstVertex[nPeak+1], fSDev, fArea)))+"\n")
            nCount += 1

    print("Writing fit and components to: ", strOutputFile)
    with open(strOutputFile, "w") as outFile:
        outFile.write("# "+" ".join(map(str, lstVertex))+"\n")
        outFile.write("# "+pObjective.strStartDate+"\n")
        for nDay in range(len(pObjective.lstData)):
            fFit = pObjective.fit(nDay, lstVertex)
            lstComponents = pObjective.components(nDay, lstVertex)
            outFile.write(" ".join(map(str, [nDay, fFit]+lstComponents))+"\n")
            
        for nI in range(nDay+1, nDay+100):
            fFit = pObjective.fit(nI, lstVertex)
            if fFit < 10: break # has not happened yet in the data
            lstComponents = pObjective.components(nI, lstVertex)
            outFile.write(" ".join(map(str, [nI, fFit]+lstComponents))+"\n")

    print("Writing diff to: ", strDiffFile)    
    with open(strDiffFile, "w") as outFile:
        for nDay, fValue  in enumerate(pObjective.lstData):
            fFit = pObjective.fit(nDay, lstVertex)
            outFile.write(" ".join(map(str, (nDay, 2*(fValue-fFit)/(fValue+fFit))))+"\n")

if __name__ == "__main__":
    pParser = argparse.ArgumentParser(prog="python3 peak_fitter.py", description="Find and fit peaks in covid data extracted by extract_column.py")
    pParser.add_argument("filename", help="File to process (must end in .csv)")
    pParser.add_argument("--maxday", "-m", help="Maximum day number to process (day number 0 is Jan 23, 2020), default is all", default=-1, type=int)
    pArgs = pParser.parse_args(sys.argv[1:])

    if not pArgs.filename.endswith(".csv"):
        print("BAD FILENAME: MUST END IN .csv:", pArgs.filename)
        print("")
        pArgs.print_help()
        sys.exit(-1)

    fitPeaks(pArgs.filename, pArgs.maxday)
