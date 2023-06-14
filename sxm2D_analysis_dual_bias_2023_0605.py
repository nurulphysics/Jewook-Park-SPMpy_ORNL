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
dual_sxm = dual_sxm_group.file_name.iloc[0]


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
#NF = nap.read.NanonisFile(single_sxm)M
Scan = nap.read.Scan(NF.fname)
#Scan.basename # file name only *.sxm 
#Scan.header # heater dict 
##############################

## additional Scan.header  tabs. 
'''
* between 'T-const' & 'comment'

    * 'multipass-config': {'Record-Ch': ('-1', '-1', '-1', '-1'),
    * 'Playback': ('FALSE', 'FALSE', 'FALSE', 'FALSE'),
    * 'Playback-Offset': ('0.000E+0', '0.000E+0', '0.000E+0', '0.000E+0'),
    * 'BOL-delay_[cycles]': ('40', '1', '40', '1'),
    * 'Bias_override': ('TRUE', 'TRUE', 'TRUE', 'TRUE'),
    * 'Bias_override_value': ('2.000E-3', '2.000E-3', '-2.000E-3', '-2.000E-3'),
    * 'Z_Setp_override': ('FALSE', 'FALSE', 'FALSE', 'FALSE'),
    * 'Z_Setp_override_value': ('0.000E+0', '0.000E+0', '0.000E+0', '0.000E+0'),
    * 'Speed_factor': ('1.000', '1.000', '1.000', '1.000')},

### usually Bias_override_value is the setup. 

## consider dual bias scan only. 
    * P1_fwd, P1_bwd, P2_fwd, P2_bwd
'''    


if 'multipass-config' in Scan.header.keys():
    print ('multipass detected')
    multipass = True
    # add xr attribute 'multipass' = True 

else: pass



if 'multipass-config' in Scan.header.keys():
    print ('multipass detected')
    multipass = True
    
    
    
    P1_Z_keys =  [s  for s in Scan.signals.keys()  if "P1"  in s  if "Z" in s ]
    P2_Z_keys =  [s  for s in Scan.signals.keys()  if "P2"  in s  if "Z" in s ]
    
    P1_LIX_keys =  [s  for s in Scan.signals.keys()  if "P1"  in s  if "LI" in s if "X" in s ]
    P2_LIX_keys =  [s  for s in Scan.signals.keys()  if "P2"  in s  if "LI" in s if "X" in s ]
    
    
    # add xr attribute 'multipass' = True 
    Z_P1fwd = Scan.signals[P1_Z_keys[0]]['forward']
    Z_P1bwd = Scan.signals[P1_Z_keys[0]]['backward'][:,::-1]
    Z_P2fwd = Scan.signals[P2_Z_keys[0]]['forward']
    Z_P2bwd = Scan.signals[P2_Z_keys[0]]['backward'][:,::-1]

    LIX_P1fwd = Scan.signals[P1_LIX_keys[0]]['forward']
    LIX_P1bwd = Scan.signals[P1_LIX_keys[0]]['backward'][:,::-1]
    LIX_P2fwd = Scan.signals[P2_LIX_keys[0]]['forward']
    LIX_P2bwd = Scan.signals[P2_LIX_keys[0]]['backward'][:,::-1]

    data_vars_name = [Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_P1bwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd]
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
    #Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_Pbwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd

    Z_P1fwd_df  = pd.DataFrame(Z_P1fwd)
    Z_P1fwd_df.index.name ='row_y'
    Z_P1fwd_df.columns.name ='col_x'

    Z_P1bwd_df  = pd.DataFrame(Z_P1bwd)
    Z_P1bwd_df.index.name ='row_y'
    Z_P1bwd_df.columns.name ='col_x'

    LIX_P1fwd_df  = pd.DataFrame(LIX_P1fwd)
    LIX_P1fwd_df.index.name ='row_y'
    LIX_P1fwd_df.columns.name ='col_x'

    LIX_P1bwd_df  = pd.DataFrame(LIX_P1bwd)
    LIX_P1bwd_df.index.name ='row_y'
    LIX_P1bwd_df.columns.name ='col_x'

    Z_P2fwd_df  = pd.DataFrame(Z_P2fwd)
    Z_P2fwd_df.index.name ='row_y'
    Z_P2fwd_df.columns.name ='col_x'

    Z_P2bwd_df  = pd.DataFrame(Z_P2bwd)
    Z_P2bwd_df.index.name ='row_y'
    Z_P2bwd_df.columns.name ='col_x'

    LIX_P2fwd_df  = pd.DataFrame(LIX_P2fwd)
    LIX_P2fwd_df.index.name ='row_y'
    LIX_P2fwd_df.columns.name ='col_x'

    LIX_P2bwd_df  = pd.DataFrame(LIX_P2bwd)
    LIX_P2bwd_df.index.name ='row_y'
    LIX_P2bwd_df.columns.name ='col_x'
           # save data channels as DataFrame

    ########################################
    Z_P1fwd_df = Z_P1fwd_df.fillna(Z_P1fwd.mean())
    Z_P1bwd_df = Z_P1bwd_df.fillna(Z_P1bwd.mean())
    Z_P2fwd_df = Z_P2fwd_df.fillna(Z_P2fwd.mean())
    Z_P2bwd_df = Z_P2bwd_df.fillna(Z_P2bwd.mean())
    # fillna using previous numpy array. 
    LIX_P1fwd_df = LIX_P1fwd_df.fillna(LIX_P1fwd.mean())
    LIX_P1bwd_df = LIX_P1bwd_df.fillna(LIX_P1bwd.mean())
    LIX_P2fwd_df = LIX_P2fwd_df.fillna(LIX_P2fwd.mean())
    LIX_P2bwd_df = LIX_P2bwd_df.fillna(LIX_P2bwd.mean())
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
    

