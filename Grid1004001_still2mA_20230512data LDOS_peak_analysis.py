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

# + [markdown] jp-MarkdownHeadingCollapsed=true
# # Experimental Conditions 
#
# ## **Sample:<font color= White, font size="5" > $FeTe_{0.55}Se_{0.45}$ (old) </font>**
#     * Cleaving: @ UHV Loadlock chamber, Room temp.
# ## **Tip: PtIr (from Unisoku)**
# ## Measurement temp: mK (40 mK)
# * SC Tc  (FeTe0.55Se0.45 ) ≈ 14.5 K 
# * STM Base Temperature : 40 mK 
# * Estimated electron temperature ~ 230mK 
# * PtIr Tip 
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
grid_xr = grid2xr(files_df[files_df.type=='3ds'].file_name.iloc[0])

# ### 1.2.1. Convert  to xarray

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

# +
grid_3D_gap =  grid_3D_Gap(grid_3D)
grid_3D_gap

grid_topo['gap_map_I'] = grid_3D_gap.gap_size_I
grid_topo['gap_map_LIX'] = grid_3D_gap.gap_size_LIX # add gap map to topo data
grid_2D = grid_topo # rename 2D xr data

grid_LDOS = grid_3D_gap[['LDOS_fb' ]]
grid_LDOS
# -

# ### 1.4 Topography view 

# +
# show topography image

isns.set_image(origin =  "lower")
isns.imshow(plane_fit_y_xr(grid_topo).topography, robust =  True, cmap= 'copper', perc = (2,98))
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

hv_bias_mV_slicing(grid_LDOS, ch = 'LDOS_fb').opts(clim = (0,5E-10))

# ####  1.5.2. Y or X slicing 

hv_XY_slicing(grid_LDOS, ch = 'LDOS_fb',slicing= 'X')#.opts(clim=(0, 1E-10))
#hv_XY_slicing(grid_3D,slicing= 'Y').opts(clim=(0, 1E-11))


# ### 1.6.Data Selection with HoloView
# * using Bounding Box or Lasso
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
dmap.opts(clim = (0,5E-10))*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box

hv_bbox_avg(grid_LDOS, bound_box= bound_box, ch ='LDOS_fb')

# #  <font color= orange > 2. gap & peak analysis (for Superconductor) </font>
#
#     * 2.1. Rotation ?
#         * move it other section? 
#
#     * 2.2. Smoothing 
#         * 2.2.1. Savatzky Golay smoothing 
#            * window polyoder setting 
#
#     * 2.3. Numerical derivative 
#         * use xr API 
#
#     * 2.4 finding plateau
#         * 2.3.1. prepare plateau detection function for Grid_xr, point 
#         * 2.3.2. prepare plateau detection function for Grid_xr
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
#

# ## 2.1.rotate 3D_xr
#
# * if target area  requires rotation, use rotate_3D_xr function 
# * thereis separate rotate_2D function 
# * based on XR API 
#
#

# +
## rotate 3D_xr # rotation in degree not radian 

grid_LDOS_rot = rotate_3D_xr(grid_LDOS,rotation_angle=0)
# -

grid_LDOS_rot

# +
#hv_bias_mV_slicing(grid_LDOS_rot, ch ='LDOS_fb').opts(clim= (0,1E-10))

# +
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

xr_data = grid_LDOS_rot
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
dmap.opts(clim = (0,5E-10))*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

bound_box


# +
# function for drawing bbox averaged STS 
# only after bbox setup & streaming bound_box positions


def hv_bbox_avg (xr_data, bound_box , ch = 'LIX_fb' ,slicing_bias_mV = 0):
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
    isns.set_image(origin = 'lower')
    # isns image directino setting 
    
    fig,axes = plt.subplots(nrows = 2,ncols = 2,figsize = (6,6))
    axs= axes.ravel()

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest"),robust = True,ax =  axs[0])

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

    isns.imshow(xr_data_bbox[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),ax =  axs[1],
                robust = True)
    sns.lineplot(x = "bias_mV",
                 y = ch, 
                 data = xr_data_bbox.to_dataframe(),
                 ax = axs[2])
    axs[3].remove()
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    fig.tight_layout()
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 


# -
grid_LDOS_rot_bbox,_ = hv_bbox_avg(grid_LDOS_rot, ch ='LDOS_fb',slicing_bias_mV=0.1 , bound_box = bound_box)

# ## 2.2 Smoothing 
# ### 2.2.1. Savatzky-Golay (SG) smoothig

# +
# grid_3D -> sg -> derivative 
grid_LDOS_rot

grid_LDOS_rot_sg = savgolFilter_xr(grid_LDOS_rot, window_length = 11, polyorder = 3)

# +

sns.lineplot( x = 'bias_mV', y = 'LDOS_fb', data=  grid_LDOS_rot.sel(X=5E-9,Y=5E-9, method = "nearest").LDOS_fb.to_dataframe(), label ="LDOS" )
sns.lineplot( x = 'bias_mV', y = 'LDOS_fb', data=  grid_LDOS_rot_sg.sel(X=5E-9,Y=5E-9, method = "nearest").LDOS_fb.to_dataframe(), label ="Savatzky-Golay smoothing" )

plt.show()
# -

# ## 2.3 Numerical derivative 
#     * Derivative + SG smoothing
#
# ### 2.3.1. SG + 1stderiv + SG + 2nd deriv + SG

# +

grid_LDOS_rot_sg_1deriv = grid_LDOS_rot_sg.differentiate('bias_mV')
grid_LDOS_rot_sg_1deriv_sg = savgolFilter_xr(grid_LDOS_rot_sg_1deriv, window_length = 11, polyorder = 3)
grid_LDOS_rot_sg_2deriv = grid_LDOS_rot_sg_1deriv_sg.differentiate('bias_mV')
grid_LDOS_rot_sg_2deriv_sg =  savgolFilter_xr(grid_LDOS_rot_sg_2deriv, window_length = 11, polyorder = 3)
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

plot_XYslice_w_LDOS(grid_LDOS_rot_sg, sliderX= sliderX, sliderY= sliderY, ch = 'LDOS_fb')

# #### 2.3.1.3. Test proper tolerance levels at XY point

