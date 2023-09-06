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

# # SPMpy 
# * Authors : Dr. Jewook Park at CNMS, ORNL
#     * Center for Nanophase Materials Sciences (CNMS), Oak Ridge National Laboratory (ORNL)
#     * email :  parkj1@ornl.gov
#         
# > **SPMpy** is a python package to analysis scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques, and utilzes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools in the [scientific python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
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

def grid_3D_unit_calc (grid_3D): 
    '''
    Grid_3D data contains 'I_fb' & 'LIX_fb' 
    using numerical derivative of xr.differentiate 
    compare the ration between  real [A/V] unit and measured Lockin 'pA' unit.
    convert and make a new channel 'LIX_unit_calc'
    
    '''
    grid_3D_dIdV_numeric = grid_3D.differentiate(coord = 'bias_mV').I_fb
    # numerically calculated dI/dV from I_fb
    LIX_convert_ratio = grid_3D_dIdV_numeric / grid_3D.LIX_fb

    grid_3D['LIX_unit_calc'] = np.abs( LIX_convert_ratio.mean())*grid_3D.LIX_fb
    
    #grid_3D

    return grid_3D
    # in case of LIX offset exist.. 
    # if it is metallic sample.. no problem 


# # Need to make a bias_mV = 0 adjust function 

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
    '''
    # simply assign the gap by using I & LIX reference 0 point. 
    
    '''
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
# +
def grid_3D_SCgap(xr_data,tolerance_I =  0.2E-11, tolerance_LIX = 1E-11,
                  apply_SGfilter = True,  window_length = 21, polyorder = 3, 
                  bias_mV_set_zero = True):
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
                   
    xr_data_prcssd['dIdV'] = xr_data_prcssd.I_fb.differentiate(
        coord = 'bias_mV')
    # numerically calculated dI/dV from I_fb
    LIX_ratio = xr_data_prcssd.dIdV / xr_data_prcssd.LIX_fb
       
    xr_data_prcssd['LIX_unit_calc'] = np.abs(
        LIX_ratio.mean())*xr_data_prcssd.LIX_fb
    # LIX unit calibration 
    # pA unit : lock-in result 
    # LIX_unit_calc : calibrated as [A/V] unit for dI/dV
       
    
    print('Find plateau in I &LIX each points')
    if apply_SGfilter == True :
        print('import savgolFilter_xr in advance' )
        xr_data_sg = savgolFilter_xr(xr_data_prcssd, 
                                     window_length = window_length,
                                     polyorder = polyorder)

    else : 
        print ('without SavgolFilter_xr, check outliers')
        xr_data_sg = xr_data_prcssd

    if 'I_fb' in xr_data_prcssd.data_vars : 
        I_fb_plateau = abs(xr_data_sg['I_fb']) <= tolerance_I 
    else :
        I_fb_plateau = abs(xr_data_sg['LIX_fb']) <= tolerance_LIx  
        print ('No I_fb channel, use LIX instead')

    if 'LIX_unit_calc' in xr_data_prcssd.data_vars : 
        LIX_fb_plateau = abs(xr_data_sg['LIX_unit_calc']) <= tolerance_LIX * np.abs( LIX_ratio.mean())
    else: 
        LIX_fb_plateau = abs(xr_data_sg['LIX_fb']) <= tolerance_LIX 
        print ('test_ No LIX_unit_calc channel, use LIX instead for tolerance_LIX check-up')

    I_LIX_plateau = I_fb_plateau*LIX_fb_plateau
    # pixels in X,Y, bias_mV  intersection of plateau

    xr_data_sg['I_LIX_plateau']=I_LIX_plateau
    #I_LIX_plateau is where  plateau within I & LIX tolerance 
    # I tolerance is near Zero Current 
    # LIX tolerance is more flat area with in I tolerance area 
    # Energy gap near Zero bias  
    
    
    ################################################
    # adjust bias_mV at zero first
    ####################################################
    if bias_mV_set_zero == True:
        # select I_LIX_plateau is False ==> non-zero conductance at zero biase) 
        # apply boolean to I_fb & areal average 
        # find base at Zero Current 

        non_zero_condunctance_avg  = xr_data_sg.I_fb.where(~xr_data_sg.I_LIX_plateau.sel(bias_mV=0, method='nearest')).mean(dim = ['X','Y'])
        # find bias_mV value in where the close to zero current 
        # xr_data_prcssd.bias_mV[np.abs(non_zero_condunctance_avg).argmin()]
        if non_zero_condunctance_avg.sum() ==0 : 
            pass
        else:
            # error message with "All-NaN slice encountered"
            #bias_mV_shift = grid_3D_gap.bias_mV -  grid_3D_gap.bias_mV[np.abs(non_zero_condunctance_avg).argmin()]
            print("bias_mV zero where I_fb =0" , xr_data_sg.bias_mV[np.abs(non_zero_condunctance_avg).argmin()].values)
            # use assign_coords to change bias_mV values 
            xr_data_prcssd = xr_data_sg.assign_coords (bias_mV = xr_data_sg.bias_mV -  xr_data_sg.bias_mV[np.abs(non_zero_condunctance_avg).argmin()])
            print("zero bias_mV: shifted")
    else: pass
    
    
    ##################################################
    ### find gap position again after bias_mV adjusted 
    #####################################################
    
    if 'I_fb' in xr_data_prcssd.data_vars : 
        I_fb_plateau = abs(xr_data_prcssd['I_fb']) <= tolerance_I 
    else :
        I_fb_plateau = abs(xr_data_prcssd['LIX_fb']) <= tolerance_LIx  
        print ('No I_fb channel, use LIX instead')

    if 'LIX_unit_calc' in xr_data_prcssd.data_vars : 
        LIX_fb_plateau = abs(xr_data_prcssd['LIX_unit_calc']) <= tolerance_LIX *np.abs( LIX_ratio.mean())
    else: 
        LIX_fb_plateau = abs(xr_data_prcssd['LIX_fb']) <= tolerance_LIX 
        print ('No LIX_unit_calc channel, use LIX instead for tolerance_LIX check-up')

    I_LIX_plateau = I_fb_plateau*LIX_fb_plateau
    # pixels in X,Y, bias_mV  intersection of plateau

    xr_data_prcssd['I_LIX_plateau'] = I_LIX_plateau
    
    
    # out figure
    gap_pos0_I = xr_data_prcssd.I_fb.where(I_LIX_plateau).idxmax(dim='bias_mV')
    gap_neg0_I = xr_data_prcssd.I_fb.where(I_LIX_plateau).idxmin(dim='bias_mV')
    gap_mapI = gap_pos0_I-gap_neg0_I
    
    
    
    xr_data_prcssd['gap_pos0_I'] = gap_pos0_I
    xr_data_prcssd['gap_neg0_I'] = gap_neg0_I
    xr_data_prcssd['gap_mapI'] = gap_mapI
    #########
    
    gap_pos0_LIX_mV = xr_data_prcssd.LIX_unit_calc.where(I_LIX_plateau).idxmax(dim='bias_mV')
    gap_neg0_LIX_mV = xr_data_prcssd.LIX_unit_calc.where(I_LIX_plateau).idxmin(dim='bias_mV')
   
    # I_LIX_plateau  가운데  max min 을 골라냈음. (전체가운데 0가 포함하는지는 아직 모름. 
    
    
    xr_data_prcssd['gap_pos0_LIX'] = gap_pos0_LIX_mV
    xr_data_prcssd['gap_neg0_LIX'] = gap_neg0_LIX_mV
    
    #######################################################
    # filtering gap_pos0_LIX <--- filtering 'neg' values 
    # filtering gap_neg0_LIX <--- filtering 'pos' values 
    #########
    #gap_neg0_LIX_neg = xr_data_prcssd.gap_neg0_LIX.where(xr_data_prcssd.gap_neg0_LIX>0).isnull()
    # True ==>   neg == neg
    gap_neg0_LIX_neg = xr_data_prcssd.gap_neg0_LIX.where(gap_neg0_LIX_mV<0)
    xr_data_prcssd['gap_neg0_LIX']= gap_neg0_LIX_neg
    # assign again 
    
    
    #gap_pos0_LIX_pos = xr_data_prcssd.gap_pos0_LIX.where(xr_data_prcssd.gap_pos0_LIX<0).isnull()
    # True ==>  pos == pos
    gap_pos0_LIX_pos = xr_data_prcssd.gap_pos0_LIX.where(xr_data_prcssd.gap_pos0_LIX>0)
    xr_data_prcssd['gap_pos0_LIX']=gap_pos0_LIX_pos
    # assign again 
    
    
    plateau_map_LIX = (~gap_pos0_LIX_pos.isnull())&(~gap_neg0_LIX_neg.isnull())
    #     plateau_map_LIX = gap_neg0_LIX_neg & gap_pos0_LIX_pos 
    
    
    # select plateau that contains ZeroBias  ---> plateau_map (zero LIX at zero bias) 
    xr_data_prcssd['plateau_map_LIX'] = plateau_map_LIX
    plateau_pos0_LIX = xr_data_prcssd.LIX_unit_calc.where(plateau_map_LIX).idxmax(dim='bias_mV')
    plateau_neg0_LIX = xr_data_prcssd.LIX_unit_calc.where(plateau_map_LIX).idxmin(dim='bias_mV')
    # LIX plateau area min & max 
    #xr_data_prcssd['plateau_pos0_LIX'] = plateau_pos0_LIX
    #xr_data_prcssd['plateau_neg0_LIX'] = plateau_neg0_LIX
    
    xr_data_prcssd['plateau_size_map_LIX'] = gap_pos0_LIX_pos-gap_neg0_LIX_neg
    # plateau_size_map_LIX
    xr_data_prcssd['zerobiasconductance'] = xr_data_prcssd.where(~plateau_map_LIX).LIX_unit_calc.sel(bias_mV=0, method = 'nearest')
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
# -


