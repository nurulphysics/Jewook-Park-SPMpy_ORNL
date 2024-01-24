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

# + [markdown] jp-MarkdownHeadingCollapsed=true
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
# -

# # Experimental Conditions 
#
# ## Data Acquistion date 
# * 2024 0105 Sr0.95Ti0.76Nb0.19Ni0.05O3 thin film with PtIr tip
# ## Measurement condition 
# * <font mcolor= Blue, font size="5" > RT + elevated temp 310 K (Temp FB) </font> 
#     * UHV annealing 
#     * STM measurement at VT STM (JG43,CNMS) UHV condition (<5E-11Torr)
#
# ## **Sample**
# * <font mcolor= Blue, font size="5" > $ Sr_{0.95}Ti_{0.76}Nb_{0.19}Ni_{0.05}O_{3} $thin film </font> (sample #2)
#     * Thin film after high temperature annealing under $H_{2}$ condition.
# ## <font color= Blue, font size="5" > **Tip** : PtIr (mechanical cutting)  </font> 
# ## <font color= Red, font size="5" > Temperature gradient ($T_{tip-sample}$ )  = $T_{tip}$(297K, RT) - $T_{sample}$ (310 K ) = 13 K </font> 

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

# +
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
# -


#folder_path = file_chooser.selected_path
#print( folder_path)
folder_path = r'C:\Users\gkp\OneDrive - Oak Ridge National Laboratory\1_VT_STM\2024-01-02 Sr0.95Ti0.76Nb0.19Ni0.05O3 _2 with PtIr tip Jewook'
files_df = files_in_folder(folder_path)

# ## 1-2. Choose <font color= orange > GWY </font> file loading to analyze
#
# ### 1.2.0 Choose the file 
# * gwy_analyze

files_df[files_df.type=='gwy']#.file_name.iloc[0]
gwy_files = files_df [files_df.type=='gwy']


# +
# Set the display option to prevent text from being truncated for all columns
pd.set_option('display.max_colwidth', None)

isin_filename = '0012'

print (gwy_files[gwy_files.file_name.str.contains(isin_filename)].file_name)


# -


#gwy_files[gwy_files.file_name.str.contains(isin_filename)].file_name
gwy_files[gwy_files.file_name.str.contains(isin_filename)]


## Choose target file 
#gwy_analyze_filename = gwy_files[gwy_files.file_name.str.contains(isin_filename)].iloc[1].file_name
gwy_analyze_filename = gwy_files[gwy_files.file_name.str.contains(isin_filename)].file_name.iloc[0]


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
gwy_xr = gwy_dict['gwy_xr2']
#gwy_xr.Y

gwy_xr

#gwy_xr[list (gwy_xr.data_vars.keys())[0]].plot()
# -
gwy_xr.data_vars.keys()

gwy_xr = gwy_xr.rename_vars( {"Z_(fwd)" : 'z_f'})
gwy_xr = gwy_xr.rename_vars( {"Bias_(fwd)" : 'vth_f'})
gwy_xr

"""
for ch_i, ch_name in enumerate (gwy_xr.data_vars.keys()):
    print (ch_name)
    
    ch_name_rename = rename_gwy_xr_data_vars(ch_name) 
    print (ch_name_rename)
    gwy_xr = gwy_xr.rename_vars({ch_name:ch_name_rename})
"""
gwy_xr


# +

#gwy_xr = gwy_intrplt_xr (gwy_xr)
#gwy_xr
gwy_xr.z_f.plot()

# -

rescale_intensity_xr(gwy_xr).vth_f.plot()

# +
#gwy_zf_gs= filter_convert2grayscale(gwy_xr.z_f)
#threshold_otsu_xr(gwy_xr).z_f.plot()
#threshold_otsu_xr(gwy_xr).vth_f.plot()


# +
#zf_rod = threshold_otsu_xr(gwy_xr,threshold_flip=False).isnull()
# find nano rod position by using otsu threshold
#zf_rod.z_f.plot()
# -

# zf_rod.z_f is True  ==>  'rod', False ==> 'film'
"""categories = xr.where(zf_rod.z_f, 'rod', 'film')
categories

gwy_xr['categories'] =categories
gwy_xr"""

gwy_df = gwy_xr.to_dataframe()


#sns.displot( data = gwy_df, x = 'z_f', y = 'vth_f', hue="categories")
sns.displot( data = gwy_df, x = 'z_f', y = 'vth_f')

# +
#gwy_df = gwy_df[(gwy_df.vth_f<0.02) &(gwy_df.vth_f>-0.005) ] 
#drop outliers

gwy_df.vth_f = gwy_df.vth_f*1E3
gwy_df.z_f = gwy_df.z_f*1E9
# unit calc  --> mV & nm
# -


sns.displot( data = gwy_df, x = 'z_f', y = 'vth_f')
sns.kdeplot( data = gwy_df, x = 'z_f', y = 'vth_f', levels=10, cmap="mako")

# +
X = gwy_df[['z_f','vth_f']]


##############################
# USe KMeans clustering 
#################################


from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score

kmeans = KMeans(n_clusters=2, random_state=42)
gwy_df['cluster'] = kmeans.fit_predict(X)

X_train, X_test, y_train, y_test = train_test_split(X, gwy_df['cluster'], test_size=0.2, random_state=42)
sns.scatterplot(x='z_f', y='vth_f', hue='cluster', data=gwy_df, palette='viridis', marker='o', s=10)

# -

gwy_df['Region'] = gwy_df['cluster'].map({0: 'rod', 1: 'film'})
# accroding to cluster --> category check 
gwy_df

sns.kdeplot( data = gwy_df, x = 'z_f', y = 'vth_f', hue =  'Region', levels=10, cmap="mako",  fill=True)

g= sns.jointplot( data = gwy_df, x = 'z_f', y = 'vth_f', hue =  'Region', s= 20, alpha=0.02, palette = 'coolwarm')
g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=5, alpha =1,palette = 'vlag')
g.set_axis_labels(xlabel='Height (nm)', ylabel='Thermovoltage (mV)')
g.fig.suptitle(r'$\Delta T_{tip-sample}$ = -194 K', x=0.45, y=0.80, fontsize=14)
# Figure Level에서 x축과 y축 범위 설정
g.fig.get_axes()[0].set_xlim(2, 22)  # x축 범위 설정
g.fig.get_axes()[0].set_ylim(-60, 0)   # y축 범위 설정

g= sns.jointplot( data = gwy_df, x = 'z_f', y = 'vth_f', hue =  'Region', s= 20, alpha=0.02, palette = 'viridis')
g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=5, alpha =1,palette = 'viridis')
g.set_axis_labels(xlabel='Height (nm)', ylabel='Thermovoltage (mV)')
g.fig.suptitle(r'$\Delta T_{tip-sample}$ = -194 K', x=0.45, y=0.80, fontsize=14)
# Figure Level에서 x축과 y축 범위 설정
g.fig.get_axes()[0].set_xlim(2, 22)  # x축 범위 설정
g.fig.get_axes()[0].set_ylim(-60, 0)   # y축 범위 설정




gwy_df.groupby('Region').z_f.mean()

gwy_df.groupby('Region').z_f.std()

# + jupyter={"source_hidden": true}
gwy_df.groupby('Region').vth_f.mean()
# -

gwy_df.groupby('Region').vth_f.std()