fig,ax = plt.subplots(1,1)
grid_3D.I_fb.isel(X=43,Y=49).plot()
ax.set_xlim(-0.1,0.1)
ax.set_ylim(-0.2E-12,0.2E-12)
plt.show()

find_plateau_tolarence_values(grid_3D,tolerance_I=1E-11, tolerance_LIX=1E-12,  x_i = sliderX.value,     y_j = sliderY.value)
# with preset function 
plt.show()

# + [markdown] jp-MarkdownHeadingCollapsed=true
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
tolerance_LIX  = 1E-11
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

grid_LDOS_rot_sg_2deriv_sg_dks.LDOS_fb.isel(X=x_i,Y=y_j)

# +
grid_LDOS_rot_bbox =  grid_LDOS_rot.where ((grid_LDOS_rot.Y>0E-10)*(grid_LDOS_rot.Y<1E-8), drop= True).where ((grid_LDOS_rot.X>0E-10)*(grid_LDOS_rot.X<10.0E-8), drop= True)

grid_LDOS_rot_bbox_sg =  savgolFilter_xr(grid_LDOS_rot_bbox, window_length=11,polyorder=3 ).where ((grid_LDOS_rot_bbox.bias_mV>-2)*(grid_LDOS_rot_bbox.bias_mV<2), drop= True)
# -

grid_LDOS_rot_bbox_sg


grid_LDOS_rot_bbox_sg_pk  = grid3D_line_avg_pks( grid_LDOS_rot_bbox_sg ,ch_l_name ='LDOS_fb', average_in= 'Y',distance = 5, threshold = 1E-11) 
grid_LDOS_rot_bbox_sg_pk

# + jupyter={"source_hidden": true}
grid_LDOS_rot_bbox_sg_slct, grid_LDOS_rot_bbox_sg_df, grid_LDOS_rot_bbox_sg_pk_df, fig = grid_lineNpks_offset(grid_LDOS_rot_bbox_sg_pk,ch_l_name ='LDOS_fb', plot_y_offset= 2E-10,peak_LIX_min = 1E-10, legend_title = "X (nm)")
plt.show()
# -

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

# ## 3.1. Peak position detection

# ### 3.1.1. SG Smoothing & Numerical derivative
#

# 3.1.2. Rolling using XR 

grid_LDOS

# +
grid_LDOS_zm = grid_LDOS.where( (grid_LDOS.X >0E-7)&(grid_LDOS.X <0.5E-7)&(grid_LDOS.Y >0.7E-7) &(grid_LDOS.Y <1.2E-7), drop = True)


fig,axs = plt.subplots(ncols =2, figsize = (8,4))
isns.imshow (grid_LDOS.LDOS_fb.sel(bias_mV =  0), ax =axs[0], robust = True)
isns.imshow (grid_LDOS_zm.LDOS_fb.sel(bias_mV =  0), ax =axs[1], robust = True)
plt.show()

# +
grid_LDOS_sg = savgolFilter_xr(grid_LDOS_zm, window_length=11, polyorder=3)
grid_LDOS_1diff =  grid_LDOS_sg.differentiate('bias_mV')
grid_LDOS_1diff_sg = savgolFilter_xr(grid_LDOS_1diff, window_length=11, polyorder=3)
grid_LDOS_2diff =  grid_LDOS_1diff_sg.differentiate('bias_mV')
grid_LDOS_2diff_sg = savgolFilter_xr(grid_LDOS_2diff, window_length=11, polyorder=3)



# -

# ### 3.1.2. Find peaks in 2nd derivative

grid_LDOS_2diff_sg_dps = find_peaks_xr ( - grid_LDOS_2diff_sg, distance= 3)
grid_LDOS_2diff_sg_dps_pad = peak_pad (grid_LDOS_2diff_sg_dps)


hv_XY_slicing(grid_LDOS_sg, slicing='X' , ch='LDOS_fb').opts(clim = (0,5E-10))
#hv_bias_mV_slicing(grid_LDOS_2diff_sg_dps_pad.where(grid_LDOS_2diff_sg_dps_pad.X<5E-9).where(grid_LDOS_2diff_sg_dps_pad.Y>3E-9), ch='LDOS_fb')

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

#grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg.isel(Y= [9,10]) ,ch_l_name ='LDOS_fb', average_in= 'Y',distance = 5, threshold = 1E-11) 
grid_LDOS_sg_pk  = grid3D_line_avg_pks( grid_LDOS_sg.isel(X= [14,15]) ,ch_l_name ='LDOS_fb', average_in= 'X',distance = 5, threshold = 1E-11) 
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
grid_LDOS_zm


np.save('LDOS_pk_zm_mV.npy', grid_LDOS_zm.LDOS_pk_mV.where((grid_LDOS_zm.bias_mV> - 1.4)&(grid_LDOS_zm.bias_mV<1.4), drop = True).to_numpy())

grid_LDOS_zm.LDOS_pk_mV.where((grid_LDOS_zm.bias_mV>-1.4)&(grid_LDOS_zm.bias_mV<1.4), drop = True).to_numpy().sum()

# ### 3.1.3. Filtering Peaks only (bool)
#
# ## 3.2. Peak properties plot
#
# ### 3.2.1. find peaks2 find_peaks_prpt
#
# ### 3.2.2. Peak height at peak position apply LDOS value (peak Height)
#
# ### 3.2.3. Peak width plot
#
# ### 3.2.4. Peak promient plot
#
# ### 3.3. Peak and in gap states
#
# ## 3.3. Peaks clustering





peak_mV_3Dxr(grid_LDOS_rot)

# +
fig,ax =  plt.subplots(ncols=1, nrows= 1, figsize =  (6,5))

grid_3D_gap.LDOS_fb.isel(X = x_i,Y = y_j).plot(ax = ax)
sns.scatterplot(x= grid_3D_gap.bias_mV.isel( bias_mV = dps_2nd), y=grid_3D_gap.LDOS_fb.isel(X=x_i,Y=y_j, bias_mV = dps_2nd) )


# +
fig,ax =  plt.subplots(ncols=1, nrows= 1, figsize =  (6,5))

