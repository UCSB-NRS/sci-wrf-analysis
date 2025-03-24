# Assessment of WRF Skill in Simulating Low Clouds and Fog for Santa Cruz Island
Using a combination of remote sensing data and weather station observational data, we are working to evaluate a 1km resolution downscaled Weather Research and Forecasting (WRF) model's skill in simulating low clouds and fog. 

__Highlighted Notebooks:__
[WRF / GOES Low Cloud Comparison (wrf-python clc)](./notebooks/wrf-goes-low-clouds.ipynb)
[WRF / GOES Low Cloud Comparison (WRF CLDFRA)](./notebooks/wrf-goes-cldfra-low-clouds.ipynb)
- [Presentation from these Notebooks](https://docs.google.com/presentation/d/1s7BILaJ4PMVKDwkKGN6IyHNXfBf6qOqc/edit?usp=sharing&ouid=114113173409564571538&rtpof=true&sd=true)
Both of these notebooks compare WRF outputs representing low clouds against a GOES-derived coastal low cloud dataset (Clemesha, 2021) for Santa Cruz Island. The difference between the notebooks is that the first uses the wrf-python package's function wrf.get_cloudfrac(), which is based on relative humidity values in the vertical column, while the second uses the variable CLDFRA, which is part of the radiation scheme. The takeaway from these analyses is that representing low clouds using CLDFRA is better than using wrf-python's function at capturing both temporal and spatial trends, and that WRF overall does a good job of capturing temporal trends in coastal low cloud presence. 

These analyses are part of a broader effort of examining WRF's skill at simulating fog. If WRF was unable to simulate low clouds, for which we have a robust satellite derived dataset, then it would not be able to simulate fog, for which data availability is much more sparse. Given that it performs fairly well with low clouds, we can continue on to fog analyses. 

A caveat of this analysis is that this GOES dataset is available for daylight hours only, which is drawback given that most fog occurs at night. A 4km resolution GOES derived dataset does exist that includes night observations, and we are currently waiting to receive this dataset. 

__Figures generated from these datasets:__
- [Monthly Aggregated Frequency Figures - 1996-2017](https://drive.google.com/drive/folders/1tzEwrGnCRC0Ht0t4o9Azcv7LLSvajjDK?usp=sharing)
- [Yearly Aggregated Frequency Figures - 1996-2017](https://drive.google.com/drive/folders/1OHOLuQCc5ZVLK1tqfUw77sgbSJKhRNU1?usp=sharing)

__Datasets:__  

_GOES Coastal Low Clouds - 1km resolution, 1996-2019, daylight hours._  
Clemesha, R. E, et al. (2021). A high-resolution record of coastal clouds and fog and their role in plant distributions over San Clemente Island, California. Environmental Research Communications, 3(10), 105003. DOI 10.1088/2515-7620/ac2894  

_1km Resolution Downscaled WRF Model Outputs:_  
Provided UCSB CLIVAC Lab  

_Observational weather station data, including fog harp fog drip data:_  
Provided by Chris Still (working on publishing this)