def hv_bias_mV_slicing(xr_data,ch = 'LIX_fb',frame_width = 200,cmap = 'bwr'): 
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
    dmap_plane  = ["X","Y"]
    dmap = xr_data_hv.to(hv.Image,
                         kdims = dmap_plane,
                         dynamic = True )
    dmap.opts(colorbar = True,
              cmap = 'bwr',
              frame_width = frame_width,
              aspect = 'equal').relabel('XY plane slicing: ')
    fig = hv.render(dmap)
    return dmap   


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






def hv_XY_slicing(xr_data,ch = 'LIX_fb', slicing= 'X', frame_width = 200,cmap = 'bwr'): 
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
    if slicing == 'Y':
        dmap_plane  = [ "X","bias_mV"]

        dmap = xr_data_hv.to(hv.Image,
                             kdims = dmap_plane,
                             dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = frame_width).relabel('X - bias_mV plane slicing: ')
    else : #slicing= 'X'
        dmap_plane  = [ "Y","bias_mV"]

        dmap = xr_data_hv.to(hv.Image,
                             kdims = dmap_plane,
                             dynamic = True )
        dmap.opts(colorbar = True,
                  cmap = 'bwr',
                  frame_width = frame_width).relabel('Y - bias_mV plane slicing: ')
    fig = hv.render(dmap)
    return dmap   


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