grid_3D_sg.LIX_fb.isel(X = x_i,Y = y_j).plot(ax = ax)
sns.scatterplot(x= grid_3D_sg.bias_mV.isel( bias_mV = dps_2nd), y=grid_3D_sg.LIX_fb.isel(X=x_i,Y=y_j, bias_mV = dps_2nd) )


# +
dps_2nd = grid_3D_sg_2deriv_sg_dks.LIX_fb_peaks.isel(X=x_i,Y=y_j)

grid_3D_sg_2deriv_sg_dks.LIX_fb.isel(X=x_i,Y=y_j, bias_mV= dps_2nd)

grid_3D_sg_2deriv_sg_dks.bias_mV.isel(bias_mV =  dps_2nd)

# +
fig,ax =  plt.subplots(ncols=1, nrows= 1, figsize =  (6,5))

grid_3D_sg_2deriv_sg.LIX_fb.isel(X = x_i,Y = y_j).plot(ax = ax)
sns.scatterplot(x= grid_3D_sg.bias_mV.isel( bias_mV = dps_2nd), y=grid_3D_sg_2deriv_sg.LIX_fb.isel(X=x_i,Y=y_j, bias_mV = dps_2nd) )

## I need to improve the peak position detection 
##  check the same thing with mK data 

# -

grid_3D_sg_pks= find_peaks_xr(grid_3D_sg, distance= 10)
grid_3D_sg_pks_pad = peak_pad( grid_3D_sg_pks)

grid_3D_sg_pks_pad #  원래식의  peak은 잘찾음 


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


grid_3D_sg_pks_mV = peak_mV_3Dxr(grid_3D_sg_pks)

# +
grid_3D_sg_pks_mV_LIX_fb_pk_mV = grid_3D_sg_pks_mV.LIX_fb* grid_3D_sg_pks_mV.LIX_fb_peaks_mV.to_numpy().astype(float)


np.save('LIX_fb_pk_mV.npy', grid_3D_sg_pks_mV_LIX_fb_pk_mV)
# -



# ## how to extract peak position 


grid_3D_sg_pks_mV

# +
LIX_peaks = grid_3D_sg_pks_mV.LIX_fb_peaks_mV * grid_3D_sg_pks_mV.LIX_fb
#I_peaks.to_numpy().astype('float64')
LIX_peaks_np = LIX_peaks.to_numpy().astype('float64')
LIX_peaks_np[LIX_peaks_np == 0] = np.nan #set 0 is nan

np.save('LIx_fb_peak_h.npy', LIX_peaks_np)
# -



grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1).values.tolist()
#  extract the isel bias_mV values 


grid_3D_sg_pks.I_fb.isel(X=1,Y=1).bias_mV.isin (grid_3D_sg_pks.I_fb.isel(X=1,Y=1).bias_mV[grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1).values.tolist()])

bias_mV_pks = grid_3D_sg_pks.I_fb.isel(X=1,Y=1).bias_mV.isel(bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1).values.tolist())
bias_mV_pks
# peak points 

I_fb_peaks_list = grid_3D_sg_pks.I_fb_peaks.values

I_fb_peaks_list[1,1]

grid_3D_sg_pks.I_fb.isel(X=1,Y=1).isel(bias_mV = I_fb_peaks_list[1,1])

# +
x_axis = grid_3D_sg_pks.X.size
y_axis = grid_3D_sg_pks.Y.size
I_fb_peaks_list = grid_3D_sg_pks.I_fb_peaks.values
# extract peaks index 

grid_3D_sg_pks.bias_mV[I_fb_peaks_list[1,1]]
# bias_mV value when peak exist 

# -

# with list comprehension each point by point 
# compare bias_mV 1D data and peak_bias_mV value (use 'isin') 
peaks_np = np.array([ grid_3D_sg_pks.bias_mV.isin(grid_3D_sg_pks.bias_mV[I_fb_peaks_list[x,y]]) for x in range(x_axis) for y in range(y_axis) ])
#make numpy 

grid_3D_sg_pks.I_fb.isel(X=1,Y=1, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=x_i,Y=y_j).to_numpy())

[grid_3D_sg_pks.I_fb.isel(X=x_i,Y=y_j, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=x_i,Y=y_j)) for x_i in range(x_axis)  for y_j in range(y_axis)]

grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1)



grid_3D_sg_pks.I_fb.isel(X=1,Y=1, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1))
# peak Height values 

# +
# check peak height value is in or not
# -

A = grid_3D_sg_pks.I_fb.isel(X=1,Y=1).isin(grid_3D_sg_pks.I_fb.isel(X=1,Y=1, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1))) 

B = grid_3D_sg_pks.I_fb.isel(X=1,Y=1)

(A * B).plot()

# +
I_peaks = grid_3D_sg_pks_mV.I_fb_peaks_mV * grid_3D_sg_pks_mV.I_fb
#I_peaks.to_numpy().astype('float64')
I_peaks_np = I_peaks.to_numpy().astype('float64')
I_peaks_np[I_peaks_np == 0] = np.nan #set 0 is nan

np.save('I_fb_peak_h.npy', I_peaks_np)

# +
LIX_peaks = grid_3D_sg_pks_mV.LIX_fb_peaks_mV * grid_3D_sg_pks_mV.LIX_fb
#I_peaks.to_numpy().astype('float64')
LIX_peaks_np = LIX_peaks.to_numpy().astype('float64')
LIX_peaks_np[LIX_peaks_np == 0] = np.nan #set 0 is nan

np.save('LIx_fb_peak_h.npy', I_peaks_np)
# -

LIX_peaks_np

grid_3D_sg_pks.I_fb.isel(X=1,Y=1, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1))*grid_3D_sg_pks.I_fb.isel(X=1,Y=1).isin(grid_3D_sg_pks.I_fb.isel(X=1,Y=1, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1)))


