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

# # SPMpy 
# * Authors : Dr. Jewook Park at CNMS, ORNL
#     * Center for Nanophase Materials Sciences (CNMS), Oak Ridge National Laboratory (ORNL)
#     * email :  parkj1@ornl.gov
#         
# > **SPMpy** is a python package to analysis scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques, and utilzes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools available in the [scientific python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
#
# >  **SPMpy** is an open-source project. (Github: https://github.com/Jewook-Park/SPMPY )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 
# # SPMpy data analysis function 
#
# * To use SPMpy functions, SPM data() need to be converted as PANDAS DataFrame or Xarray DataSet. 
#
# > * check **SPMpy_fileloading_functions** first.

# # 0.  Import modules

# +

import os
import glob
import numpy as np
import pandas as pd
import scipy as sp
from warnings import warn
from scipy import signal

import math
import skimage
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import seaborn as sns

#from SPMpy_2D_data_analysis_funcs import files_in_folder,img2xr,grid2xr,gridline2xr,gwy_img2df,gwy_df_ch2xr


# some packages may be yet to be installed
try:
     from pptx import Presentation
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named Presentation')
    # !pip install python-pptx  
    from pptx import Presentation
    from pptx.util import Inches, Pt

try:
    import nanonispy as nap
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named nanonispy')
    # !pip install nanonispy
    import nanonispy as nap

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named seaborn-image')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install --upgrade seaborn-image    
    import seaborn_image as isns

try:
    import xarray as xr
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xarray')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install xarray 
    import xarray as xr
    
try:
    import xrft
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xrft')
    # !pip install xrft 
    import xrft

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named seaborn-image')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install --upgrade seaborn-image    
    import seaborn_image as isns


# -

# # Grid data analysis functions
#

# # find the gap region 
# * gap size 
#     * based on measurement error (I limit ~ 1E-11pA) or (Lock-in resolution limnit ~ 1E-11 pA ) find the gapped region in spectroscopy 
# * calibrated LDOS 
#     * convert the LIX values (from Lockin) as dI/dV unit [A/V] 
#     * check the LIX offest value based on calibrated dI/dV at I=0
#     
#

# +
def grid_3D_Gap(grid_3D, I_0_pA = 1E-13 ,LIX_0_pA = 1E-14):
    grid_3D_prcssd = grid_3D.copy(deep = True)
    # I_fb values less than I_min_A => zero value 
    I_0_pA = I_0_pA

    gap_mask_I  = np.abs(grid_3D.I_fb) < I_0_pA
    gap_I =  grid_3D.I_fb.where(gap_mask_I)

    CBM_I_mV = grid_3D.bias_mV.where(gap_mask_I).max('bias_mV') # CBM_I_mV
    VBM_I_mV = grid_3D.bias_mV.where(gap_mask_I).min('bias_mV') # VBM_I_mV
    # map of the CBM&VBM energy (bias_mV)   
    gap_size_I =  (CBM_I_mV - VBM_I_mV ) 
    # from VBM to CBM energy gap size in mV ( index differnce * bias_mV step size) 

    grid_3D_prcssd['CBM_I_mV'] = CBM_I_mV
    grid_3D_prcssd['VBM_I_mV'] = VBM_I_mV
    grid_3D_prcssd['gap_size_I'] = gap_size_I
    ###############################################

    grid_3D['dIdV'] = grid_3D.differentiate(coord = 'bias_mV').I_fb
    # numerically calculated dI/dV from I_fb
    LIX_ratio = grid_3D.dIdV / grid_3D.LIX_fb
       
    grid_3D['LIX_unit_calc'] = np.abs( LIX_ratio.mean())*grid_3D.LIX_fb
    # LIX unit calibration 
    # pA unit : lock-in result 
    # LIX_unit_calc : calibrated as [A/V] unit for dI/dV
    
    
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
    grid_3D_prcssd['CBM_LIX_mV'] = grid_3D.bias_mV.where(gap_mask_LIX).max('bias_mV').fillna(0)
    
    #CBM_I_mV = grid_3D.bias_mV.where(gap_mask_I).max('bias_mV') # CBM_I_mV

    
    grid_3D_prcssd['VBM_LIX_mV'] = grid_3D.bias_mV.where(gap_mask_LIX).min('bias_mV').fillna(0)
    # CBM& VBM bias_mV value ,  fill nan as (0)
    gap_size_LIX = grid_3D_prcssd.CBM_LIX_mV - grid_3D_prcssd.VBM_LIX_mV
    grid_3D_prcssd['gap_size_LIX'] = gap_size_LIX
    # cf) use the 'isin' to find zero & find the index with 'np.argwhere'

    # (c.f) to fill the VBM, 
    #grid_3D_prcssd['VBM_LIX'] = grid_3D.LIX_fb.where(gap_mask_LIX).fillna(10000).argmin(dim = 'bias_mV')
    # apply find gap_mask_LIX(gapped area), fill 'nan' as -10000 & find argmax 
    #grid_3D_prcssd['VBM_LIX'] = grid_3D.VBM_LIX.where(~gap_mask_LIX).fillna(np.argwhere(grid_3D_prcssd.bias_mV.isin(0).values)[0,0])
    # for the metallic area (~gap_mask_LIX), fill the bias_mV index of 'zero_bias'
    #grid_3D_prcssd['VBM_LIX']=  grid_3D_prcssd['VBM_LIX'].astype(np.int64)
    # the same dtype as np.int64
    grid_3D_prcssd.attrs['I[A]_limit'] = I_0_pA
    grid_3D_prcssd.attrs['LDOS[A/V]_limit'] = LIX_0_AV.values
    
    ## split  LIX_fb_offst as a CB & VB region 
    
    grid_3D_prcssd['LDOS_fb_CB'] =  grid_3D_prcssd.LDOS_fb.where(
        grid_3D_prcssd.bias_mV  >  grid_3D_prcssd.CBM_LIX_mV
    )
    grid_3D_prcssd['LDOS_fb_VB'] =  grid_3D_prcssd.LDOS_fb.where(
        grid_3D_prcssd.bias_mV  <  grid_3D_prcssd.VBM_LIX_mV
    )
    
    return grid_3D_prcssd