def plot_XYslice_w_LDOS (xr_data, data_channel='LIX_fb', slicing_bias_mV = 2):
    
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
    plt.style.use('default')
    sliderX_v = xr_data.X[sliderX.value].values
    sliderY_v = xr_data.Y[sliderY.value].values


    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[data_channel]

    xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[data_channel]
    
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

    xr_data_Vline_profile.plot(ax = axs[1], robust = True, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max()*0.3)
    #xr_data_Hline_profile.T.plot(ax = axs[2], robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())
    axs[1].vlines(0,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls ='--', alpha =0.3) 
    #xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[2])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    
    return plt.show()


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



def plot_Yslice_w_LDOS (xr_data, sliderY, ch ='LIX_fb', slicing_bias_mV = 0):
    
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
    #sliderX_v = xr_data.X[sliderX.value].values
    sliderY_v = xr_data.Y[sliderY.value].values


    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[ch]

    #xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[ch]
    
    # bias_mV slicing
    fig,axes = plt.subplots (nrows = 1,
                            ncols = 2,
                            figsize = (6,3))
    axs = axes.ravel()

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ).T,
                    ax =  axs[0],
                    robust = True)
    axs[0].vlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    #axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    #xr_data_Vline_profile.plot(ax = axs[1], robust = True, vmin = xr_data_Vline_profile.to_numpy().min(), vmax = xr_data_Vline_profile.to_numpy().max()*0.25)
    #xr_data_Hline_profile.plot(ax = axs[1], robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())
    xr_data_Hline_profile.plot(ax = axs[1], robust = True, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max()*0.20)
    axs[1].vlines(0,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls ='--', alpha =0.3) 
    # L half alpha
    axs[1].vlines(0.368181818,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3) 
    axs[1].vlines(1.104545455,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3)     
    axs[1].vlines(1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3) 
    axs[1].vlines(-0.368181818,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3) 
    axs[1].vlines(-1.104545455,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3)     
    axs[1].vlines(-1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'w',ls =':', alpha =0.3) 
    
    # L int  alpha
    0.736363636, 1.472727273, 2.209090909
    axs[1].vlines(0.736363636,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5) 
    axs[1].vlines(1.472727273,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5)     
    axs[1].vlines(1.840909091,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5) 
    axs[1].vlines(-0.736363636,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5) 
    axs[1].vlines(-1.472727273,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5)     
    axs[1].vlines(-2.2090909091,0,xr_data.Y.shape[0], lw = 1, color = 'r',ls ='-', alpha =0.5) 
    
    #xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[2])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )
    
    
    axs[1].set_xlim(-2.5,2.5)
    # set x range limit
    
    fig.tight_layout()
    
    return plt.show()

# +
# function for drawing bbox averaged STS 
# only after bbox setup & streaming bound_box positions


