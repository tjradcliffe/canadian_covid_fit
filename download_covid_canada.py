from download_covid_data import *

strFilename = "canada-covid-data.csv"
strURL = "https://health-infobase.canada.ca/src/data/covidLive/covid19-epiSummary-hospVentICU.csv"
download_data(strURL, strFilename)
