# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.0
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

# + [markdown] jp-MarkdownHeadingCollapsed=true
# # Experimental Conditions 
#
# ## Data Acquistion date 
# * 2023 0814
#
# ## **Sample** :<font color= White, font size="5" > $CsV_{3}Sb_{5}, 4^{th}$ 82K cleaving </font> 
#     * Cleaving at 82K at LT cleaving holder in EX chamber
#     * UHV condition (<5E-10Torr)
# ## **Tip: Electro chemically etched W Tip# 11  normal metal tip**
# ## Measurement temp: mK ( $/approx$ 40 mK)
#
# ## Magnetic field 0.01 T (Z)
#
# # first try searching for Vortex 
#
# -

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
#install pandas 

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns
import skimage
from scipy import signal
from SPMpy_2D_data_analysis_funcs import *
from SPMpy_3D_data_analysis_funcs import *

from SPMpy_fileloading_functions import (
    grid2xr,
    grid_line2xr,
    gwy_df_ch2xr,
    gwy_img2df,
    img2xr,
)

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
file_chooser = FileChooser("")
display(file_chooser)

# +
##############################
# After choose the folder    #
# Files DataFrame            #
##############################

folder_path = file_chooser.selected_path
print("folder_path = ", file_chooser.selected_path)
print("selected file name = ", file_chooser.selected_filename)
from SPMpy_fileloading_functions import files_in_folder

files_df = files_in_folder(folder_path)
# -

# ### grid_xr  data structure 
#
# * using grid2xr function
#     * '_fb' : add fwd/bwd data average
#     * grid_topo : 2D data
#     * grid_3D : 3D data
#     * I_fb : I, (forwad + backward sweep )/2
#     * LIX_fb : LIX, (forwad + backward sweep )/2
#     * dIdV : dI/dV (using xr differentiate class )
#     * LIX_unit_calc : LIX_fb * LIX_coefficient (for unit calibration)
# * after grid_3D_gap function
#     * 2D data : CBM, VBM position assignment $\leftarrow$ based on I or LIX
#         * CBM_I_mV, VBM_I_mV, gap_size_I, CBM_LIX_mV, VBM_LIX_mV, gap_size_LIX
#     * 3D data : LDOS_fb $\leftarrow$ after unit calc & offset adjust
#         * I_fb, LIX_fb, LDOS_fb, LDOS_fb_CB, LDOS_fb_VB
#         * I_fb : I, (forwad + backward sweep )/2
#         * LIX_fb : LIX, (forwad + backward sweep )/2
#         * LDOS_fb : LIX_fb * LIX_coefficient (for unit calibration) + offset adjustment (according to LIX at I=0)
#         * LDOS_fb_CB : based on LIX assignment
#         * LDOS_fb_VB : based on LIX assignment

# ## 1-2. Choose 3ds file loading to analyze

files_df[files_df.type=='3ds']#.file_name.iloc[0]


#
# ### 1.2.1. Convert  to xarray

# 3D data 
#grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[2])
# line data
grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[0])
grid_xr

# ## 1-2.2. Separate topography / gird_3D (I_fb, LIX_fb)
# * fwd bwd data average 
#

# +
grid_xr = grid_xr.assign_coords({'X': grid_xr.X -  grid_xr.X.min()})
grid_xr = grid_xr.assign_coords({'Y': grid_xr.Y -  grid_xr.Y.min()})

# grid data to xr 
grid_xr['I_fb'] = (grid_xr.I_fwd + grid_xr.I_fwd)/2
grid_xr['LIX_fb'] = (grid_xr.LIX_fwd + grid_xr.LIX_fwd)/2
# add 'I' & 'LIX' channel "fb = [fwb+bwd] / 2 " 

grid_topo = grid_xr[['topography']]
# topography 
grid_3D = grid_xr[['I_fb','LIX_fb']]
# averaged I & LIX 
# -

grid_xr

# +
###########################
# unfinished grid data 
###########################
# Crop  (Y<1.25E-9)
#############################

grid_topo #= grid_topo.where (grid_topo.Y<1.25E-9, drop = True)
grid_3D #= grid_3D.where (grid_3D.Y<1.25E-9, drop = True)



# +

##################################
#  Padding & dirft correlation 
##################################

'''
grid_xr_pad = padding_xr(grid_xr,  padding_dim = 'X', padding_shape=10)
grid_xr_pad.LIX_fb.sel(bias_mV=0).plot(robust = True)


grid_xr_drft_y = drift_compensation_y_topo_crrltn(grid_xr)
grid_xr_drft_y_pad = padding_xr ( grid_xr_drft_y, padding_dim='Y', padding_shape= 10)
'''


# -


########################
# check rotation 
# & crop boundary area 
##########################
'''

grid_xr_drft_y_rot = rotate_3D_xr ( grid_xr_drft_y_pad, rotation_angle= -4)
# shape of X & Y need to be the same 
grid_xr_drft_y_rot = grid_xr_drft_y_rot.where(
    grid_xr_drft_y_rot.X >0.8E-9, drop = True).where(
    grid_xr_drft_y_rot.X <4.5E-9, drop = True).where(
    grid_xr_drft_y_rot.Y >0.8E-9, drop = True).where(
    grid_xr_drft_y_rot.Y <4.5E-9, drop = True)

grid_xr_drft_y_rot.topography.plot(robust = True)

'''



# +
############################################
# After drift check 
############################################
#grid_3D_gap = grid_3D_SCgap(grid_xr_drft_y_rot)
#################################################


grid_xr_crop = grid_xr.where(grid_xr.Y <0.19E-7, drop = True)

#grid_xr_crop.topography.plot(robust= True)

isns.imshow(grid_xr_crop.topography, robust= True)
# -

grid_3D_gap = grid_3D_SCgap(grid_xr_crop)
grid_3D_gap#.plateau_size_map_LIX.plot()

# +
fig, axs = plt.subplots(3, 1, figsize = (6,6))
isns.imshow(grid_3D_gap.zerobiasconductance, robust = True, cmap =  'Blues',ax = axs[0] )
axs[1] = isns.imshow(grid_3D_gap.plateau_size_map_LIX, robust = True, cmap =  'Greens',ax = axs[1])
axs[2] = isns.imshow(grid_3D_gap.gap_mapI, robust = True, cmap =  'Oranges',ax = axs[2])

axs[0].set_title ( "zero_bias_conductance_map", loc='left')
axs[1].set_title ( "plateau_size_map (LDOS gap size)", loc='left')
axs[2].set_title ( "Gap map (I tolarence gap size)", loc='left')

plt.show()

# -

grid_3D_gap

# +

#grid_3D_gap.gap_mapI.where(grid_3D_gap.gap_mapI<0).notnull().sum()
#grid_3D_gap.gap_pos0_I.plot()
#(grid_3D_gap.gap_pos0_LIX-grid_3D_gap.gap_neg0_LIX).plot()
#grid_3D_gap.gap_neg0_I.plot()
#grid_3D_gap.plateau_size_map_LIX.plot()
#grid_3D_gap.zerobiasconductance.plot()
#grid_3D_gap.plateau_map_LIX.plot()


# -

# grid_3D_gap.gap_neg0_LIX.plot()
# grid_3D_gap.plateau_size_map_LIX.plot()#.sel(bias_mV=0).plot()
# plateau 영역 extract



# ### 1.2.3. Unit calculation (LDOS_fb)
#     * for semiconductor: CBM,VBM check. gap_map check
#     * add gap_maps to grid_2D

# +

grid_3D_gap
grid_LDOS = grid_3D_gap[['LDOS_fb' ]]

# if 3D_SCGap is not working due to too small LDOS points 

grid_LDOS = grid_xr_crop[['LIX_fb' ]]
grid_LDOS = grid_LDOS.rename_vars({'LIX_fb': 'LDOS_fb'})
grid_LDOS
# -

# ### 1.4 Topography view 

print(str (round (grid_topo.image_size [0]* 1E9)), 'nm X ', str (round (grid_topo.image_size [1]* 1E9)), 'nm')

# +
grid_topo = grid_3D_gap[['topography']]
#grid_topo =  plane_fit_y_xr(grid_topo.where(grid_topo.Y<1.25E-9))
#isns.imshow(plane_fit_y_xr(grid_topo).where(grid_topo.Y < 0.7E-9, drop=True).topography)

#grid_topo = grid_topo.drop('gap_map_I').drop('gap_map_LIX')
fig, axs = plt.subplots(1, 1, figsize = (6,3))

isns.imshow(plane_fit_y_xr(grid_topo).topography, cmap ='copper',robust = True, ax =axs)
axs.set_title('Topography ( '+ str (round (grid_topo.image_size [0]* 1E9))+'nm x '+ str (round (grid_topo.image_size [1]* 1E9))+ ' nm )',
              fontsize='medium')

plt.show()
# -


# ##  Grid area extract 
#
# ### grid 3D_LDOS
#
#
#

# ## 2.3 Numerical derivative 
#     * Derivative + SG smoothing
#
# ### 2.3.1. SG + 1stderiv + SG + 2nd deriv + SG

# ##### SG fitlering only 

grid_LDOS_sg = savgolFilter_xr(grid_LDOS, window_length = 31, polyorder = 3)

# #### numerical derivative check. later 

grid_LDOS_1deriv = grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1deriv_sg = savgolFilter_xr(grid_LDOS_1deriv, window_length = 21, polyorder = 3)
grid_LDOS_2deriv = grid_LDOS_1deriv_sg.differentiate('bias_mV')
grid_LDOS_2deriv_sg =  savgolFilter_xr(grid_LDOS_2deriv, window_length = 21, polyorder = 3)
grid_LDOS_2deriv_sg

# +
### to crop the XY range

#grid_topo = grid_topo.where(grid_topo.Y < 0.7E-9, drop=True)
#grid_LDOS = grid_LDOS.where(grid_topo.Y < 0.7E-9, drop=True)
# -


# ### 1.5 grid_3D data view 
#
# * use holoview
#
#

# #### 1.5.1 Bias_mV slicing 
# * Use the function 
#     * hv_bias_mV_slicing
#     * hv_XY_slicing

#hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb',frame_width=400)#.opts(clim = (0,2E-10))
hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb',frame_width=300)#.opts(clim = (0,5E-10)) # adjust cbar limit

# ####  1.5.2. Y or X slicing 

#hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'Y')#.opts(clim=(0, 8E-10)) #
hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'X')#.opts(clim=(0, 4E-10)) #
#hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'y').opts(clim=(0, 3E-9)) # check low intensity area
#hv_XY_slicing(grid_3D,slicing= 'Y').opts(clim=(0, 1E-11))


# +
# set tolerance for I_fb * LIX_fb
#tolerance_I, tolerance_LIX = 1E-11, 0.05E-12


###############
# rotation #
#################
#grid_LDOS_rot = rotate_3D_xr(grid_LDOS, rotation_angle= 11)
## or not
#grid_LDOS_rot = rotate_3D_xr(grid_LDOS, rotation_angle= 0)
grid_LDOS_rot = grid_LDOS
###############
xr_data = grid_LDOS_rot

#tolerance_I, tolerance_dIdV, tolerance_d2IdV2 = 1E-10,1E-10,1E-10
#tolerance_LIX, tolerance_dLIXdV , tolerance_d2LIXdV2  = 1E-11,1E-11,1E-11
sliderX = pnw.IntSlider(name='X', 
                       start = 0 ,
                       end = xr_data.X.shape[0]) 
sliderY = pnw.IntSlider(name='Y', 
                       start = 0 ,
                       end = xr_data.Y.shape[0]) 

#sliderX_v_intact = interact(lambda x:  grid_3D.X[x].values, x =sliderX)[1]
#sliderY_v_intact = interact(lambda y:  grid_3D.Y[y].values, y =sliderY)[1]
pn.Column(interact(lambda x:  xr_data.X[x].values, x =sliderX), interact(lambda y: xr_data.Y[y].values, y =sliderY))


# -

# #### 2.3.1.2. STS curve at XY point

def plot_Xslice_w_LDOS (xr_data, sliderX, ch ='LIX_fb', slicing_bias_mV = 0):
    
    '''
    ################################
    # use the slider in advance 
    sliderX = pnw.IntSlider(name='X', 
                           start = 0 ,
                           end = grid_3D.X.shape[0]) 
    sliderY = pnw.IntSlider(name='Y', 
                           start = 0 ,
                           end = grid_3D.Y.shape[0]) 

    #sliderX_v_intact = interact(lambda x:  grid_3D.X[x].values, x =sliderX)[1]
    #sliderY_v_intact = interact(lambda y:  grid_3D.Y[y].values, y =sliderY)[1]
    pn.Column(interact(lambda x:  grid_3D.X[x].values, x =sliderX), interact(lambda y: grid_3D.Y[y].values, y =sliderY))

    ####################################
    
    '''
    
    print("use the sliderX&Y first")
    #plt.style.use('default')
    sliderX_v = xr_data.X[sliderX.value].values
    sliderY_v = xr_data.Y[sliderY.value].values


    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[ch]

    xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[ch]
    
    # bias_mV slicing
    fig,axes = plt.subplots (nrows = 2,
                            ncols = 1,
                            figsize = (3,6))
    axs = axes.ravel()

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    xr_data_Vline_profile.plot(ax = axs[1], robust = True, vmin = xr_data_Vline_profile.to_numpy().min(), vmax = xr_data_Vline_profile.to_numpy().max()*0.25)
    #xr_data_Hline_profile.T.plot(ax = axs[2], robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())
    axs[1].vlines(0,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls ='--', alpha =0.3) 
    # L half alpha
    axs[1].vlines(0.368181818,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3) 
    axs[1].vlines(1.104545455,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3)     
    axs[1].vlines(1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3) 
    axs[1].vlines(-0.368181818,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3) 
    axs[1].vlines(-1.104545455,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3)     
    axs[1].vlines(-1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'b',ls =':', alpha =0.3) 
    
    # L int  alpha
    0.736363636, 1.472727273, 2.209090909
    axs[1].vlines(0.736363636,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3) 
    axs[1].vlines(1.472727273,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3)     
    axs[1].vlines(1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3) 
    axs[1].vlines(-0.736363636,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3) 
    axs[1].vlines(-1.472727273,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3)     
    axs[1].vlines(-2.2090909091,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='--', alpha =0.3) 
    
    #xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[2])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    
    return plt.show()

plot_Xslice_w_LDOS(grid_LDOS_rot, sliderX= sliderX, ch = 'LDOS_fb',slicing_bias_mV = 0)
plt.show()

# +
L_half_alpha  = [0,0.368181818, 1.104545455, 1.840909091,5]

L_int_alpha  = [0.736363636, 1.472727273, 2.209090909]

L_half_beta  = [1.420454545,2.840909091, 4.261363636]
L_int_beta = [0.710227273,2.130681818,3.551136364]

L_half_gamma  = [3.636363636,7.272727273,10.90909091]
L_int_gamma = [1.818181818,5.454545455,9.090909091]

sns.scatterplot(L_half_alpha)
plt.show()

# +
#grid_LDOS_rot_sg

plot_XYslice_w_LDOS(grid_LDOS_rot, sliderX= sliderX, sliderY= sliderY, ch = 'LDOS_fb',slicing_bias_mV = 0.2)
# -

# ### 1.6.Data Selection with HoloView
# * using Bounding Box or Lasso
#
# * currently only Bounding Box plot is working. 
# * check the Lass selection later. 
# * use stream pipe line (not a functino yet..)
#

# #### 1.6.2 bokeh plot & Bound box selection 
# ####       $\to$ selected points = Bound Box 

# +
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

xr_data = grid_LDOS
ch = 'LDOS_fb'
frame_width = 400

xr_data_channel_hv = hv.Dataset(xr_data.LDOS_fb)

# bias_mV slicing
dmap_plane  = ["X","Y"]
dmap = xr_data_channel_hv.to(hv.Image,
                          kdims = dmap_plane,
                          dynamic = True )
dmap.opts(colorbar = True,
          cmap = 'bwr',
          frame_width = frame_width,
          aspect = 'equal')#.relabel('XY plane slicing: ')

xr_data_channel_hv_image  = hv.Dataset(xr_data[ch].isel(bias_mV = 0)).relabel('for BBox selection : ')

bbox_points = hv.Points(xr_data_channel_hv_image).opts(frame_width = frame_width,
                                                    color = 'k',
                                                    aspect = 'equal',
                                                    alpha = 0.1,                                   
                                                    tools=['box_select'])

bound_box = hv.streams.BoundsXY(source = bbox_points,
                                bounds=(0,0,0,0))
#dmap.opts(clim = (0,1E-10))*bbox_points
dmap.opts()*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box

bbox_2, _ = hv_bbox_avg(grid_LDOS, bound_box= bound_box, ch ='LDOS_fb',slicing_bias_mV = 0.4)

# #### multiple area selection ('bbox_1', 'bbox_2') 
#      * plot multi regions with ROI 


grid_LDOS.isel(bias_mV=0).LDOS_fb  


# +

#isns.imshow(grid_xr.isel(bias_mV=0).LIX_fb.values)
isns.imshow(grid_LDOS.isel(bias_mV=0).LDOS_fb.values, robust = True)
plt.show()
# -

isns.imshow(plane_fit_y_xr(grid_topo).topography.values, robust = True)
plt.show()

# +
sns.lineplot(x = 'bias_mV', y = 'LDOS_fb' , data  = bbox_1.LDOS_fb.mean(['X','Y']).to_dataframe(), label ='area1', color = 'y')
sns.lineplot(x = 'bias_mV', y = 'LDOS_fb' , data  = bbox_2.LDOS_fb.mean(['X','Y']).to_dataframe(), label ='area2', color = 'r' )

plt.show()

# +
LDOS_fb_area1_df =  bbox_1.LDOS_fb.to_dataframe()
LDOS_fb_area2_df =  bbox_2.LDOS_fb.to_dataframe() 
# xr to dataframe
LDOS_fb_area1_df.columns = ['Area1']
LDOS_fb_area2_df.columns = ['Area2']# change df names 

LDOS_fb_area_df = pd.concat( [LDOS_fb_area1_df,LDOS_fb_area2_df], axis= 1)
LDOS_fb_area_df# = LDOS_fb_area_df.swaplevel(0,2)
#LDOS_fb_area_df.swaplevel(0,2) # index level swap. w.r.t. 'bias_mV'
#LDOS_fb_area_df = LDOS_fb_area_df.swaplevel(0,2).unstack().unstack() # unstack X& Y


##sns.lineplot(x= 'bias_mV', y ='LDOS1', data= LDOS_fb_area_df, label = 'area1')
#sns.lineplot(x= 'bias_mV', y ='LDOS2', data= LDOS_fb_area_df, label = 'area2')
#plt.show()
# use the below sns plot instead 


# -

LDOS_fb_area_df = LDOS_fb_area_df.reset_index()
LDOS_fb_area_df_melt = LDOS_fb_area_df.melt(id_vars = ['Y','X','bias_mV'], value_vars = ['Area1','Area2'])
LDOS_fb_area_df_melt.columns = ['Y','X','bias_mV', 'Area','LDOS']
LDOS_fb_area_df_melt

sns.lineplot(x= 'bias_mV', y = 'LDOS', data = LDOS_fb_area_df_melt, hue ='Area')
plt.show()

# +
# Bbox1 & Bbox2 



fig, axs = plt.subplots(ncols = 3, figsize = (9,3))
isns.imshow(plane_fit_y_xr(grid_topo).topography, cmap ='copper', ax = axs[0])

# add patach bb1 & bb2
import matplotlib.patches as patches

rec_x0_bb1, rec_y0_bb1 = bbox_1.X[0],bbox_1.Y[0]
rec_width_bb1,rec_height_bb1 = bbox_1.X[-1]- bbox_1.X[0], bbox_1.Y[-1]- bbox_1.Y[0]

rec_xy_bb1 = (int(rec_x0_bb1/grid_LDOS.X_spacing), int(rec_y0_bb1/grid_LDOS.Y_spacing))
rec_w_px_bb1,rec_h_px_bb1 = int(rec_width_bb1/grid_LDOS.X_spacing),int(rec_height_bb1/grid_LDOS.Y_spacing)

rec_x0_bb2, rec_y0_bb2 = bbox_2.X[0],bbox_2.Y[0]
rec_width_bb2,rec_height_bb2 = bbox_2.X[-1]- bbox_2.X[0], bbox_2.Y[-1]- bbox_2.Y[0]