if multipass == True :
    ############################
    # conver to DataFrame (PANDAS) 
    z_LIX_fNb_df = pd.concat([Z_P1fwd_df.stack(),Z_P1bwd_df.stack(),
                              LIX_P1fwd_df.stack(),LIX_P1bwd_df.stack(),
                              Z_P2fwd_df.stack(),Z_P2bwd_df.stack(),
                              LIX_P2fwd_df.stack(),LIX_P2bwd_df.stack()],
                             axis = 1)
    # set colunm name for new DataFrame
    z_LIX_fNb_df.columns =['Z_P1fwd','Z_P1bwd', 'LIX_P1fwd','LIX_P1bwd','Z_P2fwd','Z_P2bwd', 'LIX_P2fwd','LIX_P2bwd']
    # z_LIX_fNb_df      

else:
    ############################
    # conver to DataFrame (PANDAS) 
    z_LIX_fNb_df = pd.concat([z_fwd_df.stack(),
                              z_bwd_df.stack(),
                              LIX_fwd_df.stack(),
                              LIX_bwd_df.stack()], axis = 1)
    # set colunm name for new DataFrame
    z_LIX_fNb_df.columns =['z_fwd','z_bwd', 'LIX_fwd','LIX_bwd']
    # z_LIX_fNb_df


z_LIX_fNb_df

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
# -

z_LIX_fNb_xr


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



# +


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
#Scan.header['multipass-config'].keys()
round(float(Scan.header['multipass-config']['Bias_override_value'][1])*1000,2)


'Pass1 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][0])*1000,2)) +' mV' + '/ Pass1 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][1])*1000,2)) +' mV' + '// Pass2 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][2])*1000,2)) +' mV' + '/ Pass2 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][3])*1000,2)) +' mV'



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


