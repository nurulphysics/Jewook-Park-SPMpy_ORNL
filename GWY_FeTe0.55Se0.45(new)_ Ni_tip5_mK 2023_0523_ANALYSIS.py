# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

#
# # SPMpy 
# * Authors : Dr. Jewook Park at CNMS, ORNL
#     * Center for Nanophase Materials Sciences (CNMS), Oak Ridge National Laboratory (ORNL)
#     * email :  parkj1@ornl.gov
#         
# > **SPMpy** is a Python package to analyze scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques and utilizes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools available in the [scientific Python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
#
# >  **SPMpy** is an open-source project. (Github: https://github.com/jewook-park/SPMpy_ORNL )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 

# # Experimental Conditions 
#
# ## Data Acquistion date 
# * 2023 0523 FeTe0.55Se0.45 Ni tip5 mK Jewook
# ## Measurement temp
# * <font mcolor= Blue, font size="5" >40 mK </font> 
#     * Cleaving at RT in Load-Lock chamber 
#     * UHV condition (<5E-10Torr)
#
# ## **Sample**
# * <font mcolor= Blue, font size="5" > $FeTe_{0.55}Se_{0.45}$ (new batch) </font> 
#     * Cleaving: @ UHV Loadlock chamber, Room temp.
# ## **Tip: Electro chemically etched Ni Tip:  <font color= Blue, font size="5" > Spin-Polarized </font>  tip**
# ## <font color= red > No Magnetic field 0T (Z)   </font>

# # <font color= orange > 0. Preparation  </font>

# + jp-MarkdownHeadingCollapsed=true
#############################
# check all necessary package
########################################
#       import modules
#########################################


import glob
import os
from warnings import warn
import math
from warnings import warn
import re
from IPython.display import display, Latex

#install pandas 

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns
import skimage

from skimage import exposure

from scipy import signal

from SPMpy_2D_data_analysis_funcs import *
from SPMpy_3D_data_analysis_funcs import *

from SPMpy_fileloading_functions import *

# some packages may be yet to be installed



try:
    from ipyfilechooser import FileChooser
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named ipyfilechooser")
    from ipyfilechooser import FileChooser





try:
    from pptx import Presentation
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named Presentation")
    # !pip install python-pptx
    from pptx import Presentation
    from pptx.util import Inches, Pt

try:
    import nanonispy as nap
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named nanonispy")
    # !pip install nanonispy
    import nanonispy as nap

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named seaborn-image")
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install --upgrade seaborn-image
    import seaborn_image as isns

try:
    import xarray as xr
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named xarray")
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !conda install -c conda-forge xarray dask netCDF4 bottleneck
    import xarray as xr

try:
    import xrft
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named xrft")
    # !pip install xrft
    import xrft
    
    

try:
    import holoviews as hv
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named holoviews')
    # !pip install holoviews 
    import holoviews as hv

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named seaborn_image')
    # !conda install -c conda-forge seaborn-image
    import seaborn_image as isns
    
    
    
try:
    import hvplot.xarray
    import hvplot.pandas 
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named hvplot')
    # !pip install hvplot
    import hvplot.xarray
    import hvplot.pandas 

    
try:
    import plotly.express as px
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named plotly')
    # !pip install plotly
    import plotly.express as px

    
    


try:
    import gwyfile
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named gwyfile')
    # !pip install gwyfile
    import gwyfile

import holoviews as hv
from holoviews import opts
from matplotlib.patches import Rectangle

import panel as pn
import panel.widgets as pnw
from panel.interact import interact
from holoviews.streams import Stream, param
from holoviews import streams

import ipywidgets as ipw


# -

# # <font color= orange > 1. Choose Folder & DataFrame for analysis</font>

# ## 1-1. choose folder 
#

# + jp-MarkdownHeadingCollapsed=true
###########################################
# Create and display a FileChooser widget #
###########################################
"""
file_chooser = FileChooser("")
display(file_chooser)
"""

# -

##############################
# After choose the folder    #
# Files DataFrame            #
##############################
"""
folder_path = file_chooser.selected_path
print("folder_path = ", file_chooser.selected_path)
print("selected file name = ", file_chooser.selected_filename)
from SPMpy_fileloading_functions import files_in_folder

files_df = files_in_folder(folder_path)
"""


# +
#folder_path = file_chooser.selected_path
#print( folder_path)

folder_path = r'C:\Users\gkp\OneDrive - Oak Ridge National Laboratory\0_mK STM DATA\2023\0523 FeTe0.55Se0.45 Ni_tip5_mK_Jewook'

files_df = files_in_folder(folder_path)
# -

# ## 1-2. Choose <font color= orange > GWY </font> file loading to analyze
#
# ### 1.2.0 Choose the file 
# * gwy_analyze

files_df[files_df.type=='gwy']#.file_name.iloc[0]
gwy_files = files_df [files_df.type=='gwy']


# +
# Set the display option to prevent text from being truncated for all columns
pd.set_option('display.max_colwidth', None)

isin_filename = '00003'

print (gwy_files[gwy_files.file_name.str.contains(isin_filename)].file_name)




# +
## Choose target file 
gwy_analyze_filename = gwy_files[gwy_files.file_name.str.contains(isin_filename)].iloc[1].file_name



# -

gwy_analyze_filename

#
#

# ### 1.2.1.  Convert Gwyddion 2D images as Xr  
# $\to $ PANDAS Dataframe 
# $\to $ Dictionary (groups /w different image size) 
# $\to $ Xarray /w 'keys'
#
# #### 1.2.1.1. gwy_img2df : gwy file name from 'gwy_analyze'
# #### 1.2.1.2. gwy_df2xr : gwy_df $\to $ gwy_dict 
# * gwy_df is composed of multiple images $\to $ grouping based on image sizes
# * multiple xr data with the same size 
# * add ref_a0 & q0 based on gwy_analyze file name 
#
# #### 1.2.1.3.  choose the xr data 
# * gwy_dict['gwy_xr2'] 
#
#

# +
gwy_df = gwy_img2df(gwy_analyze_filename)

# Reset the 'display.max_colwidth' option to its default value
pd.reset_option('display.max_colwidth')
# -

gwy_df

gwy_dict = gwy_df2xr (gwy_df)
gwy_dict

# +

gwy_dict = gwy_df2xr (gwy_df)
"""
for keys in list(gwy_dict.keys()):
    print (keys)
for i, keys in enumerate (list(gwy_dict.keys())):
    print(    gwy_dict[keys])
"""


#########################
# add ref a0 & ref_q0  ##
#########################

if 'FeTe0.55Se0.45' in gwy_analyze_filename:
    for key in gwy_dict:
        gwy_dict[key].attrs['ref_a0']=0.38E-9
        gwy_dict[key].attrs['ref_q0']=1/0.38E-9
else: pass