#test
#grid_3D_gap = grid_3D_Gap(grid_3D)
#grid_3D_gap
# -
# # Signal Treatments 
# * Assume that the coords in Xarray are 'X",'Y','bias_mV'
# * if the xr is 2D array ==> (X,bias_mV) or (Y, bias_mV) 
# ## Savatzky-Golay smoothig 
#     * use the list comprehension for the sg-smoothing 

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
                    for x in range(x_axis) 
                    for y in range(y_axis)
                ] ).reshape(x_axis,y_axis, xrdata.bias_mV.size),
                dims = ["X", "Y", "bias_mV"],
                coords = {"X": xrdata.X,
                          "Y": xrdata.Y,
                          "bias_mV": xrdata.bias_mV}            )
        else : pass
    return xrdata_prcssd

#grid_2D_sg = savgolFilter_xr(grid_2D)
#grid_2D_sg


# -

def find_peaks_xr(xrdata): 
    from scipy.signal import find_peaks
    xrdata_prcssd = xrdata.copy(deep = True)
    print('Find peaks in STS to an xarray Dataset.')

    for data_ch in xrdata:
        if len(xrdata[data_ch].dims)==2:
            # smoothing filter only for the 3D data set
                    # ==> updaded             
            
            

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
                              for x in range(x_axis)], dtype = object )[:,0],
                dims=["X"],
                coords={"X": xrdata.X})
            
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size

                #print(xrdata_prcssd[data_ch])

                xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                    np.array([ find_peaks(xrdata[data_ch].isel(Y = y).values)
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
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values)[0] 
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

# +
def peak_pad(xrdata):
    xrdata_prcssd = xrdata.copy(deep = True)
    
    
    
    if len(xrdata.dims)==2:
        for data_ch in xrdata:
        
               
            # smoothing filter only for the 3D data set
            ### 2D data case 
            ### assume that coords are 'X','Y','bias_mV'
            #### two case X,bias_mV or Y,bias_mV 
            if 'X' in xrdata[data_ch].dims :
                # xrdata is X,bias_mV 
                # use the isel(X = x) 
                x_axis = xrdata.X.size

                if data_ch.endswith('_peaks'):
                    peaks = xrdata[data_ch].values
                    peaks_count_max = max([ len(peaks_r) 
                                    for peaks_r in peaks])
                    padding_value = np.nan
                    #print(xrdata_prcssd[data_ch])
                    
                    peaks_pad = np.array(
                        [ np.pad(peaks_r.astype(float), 
                                 (0,peaks_count_max-len(peaks_r)), mode = 'constant', 
                               constant_values = padding_value)
                        for peaks_r in peaks ]
                    ).reshape((x_axis,-1))
                    
                    xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["X", "peaks"],
                    coords={"X": xrdata.X, "peaks": np.arange(peaks_count_max)})
                else: pass###
 
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size
                if data_ch.endswith('_peaks'):
                    peaks = xrdata[data_ch].values
                    peaks_count_max = max([ len(peaks_r) 
                                    for peaks_r in peaks])
                    padding_value = np.nan
                    #print(xrdata_prcssd[data_ch])
                    
                    peaks_pad = np.array(
                        [ np.pad(peaks_r.astype(float), 
                                 (0,peaks_count_max-len(peaks_r)), mode = 'constant', 
                               constant_values = padding_value)
                        for peaks_r in peaks ]
                    ).reshape((y_axis,-1))
                    
                    xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["Y", "peaks"],
                    coords={"Y": xrdata.Y, "peaks": np.arange(peaks_count_max)})
                    #print(xrdata_prcssd[data_ch])
                else: pass #
            else: pass##

    
        #if len(xrdata[data_ch].dims)==2:
            # smoothing filter only for the 3D data set
            
    elif len(xrdata.dims)==3:
        x_axis = xrdata.X.size
        y_axis = xrdata.Y.size
        for data_ch in xrdata_prcssd:
            if data_ch.endswith('_peaks'):
                peaks = xrdata[data_ch].values
                peaks_count_max = max([ len(peaks_r_c) 
                                for peaks_r in peaks
                                for  peaks_r_c in peaks_r])
                padding_value = np.nan

                peaks_pad = np.array([
                    np.pad(peaks_r_c.astype(float), 
                           (0,peaks_count_max-len(peaks_r_c)),
                           mode = 'constant', 
                           constant_values = padding_value)
                    for peaks_r in peaks 
                    for  peaks_r_c in peaks_r]).reshape((x_axis,y_axis,-1))

                xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["X", "Y","peaks"],
                    coords={"X": xrdata.X, "Y": xrdata.Y, "peaks": np.arange(peaks_count_max)})
            else: pass
        
        
    elif len(xrdata.dims) == 1:
        peaks_count_max_ch = []
        for data_ch in xrdata:
            if data_ch.endswith('_peaks'):
                peaks_count_max_ch.append(len(xrdata[data_ch].to_numpy().tolist()[0]))
        peaks_count_max = max(peaks_count_max_ch)
        #print(peaks_count_max        )
        for data_ch in xrdata:
            if data_ch.endswith('_peaks'):
                if len(xrdata[data_ch].to_numpy().tolist()[0]) != 0:
                    #print(data_ch)
                    peaks = np.array(xrdata[data_ch].to_numpy().tolist()[0])
                    #print(peaks)
                    padding_value = np.nan
                    #print((0,peaks_count_max-len(peaks)))
                    #print(xrdata_prcssd[data_ch])
                    
                    peaks_pad =np.pad(peaks.astype('float32'),
                                      (0,int(peaks_count_max-len(peaks))),
                                      mode = 'constant', 
                                      constant_values = padding_value)
                    
                    #print(peaks_pad)
                    xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["peaks"],
                            coords={ "peaks": np.arange(peaks_count_max)}).astype('int')
                else: pass
            else: pass
    
    return xrdata_prcssd
        
