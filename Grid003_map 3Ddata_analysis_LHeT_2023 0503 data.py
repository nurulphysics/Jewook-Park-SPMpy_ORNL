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
# > **SPMpy** is a python package to analysis scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques, and utilzes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools available in the [scientific python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
#
# >  **SPMpy** is an open-source project. (Github: https://github.com/jewook-park/SPMpy_ORNL )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 

# # Experimental Conditions 
#
# ## **Sample** :<font color= White, font size="5" > $FeTe_{0.55}Se_{0.45}$ (new) </font> 
#     * Cleaving: @ UHV Loadlock chamber, Room temp.
# ## **Tip: PtIr (from Unisoku)**
# ## Measurement temp: LHeT (4.8K)
#

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
    # !pip install xarray
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
grid_xr = grid_line2xr(files_df[files_df.type=='3ds'].file_name.iloc[2])
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

# ### 1.2.3. Unit calculation (LDOS_fb)
#     * for semiconductor: CBM,VBM check. gap_map check
#     * add gap_maps to grid_2D

grid_topo

# +
grid_3D_gap =  grid_3D_Gap(grid_3D)
grid_3D_gap

grid_2D = grid_topo.copy() # rename 2D xr data

grid_2D['gap_map_I'] = grid_3D_gap.gap_size_I
grid_2D['gap_map_LIX'] = grid_3D_gap.gap_size_LIX # add gap map to topo data

grid_LDOS = grid_3D_gap[['LDOS_fb' ]]
grid_LDOS
# -

# ### 1.4 Topography view 

grid_topo =  plane_fit_y_xr(grid_topo)
grid_topo


# in case of line STS
'''
# sns.lineplot(x  ='X', y = 'topography', data = plane_fit_surface_xr(plane_fit_y_xr(grid_topo), order=2).topography.to_dataframe())

# show topography image

isns.set_image(origin =  "lower")
#isns.imshow(plane_fit_x_xr(plane_fit_y_xr(grid_topo)).topography, robust =  True, cmap= 'copper', perc = (2,98))

# image topo
# isns.imshow(plane_fit_surface_xr(plane_fit_y_xr(grid_topo), order=2).topography, robust =  True, cmap= 'copper', perc = (2,98))

################
# line topo 

fig,axs = plt.subplots(nrows = 2, figsize= (4,3))
isns.imshow(plane_fit_surface_xr(plane_fit_y_xr(grid_topo), order=2).topography, robust =  True, cmap= 'copper', perc = (2,98), ax= axs[0], despine =True, cbar = False)
sns.lineplot(x  ='X', y = 'topography', data = plane_fit_surface_xr(plane_fit_y_xr(grid_topo), order=2).topography.to_dataframe(), ax = axs[1])
plt.tight_layout()
plt.show()

'''

# ##  Grid area extract 
#
# ### grid 3D_LDOS
#
#
#

# +
#isns.imshow(plane_fit_y_xr(grid_topo).where(grid_topo.Y < 0.7E-9, drop=True).topography)

#grid_topo = grid_topo.drop('gap_map_I').drop('gap_map_LIX')

isns.imshow(grid_topo.topography, cmap ='copper')
plt.show()
# -

# ## 2.3 Numerical derivative 
#     * Derivative + SG smoothing
#
# ### 2.3.1. SG + 1stderiv + SG + 2nd deriv + SG

# ##### SG fitlering only 

grid_LDOS_sg = savgolFilter_xr(grid_LDOS, window_length = 51, polyorder = 3)

# #### numerical derivative check. later 

grid_LDOS_1deriv = grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1deriv_sg = savgolFilter_xr(grid_LDOS_1deriv, window_length = 51, polyorder = 3)
grid_LDOS_2deriv = grid_LDOS_1deriv_sg.differentiate('bias_mV')
grid_LDOS_2deriv_sg =  savgolFilter_xr(grid_LDOS_2deriv, window_length = 51, polyorder = 3)
grid_LDOS_2deriv_sg

grid_LDOS_2deriv_sg.isel(X=1).LDOS_fb.plot()


# ## Y direction drift check 
#
# * use correlation between lines 
#
# * select Y avg area 
#

# +
#crrlt2D_topo_LDOS_np_0 =sp.signal.correlate2d( grid_top_ref.values, grid_LDOS.LDOS_fb.isel(bias_mV = 0 ).values, mode='valid')

