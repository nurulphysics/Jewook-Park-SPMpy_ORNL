# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
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
# > **SPMpy** is a Python package to analyze scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques and utilizes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools in the [scientific Python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
#
# >  **SPMpy** is an open-source project. (Github: https://github.com/jewook-park/SPMpy_ORNL )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 

# + [markdown] jp-MarkdownHeadingCollapsed=true
# # Experimental Conditions 
#
# * Data Acquistion date : 2023 0506
#
# ## **Sample**
# * <font color= White, font size="5" > $FeTe_{0.55}Se_{0.45}$ (new batch) </font> 
#     * UHV cleaving, Room temp
# ## **Tip**
# * PtIr (normal metal) tip
#
# ## **Measurement temp**
# * LHeT (4.2 K)
#
# ## Magnetic field 0 T (Z)
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
grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[2])
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

##
# find neares I =0 bias_mV 
def Bias_mV_offset_avg_test(grid_3D):
    I_fb_avg_df = grid_3D.I_fb.mean (dim = ['X','Y']).to_dataframe().abs()
    if I_fb_avg_df.I_fb.idxmin() == 0:
        print ('Bias_mV is set to I = 0')
    else:
        print ('need to adjust Bias_mV Zero')
        grid_3D = grid_3D.assign_coords(bias_mV= (  grid_3D.bias_mV - I_fb_avg_df.I_fb.idxmin()  ))
        print ('Bias_mV Zero shifted : '+ str( round(I_fb_avg_df.I_fb.idxmin(),2)  ))
    return grid_3D


grid_3D = Bias_mV_offset_avg_test(grid_3D)

grid_topo

grid_3D


# ### 1.2.3. Unit calculation (LDOS_fb)
#     * for semiconductor: CBM,VBM check. gap_map check
#     * add gap_maps to grid_2D