#########################
# add X&Y spacing attrs  ##
#########################

for key in gwy_dict:
    # add X_spacing & Y_spacing
    gwy_dict[key].X.attrs['X_spacing']= ((gwy_dict[key].X.max()-gwy_dict[key].X.min())/gwy_dict[key].dims['X']).values
    gwy_dict[key].Y.attrs['Y_spacing']= ((gwy_dict[key].Y.max()-gwy_dict[key].Y.min())/gwy_dict[key].dims['Y']).values

gwy_dict
# -

# # choose xr file  

# +
gwy_xr = gwy_dict['gwy_xr3']
#gwy_xr.Y

gwy_xr

#gwy_xr[list (gwy_xr.data_vars.keys())[0]].plot()
# -



# +
for ch_i, ch_name in enumerate (gwy_xr.data_vars.keys()):
    print (ch_name)
    
    ch_name_rename = rename_gwy_xr_data_vars(ch_name) 
    print (ch_name_rename)
    gwy_xr = gwy_xr.rename_vars({ch_name:ch_name_rename})
    
gwy_xr


# +

gwy_xr = gwy_intrplt_xr (   gwy_xr)
#gwy_xr
gwy_xr.z_f.plot()

# -

gwy_xr_crop = crop_square(gwy_xr, ch_name = 'z_f_C')
gwy_xr_crop

gwy_xr.z_f.plot()

# +

gwy_xr = gwy_xr_crop
#gwy_xr_crop.z_f.plot()
gwy_xr_crop.z_f_C.plot()

# -

#gwy_xr_zm1_f = filter_diffofgaussians_xr(gwy_xr_zm1,low_sigma= 5,high_sigma=None,overwrite= True)
gwy_xr_f = filter_diffofgaussians_xr(gwy_xr,low_sigma= 3,high_sigma=None,overwrite= True)
#gwy_xr_f = filter_diffofgaussians_xr(gwy_xr,low_sigma= None,high_sigma=5,overwrite= True)

# +
# if gwy data is  not "Corrected" 
filtering_ratio=[0.0, 2]
figsize = (8,4)
#gwy_xr_input = gwy_xr_zm1_f
gwy_xr_input = gwy_xr_f
distance_to_refq0 = 10
peak_detection_min_distance  = 10
#ch_names =['z_f', 'LIX_f']
#ch_names =['z_b', 'LIX_b']

# if gwy data is "Corrected"
ch_names =['z_f_C', 'LIX_f_C']

xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[0],
                        figsize = figsize,filtering_ratio=filtering_ratio,
                        add_guidlines = False)
xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[1],
                        figsize = figsize,filtering_ratio=filtering_ratio,
                        add_guidlines = False )


xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[0],
                        figsize = figsize,filtering_ratio=filtering_ratio,
                        distance_to_refq0 =  distance_to_refq0,
                        peak_detection_min_distance  = peak_detection_min_distance,
                        add_guidlines = True)
xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[1],
                        figsize = figsize,filtering_ratio=filtering_ratio, 
                        distance_to_refq0 = distance_to_refq0, 
                        peak_detection_min_distance  = peak_detection_min_distance,
                        add_guidlines = True )


# +
gwy_xr_f = filter_diffofgaussians_xr(gwy_xr,low_sigma= 3,high_sigma=None,overwrite= True)
gwy_xr_f.z_f.plot(cmap ='copper')
#gwy_xr_f.z_f_C.plot(cmap ='copper')

#gwy_xr_f.z_f_difference_of_gaussians.plot()
#gwy_xr= gwy_xr_f

# +
# if gwy data is  not "Corrected" 
filtering_ratio=[0.0, 2]

"""
xrdata_plot_r_q_space_q3(gwy_xr,ch_name= 'z_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False)
xrdata_plot_r_q_space_q3(gwy_xr,ch_name= 'LIX_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False )


xrdata_plot_r_q_space_q3(gwy_xr,ch_name= 'z_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        distance_to_refq0 = 10,
                        peak_detection_min_distance  =20,
                        add_guidlines = True)
xrdata_plot_r_q_space_q3(gwy_xr,ch_name= 'LIX_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio, 
                        distance_to_refq0 = 10, 
                        peak_detection_min_distance  =20,
                        add_guidlines = True )

# if gwy data pixcel ratio is not 1 (eg, 1024x512 case) 
# use q3_1 (aspect ratio = 2)
xrdata_plot_r_q_space_q3_1(gwy_xr,ch_name= 'z_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False, set_aspect=2)
xrdata_plot_r_q_space_q3_1(gwy_xr,ch_name= 'LIX_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False , set_aspect=2)


xrdata_plot_r_q_space_q3_1(gwy_xr,ch_name= 'z_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        distance_to_refq0 = 10,
                        peak_detection_min_distance  = 8,
                        add_guidlines = True, set_aspect=2)
xrdata_plot_r_q_space_q3_1(gwy_xr,ch_name= 'LIX_f',
                        figsize = (6,3),filtering_ratio=filtering_ratio, 
                        distance_to_refq0 = 10, 
                        peak_detection_min_distance  =8,
                        add_guidlines = True , set_aspect=2)


"""


# if gwy data is "Corrected" 

xrdata_plot_r_q_space_q(gwy_xr,ch_name= 'z_f_C',figsize = (6,3),distance_to_refq0 = 6, peak_detection_min_distance  = 8 ,add_guidlines = False)
xrdata_plot_r_q_space_q(gwy_xr,ch_name= 'LIX_f_C',figsize = (6,3), distance_to_refq0 = 6, peak_detection_min_distance  = 8,add_guidlines = False )


xrdata_plot_r_q_space_q(gwy_xr,ch_name= 'z_b_C',figsize = (6,3),distance_to_refq0 = 6, peak_detection_min_distance  = 8 ,add_guidlines = True)
xrdata_plot_r_q_space_q(gwy_xr,ch_name= 'LIX_b_C',figsize = (6,3), distance_to_refq0 = 6, peak_detection_min_distance  = 8,add_guidlines = True )

# -

#gwy_xr.z_f.plot()
gwy_xr_f

# +
#gwy_xr.z_f.plot()
gwy_xr_zm1 =  gwy_xr.where(gwy_xr.Y>1.25E-7, drop = True).where(gwy_xr.X>1.25E-7, drop = True)
gwy_xr_zm2 =  gwy_xr.where(
    gwy_xr.Y>1.25E-7, drop = True).where(
    gwy_xr.Y<1.30E-7, drop = True).where(
    gwy_xr.X>1.25E-7, drop = True).where(
    gwy_xr.X<1.30E-7, drop = True)


#gwy_xr_zm2

#xrdata_plot_r_q_space_q(gwy_xr_zm1,distance_to_refq0 = 1, peak_detection_min_distance  = 1, add_guidlines = False)


# -


gwy_xr_f

