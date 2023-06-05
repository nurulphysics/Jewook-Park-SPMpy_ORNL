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
# >  **SPMpy** is an open-source project. (Github: https://github.com/jewook-park/SPMpy_ORNL )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 

# # Create pptx file to summarize 2D SPM dataset 
#
#
# * use *fileloading_functions* in SPMpy_ORNL
#     * **Nanonis** 2D data (*.sxm) files  $\to$  **Xarray** (DataSet or DataArray) (or **PANDAS**  (DataFrame) )
# * create pptx file $\to$ add image title & 2D images
#     * add image title ( scan condition info & experimental conditions ) 
#     * topography + LDOS image(locking dI/dV)
#     * generate FFT 
#     * save pptx
#     
#

# # <font color= orange > 0. Preparation  </font>

# + jp-MarkdownHeadingCollapsed=true
#############################
# check all necessary package
#############################

import glob
import os
from warnings import warn

import numpy as np
import pandas as pd

try:
    from ipyfilechooser import FileChooser
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named ipyfilechooser")
    # !pip install ipyfilechooser 
    from ipyfilechooser import FileChooser

try:
    import xrft
except ModuleNotFoundError:
    warn("ModuleNotFoundError: No module named xrft")
    # !pip install xrft
    import xrft

# + id="Qm1zLaTHbSpK"
########################################
#    * Step 1-1
#    : Import necessary packages
#        import modules
#########################################

import glob
import math
import os
from warnings import warn

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns
import skimage
from scipy import signal
from SPMpy_2D_data_analysis_funcs import *
from SPMpy_fileloading_functions import (
    grid2xr,
    grid_line2xr,
    gwy_df_ch2xr,
    gwy_img2df,
    img2xr,
)

# some packages may be yet to be installed
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
 
# -


# # <font color= orange > 1. Choose Folder & DataFrame for files  </font>

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

# # <font color= orange > 2. loading files & data import    </font>

# +
#######

files_df

sxm_file_list_df = files_df[files_df.type == "sxm"]
# file_list_df

# use sxm file list only 
sxm_file_groups = list(set(sxm_file_list_df["group"]))
# file groups
sxm_file_groups
#############################
# sxm file loading by using img2xr
# xr format으로 파일 불러오기
# (e.g.) # img2xr(file_list_df.file_name.iloc[0])
#############################
# spmdata_xr = img2xr(file_list_df.file_name[0])
# -

# #  dual bias scan data sxm 
# * FeTe0.55Se0.45(new)_PtIrTip3_mK_2023_0508_(x0.01Bias_Factor0.01)_P2mV_N2mV_0001
#
#
#

# +
single_sxm_group = files_df [ files_df.group == 'FeTe0.55Se0.45(new)_PtIrTip3_mK_2023_0507_(x1Bias_Factor1)_0'] 
single_sxm = single_sxm_group.file_name.iloc[0]

dual_sxm_group = files_df [files_df.group == 'FeTe0.55Se0.45(new)_PtIrTip3_mK_2023_0508_(x0.01Bias_Factor0.01)_P2mV_N2mV_0']
v = dual_sxm_group.file_name.iloc[0]


# +
# dual_sxm_xr = img2xr(dual_sxm)
# error due to dual bias 


# -

single_sxm_xr = img2xr(single_sxm)
single_sxm_xr

# +
import os
import glob
import numpy as np
import pandas as pd
import scipy as sp
import math
import matplotlib.pyplot as plt
import re

from warnings import warn

try:
    import nanonispy as nap
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named nanonispy')
    # %pip install nanonispy
    import nanonispy as nap

try:
    import xarray as xr
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xarray')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # %pip install xarray 
    import xarray as xr

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named seaborn-image')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # %pip install --upgrade seaborn-image    
    import seaborn_image as isns

NF = nap.read.NanonisFile(dual_sxm)
#NF = nap.read.NanonisFile(single_sxm)
Scan = nap.read.Scan(NF.fname)
#Scan.basename # file name only *.sxm 
#Scan.header # heater dict 
##############################
# -