# -

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

    
    #########################################################################
    # scan channels in DataFrame

    if 'multipass-config' in Scan.header.keys():
        print ('multipass detected')
        multipass = True
        # add xr attribute 'multipass' = True 

    else: pass


    ####################################################
    # check image names --> multi pass? --> rotate? 
    if multipass == True :
            # image title 

        # multi pass bias voltage in str
        # 'Pass1 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][0])*1000,2)) +' mV' +
        # '/ Pass1 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][1])*1000,2)) +' mV' +
        # '// Pass2 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][2])*1000,2)) +' mV' + 
        # '/ Pass2 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][3])*1000,2)) +' mV'

        # if there is rotation ( rot !=0 ), display it. 
        if Rot_Rad ==0 : 
            image_title = Scan.basename[:-4] + '\n' + \
            str(round(size_x* 1E9 )) + ' nm x ' + \
            str(round(size_y* 1E9 )) + ' nm '  +\
            ' V = '+ str(V_b) + ' V ' +\
            ' I = ' + str(round(I_t *1E12)) + ' pA '  + '\n' + \
            'Pass1 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][0])*1000,2)) +' mV' +\
            '/ Pass1 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][1])*1000,2)) +' mV' +\
            '// Pass2 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][2])*1000,2)) +' mV' + \
            '/ Pass2 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][3])*1000,2)) +' mV'
            
        else: 
            image_title = Scan.basename[:-4] + '\n' + \
            str(round(size_x* 1E9 )) + ' nm x ' + \
            str(round(size_y* 1E9 )) + ' nm '  +\
            ' V = '+ str(V_b) + ' V ' +\
            ' I = ' + str(round(I_t *1E12)) + ' pA ' +\
            ' R = ' + str(int(math.degrees(Rot_Rad))) + 'deg' +\
            'Pass1 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][0])*1000,2)) +' mV' +\
            '/ Pass1 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][1])*1000,2)) +' mV' +\
            '// Pass2 fwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][2])*1000,2)) +' mV' + \
            '/ Pass2 bwd @' + str(round(float(Scan.header['multipass-config']['Bias_override_value'][3])*1000,2)) +' mV'
            
        print(image_title)

        
    else : 
        # normal without multi pass. only check rot 

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


    
    ######################################################
    if multipass == True :

        P1_Z_keys =  [s  for s in Scan.signals.keys()  if "P1"  in s  if "Z" in s ]
        P2_Z_keys =  [s  for s in Scan.signals.keys()  if "P2"  in s  if "Z" in s ]

        P1_LIX_keys =  [s  for s in Scan.signals.keys()  if "P1"  in s  if "LI" in s if "X" in s ]
        P2_LIX_keys =  [s  for s in Scan.signals.keys()  if "P2"  in s  if "LI" in s if "X" in s ]


        # add xr attribute 'multipass' = True 
        Z_P1fwd = Scan.signals[P1_Z_keys[0]]['forward']
        Z_P1bwd = Scan.signals[P1_Z_keys[0]]['backward'][:,::-1]
        Z_P2fwd = Scan.signals[P2_Z_keys[0]]['forward']
        Z_P2bwd = Scan.signals[P2_Z_keys[0]]['backward'][:,::-1]

        LIX_P1fwd = Scan.signals[P1_LIX_keys[0]]['forward']
        LIX_P1bwd = Scan.signals[P1_LIX_keys[0]]['backward'][:,::-1]
        LIX_P2fwd = Scan.signals[P2_LIX_keys[0]]['forward']
        LIX_P2bwd = Scan.signals[P2_LIX_keys[0]]['backward'][:,::-1]

        data_vars_name = [Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_P1bwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd]
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
        #Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_Pbwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd

        Z_P1fwd_df  = pd.DataFrame(Z_P1fwd)
        Z_P1fwd_df.index.name ='row_y'
        Z_P1fwd_df.columns.name ='col_x'

        Z_P1bwd_df  = pd.DataFrame(Z_P1bwd)
        Z_P1bwd_df.index.name ='row_y'
        Z_P1bwd_df.columns.name ='col_x'

        LIX_P1fwd_df  = pd.DataFrame(LIX_P1fwd)
        LIX_P1fwd_df.index.name ='row_y'
        LIX_P1fwd_df.columns.name ='col_x'

        LIX_P1bwd_df  = pd.DataFrame(LIX_P1bwd)
        LIX_P1bwd_df.index.name ='row_y'
        LIX_P1bwd_df.columns.name ='col_x'

        Z_P2fwd_df  = pd.DataFrame(Z_P2fwd)
        Z_P2fwd_df.index.name ='row_y'
        Z_P2fwd_df.columns.name ='col_x'

        Z_P2bwd_df  = pd.DataFrame(Z_P2bwd)
        Z_P2bwd_df.index.name ='row_y'
        Z_P2bwd_df.columns.name ='col_x'

        LIX_P2fwd_df  = pd.DataFrame(LIX_P2fwd)
        LIX_P2fwd_df.index.name ='row_y'
        LIX_P2fwd_df.columns.name ='col_x'

        LIX_P2bwd_df  = pd.DataFrame(LIX_P2bwd)
        LIX_P2bwd_df.index.name ='row_y'
        LIX_P2bwd_df.columns.name ='col_x'
               # save data channels as DataFrame

        ########################################
        Z_P1fwd_df = Z_P1fwd_df.fillna(Z_P1fwd.mean())
        Z_P1bwd_df = Z_P1bwd_df.fillna(Z_P1bwd.mean())
        Z_P2fwd_df = Z_P2fwd_df.fillna(Z_P2fwd.mean())
        Z_P2bwd_df = Z_P2bwd_df.fillna(Z_P2bwd.mean())
        # fillna using previous numpy array. 
        LIX_P1fwd_df = LIX_P1fwd_df.fillna(LIX_P1fwd.mean())
        LIX_P1bwd_df = LIX_P1bwd_df.fillna(LIX_P1bwd.mean())
        LIX_P2fwd_df = LIX_P2fwd_df.fillna(LIX_P2fwd.mean())
        LIX_P2bwd_df = LIX_P2bwd_df.fillna(LIX_P2bwd.mean())
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


    if multipass == True :
        ############################
        # conver to DataFrame (PANDAS) 
        z_LIX_fNb_df = pd.concat([Z_P1fwd_df.stack(),Z_P1bwd_df.stack(),
                                  LIX_P1fwd_df.stack(),LIX_P1bwd_df.stack(),
                                  Z_P2fwd_df.stack(),Z_P2bwd_df.stack(),
                                  LIX_P2fwd_df.stack(),LIX_P2bwd_df.stack()],
                                 axis = 1)
        # set colunm name for new DataFrame
        z_LIX_fNb_df.columns =['Z_P1fwd','Z_P1bwd', 'LIX_P1fwd','LIX_P1bwd','Z_P2fwd','Z_P2bwd', 'LIX_P2fwd','LIX_P2bwd']
        # z_LIX_fNb_df      

    else:
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
    z_LIX_fNb_xr.attrs['multipass_Ch#'] = int (len(data_vars_name)/4  )
    # data_vars_names  =  [Z_P1fwd, Z_P1bwd, LIX_P1fwd,LIX_P1bwd, Z_P2fwd, Z_P2bwd, LIX_P2fwd,LIX_P2bwd]
    z_LIX_fNb_xr.attrs['title'] = image_title
    if 'Wtip' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'W'
    elif 'PtIr' in image_title:
        z_LIX_fNb_xr.attrs['tip'] = 'PtIr'
    elif '_Ni' in image_title:
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