# +
gwy_xr_zm1 =  gwy_xr.where(gwy_xr_f.Y>1E-8, drop = True).where(gwy_xr_f.X>1E-8, drop = True)
gwy_xr_zm2 =  gwy_xr.where(
    gwy_xr_f.Y>1.0E-8, drop = True).where(
    gwy_xr_f.Y<1.30E-8, drop = True).where(
    gwy_xr_f.X>1.0E-8, drop = True).where(
    gwy_xr_f.X<1.30E-8, drop = True)



# -

#gwy_xr_zm1
gwy_xr

#gwy_xr_zm1_f = filter_diffofgaussians_xr(gwy_xr_zm1,low_sigma= 5,high_sigma=None,overwrite= True)
gwy_xr_f = filter_diffofgaussians_xr(gwy_xr,low_sigma= 5,high_sigma=None,overwrite= True)

# +
# if gwy data is  not "Corrected" 
filtering_ratio=[0.0, 2]
#gwy_xr_input = gwy_xr_zm1_f
gwy_xr_input = gwy_xr_f
distance_to_refq0 = 12
peak_detection_min_distance  = 6
#ch_names =['z_f', 'LIX_f']
#ch_names =['z_b', 'LIX_b']

# if gwy data is "Corrected"
ch_names =['z_f_C', 'LIX_f_C']

xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[0],
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False)
xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[1],
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        add_guidlines = False )


xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[0],
                        figsize = (6,3),filtering_ratio=filtering_ratio,
                        distance_to_refq0 =  distance_to_refq0,
                        peak_detection_min_distance  = peak_detection_min_distance,
                        add_guidlines = True)
xrdata_plot_r_q_space_q3(gwy_xr_input,ch_name= ch_names[1],
                        figsize = (6,3),filtering_ratio=filtering_ratio, 
                        distance_to_refq0 = distance_to_refq0, 
                        peak_detection_min_distance  = peak_detection_min_distance,
                        add_guidlines = True )


# -

xrdata_plot_r_q_space_q(gwy_xr_zm1,ch_name= 'z_f',figsize = (5,2.5), distance_to_refq0 = 8, peak_detection_min_distance  = 8, add_guidlines = True)
xrdata_plot_r_q_space_q(gwy_xr_zm1,ch_name= 'LIX_f',figsize = (5,2.5), distance_to_refq0 = 8, peak_detection_min_distance  = 8, add_guidlines = True)


















xrdata =  gwy_xr
#xrdata.dims['X']
#xrdata.X.attrs['X_spacing']= ((xrdata.X.max()-xrdata.X.min())/xrdata.dims['X']).values
#xrdata.Y.attrs['Y_spacing']= ((xrdata.Y.max()-xrdata.Y.min())/xrdata.dims['Y']).values
xrdata.X.X_spacing