# +
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
                                       for n in range (len(offset_0)+1) ])*grid_topo.Y_spacing 
    # offset is from between two region.. get an accumlated offset. for whole Y axis. 
    offset_accumulation_df =pd.DataFrame (
        np.vstack ([ np.array ([ y_j *y_sub_n *grid_topo.Y_spacing  
                                for y_j in range(len (grid_topo.Y)//y_sub_n+1) ]), 
                    offset_accumulation]).T, columns  =['Y','offset_X'])
    offset_accumulation_xr  = offset_accumulation_df.set_index('Y').to_xarray()
    offset_accumulation_xr_intrpl = offset_accumulation_xr.offset_X.interp(Y = grid_topo.Y.values,  method=drift_interpl_method)
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
    fig,axs = plt.subplots(ncols = 2, figsize = (6,3))
    xr_data_topo.topography.plot(ax =axs[0])
    xr_data_topo_offset.topography.plot(ax =axs[1])
    plt.show()
    return xr_data_topo_offset



# +
grid_topo_test = plane_fit_y_xr(grid_xr[['topography']])


#grid_topo.topography.plot()
grid_topo_offset = drift_compensation_y_topo_crrltn(grid_topo_test, y_sub_n=3, drift_interpl_method= "nearest")
# -

fig,axs = plt.subplots(ncols = 2, figsize = (6,3))
grid_topo_test.topography.plot(ax =axs[0])
grid_topo_offset.topography.plot(ax =axs[1])

# ## find a correlation between topography height and LDOS line cut 
#

crrlt2D_topo_LDOS_np_valid = np.array (
    [sp.signal.correlate2d( grid_topo.topography.values, grid_LDOS.LDOS_fb.isel(bias_mV = bias_mV_i ).values, 
                           mode = 'valid')
     for bias_mV_i,bias_mV in enumerate  (grid_LDOS.bias_mV) ]).ravel()

crrlt2D_topo_LDOS = pd.DataFrame (crrlt2D_topo_LDOS_np_valid, columns  = ['correlation2D'], index  = grid_LDOS.bias_mV)

# +
#crrlt2D_topo_LDOS.correlation2D.to_numpy()

#sp.signal.find_peaks(crrlt2D_topo_LDOS)
crrltn_pk_idx = sp.signal.argrelextrema(crrlt2D_topo_LDOS.correlation2D.to_numpy(), np.greater, order = 9)
crrltn_dp_idx = sp.signal.argrelextrema(crrlt2D_topo_LDOS.correlation2D.to_numpy(), np.less, order = 9 )
# order: range.. 



# +
###############
# choose the bias_mV slice at peaks 

#crrltn_pk_idx[0]
# grid_LDOS.isel(bias_mV= crrltn_pk_idx[0])

# extract peak & dip positions 

crrlt2D_topo_LDOS_extrema = pd.concat ([crrlt2D_topo_LDOS.iloc[crrltn_pk_idx[0]],crrlt2D_topo_LDOS.iloc[crrltn_dp_idx[0]]],axis = 1)
crrlt2D_topo_LDOS_extrema.columns=['peaks','dips']
crrlt2D_topo_LDOS_extrema


fig, axes = plt.subplots (ncols =2 , figsize = (7,3))
axs = axes.ravel()
isns.imshow( grid_topo.topography, ax = axs[0])
sns.lineplot(crrlt2D_topo_LDOS, ax =axs[1])
sns.scatterplot(data = crrlt2D_topo_LDOS_extrema, ax= axs[1])

plt.show()


# +
g= isns.ImageGrid (grid_LDOS.isel(bias_mV= crrltn_pk_idx[0]).LDOS_fb.values, col_wrap =3, height =2) 

slicemV = grid_LDOS.bias_mV[crrltn_pk_idx[0]].values.round(2)

g.axes[0][0].set_title(str(slicemV[0])+' mV')
g.axes[0][1].set_title(str(slicemV[1])+' mV')
g.axes[0][2].set_title(str(slicemV[2])+' mV')
g.axes[1][0].set_title(str(slicemV[3])+' mV')
g.axes[1][1].set_title(str(slicemV[4])+' mV')
g.fig.suptitle('peak')
plt.tight_layout()
plt.show()



# +
g= isns.ImageGrid (grid_LDOS.isel(bias_mV= crrltn_dp_idx[0]).LDOS_fb.values, col_wrap =3, height = 2 ) 

slicemV = grid_LDOS.bias_mV[crrltn_dp_idx[0]].values.round(2)

g.axes[0][0].set_title(str(slicemV[0])+' mV')
g.axes[0][1].set_title(str(slicemV[1])+' mV')
g.axes[0][2].set_title(str(slicemV[2])+' mV')
g.axes[1][0].set_title(str(slicemV[3])+' mV')
g.axes[1][1].set_title(str(slicemV[4])+' mV')
g.axes[1][2].set_title(str(slicemV[5])+' mV')
g.fig.suptitle('dip')
plt.tight_layout()
plt.show()


# -

slicemV = grid_LDOS.bias_mV[crrltn_dp_idx[0]].values.round(2)
slicemV

# + [markdown] jp-MarkdownHeadingCollapsed=true
# ## how to switch the plot 90 deg 

# +
grid_LDOS_sg_crrlt  = grid_LDOS_sg.bias_mV.to_dataframe()
grid_LDOS_sg_crrlt['crrlt_w_topo'] = grid_line_LDOS_topo_crrlt

#sns.lineplot (grid_LDOS_sg_crrlt.crrlt_w_topo)

fig, axes = plt.subplots( nrows = 2, ncols =2,  figsize = (6,6))
axs = axes.ravel()

grid_LDOS_sg.isel(Y=0).LDOS_fb.T.plot(ax = axs[0])


# draw curve first & swapt x & y
crrlt_plot =  sns.lineplot (grid_LDOS_sg_crrlt.crrlt_w_topo, ax = axs[1])
crrlt_plot_x,crrlt_plot_y =crrlt_plot.lines[0].get_data()
crrlt_plot.clear()

# c = crrlt_plot.collections[0].get_paths()[0].vertices 
# create new plot on the axes, inverting x and y
# ax.fill_between(c[:,1], c[:,0], alpha=0.5)
#fill between case 

axs[1].plot(crrlt_plot_y,crrlt_plot_x)
axs[1].set_xlabel('correlation z-LDOS')    
axs[1].set_ylabel('bais (mV)')    



grid_topo.topography.plot(ax = axs[2])
axs[2].set_ylabel('z')        

axs[3].remove()

plt.tight_layout()

plt.show()
# -

# # set new area as a grid_LDOS & grid _topo

# +
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

hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb',frame_width=400).opts(clim = (0,1E-10))
#hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb').opts(clim = (0,1.5E-10)) # adjust cbar limit

# ####  1.5.2. Y or X slicing 

#hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'Y')#.opts(clim=(0, 1E-10)) 
hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'X').opts(clim=(0, 2E-10)) # check low intensity area
#hv_XY_slicing(grid_3D,slicing= 'Y').opts(clim=(0, 1E-11))


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
#dmap.opts(clim = (0,1E-11))*bbox_points
dmap.opts()*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box

bbox_2, _ = hv_bbox_avg(grid_LDOS, bound_box= bound_box, ch ='LDOS_fb',slicing_bias_mV = 0)

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

fig, axs = plt.subplots(ncols = 2, figsize = (6,3))
isns.imshow(plane_fit_y_xr(grid_topo).topography, cmap ='copper', ax = axs[0])
isns.imshow (grid_LDOS.LDOS_fb.sel(bias_mV = 3, method ='nearest'),ax = axs[1])
plt.tight_layout()
plt.show()


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



bias_mV_slices= [8, 6, 4,2, 0, 2, 4, 6, 8][::-1]

bias_mV_slices_v = grid_LDOS.bias_mV.sel(bias_mV = bias_mV_slices, method = "nearest").values.astype(int)

g = isns.ImageGrid(grid_LDOS.LDOS_fb.values, cbar=False, height=2, col_wrap=5, slices= bias_mV_slices , cmap="bwr", robust = True)

col_wrap=5
# set a col_wrap for suptitle 

for axes_i  in range( len(bias_mV_slices)):
    #print (int(axes_i/col_wrap),axes_i%col_wrap)  # axes number check 
    g.axes[int((axes_i)/col_wrap)][axes_i%col_wrap].set_title(str(bias_mV_slices_v[axes_i])+' mV')
plt.tight_layout()
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
          frame_width = 200,
          aspect = 'equal').relabel('XY plane slicing: ')



grid_channel_hv_image = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0))

grid_channel_hv_points = hv.Points(grid_channel_hv_image).opts(frame_width = 200,  
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

fig, axs = plt.subplots(ncols = 2, nrows = 1, figsize = (8,4))

grid_3D_slct_pts.I_fb.plot(ax = axs[0], robust = True) 

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
#grid_LDOS_th= th_otsu_roi_label_2D_xr(equalize_hist_xr(grid_LDOS), bias_mV_th = 0,  threshold_flip=False)
# use Otsu 

#grid_LDOS_th= th_multiotsu_roi_label_2D_xr(grid_LDOS, bias_mV_th = 0, multiclasses = 3)
# in case of multiotsu

grid_LDOS_th= th_mean_roi_label_2D_xr(grid_LDOS, bias_mV_th = 0,threshold_flip=False)
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
# -

fig, ax = plt.subplots(figsize = (4,3))
sns.lineplot (x = 'bias_mV', y= 'LDOS_fb', 
              data = grid_LDOS_th.LDOS_fb.where(grid_LDOS_th.LDOS_fb_th_label ==7 ).mean(['X','Y']).to_dataframe(),
              ax =ax, label = '4')
sns.lineplot (x = 'bias_mV', y= 'LDOS_fb', 
              data = grid_LDOS_th.LDOS_fb.where(grid_LDOS_th.LDOS_fb_th_label ==14 ).mean(['X','Y']).to_dataframe(),
              ax =ax, label = '0')
"""
sns.lineplot (x = 'bias_mV', y= 'LDOS_fb', 
              data = grid_LDOS_th.LDOS_fb.where(grid_LDOS_th.LDOS_fb_th_label ==16 ).mean(['X','Y']).to_dataframe(),
              ax =ax, label = '16')
sns.lineplot (x = 'bias_mV', y= 'LDOS_fb', 
              data = grid_LDOS_th.LDOS_fb.where(grid_LDOS_th.LDOS_fb_th_label ==17 ).mean(['X','Y']).to_dataframe(),
              ax =ax, label = '17')"""
plt.show()

# +
grid_LDOS_th.LDOS_fb_th.plot()
# grid_LDOS_th.LDOS_fb_th.isnull().plot()

plt.show()
# -

LDOS_fb_0_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label ==0 ).mean(["X","Y"]).to_dataframe()
LDOS_fb_1_df = grid_LDOS_th.LDOS_fb.where( grid_LDOS_th.LDOS_fb_th_label !=0 ).mean(["X","Y"]).to_dataframe()
LDOS_fb_0_1_df = pd.concat( [LDOS_fb_0_df,LDOS_fb_1_df], axis= 1)
LDOS_fb_0_1_df.columns = ['(Area0)','(Area1)']
LDOS_fb_0_1_df

# +
fig,ax = plt.subplots(ncols = 3, figsize=(9,3))
isns.imshow (grid_LDOS_th.LDOS_fb_th, ax = ax[0]) 
ax[0].set_title('Thresholds')
isns.imshow (grid_LDOS_th.LDOS_fb_th.isnull(), ax = ax[1]) 
ax[1].set_title('Area Selection 0 or 1')