def peak_height_3Dxr(xr_data): 
    #after find_peaks_xr 
    xrdata_prcssd = xr_data.copy(deep = True)
    print('After peak finding in STS, marking in the 3D data')
    x_axis = xr_data.X.size
    y_axis = xr_data.Y.size
    bias_mV_axis = xr_data.bias_mV.size
    for data_ch in xr_data:
        if '_peaks' in data_ch:
            pass
        # do nothing for channels with_peaks information  
        else: 
            xrdata_prcssd[data_ch+'_peaks_mV'] = xr.DataArray (
                np.array([ grid_3D_sg_pks.I_fb.isel(X=x_i,Y=y_j, bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=x_i,Y=y_j))
                          for x_i in range(x_axis)  
                          for y_j in range(y_axis)], dtype = object ).reshape(x_axis,y_axis,bias_mV_axis),
                dims=["X", "Y","bias_mV"],
                coords={"X": xr_data.X, "Y": xr_data.Y,  "bias_mV": xr_data.bias_mV}) 
    return xrdata_prcssd



grid_3D_sg_pks_mV = peak_mV_3Dxr(grid_3D_sg_pks)

 grid_3D_sg_pks_mV.LIX_fb_peaks_mV.to_numpy().astype(int)

np.save('LIX_fb_peak.npy',  grid_3D_sg_pks_mV.LIX_fb_peaks_mV.to_numpy().astype(int))


grid_3D_sg_pks['I_fb'].isel(X=12,Y=12).bias_mV.isel(bias_mV = grid_3D_sg_pks['I_fb'+'_peaks'].isel(X=12,Y=12).values.tolist())

grid_3D_sg_pks

grid_3D_sg_pks_mV = peak_mV_3Dxr(grid_3D_sg_pks)
grid_3D_sg_pks_mV

grid_3D_sg_pks_mV

 xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values)[1] 
                          for x in range(x_axis)  
                          for y in range(y_axis)], dtype = object ).reshape(x_axis,y_axis),
                dims=["X", "Y"],
                coords={"X": xrdata.X, "Y": xrdata.Y})   

grid_3D_sg_pks

# ## in-gap state peak --> plateau  + peak 


grid_3D_sg_pks.I_fb.isel(X=1,Y=1).isel(bias_mV = grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1).values.tolist())

# grid_3D_sg_pks.I_fb.bias_mV.isin(grid_3D_sg_pks.I_fb_peaks.isel(X=1,Y=1).values.tolist())


# +
# extract plateau regions from data. 

grid_3D_sg["I_fb"+'_plateau'] = abs(grid_3D_sg.I_fb.isel(X=0,Y=0)) <= tolerance_I
grid_3D_sg["I_fb"+'_dIdV_plateau'] = abs(grid_3D_sg_1deriv_sg.I_fb.isel(X=0,Y=0)) <= tolerance_dIdV
grid_3D_sg["I_fb"+'_d2IdV2_plateau'] = abs(grid_3D_sg_2deriv_sg.I_fb.isel(X=0,Y=0)) <= tolerance_d2IdV2

grid_3D_sg["LIX_fb"+'_plateau'] = abs(grid_3D_sg.LIX_fb.isel(X=0,Y=0)) <= tolerance_LIX
grid_3D_sg["LIX_fb"+'_dIdV_plateau'] = abs(grid_3D_sg_1deriv_sg.LIX_fb.isel(X=0,Y=0)) <= tolerance_dLIXdV
grid_3D_sg["LIX_fb"+'_d2IdV2_plateau'] = abs(grid_3D_sg_2deriv_sg.LIX_fb.isel(X=0,Y=0)) <= tolerance_d2LIXdV2

# grid_3D_sg*_**_plateau ; bools T or F


# -

def find_peak_properties_xr(xrdata): 
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
                    np.array([ find_peaks(xrdata[data_ch].isel(X = x).values)
                              for x in range(x_axis)], dtype = object )[:,1],
                dims=["X"],
                coords={"X": xrdata.X})
            
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size

                #print(xrdata_prcssd[data_ch])

                xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                    np.array([ find_peaks(xrdata[data_ch].isel(Y = y).values)
                              for y in range(y_axis)], dtype = object )[:,1],
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
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values)[1] 
                          for x in range(x_axis)  
                          for y in range(y_axis)], dtype = object ).reshape(x_axis,y_axis),
                dims=["X", "Y"],
                coords={"X": xrdata.X, "Y": xrdata.Y})         
        elif len(xrdata[data_ch].dims) == 1:
            if 'bias_mV' in xrdata.dims: 
                for data_ch in xrdata: 
                    xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (find_peaks (xrdata[data_ch]))
        else : pass
    return xrdata_prcssd
#grid_2D_sg_pks = find_peaks_xr(grid_2D_sg)

grid_3D_sg_pk_prps = find_peak_properties_xr(grid_3D_sg)

import scipy as sp
peaks = sp.signal.find_peaks(grid_3D_sg['I_fb'].isel(X = 1, Y = 1).values)[0]

sp.signal.peak_prominences(grid_3D_sg['I_fb'].isel(X = 1, Y = 1).values,peaks)

grid_3D_sg_pk_prps.I_fb_peaks.isel(X=1,Y=1)


# grid_3D -> sg -> derivative 
grid_3D_sg = savgolFilter_xr(grid_3D, window_length = 15, polyorder = 3)
grid_3D_sg_1deriv = grid_3D_sg.differentiate('bias_mV')
grid_3D_sg_1deriv_sg = savgolFilter_xr(grid_3D_sg_1deriv, window_length = 15, polyorder = 3)
grid_3D_sg_2deriv = grid_3D_sg_1deriv_sg.differentiate('bias_mV')
grid_3D_sg_2deriv_sg =  savgolFilter_xr(grid_3D_sg_2deriv, window_length = 15, polyorder = 3)


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

grid_LDOS['LDOS_fb_roll'] = grid_LDOS.LDOS_fb.rolling(X =1,Y = 1, bias_mV= 1, min_periods =1).mean()

# +
fig,axes = plt.subplots (ncols=2, nrows=2, figsize = (6,6))
axs = axes.ravel()
grid_LDOS.LDOS_fb_roll.isel(bias_mV =1).plot(ax = axs[0])
grid_LDOS.LDOS_fb.isel(bias_mV =1).plot(ax = axs[1])

grid_LDOS.LDOS_fb_roll.isel(X=1, Y=1).plot(ax = axs[2])
grid_LDOS.LDOS_fb.isel(X=1, Y=1).plot(ax = axs[3])

plt.show()
# -