# ## additional Scan.header  tabs. 
# * between 'T-const' & 'comment'
#
#     * 'multipass-config': {'Record-Ch': ('-1', '-1', '-1', '-1'),
#     * 'Playback': ('FALSE', 'FALSE', 'FALSE', 'FALSE'),
#     * 'Playback-Offset': ('0.000E+0', '0.000E+0', '0.000E+0', '0.000E+0'),
#     * 'BOL-delay_[cycles]': ('40', '1', '40', '1'),
#     * 'Bias_override': ('TRUE', 'TRUE', 'TRUE', 'TRUE'),
#     * 'Bias_override_value': ('2.000E-3', '2.000E-3', '-2.000E-3', '-2.000E-3'),
#     * 'Z_Setp_override': ('FALSE', 'FALSE', 'FALSE', 'FALSE'),
#     * 'Z_Setp_override_value': ('0.000E+0', '0.000E+0', '0.000E+0', '0.000E+0'),
#     * 'Speed_factor': ('1.000', '1.000', '1.000', '1.000')},
#
# ### usually Bias_override_value is the setup. 
#
# ## consider dual bias scan only. 
#     * P1_fwd, P1_bwd, P2_fwd, P2_bwd
#     
#

if 'multipass-config' in Scan.header.keys():
    print ('multipass detected')
    multipass = True
    # add xr attribute 'multipass' = True 
else: pass


# +
if multipass == True: 
    # 1. count number of multi pass = 
    # 2. Pass= 2 or Pass = 3 
    # 3. fwd == bwd? 
        ## P1_fb, P2_fb, P3_fb
        ### or P1_f, P1b, P2f, P2b
        
    signal_keys () 
    z_P1fwd
    z_P1bwd
    LIX_P1fwd
    LIX_P1bwd
    z_P2fwd
    z_P2bwd
    LIX_P2fwd
    LIX_P2bwd
    
else: 
    z_fwd
    z_bwd
    LIX_fwd
    LIX_bwd
    

# +
Scan.signals.keys()

P1_z_keys = [s  for s in Scan.signals.keys()  if "[P1]"  in s  if "Z"  in s]
P2_z_keys = [s  for s in Scan.signals.keys()  if "[P2]"  in s  if "LI"  in s if "X"  in s]

P1_LIX_keys = [s  for s in Scan.signals.keys()  if "[P1]"  in s  if "Z"  in s]
P2_LIX_keys = [s  for s in Scan.signals.keys()  if "[P2]"  in s if "LI"  in s if "X"  in s]


#P2_keys = [s  for s in Scan.signals.keys()  if "[P2]"  in s ]
P2_LIX_keys


# +
Z_P1_fwd = Scan.signals[P1_z_keys[0]]['forward']
Z_P1_bwd = Scan.signals[P1_z_keys[0]]['backward'][:,::-1]
Z_P2_fwd = Scan.signals[P2_z_keys[0]]['forward']
Z_P2_bwd = Scan.signals[P2_z_keys[0]]['backward'][:,::-1]


LIX_P1_fwd = Scan.signals[P1_LIX_keys[0]]['forward']
LIX_P1_bwd = Scan.signals[P1_LIX_keys[0]]['backward'][:,::-1]
Z_P2_fwd = Scan.signals[P2_LIX_keys[0]]['forward']
Z_P2_bwd = Scan.signals[P2_LIX_keys[0]]['backward'][:,::-1]




# +

#Scan.signals.keys()
Scan.signals['Z'].keys()

Scan.signals['Z']['forward'].shape
z_fwd = Scan.signals['Z']['forward']
z_bwd = Scan.signals['Z']['backward'][:,::-1]


#print(Scan.signals.keys())

#print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ])
# 'LI' & 'X' in  channel name (signal.keys) 
LIX_key = [s  for s in Scan.signals.keys()  if "LI"  in s  if "X" in s ]
print(LIX_key)
# chech the LIX is empty or not 
if len(LIX_key) == 0: 
    print("LIX is empty, Current ch substitutes LIX ")
    LIX_fwd  = Scan.signals['Current']['forward']
    LIX_bwd  = Scan.signals['Current']['backward'][:,::-1]
