
from datetime import datetime
import os.path
import sys
from time import strftime
from PIL import Image

nRowSize = 2
nMargin = 0

def generateMontage(lstFilenames, strOutput):
    lstImages = [Image.open(strFilename) for strFilename in lstFilenames]

    nWidth = max(pImage.size[0] + nMargin for pImage in lstImages)*nRowSize#//2
    nHeight = sum(pImage.size[1] + nMargin for pImage in lstImages)#//2
    pMontage = Image.new(mode='RGBA', size=(nWidth, nHeight), color=(0,0,0,0))

    nMaxX = 0
    nMaxY = 0
    nOffsetX = 0
    nOffsetY = 0
    for nI, pImage in enumerate(lstImages):
#        pImage.thumbnail((pImage.size[0]//2, pImage.size[1]//2), Image.Resampling.LANCZOS)
        pMontage.paste(pImage, (nOffsetX, nOffsetY))

        nMaxX = max(nMaxX, nOffsetX + pImage.size[0])
        nMaxY = max(nMaxY, nOffsetY + pImage.size[1])

        if nI % nRowSize == nRowSize-1:
            nOffsetY = nMaxY + nMargin
            nOffsetX = 0
        else:
            nOffsetX += nMargin + pImage.size[0]

    pMontage = pMontage.crop((0, 0, nMaxX, nMaxY))
    pMontage.save(strOutput)

if __name__ == '__main__':
    strToday = str(datetime.today().date())

    lstImages = [strToday+"_can_hosp_patients.png", strToday+"_can_hosp_patients_wave_area_cut.png", 
    strToday+"_can_hosp_patients_wave_spacing_cut.png", strToday+"_can_hosp_patients_wave_width_cut.png"]
    
    strOutput = "combined.png"
    
    generateMontage(lstImages, strOutput)
    