sns.lineplot(LDOS_fb_0_1_df, ax = ax[2])
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
# -

grid_LDOS_sg= savgolFilter_xr(grid_LDOS, polyorder=5)

# +
##################################
# plot Grid_LDOS  & select BBox
#####################################

import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

xr_data = grid_LDOS_sg
ch = 'LDOS_fb'
frame_width = 300

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
#dmap.opts(clim = (0,1E-11))*bbox_points
dmap*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box


grid_LDOS_bbox,_ = hv_bbox_avg(grid_LDOS_sg, ch ='LDOS_fb',slicing_bias_mV=0.1 , bound_box = bound_box)

grid_LDOS_bbox_pk.where(grid_LDOS_bbox_pk.LDOS_fb_peaks_pad!=0)

# +
# grid_LDOS_bbox


grid_LDOS_bbox_pk = grid3D_line_avg_pks(grid_LDOS_bbox) 
grid_LDOS_bbox_pk  = grid3D_line_avg_pks( grid_LDOS_bbox ,
                                         ch_l_name ='LDOS_fb',
                                         average_in= 'Y',
                                         distance = 10, 
                                         width= 5,
                                         threshold = 1E-12, 
                                         padding_value= 0,prominence= 3E-11
                                        ) 
grid_LDOS_bbox_pk

grid_LDOS_bbox_pk_slct, grid_LDOS_bbox_df, grid_LDOS_bbox_pk_df, fig = grid_lineNpks_offset(
    grid_LDOS_bbox_pk,
    ch_l_name ='LDOS_fb',
    plot_y_offset= 1E-11,
    peak_LIX_min = 1E-11,
    legend_title = "X (nm)")

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

fig,ax = plt.subplots(figsize = (4,6))

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
plt.show()
# -

#using 
bound_box 
# get topography line profile 
# 90 deg rotation 


# ## 2.2 Smoothing 
# ### 2.2.1. Savatzky-Golay (SG) smoothig

# +
# grid_3D -> sg -> derivative 
grid_LDOS_rot= grid_LDOS.copy()

grid_LDOS_rot_sg = savgolFilter_xr(grid_LDOS, window_length = 51, polyorder = 5)
# -

fig,axs = plt.subplots(ncols = 3, figsize = (10,3))
isns.imshow(grid_LDOS_rot.LDOS_fb.isel(bias_mV=0), ax =axs[0])
isns.imshow(grid_LDOS_rot_sg.LDOS_fb.isel(bias_mV=0), ax =axs[1])
axs[0].set_title('original')
axs[1].set_title('SG_smoothing')
sns.lineplot( x = 'bias_mV',
             y = 'LDOS_fb', 
             data=  grid_LDOS_rot.sel(X=5E-9,Y=5E-9, method = "nearest").LDOS_fb.to_dataframe(),
             label ="LDOS", ax = axs[2] )
sns.lineplot( x = 'bias_mV',
             y = 'LDOS_fb',
             data=  grid_LDOS_rot_sg.sel(X=5E-9,Y=5E-9, method = "nearest").LDOS_fb.to_dataframe(),
             label ="Savatzky-Golay smoothing", ax = axs[2] )
plt.tight_layout()
plt.show()


# ## 2.3 Numerical derivative 
#     * Derivative + SG smoothing
#
# ### 2.3.1. SG + 1stderiv + SG + 2nd deriv + SG

# +

grid_LDOS_rot_sg_1deriv = grid_LDOS_rot_sg.differentiate('bias_mV')
grid_LDOS_rot_sg_1deriv_sg = savgolFilter_xr(grid_LDOS_rot_sg_1deriv, window_length = 51, polyorder = 5)
grid_LDOS_rot_sg_2deriv = grid_LDOS_rot_sg_1deriv_sg.differentiate('bias_mV')
grid_LDOS_rot_sg_2deriv_sg =  savgolFilter_xr(grid_LDOS_rot_sg_2deriv, window_length = 51, polyorder = 5)
grid_LDOS_rot_sg_2deriv_sg
# -

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

# set tolerance for I_fb * LIX_fb
tolerance_I, tolerance_dIdV, tolerance_d2IdV2 = 1E-10,1E-10,1E-10
tolerance_LIX, tolerance_dLIXdV , tolerance_d2LIXdV2  = 1E-11,1E-11,1E-11

# #### 2.3.1.2. Using hovolview, XY selection 
# * Choose a point for peak detection 

grid_LDOS_rot_sg

# +
#### use the slider 

xr_data =  grid_LDOS_rot_sg

sliderX = pnw.IntSlider(name='X', 
                       start = 0 ,
                       end = xr_data.X.shape[0]) 
sliderY = pnw.IntSlider(name='Y', 
                       start = 0 ,
                       end = xr_data.Y.shape[0]) 

#sliderX_v_intact = interact(lambda x:  grid_3D.X[x].values, x =sliderX)[1]
#sliderY_v_intact = interact(lambda y:  grid_3D.Y[y].values, y =sliderY)[1]
pn.Column(interact(lambda x:  xr_data.X[x].values, x =sliderX), interact(lambda y: xr_data.Y[y].values, y =sliderY))
# Do not exceed the max Limit ==> error
# how to connect interactive values to the other cell --> need to update (later) 
# -

# #### 2.3.1.2. STS curve at XY point

# +
#grid_LDOS_rot_sg

plot_XYslice_w_LDOS(grid_LDOS_rot_sg, sliderX= sliderX, sliderY= sliderY, ch = 'LDOS_fb',slicing_bias_mV = 10)
# -

# #### 2.3.1.3. Test proper tolerance levels at XY point

fig,ax = plt.subplots(1,1)
grid_3D.I_fb.isel(X=43,Y=49).plot()
#ax.set_xlim(-0.1,0.1)
#ax.set_ylim(-0.2E-12,0.2E-12)
plt.show()

find_plateau_tolarence_values(grid_3D,tolerance_I=1E-11, tolerance_LIX=1E-12,  x_i = sliderX.value,     y_j = sliderY.value)
# with preset function 
plt.show()

# #### 2.3.1.4. Display plateau region by using 1st and 2nd derviative (I_fb & LIX_fb) 
# * Test proper tolerance levels at XY point continued 
#

# +
# use the selected point  
# x_i,y_j = 11, 20
# draw I & LIX, 1st derivative, 2nd derivative 
# draw tolerance value for I &LIX 
# fill between yellow, cyan, magenta to marking 0th, 1st, 2nd derivative plateau
tolerance_I, tolerance_LIX  = 1E-11, 1E-12
tolerance_dIdV, tolerance_d2IdV2 = tolerance_I * 1,tolerance_I * 1
tolerance_dLIXdV , tolerance_d2LIXdV2 = tolerance_LIX * 1, tolerance_LIX * 1


x_i = sliderX.value
y_j = sliderY.value 
print (x_i ,y_j)
fig,axes =  plt.subplots (ncols = 2, nrows=3 , figsize = (6,9), sharex = True)
axs = axes.ravel()