def xrdata_plot_r_q_space(xrdata, ch_name= 'z_f',  distance_to_refq0 = 4):
    from matplotlib_scalebar.scalebar import ScaleBar
    from matplotlib.patches import Circle
    xrdata_fft = twoD_FFT_xr(xrdata)
    xrdata_fft_zm = fft_masking_near_q0only (xrdata_fft,filtering_ratio=[0.3, 2])

    
    fig, axes = plt.subplots (1,2, figsize = (8,4))
    axs = axes.ravel()
    if 'z_' in ch_name:
        cmap_r = 'copper'
        cmap_q = 'Greys'
    if 'LIX_' in ch_name:
        cmap_r = 'bwr'
        cmap_q = 'Blues'
    
    isns.imshow (xrdata[ch_name], robust = True, ax = axs[0],cmap= cmap_r, dx =xrdata[ch_name].X.X_spacing*1E9, units = "nm" )
    
    isns.imgplot(xrdata_fft.z_f_fft.where(xrdata_fft.mask_ == 1, drop = True), robust = True, ax = axs[1], cmap= cmap_q)

    scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                        units = "1/nm",
                        dimension="si-length-reciprocal",    
                        color='k'                   )
    # dx = pixel size for scale bar 
    # 1E-9 for "1/nm" unit
    # use separate scalebar option to adjust scale bar color 
    axs[1].add_artist(scalebar)


    image_shape = axs[1].get_images()[0].get_array().shape
    #get center point from image shape of plot 
    # or the center is not correct
    # fft_center  = ( xrdata_fft.z_f_fft.freq_X.shape[0] / 4,  xrdata_fft.z_f_fft.freq_X.shape[0] / 4)
    # it is not center position

    fft_center  = ( image_shape[0] / 2,  image_shape[0] / 2)
    q0_r = get_px_from_fft_coord(xrdata_fft, xrdata_fft.ref_q0)
    circle = Circle(xy = fft_center, radius= float (q0_r), fill= False, edgecolor = 'red', alpha =0.5)

    axs[1].add_patch(circle)

    from skimage.feature import peak_local_max
    im = xrdata_fft.z_f_fft.where(xrdata_fft.mask_ == 1, drop = True).fillna(0).values
    #z_f_fft_peak.fillna( z_f_fft_peak.min()).values

    coordinates = peak_local_max(im, min_distance= 20)
    #coordinates ==> find max 
    # Calculate distances between the points and the disk
    distances = np.sqrt((coordinates[:, 0] - fft_center[0]) ** 2 + (coordinates[:, 1] - fft_center[1]) ** 2)
    # distances from fft_center to each points in coordiates 

    # Find the index of the close points
    distance_to_q0r = 4
    close_points_indx = np.abs(distances-q0_r.values) < distance_to_q0r
    #closest_point_index = np.argmin(np.abs(distances-q0_r.values))
    # distance from the circle 
    closest_point = coordinates[close_points_indx]
    #closest_point  = peak points that is closed to ref_q0 ( < distance_to_q0r )

    circle_1 = Circle(xy = fft_center, radius= float (q0_r-distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'red', alpha =0.1)
    circle_2 = Circle(xy = fft_center, radius= float (q0_r+distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'red', alpha =0.1)
    axs[1].add_patch(circle_1)
    axs[1].add_patch(circle_2)

    axs[1].scatter(closest_point[:, 1], closest_point[:, 0], c='r',marker='o', s = 40 , alpha = 0.3)

    plt.tight_layout()
    plt.show()
    return 

gwyxr_fft = twoD_FFT_xr(gwy_xr)
gwyxr_fft.ref_q0 
#get_px_ratio_from_fft_coord(gwy_xr,test_fft.ref_q0  ).values


# +
gwyxr_fft_zm = fft_masking_near_q0only (gwyxr_fft, ch_name = 'z_f_fft', filtering_ratio=[0.2, 2])
#gwyxr_fft_zm = fft_masking_near_q0only (gwyxr_fft, ch_name = 'z_f_C_fft', filtering_ratio=[0.3, 2])

#gwyxr_fft_zm.mask_.plot()

isns.imgplot(gwyxr_fft_zm.z_f_fft.where(gwyxr_fft_zm.mask_ ==1, drop = True), robust = True,  cmap= 'Greys')
#isns.imgplot(gwyxr_fft_zm.z_f_C_fft.where(gwyxr_fft_zm.mask_ ==1, drop = True), robust = True,  cmap= 'Greys')
# -

xrdata_plot_r_q_space(gwy_xr,ch_name= 'z_f')
xrdata_plot_r_q_space(gwy_xr,ch_name= 'LIX_f')


fft_plot_ref_q0(gwyxr_fft_zm, distance_to_refq0= 10)

# +
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Circle

fig, ax = plt.subplots (1,1, figsize = (4,4))
isns.imgplot(gwyxr_fft_zm.z_f_fft.where(gwyxr_fft_zm.mask_ == 1, drop = True), robust = True, ax = ax, cmap= 'Greys')

scalebar = ScaleBar(dx = gwyxr_fft_zm.freq_X.spacing*1E-9,
                    units = "1/nm",
                    dimension="si-length-reciprocal",    
                    color='k'                   )
# dx = pixel size for scale bar 
# 1E-9 for "1/nm" unit
# use separate scalebar option to adjust scale bar color 
ax.add_artist(scalebar)


image_shape = ax.get_images()[0].get_array().shape
#get center point from image shape of plot 
# or the center is not correct
# fft_center  = ( gwyxr_fft_zm.z_f_fft.freq_X.shape[0] / 4,  gwyxr_fft_zm.z_f_fft.freq_X.shape[0] / 4)
# it is not center position

fft_center  = ( image_shape[0] / 2,  image_shape[0] / 2)
q0_r = get_px_from_fft_coord(gwyxr_fft_zm, gwyxr_fft_zm.ref_q0)
circle = Circle(xy = fft_center, radius= float (q0_r), fill= False, edgecolor = 'red', alpha =0.5)

ax.add_patch(circle)

from skimage.feature import peak_local_max
im = gwyxr_fft_zm.z_f_fft.where(gwyxr_fft_zm.mask_ == 1, drop = True).fillna(0).values
#z_f_fft_peak.fillna( z_f_fft_peak.min()).values

coordinates = peak_local_max(im, min_distance= 20)
#coordinates ==> find max 
# Calculate distances between the points and the disk
distances = np.sqrt((coordinates[:, 0] - fft_center[0]) ** 2 + (coordinates[:, 1] - fft_center[1]) ** 2)
# distances from fft_center to each points in coordiates 

# Find the index of the close points
distance_to_q0r = 4
close_points_indx = np.abs(distances-q0_r.values) < distance_to_q0r
#closest_point_index = np.argmin(np.abs(distances-q0_r.values))
# distance from the circle 
closest_point = coordinates[close_points_indx]
#closest_point  = peak points that is closed to ref_q0 ( < distance_to_q0r )

circle_1 = Circle(xy = fft_center, radius= float (q0_r-distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'red', alpha =0.1)
circle_2 = Circle(xy = fft_center, radius= float (q0_r+distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'red', alpha =0.1)
ax.add_patch(circle_1)
ax.add_patch(circle_2)

ax.scatter(closest_point[:, 1], closest_point[:, 0], c='r',marker='o', s = 40 , alpha = 0.3)

plt.tight_layout()
plt.show()
# -





im
#coordinates

# +

filter_diffofgaussians_xr (test_fft, low_sigma = 2, high_sigma= None, overwrite= True).z_f_fft.plot(robust = True)
# -

#test_fft.coords['freq_X'].shape[0]
test_fft.coords['freq_X']/ 49892190.08561445


def get_px_ratio_from_fft_coord(xrdata_fft, value, coord = 'freq_X' ):
    """
    Calculates the pixel ratio of a value in an FFT coordinate.
    always 'freq_X'=' freq_Y'

    Args:
        xrdata_fft: An xarray DataArray containing the FFT data.
        coord: The coordinate name of the FFT data.
        value: The value from the coordinate for which to find the pixel ratio.

    Returns:
        (The pixel ratio, which is a floating-point number between 0 and 1.)
         * (The image size, which is from shape (int))
        To draw circle based on 1/r [nm]

    Raises:
        ValueError: If the given value is out of range.
    """

    if value > xrdata_fft.coords[coord].max():
        raise ValueError("Given value is out of range")

    return (value/xrdata_fft.coords[coord].max()) * xrdata_fft.coords[coord].shape[0]*0.5



# ##  FFT filtering based on ref_q0
# * select area 
#     * 1/10 * q0  <  area_radius < 3*q0
#     
#     

 get_px_ratio_from_fft_coord(test_fft,test_fft.ref_q0  ).values


xrdata_fft.freq_X.spacing/2


def fft_masking_near_q0only (xrdata_fft, filtering_ratio = [0.2, 3]):
    xrdata_fft = test_fft
    from skimage.draw import disk
    data_shape = xrdata_fft[list(xrdata_fft.data_vars)[0]].shape
    mask_disk = np.zeros(data_shape, dtype=np.uint8)
    disk_center = ( data_shape[0] / 2, data_shape[1] / 2)

    disk_radius = get_px_ratio_from_fft_coord(xrdata_fft,xrdata_fft.ref_q0  ).values

    rr_max, cc_max = disk(disk_center, disk_radius*filtering_ratio[1])
    mask_disk[rr_max, cc_max] = 1


    rr_min, cc_min = disk(disk_center, disk_radius*filtering_ratio[0])
    mask_disk[rr_min, cc_min] = 0
    mask_disk

    xrdata_fft['mask_'] = xrdata_fft.z_f_fft.copy()
    xrdata_fft['mask_'].values = mask_disk
    return xrdata_fft


filtering_ratio[0]

test_fft_zm = fft_masking_near_q0only (test_fft,filtering_ratio=[0.3, 2])
test_fft_zm


# +
## fft filtering + zoom + plot 

# +

from matplotlib_scalebar.scalebar import ScaleBar
fig, ax = plt.subplots (1,1, figsize = (4,4))
isns.imgplot(test_fft_zm.z_f_fft.where(test_fft_zm.mask_ ==1, drop = True), robust = True, ax = ax, cmap= 'Blues')
scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                    units = "1/nm",
                    dimension="si-length-reciprocal",    
                    color='k'                   )
# dx = pixel size for scale bar 
# 1E-9 for "1/nm" unit
# use separate scalebar option to adjust scale bar color 
ax.add_artist(scalebar)
plt.tight_layout()
plt.show()

# +
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Circle

fig, ax = plt.subplots (1,1, figsize = (4,4))
isns.imgplot(test_fft_zm.z_f_fft.where(test_fft_zm.mask_ ==1, drop = True), robust = True, ax = ax, cmap= 'Blues')

scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                    units = "1/nm",
                    dimension="si-length-reciprocal",    
                    color='k'                   )
# dx = pixel size for scale bar 
# 1E-9 for "1/nm" unit
# use separate scalebar option to adjust scale bar color 
ax.add_artist(scalebar)




image_shape = ax.get_images()[0].get_array().shape
#get center point from image shape of plot 
# or the center is not correct
# fft_center  = ( test_fft_zm.z_f_fft.freq_X.shape[0] / 4,  test_fft_zm.z_f_fft.freq_X.shape[0] / 4)
# it is not center position

fft_center  = ( image_shape[0] / 2,  image_shape[0] / 2)
q0_r = get_px_ratio_from_fft_coord(test_fft,test_fft.ref_q0  ).values
circle = Circle(xy = fft_center, radius= float (q0_r), fill= False, edgecolor = 'red', alpha =0.5)


ax.add_patch(circle)




plt.tight_layout()
plt.show()
# -

# ## draw Z & corresponding FFT together 
#



# +
test_fft_nearq0 =  fft_masking_near_q0only(test_fft, filtering_ratio = [0.6,1.2])
#test_fft_nearq0.mask_.plot()

isns.imgplot(test_fft_nearq0.z_f_fft.where(test_fft_nearq0.mask_ == 1, drop = True), robust = True)
                             
# -

z_f_fft_peak.fillna(0)

# +
z_f_fft_peak = test_fft_nearq0.z_f_fft.where(test_fft_nearq0.mask_ == 1, drop = True)
img = z_f_fft_peak.fillna( z_f_fft_peak.min()).values

peaks_idx  = skimage.feature.peak_local_max(img, min_distance= 20)
peaks_idx

# -



z_f_fft_peak.iloc[[peaks_idx]:,]

# +
from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage import data, img_as_float

im =img
# image_max is the dilation of im with a 20*20 structuring element
# It is used within peak_local_max function
image_max = ndi.maximum_filter(im, size=5, mode='constant')

# Comparison between image_max and im to find the coordinates of local maxima
coordinates = peak_local_max(im, min_distance= 20)

# display results
fig, axes = plt.subplots(1, 3, figsize=(8, 3), sharex=True, sharey=True)
ax = axes.ravel()
ax[0].imshow(im, cmap=plt.cm.gray)
ax[0].axis('off')
ax[0].set_title('Original')

ax[1].imshow(image_max, cmap=plt.cm.gray)
ax[1].axis('off')
ax[1].set_title('Maximum filter')

ax[2].imshow(im, cmap=plt.cm.gray)
ax[2].autoscale(False)
ax[2].plot(coordinates[:, 1], coordinates[:, 0], 'r.')
ax[2].axis('off')
ax[2].set_title('Peak local max')

fig.tight_layout()

plt.show()

# +
import matplotlib.pyplot as plt

# Figure와 Axes 생성
fig, ax = plt.subplots()

# 이미지 그리기
# ...

# 이미지의 shape 얻기
image_shape = ax.get_images()[0].get_array().shape

# -

axes = isns.imgplot(xrdata_fft.z_f_fft.where(xrdata_fft.mask_ ==1, drop = True), robust = True)
scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                    units = "1/nm",
                    dimension="si-length-reciprocal",    
                    color='k'                   )
axes.add_artist(scalebar)
#dimension = "si-reciprocal", dx = xrdata_fft.freq_X.spacing*1E-9  , units = "1/nm", location = 'center')

xrdata_fft['mask_'] = xrdata_fft.z_f_fft.copy()
xrdata_fft['mask_'].values = mask_disk

# xrdata_fft.mask_.plot()
# rdata_fft.z_f_fft.where(xrdata_fft.mask_ ==1, drop = True).plot(robust = True)


from matplotlib_scalebar.scalebar import ScaleBar
axes = isns.imgplot(xrdata_fft.z_f_fft.where(xrdata_fft.mask_ ==1, drop = True), robust = True)
scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                    units = "1/nm",
                    dimension="si-length-reciprocal",    
                    color='k'                   )