def hv_bbox_topo_avg (xr_data, bound_box , ch = 'topography' ):
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
    isns.set_image(cmap="inferno",origin = 'lower')
    # isns image directino setting 

    fig,axs = plt.subplots (nrows = 1,
                            ncols = 3,
                            figsize = (12,4))

    isns.imshow(xr_data[ch].values,
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

    isns.imshow(xr_data_bbox[ch].values,
                ax =  axs[1],
                robust = True)

    # topography along longer axis 
    if xr_data_bbox.X.size > xr_data_bbox.Y.size : 
        avg_dim =[ 'Y']
    else : 
        avg_dim =[ 'X']

    sns.lineplot(xr_data_bbox.mean(dim = avg_dim).to_dataframe(),
                 ax = axs[2])
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 
# +
# function for drawing bbox averaged STS 
# only after bbox setup & streaming bound_box positions


def hv_bbox_avg (xr_data, bound_box , ch = 'LIX_fb' ,slicing_bias_mV = 0.5, show_LDOS_avg = False ):
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
    isns.set_image(cmap= 'viridis',origin = 'lower')
    # isns image directino setting 
    if show_LDOS_avg == True :
        ncols = 3
        
    else : 
        ncols = 2 
        
    
    fig,axs = plt.subplots (nrows = 1,
                            ncols = ncols,
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
    if show_LDOS_avg == True :   
        sns.lineplot(x = "bias_mV",
                     y = ch, 
                     data = xr_data_bbox.to_dataframe(),
                     ax = axs[2])
    else : pass
    #plt.savefig('grid011_bbox)p.png')
    plt.show()
    # 3 figures will be diplayed, original image with Bbox area, BBox area zoom, BBox averaged STS
    return xr_data_bbox, fig
    # plot STS at the selected points 
    # use the seaborn (confident interval : 95%) 
    # sns is figure-level function 
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
            
            if xrdata[data_ch].dims == ('Y', 'X'):
                print('3D data')
                pass
                
            else: # in case of X& bias_mV or Y  & bias_mV case

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


# -

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

    xr_data_Vline_profile.plot(ax = axs[1], robust = True)#, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max())
    xr_data_Hline_profile.T.plot(ax = axs[2], robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())

    xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[3])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    
    return plt.show()


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
    #sliderY_v = xr_data.Y[sliderY.value].values


    xr_data_Hline_profile = xr_data.isel(Y = sliderY.value)[ch]

    xr_data_Vline_profile = xr_data.isel(X = sliderX.value)[ch]
    
    # bias_mV slicing
    fig,axes = plt.subplots (nrows = 3,
                            ncols = 1,
                            figsize = (3,6))
    axs = axes.ravel()

    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(sliderY.value,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(sliderX.value,0,xr_data.Y.shape[0], lw = 1, color = 'm')    

    xr_data_Vline_profile.plot(ax = axs[1], robust = True)#, vmin = xr_data_Vline_profile.to_numpy().min() , vmax = xr_data_Vline_profile.to_numpy().max())
    #xr_data_Hline_profile.T.plot(ax = axs[2], robust = True)#, vmin = xr_data_Hline_profile.to_numpy().min() , vmax = xr_data_Hline_profile.to_numpy().max())

    xr_data[ch].isel(X =sliderX.value, Y =sliderY.value) .plot(ax =axs[2])
    #pn.Row(pn.Column(dmap_slideXY,xr_data_Vline_profile.plot()), )

    fig.tight_layout()
    
    return plt.show()


def find_0plateau_gap(xr_data,tolerance_I =  0.2E-11, tolerance_LIX = 1E-11, apply_SGfilter = True):
    '''
    check the tolerance_I  &  tolerance_LIx values in advance 
    USE 'find_plateau_tolarence_values' function . 
    
    plateau finding only. 
    apply SG & 1st , 2nd derivative in advance. 
    Using both I_fb & LIX_fb, 
    assign plateau as an intersection of I_fb & LIX_fb plateau 
    
    
    
    '''
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

    gap_pos0_LIX = xr_data.where(I_LIX_plateau).LIX_unit_calc.idxmax(dim='bias_mV')
    gap_neg0_LIX = xr_data.where(I_LIX_plateau).LIX_unit_calc.idxmin(dim='bias_mV')
    gap_map_LIX = gap_pos0_LIX - gap_neg0_LIX

    fig,axes = plt.subplots(ncols=3, nrows = 2 , figsize= (9,6))
    axs= axes.ravel()
    gap_pos0_I.plot(ax = axs[0] )
    axs[0].set_title('gap_I_0+')
    gap_neg0_I.plot(ax = axs[1])
    axs[1].set_title('gap_I_0+')
    gap_mapI.plot(ax = axs[2])
    axs[2].set_title('gap_map_I')

    gap_pos0_LIX.plot(ax = axs[3])
    axs[3].set_title('gap_LIX_0+')
    gap_neg0_LIX.plot(ax = axs[4])
    axs[4].set_title('gap_LIX_0+')
    gap_map_LIX.plot(ax = axs[5])
    axs[5].set_title('gap_map_LIX')
    axs[0].set_aspect(1)
    axs[1].set_aspect(1)
    axs[2].set_aspect(1)
    axs[3].set_aspect(1)
    axs[4].set_aspect(1)
    axs[5].set_aspect(1)
    fig.suptitle('tolerance_I = '+str(tolerance_I) + "& tolerance_LIX = " + str(tolerance_LIX) )
    
    plt.tight_layout()

    plt.show()

    return xr_data_sg


# +
def find_plateau_tolarence_values (xr_data, x_i ,  y_j ,ch ='LIX_fb',slicing_bias_mV = 2, tolerance_I= 1E-10, tolerance_LIX = 1E-12):
    '''
    Use slider in advance. 
    check XY position with 
    "plot_XYslice_w_LDOS" function 
    
        #### use the slider 
        sliderX = pnw.IntSlider(name='X', 
                           start = 0 ,
                           end = grid_3D.X.shape[0]) 
        sliderY = pnw.IntSlider(name='Y', 
                           start = 0 ,
                           end = grid_3D.Y.shape[0]) 

        #sliderX_v_intact = interact(lambda x:  grid_3D.X[x].values, x =sliderX)[1]
        #sliderY_v_intact = interact(lambda y:  grid_3D.Y[y].values, y =sliderY)[1]
        pn.Column(interact(lambda x:  grid_3D.X[x].values, x =sliderX), interact(lambda y: grid_3D.Y[y].values, y =sliderY))
        # Do not exceed the max Limit ==> error
        # how to connect interactive values to the other cell --> need to update (later) 
        x_i = sliderX.value
        y_j = sliderY.value 
    
    
    '''

    print (x_i ,y_j)

    fig,axes =  plt.subplots (ncols = 3, figsize = (9,3))
    axs = axes.ravel()
    
    # plot 2D map with x_i & y_j 
    
    isns.imshow(xr_data[ch].sel(bias_mV = slicing_bias_mV, method="nearest" ),
                    ax =  axs[0],
                    robust = True)
    axs[0].hlines(y_j,0,xr_data.X.shape[0], lw = 1, color = 'c')
    axs[0].vlines(x_i,0,xr_data.Y.shape[0], lw = 1, color = 'm')  
    
    
    
    # for I_fb
    sns.lineplot (xr_data.I_fb.isel(X = x_i, Y = y_j).to_dataframe(), x= 'bias_mV',y= 'I_fb', ax =axs[1])
    axs[1].axhline(y=tolerance_I, c='orange') # pos tolerance line
    axs[1].axhline(y=-tolerance_I, c='orange') # neg tolerance line
    # fill between x area where Y value is smaller than tolerance value 
    axs[1].fill_between(xr_data.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_I, tolerance_I, 
                   where=abs(xr_data.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_I,
                   facecolor='yellow', interpolate=True, alpha=0.3)
    
    # for LIX_fb
    sns.lineplot (xr_data.LIX_fb.isel(X = x_i, Y = y_j).to_dataframe(), x= 'bias_mV',y= 'LIX_fb', ax =axs[2])
    axs[2].axhline(y=tolerance_LIX, c='magenta') # pos tolerance line
    axs[2].axhline(y=-tolerance_LIX, c='magenta') # neg tolerance line
    # fill between x area where Y value is smaller than tolerance value 
    axs[2].fill_between(xr_data.LIX_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                   where=abs(xr_data.LIX_fb.isel(X = x_i, Y = y_j)) <= tolerance_LIX,
                   facecolor='cyan', interpolate=True, alpha=0.3)
                  
    axs[2].fill_between(xr_data.I_fb.isel(X = x_i, Y = y_j).bias_mV, -tolerance_LIX, tolerance_LIX, 
                        where=abs(xr_data.I_fb.isel(X = x_i, Y = y_j)) <= tolerance_I,
                        facecolor='yellow', interpolate=True, alpha=0.3)
                  
                  
    plt.tight_layout()
    plt.show()
    
    return 



# -
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

# +
def peak_pad(xrdata, padding_value = np.nan):
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
                    #padding_value = np.nan
                    #print(xrdata_prcssd[data_ch])
                    
                    peaks_pad = np.array(
                        [ np.pad(peaks_r.astype(float), 
                                 (0,peaks_count_max-len(peaks_r)), mode = 'constant', 
                               constant_values = padding_value)
                        for peaks_r in peaks ]
                    ).reshape((x_axis,-1))
                    
                    xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["X", "peaks"],
                    coords={"X": xrdata.X, "peaks": np.arange(peaks_count_max)}).astype('int')
                else: pass###
 
            elif 'Y' in xrdata[data_ch].dims :
                # xrdata is Y,bias_mV 
                # use the isel(Y = y) 
                y_axis = xrdata.Y.size
                if data_ch.endswith('_peaks'):
                    peaks = xrdata[data_ch].values
                    peaks_count_max = max([ len(peaks_r) 
                                    for peaks_r in peaks])
                    #padding_value = np.nan
                    #print(xrdata_prcssd[data_ch])
                    
                    peaks_pad = np.array(
                        [ np.pad(peaks_r.astype(float), 
                                 (0,peaks_count_max-len(peaks_r)), mode = 'constant', 
                               constant_values = padding_value)
                        for peaks_r in peaks ]
                    ).reshape((y_axis,-1))
                    
                    xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["Y", "peaks"],
                    coords={"Y": xrdata.Y, "peaks": np.arange(peaks_count_max)}).astype('int')
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
                #padding_value = np.nan

                peaks_pad = np.array([
                    np.pad(peaks_r_c.astype(float), 
                           (0,peaks_count_max-len(peaks_r_c)),
                           mode = 'constant', 
                           constant_values = padding_value)
                    for peaks_r in peaks 
                    for  peaks_r_c in peaks_r]).reshape((x_axis,y_axis,-1))

                xrdata_prcssd[data_ch+'_pad'] = xr.DataArray(peaks_pad, dims=["X", "Y","peaks"],
                    coords={"X": xrdata.X, "Y": xrdata.Y, "peaks": np.arange(peaks_count_max)}).astype('int')
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
                    #padding_value = np.nan
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
def find_peaks_prominence_xr(xrdata, find_peaks_in_ch = 'LDOS_fb', height= None, threshold=None, distance=None): 
    from scipy.signal import find_peaks, peak_prominences
    
    xrdata_prcssd = xrdata.copy(deep = True)
    
    print('Use this function only after find_peaks_xr  & peak_pad')
    # counting irregular number of dimension issue 
    # each pixel will have different pixel number 
    # use peak_pad for peak # as a dimension 
    print (' use padding_value= 0, & remove peaks at index zero' ) 
    # peak_pad filling --> 0 
    
    
    for ch_i, data_ch in enumerate(xrdata):

        if data_ch == find_peaks_in_ch:
            print (data_ch + 'dims = '+ str(len(xrdata[data_ch].dims)))
            # channel dim is not good variable to assign grid_line or grid_map
            
            if len(xrdata[data_ch].dims) == 1:
                if data_ch == find_peaks_in_ch : 
                    print (data_ch+ ' peak_properties check for dim ==1')
                    if 'bias_mV' in xrdata.dims: 
                        for data_ch in xrdata: 
                            xrdata_prcssd[data_ch+'_peaks_pad'] = xr.DataArray (peak_prominences(xrdata[data_ch].values[0,:], xrdata[data_ch+'_peaks_pad'].values[0,:])[0])
                    else : pass
                else: pass

    
            elif ( len(xrdata.X) == 1 ) or (len(xrdata.Y) == 1 ) :
                print (data_ch+ ' peak_properties check for dim ==2')
                # smoothing filter only for the 3D data set# ==> updated             
                ### 2D data case 
                ### assume that coords are 'X','Y','bias_mV'
                #### two case X,bias_mV or Y,bias_mV 
                if 'X' in xrdata[data_ch].dims :
                    # xrdata is X,bias_mV 
                    # use the isel(X = x) 
                    x_axis = xrdata.X.size
                    print('Along X')
                    #print(xrdata_prcssd[data_ch])

                    xrdata_prcssd[data_ch+'_peak_prominence'] = xr.DataArray (
                        np.array([ peak_prominences(xrdata[data_ch].isel(X = x).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(X = x).values[0,:])
                                  for x in range(x_axis)], dtype = float ),
                    dims=["X", "prominence", "peaks"],
                    coords={"X": xrdata.X, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})

                elif 'Y' in xrdata[data_ch].dims :
                    # xrdata is Y,bias_mV 
                    # use the isel(Y = y) 
                    y_axis = xrdata.Y.size
                    print('Along Y')
                    #print(xrdata_prcssd[data_ch])

                    xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                        np.array([peak_prominences(xrdata[data_ch].isel(Y = y).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(Y = y).values[0,:])
                                  for y in range(y_axis)], dtype = float ),
                    dims=["Y", "prominence", "peaks"],
                    coords={"Y": xrdata.Y, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})
                else: 
                     print (data_ch + ': channel is not for prominence finding dim==2')
                    # ==> updated 

            elif ( len(xrdata.X) != 1 ) & (len(xrdata.Y) != 1 ) :
                if data_ch == find_peaks_in_ch : 

                    print('dim ==3')
                    x_axis = xrdata.X.size
                    y_axis = xrdata.Y.size
                    print (ch_i,data_ch)
                    print ('prominence checking')
                    xrdata_prcssd[data_ch+'_peaks_prominience'] = xr.DataArray (
                        np.array([ peak_prominences(xrdata[data_ch].isel(X = x, Y = y).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(X = x, Y = y).values[0,:])[0]
                                  for y in range(y_axis)  
                                  for x in range(x_axis)], dtype = float ).reshape(x_axis,y_axis),
                        dims=["X", "Y","peaks","prominence" ],
                        coords={"X": xrdata.X, "Y": xrdata.Y, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})

                    ### there is something wrong here...
                    ###  check the find peak functions again ..
                else:                     
                    print (data_ch + str(ch_i)+ ': channel is not for prominence finding, dim ==3')
                    print('_peak_prominence_skip')
                    #xrdata_prcssd[data_ch] = xrdata[data_ch]
                    print (data_ch, ch_i)
                    print (data_ch+ ' peak_properties check not for this c hannel , for dim ==3')
            else: pass
    
                                            
        else : pass
        
    return xrdata_prcssd