# +
def grid_3D_SCgap(xr_data,tolerance_I =  1E-11, tolerance_LIX = 1E-11, apply_SGfilter = True):
    '''
    gap definition need to be improved for Superconducting sample data 
    after Bias_mV_offset_avg_test 
    I_avg --> I_0 = bias_mV_0 
    
    output : I, dI/dV, LDOS_fb, SCgap_map,SCgap_pos, SCgap_neg
    find SCgap : based on plateau finding --> plateau map + ZBCP map 
    
    
    '''
    # get plateau area 
    # tolerance for I & LIX
    
    xr_data_prcssd = xr_data.copy(deep = True)
    print('Find plateau in I &LIX each points')
    if apply_SGfilter == True :
        print('import savgolFilter_xr in advance' )
        xr_data_sg = savgolFilter_xr(xr_data_prcssd, window_length = 21, polyorder = 3)

    else : 
        print ('without SavgolFilter_xr, check outliers')
        xr_data_sg = xr_data_prcssd

    if 'I_fb' in xr_data.data_vars : 
        I_fb_plateau = abs(xr_data_sg['I_fb']) <= tolerance_I 
    else :
        I_fb_plateau = abs(xr_data_sg['LIX_fb']) <= tolerance_LIx  
        print ('No I_fb channel, use LIX instead')

    if 'LIX_unit_calc' in xr_data.data_vars : 
        LIX_fb_plateau = abs(xr_data_sg['LIX_unit_calc']) <= tolerance_LIX 
    else: 
        LIX_fb_plateau = abs(xr_data_sg['LIX_fb']) <= tolerance_LIX 
        print ('No LIX_unit_calc channel, use LIX instead')

    I_LIX_plateau = I_fb_plateau*LIX_fb_plateau
    # pixels in X,Y, bias_mV  intersection of plateau
  

    xr_data_sg['I_LIX_plateau']=I_LIX_plateau
    
    # out figure
    gap_pos0_I = xr_data.where(I_LIX_plateau).I_fb.idxmax(dim='bias_mV')
    gap_neg0_I = xr_data.where(I_LIX_plateau).I_fb.idxmin(dim='bias_mV')
    gap_mapI = gap_pos0_I-gap_neg0_I
 
    xr_data_prcssd['gap_pos0_I'] = gap_pos0_I
    xr_data_prcssd['gap_neg0_I'] = gap_neg0_I
    xr_data_prcssd['gap_mapI'] = gap_mapI
    #########
    
    
           
    xr_data_prcssd['dIdV'] = xr_data.differentiate(coord = 'bias_mV').I_fb
    # numerically calculated dI/dV from I_fb
    LIX_ratio = xr_data_prcssd.dIdV / xr_data.LIX_fb
       
    xr_data_prcssd['LIX_unit_calc'] = np.abs( LIX_ratio.mean())*xr_data.LIX_fb
    # LIX unit calibration 
    # pA unit : lock-in result 
    # LIX_unit_calc : calibrated as [A/V] unit for dI/dV
    
    
    
    gap_pos0_LIX = xr_data_prcssd.where(I_LIX_plateau).LIX_unit_calc.idxmax(dim='bias_mV')
    gap_neg0_LIX = xr_data_prcssd.where(I_LIX_plateau).LIX_unit_calc.idxmin(dim='bias_mV')
      
    xr_data_prcssd['gap_pos0_LIX'] = gap_pos0_LIX
    xr_data_prcssd['gap_neg0_LIX'] = gap_neg0_LIX
    
    #######################################################
    # filtering gap_pos0_LIX <--- filtering 'neg' values 
    # filtering gap_neg0_LIX <--- filtering 'pos' values 
    #########
    gap_neg0_LIX_neg = xr_data_prcssd.gap_neg0_LIX.where(xr_data_prcssd.gap_neg0_LIX>0).isnull()
    # True ==>   neg == neg
    gap_pos0_LIX_pos = xr_data_prcssd.gap_pos0_LIX.where(xr_data_prcssd.gap_pos0_LIX<0).isnull()
    # True ==>  pos == pos
    
    plateau_map_LIX = gap_neg0_LIX_neg & gap_pos0_LIX_pos 
    # select plateau that contains ZeroBias  ---> plateau_map (zero LIX at zero bias) 
    
    plateau_pos0_LIX = xr_data_prcssd.where(I_LIX_plateau).where(plateau_map_LIX).LIX_unit_calc.idxmax(dim='bias_mV')
    plateau_neg0_LIX = xr_data_prcssd.where(I_LIX_plateau).where(plateau_map_LIX).LIX_unit_calc.idxmin(dim='bias_mV')
    # LIX plateau area min & max 
    #xr_data_prcssd['plateau_pos0_LIX'] = plateau_pos0_LIX
    #xr_data_prcssd['plateau_neg0_LIX'] = plateau_neg0_LIX
    
    xr_data_prcssd['plateau_size_map_LIX'] = plateau_pos0_LIX - plateau_neg0_LIX
    # plateau_size_map_LIX
    xr_data_prcssd['zerobiasconductance'] = xr_data_prcssd.where(~I_LIX_plateau).LIX_unit_calc.sel(bias_mV=0, method = 'nearest')
    # non zero LIX area zerobias conductance map 
    
    #gap_map_LIX = gap_pos0_LIX.where(grid_3D_gap.gap_neg0_LIX>0) - gap_neg0_LIX.where(grid_3D_gap.gap_neg0_LIX<0)
    
    ###############################################
    # in case of  LIX offset (due to phase mismatching?) 
    """
    # LIX_fb values less than LIX_min_A => zero value 
    # LIX_0_pA = LIX_0_pA
    LIX_0_AV  =  LIX_0_pA * LIX_ratio.mean()
    # calibrated LIX resolution limit
    gap_mask_LIX  = np.abs(grid_3D.LIX_unit_calc) < LIX_0_AV
    # gap_mask_LIX  = np.abs(grid_3D.LIX_fb) > LIX_0_pA
    # because of the same coefficient ('LIX_ratio.mean()')
    # range for CBM &VBM is not different between  LIX_unit_calc & LIX_fb
    # 3D mask 

    LIX_unit_calc_offst = grid_3D.dIdV.where(gap_mask_I).mean()- grid_3D['LIX_unit_calc'].where(gap_mask_I).mean()
    # possible LIX offset adjust (based on dI/dV calc value)
    grid_3D_prcssd['LDOS_fb'] = grid_3D.LIX_unit_calc + LIX_unit_calc_offst
    # assign dI/dV value at I=0  as a reference offset 
    # grid_3D['LDOS_fb'] is calibrated dIdV with correct unit ([A/V]) for LDOS 
    # LDOS_fb is proportional to the real LDOS
    # here we dont consider the matrix element for
    """
    
    #xr_data_prcssd = xr_data_prcssd.drop('gap_pos0_LIX')
    #xr_data_prcssd = xr_data_prcssd.drop('gap_neg0_LIX')
    
    xr_data_prcssd.attrs['I[A]_limit'] = tolerance_I
    xr_data_prcssd.attrs['LDOS[A/V]_limit'] = tolerance_LIX
    xr_data_prcssd['LDOS_fb'] = xr_data_prcssd['LIX_unit_calc']
    # meaningless redundant channel name. 
    # save the LDOS_fb for other functions. 
    
    return xr_data_prcssd