axes.add_artist(scalebar)
#dimension = "si-reciprocal", dx = xrdata_fft.freq_X.spacing*1E-9  , units = "1/nm", location = 'center')

xrdata_fft.freq_X.spacing

xrdata_fft.z_f_fft.where(mask_disk == 1, drop = True ).plot()

isns.imshow (mask_disk)

# +
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import numpy as np

# Load the image
#test_fft = np.load('test_fft.npy')

# Create a figure and axes
fig, axes = plt.subplots(1, 1, figsize=(4, 4))

# Display the image
isns.imshow(test_fft.z_f_fft, ax = axes, robust=True, perc=(2, 99))

# Calculate the center and radius of the circle
center1 = ( test_fft.freq_X.shape[0] / 2,  test_fft.freq_X.shape[0] / 2)
get_px_ratio_from_fft_coord(test_fft,test_fft.ref_q0  )
radius = 52.74530829
# Create a red circle
circle = Circle(center1, radius, color='red', fill= False)
# Add the circle to the plot
axes.add_patch(circle)

axes.set_aspect('equal')

# Show the plot
plt.show()


# +
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# Create an image.
image = np.random.randint(0, 255, size=(100, 100))

# Create a circle.
center = (50, 50)
radius = 25

# Create a mask for the circle.
mask = np.zeros((100, 100), dtype=bool)  # <- Remove the `np.bool` type.
circle = Circle(xy=center, radius=radius, color='red')
mask = circle.contains(np.arange(100), np.arange(100))

# Filter the image.
filtered_image = image[mask]

# Plot the filtered image.
plt.imshow(filtered_image)
plt.show()



# +
###### from matplotlib.patches import Circle
fig,axes = plt.subplots(1,1, figsize = (4,4))
isns.imshow(test_fft.z_f_fft,robust = True, perc = (2,99), ax = axes )

image_width = test_fft.coords["freq_X"].max() - test_fft.coords["freq_X"].min()
image_height = test_fft.coords["freq_Y"].max() - test_fft.coords["freq_Y"].min()

#axes.imshow(test_fft.z_f_fft)
center1 = (0, 0)    # Center coordinates of the circle (x, y)
radius = 2631578947.368421* min(image_width, image_height)  # 반지름 (스케일 조정)

# Draw red  circle
#circle1 = plt.Circle(center1, radius, color='red', fill=True)
# Add the circle to the plot
circle = Circle(center1, radius, color='red', fill=True)

plt.show()

# +
import numpy as np
import matplotlib.pyplot as plt
from skimage.draw import draw_disk

# Create an image.
image = np.random.randint(0, 255, size=(100, 100))

# Create a circle.
center = (50, 50)
radius = 25

# Draw the circle.
disk = draw_disk(image.shape, center, radius)

# Create a mask for the circle.
mask = disk > 0

# Filter the image.
filtered_image = image[mask]

