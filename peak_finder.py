import argparse
import sys

class PeakFinder:
    """
    Dumb peak finder that looks for a peak, then a drop week-by-week
    """
    def __init__(self, strFilename, nMaxDay):
        """Read two-column space-separated data file: day data,
        and sum the data into weeks"""
        
        self.lstPeaks = []
        
        self.lstData = []
        self.strStartDate = ""
        lstWeek = []
        nCount = 0
        with open(strFilename) as inFile:
            for strLine in inFile:
                if strLine.strip().startswith("#"):
                    self.strStartDate = strLine.strip().split()[1]
                    continue
                lstWeek.append(float(strLine.strip().split()[1]))
                if len(lstWeek) == 7:
                    self.lstData.append(sum(lstWeek))
                    lstWeek = []
                nCount += 1
                if nMaxDay >= 0 and nCount > nMaxDay:
                    break
        
    def findPeaks(self):
        """Find peaks. The sensitivity is the fractional drop required 
        for the max to be a peak. Default is 0.9, so 10% drop required."""

        bExtrapolated = False # flag to tell if we are extrapolating a new peak
        fPreviousSlope = 0
        fPreviousValue = 0
        lstDips = []
        for nWeek, fValue in enumerate(self.lstData):
            fSlope = fValue-fPreviousValue
            if fSlope < -115 and fPreviousSlope > 115:
#                print("Peak: ", 7*nWeek-3.5, fSlope, fPreviousSlope)
                self.lstPeaks.append((7*nWeek-3.5, fPreviousValue/7))
            if fPreviousSlope < -115 and fSlope > 115:
#                print("Dip: ", 7*nWeek-3.5, fSlope, fPreviousSlope)
                lstDips.append((7*nWeek-3.5, fPreviousValue/7))
            fPreviousValue = fValue
            fPreviousSlope = fSlope

        if lstDips[-1][0] > self.lstPeaks[-1][0]:   # out of the last dip so project a new peak
            bExtrapolated = True # flag that we are extrapolating a peak
            if len(self.lstPeaks) > 2: # use previous inter-peak spacing added to last peak position
                fDelta = self.lstPeaks[-1][0]-self.lstPeaks[-2][0]
                self.lstPeaks.append((self.lstPeaks[-1][0]+fDelta, self.lstPeaks[-1][1]))
            else:   # use distance from last peak to dip, added to dip position
                fDelta = lstDips[-1][0]-self.lstPeaks[-1][0]
                self.lstPeaks.append((lstDips[-1][0]+fDelta, self.lstPeaks[-1][1]))
        
        # deal with noisy peak-tops by merging any peaks within 30 days of each other
        lstMergedPeaks = [self.lstPeaks[0]]
        for fDay, fPeak in self.lstPeaks[1:]:
            if fDay-lstMergedPeaks[-1][0] < 37:
                lstMergedPeaks[-1] = ((fDay+lstMergedPeaks[-1][0])/2, (fPeak+lstMergedPeaks[-1][1])/2)
            else:
                lstMergedPeaks.append((fDay, fPeak))

        self.lstPeaks = lstMergedPeaks
        
        return self.lstPeaks, bExtrapolated

if __name__ == "__main__":
    
    pParser = argparse.ArgumentParser(prog="python3 peak_finder2.py", description="Find peaks in covid data extracted by extract_column.py")
    pParser.add_argument("filename", help="File to process")
    pParser.add_argument("--maxday", "-m", help="Maximum day number to process (counts from Jan 23, 2020), default is all", default=-1, type=int)

    pArgs = pParser.parse_args(sys.argv[1:])

    pPeakFinder = PeakFinder(pArgs.filename, pArgs.maxday)
    lstPeaks = pPeakFinder.findPeaks()
    for (nDay, fPeak) in lstPeaks:
        print(nDay, fPeak)