rec_xy_bb2 = (int(rec_x0_bb2/grid_LDOS.X_spacing), int(rec_y0_bb2/grid_LDOS.Y_spacing))
rec_w_px_bb2,rec_h_px_bb2 = int(rec_width_bb2/grid_LDOS.X_spacing),int(rec_height_bb2/grid_LDOS.Y_spacing)

rec_in_topo_bb1 =  patches.Rectangle( rec_xy_bb1 , rec_w_px_bb1,rec_h_px_bb1 , linewidth=1, edgecolor='cyan', facecolor='none')
rec_in_topo_bb2 =  patches.Rectangle( rec_xy_bb2 , rec_w_px_bb2,rec_h_px_bb2 , linewidth=1, edgecolor='orange', facecolor='none')

axs[0].add_patch(rec_in_topo_bb1)
axs[0].add_patch(rec_in_topo_bb2)

isns.imshow (grid_LDOS.LDOS_fb.sel(bias_mV = 0, method ='nearest'),ax = axs[1])
# LDOS_bias_mV
rec_in_topo_bb1 =  patches.Rectangle( rec_xy_bb1 , rec_w_px_bb1,rec_h_px_bb1 , linewidth=1, edgecolor='cyan', facecolor='none')
rec_in_topo_bb2 =  patches.Rectangle( rec_xy_bb2 , rec_w_px_bb2,rec_h_px_bb2 , linewidth=1, edgecolor='orange', facecolor='none')

axs[1].add_patch(rec_in_topo_bb1)
axs[1].add_patch(rec_in_topo_bb2)

sns.lineplot(x= 'bias_mV', y = 'LDOS', data = LDOS_fb_area_df_melt, hue ='Area', ax =axs[2])
# area averaged BB1 BB2  STS

plt.tight_layout()
plt.show()
# -


# #### plot LODS slices using isns image grid 
# * select bias from energy level 
#
# * make a function later 
# def ImageGrid with bias slicing 
#
# input slicing bias energy 
# add bias mV title for each Axes
#

# +
# set slicing bias_mV index

## make a function later 


#bias_mV_slices= [ -5,-4, -3, -2, -1, 0, 1, 2, 3, 4,5][::-1]
#bias_mV_slices= [ -2.4, -2, -1, 0, 1, 2, 2.4 ][::-1]

#bias_mV_slices= [-1.4, -1.2, -1, -0.8, -0.6, 0, 0.6, 0.8,1,1.2,1.4][::-1]
#bias_mV_slices= [-1.0, -0.8, -0.6,-0.4,-0.2, 0,0.2,0.4, 0.6, 0.8,1][::-1]
#bias_mV_slices= [ -0.8, -0.6,-0.4,-0.2, 0,0.2,0.4, 0.6, 0.8][::-1]
bias_mV_slices = np.arange (-2,2.1,0.4) 
print (bias_mV_slices)
bias_mV_slices_v = grid_LDOS.bias_mV.sel(bias_mV = bias_mV_slices, method = "nearest").values#.round(2)
bias_mV_slices_v
# -

grid_LDOS


# +
# value --> use Where ! 
col_wrap=3

g = isns.ImageGrid(grid_LDOS.sel(bias_mV = bias_mV_slices, method = "nearest").LDOS_fb.values, 
                   cbar=False, height=2, col_wrap=col_wrap,  cmap="bwr", robust = True)

# set a col_wrap for suptitle 

for axes_i  in range( len(bias_mV_slices)):
    #print (int(axes_i/col_wrap),axes_i%col_wrap)  # axes number check 
    g.axes[int((axes_i)/col_wrap)][axes_i%col_wrap].set_title(str(bias_mV_slices_v[axes_i].round(2))+' mV')

plt.tight_layout()
plt.show()

# +
grid_LDOS_df = grid_LDOS.to_dataframe().unstack()
# xarray to data frame 

#############################################
# adjust multi index of dataframe as a single index 
grid_LDOS_df_T = grid_LDOS_df.T.reset_index().drop(['level_0'],axis=1)
# drop index level0 
grid_LDOS_df_T['bias_mV'] = grid_LDOS_df_T['bias_mV'].round(3)
# bias_mV index rounding (shorter name)
grid_LDOS_df_T = grid_LDOS_df_T.set_index('bias_mV')
# set index  as 'bias_mV'
grid_LDOS_df =  grid_LDOS_df_T.T
####################################3
# grid_LDOS_df with single column index 
###############################


# Compute the correlation matrix
grid_LDOS_df_corr = grid_LDOS_df.corr()

# +
# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(grid_LDOS_df_corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(grid_LDOS_df_corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
plt.show()
# -

# #### 1.6.5. Lasso area selection 
# * it works if I using grid_3D 
#     * with multiple data channels 
#     * but not with grid_LDOS (only 1 data channel) 
# * later.... lasso pts combine_by_coords need to repaired.. 
#     * but I can extract the target area anyway.. 
#
#

# +
hv.extension('bokeh')


grid_channel_hv = hv.Dataset(grid_3D.I_fb)

# bias_mV slicing
dmap_plane  = ["X","Y"]
dmap = grid_channel_hv.to(hv.Image,
                          kdims = dmap_plane,
                          dynamic = True )
dmap.opts(colorbar = True,
          cmap = 'bwr',
          frame_width = 400,
          aspect = 'equal').relabel('XY plane slicing: ')



grid_channel_hv_image = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0))

grid_channel_hv_points = hv.Points(grid_channel_hv_image).opts(frame_width = 400,  
                                   aspect = 'equal', alpha = 0.1,                                   
                                   tools=['box_select', 'lasso_select']
                                  )

slct_pts = hv.streams.Selection1D(source=grid_channel_hv_points)

dmap*grid_channel_hv_image*grid_channel_hv_points

# +
#slct_pts
pts = grid_channel_hv_points.iloc[slct_pts.index].dframe().set_index(['X', 'Y'])

pts_xr = xr.Dataset.from_dataframe(pts)

grid_3D_slct_pts = xr.combine_by_coords ([grid_3D, pts_xr], compat = 'override', join = 'inner')
#y_pts = points.iloc[slct_pts.index].dframe().Y
#grid_3D.sel(X = x_pts,Y = y_pts)
#grid_3D.I_fb.isel(bias_mV = 0).plot()

fig, axs = plt.subplots(ncols = 2, nrows = 1, figsize = (10,3))

grid_3D_slct_pts.I_fb.T.plot(ax = axs[0], robust = True) 
axs[0].set_aspect= 0.5

sns.lineplot(x = "bias_mV",            
             y = "LIX_fb", 
             data = grid_3D_slct_pts.to_dataframe(),
             ax = axs[1])
plt.show()
#grid_3D_slct_pts
#
#sns.relplot(x="bias_mV",
#            y="LIX_fb", 
#            kind="line",
#            data=grid_3D_slct_pts.to_dataframe())
# check. sn.relplot is  figure-level function
# -

grid_3D_slct_pts.I_fb.plot()
## I_fb area is selected region, no bias_mV info. 
plt.show()

# #### 1.7. area selection based on special selection 
#     * tresholds_xxxx_xr = LDOS_fb channel th + use threshold_fiip   
#         * th_otsu_roi_label_2D_xr
#         * th_multiotsu_roi_label_2D_xr
#         * th_mean_roi_label_2D_xr
#         
#         

# +

#grid_LDOS.rolling(X=3, Y=3,min_periods=2,center= True).mean().isel(bias_mV=0).LDOS_fb.plot()
#plt.show()
grid_LDOS_th= th_mean_roi_label_2D_xr(grid_LDOS.rolling(X=4, Y=2,min_periods=2,center= True).mean(),
                                      bias_mV_th = 0.0,threshold_flip=False)
# -

grid_LDOS_th.LDOS_fb_th


# +
#grid_LDOS_th= th_otsu_roi_label_2D_xr(equalize_hist_xr(grid_LDOS), bias_mV_th = 0,  threshold_flip=False)
# use Otsu 

grid_LDOS_th= th_multiotsu_roi_label_2D_xr(grid_LDOS, bias_mV_th = 0.0, multiclasses = 5)
# in case of multiotsu

#grid_LDOS_th= th_mean_roi_label_2D_xr(grid_LDOS.rolling(X=4, Y=2,min_periods=2,center= True).mean(),
#                                      bias_mV_th = 0,threshold_flip=False)
# in case of mean_roi

# results. 
    #grid_LDOS_th

isns.imshow (grid_LDOS_th.LDOS_fb_th_label, aspect =1)
isns.imshow(grid_LDOS_th.LDOS_fb_th)
plt.show()




# +
#plot with labes 
import matplotlib.patches as mpatches
from skimage.segmentation import clear_border
from skimage.morphology import closing, square
from skimage.measure import label, regionprops

fig,ax =  plt.subplots(figsize =  (5,5))

isns.imshow (grid_LDOS_th.LDOS_fb_th_label, ax =ax, aspect = 1)
label_map = skimage.morphology.closing (grid_LDOS_th.LDOS_fb_th_label, skimage.morphology.square(2))
# use closing for ROI selection 
clear_border = False 

if clear_border == True :
    label_map_clear_border = skimage.segmentation.clear_border( label_map)
else :     label_map_clear_border =label_map
# clear border in the label map 

for region in skimage.measure.regionprops(label_map_clear_border):
    # take regions with large enough areas
    if region.area >= 5:
        # draw rectangle around segmented coins
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='red', linewidth=1)
        ax.add_patch(rect)
        
        (center_y,center_x) = region.centroid
        ax.annotate (region.label, xy= (center_x,center_y), c = 'r')
        # Anonotate region info by using region properties  
        
# use region properties to extract ROI info
plt.show()

# +
fig, ax = plt.subplots(figsize = (4,3))
#slctd_lables = [3,16,15,9,22]
slctd_lables = [1,2]

#for labels in range (int(grid_LDOS_th.LDOS_fb_th_label.max())):
for labels in slctd_lables:    
    sns.lineplot (x = 'bias_mV', y= 'LDOS_fb', 
              data = grid_LDOS_th.LDOS_fb.where(grid_LDOS_th.LDOS_fb_th_label ==labels ).mean(['X','Y']).to_dataframe(),
              ax =ax, label = str(labels))
plt.show()
# -