#grid_3D_sg_pks_pad = peak_pad(grid_3D_sg_pks)
#grid_3D_sg_pks_pad
# -
'''
def peak_pad(xrdata):
    xrdata_prcssd = xrdata.copy(deep = True)
    xAxis = xrdata.X.size
    yAxis = xrdata.Y.size
    for ch in xrdata_prcssd:
        if ch.endswith('_peaks'):
            peaks = xrdata[ch].values
            peaks_count_max = max([ len(peaks_r_c) 
                            for peaks_r in peaks
                            for  peaks_r_c in peaks_r])
            padding_value = np.nan
            
            peaks_pad = np.array([
                np.pad(peaks_r_c.astype(float), 
                       (0,peaks_count_max-len(peaks_r_c)),
                       mode = 'constant', 
                       constant_values = padding_value)
                for peaks_r in peaks 
                for  peaks_r_c in peaks_r]).reshape((xAxis,yAxis,-1))
            
            xrdata_prcssd[ch+'_pad'] = xr.DataArray(peaks_pad, dims=["X", "Y","peaks"],
                coords={"X": xrdata.X, "Y": xrdata.Y, "peaks": np.arange(peaks_count_max)})
        else: pass
    return xrdata_prcssd
        
#grid_3D_sg_pks_pad = peak_pad(grid_3D_sg_pks)
#grid_3D_sg_pks_pad
'''

# ### Rotating the 3D data 

# ### 3D rotation 

