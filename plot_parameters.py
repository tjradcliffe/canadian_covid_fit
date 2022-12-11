
import argparse
from datetime import datetime, timedelta
import math
import sys

import numpy as np

import matplotlib
import matplotlib.dates as mdates
matplotlib.use("Agg")
import matplotlib.pyplot as plt

lstAnnotations = ["Wave 1",
"Fall 2020",
"Post\nVax",
"Delta",
"Omicron",
"BA.2",
"BA.5"]

strParam = "_parameters.csv"

def findError(lstData):
    """Returns standard deviation"""
    fMean = sum(lstData)/len(lstData)
    return math.sqrt(sum([(fX-fMean)**2 for fX in lstData])/(len(lstData)-1))

def makePlot(strFilename, lstNumber, lstData, strYLabel, strType, bErrorBars, bCut):
    # generate error for pre-omicon and omicron
    nCut = 4 # separate the first four points from omicron-era
    if strType == "Spacing":
        nCut -= 1
    fPreOmicronError = findError(lstData[0:nCut])
    fOmicronError = findError(lstData[nCut:])
    lstError = [fPreOmicronError for nI in range(nCut)]
    lstError.extend([fOmicronError for nI in range(len(lstData)-nCut)])

    pFigure, pPlot = plt.subplots()
    pPlot.set_title("Canada Hospitalization Wave "+strType)
        
    pPlot.grid(linewidth=0.2)
    pPlot.set_xlabel("Wave Number")
    pPlot.set_ylabel(strYLabel)
    strDate = str(datetime.today().date())
    strURL = "https://health-infobase.canada.ca/src/data/covidLive/covid19-epiSummary-hospVentICU.csv"    
    pPlot.annotate('Generated: '+strDate+"\nfrom: "+strURL,
                xy=(.17, .17), xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=6)

    if bErrorBars:
        pPlot.errorbar(lstNumber, lstData, lstError, fmt="bx", label=strType)
    else:
        pPlot.plot(lstNumber, lstData, "bx", label=strType)

    if strType == "Spacing":
        pPlot.legend(loc="upper right")
    else:
        pPlot.legend(loc="upper left")

    if bCut: # fit eras separately 
        # plot pre-omicron fit
        lstCoeffs = np.polyfit(lstNumber[0:nCut], lstData[0:nCut], deg=1)
        fit = np.poly1d(lstCoeffs)
        lstFit = [fit(nI) for nI in lstNumber]
        pPlot.plot(lstNumber[0:nCut], lstFit[0:nCut], color="r", label="Fit")
        
        # plot omicron-era fit
        lstCoeffs = np.polyfit(lstNumber[nCut:], lstData[nCut:], deg=1)
        fit = np.poly1d(lstCoeffs)
        lstFit = [fit(nI) for nI in lstNumber]
        pPlot.plot(lstNumber[nCut:], lstFit[nCut:], color="r", label="Fit")

        strTailExtension = "_cut.png"        
    else:
        # plot total fit
        lstCoeffs = np.polyfit(lstNumber, lstData, deg=1)
        fit = np.poly1d(lstCoeffs)
        lstFit = [fit(nI) for nI in lstNumber]
        pPlot.plot(lstNumber, lstFit, color="r", label="Fit")
        strTailExtension = ".png"        

    # figure out bounding box to auto-place annotations
    fXLower, fXUpper = pPlot.get_xlim()
    fYLower, fYUpper = pPlot.get_ylim()
    fYLower = 0
    pPlot.set_ylim(fYLower, fYUpper)
    pBox = pPlot.get_position()
    fXLow = pBox.x0
    fYLow = pBox.y0
    fXHigh = pBox.x1
    fYHigh = pBox.y1

    fXSlope = (fXHigh-fXLow)/(fXUpper-fXLower)
    fYSlope = (fYHigh-fYLow)/(fYUpper-fYLower)

    # ensure we have enough annotations for all peaks
    while len(lstAnnotations) < len(lstNumber):
        lstAnnotations.append("#"+str(len(lstAnnotations)+1))

    for nI, nWave in enumerate(lstNumber):
        fX = fXLow + (nWave-fXLower)*fXSlope+0.045
        fY = fYLow + (lstData[nI]-fYLower)*fYSlope+0.05