LDOS_fb_0_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label ==3 ).mean(["X","Y"]).to_dataframe()
LDOS_fb_1_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label !=3 ).mean(["X","Y"]).to_dataframe()
LDOS_fb_0_1_df = pd.concat( [LDOS_fb_0_df,LDOS_fb_1_df], axis= 1)
LDOS_fb_0_1_df.columns = ['(Area0)','(Area1)']
#LDOS_fb_0_1_df

# +
LDOS_fb_0_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label ==0 ).to_dataframe()
LDOS_fb_0_df= LDOS_fb_0_df.rename( columns ={'LDOS_fb':'LDOS_Area0'})
LDOS_fb_1_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label !=0 ).to_dataframe()
LDOS_fb_1_df= LDOS_fb_1_df.rename( columns ={'LDOS_fb':'LDOS_Area1'})
# rename columns 

LDOS_fb_0_1_df = pd.concat( [LDOS_fb_0_df,LDOS_fb_1_df], axis= 1)
#LDOS_fb_0_1_df = pd.concat( [LDOS_fb_0_df,LDOS_fb_1_df], axis= 1, join='outer')

LDOS_fb_0_1_df = LDOS_fb_0_1_df.reset_index()
#LDOS_fb_0_1_df
# -

####################33
# melt dataframe for avg plot
#####################
LDOS_fb_0_1_df_area_df_melt = LDOS_fb_0_1_df.melt(id_vars = ['Y','X', 'bias_mV'], value_vars = ['LDOS_Area0','LDOS_Area1'] )
LDOS_fb_0_1_df_area_df_melt.columns = ['Y','X','bias_mV', 'Area','LDOS']
LDOS_fb_0_1_df_area_df_melt

# +
fig,ax = plt.subplots(ncols = 3, figsize=(9,3))
isns.imshow (grid_LDOS_th.LDOS_fb_th, ax = ax[0]) 
ax[0].set_title('Thresholds')
isns.imshow (grid_LDOS_th.LDOS_fb_th.isnull(), ax = ax[1]) 
ax[1].set_title('Area Selection 0 or 1')

sns.lineplot(LDOS_fb_0_1_df_area_df_melt,x = 'bias_mV', y = 'LDOS', ax = ax[2], hue = 'Area')
#sns.lineplot( x  =LDOS_fb__1_df, data = LDOS_fb__1_df, ax = ax[2])
#sns.lineplot(grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label !=0 ).mean(["X","Y"]).to_dataframe(), ax = ax[2], label ='1')
ax[2].set_title('LDOS at Area 0 or 1')
plt.tight_layout()
plt.show()
# -

# #  Use find local peaks in 2D image 
#
#

# find local peaks in in topogrpahy --> atom assign 
#
#

isns.imshow(grid_topo.topography)

# +
from skimage.draw import disk

grid_topo_smth =  filter_gaussian_xr ( plane_fit_x_xr(plane_fit_y_xr(grid_topo)), sigma =30)
grid_topo_smth = filter_convert2grayscale ( filter_median_xr(grid_topo_smth))

im = grid_topo_smth.topography.values
im_ivt= 255-normalized_data


'''
normalized_data = 255 * (im - im.min()) / (im.max() - im.min())
# Ensure the values are within [0, 255] range
#normalized_data = np.clip(normalized_data, 0, 255).astype(np.uint8)
'''
#im
isns.imshow(im)

###############
# local max
# with peak_local_max #
# ** tested bulb detection &  extrema 
#   ==> not working for this image. 
###############

from scipy import ndimage as ndi
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage import data, img_as_float

# image_max is the dilation of im with a 20*20 structuring element
# It is used within peak_local_max function
image_max = ndi.maximum_filter(im_ivt, size=3, mode='constant')

# Comparison between image_max and im to find the coordinates of local maxima
coordinates = peak_local_max(im_ivt, min_distance=3)

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

# -

grid_topo_smth

grid_topo_smth.topography.zeros()

# +
grid_topo_smth['label'] = xr.zeros_like(grid_topo_smth.topography)
# deep position 1 
# Toward peak position (lower (-1 at -Y) 
# 1,2,3,4,5,6,=

for idx in coordinates:
    grid_topo_smth.label[idx[0], idx[1]] = 1
    grid_topo_smth.label[idx[0]-1, idx[1]] = 2
    grid_topo_smth.label[idx[0]-2, idx[1]] = 3
    grid_topo_smth.label[idx[0]-3, idx[1]] = 4
    grid_topo_smth.label[idx[0]-4, idx[1]] = 5
    grid_topo_smth.label[idx[0]-5, idx[1]] = 6
    grid_topo_smth.label[idx[0]-6, idx[1]] = 7
# draw a line 

isns.imshow(grid_topo_smth.label, cmap = 'inferno')

# +
# check filter for label 1 
#label1 = (grid_topo_smth.label == 1)
#label1#.sum()


label1 = (grid_topo_smth.label == 1)
label2 = (grid_topo_smth.label == 2)
label3 = (grid_topo_smth.label == 3)
label4 = (grid_topo_smth.label == 4)
label5 = (grid_topo_smth.label == 5)
label6 = (grid_topo_smth.label == 6)
label7 = (grid_topo_smth.label == 7)


# +
#grid_LDOS.LDOS_fb.where( label1,drop= True ).mean(dim = ["X","Y"]).plot()
# check averaged STS for label1
#grid_LDOS.LDOS_fb.where( label1, drop= True).to_dataframe().dropna()
# selected df for each label 
label1_df = grid_LDOS.LDOS_fb.where( label1, drop= True).to_dataframe().dropna()
label2_df = grid_LDOS.LDOS_fb.where( label2, drop= True).to_dataframe().dropna()
label3_df = grid_LDOS.LDOS_fb.where( label3, drop= True).to_dataframe().dropna()
label4_df = grid_LDOS.LDOS_fb.where( label4, drop= True).to_dataframe().dropna()
label5_df = grid_LDOS.LDOS_fb.where( label5, drop= True).to_dataframe().dropna()
label6_df = grid_LDOS.LDOS_fb.where( label6, drop= True).to_dataframe().dropna()
label7_df = grid_LDOS.LDOS_fb.where( label7, drop= True).to_dataframe().dropna()


frames = [label1_df, label2_df, label3_df, label4_df,label5_df,label6_df,label7_df]
keys = ['Dip1', 'Dip2', 'Dip3', 'Dip4','Dip5','Dip6','Dip7']

concatenated_df = pd.concat(frames, keys=keys)



concatenated_LDOS =  concatenated_df.reset_index()
# -

sns.lineplot(data=concatenated_df.reset_index(), x='bias_mV', y='LDOS_fb', hue='level_0', palette = 'inferno')


# +
############3
# bulb detection test 

############



from math import sqrt
from skimage import data
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.color import rgb2gray

import matplotlib.pyplot as plt

image_gray = im
blobs_log = blob_log(image_gray, max_sigma=1, num_sigma=10, threshold=.1)

# Compute radii in the 3rd column.
blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)

blobs_dog = blob_dog(image_gray, max_sigma=1, threshold=.1)
blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)

blobs_doh = blob_doh(image_gray, max_sigma=1, threshold=.01)

blobs_list = [blobs_log, blobs_dog, blobs_doh]
colors = ['yellow', 'lime', 'red']
titles = ['Laplacian of Gaussian', 'Difference of Gaussian',
          'Determinant of Hessian']
sequence = zip(blobs_list, colors, titles)

fig, axes = plt.subplots(1, 3, figsize=(9, 3), sharex=True, sharey=True)
ax = axes.ravel()

for idx, (blobs, color, title) in enumerate(sequence):
    ax[idx].set_title(title)
    ax[idx].imshow(im)
    for blob in blobs:
        y, x, r = blob
        c = plt.Circle((x, y), r, color=color, linewidth=2, fill=False)
        ax[idx].add_patch(c)
    ax[idx].set_axis_off()

plt.tight_layout()
plt.show()


# +
###   searching for extrema is not working 
### test h = 0.05 ~~ 10 ==> non 

import matplotlib.pyplot as plt

from skimage.measure import label
from skimage import data
from skimage import color
from skimage.morphology import extrema
from skimage import exposure
# Maxima in the galaxy image are detected by mathematical morphology.
# There is no a priori constraint on the density.

# We find all local maxima
local_maxima = extrema.local_maxima(im)
label_maxima = label(local_maxima)
overlay = color.label2rgb(label_maxima, im, alpha=0.7, bg_label=0,
                          bg_color=None, colors=[(1, 0, 0)])

# We observed in the previous image, that there are many local maxima
# that are caused by the noise in the image.
# For this, we find all local maxima with a height of h.
# This height is the gray level value by which we need to descent
# in order to reach a higher maximum and it can be seen as a local
# contrast measurement.
# The value of h scales with the dynamic range of the image, i.e.
# if we multiply the image with a constant, we need to multiply
# the value of h with the same constant in order to achieve the same result.
h = 10
h_maxima = extrema.h_maxima(im, h)
label_h_maxima = label(h_maxima)
overlay_h = color.label2rgb(label_h_maxima, im, alpha=0.7, bg_label=0,
                            bg_color=None, colors=[(1, 0, 0)])

# a new figure with 3 subplots
fig, ax = plt.subplots(1, 3, figsize=(15, 5))

ax[0].imshow(im, cmap='gray')
ax[0].set_title('Original image')
ax[0].axis('off')

ax[1].imshow(overlay)
ax[1].set_title('Local Maxima')
ax[1].axis('off')

ax[2].imshow(overlay_h)
ax[2].set_title(f'h maxima for h = {h:.2f}')
ax[2].axis('off')
plt.show()
# -

isns.imshow( filter_gaussian_xr ( 
    plane_fit_x_xr(plane_fit_y_xr(grid_topo)), 
    sigma = 0.5  ).topography,
            robust = True)
plt.show()





# #  <font color= orange > 2. gap & peak analysis (for Superconductor) </font>
#
#     * (optional) 2.0. Rotation 
#     * 2.1 BBox selection 
#     
#     
#     * 2.1. Smoothing 
#     * 2.1. 1.Savatzky Golay smoothing 
#            * window polyoder setting 
#     * 2.2. Numerical derivative 
#         * use xr API 
#     * 2.3. BBox avg for line avg plot with peaks 
#
#