# for I_fb
grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j).plot(ax =axs[0])
axs[0].axhline(y=tolerance_I, c='orange') # pos tolerance line
axs[0].axhline(y=-tolerance_I, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[0].fill_between(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_I, tolerance_I, 
                   where=abs(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_I,
                   facecolor='yellow', interpolate=True, alpha=0.3)
axs[2].fill_between(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_I, tolerance_I, 
                   where=abs(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_I,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the I_fb is plateau in dIdV curve
axs[4].fill_between(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_I, tolerance_I, 
                   where=abs(grid_LDOS_rot.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_I,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the I_fb is plateau in d2Id2V curve
axs[0].set_ylim((-tolerance_I*10, tolerance_I*10))#set ylimit for magnification


# for LIX_fb
grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j).plot(ax = axs[1])
axs[1].axhline(y=tolerance_LIX, c='orange') # pos tolerance line
axs[1].axhline(y=-tolerance_LIX, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[1].fill_between(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)

axs[3].fill_between(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the LIX_fb is plateau in dIdV curve

axs[5].fill_between(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the LIX_fb is plateau in dIdV curve

axs[1].set_ylim((-tolerance_LIX*10, tolerance_LIX*10))#set ylimit for magnification



# for I_fb after 1st derivative + smoothing 
# dI/dV
grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j).plot(ax =axs[2])
axs[2].axhline(y=tolerance_dIdV, c='orange') # pos tolerance line
axs[2].axhline(y=-tolerance_dIdV, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[2].fill_between(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dIdV, tolerance_dIdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_dIdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)

axs[4].fill_between(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dIdV, tolerance_dIdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_dIdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)

axs[0].fill_between(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dIdV, tolerance_dIdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_dIdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)

# fill area with cyan where the dIdV is plateau in d2Id2V curve

axs[2].set_ylim((-tolerance_dIdV*10, tolerance_dIdV*10))#set ylimit for magnification
axs[2].set_ylabel("dIdV")


# for LIX_fb after 1st derivative + smoothing 
# d(LIX)/dV
grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).plot(ax = axs[3])

axs[3].axhline(y=tolerance_dLIXdV, c='orange') # pos tolerance line
axs[3].axhline(y=-tolerance_dLIXdV, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[3].fill_between(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)

axs[5].fill_between(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)
axs[1].fill_between(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)
# fill area with cyan where the dLIXdV is plateau in d2Id2V curve


axs[3].set_ylim((-tolerance_dLIXdV*10, tolerance_dLIXdV*10))#set ylimit for magnification
axs[3].set_ylabel("dLIXdV")

# for I_fb after 2nd derivative + smoothing 
# d2I/dV2
grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j).plot(ax =axs[4])
axs[4].axhline(y=tolerance_d2IdV2, c='orange') # pos tolerance line
axs[4].axhline(y=-tolerance_d2IdV2, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[4].fill_between(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2IdV2, tolerance_d2IdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2IdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)
axs[0].fill_between(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2IdV2, tolerance_d2IdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2IdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)
axs[2].fill_between(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2IdV2, tolerance_d2IdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2IdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)


axs[4].set_ylim((-tolerance_d2IdV2*10, tolerance_d2IdV2*10))#set ylimit for magnification
axs[4].set_ylabel("d2IdV2")



# for LIX_fb after 2nd derivative + smoothing 
# d2(LIX)/dV2
grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).plot(ax = axs[5])

axs[5].axhline(y=tolerance_d2LIXdV2, c='orange') # pos tolerance line
axs[5].axhline(y=-tolerance_d2LIXdV2, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[5].fill_between(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)

axs[1].fill_between(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)
axs[3].fill_between(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)

axs[5].set_ylim((-tolerance_d2LIXdV2*10, tolerance_d2LIXdV2*10))#set ylimit for magnification
axs[5].set_ylabel("d2LIXdV2")

## how to draw a pixels 






fig.tight_layout()
# -

# #### 2.3.1.5. Display plateau region by using 1st and 2nd derviative (LDOS_fb)
# * Test proper tolerance levels at XY point continued only for LDOS_fb
#

# +
# use the selected point  
# x_i,y_j = 11, 20
# draw I & LIX, 1st derivative, 2nd derivative 
# draw tolerance value for I &LIX 
# fill between yellow, cyan, magenta to marking 0th, 1st, 2nd derivative plateau
tolerance_LIX  =0.5E-12
tolerance_dLIXdV , tolerance_d2LIXdV2 = tolerance_LIX * 1, tolerance_LIX * 1


y_j = sliderY.value 
print (x_i ,y_j)
fig,axes =  plt.subplots (ncols = 1, nrows=3 , figsize = (6,9), sharex = True)
axs = axes.ravel()

# for LDOS_fb
grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j).plot(ax = axs[0])
axs[0].axhline(y=tolerance_LIX, c='orange') # pos tolerance line
axs[0].axhline(y=-tolerance_LIX, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[0].fill_between(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)

axs[1].fill_between(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the LDOS_fb is plateau in dIdV curve

axs[2].fill_between(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(grid_LDOS_rot_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='yellow', interpolate=True, alpha=0.3)
# fill area with yellow where the LDOS_fb is plateau in dIdV curve

axs[0].set_ylim((-tolerance_LIX*10, tolerance_LIX*10))#set ylimit for magnification



# for LDOS_fb after 1st derivative + smoothing 
# d(LIX)/dV
grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).plot(ax = axs[1])

axs[1].axhline(y=tolerance_dLIXdV, c='orange') # pos tolerance line
axs[1].axhline(y=-tolerance_dLIXdV, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[1].fill_between(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)

axs[2].fill_between(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)
axs[0].fill_between(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_dLIXdV, tolerance_dLIXdV, 
                   where=abs(grid_LDOS_rot_sg_1deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_dLIXdV,
                   facecolor='cyan', interpolate=True, alpha=0.3)
# fill area with cyan where the dLIXdV is plateau in d2Id2V curve


axs[1].set_ylim((-tolerance_dLIXdV*10, tolerance_dLIXdV*10))#set ylimit for magnification
axs[1].set_ylabel("dLIXdV")


# for LDOS_fb after 2nd derivative + smoothing 
# d2(LIX)/dV2
grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).plot(ax = axs[2])

axs[2].axhline(y=tolerance_d2LIXdV2, c='orange') # pos tolerance line
axs[2].axhline(y=-tolerance_d2LIXdV2, c='orange') # neg tolerance line
# fill between x area where Y value is smaller than tolerance value 
axs[2].fill_between(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)

axs[0].fill_between(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)
axs[1].fill_between(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_d2LIXdV2, tolerance_d2LIXdV2, 
                   where=abs(grid_LDOS_rot_sg_2deriv_sg.LDOS_fb.isel(X = x_i, Y = y_j)) <= tolerance_d2LIXdV2,
                   facecolor='magenta', interpolate=True, alpha=0.3)

axs[2].set_ylim((-tolerance_d2LIXdV2*10, tolerance_d2LIXdV2*10))#set ylimit for magnification
axs[2].set_ylabel("d2LIXdV2")

## how to draw a pixels 


fig.tight_layout()
plt.show()
# -

# #### 2.3.1.5. find_plateau  xarray 
#     * After checking which tolerance is relaible for plateau detection
#     * for SC gap..  dIdV or dLIX/dV ?
#     * grid_LDOS_rot_sg

grid_LDOS_rot_sg_plateau = find_plateau(grid_LDOS_rot_sg)

grid_LDOS_rot_sg_1deriv_sg_plateau = find_plateau(grid_LDOS_rot_sg_1deriv_sg)
grid_LDOS_rot_sg_1deriv_sg_plateau


# ### 2.4. peak finding and plot peaks with STS results 
#

def find_peaks_xr(xrdata, distance = 10): 
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
                    np.array([ find_peaks(xrdata[data_ch].isel(X = x).values, distance = distance)
                              for x in range(x_axis)], dtype = object )[:,0],
                dims=["X"],
                coords={"X": xrdata.X})
            
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size

                #print(xrdata_prcssd[data_ch])

                xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                    np.array([ find_peaks(xrdata[data_ch].isel(Y = y).values, distance = distance)
                              for y in range(y_axis)], dtype = object )[:,0],
                dims=["Y"],
                coords={"Y": xrdata.Y})
            
            # ==> updated 
            
        elif len(xrdata[data_ch].dims) == 3:
            
            x_axis = xrdata.X.size
            y_axis = xrdata.Y.size
            print (data_ch)
            """xrdata_prcssd[data_ch+'_peaks']= xr.DataArray(np.ones((xAxis,yAxis), dtype = object),
                                                             dims=["X", "Y"],
                                                             coords={"X": xrdata.X, "Y": xrdata.Y} )"""
            xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values, distance = distance)[0] 
                          for x in range(x_axis)  
                          for y in range(y_axis)], dtype = object ).reshape(x_axis,y_axis),
                dims=["X", "Y"],
                coords={"X": xrdata.X, "Y": xrdata.Y})         
        elif len(xrdata[data_ch].dims) == 1:
            if 'bias_mV' in xrdata.dims: 
                for data_ch in xrdata: 
                    xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (find_peaks (xrdata[data_ch], distance = distance))
        else : pass
    return xrdata_prcssd
#grid_2D_sg_pks = find_peaks_xr(grid_2D_sg)

grid_LDOS_rot_sg_2deriv_sg_dks= find_peaks_xr(-grid_LDOS_rot_sg_2deriv_sg, distance = 10) 

grid_LDOS_rot_sg_2deriv_sg_dks


# ### 2.5.2 STS curve with peaks  choose the selected area for line profile STS
#     * For the line averge + pks
#     * use the grid3D_line_avg_pks ( X or Y direction) function
#     * For ther offset plot of line averaged dataset
#     * use the grid_lineNpks_offset *( slcted pk with LIX limit value, + return line &pk dataframe with figure)

def grid3D_line_avg_pks (xr_data, average_in =  'X',
                         ch_l_name = 'LIX_unit_calc',
                         distance = None,
                         threshold = None) : 

    if average_in ==  'X':
        mean_direction = 'X'
        line_direction = 'Y'
        print('line_direction == Y')
    elif average_in ==  'Y': 
        mean_direction = 'Y'
        line_direction = 'X'
        print('line_direction == X')
    else: print ('check the line STS direction in 3D dataset ')

    xr_data_l = xr_data.mean( dim = mean_direction )
    xr_data_l.attrs = xr_data.attrs.copy()
    # add attrs manually 

    ### find peaks & pad 
    #* use the SG filter 
    #* derivative (dim = 'bias_mV') twice 
    #* find peaks & padding 

    xr_data_l_pks=  peak_pad(
        find_peaks_xr(
            savgolFilter_xr(
                savgolFilter_xr(
                    xr_data_l.differentiate(coord='bias_mV')
                ).differentiate(coord='bias_mV')
            )*-1, distance = distance))
    if average_in ==  'X':
        xr_data_l_pks.attrs['line_direction'] ='Y'
    elif average_in ==  'Y': 
        xr_data_l_pks.attrs['line_direction'] ='X'
    else: print ('check the line STS direction in 3D dataset ')
    # smooth, deriv, smooth, derive, find peak, padding 
    #xr_data_l_pks
    
    
    # in the xr_data_l_pks
    # choose a particular channel after pean & pad 
    # replace the channel to original xrdata 
    # xr_data_l_pks contains 2nd derivative results 
    
    for ch_names in xr_data:
        xr_data_l_pks[ch_names] =  xr_data_l [ch_names]
    
    
    return xr_data_l_pks
#grid_3D_test_l_pk = grid3D_line_avg_pks(grid_3D, average_in= 'Y')
#grid_3D_test_l_pk

# grid_LDOS_rot_sg_2deriv_sg_dks.LDOS_fb.isel(X=x_i,Y=y_j)


grid_LDOS_rot

# +
grid_LDOS_rot_bbox =  grid_LDOS_rot.where ((grid_LDOS_rot.Y>0E-10)*(grid_LDOS_rot.Y<1E-8), drop= True).where ((grid_LDOS_rot.X>0E-10)*(grid_LDOS_rot.X<10.0E-8), drop= True)

grid_LDOS_rot_bbox_sg =  savgolFilter_xr(grid_LDOS_rot_bbox, window_length=11,polyorder=3 ).where ((grid_LDOS_rot_bbox.bias_mV>-200)*(grid_LDOS_rot_bbox.bias_mV<200), drop= True)
# -

grid_LDOS_rot_bbox_sg


grid_LDOS_rot_bbox_sg_pk  = grid3D_line_avg_pks( grid_LDOS_rot_bbox_sg ,ch_l_name ='LDOS_fb', average_in= 'Y',distance = 5, threshold = 0.2E-13) 
grid_LDOS_rot_bbox_sg_pk

grid_LDOS_rot_bbox_sg_slct, grid_LDOS_rot_bbox_sg_df, grid_LDOS_rot_bbox_sg_pk_df, fig = grid_lineNpks_offset(grid_LDOS_rot_bbox_sg_pk,ch_l_name ='LDOS_fb', plot_y_offset= 1E-13,peak_LIX_min = 1E-14, legend_title = "X (nm)")
plt.show()

# # 3. Peaks in 3D 
#
#
# * 3.1. Peak position detection 
# * 3.1.1. SG Smoothing & Numerical derivative 
# * 3.1.2. Find peaks in 2nd derivative 
# * 3.1.3. Filtering Peaks only (bool) 
#
# * 3.2. Peak properties plot 
# * 3.2.1. find peaks2 find_peaks_prpt
# * 3.2.2. Peak height at peak position apply LDOS value (peak Height) 
# * 3.2.3. Peak width plot 
# * 3.2.4. Peak promient plot 
#
#
# * 3.3. Peak and in gap states 
#
# * 3.3. Peaks clustering 
#
#
# # 4. Fitting multi peak gaussian 
#

# #### peak finding using JW functions 
# * grid3D_line_avg_pks
# * find_peaks_xr
# * peak_pad
# * find_peaks_prominence_xr
#      * confirmed for Line STS chase. 
#      * check 3D case later 
#      * currently format need to be more general. 
#          * use the peak_pad channel 
#          * peak with irregular length is not applicapable now. (need to be improved) 
#      * extract the prominence info at the peak position 
#          * make an separate dataframe to draw the 2D plot. (or 3D) 
#      * prominence function only 
#      * make a separate width function 
#          * find_peaks_width_xr
#      * find_peaks_properties_xr --> prominence or width was given
#      

grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg ,ch_l_name ='LDOS_fb', average_in= 'Y',distance =10, height = 2E-11, padding_value= 0) 
grid_LDOS_sg_pk  

grid_LDOS_sg_pk = find_peaks_xr(grid_LDOS_sg, prominence  = 1E-13)
#grid_LDOS_sg_pk


grid_LDOS_sg_pk_pad = peak_pad(grid_LDOS_sg_pk, padding_value=0)
#grid_LDOS_sg_pk_pad

grid_LDOS_sg_pk_pad_prominence = find_peaks_prominence_xr(grid_LDOS_sg_pk_pad)

# #### extrct prominence part from xr data array 
# * extract dataframe 

# +
##############
# how to extrct prominence part 

#grid_LDOS_sg_pk_pad_prominence
#grid_LDOS_sg_pk_pad_prominence.LDOS_fb_peak_prominence.isel(prominence = 0)
#grid_LDOS_sg_pk_pad_prominence.LDOS_fb_peak_prominence.sel(prominence = 'prominences').drop('prominence')


##################################

# how to extract peak position part 
#grid_LDOS_sg_pk_pad_prominence.LDOS_fb_peaks_pad.isel(Y=0)


# +
#import plotly.express as px
# maybe... layter plotly 


#################################
####  extract peak & prominence 
#################################
xr_peaks =grid_LDOS_sg_pk_pad_prominence.LDOS_fb_peaks_pad.isel(Y=0)
xr_promi = grid_LDOS_sg_pk_pad_prominence.LDOS_fb_peak_prominence.sel(prominence = 'prominences').drop('prominence')

##############################
# convert to dataframe test
##############################
#
# xr_peaks.to_dataframe().drop(columns = ['Y'])
#  xr_promi.to_dataframe()
# make a same shaped dataframe 

#########################################
# Make DATA FRAME FOR PLOT in 2D 
xr_df = pd.concat ([xr_peaks.to_dataframe().drop(columns = ['Y']),  xr_promi.to_dataframe()], axis =1)
#########################
# remove  zeros....  
# instead of using padding value  = np.nan use  "0" to match the integer condition 
xr_df_nonzero = xr_df[xr_df.LDOS_fb_peaks_pad != 0]
###############
#xr_promi
# -

# #### plot in 2D with isns is **not** correct  

# +
##############################
# reshaping the data set 
##############################
#xr_df_nonzero.reset_index()
#############################
# after reset_index, make a pivot table. only peak points are show. 

xr_df_nonzero_reshape = xr_df_nonzero.reset_index().pivot(index = 'X', columns = 'LDOS_fb_peaks_pad', values = 'LDOS_fb_peak_prominence')

############################
## plot in 2D 
###########################

isns.imshow (xr_df_nonzero_reshape)


# peak axis is not correct.  data points  < original frame 
# -

# #### use the xarray plot to fill **Nan** area 
# * find a better option. 
#

# +
xr_df_nonzero_reshape

xr.DataArray (xr_df_nonzero_reshape).plot()
#xr_df_nonzero_reshape.plot.scatter()
#xr_df_nonzero_reshape.plot.scatter(x = 'X', y  = 'LDOS_fb_peaks_pad')

# +
#grid_LDOS_sg_pk.LDOS_fb.plot()
############
# use seaborn image
'''
fig,ax = plt.subplots(figsize= (4,4))
isns.imshow (grid_LDOS_sg_pk.LDOS_fb,cbar=False, aspect = 0.5, ax = ax)
ax.set_aspect(10)
plt.show()
'''
#############
# collect peaks_pad near center 

peaks_near_0 = grid_LDOS_sg_pk_pad.LDOS_fb_peaks_pad.where (abs(grid_LDOS_sg_pk_pad.LDOS_fb_peaks_pad-256)< 100)

peaks_near_0
#

# +
#grid_LDOS_sg_pk.bias_mV[peaks_near_0.sel(X= 2E-8, method = 'nearest').values ]

peaks_near_0.sel(X= 1E-8, method = 'nearest').dropna(dim = 'peaks').astype(int).values[0]
# select 1 X position, drop nan, inter type, values as np array 
#peaks_near_0
# -

### input to the bias_mV 
grid_LDOS_sg_pk_pad.bias_mV[peaks_near_0.sel(X= 1E-8, method = 'nearest').dropna(dim = 'peaks').astype(int).values[0]]
## find bias mV 

grid_LDOS_sg_pk_pad

grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg,ch_l_name ='LDOS_fb', average_in= 'Y',distance =20, prominence= 4E-11, height = 1E-11,  threshold= 1E-12, padding_value= 0) 
grid_LDOS_sg_pk


# +

grid_LDOS_sg_pk_slct, grid_LDOS_sg_df, grid_LDOS_sg_pk_df, fig = grid_lineNpks_offset(grid_LDOS_sg_pk,ch_l_name ='LDOS_fb', plot_y_offset= 2E-11,legend_title = "X (nm)")#peak_LIX_min = 3E-11)
plt.show()
# -

# ## 3.1. Peak position detection

# ### 3.1.1. SG Smoothing & Numerical derivative
#

# 3.1.2. Rolling using XR 

# +

grid_LDOS

# +
import matplotlib.patches as patches

rec_x0, rec_y0 = 5.6E-9,4.5E-9
rec_width,rec_height = 0.8E-9, 10E-9

grid_LDOS_zm = grid_LDOS.where( (grid_LDOS.X >rec_x0)&(grid_LDOS.X <rec_x0+rec_width)&(grid_LDOS.Y >rec_y0) &(grid_LDOS.Y <rec_y0+rec_height ), drop = True)
grid_topo_zm = grid_topo.where( (grid_LDOS.X >rec_x0)&(grid_LDOS.X <rec_x0+rec_width)&(grid_LDOS.Y >rec_y0) &(grid_LDOS.Y <rec_y0+rec_height ), drop = True)

fig,axs = plt.subplots(ncols =3, figsize = (8,3))
isns.imshow (grid_LDOS.LDOS_fb.sel(bias_mV =  -800, method = 'nearest'), ax =axs[0], robust = True)
# plot map

#int(rec_x0/grid_LDOS.X_spacing)
#int(rec_y0/grid_LDOS.Y_spacing)
#int(rec_width/grid_LDOS.X_spacing)
#int(height/grid_LDOS.Y_spacing)


rec_xy = (int(rec_x0/grid_LDOS.X_spacing), int(rec_y0/grid_LDOS.Y_spacing))
rec_w_px,rec_h_px = int(rec_width/grid_LDOS.X_spacing),int(rec_height/grid_LDOS.Y_spacing)

rec_in_topo =  patches.Rectangle( rec_xy , rec_w_px,rec_h_px , linewidth=1, edgecolor='r', facecolor='none')
axs[0].add_patch(rec_in_topo)
# add rectangle 
isns.imshow (grid_LDOS_zm.LDOS_fb.sel(bias_mV =  0), ax =axs[1], robust = True)

sns.lineplot(x =  'X', y= 'topography', data = grid_topo_zm.topography.to_dataframe(), ax= axs[2])
plt.tight_layout()
plt.show()
# -

#grid_topo_zm.topography.to_dataframe()
sns.lineplot(x =  'X', y= 'topography', data = grid_topo_zm.topography.to_dataframe())
plt.show()


# +

def savgolFilter_xr(xrdata,window_length=7,polyorder=3): 
    # window_length = odd number
    #import copy
    #xrdata_prcssd = copy.deepcopy(xrdata)
    xrdata_prcssd = xrdata.copy()
    print('Apply a Savitzky-Golay filter to an xarray Dataset.')

    for data_ch in xrdata:

        if len(xrdata[data_ch].dims) == 2:
            print('3D data')
            # smoothing filter only for the 3D data set
            # ==> updaded 
            xrdata_prcssd[data_ch]
            ### 2D data case 
            ### assume that coords are 'X','Y','bias_mV'
            #### two case X,bias_mV or Y,bias_mV 
            if 'X' in xrdata[data_ch].dims :
                x_axis = xrdata.X.size # or xrdata.dims.mapping['X']
                # xrdata is X,bias_mV 
                # use the isel(X = x) 
                xrdata_prcssd[data_ch] = xr.DataArray (
                    np.array (
                        [sp.signal.savgol_filter(xrdata[data_ch].isel(X = x).values,
                                                 window_length, 
                                                 polyorder , 
                                                 mode = 'nearest')
                         for x in range(x_axis)]),
                    dims = ["X", "bias_mV"],
                    coords = {"X": xrdata.X,
                              "bias_mV": xrdata.bias_mV})
            elif 'Y' in xrdata[data_ch].dims  :                # xrdata is XY,bias_mV                 # use the isel(Y = y) 
                y_axis = xrdata.Y.size
                xrdata_prcssd[data_ch] = xr.DataArray (
                    np.array (
                        [sp.signal.savgol_filter(xrdata[data_ch].isel(Y = y).values,
                                                 window_length, 
                                                 polyorder , 
                                                 mode = 'nearest')
                         for y in range(y_axis) ]),
                    dims = ["Y", "bias_mV"],
                    coords = {"Y": xrdata.Y,
                              "bias_mV": xrdata.bias_mV}
                )
            else: pass
            
        elif len(xrdata[data_ch].dims) == 3:
            x_axis = xrdata.X.size # or xrdata.dims.mapping['X']
            y_axis = xrdata.Y.size
            print (data_ch)
            xrdata_prcssd[data_ch] = xr.DataArray (
                np.array ([
                    sp.signal.savgol_filter(xrdata[data_ch].isel(X = x, Y = y).values,
                                            window_length, 
                                            polyorder , 
                                            mode = 'nearest')
                    for y in range(y_axis) 
                    for x in range(x_axis)
                ] ).reshape(y_axis,x_axis, xrdata.bias_mV.size),
                dims = ["Y", "X", "bias_mV"],
                coords = {"X": xrdata.X,
                          "Y": xrdata.Y,
                          "bias_mV": xrdata.bias_mV}            )
            # transpose np array to correct X&Y direction 
        else : pass
    return xrdata_prcssd

#grid_2D_sg = savgolFilter_xr(grid_2D)
#grid_2D_sg


# +
grid_LDOS_sg = savgolFilter_xr(grid_LDOS_zm, window_length=21, polyorder=5)
grid_LDOS_1diff =  grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1diff_sg = savgolFilter_xr(grid_LDOS_1diff, window_length=21, polyorder=5)
grid_LDOS_2diff =  grid_LDOS_1diff_sg.differentiate('bias_mV')
grid_LDOS_2diff_sg = savgolFilter_xr(grid_LDOS_2diff, window_length=21, polyorder=5)



# -

# ### 3.1.2. Find peaks in 2nd derivative

grid_LDOS_sg

grid_LDOS_sg.isel(X=0).LDOS_fb.plot()

grid_LDOS_2diff_sg_dps = find_peaks_xr ( - grid_LDOS_2diff_sg, distance= 10)
grid_LDOS_2diff_sg_dps_pad = peak_pad (grid_LDOS_2diff_sg_dps)


# +
hv_XY_slicing(grid_LDOS_2diff_sg, slicing='X' , ch='LDOS_fb')#.opts(clim = (0,5E-10))
# 2deriv plot

#hv_XY_slicing(grid_LDOS_sg, slicing='Y' , ch='LDOS_fb')#.opts(clim = (0,5E-10))
#LDOS_sg plot

#hv_bias_mV_slicing(grid_LDOS_2diff_sg_dps_pad.where(grid_LDOS_2diff_sg_dps_pad.X<5E-9).where(grid_LDOS_2diff_sg_dps_pad.Y>3E-9), ch='LDOS_fb')
# -

grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg,ch_l_name ='LDOS_fb', average_in= 'X',distance = 20, threshold = (5E-9)) 
#grid_LDOS_sg_pk

grid_LDOS_sg_pk_slct, grid_LDOS_sg_df, grid_LDOS_sg_pk_df, fig = grid_lineNpks_offset(grid_LDOS_sg_pk,ch_l_name ='LDOS_fb', 
                                                                                      plot_y_offset= 2E-11,
                                                                                      legend_title = "X (nm)",
                                                                                      peak_LIX_min = 4E-15)
plt.show()

axs.Axes.set_ylabel('dI/dV')
fig

# +
grid_LDOS_sg

grid_LDOS_sg = savgolFilter_xr(grid_LDOS)
# -

grid_LDOS_zm = grid_LDOS_sg.where( (grid_LDOS_sg.Y<1.45E-8)&(grid_LDOS_sg.Y>0.45E-8)).where((grid_LDOS_sg.X<1.1E-8)&(grid_LDOS_sg.X>0.1E-8))

isns.imshow(grid_LDOS_zm.LDOS_fb.sel(bias_mV =0, method = 'nearest'), robust = True, cmap = 'bwr')

# #  save npy for tomviz 


# +
# use grid_LDOS_rot for 120x 120 
#grid_LDOS_rot

grid_LDOS_sg = savgolFilter_xr(grid_LDOS_rot, window_length=61, polyorder=5)
grid_LDOS_1diff =  grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1diff_sg = savgolFilter_xr(grid_LDOS_1diff, window_length=61, polyorder=5)
grid_LDOS_2diff =  grid_LDOS_1diff_sg.differentiate('bias_mV')
grid_LDOS_2diff_sg = savgolFilter_xr(grid_LDOS_2diff, window_length=61, polyorder=5)

# -

grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV.sum()

# +
grid_LDOS_2diff_sg_dps = find_peaks_xr ( - grid_LDOS_2diff_sg, distance= 5)
grid_LDOS_2diff_sg_dps_pad = peak_pad (grid_LDOS_2diff_sg_dps)
# find a peak in the Zoom in area 
# grid_LDOS_2diff_sg_dps_pad


grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch= 'LDOS_fb')
#grid_LDOS_2diff_sg_zm_dps_pad_mV