#test
#grid_3D_gap = grid_3D_Gap(grid_3D)
#grid_3D_gap
# +
grid_3D_gap =  grid_3D_SCgap(grid_3D,tolerance_I = 1E-12, tolerance_LIX = 5E-13, apply_SGfilter = True)
grid_3D_gap

grid_2D = grid_topo.copy() # rename 2D xr data

grid_LDOS = grid_3D_gap[['LDOS_fb' ]]
grid_LDOS

# -

grid_3D_gap

grid_3D_gap.gap_mapI.plot()

# +
#grid_3D_gap.gap_mapI.plot()

grid_3D_gap.plateau_size_map_LIX.plot()

#grid_3D_gap.zerobiasconductance.plot()

plt.show()
# -

# ### 1.4 Topography view 

# +
grid_topo =  plane_fit_x_xr(plane_fit_y_xr(grid_topo))
grid_topo

#isns.imshow(plane_fit_y_xr(grid_topo).where(grid_topo.Y < 0.7E-9, drop=True).topography)

#grid_topo = grid_topo.drop('gap_map_I').drop('gap_map_LIX')

isns.imshow(grid_topo.topography, cmap ='copper', robust = True)
plt.show()


# -


# ### correlation of topography check 

def drift_compensation_y_topo_crrltn (xr_data_topo, y_sub_n=5, drift_interpl_method='nearest'): 
    y_N = len (xr_data_topo.Y)
    y_sub_n = y_sub_n
    #y_j = 0 
    offset = np.array([0, y_N//2])
    # use for loop 
    print ('only for topo, 2D data, apply to 3D data & other channels later ')
    for y_j  in range (len (xr_data_topo.Y)//y_sub_n - 1) :
        y_N = len (xr_data_topo.Y)
        #print (y_j)

        Y_sub_n0 = y_j*y_sub_n * xr_data_topo.Y_spacing
        Y_sub_n1 = (y_j+1)*y_sub_n * xr_data_topo.Y_spacing
        Y_sub_n2 = (y_j+2)*y_sub_n * xr_data_topo.Y_spacing
        #print (Y_sub_n0, Y_sub_n1, Y_sub_n2)
        # check Y drift comparision area 
        # use y_sub_n = 5 ==> 0-5, 6-10, 10-5, ... 
        line0 = xr_data_topo.where(xr_data_topo.Y >= Y_sub_n0, drop = True).where (xr_data_topo.Y < Y_sub_n1, drop = True ).topography
        line1 = xr_data_topo.where(xr_data_topo.Y >=  Y_sub_n1, drop = True).where (xr_data_topo.Y <  Y_sub_n2, drop = True ).topography
        # select two region for correlation search 
        corrl_line0_line1 = sp.signal.correlate2d(line0.values, line1.values, mode = 'same')#  use mode = same area to use the line0 X& Y value
        # search for the correlation. if correlation is not center --> drift. 
        # but.. there will be an step edge (horizontal), or atomic lattice --> y_sub_n << atomic lattice 
        ind_max = np.array (np.unravel_index(np.argmax(corrl_line0_line1, axis=None), corrl_line0_line1.shape)) # find max point 
        # find argmax index point
        #print (ind_max)
        offset = np.vstack ([offset, ind_max])
    
    offset_0 = offset[: , -1] -  y_N//2
    # check offset from center 
    #offset_accumulation  = [ offset_0[:n+1].sum()  for n in range (len(offset_0)) ]
    
    offset_accumulation  = np.array ( [ offset_0[:n].sum()  
                                       for n in range (len(offset_0)+1) ])*xr_data_topo.Y_spacing 
    # offset is from between two region.. get an accumlated offset. for whole Y axis. 
    offset_accumulation_df =pd.DataFrame (
        np.vstack ([ np.array ([ y_j *y_sub_n *xr_data_topo.Y_spacing  
                                for y_j in range(len (xr_data_topo.Y)//y_sub_n+1) ]), 
                    offset_accumulation]).T, columns  =['Y','offset_X'])
    offset_accumulation_xr  = offset_accumulation_df.set_index('Y').to_xarray()
    offset_accumulation_xr_intrpl = offset_accumulation_xr.offset_X.interp(Y = xr_data_topo.Y.values,  method=drift_interpl_method)
    # accumluted offset--> covert to df , xr, 
    # accumnulated offset to compensate in X 
    # use interpolation along Y --> point offset calc ==> apply to all y points. 

    # for each lines, adjust value after offset compensated  ==> interpolated again. 
    xr_data_topo_offset = xr_data_topo.copy(deep= True)
    # dont forget deep copy... 
    
    for y_j, y  in enumerate (xr_data_topo.Y):
        new_x_i =  xr_data_topo.isel (Y=y_j).X - offset_accumulation_xr_intrpl.isel(Y=y_j)
        # for each y axis. shift X position 
        xr_data_topo_offset_y_j = xr_data_topo_offset.isel (Y=y_j).assign_coords({"X": new_x_i}) 
        # assign_coord as a new calibrated offset-X coords
        xr_data_topo_offset_y_j_intp = xr_data_topo_offset_y_j.interp(X=xr_data_topo.X)
        # using original X points, interpolated offset- topo --> set new topo value to original X position 
        xr_data_topo_offset.topography[dict(Y = y_j)] =  xr_data_topo_offset_y_j_intp.topography
        #grid_topo_offset.isel(Y=y_j).topography.values = grid_topo_offest_y_j_intp.topography
        # use [dict()] for assign values , instead of isel() 
        # isel is not working... follow the instruction manual in web.!
        
        # in order not to loose the data point shift from X range ==> adjust interpolatino 
        
    fig,axs = plt.subplots(ncols = 2, figsize = (6,3))
    xr_data_topo.topography.plot(ax =axs[0])
    xr_data_topo_offset.topography.plot(ax =axs[1])
    plt.show()
    return xr_data_topo_offset


grid_topo_drift_compensated = drift_compensation_y_topo_crrltn(grid_topo, y_sub_n=5, drift_interpl_method='nearest')

grid_topo_drift_compensated.topography.plot()

### FFT check. 
grid_LDOS_fft = twoD_FFT_xr(grid_LDOS)
#xrdata_fft_plot_p6r6

grid_LDOS_fft_log = np.log(grid_LDOS_fft)
grid_LDOS_fft_log.LDOS_fb_fft.sel(freq_bias_mV = 2, method = "nearest").plot(robust = True)


### Xr rotation function 
# rotate the XY plan in xr data 
def rotate_3D_xr_fft (xrdata_fft, rotation_angle): 
    # padding first 
    for ch_i,ch_name in enumerate (xrdata_fft):
        if ch_i == 0:  # use only the first channel to calculate a padding size 
            padding_shape = skimage.transform.rotate(xrdata_fft[ch_name].values.astype('float64'),
                                                     rotation_angle,
                                                     resize = True).shape[:2]
            # After rotation, still 3D shape ->  [:2]
            
            padding_xy = (np.array( padding_shape)-np.array(xrdata_fft[ch_name].shape[:2]) +1)/2
            padding_xy = padding_xy.astype(int)
    xrdata_pad = xrdata_fft.pad(X=(padding_xy[0],padding_xy[0]), 
                            Y =(padding_xy[1],padding_xy[1]),
                            mode='constant',
                            cval = xrdata_fft.min())
    if np.array(xrdata_pad[ch_name]).shape[:2] != padding_shape:
        # in case of xrdata_pad shape is +1 larger than real padding_shape
        # index 다루는 법  (X)
        x_spacing = np.diff(xrdata_fft.freq_X).mean()
        y_spacing = np.diff(xrdata_fft.freq_Y).mean()
        xrdata_fft.freq_X[0]
        xrdata_fft.freq_Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata_fft.freq_X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata_fft.freq_Y.shape[0])

        x_pad_arr =  np.linspace(-1*padding_xy[0]*x_spacing, x_spacing*x_pad_dim,x_pad_dim+1)
        y_pad_arr =  np.linspace(-1*padding_xy[1]*y_spacing, y_spacing*y_pad_dim,y_pad_dim+1)

        # 0 에서 전체 크기 만큼 padding 한결과를 array 만들고 offset 은 pad_x 만큼 
        x_pad_arr.shape
        y_pad_arr.shape
        xrdata_pad = xrdata_pad.assign_coords( {"X" :  x_pad_arr}).assign_coords({"Y" :  y_pad_arr})
        xrdata_rot = xrdata_pad.sel(X = xrdata_pad.X[:-1].values, Y = xrdata_pad.Y[:-1].values)
        print ('padding size != rot_size')
    else : # np.array(xrdata_pad[ch_name]).shape == padding_shape 
            # in case of xrdata_pad shape is +1 larger than real padding_shape

        # index 다루는 법  (X)
        x_spacing = np.diff(xrdata_fft.freq_X).mean()
        y_spacing = np.diff(xrdata_fft.freq_Y).mean()
        xrdata_fft.freq_X[0]
        xrdata_fft.freq_Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata_fft.freq_X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata_fft.freq_Y.shape[0])

        x_pad_arr =  np.linspace(-1*padding_xy[0]*x_spacing, x_spacing*x_pad_dim,x_pad_dim)
        y_pad_arr =  np.linspace(-1*padding_xy[1]*y_spacing, y_spacing*y_pad_dim,y_pad_dim)

        # 0 에서 전체 크기 만큼 padding 한결과를 array 만들고 offset 은 pad_x 만큼 
        x_pad_arr.shape
        y_pad_arr.shape
        xrdata_pad = xrdata_pad.assign_coords( {"X" :  x_pad_arr}).assign_coords({"Y" :  y_pad_arr})
        xrdata_rot = xrdata_pad.copy()      
        print ('padding size == rot_size')
    # call 1 channel
        # use the list_comprehension for bias_mV range
        # list comprehension is more faster
        # after rotation, resize = False! , or replacement size error! 
        # replace the channel(padded) 3D data as a new 3D (rotated )data set 

    for ch in xrdata_pad:
        xrdata_rot[ch].values = skimage.transform.rotate(xrdata_rot[ch].values.astype('float64'),
                                                         rotation_angle,
                                                         cval =xrdata_pad[ch].to_numpy().min(),
                                                         resize = False)
    return xrdata_rot
# ### average X or Y direction jof Grid_3D dataset 
# * use xr_data (3D)
# * average_in = 'X' or 'Y'
# * ch_l_name = channel name for line profile  
# * ch_l_name = channel name for line profile  

# +
grid_LDOS_fft_rot  = rotate_3D_xr_fft(grid_LDOS_fft, rotation_angle=47)
#grid_LDOS_fft_rot

grid_LDOS_fft_rot.LDOS_fb_fft.sel(freq_bias_mV = 2, method = "nearest").plot(robust = True)
# -

np.log(grid_LDOS_fft_rot.LDOS_fb_fft.sel(freq_Y = 0, method = "nearest").T).plot(robust = True)

# +
grid_LDOS_fft_rot  = rotate_3D_xr_fft(grid_LDOS_fft, rotation_angle=2)
#grid_LDOS_fft_rot

grid_LDOS_fft_rot.LDOS_fb_fft.sel(freq_bias_mV = 2, method = "nearest").plot(robust = True)
# -

np.log(grid_LDOS_fft_rot.LDOS_fb_fft.sel(freq_Y = 0, method = "nearest").T).plot(robust = True)

# +
grid_LDOS_fft_rot  = rotate_3D_xr_fft(grid_LDOS_fft, rotation_angle=0)
#grid_LDOS_fft_rot

grid_LDOS_fft_rot.LDOS_fb_fft.sel(freq_bias_mV = 2, method = "nearest").plot(robust = True)

# +
import xarray as xr
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

# Load the image data in xarray format
data = grid_LDOS_fft_log

# Extract the 2D image data from the xarray dataset
image = data['LDOS_fb_fft'].isel(freq_bias_mV = 0).values

# Rotate the image by 30 degrees
rotated_image = rotate(image, angle=30)

# Plot the original and rotated images side by side
fig, axs = plt.subplots(1, 2)
axs[0].imshow(image)
axs[0].set_title('Original Image')
axs[1].imshow(rotated_image)
axs[1].set_title('Rotated Image')
plt.show()


# +

# Rotate each 2D image in the stacked dataset by 30 degrees
rotated_data = xr.Dataset()
for mV in data['freq_bias_mV']:
    image = data.sel(freq_bias_mV=mV)['LDOS_fb_fft'].values
    rotated_image = rotate(image, angle=30)
    rotated_data = xr.concat([rotated_data, xr.DataArray(rotated_image)], dim='freq_bias_mV')
    
    

# +
fft_0 = np.log(grid_LDOS_fft.LDOS_fb_fft.sel(freq_bias_mV = 0, method = "nearest"))

isns.imshow(fft_0, robust= True)
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
grid_LDOS_1deriv_sg = savgolFilter_xr(grid_LDOS_1deriv, window_length = 31, polyorder = 3)
grid_LDOS_2deriv = grid_LDOS_1deriv_sg.differentiate('bias_mV')
grid_LDOS_2deriv_sg =  savgolFilter_xr(grid_LDOS_2deriv, window_length = 31, polyorder = 3)
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

hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb',frame_width=400)#.opts(clim = (0,2E-10))
#hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb').opts(clim = (0,1.5E-10)) # adjust cbar limit

# ####  1.5.2. Y or X slicing 

#hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'Y')#.opts(clim=(0, 8E-10)) #
#hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'Y').opts(clim=(0, 4E-10)) #
hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'X')#.opts(clim=(0, 1E-10)) # check low intensity area
#hv_XY_slicing(grid_3D,slicing= 'Y').opts(clim=(0, 1E-11))


# +
# set tolerance for I_fb * LIX_fb
#tolerance_I, tolerance_LIX = 1E-11, 0.05E-12


###############
# rotation #
#################
grid_LDOS_rot = rotate_3D_xr(grid_LDOS, rotation_angle= 11)
## or not
grid_LDOS_rot = rotate_3D_xr(grid_LDOS, rotation_angle= 0)

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


bias_mV_slices= [ -5,-4, -3, -2, -1, 0, 1, 2, 3, 4,5][::-1]
#bias_mV_slices= [ -2.4, -2, -1, 0, 1, 2, 2.4 ][::-1]

#bias_mV_slices= [-1.4, -1.2, -1, -0.8, -0.6, 0, 0.6, 0.8,1,1.2,1.4][::-1]
#bias_mV_slices= [-1.0, -0.8, -0.6,-0.4,-0.2, 0,0.2,0.4, 0.6, 0.8,1][::-1]

bias_mV_slices_v = grid_LDOS.bias_mV.sel(bias_mV = bias_mV_slices, method = "nearest").values#.round(2)
bias_mV_slices_v
# -

grid_LDOS


# +
# value --> use Where ! 


g = isns.ImageGrid(grid_LDOS.sel(bias_mV = bias_mV_slices, method = "nearest").LDOS_fb.values, 
                   cbar=False, height=2, col_wrap=4,  cmap="bwr", robust = True)

col_wrap=4
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

# +
#grid_LDOS_th= th_otsu_roi_label_2D_xr(equalize_hist_xr(grid_LDOS), bias_mV_th = 0,  threshold_flip=False)
# use Otsu 

#grid_LDOS_th= th_multiotsu_roi_label_2D_xr(grid_LDOS, window_length=51, polyorder=3), bias_mV_th = 0.5, multiclasses = 5)
# in case of multiotsu

grid_LDOS_th= th_mean_roi_label_2D_xr(grid_LDOS.rolling(X=4, Y=2,min_periods=2,center= True).mean(),
                                      bias_mV_th = 0,threshold_flip=False)
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

LDOS_fb_0_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label ==0 ).mean(["X","Y"]).to_dataframe()
LDOS_fb_1_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label !=0 ).mean(["X","Y"]).to_dataframe()
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
#grid_LDOS_rot  = grid_LDOS

grid_LDOS_rot = rotate_3D_xr(grid_LDOS,rotation_angle=0)
# -


grid_LDOS_sg= savgolFilter_xr(grid_LDOS_rot, window_length=21, polyorder=3)

# +
##################################
# plot Grid_LDOS  & select BBox
#####################################

import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

xr_data = grid_LDOS_sg
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


def hv_bbox_avg_2 (xr_data, bound_box , ch = 'LIX_fb' ,slicing_bias_mV = 0.5):
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
                            ncols = 1,
                            figsize = (5,5))
    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs,robust = True)
    """
    fig,axs = plt.subplots (nrows = 1,
                            ncols = 3,
                            figsize = (4,4))
    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[0],
                robust = True)
    """

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
    axs.add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                               Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                               edgecolor = 'pink',
                               fill=False,
                               lw=2,
                               alpha=0.5))
    """
     axs[0].add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                               Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                               edgecolor = 'pink',
                               fill=False,
                               lw=2,
                               alpha=0.5))"""
    
    
    
    """
    isns.imshow(xr_data_bbox[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                ax =  axs[1],
                robust = True)
    sns.lineplot(x = "bias_mV",
                 y = ch, 
                 data = xr_data_bbox.to_dataframe(),
                 ax = axs[2])
    axs[1].remove()
    axs[2].remove()"""
    #plt.savefig('grid011_bbox)p.png')
    
    isns.imshow(xr_data_bbox[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                robust = True)
    plt.show()
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 
# -
grid_LDOS_bbox,grid_LDOS_bbox_fig = hv_bbox_avg_2(grid_LDOS_sg, ch ='LDOS_fb',slicing_bias_mV=-0 , bound_box = bound_box)



def  grid_lineNpks_offset(xr_data_l_pks, 
                          ch_l_name = 'LIX_unit_calc',
                          plot_y_offset= 2E-11, 
                          peak_LIX_min = 1E-13, 
                          fig_size = (6,8), 
                          legend_title = None):
    # add peak point one-by-one (no palett func in sns)
    #  after find peak & padding
    # use choose the channel to offset-plot 
    # use the plot_y_offset to adjust the offset values 
    ch_l_name = ch_l_name
    ch_l_pk_name = ch_l_name +'_peaks_pad'
    line_direction = xr_data_l_pks.line_direction
    plot_y_offset  =  plot_y_offset
    
    sns_color_palette = "rocket"
    #color map for fig
    
    #xr_data_l_pks
    ### prepare XR dataframe for line spectroscopy plot 
    xr_data_l_pks_ch_slct = xr_data_l_pks[[ch_l_name,ch_l_pk_name]]
    # choose the 2 channels from 2nd derivative (to maintain the coords info) 


    #line_direction check again 
    
    if xr_data_l_pks.line_direction == 'Y': 
        spacing = xr_data_l_pks_ch_slct.Y_spacing
    elif xr_data_l_pks.line_direction == 'X': 
        spacing = xr_data_l_pks_ch_slct.X_spacing
    else : 
        print('check direction & X or Y spacing for offset') 

    xr_data_l_pks_ch_slct['offset'] = (xr_data_l_pks_ch_slct[line_direction] - xr_data_l_pks_ch_slct[line_direction].min())/spacing
    # prepare offset index channnel 
    print (' plot_y_offset  to adjust line-by-line spacing')

    xr_data_l_pks_ch_slct[ch_l_name+'_offset'] = xr_data_l_pks_ch_slct[ch_l_name] + plot_y_offset * xr_data_l_pks_ch_slct['offset']
    # offset the curve b
    print (xr_data_l_pks_ch_slct)
    

    ch_l_name_df_list = [] 
    ch_l_name_pks_df_list = []
    # prepare empty list to append dataframes in the for - loop (y_i or x_i)

    #line_direction check again 
    #########################
    # line_diection check
    if xr_data_l_pks_ch_slct.line_direction == 'Y': 
        lines  = xr_data_l_pks_ch_slct.Y

        for y_i, y_points in enumerate (lines):

            # set min peak height (LIX amplitude =  resolution limit)

            y_i_pks  = xr_data_l_pks_ch_slct[ch_l_pk_name].isel(Y = y_i).dropna(dim='peaks').astype('int32')
            # at (i_th )Y position, select peak index for bias_mV
            real_pks_mask = (xr_data_l_pks_ch_slct.isel(Y = y_i, bias_mV = y_i_pks.values)[ch_l_name] > peak_LIX_min).values
            # prepare a 'temp' mask for each Y position 
            y_i_pks_slct =  y_i_pks.where(real_pks_mask).dropna(dim='peaks').astype('int32')
            # y_i_pks_slct with mask selection  

            ch_l_name_y_i_df = xr_data_l_pks_ch_slct[ch_l_name+'_offset'].isel(Y = y_i).to_dataframe()
            # LIX_offset  at Y_i position 
            ch_l_name_df_list.append(ch_l_name_y_i_df)
            
            ch_l_name_y_i_pks_df = xr_data_l_pks_ch_slct.isel(Y = y_i, bias_mV = y_i_pks_slct.values)[ch_l_name+'_offset'].to_dataframe()
            # selected peaks with offest Y 
            ch_l_name_pks_df_list.append(ch_l_name_y_i_pks_df)
            
            # data at selected Y, & peak position, LIX_offset
            
    #########################
    # line_diection check

    elif xr_data_l_pks_ch_slct.line_direction == 'X': 
        lines = xr_data_l_pks_ch_slct.X

        for x_i, x_points in enumerate (lines):

            # set min peak height (LIX amplitude =  resolution limit)

            x_i_pks  = xr_data_l_pks_ch_slct[ch_l_pk_name].isel(X = x_i).dropna(dim='peaks').astype('int32')
            # at (i_th )X position, select peak index for bias_mV
            real_pks_mask = (xr_data_l_pks_ch_slct.isel(X = x_i, bias_mV = x_i_pks.values)[ch_l_name] > peak_LIX_min).values
            # prepare a 'temp' mask for each X position 
            x_i_pks_slct =  x_i_pks.where(real_pks_mask).dropna(dim='peaks').astype('int32')
            # x_i_pks_slct with mask selection  

            ch_l_name_x_i_df = xr_data_l_pks_ch_slct[ch_l_name+'_offset'].isel(X = x_i).to_dataframe()
            # LIX_offset  at X_i position 
            ch_l_name_df_list.append(ch_l_name_x_i_df)
            ch_l_name_x_i_pks_df = xr_data_l_pks_ch_slct.isel(X = x_i, bias_mV = x_i_pks_slct.values)[ch_l_name+'_offset'].to_dataframe()
            ch_l_name_pks_df_list.append(ch_l_name_x_i_pks_df)
            
            # selected peaks with offest X 
            
    else : 
        print('check direction & X or Y spacing for offset') 
    
    ch_l_name_df = pd.concat(ch_l_name_df_list).reset_index()
    ch_l_name_pks_df = pd.concat(ch_l_name_pks_df_list).reset_index()
    
    fig,ax = plt.subplots(figsize = fig_size)

    sns.lineplot(data = ch_l_name_df,
                         x ='bias_mV', 
                         y = ch_l_name+'_offset',
                         palette = "rocket",
                         hue = xr_data_l_pks.line_direction,
                         ax = ax,legend='full')

    sns.scatterplot(data = ch_l_name_pks_df,
                            x ='bias_mV',
                            y = ch_l_name+'_offset',
                            palette ="rocket",
                            #marker = "|",
                            s = 20,
                            hue = xr_data_l_pks.line_direction,
                            ax = ax,legend='full')
    # legend control!( cut the handles 1/2)
    ax.set_xlabel('Bias (mV)')   
    #ax.set_ylabel(ch_l_name+'_offset')   
    ax.set_ylabel('LDOS')   
    handles0, labels0 = ax.get_legend_handles_labels()
    handles1 = handles0[:int(len(handles0)//2)]
    labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
    handles2 = handles1[::5][::-1]
    labels2 = labels1[::5][::-1]
    # convert the line length as nm
    print(labels2)
    ax.legend(handles2,   labels2, title = legend_title)
    # use the half of legends (line + scatter) --> use lines only
    #plt.show()
    return xr_data_l_pks_ch_slct, ch_l_name_df, ch_l_name_pks_df, fig

# +
# grid_LDOS_bbox

average_in= 'Y'

grid_LDOS_bbox_pk = grid3D_line_avg_pks(grid_LDOS_bbox) 
grid_LDOS_bbox_pk  = grid3D_line_avg_pks( grid_LDOS_bbox ,
                                         ch_l_name ='LDOS_fb',
                                         average_in= average_in,
                                         distance = 1, 
                                         width= 4,
                                         threshold = 0.8E-12, 
                                         padding_value= 0,
                                         prominence= 0.8E-12
                                        ) 
grid_LDOS_bbox_pk

grid_LDOS_bbox_pk_slct, grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df, fig = grid_lineNpks_offset(
    grid_LDOS_bbox_pk,
    ch_l_name ='LDOS_fb',
    plot_y_offset= 0.4E-11,
    peak_LIX_min = 1E-12,
    legend_title = "Y (nm)")

plt.show()

# +
##############
# Fig plot again (remove 0th peak points) 

#grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df

##########
grid_LDOS_bbox_pk_df=  grid_LDOS_bbox_pk_df[grid_LDOS_bbox_pk_df.bias_mV<=8]
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

sns.scatterplot(data = grid_LDOS_bbox_pk_df,
                        x ='bias_mV',
                        y = ch_l_name+'_offset',
                        palette ="rocket",
                        hue = xr_data_l_pks.line_direction,
                        ax = ax,legend='full',
                           s = 20)
# legend control!( cut the handles 1/2)
ax.set_xlabel('Bias (mV)')   
#ax.set_ylabel(ch_l_name+'_offset')   
ax.set_ylabel('LDOS')   
ax.set_xlim(-7.5,7.5)
#ax.set_ylim(-1.0E-9,6.0E-9)

ax.vlines(x = 0, ymin=ax.get_ylim()[0],  ymax=ax.get_ylim()[1], linestyles='dashed',alpha = 0.5, color= 'k')

handles0, labels0 = ax.get_legend_handles_labels()
handles1 = handles0[:int(len(handles0)//2)]
labels1 = [ str(round(float(label)*1E9,2)) for label in labels0[:int(len(labels0)//2)] ] 
handles2 = handles1[::5][::-1]
labels2 = labels1[::5][::-1]
# convert the line length as nm
print(labels2)
ax.legend(handles2,   labels2, title = legend_title,loc='upper right', bbox_to_anchor=(1.3, 0.8))
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


grid_LDOS_sg

isns.imshow(grid_LDOS_sg.LDOS_fb.sel(bias_mV = 0, method="nearest" ),robust = True)
plt.show()

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