#     * 2.5 finding peaks 
#
#         * 2.5.1. peaks from LDOS & d2(LDOS)/dV2
#             * draw line spectroscopy with peak positions
#             * compare point spectroscopy w.r.t. parameters. 
#         * 2.5.2. peaks position 3D drawing
#             * Zoomin Bbox + bias range 
#             * using Tomviz + npy 
#         * 2.5.3 peak properties 
#             * peak properties mapping 
#             * replace values ( for loop.. not many points..)
#
#
#
#     * 2.3 finding plateau
#         * 2.3.1. prepare plateau detection function for Grid_xr, point 
#         * 2.3.2. prepare plateau detection function for Grid_xr

# ## 2.1.rotate 3D_xr
#
# * if target area  requires rotation, use rotate_3D_xr function 
# * thereis separate rotate_2D function 
# * based on XR API 
#
#

# ## 2.0. # use Grid_LDOS

# +
##############
## rotate 3D_xr 
#####################
# rotation in degree not radian 
#################################
# grid_LDOS_rot = rotate_3D_xr(grid_LDOS,rotation_angle=0)
#############################################################
#hv_bias_mV_slicing(grid_LDOS_rot, ch ='LDOS_fb').opts(clim= (0,1E-10))
# hv plot & check rotation
#########################################################################

# +
grid_LDOS_rot  = grid_LDOS

#grid_LDOS_rot = rotate_3D_xr(grid_LDOS,rotation_angle=11)
# -


grid_LDOS_sg= savgolFilter_xr(grid_LDOS_rot, window_length=4, polyorder=3)

# +
##################################
# plot Grid_LDOS  & select BBox
#####################################

import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

#xr_data = grid_LDOS_sg
xr_data = grid_LDOS


ch = 'LDOS_fb'
frame_width = 600

xr_data_channel_hv = hv.Dataset(xr_data.LDOS_fb)

# bias_mV slicing
dmap_plane  = ["X","Y"]
dmap = xr_data_channel_hv.to(hv.Image,
                          kdims = dmap_plane,
                          dynamic = True )
dmap.opts(colorbar = True,
          cmap = 'bwr',
          frame_width = frame_width,
          aspect = 'equal')#.relabel('XY plane slicing: ')

xr_data_channel_hv_image  = hv.Dataset(xr_data[ch].isel(bias_mV = 0)).relabel('for BBox selection : ')

bbox_points = hv.Points(xr_data_channel_hv_image).opts(frame_width = frame_width,
                                                    color = 'k',
                                                    aspect = 'equal',
                                                    alpha = 0.1,                                   
                                                    tools=['box_select'])

bound_box = hv.streams.BoundsXY(source = bbox_points,
                                bounds=(0,0,0,0))
#dmap.opts(clim = (0,1E-9))*bbox_points
dmap*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box

# +
# function for drawing bbox averaged STS 
# only after bbox setup & streaming bound_box positions


def hv_bbox_avg (xr_data, bound_box , ch = 'LIX_fb' ,slicing_bias_mV = 0.5):
    '''
    ** only after Bound box settup with hV 
    
        import holoviews as hv
        from holoviews import opts
        hv.extension('bokeh')

        grid_channel_hv = hv.Dataset(grid_3D.I_fb)

        # bias_mV slicing
        dmap_plane  = ["X","Y"]
        dmap = grid_channel_hv.to(hv.Image,
                                  kdims = dmap_plane,
                                  dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = 200,
                  aspect = 'equal')#.relabel('XY plane slicing: ')

        grid_channel_hv_image  = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0)).relabel('for BBox selection : ')

        bbox_points = hv.Points(grid_channel_hv_image).opts(frame_width = 200,
                                                            color = 'k',
                                                            aspect = 'equal',
                                                            alpha = 0.1,                                   
                                                            tools=['box_select'])

        bound_box = hv.streams.BoundsXY(source = bbox_points,
                                        bounds=(0,0,0,0))
        dmap*bbox_points
        
        add grid_topo line profile 

    
    '''
    import holoviews as hv
    from holoviews import opts
    hv.extension('bokeh')
    # slicing bias_mV = 5 mV
    
    #bound_box.bounds
    x_bounds_msk = (xr_data.X > bound_box.bounds[0] ) & (xr_data.X < bound_box.bounds[2])
    y_bounds_msk = (xr_data.Y > bound_box.bounds[1] ) & (xr_data.Y < bound_box.bounds[3])

    xr_data_bbox = xr_data.where (xr_data.X[x_bounds_msk] + xr_data.Y[y_bounds_msk])
    
    #isns.reset_defaults()
    #isns.set_image(origin = 'lower')
    # isns image directino setting 

    fig,axs = plt.subplots (nrows = 1,
                            ncols = 3,
                            figsize = (12,4))

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[0],
                robust = True)

    # add rectangle for bbox 
    from matplotlib.patches import Rectangle
    # find index value of bound box 

    Bbox_x0 = np.abs((xr_data.X-bound_box.bounds[0]).to_numpy()).argmin()
    Bbox_y0 = np.abs((xr_data.Y-bound_box.bounds[1]).to_numpy()).argmin()
    Bbox_x1 = np.abs((xr_data.X-bound_box.bounds[2]).to_numpy()).argmin()
    Bbox_y1 = np.abs((xr_data.Y-bound_box.bounds[3]).to_numpy()).argmin()
    Bbox = Bbox_x0,Bbox_y0,Bbox_x1,Bbox_y1
    # substract value, absolute value with numpy, argmin returns index value

    # when add rectangle, add_patch used index 
    axs[0].add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                               Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                               edgecolor = 'pink',
                               fill=False,
                               lw=2,
                               alpha=1))

    isns.imshow(xr_data_bbox[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[1],
                robust = True)
    sns.lineplot(x = "bias_mV",
                 y = ch, 
                 data = xr_data_bbox.to_dataframe(),
                 ax = axs[2])
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 
# +
#grid_LDOS_bbox,_ = hv_bbox_avg(grid_LDOS_sg, ch ='LDOS_fb',slicing_bias_mV=-0 , bound_box = bound_box)

grid_LDOS_bbox,_ = hv_bbox_avg(grid_LDOS, ch ='LDOS_fb',slicing_bias_mV=-0 , bound_box = bound_box)

# +
#grid_LDOS_bbox

# +
# grid_LDOS_bbox

average_in= 'Y'

grid_LDOS_bbox_pk = grid3D_line_avg_pks(grid_LDOS_bbox) 
grid_LDOS_bbox_pk  = grid3D_line_avg_pks( grid_LDOS_bbox ,
                                         ch_l_name ='LDOS_fb',
                                         average_in= average_in,
                                         distance = 8, 
                                         width= 9,
                                         threshold = 2E-11, 
                                         padding_value= 0,
                                         prominence=2E-11
                                        ) 
grid_LDOS_bbox_pk

grid_LDOS_bbox_pk_slct, grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df, fig = grid_lineNpks_offset(
    grid_LDOS_bbox_pk,
    ch_l_name ='LDOS_fb',
    plot_y_offset= 2E-11,
    peak_LIX_min = 2E-11,
    legend_title = "Y (nm)")

plt.show()

# +
grid_LDOS_bbox_pk_df

#################
##  Classify peaks by using k-mean clustering 
####################

from sklearn.cluster import KMeans

X = grid_LDOS_bbox_pk_df[['bias_mV', 'LDOS_fb_offset']].values

kmeans = KMeans(n_clusters=11)
kmeans.fit(X)

y_kmeans = kmeans.predict(X)
grid_LDOS_bbox_pk_df['y_kmeans']=y_kmeans

grid_LDOS_bbox_pk_df_choose
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='viridis')
plt.show()
# -

grid_LDOS_bbox_pk_df
sns.color_palette("tab10")
sns.scatterplot( data  = grid_LDOS_bbox_pk_df, x = 'bias_mV', y = 'LDOS_fb_offset', hue = y_kmeans, palette='deep' , legend ='full')
plt.show()

# +
# y_kmeans

# +
##############
# Fig plot again (remove 0th peak points) 

#grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df


#############
# Choose peak labels
###############
grid_LDOS_bbox_pk_df_choose = grid_LDOS_bbox_pk_df [(grid_LDOS_bbox_pk_df.y_kmeans  ==1) |(grid_LDOS_bbox_pk_df.y_kmeans  == 3)]


##########
#grid_LDOS_bbox_pk_df =  grid_LDOS_bbox_pk_df[grid_LDOS_bbox_pk_df.bias_mV<=8]
# remove 0th peak points 
ch_l_name = 'LDOS_fb'
xr_data_l_pks = grid_LDOS_bbox_pk
legend_title = "X (nm)"

fig,ax = plt.subplots(figsize = (5,7))

sns.lineplot(data = grid_LDOS_bbox_df,
                     x ='bias_mV', 
                     y = ch_l_name+'_offset',
                     palette = "rocket",
                     hue = xr_data_l_pks.line_direction,
                     ax = ax,legend='full')

sns.scatterplot(data = grid_LDOS_bbox_pk_df_choose,
                        x ='bias_mV',
                        y = ch_l_name+'_offset',
                        #s = 20,
                        palette ="rocket",
                        hue = xr_data_l_pks.line_direction,
                
                        ax = ax,legend='full')
# legend control!( cut the handles 1/2)
ax.set_xlabel('Bias (mV)')   
#ax.set_ylabel(ch_l_name+'_offset')   
ax.set_ylabel('LDOS')   
ax.set_xlim(-1.0,1.0)
#ax.set_ylim(-1.0E-9,6.0E-9)

ax.vlines(x = 0, ymin=ax.get_ylim()[0],  ymax=ax.get_ylim()[1], linestyles='dashed',alpha = 0.5, color= 'k')