dual_xr  =  img2xr(dual_sxm)
dual_xr

# +
## split dual XR 

dual_xr_P1 = dual_xr.drop(['Z_P2fwd', 'Z_P2bwd','LIX_P2fwd', 'LIX_P2bwd'])
dual_xr_P2 = dual_xr.drop(['Z_P1fwd', 'Z_P1bwd','LIX_P1fwd', 'LIX_P1bwd'])

# rename channel names after split dual XR 

dual_xr_P1 = dual_xr_P1.rename ({'Z_P1fwd': 'Z_fwd', 'Z_P1bwd': 'Z_bwd', 'LIX_P1fwd': 'LIX_fwd', 'LIX_P1bwd': 'LIX_bwd'})
dual_xr_P2 = dual_xr_P2.rename ({'Z_P2fwd': 'Z_fwd', 'Z_P2bwd': 'Z_bwd', 'LIX_P2fwd': 'LIX_fwd', 'LIX_P2bwd': 'LIX_bwd'})


dual_xr_P1
# -

#dual_xr_P1.title.split('Pass1')
dual_xr_P1.title.split('Pass2')

dual_xr_P1.title.split('//')[0]

dual_xr_P1.title = dual_xr_P1.title.split('//')[0]

dual_xr_P1.attrs['title'] =  dual_xr_P1.title.split('//')[0]

dual_xr_P2.attrs['title'] = dual_xr_P2.title.split('Pass1')[0]+dual_xr_P2.title.split('//')[-1]

dual_xr_P2.title.split('Pass1')[0]+dual_xr_P2.title.split('//')[-1]

dual_xr_P2.title.split('//')[-1]


# + id="LtsdRqHwVAu2" jp-MarkdownHeadingCollapsed=true
#######################################
# plot Xarray (xr) data set with isns
###############\###############\
# len(z_LIX_fNb_xr_intrp.data_vars) # check xr DataArray number
 #######################
def xr_isns_plot_r_space(xrdata,
                         ncols = 2,
                         figsize = (6,6)): 
    """
    display xr DATA Array channels 
    use isns. 'nm' unit, 
    Parameters
    ----------
    xrdata : Xarray DataSet TYPE
        DESCRIPTION.
    ncols : Integer TYPE, optional
        DESCRIPTION. The default is 2.
        number of columns to grid image display
    figsize : tuple TYPE, optional
        DESCRIPTION. The default is (6,6).
        out put figure size 

    Returns
    -------
    fig :image show TYPE
        DESCRIPTION.
        need to chekc the figure saving 
        
    """
    # aspect ratio check 
    [size_x, size_y] = xrdata.image_size
    step_dx = size_x/len(xrdata.X)
    step_dy = size_y/len(xrdata.Y)
    scan_aspect_ratio = (size_x/len(xrdata.X))/(size_y/len(xrdata.Y))
    if scan_aspect_ratio == 1: 
        cbar_show = True
    else:
        cbar_show = False
    ####################################
    isns.set_image(cmap='viridis', origin ="lower")
    fig,axes = plt.subplots(ncols = ncols,
                            nrows = len(xrdata.data_vars)//ncols+1,
                            figsize = figsize)
    axs = axes.ravel()
    axs = trim_axs(axs, len(xrdata.data_vars))
    # triming first with respect to # of data channel 
    isns.set_image(origin='lower')   #  set image  direction
    
    for i,i_channels in enumerate(xrdata):
        isns_channels= i_channels+'_isns'
        print(isns_channels)
        if 'z_' in  i_channels:
            cmap =  'copper'
        elif 'Z_' in  i_channels:
            cmap =  'copper'
        elif 'LIX_' in  i_channels:
            cmap = 'bwr'
        isns_channels = isns.imshow(xrdata[i_channels],
                                    ax =  axs[i],
                                    cbar = cbar_show,
                                    dx = step_dx*1E9,
                                    units = "nm",
                                    cmap = cmap,
                                    robust = True)
        axs[i].set_title(i_channels, loc='left', fontsize = 'small')
        #################################
        if scan_aspect_ratio != 1: 
                fig.colorbar(isns_channels.get_children()[-2],  
                            fraction = 0.045, 
                            ax = axs[i])  
        ################################
        # colorbar setting separately 
        ############################## 
        if 'ref_lattice_a0' in xrdata.attrs:
            ref_lattice_r0 = xrdata.attrs['ref_lattice_a0'] # kspace atomic lattice_k0
            ref_6p_radious = ref_lattice_r0/xrdata.attrs['X_spacing']
        else: pass

    # 4channel 2x2 
    fig.suptitle(xrdata.title, fontsize = 'small', position=(0.5, 1.0+0.05) )
    fig.tight_layout()
    isns.reset_defaults()
    plt.show()
    return fig