# Plot the filtered image.
plt.imshow(filtered_image)
plt.show()

# -

isns.imshow(mask)

# +
axes.add_patch(circle)


#axes.add_patch(circle1)
# -

# Show the plot


1/0.38E-9

test_fft.z_f_fft


1/(test.X.max()-test.X.min())/677 < 2631578947.368421

1/(test.X.max()-test.X.min())

img = filter_convert2grayscale( test.z_f).values
#img = test.z_f.values


#adjust_gamma
adj_gamma = isns.filterplot(img, skimage.exposure.adjust_gamma, gamma=10,gamma_gain =0.5, robust = True )

isns.implemented_filters.keys()

isns.filterplot(img, 'diff_of_gaussians', low_sigma = 1)

filter_diffofgaussians_xr


# +
test_fft = twoD_FFT_xr(filter_diffofgaussians_xr(test, low_sigma=1,high_sigma=None))
test_fft

#isns.imshow(skimage.filters.difference_of_gaussians(img, low_sigma=1))

# +

image_width = test_fft_dog.coords["freq_X"].max() - test_fft_dog.coords["freq_X"].min()
image_height = texst_fft_dog.coords["freq_Y"].max() - test_fft_dog.coords["freq_Y"].min()

# -

# %matplotlib inline





# +
from matplotlib.patches import Circle
fig,axes = plt.subplots(1,1, figsize = (4,4))
#isns.imshow(test_fft_dog.z_f_difference_of_gaussians_fft,robust = True, perc = (2,99), ax = axes )

image_width = test_fft_dog.coords["freq_X"].max() - test_fft_dog.coords["freq_X"].min()
image_height = test_fft_dog.coords["freq_Y"].max() - test_fft_dog.coords["freq_Y"].min()

axes.imshow(test_fft_dog.z_f_difference_of_gaussians_fft)
center1 = (0, 0)    # Center coordinates of the circle (x, y)
radius = 2631578947.368421* min(image_width, image_height)  # 반지름 (스케일 조정)

# Draw red  circle
#circle1 = plt.Circle(center1, radius, color='red', fill=True)
# Add the circle to the plot
circle = Circle(center1, radius, color='red', fill=True)


axes.add_patch(circle)


#axes.add_patch(circle1)

# Show the plot
plt.show()
# -

fig,axes = plt.subplots(1,3,figsize = (6,3))
isns.imshow( test_fft.z_f_fft, ax = axes[0], robust = True)
isns.imshow( test_fft.z_f_difference_of_gaussians_fft, ax = axes[1], robust = True, perc = (90,100))
isns.imshow( filter_diffofgaussians_xr(test_fft, low_sigma=1,high_sigma=None).z_f_difference_of_gaussians_fft_difference_of_gaussians , ax = axes[2], robust = True)


# +
img = filter_convert2grayscale( test.z_f).values


fig,axes = plt.subplots(ncols = 3,nrows = 2, figsize=(8, 5))
axs = axes.ravel()

isns.imshow(img , robust =True, ax = axs[0])
axs[0].set_title ('original_robust', size ='small')

#adjust_gamma
gamma = 2
gamma_gain =0.5
img_adjust_gamma = exposure.adjust_gamma(img, 
                                         gamma = gamma, 
                                         gain = gamma_gain)
isns.imshow(img_adjust_gamma, robust =True, ax = axs[1])
axs[1].set_title(
    f'adjust_gamma \n gamma = { gamma}, \n gamma_gain =  {gamma_gain }',
    size = 'small')

#adjust_log
log_gain = 0.5
img_adjust_log = exposure.adjust_log(img, gain = log_gain)
isns.imshow(img_adjust_log, robust =True, ax = axs[2])
axs[2].set_title(
    f'adjust_log \n gain = {log_gain}', 
    size ='small')

#adjust_sigmoid 
cutoff=0.5
sigmoid_gain=10
img_adjust_sigmoid = exposure.adjust_sigmoid(img, 
                                             cutoff = 0.5,
                                             gain = sigmoid_gain,
                                             inv = False)

isns.imshow(img_adjust_sigmoid, robust =True, ax = axs[3])
axs[3].set_title(
    f'adjust_gamma \n cutoff = {cutoff} \n sigmoid_gain = {sigmoid_gain}', 
    size = 'small')


#img_equalize_adapthist
# Contrast Limited Adaptive Histogram Equalization (CLAHE)
clip_limit=0.03
img_CLAHE = exposure.equalize_adapthist(img, clip_limit=clip_limit)
isns.imshow(img_CLAHE , robust =True, ax = axs[4])
axs[4].set_title(
    f'CLAHE \n clip_limit= {clip_limit}', 
    size = 'small')


img_eq_hist = exposure.equalize_hist(img)

isns.imshow(img_eq_hist , robust =True, ax = axs[5])

axs[5].set_title('equalize_hist', 
    size = 'small')



fig.tight_layout()
plt.show()
#isns.imshow(exposure.rescale_intensity(test.z_f.values))

# +
# change  Xarrary 



img = filter_convert2grayscale( test.z_f).values



img = exposure.adjust_gamma(test.values, gamma=gamma_value, gain=gamma_gain)

# 새로운 xarray DataArray 생성
adjusted_test = xr.DataArray(img, coords=test.coords, dims=test.dims)


# +
###########################################
#  apply mean rank.mean to xr_gs
############################################
def filter_gs_substract_mean_xr (xrdata_gs,disk_radious=10): 
    """
    substract the mean value to emphasize atomic details
       
    Input data is unsigned 8 bit 

    Parameters
    ----------
    xrdata_gs : Xarray DataSet TYPE
        DESCRIPTION.
        Input data is unsigned 8 bit (0-255)
    disk_radious : TYPE, optional
        DESCRIPTION. The default is 10.
        area radius to get mean value 

    Returns
    -------
    xrdata_gs_sub_mean :Xarray DataSet TYPE
        DESCRIPTION.

    """
    import skimage.morphology
    from skimage.morphology import disk
    xrdata_gs_sub_mean = xrdata_gs.copy()
    for ch_name in  xrdata_gs:
        xrdata_gs_sub_mean[ch_name].values = \
        xrdata_gs[ch_name] - skimage.filters.rank.mean(xrdata_gs[ch_name],disk(disk_radious))
    return xrdata_gs_sub_mean

# test



# -

test_gs_sb_mean = filter_gs_substract_mean_xr(test_gs, disk_radious= 10)

test_gs_sb_mean.z_f.plot()

test_gs_sb_mean_fft = twoD_FFT_xr(test_gs_sb_mean)

np.log(rescale_intensity_xr(equalize_hist_xr(np.log(test_gs_sb_mean_fft)), percentile = (99,100)).z_f_fft).plot()

# +
#test_gs_sb_mean_fft
##

# 
# -

test_gs_sb_mean.z_b.plot()