else:
    # 0 is fwd, 1 is bwd 
    LIX_fwd  = Scan.signals[LIX_key[0]]['forward']
    LIX_bwd  = Scan.signals[LIX_key[0]]['backward'][:,::-1]


# +
def img2xr (loading_sxm_file, center_offset = False):
    # updated for multipass 
    # import necessary module 
    import os
    import glob
    import numpy as np
    import pandas as pd
    import scipy as sp
    import math
    import matplotlib.pyplot as plt
    import re

    from warnings import warn

    try:
        import nanonispy as nap
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named nanonispy')
        # %pip install nanonispy
        import nanonispy as nap

    try:
        import xarray as xr
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named xarray')
        # #!pip install --upgrade scikit-image == 0.19.0.dev0
        # %pip install xarray 
        import xarray as xr

    try:
        import seaborn_image as isns
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named seaborn-image')
        # #!pip install --upgrade scikit-image == 0.19.0.dev0
        # %pip install --upgrade seaborn-image    
        import seaborn_image as isns


    NF = nap.read.NanonisFile(loading_sxm_file)
    Scan = nap.read.Scan(NF.fname)
    #Scan.basename # file name only *.sxm 
    #Scan.header # heater dict 
    ##############################
    # Scan conditions from the header
    V_b = float(Scan.header['bias>bias (v)'])
    I_t = float(Scan.header['z-controller>setpoint'])

    [size_x,size_y] = Scan.header['scan_range']
    [cntr_x, cntr_y] = Scan.header['scan_offset']
    [dim_px,dim_py] = Scan.header['scan_pixels']
    [step_dx,step_dy] = [ size_x/dim_px, size_y/dim_py] 
    #pixel_size = size / pixel
    Rot_Rad = math.radians( float(Scan.header['scan_angle'])) 
    #str --> degree to radian 

    print ('scan direction (up/down): ', Scan.header['scan_dir'])
    ###   nX, nY --> x,y real scale  np array 
    nX = np.array([step_dx*(i+1/2) for i in range (0,dim_px)])
    nY = np.array([step_dy*(i+1/2) for i in range (0,dim_py)])
    # nX,nY for meshgrid (start from 1/2, not 0 )
    # x, y steps with dimension 
    # In case of rotation ==0
    x = cntr_x - size_x + nX
    y = cntr_y - size_y + nY
    # real XY position in nm scale, Center position & scan_szie + XY position
    
    #########################################################################
    # np.meshgrid 
    x_mesh_0, y_mesh_0 = np.meshgrid(nX, nY)
    x_mesh = cntr_x - size_x + x_mesh_0
    y_mesh = cntr_y - size_y + y_mesh_0 
    # if there is rotation 
    x_mesh_r   =  np.cos(Rot_Rad)*x_mesh_0 + np.sin(Rot_Rad)*y_mesh_0  # "cloclwise"
    y_mesh_r   = -np.sin(Rot_Rad)*x_mesh_0 + np.cos(Rot_Rad)*y_mesh_0
    #########################################################################
    # image title 
    # if there is rotation ( rot !=0 ), display it. 
    if Rot_Rad ==0 : 
        image_title = Scan.basename[:-4] + '\n' + \
            str(round(size_x* 1E9 )) + ' nm x ' + \
                str(round(size_y* 1E9 )) + ' nm '  +\
                    ' V = '+ str(V_b) + ' V ' +\
                        ' I = ' + str(round(I_t *1E12)) + ' pA ' 
    else: 
        image_title = Scan.basename[:-4] + '\n' + \
            str(round(size_x* 1E9 )) + ' nm x ' + \
                str(round(size_y* 1E9 )) + ' nm '  +\
                    ' V = '+ str(V_b) + ' V ' +\
                        ' I = ' + str(round(I_t *1E12)) + ' pA ' +\
                            ' R = ' + str(int(math.degrees(Rot_Rad))) + 'deg'
    print(image_title)
    #########################################################################
    # scan channels in DataFrame

    if 'multipass-config' in Scan.header.keys():
        print ('multipass detected')
        multipass = True
        # add xr attribute 'multipass' = True 
        Z_P1bwd = Scan.signals[P1_z_keys[0]]['forward']
        Z_P1bwd = Scan.signals[P1_z_keys[0]]['backward'][:,::-1]
        Z_P2fwd = Scan.signals[P2_z_keys[0]]['forward']
        Z_P2bwd = Scan.signals[P2_z_keys[0]]['backward'][:,::-1]

        LIX_P1fwd = Scan.signals[P1_LIX_keys[0]]['forward']
        LIX_P1bwd = Scan.signals[P1_LIX_keys[0]]['backward'][:,::-1]
        LIX_P2fwd = Scan.signals[P2_LIX_keys[0]]['forward']
        LIX_P2bwd = Scan.signals[P2_LIX_keys[0]]['backward'][:,::-1]
                
        data_vars_name = [Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_Pbwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd]
    else:    
    

        #Scan.signals.keys()
        Scan.signals['Z'].keys()

        Scan.signals['Z']['forward'].shape
        z_fwd = Scan.signals['Z']['forward']
        z_bwd = Scan.signals['Z']['backward'][:,::-1]


        #print(Scan.signals.keys())

        #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ])
        # 'LI' & 'X' in  channel name (signal.keys) 
        LIX_key = [s  for s in Scan.signals.keys()  if "LI"  in s  if "X" in s ]
        print(LIX_key)
        # chech the LIX is empty or not 
        if len(LIX_key) == 0: 
            print("LIX is empty, Current ch substitutes LIX ")
            LIX_fwd  = Scan.signals['Current']['forward']
            LIX_bwd  = Scan.signals['Current']['backward'][:,::-1]
        else:
            # 0 is fwd, 1 is bwd 
            LIX_fwd  = Scan.signals[LIX_key[0]]['forward']
            LIX_bwd  = Scan.signals[LIX_key[0]]['backward'][:,::-1]

        #LIX_fwd = Scan.signals['LI_Demod_1_X']['forward']
        #LIX_bwd = Scan.signals['LI_Demod_1_X']['backward'][:,::-1]
        # LIX channel name varies w.r.t nanonis version 

        # same for LIY --> update later.. if needed 
        #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ])
        # 'LI' & 'Y' in  channel name (signal.keys) 
        #LIY_keys = [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ]
        # 0 is fwd, 1 is bwd 
        #LIY_fwd, LIY_bwd = Gr.signals[LIY_keys[0]] ,Gr.signals[LIY_keys[1] ]

        #bwd channel : opposite data direction in X ==> reverse it. 

    
    ########################################
    if Scan.header['scan_dir'] == 'down':
        if multipass == True : 
            for data_var_name in data_vars_name : 
                data_var_name = data_var_name[::-1,:]
            
        else: 
            z_fwd = z_fwd[::-1,:]
            z_bwd = z_bwd[::-1,:]
            LIX_fwd = LIX_fwd[::-1,:]
            LIX_bwd = LIX_bwd[::-1,:]
    # if scan_direction == down, flip the data (Y)
    ########################################
    if multipass == True :
        Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_Pbwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd
        
        Z_P1fwd_df  =pd.DataFrame(Z_P1fwd)
        Z_P1fwd_df.index.name ='row_y'
        Z_P1fwd_df.columns.name ='col_x'
        
        Z_P1bwd_df  =pd.DataFrame(Z_P1bwd)
        Z_P1bwd_df.index.name ='row_y'
        Z_P1bwd_df.columns.name ='col_x'
        
        LIX_P1fwd_df  =pd.DataFrame(LIX_P1fwd)
        LIX_P1fwd_df.index.name ='row_y'
        LIX_P1fwd_df.columns.name ='col_x'
        
        LIX_P1bwd_df  =pd.DataFrame(LIX_P1bwd)
        LIX_P1bwd_df.index.name ='row_y'
        LIX_P1bwd_df.columns.name ='col_x'
        
        Z_P2fwd_df  =pd.DataFrame(Z_P2fwd)
        Z_P2fwd_df.index.name ='row_y'
        Z_P2fwd_df.columns.name ='col_x'
        
        Z_P2bwd_df  =pd.DataFrame(Z_P2bwd)
        Z_P2bwd_df.index.name ='row_y'
        Z_P2bwd_df.columns.name ='col_x'
        
        LIX_P2fwd_df  =pd.DataFrame(LIX_P2fwd)
        LIX_P2fwd_df.index.name ='row_y'
        LIX_P2fwd_df.columns.name ='col_x'
        
        LIX_P2bwd_df  =pd.DataFrame(LIX_P2bwd)
        LIX_P2bwd_df.index.name ='row_y'
        LIX_P2bwd_df.columns.name ='col_x'
               # save data channels as DataFrame
        ########################################
        Z_P1fwd_df = Z_P1fwd_df.fillna(Z_P1fwd_df.mean())
        Z_P1bwd_df = Z_P1bwd_df.fillna(Z_P1bwd_df.mean())
        Z_P2fwd_df = Z_P2fwd_df.fillna(Z_P2fwd_df.mean())
        Z_P2bwd_df = Z_P2bwd_df.fillna(Z_P2bwd_df.mean())

        LIX_P1fwd_df = LIX_P1fwd_df.fillna(LIX_P1fwd_df.mean())
        LIX_P1bwd_df = LIX_P1bwd_df.fillna(LIX_P1bwd_df.mean())
        LIX_P2fwd_df = LIX_P2fwd_df.fillna(LIX_P2fwd_df.mean())
        LIX_P2bwd_df = LIX_P2bwd_df.fillna(LIX_P2bwd_df.mean())
          # in case of incompleted scan ==> np.nan in data point, ==> fillna()
        # how about fill df.mean ? 
    else : 
    ########################################

        z_fwd_df = pd.DataFrame(z_fwd)
        z_fwd_df.index.name ='row_y'
        z_fwd_df.columns.name ='col_x'

        z_bwd_df = pd.DataFrame(z_bwd)
        z_bwd_df.index.name ='row_y'
        z_bwd_df.columns.name ='col_x'

        LIX_fwd_df = pd.DataFrame(LIX_fwd)
        LIX_fwd_df.index.name ='row_y'
        LIX_fwd_df.columns.name ='col_x'

        LIX_bwd_df = pd.DataFrame(LIX_bwd)
        LIX_bwd_df.index.name ='row_y'
        LIX_bwd_df.columns.name ='col_x'
            # save data channels as DataFrame
        ########################################
        z_fwd_df = z_fwd_df.fillna(0)
        z_bwd_df = z_bwd_df.fillna(0)
        LIX_fwd_df = LIX_fwd_df.fillna(0)   
        LIX_bwd_df = LIX_bwd_df.fillna(0)
        # in case of incompleted scan ==> np.nan in data point, ==> fillna()
        # how about fill df.mean ? 
            #  we can keep the max & min values 
            # or just leave as np.nan --> FFT calc. issue. 
            # 2D sxm summary --> fillna(0) , otherwise --> leave it as nan
        ########################################
