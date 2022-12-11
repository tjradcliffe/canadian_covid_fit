"""
Download data from Our World in Data, extract Canadian hospitalization data
and fit it with a series of Gaussian waves. The code currently expects 8 waves.
Data is only downloaded if current data file is at least 12 hours old.
"""
from datetime import datetime

from download_covid_canada import *
from extract_hospitalized import extractHospitalized
from peak_fitter import fitPeaks
from plot_fit import plotFit
from plot_parameters import plotParameters
from generate_montage import generateMontage
from seirs_model_objective import fitSeirsModel

# download if not done so in the past 12 hours
strFilename = "canada-covid-data.csv"
strURL = "https://health-infobase.canada.ca/src/data/covidLive/covid19-epiSummary-hospVentICU.csv"
download_data(strURL, strFilename)

# extract hospitalization data
strSource = strFilename
strOutputFile = "can_hosp_patients.csv"
pLastDate = extractHospitalized(strSource, strOutputFile)

print("Data written to:", strOutputFile)
print("Last date with data was:", pLastDate.date(), "which was", (datetime.today()-pLastDate).days, "days ago")

# fit the peaks
fitPeaks(strOutputFile)

# fit to the SEIRS model output
fitSeirsModel(strOutputFile)

# plot the fit and the scaled/shifted model
plotFit(strOutputFile)

# plot the parameters
strFilename = strOutputFile.replace(".csv", "_parameters.csv")
plotParameters(strFilename)

# generate montage image
strToday = str(datetime.today().date())
lstImages = [strToday+"_can_hosp_patients.png", strToday+"_can_hosp_patients_wave_area_cut.png", 
strToday+"_can_hosp_patients_wave_spacing_cut.png", strToday+"_can_hosp_patients_wave_width_cut.png"]
strOutput = "combined.png"
generateMontage(lstImages, strOutput)