grid_LDOS_rot['LDOS_pk_mV'] = (grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV * grid_LDOS_rot.LDOS_fb).astype(float)
grid_LDOS_rot
# extract the peak positions 


np.save('LDOS_pk_zm_mV.npy', grid_LDOS_rot.LDOS_pk_mV.where((grid_LDOS_rot.bias_mV> - 400)& (grid_LDOS_rot.bias_mV<400), drop = True).to_numpy())

# -

grid_LDOS_rot

# +
#### use the slider 

xr_data =  grid_LDOS_sg

sliderX = pnw.IntSlider(name='X', 
                       start = 0 ,
                       end = xr_data.X.shape[0]) 
sliderY = pnw.IntSlider(name='Y', 
                       start = 0 ,
                       end = xr_data.Y.shape[0]) 

#sliderX_v_intact = interact(lambda x:  grid_3D.X[x].values, x =sliderX)[1]
#sliderY_v_intact = interact(lambda y:  grid_3D.Y[y].values, y =sliderY)[1]
pn.Column(interact(lambda x:  xr_data.X[x].values, x =sliderX), interact(lambda y: xr_data.Y[y].values, y =sliderY))
# Do not exceed the max Limit ==> error
# how to connect interactive values to the other cell --> need to update (later) 
# -

# #### 2.3.1.2. STS curve at XY point