# test
# xrdata_set_isns_plot_r_space(z_LIX_fNb_xr_intrp)


#####################################################################
def xr_isns_plot_k_space(xrdata_fft,
                         nrows = 2, 
                         ncols = 2,
                         figsize =  (8,4), 
                         zoom_in_fft = True,
                         zoom_in_expand = 3): 
    """
    display xr DATA Array channels after FFT 
    (k-space)
    default cmap = 'viridis'
    # use isns. 'nm' unit, 
    Parameters
    ----------
    xrdata_fft : Xarray DataSet TYPE
        DESCRIPTION.
        xrdata_fft  for k space plot 
    ncols : Integer TYPE, optional
        DESCRIPTION. The default is 4.
        number of columns to grid image display
    figsize : tuple TYPE, optional
        DESCRIPTION. The default is (8,4).
        out put figure size
    zoom_in_fft : Boolean TYPE, optional
        DESCRIPTION. The default is True.
        check the zoomin or not 
    zoom_in_expand :  Integer TYPE, optional
        DESCRIPTION. The default is 3.
        Zoom in area : ref_lattice_k0 * zoom_in_expand

    Returns
    -------
    fig : out figure TYPE
        DESCRIPTION.
        check the saving figure results. 
        

    """
    # aspect ratio check 
    [size_x, size_y] = xrdata_fft.image_size
    step_dx = size_x/len(xrdata_fft.freq_X)
    step_dy = size_y/len(xrdata_fft.freq_Y)
    scan_aspect_ratio = (size_x/len(xrdata_fft.freq_X))/(size_y/len(xrdata_fft.freq_Y))
    if scan_aspect_ratio == 1: 
        cbar_show = True
    else:
        cbar_show = False
    #######################################
    isns.set_image(cmap='cividis', origin ="lower")
    
    
    #  set image  direction
    fig,axes = plt.subplots(ncols = ncols,
                            nrows = len(xrdata_fft.data_vars)//ncols+1,
                            figsize = figsize)
    axs = axes.ravel()
    axs = trim_axs(axs, len(xrdata_fft.data_vars))
    # triming first with respect to # of data channel 
    for i,i_channels in enumerate(xrdata_fft):
        if 'z_' in i_channels:
            cmap = 'Greys'
        elif 'Z_' in i_channels:
            cmap = 'Greys'
        elif 'LIX_' in i_channels:
            cmap = 'Blues'
        
        isns_channels= i_channels+'_isns'
        if i_channels.endswith('fft'): # fft channels 
            dx=(1/size_x)*1E-9
            units="1/nm"
            dimension  = "si-reciprocal"
        else : 
            dx=step_dx*1E9
            units="nm"
            dimension  = "si"
        print(isns_channels)

        isns_channels = isns.imshow(xrdata_fft[i_channels],
                                    ax =  axs[i],
                                    cmap= cmap,
                                    cbar = cbar_show,
                                    dx = dx,
                                    units= units,
                                    dimension = dimension,
                                    robust = True)
        axs[i].set_title(i_channels, loc='left', fontsize = 'small')
        #################################
        if scan_aspect_ratio != 1: 
            fig.colorbar(isns_channels.get_children()[-2],  
                        fraction = 0.045, 
                        ax=axs[i])  
        ################################
        # colorbar setting separately
        ################################
        if 'ref_lattice_k0' in xrdata_fft.attrs: 
            ref_lattice_k0 = xrdata_fft.attrs['ref_lattice_k0'] # kspace atomic lattice_k0
            ref_6p_radious = ref_lattice_k0/xrdata_fft.attrs['freq_X_spacing']
        else : pass
    
        ## for zoom in (
        if zoom_in_fft == True:
            # center position (0,0) -> (0,0) in (freq_X,freq_Y )-> find index
            # np.abs(z_LIX_fNb_xr_fft.freq_X).argmin()
            x_lower_limit = \
             np.abs(xrdata_fft.freq_X).argmin()\
             -int(ref_6p_radious)*zoom_in_expand
            x_upper_limit = \
            np.abs(xrdata_fft.freq_X).argmin()\
            +int(ref_6p_radious)*zoom_in_expand 
            axs[i].set_xlim([x_lower_limit,x_upper_limit])
            axs[i].set_ylim([x_lower_limit,x_upper_limit])    
        ## for zoom in )
    fig.suptitle(xrdata_fft.title +'(2D FFT)',
                 fontsize = 'small',
                 position=(0.5, 1.0+0.05) )
    fig.tight_layout()
    isns.reset_defaults()
    plt.show()
    
    return fig