#grid_2D_sg_pks = find_peaks_xr(grid_2D_sg)

def find_peaks_properties_xr(xrdata, find_peaks_in_ch = 'LDOS_fb', height= None, threshold=None, distance=None): 
    from scipy.signal import find_peaks, peak_prominences
    
    xrdata_prcssd = xrdata.copy(deep = True)
    
    print('Use this function only after find_peaks_xr  & peak_pad')
    # counting irregular number of dimension issue 
    # each pixel will have different pixel number 
    # use peak_pad for peak # as a dimension 
    print (' use padding_value= 0, & remove peaks at index zero' ) 
    print (' this function will be updated later for properties dict in case of prominence or width was given for peak finding ' )
    # peak_pad filling --> 0 
    
    
    for ch_i, data_ch in enumerate(xrdata):

        if data_ch == find_peaks_in_ch:
            print (data_ch + 'dims = '+ str(len(xrdata[data_ch].dims)))
            # channel dim is not good variable to assign grid_line or grid_map
            
            if len(xrdata[data_ch].dims) == 1:
                if data_ch == find_peaks_in_ch : 
                    print (data_ch+ ' peak_properties check for dim ==1')
                    if 'bias_mV' in xrdata.dims: 
                        for data_ch in xrdata: 
                            xrdata_prcssd[data_ch+'_peaks_pad'] = xr.DataArray (peak_prominences(xrdata[data_ch].values[0,:], xrdata[data_ch+'_peaks_pad'].values[0,:])[0])
                    else : pass
                else: pass

    
            elif ( len(grid_LDOS_sg_pk.X) == 1 ) or (len(grid_LDOS_sg_pk.Y) == 1 ) :
                print (data_ch+ ' peak_properties check for dim ==2')
                # smoothing filter only for the 3D data set# ==> updated             
                ### 2D data case 
                ### assume that coords are 'X','Y','bias_mV'
                #### two case X,bias_mV or Y,bias_mV 
                if 'X' in xrdata[data_ch].dims :
                    # xrdata is X,bias_mV 
                    # use the isel(X = x) 
                    x_axis = xrdata.X.size
                    print('Along X')
                    #print(xrdata_prcssd[data_ch])

                    xrdata_prcssd[data_ch+'_peak_prominence'] = xr.DataArray (
                        np.array([ peak_prominences(xrdata[data_ch].isel(X = x).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(X = x).values[0,:])
                                  for x in range(x_axis)], dtype = float ),
                    dims=["X", "prominence", "peaks"],
                    coords={"X": xrdata.X, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})

                elif 'Y' in xrdata[data_ch].dims :
                    # xrdata is Y,bias_mV 
                    # use the isel(Y = y) 
                    y_axis = xrdata.Y.size
                    print('Along Y')
                    #print(xrdata_prcssd[data_ch])

                    xrdata_prcssd[data_ch+'_peaks'] = xr.DataArray (
                        np.array([peak_prominences(xrdata[data_ch].isel(Y = y).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(Y = y).values[0,:])
                                  for y in range(y_axis)], dtype = float ),
                    dims=["Y", "prominence", "peaks"],
                    coords={"Y": xrdata.Y, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})
                else: 
                     print (data_ch + ': channel is not for prominence finding dim==2')
                    # ==> updated 

            elif ( len(grid_LDOS_sg_pk.X) != 1 ) & (len(grid_LDOS_sg_pk.Y) != 1 ) :
                if data_ch == find_peaks_in_ch : 

                    print('dim ==3')
                    x_axis = xrdata.X.size
                    y_axis = xrdata.Y.size
                    print (ch_i,data_ch)
                    print ('prominence checking')
                    xrdata_prcssd[data_ch+'_peaks_prominience'] = xr.DataArray (
                        np.array([ peak_prominences(xrdata[data_ch].isel(X = x, Y = y).values[0,:], xrdata[data_ch+'_peaks_pad'].isel(X = x, Y = y).values[0,:])[0]
                                  for y in range(y_axis)  
                                  for x in range(x_axis)], dtype = float ).reshape(x_axis,y_axis),
                        dims=["X", "Y","peaks","prominence" ],
                        coords={"X": xrdata.X, "Y": xrdata.Y, "peaks": xrdata.peaks, "prominence":['prominences', 'left_bases','right_basis']})

                    ### there is something wrong here...
                    ###  check the find peak functions again ..
                else:                     
                    print (data_ch + str(ch_i)+ ': channel is not for prominence finding, dim ==3')
                    print('_peak_prominence_skip')
                    #xrdata_prcssd[data_ch] = xrdata[data_ch]
                    print (data_ch, ch_i)
                    print (data_ch+ ' peak_properties check not for this c hannel , for dim ==3')
            else: pass
    
                                            
        else : pass
        
    return xrdata_prcssd