plot_XYslice_w_LDOS(grid_LDOS_sg, sliderX= sliderX, sliderY= sliderY, ch = 'LDOS_fb',slicing_bias_mV= 0)

grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg.isel(Y= [1,2]) ,ch_l_name ='LDOS_fb', average_in= 'Y',distance = 5, threshold = 1E-11) 
#grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg.isel(X= [14,15]) ,ch_l_name ='LDOS_fb', average_in= 'X',distance = 5, threshold = 1E-11) 
grid_LDOS_sg_pk

grid_LDOS_sg_pk_slct, grid_LDOS_sg_df, grid_LDOS_sg_pk_df, fig = grid_lineNpks_offset(grid_LDOS_sg_pk,ch_l_name ='LDOS_fb', plot_y_offset= 5E-10,peak_LIX_min = 1E-10, legend_title = "Y (nm)")
plt.show()


def peak_mV_3Dxr(xr_data,ch='LIX_fb'): 
    #after find_peaks_xr 
    xrdata_prcssd = xr_data.copy(deep = True)
    print('After peak finding in STS, marking in the 3D data')
    x_axis = xr_data.X.size
    y_axis = xr_data.Y.size
    bias_mV_axis = xr_data.bias_mV.size
    
    peaks_list = xr_data[ch+'_peaks'].values
    for data_ch in xr_data:
        if '_peaks' in data_ch:
            pass
        # do nothing for channels with_peaks information  
        else: 
            xrdata_prcssd[data_ch+'_peaks_mV'] = xr.DataArray (
                np.array([ xr_data.bias_mV.isin(xr_data.bias_mV[peaks_list[x,y]])
                          for x in range(x_axis)  
                          for y in range(y_axis)], dtype = object ).reshape(x_axis,y_axis,bias_mV_axis),
                dims=["X", "Y","bias_mV"],
                coords={"X": xr_data.X, "Y": xr_data.Y,  "bias_mV": xr_data.bias_mV}) 
    return xrdata_prcssd