# # + [markdown] tags=[] jp-MarkdownHeadingCollapsed=true
# ### 9.  xrdata_fft analysis 
# * (p6 & r6,rot_angle, pad & rot)
# * for xrdata_fft find 6 points 
# * 1-2-7 : xr_data analysis ( p6r6, rot angle, padding, rotate, ) 
#
# ### find 6 peaks and 6 reference points 
# * xrdata_fft data  should have <U> reference$a_{0}$ </U>
# * **xrdata_fft_plot_p6r6** (xrdata_fft,zoom_in_fft = True, zoom_in_expand = 3):
# > * input : xrdata_fft 
# > * output: p6,r6,fig
# * p6,r6 point lists are saved as attributes to the xr_data_ffft data 

# # + tags=[]
##################################################################
# input data :  xrdata_fft 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# return #  peak6points_kspace_idxs, ref_6points_kspace_idxs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#################################

def xrdata_fft_plot_p6r6(xrdata_fft,
                           zoom_in_fft = True, 
                           zoom_in_expand = 3):
    '''
    # xrdata_fft should have attributes 'ref_lattice_a0' & 'ref_lattice_k0'
    # xrdata_fft  # with ref_a0  : input data     
    # zoom_in_fft : zoomin for the center region 
    # zoom_in_expand : control zoom in area (3times of atomic lattice)
        out put  p6 & r6 
            p6 : peak_6points_kspace_idxs,
            r6: ref_6points_kspace_idxs
    
    #~~~~~~#
    '''
    ref_lattice_a0 = xrdata_fft.attrs['ref_lattice_a0'] # ref_lattice_a0
    ref_lattice_k0 = xrdata_fft.attrs['ref_lattice_k0'] # kspace atomic lattice_k0
    ref_6pts  = ref_lattice_k0 * np.array([[math.cos(pt_i* math.pi/3), 
                                   math.sin(pt_i* math.pi/3)]
                       for pt_i in range(6)])
    # ref_6pts: (x,y) form
    # from a0 calibrate  'k0' & point list
    ref_6points_kspace_x =  (ref_6pts[:,0] 
                            - xrdata_fft.freq_X.values[0]
                            )/xrdata_fft.freq_X.spacing
    # 
    ref_6points_kspace_y =  (ref_6pts[:,1] 
                            - xrdata_fft.freq_Y.values[0]
                            )/xrdata_fft.freq_Y.spacing
    ref_6p_radious = ref_lattice_k0/xrdata_fft.freq_X.spacing
    # fro "skimage.draw.disk" center_indx -> dtype(int), save as np 
    ref_6points_kspace_idxs = np.array([[round(x,2),round(y,2)]
            for x, y  in zip(ref_6points_kspace_x, ref_6points_kspace_y) ])
    # use list comprehention x,y 
    # round ( , 2)
    #print(ref_6points_kspace_idxs)
    # ref_6points_kspace_idxs : (x,y) form
    #~~~~~~~~~~~~~~~~~~~~~~~~~#

    # find  6 point  in the measured fft 
    peak_6points_kspace_idxs = np.array(
    [np.zeros_like(ref_6points_kspace_idxs) 
    for i in range (len(xrdata_fft))])
    p6s_k_pts = peak_6points_kspace_idxs.copy()
    # assigne array for the measured peak lists (for each channels)
   
    # ref6points_kspace_idxs : 
    # ideal 6 points of atomic lattice
    # peak6points_kspace_idxs :
    # measured 6 points from atomic lattice
    # ref point. shape = (6,2) 
    # local peaks. shape  = (N, 6, 2) dimension 
    # 
    ################### plot #################
    isns.set_image( origin = "lower", cmap = 'cividis')
    
    fig,axes = plt.subplots(2,2, figsize = (6,6))
    axs = axes.ravel()
    for i,ch_map in enumerate (xrdata_fft):
        isns_channel = ch_map+'isns'
        print(ch_map)    
        # use the isns instead of xr.plot 
        # plot type is different, isns type is more controllable
        # for example, we can adjust the set_aspect ration
        isns_channel = isns.imshow(xrdata_fft[ch_map],
                                   ax = axs[i],
                                   dx = xrdata_fft.freq_X.spacing*1E-9,
                                   units= "1/nm",
                                   dimension = "si-reciprocal",
                                   robust = True)
        axs[i].set_aspect(1)
        
        #################################
        # Red circle for peak positions  plot
        #################################
        for r_i, ref_6points_kspace_idx in  enumerate(ref_6points_kspace_idxs):
            ref_circles = Circle(tuple(ref_6points_kspace_idx), # center x,yidxs
                                    ref_6p_radious/4, # radius
                                    facecolor = 'none', 
                                    edgecolor = 'red',
                                    linewidth = 1,
                                    alpha = 0.5)
            axs[i].annotate(str(r_i),
                            tuple(ref_6points_kspace_idx),
                            color='r',
                            size =8) # ref peak numbers
            axs[i].add_patch(ref_circles)
            # circle xy = (x,y) 
            #  ref_6points_kspace_idx is also  (x, y) 
        #################################
        # white circles for local peaks
        # find local peaks (it could be any number)
        #################################
        local_peaks_in_ch_rycx_test = skimage.feature.peak_local_max(
            gaussian_filter(
                xrdata_fft[ch_map].values, sigma=1
                ),
                min_distance=int(ref_6p_radious/2),
                threshold_rel = 0.2 )
        # check the number of local peaks 
        # if there is no local peaks, adjust the peak_local_max prameters 
        print ('local leaks Number : ', len(local_peaks_in_ch_rycx_test))
        # if "local leaks Numbe" is zero ==> error!
        if len(local_peaks_in_ch_rycx_test) == 0: 
            local_peaks_in_ch_rycx = skimage.feature.peak_local_max(
                gaussian_filter(xrdata_fft[ch_map].fillna(0).values,
                                sigma=1),
                min_distance=int(ref_6p_radious/2) 
            )
                
            # Find all local peaks without threshold condition
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # in case of filtered FFT --> fill the nan to 0 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
            # local_peaks_in_ch result ==> (ry,cx) order due to 'peak_local_max'
            local_peaks_in_ch = local_peaks_in_ch_rycx[:,::-1]
        # change the array (ry, cx,) -> (cx,ry) 
            print ('local leaks Number : ', len(local_peaks_in_ch))
        else :
            local_peaks_in_ch_rycx = skimage.feature.peak_local_max(
            gaussian_filter(
                xrdata_fft[ch_map].values, sigma = 1
                ),
                min_distance=int(ref_6p_radious/2),
                threshold_rel = 0.2 )
            # Find local loca peaks with top 20% in the (channel) image 
            # local_peaks_in_ch result ==> (ry,cx) order due to 'peak_local_max'
        local_peaks_in_ch = local_peaks_in_ch_rycx[:,::-1]
            

        #################
        for local_peak in  local_peaks_in_ch:
            #print(local_peak)
            peak_bumps = Circle(tuple(local_peak),
                                ref_6p_radious/3, # radius
                                facecolor = 'none', 
                                edgecolor = 'white',
                                linewidth = 1,
                                alpha = 0.5) 
            axs[i].add_patch(peak_bumps)
            # circle xy = (x,y) 
            #  local_peak  is also  (x, y) 
            # white circles. 
        ''' # if you want use scatter
        axs[i].scatter(local_peaks_in_ch[:,0], # cx
                       local_peaks_in_ch[:,1], # ry
                       c='w', 
                       s = ref_6p_radious/2,
                       alpha =0.5
                       )'''
        #######################################
        # select (slct) 6 local peaks 
        # which is close to the ref 6 pts 
        ###########################################
        find_6peaks_idx_in_peak_list = [
                                        np.array([distance.euclidean(
                                            ref_6points_kspace_idx,
                                            local_peak
                                            ) 
                                        for local_peak in local_peaks_in_ch]).argmin()
                                        for ref_6points_kspace_idx 
                                        in  ref_6points_kspace_idxs
                                        ]
        print (find_6peaks_idx_in_peak_list)
        # local peaks in  each channels 
        # make list for euclidean distance with one of ref pt
        # check (x,y)  vs (x,y) !!!
        # find 'arg min '
        # 
        peak_6points_kspace_idx = local_peaks_in_ch[find_6peaks_idx_in_peak_list]
        
        p6_k_pts_cx = xrdata_fft.freq_X[peak_6points_kspace_idx[:,0].astype(int)]
        
        p6_k_pts_ry = xrdata_fft.freq_Y[peak_6points_kspace_idx[:,1].astype(int)]
        p6_k_pts_i = np.stack((p6_k_pts_cx,p6_k_pts_ry),axis =1)
        # index --> real k-point values w.r.t coordinates
        # for [i]th channel 
        
        p6s_k_pts[i] = p6_k_pts_i
        peak_6points_kspace_idxs[i] = peak_6points_kspace_idx

        ############################################
        # add selected local  6 peaks 
        ############################################
        axs[i].scatter(peak_6points_kspace_idx[:,0],
                       peak_6points_kspace_idx[:,1],
                       c='b',
                       s = ref_6p_radious/1,
                       alpha =0.5)
        for pk_j, peak6points in  enumerate(peak_6points_kspace_idx):
            axs[i].annotate(str(pk_j),
                            xy = tuple(peak6points),
                            color='b',
                            size =8) #anntates
        # peak_6points_kspace_idxs .shape = [i]channel * (6,2)
        # check channel [i]
        #################
        '''
        for pk_i, local_peak_in6 in  enumerate(peak_6points_kspace_idxs[i]):
            local_peak_6list = Circle(tuple(local_peak_in6),
                                ref_6p_radious/4, # radius
                                facecolor = 'none', 
                                edgecolor = 'blue',
                                linewidth = 1,
                                alpha = 0.8) 
            axs[i].add_patch(local_peak_6list)
            axs[i].annotate(str(pk_i),
                            tuple(local_peak_in6)
                            , color='blue',
                            size =8) #번호넣기
                            
                            '''
        ######################################
        #Zoom in with  xy limit
        if zoom_in_fft == True:
            # center position (0,0) -> (0,0) in (freq_X,freq_Y )-> find index
            # np.abs(z_LIX_fNb_xr_fft.freq_X).argmin()
            x_lower_limit = \
             np.abs(xrdata_fft.freq_X).argmin()\
             -int(ref_6p_radious)*zoom_in_expand
            x_upper_limit = \
            np.abs(xrdata_fft.freq_Y).argmin()\
            +int(ref_6p_radious)*zoom_in_expand 
            axs[i].set_xlim([x_lower_limit,x_upper_limit])
            axs[i].set_ylim([x_lower_limit,x_upper_limit])
    isns.reset_defaults()
    plt.tight_layout()
    
    plt.show()
    
    
    # assign r6 & p6s #xrdata_fft.attributes  
    xrdata_fft.attrs['r6_k_pts'] = ref_6pts
    xrdata_fft.attrs['p6s_k_pts'] = p6s_k_pts
    
    #print ('6 reference spots(dst)')
    #print (ref_6points_kspace_idxs)
    #print ('6 measured peaks(src)')
    #print (peak_6points_kspace_idxs)
    return  peak_6points_kspace_idxs, ref_6points_kspace_idxs, fig