# ### I peak detection 
# * 1. I peak  =  dIdV plateau & dI/DV Pos
# * 2. I peak = d2IdV2 local min  ==> -d2IdV2 peak position 
#
# ### LDOS peak detection 
#
# * 1. LIX peak detection 
# * 2. dLIXdV plateau & dLIX/dV2 Pos
# * 4. LIX peak = d2IdV2 local min  ==> -d2IdV2 peak position 
#
# #### make a function 
#
# def find_plateau (xrdata, tolerance_I = 1E-10, tolerance_LIX= 1E-11): 
#
#
# xr_data 에 대해서 모든  point 에 대해서 plateau 를 찾기 
# tolerance  는 각각 I 와 LIX 기준 다르게 
#
# 1차 미분값을 기준으로 plateau 잡기 
#
#

#
#
grid_3D_sg

grid_3D_gap = grid_3D_Gap(grid_3D)
# assign gap from STS
grid_3D_gap

# # <font color= orange > 2. Visualization with Holoview </font>

# ## 2-1. ROI (Ara) selection

# + [markdown] jp-MarkdownHeadingCollapsed=true
# ### 2-1.1 Bound Box
# * using Bounding Box 
# * live 
# -

# ### 2-1-1 bokeh plot & Bound box selection + get point selection

# +
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
          frame_width = 400,
          aspect = 'equal')#.relabel('XY plane slicing: ')

grid_channel_hv_image  = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0)).relabel('for BBox selection : ')

bbox_points = hv.Points(grid_channel_hv_image).opts(frame_width = 400,
                                                    color = 'k',
                                                    aspect = 'equal',
                                                    alpha = 0.1,                                   
                                                    tools=['box_select'])

bound_box = hv.streams.BoundsXY(source = bbox_points,
                                bounds=(0,0,0,0))
dmap*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

# ### 2-1-2 averaged STS of the selected Bound Box region
#
#
# #### 2-1-2.1 draw 3 plots with isns

# +
# slicing bias_mV = 5 mV
slicing_bias_mV = 5
#bound_box.bounds
x_bounds_msk = (grid_3D.X > bound_box.bounds[0] ) & (grid_3D.X < bound_box.bounds[2])
y_bounds_msk = (grid_3D.Y > bound_box.bounds[1] ) & (grid_3D.Y < bound_box.bounds[3])

grid_3D_bbox = grid_3D.where (grid_3D.X[x_bounds_msk] + grid_3D.Y[y_bounds_msk])

fig,axs = plt.subplots (nrows = 1,
                        ncols = 3,
                        figsize = (12,4))

isns.imshow(grid_3D.I_fb.isel(bias_mV = -50 ),
            ax =  axs[0],
            robust = True)
# add rectangle for bbox 

isns.imshow(grid_3D_bbox.I_fb.isel(bias_mV = -50 ),
            ax =  axs[1],
            robust = True)
sns.lineplot(x = "bias_mV",
             y = "LIX_fb", 
             data = grid_3D_bbox.to_dataframe(),
             ax = axs[2])
plt.savefig('grid011_bbox)p.png')
plt.show()

# plot STS at the selected points 
# use the seaborn (confident interval : 95%) 
# sns is figure-level function 


# -

# #### 2-1-2.2 draw 3 plots with hv plots  
# * curve is not clear... 
# * use the bounds as a mark. 
#

# +
# bias_mV slicing
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')
#######################
# map with BBOX       #   
#######################

dmap_hv_wBbox = dmap.opts(frame_width = 200,)*hv.Bounds( bound_box.bounds ).opts(opts.Bounds(color='orange', line_width=6))



###########################
# BBOX separate plot      #   
###########################


grid_ch_bbox_hv = hv.Dataset(grid_3D_bbox.I_fb)
dmap_plane  = ["X","Y"]
dmap_bbox = grid_ch_bbox_hv.to(hv.Image,
                          kdims = dmap_plane,
                          dynamic = True, cmap = 'bwr')
# dmap size 
#frame_pixel_size =  10
#dmap_bbox#.opts(frame_width = len(grid_3D_bbox.X)*frame_pixel_size, frame_height = len(grid_3D_bbox.Y)*frame_pixel_size)


##########################
## bbox avg plot with hv #
##########################
grid_ch_bbox_mean = hv.Dataset(grid_3D_bbox.LIX_fb.mean(dim = ["X","Y"])).to(hv.Curve)
# simple plot 

dmap_hv_wBbox+dmap_bbox+ grid_ch_bbox_mean


