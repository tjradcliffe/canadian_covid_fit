import math

class PeaksObjective:
    
    def __init__(self, strFilename, nMaxDay, nMInDay = 0):
        
        self.lstData = []
        self.strStartDate = ""
        with open(strFilename) as inFile:
            nCount = 0
            for strLine in inFile:
                if strLine.strip().startswith("#"):
                    self.strStartDate = strLine.strip().split()[1]
                    continue
                nCount += 1
                if nCount < nMInDay:
                    continue
                self.lstData.append(float(strLine.strip().split()[1]))
                if nMaxDay >= 0 and len(self.lstData) > nMaxDay:
                    break

    def __call__(self, lstX):
        
        # lstX has structure slope, area1, pos1, width1, area2, ...
        
        fError = 0.0
        for nDay, fValue in enumerate(self.lstData):
            fError += (self.fit(nDay, lstX)-fValue)**2
        return math.sqrt(fError/nDay)

    def fit(self, nDay, lstX):
        fFit = lstX[0]*nDay # start with slope
        for nPeak in range(1, len(lstX), 3): # add peaks
            fFit += self.peak(nDay, lstX[nPeak:nPeak+3])
        return fFit

    def components(self, nDay, lstX):
        lstComponents = [lstX[0]*nDay] # start with slope
        for nPeak in range(1, len(lstX), 3): # add peaks
            lstComponents.append(self.peak(nDay, lstX[nPeak:nPeak+3]))
        return lstComponents
        
    def peak(self, nDay, lstPeak):
        return lstPeak[0]*math.exp(-(nDay-lstPeak[1])**2/lstPeak[2])
