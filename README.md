# Merfish python pons
This is the code to replicate the cell by gene matrices used in the paper "A spatially-resolved
transcriptional atlas of the murine dorsal pons at single-cell resolution" by Nardone et al.

## Installation

* Create as usual a new `env`, I will name it cell_by_gene, but it can be anything :
  * `conda create --name merfish_pons python=3.8`
  * Activate the new env: 

    `conda activate merfish_pons` and then install the pip package:
  
    `pip install https://github.com/acycliq/merfish_python_pons/raw/master/dist/merfish_pons-0.0.1-py3-none-any.whl`

## Usage
You can download Merfish raw and processed data from the BIDMC repository [here](https://research.bidmc.harvard.edu/datashare/DataShareInfo.ASP?Submit=Display&ID=7) 
It is assumed that they are in a nested folder with the following structure:
```
MsBrain_Eg1_VS6_JH_V6_05-02-2021
        |
        |
        |
      region_0
        |---- detected_transcripts.csv
        |---- cell_metadata.csv
        |
      images
        |---- manifest.json 
        |---- micron_to_mosaic_pixel_transform.csv
        |---- mosaic_DAPI_z3.tif  
        
```
The `manifest.json` file may be missing from some folders.

To get the cell by gene
matrix for a particular slice you need to get first the configuration settings for that
slice and then call the app method as shown below.
Note that the root arg in the get_config() method should point to the parent folder 
where the raw data are saved.
```
Python 3.8.18 | packaged by conda-forge | (default, Oct 10 2023, 15:37:54) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> import import merfish_python_pons as pons
>>> import os
>>> 
>>> root = os.path.join('path/to/folder/with/merfish/data')
>>> region_id = 'region_0'
>>> slice_id = "MsBrain_Eg1_VS6_JH_V6_05-02-2021"
>>> cfg = pons.config.get_config(root=root, slice_id=slice_id, region_id=region_id)
>>> df = pons.app(cfg)
>>> df.head()

>>> print(df.head())
                                         8030451A03Rik  9130024F11Rik  9630002D21Rik  ...  Blank-67  Blank-68  Blank-69
                                                                                      ...
153127751520141260813562351177982035458            0.0            0.0            0.0  ...       0.0       0.0       0.0
166271953404365183309737552786130502029            0.0            0.0            0.0  ...       0.0       0.0       0.0
177380451537047124052019662406619664581            0.0            0.0            0.0  ...       0.0       0.0       0.0
179975272202797958871555878915327831077            0.0            0.0            0.0  ...       0.0       0.0       0.0
205448018040433558377739476266679963740            0.0            0.0            0.0  ...       0.0       0.0       0.0

[5 rows x 385 columns]
>>> 
>>> df.shape
(16759, 385)
>>> 
```