# -

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
                         ax = ax)

    sns.scatterplot(data = ch_l_name_pks_df,
                            x ='bias_mV',
                            y = ch_l_name+'_offset',
                            palette ="rocket",
                            hue = xr_data_l_pks.line_direction,
                    s =0,
                            ax = ax)
    # legend control!( cut the handles 1/2)
    ax.set_xlabel('Bias (mV)')   
    #ax.set_ylabel(ch_l_name+'_offset')   
    ax.set_ylabel('LDOS')   
    handles0, labels0 = ax.get_legend_handles_labels()
    labels1 = [ str(float(label)*10) for label in labels0[:int(len(labels0)//2)] ] 
    # convert the line length as nm  
    ax.legend(handles0[:int(len(handles0)//2)],
              labels1, title = legend_title)
    # use the half of legends (line + scatter) --> use lines only
    #plt.show()
    ax.legend().remove()
    #ax.xlim([25, 50])
    
    return xr_data_l_pks_ch_slct, ch_l_name_df, ch_l_name_pks_df, fig


grid_3D_bbox

# +
grid_3D_bbox_pk = grid3D_line_avg_pks (grid_3D_bbox,average_in= 'Y', ch_l_name= 'LIX_fb')
#grid_3D_crop_pk
xr_data_l_pks_ch_slct, ch_l_name_df, ch_l_name_pks_df, fig = grid_lineNpks_offset(grid_3D_bbox_pk,peak_LIX_min=2E-14,plot_y_offset=5E-10)


fig.savefig('grid0T_still2mA_10004001_l_pf.png')
# -

#grid_3D_gap
grid_3D_gap.CBM_LIX_mV.plot()


# # <font color= orange > 3. Signal Treatments </font>
#

# ## Smoothing 
# ### Savatzky-Golay smoothig

import panel as pn
import panel.widgets as pnw
import ipywidgets as ipw

# +

grid_3D_sg = savgolFilter_xr(grid_3D, window_length = 7, polyorder = 3)
## savatzk-golay filtered 

# -

# ## Numerical Derivatives
# ### xarray APIs

# grid_3D -> sg -> derivative 
grid_3D_sg = savgolFilter_xr(grid_3D, window_length = 21, polyorder = 3)
grid_3D_sg_1deriv = grid_3D_sg.differentiate('bias_mV')
grid_3D_sg_1deriv_sg = savgolFilter_xr(grid_3D_sg_1deriv, window_length = 21, polyorder = 3)
grid_3D_sg_2deriv = grid_3D_sg_1deriv_sg.differentiate('bias_mV')

grid_3D_sg_2deriv
np.save ("grid_3D_sg_2deriv_LIX_unit_cal.npy", grid_3D_sg_2deriv.LIX_unit_calc.values)

LIX_unit_calc_curve = hv.Curve(grid_3D_sg.isel(X = sliderX.value, Y = sliderY.value).LIX_unit_calc).opts(axiswise=True, ylabel='LDOS (A/V)', title = 'LDOS')
d_LIX_unit_calc_curve_dV =  hv.Curve(grid_3D_sg_1deriv.isel(X = sliderX.value, Y = sliderY.value).LIX_unit_calc).opts(axiswise=True, ylabel='LDOS (A/V)', title = 'd(LDOS)/dV')
d2_LIX_unit_calc_curve_dV2 = hv.Curve(grid_3D_sg_2deriv.isel(X = sliderX.value, Y = sliderY.value).LIX_unit_calc).opts(axiswise=True, ylabel='LDOS (A/V)', title = 'd2(LDOS)/dV2')
dmap*points + LIX_unit_calc_curve + d_LIX_unit_calc_curve_dV + d2_LIX_unit_calc_curve_dV2

# ## find peaks 
# * function find_peaks_xr
#
#
# ## Handling peaks with different numbers
#     * use the np.pad & count the max number of peak
#     * fill the np.nan the empty
#     * function : peak_pad
#
#
#

# +
grid_3D_sg_pks = find_peaks_xr(grid_3D_sg)
#grid_3D_sg_pks.LIX_fb_peaks

grid_3D_sg_pks_pad = peak_pad(grid_3D_sg_pks)
grid_3D_sg_pks_pad

# -

# ### counting peaks for after derivatives
# * original data : grid_3D
# * find gap data : grid_3D_gap
# * smoothing data : grid_3D_gap_sg
# * derivative data : grid_3D_gap_sg_1deriv, grid_3D_gap_sg_2deriv
# * find_peaks : grid_3D_sg_1deriv_sg_pks
# * find_peaks& padding : grid_3D_sg_1deriv_sg_pks_pad
#
# ### LDOS in data
# * grid_3D_gap_sg
# ### for the peaks in LDOS
# * grid_3D_sg_pks_pad
# ### d(LDOS)/dV IETS
# * grid_3D_sg_1deriv_sg
# * peaks & dips in IETS : d2I/dV2 values
# * grid_3D_sg_1deriv_sg_pks_pad
# * grid_3D_sg_1deriv_sg_dps_pad
#
# ### To find LDOS peaks 
# *  2nd derivative LDOS dips! (for acurate detection)
# * grid_3D_sg_2deriv_sg
#     * grid_3D_sg_2deriv_sg_pks_pad
#     * grid_3D_sg_2deriv_sg_dps_pad

# +
# grid_3D -> sg -> derivative 
grid_3D_sg = savgolFilter_xr(grid_3D, window_length = 31, polyorder = 3)
grid_3D_sg_1deriv = grid_3D_sg.differentiate('bias_mV')
grid_3D_sg_1deriv_sg = savgolFilter_xr(grid_3D_sg_1deriv, window_length = 31, polyorder = 3)
grid_3D_sg_2deriv = grid_3D_sg_1deriv_sg.differentiate('bias_mV')

# d(LDOS)dV pks & dps
grid_3D_sg_1deriv_sg_pks = find_peaks_xr(grid_3D_sg_1deriv_sg)
grid_3D_sg_1deriv_sg_pks_pad = peak_pad(grid_3D_sg_1deriv_sg_pks)

grid_3D_sg_1deriv_sg_dps = find_peaks_xr(-1* grid_3D_sg_1deriv_sg)
grid_3D_sg_1deriv_sg_dps_pad = peak_pad(grid_3D_sg_1deriv_sg_dps)

# d2(LDOS)dV2 pks & dps

grid_3D_sg_2deriv_sg =  savgolFilter_xr(grid_3D_sg_2deriv)
grid_3D_sg_2deriv_sg_pks = find_peaks_xr(grid_3D_sg_2deriv_sg)
grid_3D_sg_2deriv_sg_pks_pad = peak_pad(grid_3D_sg_2deriv_sg_pks)

grid_3D_sg_2deriv_sg_dps = find_peaks_xr(-1* grid_3D_sg_2deriv_sg)
grid_3D_sg_2deriv_sg_dps_pad = peak_pad(grid_3D_sg_2deriv_sg_dps)
# -

grid_3D_sg_2deriv_sg_dps_pad.isel(peaks=0).I_fb_peaks_pad.plot()
# 첫번째 peak 만 골라내서 그리기.



# +
# peak 들 가운데 (0-300 사이) 가운데 가장 가까운것들만 모으기 

#pd.DataFrame(np.isin(grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks.values,[149,151])).sum()


# list 로 꺼내는법 

grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks.isel(X=0, Y=0).values.tolist().tolist()


# -

TEST = grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks_pad.isel(X=0, Y=0).to_numpy()
TEST

 grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks_pad.to_numpy()

grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks.to_numpy()

np.save("test0.npy",grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks_pad.values)

np.save("test.npy",grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks_pad.isin([150]).values)

grid_3D_sg_2deriv_sg_dps_pad['LIX_unit_calc_peaks_v'] = grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc.isel(bias_mV=0)
# make a null space 


# +
X_len  = len(grid_3D_sg_2deriv_sg_dps_pad.X)
Y_len  = len(grid_3D_sg_2deriv_sg_dps_pad.Y)

for x_i in range(X_len) for y_j in range(Y_len) 
# -

grid_3D_sg_2deriv_sg_dps_pad['LIX_unit_calc_peaks_v'].map

[grid_3D_sg_2deriv_sg_dps_pad['LIX_unit_calc_peaks_v'].isel(X= x_i, Y = y_j) for x_i in range(X_len) for y_j in range(Y_len) ]

# +
grid_3D_sg_2deriv_sg_dps_pad['LIX_unit_calc_peaks_v']

=
grid_3D_sg_2deriv_sg_dps_pad
#grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks.isel(X=0, Y=0).values.ravel()
# -

grid_3D_sg_2deriv_sg_dps_pad.LIX_unit_calc_peaks.values

# ### 2-2-1 bokeh plot & Lasso Selection + get point_lists





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

fig, axs = plt.subplots(ncols = 2, nrows = 1, figsize = (8,4))

grid_3D_slct_pts.I_fb.plot(ax = axs[0], robust = True) 

sns.lineplot(x = "bias_mV",            
             y = "LIX_fb", 
             data = grid_3D_slct_pts.to_dataframe(),
             ax = axs[1])
plt.show
#grid_3D_slct_pts
#
#sns.relplot(x="bias_mV",
#            y="LIX_fb", 
#            kind="line",
#            data=grid_3D_slct_pts.to_dataframe())
# check. sn.relplot is  figure-level function
# -

# ### Lasso selected points

# +
#slct_pts
pts = grid_channel_hv_points.iloc[slct_pts.index].dframe().set_index(['X', 'Y'])

pts_xr = xr.Dataset.from_dataframe(pts)


## Lasso selected points 

grid_3D_slct_pts = xr.combine_by_coords ([grid_3D, pts_xr], compat = 'override', join = 'outer')
#y_pts = points.iloc[slct_pts.index].dframe().Y
#grid_3D.sel(X = x_pts,Y = y_pts)
#grid_3D.I_fb.isel(bias_mV = 0).plot()

fig, axs = plt.subplots(ncols = 2, nrows = 1, figsize = (8,4))

grid_3D_slct_pts.I_fb.T.plot(ax = axs[0], robust = True) 

sns.lineplot(x = "bias_mV",            
             y = "LIX_fb", 
             data = grid_3D_slct_pts.to_dataframe(),
             ax = axs[1])
plt.show
#grid_3D_slct_pts
#
#sns.relplot(x="bias_mV",
#            y="LIX_fb", 
#            kind="line",
#            data=grid_3D_slct_pts.to_dataframe())
# check. sn.relplot is  figure-level function

# +
## Lasso not - selected points 
grid_3D_not_slct_pts = grid_3D.where(grid_3D_slct_pts.I_fb.isnull())
#grid_3D_not_slct_pts

fig, axs = plt.subplots(ncols = 2, nrows = 1, figsize = (8,4))

grid_3D_not_slct_pts.LIX_fb.isel(bias_mV= 0).plot(ax = axs[0], robust = True) 

sns.lineplot(x = "bias_mV",            
             y = "LIX_fb", 
             data = grid_3D_not_slct_pts.to_dataframe(),
             ax = axs[1])
plt.show
#grid_3D_slct_pts
#
# -

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

# ### 2-1-2 averaged STS of the selected Bound Box region
#
#
# #### 2-1-2.1 draw 3 plots with isns

# +
#1.6. Bound Box selectin based on hv slicing 

 ## function 
    
# -



# ### 2-1-1 bokeh plot & Bound box selection + get point selection

# +
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
          frame_width = 400,
          aspect = 'equal')#.relabel('XY plane slicing: ')

grid_channel_hv_image  = hv.Dataset(grid_3D.I_fb.isel(bias_mV = 0)).relabel('for BBox selection : ')

bbox_points = hv.Points(grid_channel_hv_image).opts(frame_width = 400,
                                                    color = 'k',
                                                    aspect = 'equal',
                                                    alpha = 0.1,                                   
                                                    tools=['box_select'])

bound_box = hv.streams.BoundsXY(source = bbox_points,
                                bounds=(0,0,0,0))
dmap*bbox_points


## hv.DynamicMap( 뒤에는 function 이 와야함), streams  로 해당 영역을 지정.( or 함수의 입력정보 지정) 
# averaged curve 를 그리기 위해서 해당영역을  xr  에서 average  해야함.. 
# curve 의 area 로 error bar도 같이 그릴것.. 


# -

# ### 2-1-2 averaged STS of the selected Bound Box region
#
#
# #### 2-1-2.1 draw 3 plots with isns

# +
# slicing bias_mV = 5 mV
slicing_bias_mV = 5
#bound_box.bounds
x_bounds_msk = (grid_3D.X > bound_box.bounds[0] ) & (grid_3D.X < bound_box.bounds[2])
y_bounds_msk = (grid_3D.Y > bound_box.bounds[1] ) & (grid_3D.Y < bound_box.bounds[3])

grid_3D_bbox = grid_3D.where (grid_3D.X[x_bounds_msk] + grid_3D.Y[y_bounds_msk])

fig,axs = plt.subplots (nrows = 1,
                        ncols = 3,
                        figsize = (12,4))

isns.imshow(grid_3D.I_fb.isel(bias_mV = -50 ),
            ax =  axs[0],
            robust = True)
# add rectangle for bbox 

isns.imshow(grid_3D_bbox.I_fb.isel(bias_mV = -50 ),
            ax =  axs[1],
            robust = True)
sns.lineplot(x = "bias_mV",
             y = "LIX_fb", 
             data = grid_3D_bbox.to_dataframe(),
             ax = axs[2])
plt.savefig('grid011_bbox)p.png')
plt.show()

# plot STS at the selected points 
# use the seaborn (confident interval : 95%) 
# sns is figure-level function 


# -

bound_box.bounds[1]

# +
fig,axs = plt.subplots (nrows = 1,
                        ncols = 1,
                        figsize = (12,4))

isns.imshow(grid_3D.I_fb.isel(bias_mV = -50 ),
            ax =  axs,
            robust = True)

from matplotlib.patches import Rectangle
axs.add_patch(Rectangle((1,1),
                        4,
                        6,
                        edgecolor = 'pink',
                        facecolor = 'blue',
                        fill=True,
                        lw=5))

"""
axs.add_patch(Rectangle((bound_box.bounds[0], bound_box.bounds[1]),
                        bound_box.bounds[2]-bound_box.bounds[0],
                        bound_box.bounds[3]-bound_box.bounds[1],
                        edgecolor = 'pink',
                        facecolor = 'blue',
                        fill=True,
                        lw=5))"""


# +
x_i = sliderX
y_j = sliderY



# Fixed value from slider XY
sliderX_v = grid_3D.X[sliderX.value].values
sliderY_v = grid_3D.Y[sliderY.value].values
# add HLine & VLines # H line is for Y & V line is for X!! 
dmap_slideXY = dmap *hv.VLine(sliderX_v).opts(
    color = 'green', line_width = 4, alpha =0.5)*hv.HLine(
    sliderY_v).opts(
    color = 'yellow', line_width = 4, alpha =0.5)
grid_3D_selXY= grid_3D.isel(X = sliderX.value, Y= sliderY.value)
grid_3D_I_plot = hv.Curve(grid_3D_selXY.I_fb).relabel('I_fb')
grid_3D_LIX_plot = hv.Curve(grid_3D_selXY.LIX_fb).relabel('LIX_fb')
pn.Column(pn.Row(interact(lambda x:  grid_3D.X[x].values, x =sliderX), interact(lambda y: grid_3D.Y[y].values, y =sliderY)),dmap_slideXY)



# -


def plot_XYslice_w_LDOS (xr_data, data_channel='LIX_fb'):

    plt.style.use('default')
    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[data_channel]

    xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[data_channel]
    sliderX_v = xr_data.X[sliderX.value].values
    sliderY_v = xr_data.Y[sliderY.value].values
    slicing_bias_mV = 5

    # bias_mV slicing
    fig,axes = plt.subplots (nrows = 2,
                            ncols = 2,
                            figsize = (6,6))
    axs = axes.ravel()

    isns.imshow(xr_data.LIX_fb.sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    xr_data_Vline_profile.plot(ax = axs[1],robust = True)#, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max())
    xr_data_Hline_profile.T.plot(ax = axs[2],robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())

    xr_data.LIX_fb.isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[3])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    return



def plot_XYslice_w_LDOS (xr_data, data_channel='LIX_fb'):

    plt.style.use('default')
    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[data_channel]

    xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[data_channel]
    sliderX_v = xr_data.X[sliderX.value].values
    sliderY_v = xr_data.Y[sliderY.value].values
    slicing_bias_mV = 5

    # bias_mV slicing
    fig,axes = plt.subplots (nrows = 2,
                            ncols = 2,
                            figsize = (6,6))
    axs = axes.ravel()

    isns.imshow(xr_data.LIX_fb.sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    xr_data_Vline_profile.plot(ax = axs[1],robust = True)#, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max())
    xr_data_Hline_profile.T.plot(ax = axs[2],robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())

    xr_data.LIX_fb.isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[3])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    return



def plot_XYslice_w_LDOS (xr_data, sliderX, sliderY, ch ='LIX_fb', slicing_bias_mV = 2):
    
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
                            ncols = 2,
                            figsize = (6,6))
    axs = axes.ravel()

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    xr_data_Vline_profile.plot(ax = axs[1],robust = True)#, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max())
    xr_data_Hline_profile.T.plot(ax = axs[2],robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())

    xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[3])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    
    return plt.show()


# + [markdown] jp-MarkdownHeadingCollapsed=true
# ### 2-1.1 Bound Box
# * using Bounding Box 
# * live 
# -

bound_box, dmpa_bbox  = hv_bbox(grid_3D)

np.abs((grid_3D.X-bound_box.bounds[0]).to_numpy()).argmin()

# +
# slicing bias_mV = 5 mV
slicing_bias_mV = -0.5
#bound_box.bounds
x_bounds_msk = (grid_3D.X > bound_box.bounds[0] ) & (grid_3D.X < bound_box.bounds[2])
y_bounds_msk = (grid_3D.Y > bound_box.bounds[1] ) & (grid_3D.Y < bound_box.bounds[3])

grid_3D_bbox = grid_3D.where (grid_3D.X[x_bounds_msk] + grid_3D.Y[y_bounds_msk])

fig,axs = plt.subplots (nrows = 1,
                        ncols = 3,
                        figsize = (12,4))

isns.imshow(grid_3D.I_fb.sel(bias_mV = slicing_bias_mV, method="nearest" ),
            ax =  axs[0],
            robust = True)

# add rectangle for bbox 
from matplotlib.patches import Rectangle
# find index value of bound box 

Bbox_x0 = np.abs((grid_3D.X-bound_box.bounds[0]).to_numpy()).argmin()
Bbox_y0 = np.abs((grid_3D.Y-bound_box.bounds[1]).to_numpy()).argmin()
Bbox_x1 = np.abs((grid_3D.X-bound_box.bounds[2]).to_numpy()).argmin()
Bbox_y1 = np.abs((grid_3D.Y-bound_box.bounds[3]).to_numpy()).argmin()
# substract value, absolute value with numpy, argmin returns index value

# when add rectangle, add_patch used index 
axs[0].add_patch(Rectangle((Bbox_x0 , Bbox_y0 ), 
                           Bbox_x1 -Bbox_x0 , Bbox_y1-Bbox_y0,
                           edgecolor = 'pink',
                           fill=False,
                           lw=2,
                           alpha=0.5))

isns.imshow(grid_3D_bbox.I_fb.sel(bias_mV = slicing_bias_mV, method="nearest" ),
            ax =  axs[1],
            robust = True)
sns.lineplot(x = "bias_mV",
             y = "LIX_fb", 
             data = grid_3D_bbox.to_dataframe(),
             ax = axs[2])
#plt.savefig('grid011_bbox)p.png')
plt.show()

# plot STS at the selected points 
# use the seaborn (confident interval : 95%) 
# sns is figure-level function 