# return p6 & r6 : check the order 



# # + colab={"base_uri": "https://localhost:8080/"} id="mGfdySXL55C8" outputId="d2e5f006-392c-4ffa-a70f-f08ab139b707"
###################################
# src & dst points 
#dst_r6 = z_LIX_fNb_xr_fft_r6
#src_p6 = z_LIX_fNb_xr_fft_p6

def xrdata_fft_rot_angle(xrdata_fft): 
    '''
    only after : xrdata_fft_plot_p6r6
    input: xrdata_fft
    output : rotation_angle_deg (deg)
    after get rotation_angle_deg, 
    send the xrdata_fft['rot_angle']  to the (real space) xrdata
    eg) #z_LIX_fNb_xr_lattice.attrs = z_LIX_fNb_xr_lattice_fft.attrs

    '''
    # p6 & r6 from attributes
    src_p6 = xrdata_fft.attrs['p6s_k_pts']
    dst_r6 = xrdata_fft.attrs['r6_k_pts']
    
    ###################################
    # check the slope  (dy/dx)
    #####################################
    # use the horizontal axis  spots (0, 3) 
    dst_slope = np.degrees(
            2*math.pi+math.atan2(
                (dst_r6[0]-dst_r6[3])[1],
                (dst_r6[0]-dst_r6[3])[0]
                )
            )
    #####################################
    # measured p6points 
    # check the different dimension 
    # use the first channel (z_fwd)
    #####################################
    src_slope = np.degrees(
            2*math.pi+math.atan2(
                (src_p6[0][0]-src_p6[0][3])[1],
                (src_p6[0][0]-src_p6[0][3])[0]
                )
            )
    rotation_angle_deg =  src_slope - dst_slope 
    xrdata_fft.attrs['rot_angle'] = rotation_angle_deg
    return rotation_angle_deg