#        print("Annotation: ", lstAnnotations[nI], lstAnnotations[nI].split("_"))
        strAnnotation = lstAnnotations[nI].split("_")[0]
        if strType == "Spacing":
            strAnnotation = lstAnnotations[nI+1].split("_")[0]
#        print(fX, fY)
        strAlignment = "left"
        if fX > 0.55:
            strAlignment = "right"
            fX -= 0.01
            fY += 0.02
        pPlot.annotate(strAnnotation,
                    xy=(fX, fY), xycoords='figure fraction',
                    horizontalalignment=strAlignment, verticalalignment='top',
                    fontsize=12)            

    pFigure.subplots_adjust(left=0.15)
    pFigure.subplots_adjust(right=0.95)
    pFigure.subplots_adjust(top=0.92)

    strFigFile = strDate+"_"+strFilename.replace(strParam, "_wave_"+strType.lower()+strTailExtension)
    print("Plotting:", strFigFile)
    pFigure.savefig(strFigFile)

def plotParameters(strFilename, bCut=True, bErrorBars=True, bArea=False, bWidth=False, bSpacing=False):

    bPlotAll = True # plot everything if no selection is given
    if bArea or bWidth or bSpacing:
        bPlotAll = False
        
    lstDx = []
    lstDy = []

    fSlope = None
    lstNumber = []
    lstPeak = []
    lstWidth = []
    lstArea = []
    nPeak = 1
    with open(strFilename) as inFile:
        for strLine in inFile:
            if strLine.strip().startswith("# slope"):
                fSlope = float(strLine.strip().split()[-1])
                continue
            elif strLine.strip().startswith("#"):
                continue
                
            fPeak, fWidth, fArea = map(float, strLine.strip().split()[2:])
            lstPeak.append(fPeak)
            lstWidth.append(fWidth)
            lstArea.append(fArea)
            lstNumber.append(nPeak)
            nPeak += 1

    if bPlotAll or bArea:
        makePlot(strFilename, lstNumber, lstArea, "Person-Days Hospitalized", "Area", bErrorBars, bCut)
    if bPlotAll or bWidth:
        makePlot(strFilename, lstNumber, lstWidth, "Wave Width (days)", "Width", bErrorBars, bCut)
    if bPlotAll or bSpacing:
        lstDiff = [lstPeak[nI]-lstPeak[nI-1] for nI in range(1, len(lstPeak))]
        makePlot(strFilename, lstNumber[1:], lstDiff, "Wave Interval (days)", "Spacing", bErrorBars, bCut)

if __name__ == "__main__":
    pParser = argparse.ArgumentParser(prog="python3 plot_parameters.py", description="Plot parameters from fit (must end with _parameters.csv)")
    pParser.add_argument("filename", help="Name of input file", nargs="?", default="")
    pParser.add_argument("--area", "-a", action="store_true", help="Plot only the peak area")
    pParser.add_argument("--width", "-w", action="store_true", help="Plot only the peak width")
    pParser.add_argument("--spacing", "-s", action="store_true", help="Plot only the peak spacing")
    pParser.add_argument("--errorbars", "-e", action="store_true", help="Include error bars derived from data dispersion")
    pParser.add_argument("--cut", "-c", action="store_true", help="Fit omicron and pre-omicron separately")
    pArgs = pParser.parse_args(sys.argv[1:])

    if not pArgs.filename.endswith(strParam):
        print("Filename must end in"+strParam)
        sys.exit(-1)
        
    plotParameters(pArgs.filename, pArgs.cut, pArgs.errorbars, pArgs.area, pArgs.width, pArgs.spacing)
    