# +
#grid_LDOS_zm = grid_LDOS#.where(grid_LDOS.X<5E-9, drop= True).where(grid_LDOS.Y>3E-9, drop = True)
#grid_LDOS_2diff_sg_zm = grid_LDOS_2diff_sg#.where(grid_LDOS_2diff_sg.X<5E-9, drop = True).where(grid_LDOS_2diff_sg.Y>3E-9, drop = True)
## Zoom in for LDOS & LDOS 2nd derivative 


grid_LDOS_2diff_sg_dps = find_peaks_xr ( - grid_LDOS_2diff_sg, distance= 5)
grid_LDOS_2diff_sg_dps_pad = peak_pad (grid_LDOS_2diff_sg_dps)
# find a peak in the Zoom in area 
grid_LDOS_2diff_sg_dps_pad


# -

def peak_mV_3Dxr(xr_data,ch='LIX_fb'): 
    '''
    after peak finding 
    make a boolean 3D arrary that show peak positions 
    
    computation with other channels --> extract info 
    
    '''
    #after find_peaks_xr 
    xrdata_prcssd = xr_data.copy(deep = True)
    print('After peak finding in STS, marking in the 3D data')
    x_axis = xr_data.X.size
    y_axis = xr_data.Y.size
    bias_mV_axis = xr_data.bias_mV.size
    
    peaks_list = xr_data[ch+'_peaks'].values
    for data_ch in xr_data:
        if '_peaks' in data_ch:
            pass
        # do nothing for channels with_peaks information  
        else: 
            xrdata_prcssd[data_ch+'_peaks_mV'] = xr.DataArray (
                np.array([ xr_data.bias_mV.isin(xr_data.bias_mV[peaks_list[x,y]])
                          for x in range(x_axis)  
                          for y in range(y_axis)], dtype = object ).reshape(x_axis,y_axis,bias_mV_axis),
                dims=["X", "Y","bias_mV"],
                coords={"X": xr_data.X, "Y": xr_data.Y,  "bias_mV": xr_data.bias_mV}) 
    return xrdata_prcssd


