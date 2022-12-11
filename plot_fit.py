
import argparse
from datetime import datetime, timedelta
import math
import sys

import numpy as np

import matplotlib
import matplotlib.dates as mdates
matplotlib.use("Agg")
import matplotlib.pyplot as plt

strEnd = ".csv"

def weeklyAvg(lstDays, lstData):
    lstSum = []
    lstWeeklyData = []
    lstWeeklyDays = []
    for nI, fData in enumerate(lstData):
        lstSum.append(fData)
        if len(lstSum) == 7:
            lstWeeklyData.append(sum(lstSum)/7)
            lstSum = []
            lstWeeklyDays.append(lstDays[nI]-3)
    return lstWeeklyDays, lstWeeklyData

def peak(nDay, fArea, fPosition, fWidth):
    return fArea*math.exp(-(nDay-fPosition)**2/fWidth)

def plotFit(strFilename):

    lstPatients = []
    lstDays = []
    pBaseDate = None
    with open(strFilename) as inFile:
        for strLine in inFile:
            if strLine.strip().startswith("#"):
                nYear, nMonth, nDay = map(int, strLine.strip().split()[1].split("-"))
                pBaseDate = datetime(nYear, nMonth, nDay)
                continue
                
            nDay, fPatients = map(float, strLine.strip().split())
            lstDays.append(int(nDay))
            lstPatients.append(fPatients)

    lstFit = []
    lstFitDays = []
    strFitFile = strFilename.replace(".csv", "_fit.csv")
    with open(strFitFile) as inFile:
        for strLine in inFile:
            if strLine.strip().startswith("#"):
                if len(strLine) < 100:
                    nYear, nMonth, nDay = map(int, strLine.strip().split()[1].split("-"))
                    if pBaseDate != datetime(nYear, nMonth, nDay):
                        print("Date mismatch in fit/data files")
                        sys.exit(-1)
                continue
                
            nDay, fFit = list(map(float, strLine.strip().split()))[0:2]
            lstFit.append(fFit)
            lstFitDays.append(int(nDay))

    lstDays, lstPatients = weeklyAvg(lstDays, lstPatients)

    # read parameters to get locations for annotations
    lstAnnotations = ["Wave 1", "Fall 2020", "Post-Vax", "Delta", "               Omicron", "BA.2", "BA.5"]
    lstVShift = [1140, 1520, 760, 760, 570, 1250, 1600] # additional shift for labels
    lstPeakDays = []
    lstPeakHeights = []
    lstPositions = []
    lstWidths = []
    lstAreas = []
    strParameterFile = strFilename.replace(".csv", "_parameters.csv")
    with open(strParameterFile) as inFile:
        for strLine in inFile:
            if strLine.strip().startswith("#"): continue
            
            pDate = datetime.strptime(strLine.split()[1], "%Y-%m-%d")
            fDay = float(strLine.split()[2])
            fArea = float(strLine.split()[4])
            fSigma = float(strLine.split()[3])
            fHeight = fArea/(fSigma*2.5066282746310002)

            lstPositions.append(fDay)
            lstWidths.append(2*fSigma**2)
            lstAreas.append(fArea/(math.sqrt(2*math.pi)*fSigma))
            
            lstPeakDays.append(pDate)
            lstPeakHeights.append(fHeight)

    # plot with dates: configure plot
    strDate = str(datetime.today().date())
    lstDates = [pBaseDate+timedelta(days=x) for x in lstDays]
    pLocator = mdates.AutoDateLocator()
    pFormatter = mdates.AutoDateFormatter(pLocator)
    pFigure, pPlot = plt.subplots()
    pPlot.xaxis.set_major_locator(pLocator)
    pPlot.xaxis.set_major_formatter(pFormatter)
    pPlot.set_title("Canada Hospitalized Covid Patients")

    # plot    
    pPlot.grid(True, linewidth=0.2)
    pPlot.set_xlabel("Date")
    pPlot.set_ylabel("Hospitalized")
    strURL = "https://health-infobase.canada.ca/src/data/covidLive/covid19-epiSummary-hospVentICU.csv"
    pPlot.annotate('Generated: '+strDate+" from: "+strURL,
                xy=(.19, .03), xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=6)
    pPlot.plot(lstDates, lstPatients, "x", markersize=4, color="xkcd:blue", label="Data")

    # plot fit
    lstFitDates = [pBaseDate+timedelta(days=x) for x in lstFitDays]
    pPlot.plot(lstFitDates, lstFit, color="xkcd:red", label="Fit")

    # find next peak
    nLookback = 4
    lstDiff = []
    lstRealWidth = []
    lstTotalArea = []
    for nI in range(1, 1+nLookback):
        lstDiff.append(lstPositions[-nI]-lstPositions[-nI-1])
        lstRealWidth.append(math.sqrt(lstWidths[-nI]/2))
        lstTotalArea.append(lstAreas[-nI]*math.sqrt(2*math.pi)*lstRealWidth[-1])

    fAverageDiff = sum(lstDiff)/len(lstDiff)
    fNextPosition = lstPositions[-1]+fAverageDiff
    fAverageArea = sum(lstTotalArea[-nLookback:])/nLookback
    fAverageWidth = sum(lstRealWidth[-nLookback:])/nLookback
    fDiffSDev = math.sqrt(sum([(fAverageDiff-fDiff)**2 for fDiff in lstDiff])/(nLookback-1))
    fWidthSDev = math.sqrt(sum([(fAverageWidth-fWidth)**2 for fWidth in lstRealWidth])/(nLookback-1))
    fAreaSDev = math.sqrt(sum([(fAverageArea-fArea)**2 for fArea in lstTotalArea])/(nLookback-1))
    print("Spacing: ", lstDiff[-4:])
    print("Average spacing: ",fAverageDiff,"+/-", fDiffSDev)

    # plot model fit
    lstModel = []
    lstModelDates = []
    with open(strFilename.replace(".csv", "_model.csv")) as inFile:
        for strLine in inFile:
            nDay, fPatients = map(float, strLine.strip().split())
            pDate = pBaseDate+timedelta(days=nDay)
            if pDate > datetime(2023,12,31): break
            lstModelDates.append(pDate)
            lstModel.append(fPatients)
    nDayMax = int(nDay)
    pPlot.plot(lstModelDates, lstModel, color="firebrick", linewidth="0.3", label="SEIRS Model")

    # plot next peak
    fNextSdev = math.sqrt(fAverageWidth/2)
    fStart = fNextPosition-3*fAverageWidth
    lstNextDays = [fStart+nI for nI in range(int(6*fAverageWidth))]
    lstNextDates = [pBaseDate+timedelta(days=x) for x in lstNextDays]

    fAverageA = sum(lstAreas[-nLookback:])/nLookback    # parameter averages
    fAverageW = sum(lstWidths[-nLookback:])/nLookback

    lstNextPeak = [peak(nDay, fAverageA, fNextPosition, fAverageW) for nDay in lstNextDays]
    fNextHeight = max(lstNextPeak)
    pPlot.plot(lstNextDates, lstNextPeak, color="xkcd:black", label="Prediction")
    pNextDate = lstNextDates[len(lstNextDates)//2]
    fSDev = math.sqrt(fAverageWidth/2)
    fRealArea = fAverageArea*math.sqrt(2*math.pi)*fSDev
    print("PREDICTED:")
    print("Date:", pNextDate.date(), "+/-", fDiffSDev)
    print("Width:", fAverageWidth, fWidthSDev)
    print("Area:", fAverageArea, fAreaSDev)
    strNextDate = "         "+str(pNextDate.date())
    # annotate
    for nI, pDate in enumerate(lstPeakDays):
        strAnnotation = "#"+str(nI+1)
        nVShift = 800
        if nI < len(lstAnnotations):
            strAnnotation = lstAnnotations[nI]
            nVShift = lstVShift[nI]
        pPlot.annotate(strAnnotation, xy=(pDate, lstPeakHeights[nI]+nVShift), horizontalalignment="center", verticalalignment="top", fontsize=10)
    nVShift = 500
    pPlot.annotate(strNextDate, xy=(pNextDate, fNextHeight+nVShift), horizontalalignment="center", verticalalignment="top", fontsize=8)

    # set the lower end to be strictly 0
    pPlot.set_ybound(lower=0)

    # shade with season markers
    lstSeasonMonth = [3, 6, 9, 12]
    lstAlpha = [0.05, 0.15, 0.25, 0.35]
    lstSeasonDays = [pBaseDate]
    pDate = pBaseDate
    for nI in range(nDayMax):
        pDate = pDate + timedelta(days=1)
        if pDate.month in lstSeasonMonth:
            if pDate.day == 21:
                lstSeasonDays.append(pDate)
    for nI, pDate in enumerate(lstSeasonDays[1:]):
    #    if not nI%2:
            pPlot.axvspan(lstSeasonDays[nI], pDate, color='gray', alpha=lstAlpha[nI%4], lw=0)

    pPlot.legend(loc="upper left")

    pFigure.autofmt_xdate()
    strFigFile = strDate+"_"+strFilename.replace(strEnd, ".png")
    pFigure.savefig(strFigFile)

if __name__ == "__main__":
    pParser = argparse.ArgumentParser(prog="python3 plot_fit.py", description="Plot fit from .csv file (must end in .csv)")
    pParser.add_argument("filename", help="Name of input file", nargs="?", default="")
    pArgs = pParser.parse_args(sys.argv[1:])
    if not pArgs.filename.endswith(strEnd):
        print("Filename must end in"+strEnd)
        sys.exit(-1)

    plotFit(pArgs.filename)