################################
#test 
#rotation_angle_deg =   xrdata_fft_rot_angle(z_LIX_fNb_xr_lattice_fft)
#
# after find rotational angle, copy the attributes to the real space data 
#z_LIX_fNb_xr_lattice.attrs = z_LIX_fNb_xr_lattice_fft.attrs

#print(rotation_angle_deg)
#print (z_LIX_fNb_xr_lattice_fft)

# # + [markdown] tags=[]
# * fig can be saved as image (png) 
#
# ### find_rot_angle from (p6, r6)
#
# * **xrdata_fft_rot_angle**
# > * input : xrdata_fft
# > * output : rot_angle_deg
#
#     * based on previous 6 spot test 
#         * find slope between reference 6points & measured data
#     * xr padding region checking (pad_x, pad_y)
#     * Rotation angle is saved as attributes 
#         * save it to both xrdata_fft & xr_data
#         
#
# ### Padding according to (rot_angle) 
# * **xrdata_padding**  after FFT 
#     * Padding original data to prevent image edge cutting off during affine transform 
#     * rotating the original data set 
#         * rotation test (resize (True) during rotation) 
#         * Confirm the required area for **xarray padding**
#     * adjust **x,y coords**  according to the padding size
#         *re-calibrate: spacing + offset
#         
# ### Rotating image after (padding) 
# * **xrdata_rotate** after padding
#     * rotate the original xrdata after padding
#     * increased size after rotation <-- padding size
# -

xr_isns_plot_r_space(dual_xr_P1)



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