handles0, labels0 = ax.get_legend_handles_labels()
handles1 = handles0[:int(len(handles0)//2)]
labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
handles2 = handles1[::5][::-1]
labels2 = labels1[::5][::-1]
# convert the line length as nm
print(labels2)
ax.legend(handles2,   labels2, title = legend_title,loc='upper right', bbox_to_anchor=(1.3, 0.5))
# use the half of legends (line + scatter) --> use lines only
plt.show()

# +
#grid_topo_bbox,_  = hv_bbox_topo_avg(grid_topo, ch = 'topography',bound_box=bound_box )

#grid_topo_o = grid_xr[['topography']]
grid_topo_o = grid_topo

grid_topo_bbox, grid_topo_o_l_pf  = hv_bbox_topo_avg(grid_topo_o, ch = 'topography',bound_box=bound_box )


# +
##############
# Fig plot again (remove 0th peak points) 

#grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df

##########
grid_LDOS_bbox_pk_df=  grid_LDOS_bbox_pk_df[grid_LDOS_bbox_pk_df.bias_mV<=8]
# remove 0th peak points 
ch_l_name = 'LDOS_fb'
xr_data_l_pks = grid_LDOS_bbox_pk
legend_title = "Y (nm)"

fig,axs = plt.subplots(ncols =2, figsize = (9,7))

sns.lineplot(data = grid_LDOS_bbox_df,
                     x ='bias_mV', 
                     y = ch_l_name+'_offset',
                     palette = "rocket",
                     hue = xr_data_l_pks.line_direction,
                     ax = axs[0],legend='full')

sns.scatterplot(data = grid_LDOS_bbox_pk_df,
                        x ='bias_mV',
                        y = ch_l_name+'_offset',
                        palette ="rocket",
                        hue = xr_data_l_pks.line_direction,
                        ax = axs[0],legend='full')
# legend control!( cut the handles 1/2)
axs[0].set_xlabel('Bias (mV)')   
#ax.set_ylabel(ch_l_name+'_offset')   
axs[0].set_ylabel('LDOS')   
axs[0].set_xlim(-2.4,2.4)


handles0, labels0 = axs[0].get_legend_handles_labels()
handles1 = handles0[:int(len(handles0)//2)]
labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
handles2 = handles1[::5][::-1]
labels2 = labels1[::5][::-1]
# convert the line length as nm
print(labels2)
axs[0].legend(handles2,   labels2, title = legend_title)
# use the half of legends (line + scatter) --> use lines only

# add Z profile 

topo_vertical = sns.lineplot(grid_topo_bbox.mean(dim = ['X']).to_dataframe(), ax = axs[1])

topo_vertical_x,topo_vertical_y =topo_vertical.lines[0].get_data()
topo_vertical.clear()
# create new plot on the axes, inverting x and y

# ax.fill_between(c[:,1], c[:,0], alpha=0.5)
#fill between case 

axs[1].plot(topo_vertical_y,topo_vertical_x)
axs[1].set_xlabel('Topography (z)')    
axs[1].set_ylabel('Y')    

plt.show()

# -


# ##### for Y 

# +
##############
# Fig plot again (remove 0th peak points) 

#grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df

##########
grid_LDOS_bbox_pk_df=  grid_LDOS_bbox_pk_df[grid_LDOS_bbox_pk_df.bias_mV<=8]
# remove 0th peak points 
ch_l_name = 'LDOS_fb'
xr_data_l_pks = grid_LDOS_bbox_pk
legend_title = "Y (nm)"

fig,axs = plt.subplots(ncols =3, figsize = (12,7))

sns.lineplot(data = grid_LDOS_bbox_df,
                     x ='bias_mV', 
                     y = ch_l_name+'_offset',
                     palette = "rocket",
                     hue = xr_data_l_pks.line_direction,
                     ax = axs[0],legend='full')

sns.scatterplot(data = grid_LDOS_bbox_pk_df,
                        x ='bias_mV',
                        y = ch_l_name+'_offset',
                        palette ="rocket",
                        hue = xr_data_l_pks.line_direction,
                        ax = axs[0],legend='full')
# legend control!( cut the handles 1/2)
axs[0].set_xlabel('Bias (mV)')   
#ax.set_ylabel(ch_l_name+'_offset')   
axs[0].set_ylabel('LDOS')   
axs[0].set_xlim(-2.4,2.4)


handles0, labels0 = axs[0].get_legend_handles_labels()
handles1 = handles0[:int(len(handles0)//2)]
labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
handles2 = handles1[::5][::-1]
labels2 = labels1[::5][::-1]
# convert the line length as nm
print(labels2)
axs[0].legend(handles2,   labels2, title = legend_title, loc='upper left', bbox_to_anchor=(1, 0.4))

# use the half of legends (line + scatter) --> use lines only

# add Z profile 

topo_vertical = sns.lineplot(grid_topo_bbox.mean(dim = ['X']).to_dataframe(), ax = axs[1])

topo_vertical_x,topo_vertical_y =topo_vertical.lines[0].get_data()
topo_vertical.clear()
# create new plot on the axes, inverting x and y

# ax.fill_between(c[:,1], c[:,0], alpha=0.5)
#fill between case 

axs[1].plot(topo_vertical_y,topo_vertical_x)
axs[1].set_xlabel('Topography (z)')    
axs[1].set_ylabel('X')    



# add LDOS profile 

plane_fit_y_df(grid_LDOS_bbox_pk_df)

LDOS_l_pf_vertical = sns.lineplot (x = 'Y', 
                                   y = 'LDOS_fb_offset', 
                                   data  = grid_LDOS_bbox_pk_df.groupby('Y').mean())

LDOS_l_pf_vertical_x,LDOS_l_pf_vertical_y =LDOS_l_pf_vertical.lines[0].get_data()
LDOS_l_pf_vertical.clear()
# create new plot on the axes, inverting x and y

axs[2].plot(LDOS_l_pf_vertical_y,LDOS_l_pf_vertical_x)
axs[2].set_xlabel('LDOS')    
axs[2].set_ylabel('Y')    

plt.tight_layout()


plt.show()

# -


# ##### for X

# +
##############
# Fig plot again (remove 0th peak points) 

#grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df

##########
grid_LDOS_bbox_pk_df=  grid_LDOS_bbox_pk_df[grid_LDOS_bbox_pk_df.bias_mV<=8]
# remove 0th peak points 
ch_l_name = 'LDOS_fb'
xr_data_l_pks = grid_LDOS_bbox_pk
legend_title = "Y (nm)"

fig,axs = plt.subplots(ncols =3, figsize = (12,7))

sns.lineplot(data = grid_LDOS_bbox_df,
                     x ='bias_mV', 
                     y = ch_l_name+'_offset',
                     palette = "rocket",
                     hue = xr_data_l_pks.line_direction,
                     ax = axs[0],legend='full')

sns.scatterplot(data = grid_LDOS_bbox_pk_df,
                        x ='bias_mV',
                        y = ch_l_name+'_offset',
                        palette ="rocket",
                        hue = xr_data_l_pks.line_direction,
                        ax = axs[0],legend='full')
# legend control!( cut the handles 1/2)
axs[0].set_xlabel('Bias (mV)')   
#ax.set_ylabel(ch_l_name+'_offset')   
axs[0].set_ylabel('LDOS')   
axs[0].set_xlim(-2.2,2.2)


handles0, labels0 = axs[0].get_legend_handles_labels()
handles1 = handles0[:int(len(handles0)//2)]
labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
handles2 = handles1[::5][::-1]
labels2 = labels1[::5][::-1]
# convert the line length as nm
print(labels2)
axs[0].legend(handles2,   labels2, title = legend_title, loc='upper left', bbox_to_anchor=(1, 0.4))

# use the half of legends (line + scatter) --> use lines only

# add Z profile 

topo_vertical = sns.lineplot(grid_topo_bbox.mean(dim = ['Y']).to_dataframe(), ax = axs[1])

topo_vertical_x,topo_vertical_y =topo_vertical.lines[0].get_data()
topo_vertical.clear()
# create new plot on the axes, inverting x and y

# ax.fill_between(c[:,1], c[:,0], alpha=0.5)
#fill between case 

axs[1].plot(topo_vertical_y,topo_vertical_x)
axs[1].set_xlabel('Topography (z)')    
axs[1].set_ylabel('X')    



# add LDOS profile 

#plane_fit_y_df(grid_LDOS_bbox_pk_df)

LDOS_l_pf_vertical = sns.lineplot (x = 'X', 
                                   y = 'LDOS_fb_offset', 
                                   data  =grid_LDOS_bbox_pk_df.groupby('X').mean())

LDOS_l_pf_vertical_x,LDOS_l_pf_vertical_y =LDOS_l_pf_vertical.lines[0].get_data()
LDOS_l_pf_vertical.clear()
# create new plot on the axes, inverting x and y

axs[2].plot(LDOS_l_pf_vertical_y,LDOS_l_pf_vertical_x)
axs[2].set_xlabel('LDOS')    
axs[2].set_ylabel('Y')    

plt.tight_layout()


plt.show()

# -


# #### space 

#
# ### 2.3 finding plateau
#     * 2.3.1. prepare plateau detection function for Grid_xr, point 
#     * 2.3.2. prepare plateau detection function for Grid_xr
#
#

# #### 2.3.1. prepare plateau detection function for Grid_xr, point 
#
#     * set  Tolerence to find plateau
#
#         * 2.3.1.1. Set tolerance for I_fb * LIX_fb

find_plateau_tolarence_values(grid_3D, x_i= sliderX.value  ,  y_j= sliderY.value ,ch ='LIX_fb',slicing_bias_mV = 0.2, tolerance_I= 1E-11, tolerance_LIX = 1E-12)

# #  <font color= orange > 3. FFT & peak analysis (for P6 symmetry) </font>
#
#     * 3.0. FFT xr
#     * 3.0.1. test reference lattice 
# by using [lattice gen](https://moire-lattice-generator.readthedocs.io/en/latest/index.html#)
#         
#     * 3.1. lattcies 
#     

grid_LDOS_fft  = twoD_FFT_xr(grid_LDOS)

help(latticegen.anylattice_gen)


# +
import latticegen
# import latticegen 
# r_k = 

# if image size = X nm = 512 pixel =  n*a0 atom lattice = 10nm 
# r_x = 1/a= n/512 = (image size/ a0)/pixel 

# offset  later 


ref_lattice = latticegen.anylattice_gen(r_k=(32/0.542/200), theta=0,
                                    order=1, symmetry=3, size = 200)
# -

#plt.imshow(twoD_FFT(ref_lattice).T)
plt.imshow(ref_lattice.T)

# +
#twoD_FFT(ref_lattice)

grid_LDOS['ref_array']= xr.DataArray(data = ref_lattice, dims = ["X","Y"])
# -

twoD_FFT_xr(grid_LDOS).ref_array_fft.plot(robust = True)


plt.imshow(lattice.T)

#grid_topo.topography.isel(image_size )
grid_topo.isel (X = int (len(grid_topo.X)/2)).isel (Y = int (len(grid_topo.Y)/2))



fft_0 = grid_LDOS_fft.sel(freq_bias_mV = 0, method = 'nearest').LDOS_fb_fft
isns.imshow(fft_0, robust = True)


### Xr rotation function 
# rotate the XY plan in xr data 
def rotate_3D_fft_xr (xrdata, rotation_angle): 
    # padding first 
    for ch_i,ch_name in enumerate (xrdata):
        if ch_i == 0:  # use only the first channel to calculate a padding size 
            padding_shape = skimage.transform.rotate(xrdata[ch_name].values.astype('float64'),
                                                     rotation_angle,
                                                     resize = True).shape[:2]
            # After rotation, still 3D shape ->  [:2]
            
            padding_xy = (np.array( padding_shape)-np.array(xrdata[ch_name].shape[:2]) +1)/2
            padding_xy = padding_xy.astype(int)
    xrdata_pad = xrdata.pad(freq_X=(padding_xy[0],padding_xy[0]), 
                            freq_Y =(padding_xy[1],padding_xy[1]),
                            mode='constant',
                            cval = xrdata.min())
    if np.array(xrdata_pad[ch_name]).shape[:2] != padding_shape:
        # in case of xrdata_pad shape is +1 larger than real padding_shape
        # index 다루는 법  (X)
        x_spacing = np.diff(xrdata.freq_X).mean()
        y_spacing = np.diff(xrdata.freq_Y).mean()
        xrdata.freq_X[0]
        xrdata.freq_Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata.X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata.Y.shape[0])

        x_pad_arr =  np.linspace(-1*padding_xy[0]*x_spacing, x_spacing*x_pad_dim,x_pad_dim+1)
        y_pad_arr =  np.linspace(-1*padding_xy[1]*y_spacing, y_spacing*y_pad_dim,y_pad_dim+1)

        # 0 에서 전체 크기 만큼 padding 한결과를 array 만들고 offset 은 pad_x 만큼 
        x_pad_arr.shape
        y_pad_arr.shape
        xrdata_pad = xrdata_pad.assign_coords( {"freq_X" :  x_pad_arr}).assign_coords({"freq_Y" :  y_pad_arr})
        xrdata_rot = xrdata_pad.sel(freq_X = xrdata_pad.freq_X[:-1].values, freq_Y = xrdata_pad.freq_Y[:-1].values)
        print ('padding size != rot_size')
    else : # np.array(xrdata_pad[ch_name]).shape == padding_shape 
            # in case of xrdata_pad shape is +1 larger than real padding_shape

        # index 다루는 법  (X)
        x_spacing = np.diff(xrdata.freq_X).mean()
        y_spacing = np.diff(xrdata.freq_Y).mean()
        xrdata.freq_X[0]
        xrdata.freq_Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata.X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata.Y.shape[0])

        x_pad_arr =  np.linspace(-1*padding_xy[0]*x_spacing, x_spacing*x_pad_dim,x_pad_dim)
        y_pad_arr =  np.linspace(-1*padding_xy[1]*y_spacing, y_spacing*y_pad_dim,y_pad_dim)

        # 0 에서 전체 크기 만큼 padding 한결과를 array 만들고 offset 은 pad_x 만큼 
        x_pad_arr.shape
        y_pad_arr.shape
        xrdata_pad = xrdata_pad.assign_coords( {"freq_X" :  x_pad_arr}).assign_coords({"freq_Y" :  y_pad_arr})
        xrdata_rot = xrdata_pad.copy()      
        print ('padding size == rot_size')
    # call 1 channel
        # use the list_comprehension for bias_mV range
        # list comprehension is more faster
        # after rotation, resize = False! , or replacement size error! 
        # replace the channel(padded) 3D data as a new 3D (rotated )data set 

    for ch in xrdata_pad:
        xrdata_rot[ch].values = skimage.transform.rotate(xrdata[ch].values.astype('float64'),
                                                         rotation_angle,
                                                         cval =xrdata[ch].to_numpy().min(),
                                                         resize = True)
    return xrdata_rot
# ### average X or Y direction jof Grid_3D dataset 
# * use xr_data (3D)
# * average_in = 'X' or 'Y'
# * ch_l_name = channel name for line profile  

grid_LDOS_fft_rot =  rotate_3D_fft_xr(grid_LDOS_fft, 120)


def hv_fft_bias_mV_slicing(xr_data,ch = 'LDOS_fb_fft',frame_width = 200,cmap = 'bwr'): 
    '''
    input : xarray dataset 
    output : holoview image
    
    * slicing 3D data set in XY plane 
    * bias_mV is knob
    
    default channel  =  'LIX_fb',  or assgin 'I_fb' or 'LDOS_fb'
    default setting for frame width and cmap  can be changed. 
    
    if you need to add color limit 
        add ".opts(clim=(0, 1E-10))"
        
    '''
    
    import holoviews as hv
    from holoviews import opts

    xr_data_hv = hv.Dataset(xr_data[ch])

    hv.extension('bokeh')
    ###############
    # bias_mV slicing
    dmap_plane  = ["freq_X","freq_Y"]
    dmap = xr_data_hv.to(hv.Image,
                         kdims = dmap_plane,
                         dynamic = True )
    dmap.opts(colorbar = True,
              cmap = 'bwr',
              frame_width = frame_width,
              aspect = 'equal').relabel('XY plane slicing: ')
    fig = hv.render(dmap)
    return dmap   


hv_fft_bias_mV_slicing(np.log(grid_LDOS_fft_rot), ch = 'LDOS_fb_fft',frame_width=300)


def hv_fft_XY_slicing(xr_data,ch = 'LDOS_fb_fft', slicing= 'X', frame_width = 200,cmap = 'bwr'): 
    '''
    input : xarray dataset 
    output : holoview image 
    
    
    * slicing 3D data set in X-bias_mV or Y-bias_mV plane 
    * X or Y position is knob
    
    
    default channel  =  'LIX_fb',  or assgin 'I_fb'
    default setting for frame width and cmap  can be changed. 
    if you need to add color limit 
     
    add ".opts(clim=(0, 1E-10))"
    
    '''
    import holoviews as hv
    from holoviews import opts

    xr_data_hv = hv.Dataset(xr_data[ch])

    hv.extension('bokeh')
    ###############
    # bias_mV slicing
    if slicing == 'freq_Y':
        dmap_plane  = [ "freq_X","freq_bias_mV"]

        dmap = xr_data_hv.to(hv.Image,
                             kdims = dmap_plane,
                             dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = frame_width).relabel('X - bias_mV plane slicing: ')
    else : #slicing= 'freq_X'
        dmap_plane  = [ "freq_Y","freq_bias_mV"]

        dmap = xr_data_hv.to(hv.Image,
                             kdims = dmap_plane,
                             dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = frame_width).relabel('Y - bias_mV plane slicing: ')
    fig = hv.render(dmap)
    return dmap   


hv_fft_XY_slicing(np.log(grid_LDOS_fft), ch = 'LDOS_fb_fft',slicing= 'freq_Y', frame_width=300)

# +
## BBOX selection from FFT plot 

# +
##################################
# plot Grid_LDOS_fft  & select BBox
#####################################

import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

xr_data = np.log(grid_LDOS_fft_rot)
ch = 'LDOS_fb_fft'
frame_width = 400

xr_data_channel_hv = hv.Dataset(xr_data[ch])

# bias_mV slicing
dmap_plane  = ["freq_X","freq_Y"]
dmap = xr_data_channel_hv.to(hv.Image,
                          kdims = dmap_plane,
                          dynamic = True )
dmap.opts(colorbar = True,
          cmap = 'bwr',
          frame_width = frame_width,
          aspect = 'equal')#.relabel('XY plane slicing: ')

xr_data_channel_hv_image  = hv.Dataset(xr_data[ch].isel(freq_bias_mV = 0)).relabel('for BBox selection : ')

bbox_points = hv.Points(xr_data_channel_hv_image).opts(frame_width = frame_width,
                                                    color = 'k',
                                                    aspect = 'equal',
                                                    alpha = 0.1,                                   
                                                    tools=['box_select'])

bound_box_fft = hv.streams.BoundsXY(source = bbox_points,
                                bounds=(0,0,0,0))
#dmap.opts(clim = (0,1E-9))*bbox_points
dmap*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box_fft


def hv_fft_bbox_crop (xr_data, bound_box , ch = 'LDOS_fb_fft' ,slicing_bias_mV = 0.5):
    '''
    use cropped BBox area 
    freq_X or freq_Y  vs  Bias plot 
    
    '''
    import holoviews as hv
    from holoviews import opts
    hv.extension('bokeh')
    # slicing bias_mV = 5 mV
    
    #bound_box.bounds
    x_bounds_msk = (xr_data.freq_X > bound_box.bounds[0] ) & (xr_data.freq_X < bound_box.bounds[2])
    y_bounds_msk = (xr_data.freq_Y > bound_box.bounds[1] ) & (xr_data.freq_Y < bound_box.bounds[3])

    xr_data_bbox = xr_data.where (xr_data.freq_X[x_bounds_msk] + xr_data.freq_Y[y_bounds_msk])
    
    fig,axs = plt.subplots (nrows = 1,
                            ncols = 2,
                            figsize = (12,4))

    isns.imshow(xr_data[ch].sel(freq_bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[0],
                robust = True)

    # add rectangle for bbox 
    from matplotlib.patches import Rectangle
    # find index value of bound box 

    Bbox_x0 = np.abs((xr_data.freq_X-bound_box.bounds[0]).to_numpy()).argmin()
    Bbox_y0 = np.abs((xr_data.freq_Y-bound_box.bounds[1]).to_numpy()).argmin()
    Bbox_x1 = np.abs((xr_data.freq_X-bound_box.bounds[2]).to_numpy()).argmin()
    Bbox_y1 = np.abs((xr_data.freq_Y-bound_box.bounds[3]).to_numpy()).argmin()
    Bbox = Bbox_x0,Bbox_y0,Bbox_x1,Bbox_y1
    # substract value, absolute value with numpy, argmin returns index value

    # when add rectangle, add_patch used index 
    axs[0].add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                               Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                               edgecolor = 'red',
                               fill=False,
                               lw=2,
                               alpha=1))

    isns.imshow(xr_data_bbox[ch].sel(freq_bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[1],
                robust = True)
    #sns.lineplot(x = "freq_bias_mV",
    #             y = ch, 
    #             data = xr_data_bbox.to_dataframe(),
    #             ax = axs[2])
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    
    
    return xr_data_bbox


grid_LDOS_fft_bbox = hv_fft_bbox_crop(grid_LDOS_fft_rot, bound_box_fft)

np.log(grid_LDOS_fft_bbox.mean(dim = "freq_Y").LDOS_fb_fft).T.plot(robust = True)

# +
# function for drawing bbox averaged STS 
# only after bbox setup & streaming bound_box positions


def hv_bbox_avg (xr_data, bound_box , ch = 'LIX_fb' ,slicing_bias_mV = 0.5):
    '''
    ** only after Bound box settup with hV 
    
        import holoviews as hv
        from holoviews import opts
        hv.extension('bokeh')

        grid_channel_hv = hv.Dataset(grid_3D.I_fb)

        # bias_mV slicing
        dmap_plane  = ["X","Y"]
        dmap = grid_channel_hv.to(hv.Image,
                                  kdims = dmap_plane,
                                  dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = 200,
                  aspect = 'equal')#.relabel('XY plane slicing: ')

        grid_channel_hv_image  = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0)).relabel('for BBox selection : ')

        bbox_points = hv.Points(grid_channel_hv_image).opts(frame_width = 200,
                                                            color = 'k',
                                                            aspect = 'equal',
                                                            alpha = 0.1,                                   
                                                            tools=['box_select'])

        bound_box = hv.streams.BoundsXY(source = bbox_points,
                                        bounds=(0,0,0,0))
        dmap*bbox_points
        
        add grid_topo line profile 

    
    '''
    import holoviews as hv
    from holoviews import opts
    hv.extension('bokeh')
    # slicing bias_mV = 5 mV
    
    #bound_box.bounds
    x_bounds_msk = (xr_data.X > bound_box.bounds[0] ) & (xr_data.X < bound_box.bounds[2])
    y_bounds_msk = (xr_data.Y > bound_box.bounds[1] ) & (xr_data.Y < bound_box.bounds[3])

    xr_data_bbox = xr_data.where (xr_data.X[x_bounds_msk] + xr_data.Y[y_bounds_msk])
    
    isns.reset_defaults()
    isns.set_image(origin = 'lower')
    # isns image directino setting 

    fig,axs = plt.subplots (nrows = 1,
                            ncols = 3,
                            figsize = (12,4))

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[0],
                robust = True)

    # add rectangle for bbox 
    from matplotlib.patches import Rectangle
    # find index value of bound box 

    Bbox_x0 = np.abs((xr_data.X-bound_box.bounds[0]).to_numpy()).argmin()
    Bbox_y0 = np.abs((xr_data.Y-bound_box.bounds[1]).to_numpy()).argmin()
    Bbox_x1 = np.abs((xr_data.X-bound_box.bounds[2]).to_numpy()).argmin()
    Bbox_y1 = np.abs((xr_data.Y-bound_box.bounds[3]).to_numpy()).argmin()
    Bbox = Bbox_x0,Bbox_y0,Bbox_x1,Bbox_y1
    # substract value, absolute value with numpy, argmin returns index value

    # when add rectangle, add_patch used index 
    axs[0].add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                               Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                               edgecolor = 'pink',
                               fill=False,
                               lw=2,
                               alpha=0.5))

    isns.imshow(xr_data_bbox[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[1],
                robust = True)
    sns.lineplot(x = "bias_mV",
                 y = ch, 
                 data = xr_data_bbox.to_dataframe(),
                 ax = axs[2])
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 
# -
# #  save npy for tomviz 




grid_LDOS_bbox

grid_LDOS_rot=grid_LDOS.copy()

# +
# use grid_LDOS_rot for 120x 120 
#grid_LDOS_rot

grid_LDOS_sg = savgolFilter_xr(grid_LDOS_rot, window_length=61, polyorder=5)
grid_LDOS_1diff =  grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1diff_sg = savgolFilter_xr(grid_LDOS_1diff, window_length=61, polyorder=5)
grid_LDOS_2diff =  grid_LDOS_1diff_sg.differentiate('bias_mV')
grid_LDOS_2diff_sg = savgolFilter_xr(grid_LDOS_2diff, window_length=61, polyorder=5)

# -

grid_LDOS_2diff_sg_dps = find_peaks_xr(-1*grid_LDOS_2diff_sg,distance = 10, width = 5,threshold = 2E-12,prominence= 4E-11 )
grid_LDOS_2diff_sg_dps_pad = peak_pad ( grid_LDOS_2diff_sg_dps)
grid_LDOS_2diff_sg_dps_pad

# +
grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch = 'LDOS_fb')

grid_LDOS_2diff_sg_dps_pad_mV#grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV.sum()


grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch= 'LDOS_fb')
#grid_LDOS_2diff_sg_zm_dps_pad_mV



grid_LDOS_rot['LDOS_pk_mV'] = (grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV * grid_LDOS_rot.LDOS_fb).astype(float)
grid_LDOS_rot
# extract the peak positions 
# -

np.save('LDOS008_001_pk_zm_mV.npy', grid_LDOS_rot.LDOS_pk_mV.where((grid_LDOS_rot.bias_mV> - 3.6)& (grid_LDOS_rot.bias_mV<3.6), drop = True).to_numpy())

# #  <font color= orange > 3. zero bias map analysis (for MZM) </font>
#



# #  <font color= orange >  Find SC peaks </font>
# * After 3D_SCGap 
#
#

# +
grid_3D_gap

grid_LDOS = grid_3D_gap[['LDOS_fb']]
grid_LDOS
# -

find_peaks

grid_LDOS_rot=grid_LDOS

# +
# use grid_LDOS_rot for 120x 120 
#grid_LDOS_rot

grid_LDOS_sg = savgolFilter_xr(grid_LDOS_rot, window_length=5, polyorder=3)
grid_LDOS_1diff =  grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1diff_sg = savgolFilter_xr(grid_LDOS_1diff, window_length=5, polyorder=3)
grid_LDOS_2diff =  grid_LDOS_1diff_sg.differentiate('bias_mV')
grid_LDOS_2diff_sg = savgolFilter_xr(grid_LDOS_2diff, window_length=5, polyorder=3)

# -

grid_LDOS_2diff_sg_dps = find_peaks_xr(-1*grid_LDOS_2diff_sg,distance = 3, width = 3,threshold = 1E-12,prominence= 0.4E-11 )
grid_LDOS_2diff_sg_dps_pad = peak_pad ( grid_LDOS_2diff_sg_dps)
grid_LDOS_2diff_sg_dps_pad

# +
grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch = 'LDOS_fb')

grid_LDOS_2diff_sg_dps_pad_mV#grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV.sum()


grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch= 'LDOS_fb')
#grid_LDOS_2diff_sg_zm_dps_pad_mV