#grid_2D_sg_pks = find_peaks_xr(grid_2D_sg)

def peak_mV_3Dxr(xr_data,ch='LIX_fb'): 
    '''
    after peak finding, 
    _peaks channels --> 
    
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
                          for y in range(y_axis)  
                          for x in range(x_axis)], dtype = object ).reshape(y_axis,x_axis,bias_mV_axis),
                dims=["Y", "X","bias_mV"],
                coords={"X": xr_data.X, "Y": xr_data.Y,  "bias_mV": xr_data.bias_mV}) 
    return xrdata_prcssd


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

def grid3D_line_avg_pks (xr_data, average_in =  'X',
                         ch_l_name = 'LIX_unit_calc',
                         height = None,
                         distance = None,
                         threshold = None,
                         prominence=None, width=None,
                         padding_value = np.nan,
                         window_length=7,
                         polyorder=3
                        ) : 

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
                    xr_data_l.differentiate(coord='bias_mV'),
                    window_length=window_length,polyorder=polyorder,
                ).differentiate(coord='bias_mV'),
                window_length=window_length,polyorder=polyorder
            )*-1, height =height, distance = distance, threshold = threshold, prominence=prominence, width=width), 
        padding_value = padding_value)
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
                            palette ="rocket",sizes=0.2,
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
# Check drift compensation result for each lines. 
# use correlation between selected areas. 

# not fully 
# -

def padding_xr (xrdata, padding_dim = 'X', padding_shape =5, padding_value = np.nan): 
    '''
    Input: 
    xrdata : use padding result only for XY
    convert XY coord accordingly 
    padding_value : filling value, can be other constant, update if needed.
    
    Output:  padding result 
    '''
    
    # padding 

    # padding amount:  padding_shape 
    padding_shape = padding_shape 
    
    # front side append for X dimension 
    X_pad  = np.append (
        np.append(
            (np.arange(1,padding_shape+1,1)[::-1]* -xrdata.X_spacing)
            - xrdata.X.min().values , 
            xrdata.X ), 
        (np.arange(1,padding_shape+1,1)* xrdata.X_spacing)
        + xrdata.X.max().values)
    Y_pad  = np.append (
        np.append(
            (np.arange(1,padding_shape+1,1)[::-1]* -xrdata.Y_spacing)
            - xrdata.Y.min().values , 
            xrdata.Y ), 
        (np.arange(1,padding_shape+1,1)* xrdata.Y_spacing)
        + xrdata.Y.max().values)
        # np.arange start from 1 & end with +1 to match existing X arange min & max)
    # or we will see iterated min & max values 
    # use append function twice for front & back side 

    
    if padding_dim == 'X': 
    
        # front side append for X dimension 
        xrdata_pad = xrdata.pad(X=(padding_shape,padding_shape), constant_values = np.nan)
        xrdata_pad = xrdata_pad.assign_coords(X = X_pad)
    elif padding_dim == 'Y':
        # Y_pad only     
        xrdata_pad = xrdata.pad(Y=(padding_shape,padding_shape),constant_values = np.nan)
        xrdata_pad = xrdata_pad.assign_coords(Y = Y_pad)
    
    elif padding_dim == 'XY':
        xrdata_pad = xrdata.pad(X=(padding_shape,padding_shape), Y=(padding_shape,padding_shape),constant_values = np.nan)
        xrdata_pad = xrdata_pad.assign_coords(X = X_pad)
        xrdata_pad = xrdata_pad.assign_coords(Y = Y_pad)
    else: 
        print("choose padding_dim = 'X', 'Y', or 'XY'")
        
    return xrdata_pad


def drift_compensation_y_topo_crrltn (xr_data, y_sub_n=10, padding_shape = 10, drift_interpl_method='nearest'): 
    '''
    input: xr 3D data 
    use grid_xr.topography to calculate Y drift with drift 
    
    use padding_xr function with padding_dims= 'X' only
    
    output: Xr 3D data + padding 
    
    
    '''
    xr_data_topo = xr_data.topography
    xr_data_topo.attrs = xr_data.attrs
    xr_data_pad = padding_xr(xr_data, padding_dim = 'X', padding_shape = padding_shape)

    y_N = len (xr_data_topo.Y)

    y_sub_n = y_sub_n
    drift_interpl_method='nearest'

    # use xr_data for correlation search 
    # apply the correlation shift to the pad results 


    #y_j = 0 
    offset = np.array([0, y_N//2])
    # use for loop 
    print ('drift check with for topography channel(2D data), apply to 3D data')
    for y_j  in range (len (xr_data_topo.Y)//y_sub_n - 1) :
        y_N = len (xr_data_topo.Y)
        #print (y_j)

        Y_sub_n0 = y_j*y_sub_n * xr_data_topo.Y_spacing
        Y_sub_n1 = (y_j+1)*y_sub_n * xr_data_topo.Y_spacing
        Y_sub_n2 = (y_j+2)*y_sub_n * xr_data_topo.Y_spacing
        #print (Y_sub_n0, Y_sub_n1, Y_sub_n2)
        # check Y drift comparision area 
        # use y_sub_n = 5 ==> 0-5, 6-10, 10-5, ... 
        line0 = xr_data_topo.where(xr_data_topo.Y >= Y_sub_n0, drop = True).where (xr_data_topo.Y < Y_sub_n1, drop = True )
        line1 = xr_data_topo.where(xr_data_topo.Y >=  Y_sub_n1, drop = True).where (xr_data_topo.Y <  Y_sub_n2, drop = True )
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

    #offset_accumulation_xr_intrpl.plot()

    # for each lines, adjust value after offset compensated  ==> interpolated again. 
    xr_data_topo_offset = xr_data_topo.copy(deep= True)
    # dont forget deep copy... 

    #offset_accumulation_xr_intrpl
    # for each lines, adjust value after offset compensated  ==> interpolated again. 
    xr_data_offset = xr_data_pad.copy(deep= True)
    # dont forget deep copy... 
    # used padding xr result for applying offset 


    for ch_i, ch_name in enumerate (xr_data_pad): 
        print(ch_i, ch_name)
        # adjust y drift of all channels
        #xr_data_pad[ch_name]
        for y_j, y  in enumerate (xr_data_pad[ch_name].Y):
            new_x_i =  xr_data_offset.isel (Y=y_j).X - offset_accumulation_xr_intrpl.isel(Y=y_j)
            # for each y axis. shift X position 
            #new_x_i
            xr_data_offset_ch_y_j = xr_data_pad[ch_name].isel (Y=y_j).assign_coords({"X": new_x_i}) 
            #xr_data_offset_y_j

            # assign_coord as a new calibrated offset-X coords
            xr_data_offset_ch_y_j_intp = xr_data_offset_ch_y_j.interp(X = xr_data_offset.X)
            #xr_data_offset_y_j_intp

            xr_data_pad[ch_name][dict(Y = y_j)]= xr_data_offset_ch_y_j_intp
            #grid_topo_offset.isel(Y=y_j).topography.values = grid_topo_offest_y_j_intp.topography
            # use [dict()] for assign values , instead of isel() 
            # isel is not working... follow the instruction manual in web.!
    #xr_data_pad

    fig,axs = plt.subplots(ncols = 2, figsize = (8,3))
    xr_data.topography.plot(ax =axs[0], robust = True)
    xr_data_pad.topography.plot(ax =axs[1], robust = True)
    plt.show()
    return xr_data_offset


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