### Xr rotation function 
# rotate the XY plan in xr data 
def rotate_3D_xr (xrdata, rotation_angle): 
    # padding first 
    for ch_i,ch_name in enumerate (xrdata):
        if ch_i == 0:  # use only the first channel to calculate a padding size 
            padding_shape = skimage.transform.rotate(xrdata[ch_name].values.astype('float64'),
                                                     rotation_angle,
                                                     resize = True).shape[:2]
            # After rotation, still 3D shape ->  [:2]
            
            padding_xy = (np.array( padding_shape)-np.array(xrdata[ch_name].shape[:2]) +1)/2
            padding_xy = padding_xy.astype(int)
    xrdata_pad = xrdata.pad(X=(padding_xy[0],padding_xy[0]), 
                            Y =(padding_xy[1],padding_xy[1]),
                            mode='constant',
                            cval = xrdata.min())
    if np.array(xrdata_pad[ch_name]).shape[:2] != padding_shape:
        # in case of xrdata_pad shape is +1 larger than real padding_shape
        # index 다루는 법  (X)
        x_spacing = np.diff(xrdata.X).mean()
        y_spacing = np.diff(xrdata.Y).mean()
        xrdata.X[0]
        xrdata.Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata.X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata.Y.shape[0])

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
        x_spacing = np.diff(xrdata.X).mean()
        y_spacing = np.diff(xrdata.Y).mean()
        xrdata.X[0]
        xrdata.Y[0]

        x_pad_dim = padding_shape[0]#int(padding_xy[0]*2+xrdata.X.shape[0])
        y_pad_dim = padding_shape[1]#int(padding_xy[0]*2+xrdata.Y.shape[0])

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
        xrdata_rot[ch].values = skimage.transform.rotate(xrdata[ch].values.astype('float64'),
                                                         rotation_angle,
                                                         cval =xrdata[ch].to_numpy().min(),
                                                         resize = True)
    return xrdata_rot
# ### average X or Y direction jof Grid_3D dataset 
# * use xr_data (3D)
# * average_in = 'X' or 'Y'
# * ch_l_name = channel name for line profile  

def grid3D_line_avg_pks (xr_data, average_in =  'X', ch_l_name = 'LIX_unit_calc') : 

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
            )*-1))
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

# ### Plot line profile (line offset + peak positions) 
# ### only after after **grid3D_line_avg_pks**
#

def  grid_lineNpks_offset(xr_data_l_pks, 
                          ch_l_name = 'LIX_unit_calc',
                          plot_y_offset= 2E-11, 
                          peak_LIX_min = 1E-13, fig_size = (6,8)):
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
                            ax = ax)
    # legend control!( cut the handles 1/2)
    ax.set_xlabel('Bias (mV)')   
    ax.set_ylabel(ch_l_name+'_offset')   
    plt.show()
    return xr_data_l_pks_ch_slct, ch_l_name_df, ch_l_name_pks_df, fig


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
    return xr_data_l_pks_ch_slct, ch_l_name_df, ch_l_name_pks_df, fig






# ### Not Used Previous (WORKING)Functions (FOR 3d ONLY)

'''
def savgolFilter_xr(xrdata,window_length=7,polyorder=3): 
    # window_length = odd number
    #import copy
    #xrdata_prcssd = copy.deepcopy(xrdata)
    xrdata_prcssd = xrdata.copy(deep = True)
    print('Apply a Savitzky-Golay filter to an xarray Dataset.')
    xAxis = xrdata.X.size # or xrdata.dims.mapping['X']
    yAxis = xrdata.Y.size
    for data_ch in xrdata:
        if len(xrdata[data_ch].dims) == 2:
            # smoothing filter only for the 3D data set
            pass
            
        else :
            print (data_ch)
            xrdata_prcssd[data_ch] = xr.DataArray (
                np.array ([
                    sp.signal.savgol_filter(xrdata[data_ch].isel(X = x, Y = y).values,
                                            window_length, 
                                            polyorder , 
                                            mode = 'nearest')
                    for x in range(xAxis) 
                    for y in range(yAxis)
                ] ).reshape(xAxis,yAxis, xrdata.bias_mV.size),
                dims = ["X", "Y", "bias_mV"],
                coords = {"X": xrdata.X,
                          "Y": xrdata.Y,
                          "bias_mV": xrdata.bias_mV}
            )
    return xrdata_prcssd
'''


'''
def find_peaks_xr(xrdata): 
    from scipy.signal import find_peaks
    xrdata_prcssd = xrdata.copy(deep = True)
    print('Find peaks in STS to an xarray Dataset.')
    xAxis = xrdata.X.size
    yAxis = xrdata.Y.size
    for data_ch in xrdata:
        if len(xrdata[data_ch].dims)==2:
            # smoothing filter only for the 3D data set
            pass
            
        else :
            print (data_ch)
            """xrdata_prcssd[data_ch+'_peaks']= xr.DataArray(np.ones((xAxis,yAxis), dtype = object),
                                                             dims=["X", "Y"],
                                                             coords={"X": xrdata.X, "Y": xrdata.Y} )"""
            xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                np.array([ find_peaks(xrdata[data_ch].isel(X = x, Y = y).values)[0] 
                          for x in range(xAxis)  
                          for y in range(yAxis)], dtype = object ).reshape(xAxis,yAxis),
                dims=["X", "Y"],
                coords={"X": xrdata.X, "Y": xrdata.Y})
            
                    # use the "xrdata_prcssd[data_ch].values[x,y,:]"  for "xrdata_prcssd" 
                    # not ".isel(X = x, Y = y).values"""

    return xrdata_prcssd
#grid_3D_sg_pks = find_peaks_xr(grid_3D_sg)
'''

