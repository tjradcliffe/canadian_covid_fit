# canadian_covid_fit
System to download and fit Canadian covid hospitalization data

## Background

I wrote this to scratch an itch: I wanted to feel like I had some idea of what was going on in Canada with covid in 2022 even though our "public health" authorities had completely abandoned any pretense of caring about public health. Covid testing has been spotty and some governments, particularly the NDP in BC, have done everything in their power to suppress what little data they are still gathering.

Hospitalization data are relatively hard for political parties to coerce people into lying about, and the Canadian data showed a definite peaks that looked pretty Gaussian. I tried fitting the data to a series of Gaussians and it worked really well. As more omicron peaks accumulated it became apparent that they had really consistent parameters: 95 day spacing, 30 day width, and half a million person-days in hospital.

At the same time I was working on a susceptible/exposed/infectious/recovered/susceptible (SEIRS) model of pandemic spread that had only a few free parameters and produced waves that looked a lot like what I was seeing in the data. By fiddling with the immunity-waning parameters, so immunity vanishes on a sigmoid between 15 and 60 days after recovery, I was able to get peak spacing, widths, and amplitudes that looked a lot like what we are seeing with omicron, so I added that curve--scaled and shifted--to the fit.

NOTE: this code has not been run on Windows or Mac. It'll probably work, but YMMV.

## Dependencies

As well as numpy and matplotlib, which you probably already have if you're reading this, you'll need to:

    pip install simple_minimizer

to get the nonlinear minimizer I'm using.

## How To Run It

    python3 decompose_can_covid_hosp_data.py

This will:

1. Download data from Health Canada to canada-covid-data.csv
2. Extract the hospitalization numbers to can_hosp_patients.csv
3. Fit the data to a series of Gaussian peaks. This will create the files: can_hosp_patients_fit.csv, can_hosp_patients_diff.csv, and can_hosp_patients_parameters.csv
4. Fit the SEIRS model data to the omicron era peaks
5. Plot the data, fit, and SEIRS model to YYYY-MM-DD_can_hosp_patients.png
6. Plot the area, spacing, and width of the fitted peaks to their own image files
7. Create a montage, combined.png, of all the generated images

The parameter files have _cut in the name which indicates the omicron and pre-omicron eras have been fit separately, which is part of the plotting process. Each parameter is fitted with a line to get a sense of the trend. Health Canada updates their data a couple of times a month, so things are usually between one and three weeks out of date. The download only occurs if the canada-covid-data.csv file is more than 12 hours old.

I've written up some discussion of the results on [my substack](https://world_of_wonders.substack.com) and will likely take one last pass at a write-up before abandoning this project. It has been a hobby over the past six months or so, but at this point I think I've learned what I can from it.

## The Future

I originally thought it was pretty likely that we were going to see an endless series of distinct waves in Canada, but based on the SEIRS model and the slight trends in the Gaussian parameters it now looks likely that we'll move to a high constant level of hospitalizations for covid, in the range of 5000-6000 people in hospital all the time.  Canada has about 2.5 hospital beds per 1000 people, and we have 38 million people, so that implies a total of 95,000 hospital beds, about 7% of which will be taken up by covid patients in perpetuity.

The [average covid patient](https://www.cihi.ca/sites/default/files/document/cost-covid-19-other-hospitalizations-2019-2021-data-tables-en.xlsx) stays in hospital 15 days at a cost of $23,111 (2020 dollars), or $1540/day, so the daily cost of 5500 people in hospital is just shy of a million dollars, for around $350 million per year total hospitalization costs. 

5500 people in hospital for 15 days each implies 134,000 distinct individuals in hospital each year, of which 18% will die based on current data, for around 24,000 deaths per year--463 per week, 66 per day--in Canada from covid, every year from now on. That will cement covid as [the third leading cause of death in Canada](https://www.finder.com/ca/what-are-the-top-10-causes-of-death-in-canada), at about 1/3 the rate of cancer deaths and 1/2 the rate of deaths from heart disease. It is about five times the death rate from flu and pneumonia.

Vaccination is not enough to prevent this future. Mandatory N95 wearing at all indoor public places and crowded outdoor spaces until we upgrade or install ventilation, filtration, and UV systems capable of cleaning our indoor air are required. These are engineering solutions which medical doctors are not competent to comment on, much less implement. We need an engineering-led effort to curb airborne infectious diseases, and universal indoor N95 mandates until that effort is successful.

Anyone who does not N95 in all indoor public spaces really needs to look at themselves in the mirror each morning and say, "I don't care that sixty-six Canadians are going to die of a preventable disease today." Because they don't.