grid_LDOS_rot['LDOS_pk_mV'] = (grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV * grid_LDOS_rot.LDOS_fb).astype(float)
grid_LDOS_rot
# extract the peak positions 
# -

grid_LDOS_rot.LDOS_pk_mV.sel(bias_mV= 0, method= 'nearest').plot()


def find_peaks_xr(xrdata, height= None, threshold=None, distance=None, prominence = None, width=None): 
    from scipy.signal import find_peaks
    xrdata_prcssd = xrdata.copy(deep = True)
    print('Find peaks in STS to an xarray Dataset.')

    for data_ch in xrdata:
        if len(xrdata[data_ch].dims)==2:
            # smoothing filter only for the 3D data set
                    # ==> updated             
            
            

            ### 2D data case 
            ### assume that coords are 'X','Y','bias_mV'
            #### two case X,bias_mV or Y,bias_mV 
            if 'X' in xrdata[data_ch].dims :
                # xrdata is X,bias_mV 
                # use the isel(X = x) 
                x_axis = xrdata.X.size

                #print(xrdata_prcssd[data_ch])

                xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                    np.array([ find_peaks(xrdata[data_ch].isel(X = x).values, height =height, distance = distance, threshold = threshold, prominence= prominence, width =width)
                              for x in range(x_axis)], dtype = object )[:,0],
                dims=["X"],
                coords={"X": xrdata.X})
            
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size

                #print(xrdata_prcssd[data_ch])

                xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                    np.array([ find_peaks(xrdata[data_ch].isel(Y = y).values, height =height, distance = distance,threshold = threshold, prominence=prominence, width=width)
                              for y in range(y_axis)], dtype = object )[:,0],
                dims=["Y"],
                coords={"Y": xrdata.Y})
            
            # ==> updated 
            
        elif len(xrdata[data_ch].dims) == 3:
            
            x_axis = xrdata.X.size
            y_axis = xrdata.Y.size
            print (data_ch)
            xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values, height =height, distance = distance,threshold = threshold,prominence=prominence, width=width)[0] 
                          for y in range(y_axis)  
                          for x in range(x_axis)], dtype = object ).reshape(x_axis,y_axis),
                dims=["X", "Y"],
                coords={"X": xrdata.X, "Y": xrdata.Y})         
        elif len(xrdata[data_ch].dims) == 1:
            if 'bias_mV' in xrdata.dims: 
                for data_ch in xrdata: 
                    xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (find_peaks (xrdata[data_ch], height =height, distance = distance,threshold = threshold, prominence= prominence, width= width))
        else : pass
    return xrdata_prcssd
#grid_2D_sg_pks = find_peaks_xr(grid_2D_sg)

grid_LDOS_2diff_sg_dps = find_peaks_xr(-1*grid_LDOS_2diff_sg,distance = 3, width = 3,threshold = 1E-12,prominence= 0.2E-11 )

grid_LDOS_2diff_sg_dps_pad = peak_pad ( grid_LDOS_2diff_sg_dps)
grid_LDOS_2diff_sg_dps_pad

# +
grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch = 'LDOS_fb')

grid_LDOS_2diff_sg_dps_pad_mV#grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV.sum()


grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch= 'LDOS_fb')
#grid_LDOS_2diff_sg_zm_dps_pad_mV



grid_LDOS_rot['LDOS_pk_mV'] = (grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV * grid_LDOS_rot.LDOS_fb).astype(float)
grid_LDOS_rot
# extract the peak positions 
# -