# +
grid_LDOS_2diff_sg_dps_pad_mV = peak_mV_3Dxr(grid_LDOS_2diff_sg_dps_pad, ch= 'LDOS_fb')
#grid_LDOS_2diff_sg_zm_dps_pad_mV

grid_LDOS_zm['LDOS_pk_mV'] = (grid_LDOS_2diff_sg_dps_pad_mV.LDOS_fb_peaks_mV * grid_LDOS_zm.LDOS_fb).astype(float)
#grid_LDOS_zm
# extract the peak positions 
# -
grid_LDOS_2diff_sg_dps_pad


np.save('LDOS_pk_zm_mV.npy', grid_LDOS_zm.LDOS_pk_mV.where((grid_LDOS_zm.bias_mV> - 1.4)&(grid_LDOS_zm.bias_mV<1.4), drop = True).to_numpy())

grid_LDOS_zm.LDOS_pk_mV.where((grid_LDOS_zm.bias_mV>-1.4)&(grid_LDOS_zm.bias_mV<1.4), drop = True).to_numpy().sum()

# #### collect selected points and not selected points 
#
#

# +
grid_3D_slct_pts_df = grid_3D_slct_pts.LIX_fb.to_dataframe()
grid_3D_not_slct_pts_df = grid_3D_not_slct_pts.LIX_fb.to_dataframe()

#grid_3D_not_slct_pts_df
# -

grid_3D_slct_pts_df.rename(columns = {"LIX_fb" : "LIX_large_defect"})
grid_3D_not_slct_pts_df.rename(columns = {"LIX_fb" : "LIX_avg"})

grid_3D_avg = pd.concat ([grid_3D_slct_pts_df.rename(columns = {"LIX_fb" : "LIX_large_defect"}),
                          grid_3D_not_slct_pts_df.rename(columns = {"LIX_fb" : "LIX_avg"})], axis=1 )

grid_3D_avg_mean = grid_3D_avg.groupby('bias_mV').mean()
grid_3D_avg_std = grid_3D_avg.groupby('bias_mV').std()
grid_3D_avg_mean

grid_3D_avg_mean.index

# #### use matplotlib to show fillbetween 

fig, ax = plt.subplots()
ax.plot( grid_3D_avg_mean.LIX_large_defect)
ax.plot( grid_3D_avg_mean.LIX_avg)
#plt.show()
ax.fill_between(grid_3D_avg_mean.index,grid_3D_avg_mean.LIX_large_defect - grid_3D_avg_std.LIX_large_defect, grid_3D_avg_mean.LIX_large_defect + grid_3D_avg_std.LIX_large_defect, alpha=0.2)
ax.fill_between(grid_3D_avg_mean.index,grid_3D_avg_mean.LIX_avg - grid_3D_avg_std.LIX_avg, grid_3D_avg_mean.LIX_avg + grid_3D_avg_std.LIX_avg, alpha=0.2)
#ax.plot(x, y, 'o', color='tab:brown')

grid_3D_avg_df =  grid_3D_avg.unstack().melt().set_index('bias_mV')
grid_3D_avg_df.columns = ['Type', 'LIX']
grid_3D_avg_df

# #### use sns to compare two area 

#sns.lineplot(data = grid_3D_avg_df, x = "bias_mV", y = "LIX",hue = "Type", errorbar =("sd"))
sns.lineplot(data = grid_3D_avg, x = "bias_mV", y = "LIX_avg", errorbar =("sd"), label = "LIX_avg")
sns.lineplot(data = grid_3D_avg, x = "bias_mV", y = "LIX_large_defect", errorbar =("sd"), label = "LIX_large_defect")


# ### Use the topography map for threshold
#
#

# +
grid_xr_gs = grid_xr
plane_fit_y_xr(grid_xr).topography 

grid_xr_gs.topography.values = plane_fit_y_xr(grid_xr).topography 
grid_xr_gs = filter_convert2grayscale(grid_xr_gs)
topograph_gs = grid_xr_gs.topography

topograph_gs.plot()
# -

# #### check the histogram + Otsu thresholds
#

# +
#grid_xr.topography.plot.hist()
#threshold_otsu_xr(grid_xr.topography).plot()

threshold_otsu_xr(grid_xr_gs).topography.plot()
topo_mask = threshold_otsu_xr(grid_xr_gs).topography.isnull()

#######################
# topo_mask 
# mask with xr format 
#######################
# -

####################
# topo masking 
#
# topo  T&F  
grid_xr.topography.where(~topo_mask).plot()
###############################

# +
###############################
#  
#  topo masking for LIX_fb
#
#################################

grid_xr.LIX_fb.where(~topo_mask)
filtere_df  = grid_xr.LIX_fb.where(~topo_mask).to_dataframe()

# standard deviation 
sns.lineplot(data = filtere_df, x = "bias_mV", y = "LIX_fb", errorbar =("sd"))


## confidential interval 
#sns.lineplot(data = filtere_df, x = "bias_mV", y = "LIX_fb", errorbar =("ci"))


## percentile interval (50%)
#sns.lineplot(data = filtere_df, x = "bias_mV", y = "LIX_fb", errorbar =("pi"))

# -

# ### Masking with LDOS 
# * use the sel(bias_mV=-300,method="nearest")
# * use the bbox xr 
#

# +
# Test grid slicing use sel 

grid_3D_bbox.LIX_fb.sel(bias_mV=-300,method="nearest").plot()
# -

# #### Use the grayscale - threshold - slicing 
#

# +
LDOS_mask  = threshold_mean_xr(filter_convert2grayscale(grid_3D_bbox)).LIX_unit_calc.sel(bias_mV=-300,method="nearest")

LDOS_mask.plot()

# LDOS_mask.isnull()

# LDOS_mask.notnull()


# +
# masking with LDOS mask 
grid_3D_bbox.where(LDOS_mask.isnull())

filtered_LDOS300mV_null_df = grid_xr.LIX_fb.where(LDOS_mask.isnull()).to_dataframe()
filtered_LDOS300mV_notnull_df = grid_xr.LIX_fb.where(LDOS_mask.notnull()).to_dataframe()

filtered_LDOS300mV_df = pd.concat ([filtered_LDOS300mV_null_df,filtered_LDOS300mV_notnull_df], axis = 1)
filtered_LDOS300mV_df.columns=["null","notnull"]

filtered_LDOS300mV_df
# -

# standard deviation 
sns.lineplot(data = filtered_LDOS300mV_df, x = "bias_mV", y = "null", errorbar =("sd"), label = 'low LDOS')
sns.lineplot(data = filtered_LDOS300mV_df, x = "bias_mV", y = "notnull", errorbar =("sd"), label = 'high LDOS')

LDOS_mask.isnull().plot()