-----

continu here





----
    ############################
    # conver to DataFrame (PANDAS) 
    z_LIX_fNb_df = pd.concat([z_fwd_df.stack(),
                              z_bwd_df.stack(),
                              LIX_fwd_df.stack(),
                              LIX_bwd_df.stack()], axis = 1)
    # set colunm name for new DataFrame
    z_LIX_fNb_df.columns =['z_fwd','z_bwd', 'LIX_fwd','LIX_bwd']
    # z_LIX_fNb_df
    ############################
    # conver to xarray 
    ############################
    z_LIX_fNb_xr = z_LIX_fNb_df.to_xarray()
    # rename coord as "X", "Y" 
    z_LIX_fNb_xr = z_LIX_fNb_xr.rename(
        {"row_y": "Y", "col_x":"X"})
    # real size of XY 
    z_LIX_fNb_xr= z_LIX_fNb_xr.assign_coords(
        X = z_LIX_fNb_xr.X.values *step_dx, 
        Y = z_LIX_fNb_xr.Y.values *step_dy )
    # XY axis: 0 ~ size_XY

    ############################
    # check the XY ratio 
    ############################
    if  size_x == size_y : 
        pass
    else : 
        print ('size_x != size_y')
    # if xy size is not same, report it! 

    if step_dx != step_dy :
        xystep_ratio = step_dy/step_dx # check the XY pixel_ratio
        X_interp = np.linspace(z_LIX_fNb_xr.X[0], z_LIX_fNb_xr.X[-1], z_LIX_fNb_xr.X.shape[0]*1)
        step_dx = step_dx # step_dx check 

        Y_interp = np.linspace(z_LIX_fNb_xr.Y[0], z_LIX_fNb_xr.Y[-1], int(z_LIX_fNb_xr.Y.shape[0]*xystep_ratio)) 
        step_dy = step_dy/ xystep_ratio # step_dy check 

        # interpolation ratio should be int
        z_LIX_fNb_xr= z_LIX_fNb_xr.interp(X = X_interp, Y = Y_interp, method="linear")
        print('step_dx/step_dy = ', xystep_ratio)
        print ('z_LIX_fNb_xr ==> reshaped')
    else: 
        z_LIX_fNb_xr =z_LIX_fNb_xr
        print('step_dx == step_dy')
    #print('z_LIX_fNb_xr', 'step_dx, step_dy = ',  z_LIX_fNb_xr.dims)
    print('z_LIX_fNb_xr', 'step_dx, step_dy = ', 
          re.findall('\{([^}]+)', str(z_LIX_fNb_xr.dims)))
    # regex practice


    ##########
    #################################
    # assign attributes 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
    # attribute 'multipass' set
    z_LIX_fNb_xr.attrs['multipass'] = multipass
    
    z_LIX_fNb_xr.attrs['title'] = image_title
    if 'Wtip' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'W'
    elif 'Ni_tip' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'Ni'
    elif 'Co_coated' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'Co_coated'
    elif 'AFM' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'AFM'
    else: 
        z_LIX_fNb_xr.attrs['tip'] = 'To Be Announced'
        print('tip material will be announced')
    
    if 'NbSe2' in image_title:
        z_LIX_fNb_xr.attrs['sample'] = 'NbSe2'
    elif 'Cu(111)' in image_title:
        z_LIX_fNb_xr.attrs['sample'] = 'Cu(111)'
    elif 'Au(111)' in image_title:
        z_LIX_fNb_xr.attrs['sample'] = 'Au(111)'
    elif 'MoS2' in image_title:
        z_LIX_fNb_xr.attrs['sample'] = 'MoS2'
    elif 'FeTe0.55Se0.45' in image_title:
        z_LIX_fNb_xr.attrs['sample'] = 'FeTe0.55Se0.45'
    else: 
        z_LIX_fNb_xr.attrs['sample'] = 'To Be Announced'
        print('sample type will be announced')
    
    z_LIX_fNb_xr.attrs['image_size'] = [size_x,size_y]
    z_LIX_fNb_xr.attrs['X_spacing'] = step_dx
    z_LIX_fNb_xr.attrs['Y_spacing'] = step_dy    
    z_LIX_fNb_xr.attrs['freq_X_spacing'] = 1/step_dx
    z_LIX_fNb_xr.attrs['freq_Y_spacing'] = 1/step_dy

    # in case of real X Y ( center & size of XY)
    if center_offset == True:
        # move the scan center postion in real scanner field of view
        z_LIX_fNb_xr.assign_coords(X=(z_LIX_fNb_xr.X + cntr_x -  size_x/2))
        z_LIX_fNb_xr.assign_coords(Y=(z_LIX_fNb_xr.Y + cntr_y -  size_y/2))
    else :
        pass
        # (0,0) is the origin of image 


    #################################
    # test & how to use xr data 
    # z_LIX_fNb_xr  # xr dataset (with data array channels )
    #z_LIX_fNb_xr.z_fwd # select data channel
    #z_LIX_fNb_xr.data_vars # data channels check 
    #z_LIX_fNb_xr.z_fwd.values  # to call data array in nd array 
    #z_yLIX_fNb_xr.dims # data channel dimension (coords) 
    #z_LIX_fNb_xr.coords # data  channel coordinates check 
    #z_LIX_fNb_xr.attrs # data  channel attributes check 

    return z_LIX_fNb_xr
