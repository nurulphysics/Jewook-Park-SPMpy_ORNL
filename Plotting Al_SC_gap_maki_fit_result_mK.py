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

# # Al superconducting gap result of ORNL mK STM 
# * Base Temperature : 37 mK
# * Calibrated electron temperature 228.275mK 
#
#
# ## load cvs data $\to$ pandas

# +
#############################
# check all necessary package
#############################

import glob
import os
from warnings import warn

import numpy as np
import pandas as pd
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# -

# # <font color= orange > 1. Choose Folder & DataFrame for files  </font>

# + jp-MarkdownHeadingCollapsed=true
###########################################
# Create and display a FileChooser widget #
###########################################
from ipyfilechooser import FileChooser
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
# -

files_df = files_in_folder(folder_path)

files_df

# +
files_df[files_df.type== 'xlsx'].iloc[1].file_name


data_df = pd.read_excel(files_df[files_df.type== 'xlsx'].iloc[1].file_name)
data_df.columns =['bias_mV_Al','LDOS','blank','bias_mV_maki','maki_fit']
data_df = data_df.drop(columns = ['blank'])
data_df_LDOS = data_df[['bias_mV_Al','LDOS']]
data_df_maki = data_df[['bias_mV_maki','maki_fit']]
data_df_LDOS= data_df_LDOS.rename(columns = {'bias_mV_Al':'bias_mV'}).drop(0)
data_df_maki = data_df_maki.rename(columns = {'bias_mV_maki':'bias_mV'}).drop(0)


# -

data_df_maki

data_df_f = pd.merge (data_df_LDOS,data_df_maki, how = 'outer' )
data_df_f

data_df_f = data_df_f.melt(id_vars = ['bias_mV'], value_vars = ['LDOS','maki_fit'], var_name= 'LDOS_v', value_name = 'SC')
data_df_f

# +
fig, ax  = plt.subplots (figsize = (4,3))

sns.set_style("whitegrid")
sns.lineplot ( x = 'bias_mV', y = 'SC', data = data_df_f, hue = 'LDOS_v', ax = ax)
ax.set_xlabel ('Bias (mV)')
ax.set_ylabel ('dI/dV')
handles,labels  = ax.get_legend_handles_labels()
ax.legend(handles = handles, labels=labels)
fig.suptitle ('Aluminum Superconducting gap (at T = 38 mK)')
plt.show()