# +
test_gs_dog = filter_diffofgaussians_xr (test_gs_sb_mean.z_f, low_sigma = 0, 
                              high_sigma = 20,
                              overwrite = True )

isns.imshow(test_gs_dog,robust= True, perc = (0,40))
# -

gwy_dict['gwy_xr1'].Z(Forward)

gwy_df

# +
gwy_df.iloc[0:2,:]

#unique_xres_values = original_df.loc['xres'].unique()


# +
# Get unique xres values.
unique_xres_values = gwy_df.loc['xres'].unique()

# Create a list to store the results.
result_dfs = []
# Create groups for each xres value and create a separate DataFrame for each group.
for xres_value in unique_xres_values:
    group_df = gwy_df[gwy_df.columns[gwy_df.loc['xres'] == xres_value]]
    # group_df with the same xres
    unique_yres_values = group_df.loc['yres'].unique()
    if len(unique_yres_values) == 1:
        result_dfs.append(group_df)
# result_dfs is group_dfs list with different 'xres'
# group_dfs = channels with unique xres&yres



# +
gwy_xr_dict = {}
# prepare empty dictionary for gwy_xrs 
# this is because of different X&Y size of eqch group.  
for results_df_i in range(1,len(result_dfs)+1):
    # number of unique groups in result_df 
    
    gwy_xr_dict[f'gwy_xr{results_df_i}'] = xr.DataArray()
    #prepare Data Set
    # Create a dictionary to store empty Xarrays (DataArrays)

    
for i, gwy_xr_i in enumerate(gwy_xr_dict.keys()):
    # call each gwy_xrs
    # use keys() 
    print(gwy_xr_i)
    gwy_xr_j  = xr.Dataset()
    for j, group_df in enumerate(result_dfs[i]):
        # call group_df from results_dfs
        print (j)
        xr_array = gwy_df_ch2xr(result_dfs[i], ch_N=j)
        gwy_xr_j[result_dfs[i].columns[j]] = xr_array
        # convert single dataframe, ch_N = j as a xr_array 
        
        gwy_xr_dict[gwy_xr_i] = gwy_xr_j
        # save Data array in empty DataSet
# Xarray dictionary consist of different size DataSet       
# -

gwy_xr_dict['gwy_xr3']

result_dfs[0].columns[1]

# +
for ch_n in range (result_dfs[1].shape[1]):
    gwy_df_ch2xr(result_dfs[1],ch_N= ch_n)

#gwy_df_ch2xr(result_dfs[1])
# -

result_dfs[1].columns[0]
#gwy_df_ch2xr(result_dfs[1], ch_N=0)

# +
# Create an empty Xarray Dataset

for results_df_i in range(len(result_dfs)):
    f'result_xr{i + 1}' = xr.Dataset()


# -

    # Convert each DataFrame to Xarray and add it to the Dataset
    for i, df in enumerate(result_dfs[results_df_i]):
        xr_array = gwy_df_ch2xr(result_dfs[results_df_i], ch_N=i)

        result_xr[result_dfs[results_df_i].columns[i]] = xr_array
        # result_dfs[1].columns[i] 
        # ==> results_dfs column names to Xrarray data Array name
result_xr

# +
       
    
# Convert each DataFrame to Xarray and add it to the Dataset
for i, df in enumerate(result_dfs[1]):
    xr_array = gwy_df_ch2xr(result_dfs[1], ch_N=i)
    
    dataset[result_dfs[1].columns[i]] = xr_array
    # result_dfs[1].columns[i] 
    # ==> results_dfs column names to Xrarray data Array name

print(dataset)
# -

dataset

# +
# Get unique xres values.
unique_xres_values = gwy_df.loc['xres'].unique()
# Create a list to store the results.
result_dfs = []

# Create groups for each xres value and create a separate DataFrame for each group.
for xres_value in unique_xres_values:
    group_df = gwy_df.loc[gwy_df.loc['xres'] == xres_value]
    
    # Process the group only if all yres values are the same.
    unique_yres_values = group_df.loc['yres'].unique()
    if len(unique_yres_values) == 1:
        result_dfs.append(group_df)
# -

dataset

# +


# Iterate over each column in the DataFrame to create Xarray DataArrays and add them to the DataSet.
for column_name in df.columns:
    # Get the values of each column in the DataFrame.
    column_values = df.loc[column_name].values
    
    # Create an Xarray DataArray.
    data_array = xr.DataArray(column_values, dims=('variable',))
    
    # Add the Xarray DataArray to the DataSet, using the column name as the variable name.
    dataset[column_name] = data_array

# You can print or further manipulate the created DataSet as needed.
print(dataset)
# -

gwy_df_ch2xr(gwy_df)

# +
import pandas as pd
import xarray as xr

def gwy_df_ch2xr(gwy_df):
    """
    Convert channel data from a Pandas DataFrame to an xarray DataArray format.

    Parameters:
    gwy_df (pd.DataFrame): The input Pandas DataFrame containing channel data.
    ch_N (int, optional): The channel index to convert (default is 0).

    Returns:
    xr.DataArray: An xarray DataArray containing the channel data with proper coordinates.
    
    This function takes a DataFrame (`gwy_df`) and an optional `ch_N` parameter to specify
    which channel to convert into an xarray DataArray format. It reshapes the channel data
    into a 2D DataFrame, stacks it, and assigns 'Y' and 'X' coordinates with proper scaling.
    The resulting xarray DataArray is returned.
    """
    # Extract the channel data from the DataFrame
    chN_df = gwy_df.iloc[:, ch_N]

    # Reshape the channel data into a 2D DataFrame and stack it
    chNdf_temp = pd.DataFrame(chN_df.data.reshape((chN_df.yres, chN_df.xres))).stack()

    # Rename the indices as 'Y' and 'X'
    chNdf_temp = chNdf_temp.rename_axis(['Y', 'X'])

    # Calculate the x and y step sizes
    x_step = chN_df.xreal / chN_df.xres
    y_step = chN_df.yreal / chN_df.yres

    # Convert the DataFrame to an xarray DataArray
    chNxr = chNdf_temp.to_xarray()

    # Assign coordinates 'X' and 'Y' with proper scaling
    chNxr = chNxr.assign_coords(X=chNxr.X.values * x_step, Y=chNxr.Y.values * y_step)

    return chNxr



# +
import pandas as pd
import xarray as xr

def gwy_df_ch2xr(gwy_df, ch_N=0):
    """
    Convert channel data from a Pandas DataFrame to an xarray DataArray format.

    Parameters:
    gwy_df (pd.DataFrame): The input Pandas DataFrame containing channel data.
    ch_N (int, optional): The channel index to convert (default is 0).

    Returns:
    xr.DataArray: An xarray DataArray containing the channel data with proper coordinates.
    
    This function takes a DataFrame (`gwy_df`) and an optional `ch_N` parameter to specify
    which channel to convert into an xarray DataArray format. It reshapes the channel data
    into a 2D DataFrame, stacks it, and assigns 'Y' and 'X' coordinates with proper scaling.
    The resulting xarray DataArray is returned.
    """
    # Extract the channel data from the DataFrame
    chN_df = gwy_df.iloc[:, ch_N]

    # Reshape the channel data into a 2D DataFrame and stack it
    chNdf_temp = pd.DataFrame(chN_df.data.reshape((chN_df.yres, chN_df.xres))).stack()

    # Rename the indices as 'Y' and 'X'
    chNdf_temp = chNdf_temp.rename_axis(['Y', 'X'])

    # Calculate the x and y step sizes
    x_step = chN_df.xreal / chN_df.xres
    y_step = chN_df.yreal / chN_df.yres

    # Convert the DataFrame to an xarray DataArray
    chNxr = chNdf_temp.to_xarray()

    # Assign coordinates 'X' and 'Y' with proper scaling
    chNxr = chNxr.assign_coords(X=chNxr.X.values * x_step, Y=chNxr.Y.values * y_step)

    return chNxr



# -

xr.DataArray(gwy_df,dims = gwy_df.columns.astype(str))

# 3D data 
#grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[2])
# line data
grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[2])
grid_xr









def xrdata_plot_r_q_space_q(xrdata, ch_name= 'z_f',figsize = (6,3), peak_detection_min_distance=20, distance_to_refq0 = 4, add_guidlines = True):
    from matplotlib_scalebar.scalebar import ScaleBar
    from matplotlib.patches import Circle
    xrdata_fft = twoD_FFT_xr(xrdata)
    xrdata_fft_zm = fft_masking_near_q0only (xrdata_fft,ch_name= ch_name+'_fft', filtering_ratio=[0.3, 2])

    
    fig, axes = plt.subplots (1,2, figsize = figsize)
    axs = axes.ravel()
    if 'z_' in ch_name:
        cmap_r = 'copper'
        cmap_q = 'Greys'
    if 'LIX_' in ch_name:
        cmap_r = 'bwr'
        cmap_q = 'Blues'
    
    isns.imshow (xrdata[ch_name], robust = True, ax = axs[0],cmap= cmap_r, dx =xrdata[ch_name].X.X_spacing*1E9, units = "nm" )
    axs[0].set_title(ch_name)
    isns.imgplot(xrdata_fft[ch_name+'_fft'].where(xrdata_fft.mask_ == 1, drop = True), robust = True, ax = axs[1], cmap= cmap_q)
    axs[1].set_title(ch_name+' (2D FFT)')
    scalebar = ScaleBar(dx = xrdata_fft.freq_X.spacing*1E-9,
                        units = "1/nm",
                        dimension="si-length-reciprocal",    
                        color='k'                   )
    # dx = pixel size for scale bar 
    # 1E-9 for "1/nm" unit
    # use separate scalebar option to adjust scale bar color 
    axs[1].add_artist(scalebar)
    image_shape = axs[1].get_images()[0].get_array().shape
    #get center point from image shape of plot 
    # or the center is not correct
    # fft_center  = ( xrdata_fft.z_f_fft.freq_X.shape[0] / 4,  xrdata_fft.z_f_fft.freq_X.shape[0] / 4)
    # it is not center position
    if add_guidlines == True : 

        fft_center  = ( image_shape[0] / 2,  image_shape[0] / 2)
        q0_r = get_px_from_fft_coord(xrdata_fft, xrdata_fft.ref_q0)
        circle_q0 = Circle(xy = fft_center, radius= float (q0_r), fill= False, edgecolor = 'blue', alpha =0.5)
        axs[1].add_patch(circle_q0)

        from skimage.feature import peak_local_max
        im = xrdata_fft[ch_name+'_fft'].where(xrdata_fft.mask_ == 1, drop = True).fillna(0).values
        #z_f_fft_peak.fillna( z_f_fft_peak.min()).values
        coordinates = peak_local_max(im, min_distance= peak_detection_min_distance)
        #coordinates ==> find max 
        # Calculate distances between the points and the disk
        distances = np.sqrt((coordinates[:, 0] - fft_center[0]) ** 2 + (coordinates[:, 1] - fft_center[1]) ** 2)
        # distances from fft_center to each points in coordiates 

        # Find the index of the close points
        distance_to_q0r = distance_to_refq0
        close_points_indx = np.abs(distances-q0_r.values) < distance_to_q0r
        #closest_point_index = np.argmin(np.abs(distances-q0_r.values))
        # distance from the circle 
        closest_point = coordinates[close_points_indx]
        #closest_point  = peak points that is closed to ref_q0 ( < distance_to_q0r )
        '''
        circle_1 = Circle(xy = fft_center, radius= float (q0_r-distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'blue', alpha =0.1)
        circle_2 = Circle(xy = fft_center, radius= float (q0_r+distance_to_q0r), linestyle='dotted', fill= False, edgecolor = 'blue', alpha =0.1)
        axs[1].add_patch(circle_1)
        axs[1].add_patch(circle_2)
        '''
        axs[1].scatter(closest_point[:, 1], closest_point[:, 0], c='blue',marker='o', s = 80 , alpha = 0.3)

        # Find the index of the close points
        q0_sqrt2_r = q0_r*math.sqrt(2)
        distance_to_q0sqrt2r = distance_to_refq0
        close_pointsq0_sqrt2r_indx = np.abs(distances-q0_sqrt2_r.values) < distance_to_q0sqrt2r
        #closest_point_index = np.argmin(np.abs(distances-q0_r.values))
        # distance from the circle 
        closest_point_sqrt2 = coordinates[close_pointsq0_sqrt2r_indx]
        #closest_point  = peak points that is closed to ref_q0 ( < distance_to_q0r )
        axs[1].scatter(closest_point_sqrt2[:, 1], closest_point_sqrt2[:, 0], c='red',marker='o', s = 80 , alpha = 0.4)


        circle_sqrt2q0 = Circle(xy = fft_center, radius= float (q0_r)*math.sqrt(2), fill= False, linestyle='dotted', edgecolor = 'red', alpha =0.5)
        axs[1].add_patch(circle_sqrt2q0)

        text_position = [1, 1]
        axs[1].annotate(r'$q_{0} (Se/Te)$', (text_position[0]*0.05, text_position[1]*0.12), size=10, color="blue", xycoords="axes fraction")#alpha = 0.3,
                #bbox=dict(facecolor="white", alpha=0.5, edgecolor="black", linewidth=1))
        axs[1].annotate(r'$ \sqrt{2} q_{0} ( \frac{1}{2}$Fe)', (text_position[0]*0.05, text_position[1]*0.04), size=10, color="red", xycoords="axes fraction")
    else: pass
    plt.tight_layout()
    plt.show()
    return 
