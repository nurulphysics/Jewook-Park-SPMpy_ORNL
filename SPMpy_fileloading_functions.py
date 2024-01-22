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

# # SPMpy 
# * Authors : Dr. Jewook Park at CNMS, ORNL
#     * Center for Nanophase Materials Sciences (CNMS), Oak Ridge National Laboratory (ORNL)
#     * email :  parkj1@ornl.gov
#         
# > **SPMpy** is a python package to analysis scanning probe microscopy (SPM) data analysis, such as scanning tunneling microscopy and spectroscopy (STM/S) data and atomic force microscopy (AFM) images, which are inherently multidimensional. SPMpy exploits recent image processing(a.k.a. Computer Vision) techniques, and utilzes [building blocks](https://scipy-lectures.org/intro/intro.html#the-scientific-python-ecosystem) and excellent visualization tools available in the [scientific python ecosystem](https://holoviz.org/index.html). Many parts are inspired by well-known SPM data analysis programs, for example, [Wsxm](http://www.wsxm.eu/) and [Gwyddion](http://gwyddion.net/). SPMpy is trying to apply lessons from [Fundamentals in Data Visualization](https://clauswilke.com/dataviz/).
#
# >  **SPMpy** is an open-source project. (Github: https://github.com/Jewook-Park/SPMPY )
# > * Contributions, comments, ideas, and error reports are always welcome. Please use the Github page or email parkj1@ornl.gov. Comments & remarks should be in Korean or English. 

# # file_loading functions 
#
# ## 0. Choose the working folder
# ## 1. Check file_list (DataFrame) 
# *  *def* files_in_folder(path)
#
# ## 2. Image to xarray 
# *  *def* img2xr
#     * 2D image (topography & LDOS) to xarray
#     * input: nanonis 2D data (*.sxm)
#     * output : Xarray (_xr) with attributes 
#     * nanonis (sxm) $\to $ numpy $\to $ pd.DataFrame(_df) $\to $ xr.DataSet (_xr)
#     * (Xarray) attributes 
#         * title, X_spacing, Y_spacing, freq_X_spacing, freq_Y_spacing
#         * attributes can be added later. 
#
# ## 3. Grid 3D to xarray 
# *  *def* grid2xr* 
#     * 3D data (grid spectroscopy) to xarray
#     * input: nanonis grid3d data set (*.3ds)
#     * output: Xarray (_xr) with attributes
#     * nanonis 3D data set (3ds)  $\to $ numpy $\to$ pd.DataFrame(_df) $\to$ xr.DataSet (_xr) 
#     * (Xarray) attributes
#         * title, X_spacing, Y_spacing, bias mV info, freq_X_spacing, freq_Y_spacing
#         * attributes can be added later. * attributes can be added later. 
#         
# ## 4. Line spectroscopy (1D grid) to xarray   
# *  *def* gridline2xr* 
#     * in case of line spectroscopy: step_dy = 0 $\to$ **error** 
#     * input: *.3ds file (Line spectroscopy) 
#     * output: Xarray (_xr) with attributes
#     * nanonis 3D data set (3ds)  $\to $ numpy $\to$ pd.DataFrame(_df) $\to$ xr.DataSet (_xr) 
#     * simply not using the step_dx
#
#
# ## 5. Gwyddion 2D image to PANDAS Dataframe or Xarray
# ### 5.1. gwy_img2df : gwy file name 
# * Gwyddion data container to PANDAS DataFrame
# * input: *.gwy file
#     * gwyddion 2D image data (*gwy) $\to $ numpy $\to $  pd.DataFrame(_df)
# * output: PANDAS DataFrame
#     
#
# ### 5.2. gwy_df_ch2xr : Choose a data channe in gwy_df 
# * Gwyddion data container to Xarray DataArray
# * input: gwy_df dataframe & channel number ( N=0)
#     * pd.DataFrame(_df) $\to $  xarray Dataset (_xr)
# * output: Xarray DataSet 
#
# ### 5.3. gwy_df2xr : Choose a data channe in gwy_df 
# * Gwyddion data container to Xarray DataArray
# * using gwy_df_ch2xr function 
# * input: gwy_df dataframe
#     * pd.DataFrame(_df) $\to $  xarray Dataset (_xr)
# * output: Xarray DataSet 
#

# ## <font color=blue>0. Choose the working folder </font>
#

# + jp-MarkdownHeadingCollapsed=true
#############################
# check all necessary package
#############################

import os
import glob
import numpy as np
import pandas as pd
from warnings import warn

try:
    from ipyfilechooser import FileChooser
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named ipyfilechooser')
    # %from ipyfilechooser import FileChooser

try:
    import xrft
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xrft')
    # !pip install xrft 
    import xrft


# + jp-MarkdownHeadingCollapsed=true
###########################################
# Create and display a FileChooser widget #
###########################################
#file_chooser = FileChooser('')
#display(file_chooser)
# -

# ## <font color=blue>1. Check file_list (DataFrame) </font>

def files_in_folder(path_input): 
    """
    

    Parameters
    ----------
    path : str 
        folder path 
        * copy and paste the folder path
        * add 'r' to avoid unicodeerror 
    Returns
    -------
    file_list_df : PANDAS DataFrame
        file list dataframe 
"""
    import os
    import glob
    import pandas as pd
    import numpy as np
    import nanonispy as nap
    currentPath = os.getcwd() #get current path
    print ("Current Path = ", os.getcwd()) # print current path 
    #######################################
    working_folder = path_input
    # copy & paste the "SPM data file" location (folder(path)) 
    os.chdir(working_folder)
    print ("Changed Path = ", os.getcwd()) 
    # check the re-located path 
    ####################################

    ######################################
    # call all the sxm  files in path    #
    ######################################
    path = "./*"
    # pt_spec_file_list = (glob.glob('*.dat')) 
    sxm_file_list = (glob.glob('*.sxm')) 
    grid_file_list = (glob.glob('*.3ds')) 
    csv_file_list = (glob.glob('*.csv')) 
    gwy_file_list = (glob.glob('*.gwy')) 
    xlsx_file_list = (glob.glob('*.xlsx')) 
    # using "glob"  all " *.sxm" files  in file_list
    #####################################
    ## sxm file
    file_list_sxm_df = pd.DataFrame([[
        file[:-7],file[-7:-4],file] 
                                     for file in sxm_file_list],
        columns =['group','num','file_name'])

    sxm_file_groups= list (set(file_list_sxm_df['group']))
    ## 3ds file
    file_list_3ds_df = pd.DataFrame([[
    file[:-7],file[-7:-4],file] 
                                 for file in grid_file_list],
    columns =['group','num','file_name'])
    ## csv file
    file_list_csv_df = pd.DataFrame([[
        file[:-7],file[-7:-4],file] 
                                     for file in csv_file_list],
        columns =['group','num','file_name'])
    ## gwy file
    file_list_gwy_df = pd.DataFrame([[
        file[:-4], np.nan, file] 
                                     for file in gwy_file_list],
        columns =['group','num','file_name'])   
    
    ## excel file
    file_list_xlsx_df = pd.DataFrame([[
        file[:-5], np.nan, file] 
                                     for file in xlsx_file_list],
        columns =['group','num','file_name']) 
    
    file_list_df = pd.concat ([file_list_sxm_df, file_list_3ds_df, file_list_csv_df, file_list_gwy_df,file_list_xlsx_df],ignore_index= True)
    file_list_df['type'] = [file_name[-3:] for file_name in  file_list_df.file_name]
    file_list_df.type [ file_list_df.type == 'lsx']  = 'xlsx'
    print (file_list_df)

    
    #############################################################
    # to call all the files in sxm_file_groups[0]
    ##  file_list_df[file_list_df['group'] == sxm_file_groups[0]]
    #############################################################
    #print (file_list_sxm_df)
    #print (file_list_3ds_df)
    # indicates # of files in each group 
    for group in sxm_file_groups:
        print ('sxm file groups :  ', group, ':  # of files = ',
               len(file_list_sxm_df[file_list_sxm_df['group'] == group]) )
    if len(file_list_df[file_list_df['type'] == '3ds']) ==0 :
        print ('No GridSpectroscopy data')
    else :
        print ('# of GridSpectroscopy',
               list(set(file_list_df[file_list_df['type'] == '3ds'].group))[0], 
               ' = ',           
               file_list_df[file_list_df['type'] == '3ds'].group.count())

    return file_list_df

# +
import os
import glob
import pandas as pd
import numpy as np
import nanonispy as nap

def files_in_folder(path_input):
    """
    Retrieve file information from a specified folder path.

    Parameters:
    - path_input (str): 
    Folder path where files are located.
    Use 'r' to avoid UnicodeError.

    Returns:
    - file_list_df (pd.DataFrame): 
    DataFrame containing information about files in the folder.
    ---
    Summary
    
    Imports necessary libraries, including os, glob, pandas, numpy, and nanonispy.
    Gets the current working directory using os.getcwd() and prints it.
    Changes the working directory to the provided folder path
    using os.chdir() and prints the new working directory.
    Uses glob.glob() to find specific types of files 
    (*.sxm, *.3ds, *.csv, *.gwy, and *.xlsx) 
    in the folder and stores their filenames in separate lists.

    Creates Pandas DataFrames 
    (file_list_sxm_df, 
    file_list_3ds_df,
    file_list_csv_df,
    file_list_gwy_df,
    and file_list_xlsx_df) for each type of file,
    extracting the group, number, and file name from the filenames.

    Concatenates these DataFrames into a single Pandas DataFrame called file_list_df.
    Assigns file types based on the file extensions, converting 'lsx' to 'xlsx' for Excel files.
    Prints information about the files, including the resulting DataFrame.
    Optionally, it provides additional information about the number of files in each group and the presence of GridSpectroscopy data.
    Returns the file_list_df DataFrame as the function's output.
    ---
    
    """
    import os
    import glob
    import pandas as pd
    import numpy as np
    import nanonispy as nap
    currentPath = os.getcwd()
    print("Current Path = ", os.getcwd())

    working_folder = path_input
    os.chdir(working_folder)
    print("Changed Path = ", os.getcwd())

    path = "./*"
    sxm_file_list = (glob.glob('*.sxm'))
    grid_file_list = (glob.glob('*.3ds'))
    csv_file_list = (glob.glob('*.csv'))
    gwy_file_list = (glob.glob('*.gwy'))
    xlsx_file_list = (glob.glob('*.xlsx'))

    file_list_sxm_df = pd.DataFrame([[
        file[:-7], file[-7:-4], file]
                                     for file in sxm_file_list],
                                    columns=['group', 'num', 'file_name'])

    sxm_file_groups = list(set(file_list_sxm_df['group']))

    file_list_3ds_df = pd.DataFrame([[
        file[:-7], file[-7:-4], file]
                                     for file in grid_file_list],
                                    columns=['group', 'num', 'file_name'])

    file_list_csv_df = pd.DataFrame([[
        file[:-7], file[-7:-4], file]
                                    for file in csv_file_list],
                                   columns=['group', 'num', 'file_name'])

    file_list_gwy_df = pd.DataFrame([[
        file[:-4], np.nan, file]
                                    for file in gwy_file_list],
                                   columns=['group', 'num', 'file_name'])

    file_list_xlsx_df = pd.DataFrame([[
        file[:-5], np.nan, file]
                                      for file in xlsx_file_list],
                                     columns=['group', 'num', 'file_name'])

    file_list_df = pd.concat([file_list_sxm_df, 
                              file_list_3ds_df, 
                              file_list_csv_df, 
                              file_list_gwy_df, 
                              file_list_xlsx_df],
                             ignore_index=True)
    file_list_df['type'] = [file_name[-3:] for file_name in file_list_df.file_name]
    file_list_df.type[file_list_df.type == 'lsx'] = 'xlsx'
    print(file_list_df)

    for group in sxm_file_groups:
        print('sxm file groups: ', group, ': # of files = ',
              len(file_list_sxm_df[file_list_sxm_df['group'] == group]))

    if len(file_list_df[file_list_df['type'] == '3ds']) == 0:
        print('No GridSpectroscopy data')
    else:
        print('# of GridSpectroscopy',
              list(set(file_list_df[file_list_df['type'] == '3ds'].group))[0],
              ' = ',
              file_list_df[file_list_df['type'] == '3ds'].group.count())

    return file_list_df



# -

# ## <font color=blue>2. Image to xarray</font>

# +
###############################
# check all necessary package #
# for img2xr                  #
###############################
import os
import glob
import numpy as np
import pandas as pd
import scipy as sp
import math
import matplotlib.pyplot as plt
import re

from warnings import warn
# %pip install importlib-metadata
# 2023 0510 added 

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

# -

# original img2xr 
# not consider multipass cases
"""
def img2xr (loading_sxm_file, center_offset = False):
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
        %pip install nanonispy
        import nanonispy as nap

    try:
        import xarray as xr
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named xarray')
        #!pip install --upgrade scikit-image == 0.19.0.dev0
        %pip install xarray 
        import xarray as xr

    try:
        import seaborn_image as isns
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named seaborn-image')
        #!pip install --upgrade scikit-image == 0.19.0.dev0
        %pip install --upgrade seaborn-image    
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
        z_fwd = z_fwd[::-1,:]
        z_bwd = z_bwd[::-1,:]
        LIX_fwd = LIX_fwd[::-1,:]
        LIX_bwd = LIX_bwd[::-1,:]
    # if scan_direction == down, flip the data (Y)
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
    ########################################

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
    # assigne attributes 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
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
"""


def img2xr (loading_sxm_file, center_offset = False):
    """
    
    
    
    Convert Nanonis .sxm file data to an xarray dataset.

    Parameters:
    loading_sxm_file (str): The path to the Nanonis .sxm file to be loaded.
    center_offset (bool): If True, 
        adjusts the scan data to center it within the scanner's field of view.

    Returns:
    xarray.Dataset: An xarray dataset containing the scan data.

    Raises:
    ModuleNotFoundError: 
        If required modules (nanonispy, xarray, seaborn-image) are not found, 
        it attempts to install them.

    Example:
    >>> data = img2xr('path/to/your/file.sxm', center_offset=True)
    """
    
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

    else: 
        multipass = False


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
    #    if  size_x == size_y : 
    if  dim_px == dim_py : 

        pass
    else : 
        print ('dim_px != dim_py')
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
    if multipass == True : 
        z_LIX_fNb_xr.attrs['multipass_Ch#'] =  int( len(data_vars_name)/4  )
    if multipass == False : 
        z_LIX_fNb_xr.attrs['multipass_Ch#'] =  1
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
    #z_LIX_fNb_xr.attrs['freq_X_spacing'] = 1/step_dx
    #z_LIX_fNb_xr.attrs['freq_Y_spacing'] = 1/step_dy
    # use xrft with complex128= True, 
    # freq_X.spacing will provide new axis spacing info

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


def img2xr_Vth (loading_sxm_file, center_offset = False):
    
    ###############
    # multipass was not considered for img2xr_Vth
    ###############
    """
    
    
    
    Convert Nanonis .sxm file data to an xarray dataset.

    Parameters:
    loading_sxm_file (str): The path to the Nanonis .sxm file to be loaded.
    center_offset (bool): If True, 
        adjusts the scan data to center it within the scanner's field of view.

    Returns:
    xarray.Dataset: An xarray dataset containing the scan data.

    Raises:
    ModuleNotFoundError: 
        If required modules (nanonispy, xarray, seaborn-image) are not found, 
        it attempts to install them.

    Example:
    >>> data = img2xr('path/to/your/file.sxm', center_offset=True)
    """
    
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

    else: 
        multipass = False


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

        ###################
        Vth_fwd = Scan.signals['Bias']['forward']
        Vth_bwd = Scan.signals['Bias']['backward'][:,::-1]


        ####################
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

            Vth_fwd = Vth_fwd[::-1,:]
            Vth_bwd = Vth_bwd[::-1,:]
            
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


        
        Vth_fwd_df = pd.DataFrame(Vth_fwd)
        Vth_fwd_df.index.name ='row_y'
        Vth_fwd_df.columns.name ='col_x'

        Vth_bwd_df = pd.DataFrame(Vth_bwd)
        Vth_bwd_df.index.name ='row_y'
        Vth_bwd_df.columns.name ='col_x'


        
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

        Vth_fwd_df = Vth_fwd_df.fillna(0)
        Vth_bwd_df = Vth_bwd_df.fillna(0)
                                   
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
                                  Vth_fwd_df.stack(),
                                  Vth_bwd_df.stack(),
                                  LIX_fwd_df.stack(),
                                  LIX_bwd_df.stack()], axis = 1)
        # set colunm name for new DataFrame
        z_LIX_fNb_df.columns =['z_fwd','z_bwd','Vth_fwd','Vth_bwd', 'LIX_fwd','LIX_bwd']
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
    #    if  size_x == size_y : 
    if  dim_px == dim_py : 

        pass
    else : 
        print ('dim_px != dim_py')
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
    if multipass == True : 
        z_LIX_fNb_xr.attrs['multipass_Ch#'] =  int( len(data_vars_name)/4  )
    if multipass == False : 
        z_LIX_fNb_xr.attrs['multipass_Ch#'] =  1
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
    #z_LIX_fNb_xr.attrs['freq_X_spacing'] = 1/step_dx
    #z_LIX_fNb_xr.attrs['freq_Y_spacing'] = 1/step_dy
    # use xrft with complex128= True, 
    # freq_X.spacing will provide new axis spacing info

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

# ## <font color=blue>3. Grid to xarray </font>
#
#

# +
###############################
# check all necessary package #
# for img2xr                  #
###############################
import os
import glob
import numpy as np
import numpy.fft as npf
#import xarray as xr
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt


try:
    import nanonispy as nap
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named nanonispy')
    # !pip install nanonispy
    import nanonispy as nap

try:
    import xarray as xr
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xarray')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install xarray 
    import xarray as xr

try:
    import seaborn_image as isns
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named seaborn-image')
    # #!pip install --upgrade scikit-image == 0.19.0.dev0
    # !pip install --upgrade seaborn-image    
    import seaborn_image as isns


try:
    import xrft
except ModuleNotFoundError:
    warn('ModuleNotFoundError: No module named xrft')
    # !pip install xrft 
    import xrft


# +
#griddata_file = file_list_df[file_list_df.type=='3ds'].iloc[0].file_name

def grid2xr(griddata_file, center_offset = True): 
    """
    An xarray DataSet representing grid data from a Nanonis 3ds file.

    This DataSet contains multiple variables corresponding to different data channels, such as "I_fwd" (Forward Current), "I_bwd" (Backward Current), "LIX_fwd" (Lock-In X Forward), "LIX_bwd" (Lock-In X Backward), and "topography" (Topography). The data is organized along three dimensions: "Y" (Y-coordinate), "X" (X-coordinate), and "bias_mV" (Bias Voltage in mV).

    Attributes:
        - title (str): A title or description of the grid data.
        - image_size (list): A list containing the size of the image in X and Y dimensions.
        - X_spacing (float): The spacing between X-coordinates in nanometers.
        - Y_spacing (float): The spacing between Y-coordinates in nanometers.

    Additional Information:
    - The "bias_mV" dimension represents the bias voltage values in mV, and it includes values that are adjusted to have a "zero" bias point.
    - Depending on the `center_offset` parameter used during conversion, the X and Y coordinates may be adjusted to represent positions in the real scanner field of view or with (0,0) as the origin of the image.

    Example Usage:

    Convert a Nanonis 3ds file to a grid_xr DataSet
    grid_xr = grid2xr("example.3ds")

    Access data variables
    topography_data = grid_xr["topography"]
    forward_current_data = grid_xr["I_fwd"]

    Access attributes
    title = grid_xr.attrs["title"]
    image_size = grid_xr.attrs["image_size"]
    x_spacing = grid_xr.attrs["X_spacing"]
    y_spacing = grid_xr.attrs["Y_spacing"]


    Note: This DataSet is suitable for further analysis, visualization, and manipulation using the xarray library in Python.


    ---
    Summary 
    
    Here's a breakdown of the main steps in the grid2xr function:
    Read the Nanonis 3ds file using NanonisFile and extract relevant information such as grid dimensions, position, size, step sizes, channels (e.g., topography, current), and bias values.
    Check the topography data and reshape it if necessary. This step is for handling cases where the topography data is not in the expected shape.
    Process and interpolate bias values to ensure they include "zero" bias and have an odd number of points. This step is necessary to account for different bias settings in the data.
    Interpolate the current and lock-in data (both forward and backward) to match the new bias values.
    Create an xarray DataSet named grid_xr with the following variables: "I_fwd," "I_bwd," "LIX_fwd," "LIX_bwd," and "topography." These variables are associated with dimensions "Y," "X," and "bias_mV."
    Assign various attributes to the grid_xr DataSet, including the title, image size, spacing, and frequency information.
    Optionally, adjust the scan center position in real scanner field-of-view based on the center_offset parameter.
    Check and handle cases where the XY dimensions are not equal and may require interpolation.
    Return the grid_xr DataSet as the result of the function.
    This function seems to be designed for specific data formats and processing tasks related to Nanonis data. You can call this function with a Nanonis 3ds file as input to convert it into an xarray DataSet with the described attributes and dimensions.
    
    ---
    
    """
    
    import re
    file = griddata_file
    #####################
    # conver the given 3ds file
    # to  xarray DataSet (check the attributes)
    NF = nap.read.NanonisFile(file)
    Gr = nap.read.Grid(NF.fname)#
    channel_name = Gr.signals.keys()  
    #print (channel_name)
    N = len(file);
    f_name = file[0:N-4]
    print (f_name) # Gr.basename

    #####################################
    #  Header part
    #  Gr.header
    #####################################
    [dim_px,dim_py] = Gr.header['dim_px'] 
    [cntr_x, cntr_y] = Gr.header['pos_xy']
    [size_x,size_y] = Gr.header['size_xy']
    [step_dx,step_dy] = [ size_x/dim_px, size_y/dim_py] 
    #pixel_size =  size / pixel 

    ###   nX, nY --> x,y real scale  np array 
    nX = np.array([step_dx*(i+1/2) for i in range (0,dim_px)])
    nY = np.array([step_dy*(i+1/2) for i in range (0,dim_py)])

    x = cntr_x - size_x + nX
    y = cntr_y - size_y + nY
    # real XY position in nm scale, Center position & scan_szie + XY position
    
    #####################################
    # signal part
    # Gr.signals
    #####################################
    topography = Gr.signals['topo']
    params_v = Gr.signals['params'] 
    # params_v.shape = (dim_px,dim_py,15) 
    # 15: 3ds infos. 
    bias = Gr.signals['sweep_signal']
    # check the shape (# of 'original' bias points)
    I_fwd = Gr.signals['Current (A)'] # 3d set (dim_px,dim_py,bias)
    I_bwd = Gr.signals['Current [bwd] (A)'] # I bwd
    # sometimes, LI channel names are inconsistent depends on program ver. 
    # find 'LI Demod 1 X (A)'  or  'LI X 1 omega (A)'

    #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ])
    # 'LI' & 'X' in  channel name (signal.keys) 
    LIX_keys = [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ]
    # 0 is fwd, 1 is bwd 
    LIX_fwd, LIX_bwd = Gr.signals[LIX_keys[0]] ,Gr.signals[LIX_keys[1] ]

    # same for LIY
    #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ])
    # 'LI' & 'Y' in  channel name (signal.keys) 
    LIY_keys = [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ]
    # 0 is fwd, 1 is bwd 
    LIY_fwd, LIY_bwd = Gr.signals[LIY_keys[0]] ,Gr.signals[LIY_keys[1] ]


    ###########################################################
    #plt.imshow(topography) # toppography check
    #plt.imshow(I_fwd[:,:,0]) # LIX  check
    ###########################################################

    ##########################################################
    #		 Title for Grid data 
    #       grid size, pixel, bias condition, and so on.
    #############################################################
    # Gr.header.get('Bias>Bias (V)') # bias condition 
    # Gr.header.get('Z-Controller>Setpoint') # current set  condition
    # Gr.header.get('dim_px')  # jpixel dimension 
    title = Gr.basename +' ('  + str(
        float(Gr.header.get('Bias Spectroscopy>Sweep Start (V)'))
    ) +' V ~ ' +str( 
        float(Gr.header.get('Bias Spectroscopy>Sweep End (V)'))
    )+ ' V) \n at Bias = '+ Gr.header.get(
        'Bias>Bias (V)'
    )[0:-3]+' mV, I_t =  ' + Gr.header.get(
        'Z-Controller>Setpoint'
    )[0:-4]+ ' pA, '+str(
        Gr.header.get('dim_px')[0]
    )+' x '+str(
        Gr.header.get('dim_px')[1]
    )+' points'
    #############################################################       

    ### some times the topography does not look right. 
    # * then use the reshaping function 
    # only for asymmetry grid data set

    # eg) JW's MoS2 on HOPG exp. data 

    ###########################################################
    # assign topography as topography_reshape
    ###########################################################
    topo_dimension_true = True
    # if topography looks normal.
    ################################
    if topo_dimension_true == True:
        topography_reshape = topography   
        #################################
        I_fwd_copy = I_fwd
        I_bwd_copy = I_bwd
        LIX_fwd_copy = LIX_fwd 
        LIX_bwd_copy = LIX_bwd 	
        
    else:
        # if a topography looks abnormal
        # it is very rare case, 
        # but I leave manual setting to remind "mistake!"
        
        
        ##########################################################
        # if there is an error or mixed array for 
        ##########################################################
        # adjust lattice manually 
        ##########################################################
        # for example
        # some times 40 x 80 array shape --> 40x40 + 40 x40
        # because of mischoosen step & shape setting 
        # X one line = 0-39: 1st line + 40-79 
        # in this case 
        # make a new arrary (vertically)
        # 0-39 --> 2n & 40-79 -->  2n+1 
        # topo # LIX f&b # I f&b #
        ##########################################################

        
        topography_reshape = np.transpose(np.copy(topography),(1,0)) 
        # make a new lattcie with reshaped dimension 
        for x_indx, y_indx in enumerate (topography):
        # print(x_indx) # 0-39 # print(y_indx.shape)
            topography_reshape[2*x_indx,:] = y_indx[:40] # reshaping first half
            topography_reshape[2*x_indx+1,:] = y_indx[40:80] # reshaping second half
        #################################
        # same deformation for I& LIX 
        #################################
        # check the topographyt 
        plt.imshow(topography_reshape) # 80 * 40 OK
        # topography_reshape is done. 
        
        #################################
        # make a new lattcie with reshaped dimension 
        I_fwd_copy = np.transpose(np.copy(I_fwd),(1,0,2))
        I_bwd_copy = np.transpose(np.copy(I_bwd),(1,0,2)) 
        
        for x_indx, yNbias_plane in enumerate (I_fwd): 
            # make a new lattcie with reshaped dimension 
            print(x_indx) # 0-39 
            I_fwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            I_fwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half

        for x_indx, yNbias_plane in enumerate (I_bwd): 
            # make a new lattcie with reshaped dimension 
            print(x_indx) # 0-39 
            I_bwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            I_bwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        #################################
        # I reshape is done 
        #################################
        LIX_fwd_copy = np.transpose(np.copy(LIX_fwd),(1,0,2)) 
        LIX_bwd_copy = np.transpose(np.copy(LIX_bwd),(1,0,2)) 
        # make a new lattcie with reshaped dimension 
        for x_indx, yNbias_plane in enumerate (LIX_fwd): 
            LIX_fwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            LIX_fwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        for x_indx, yNbias_plane in enumerate (LIX_bwd): 
            LIX_bwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            LIX_bwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        #################################
        # LIX reshape is done 
        #################################

    # after reshaping 

    topography = topography_reshape 
    #################################
    I_fwd = I_fwd_copy 
    I_bwd = I_bwd_copy 
    LIX_fwd  = LIX_fwd_copy 
    LIX_bwd  = LIX_bwd_copy
    ##########################################################


    ###########################
    # Bias segment check      #
    ###########################
    Segment = Gr.header['Bias>Bias (V)']
    # bias unit : '(V)' 

    if type(Segment) == str: # single segment case
        print ('No Segments\n'+ 'Grid data acquired at bias = '+  str(float(Segment)) + 'V')    
    ## No Segments # +  bias setting 

    ########################
    # bias interpolation to have a "zero" bias 
    # interpolate bias_mV that include "zero" bias 
    # in 3D data : center x,y bias interpolation 
    # e.g  256--> including end points + zero  = 256+1 ( the center is "0")
        if len(bias)%2==0:
            bias_new = np.linspace(bias[0],bias[-1],num=(len(bias)+1)) 
            # if bias length is even_number 
            # including "0", total size is "len+1" 
        else:# if bias length is odd_number 
            bias_new = np.linspace(bias[0],bias[-1],num=(len(bias))) 
            # bias_new make a odd number of length
            # make only one value is closest to the zero. 
            
        nearest_zero_bias = np.where(abs(bias_new) == np.amin(abs(bias_new))) 
        # find the index of closest to "0" bias 
        bias_new = bias_new - bias_new[nearest_zero_bias] 
        # assign closest zero vavlue as a zero. 
        #bias_new[np.where(bias_new == np.amin(abs(bias_new)))]=0

    ##############################################
    #'Segment Start (V), Segment End (V), Settling (s), Integration (s), Steps (xn)'
    elif len(Segment) == 3:
        print('Number of Segments =' + str(len(Segment))) 
        Segments = np.array([[ float(Segments) 
                              for Segments in Seg.split(',') ] 
                             for Seg in Segment], dtype = np.float64)
        # in the Segment, split strings sith "," 
        #  make a array after change it as float. 
        # check Nanonispy version
        # bias value could be not correct. 
        
        Seg1 = np.linspace(Segments[0,0],Segments[0,1],int(Segments[0,-1]))
        Seg2 = np.linspace(Segments[1,0],Segments[1,1],int(Segments[1,-1]))
        Seg3 = np.linspace(Segments[2,0],Segments[2,1],int(Segments[2,-1]))
        # except boundary end points,  combine segments ([1:]), Seg1, Seg2[1:], Seg3[1:] 
        bias_Seg = np.append(np.append(Seg1,Seg2[1:]),Seg3[1:]) 
        # Seg1 +  Seg2[1:] +  Se3[1:] 
        # make a clever & shoter way 'later...'
        print ('bias_Seg size = ' + str(len(bias_Seg)))
        bias_Nsteps=int(int(Segments[1,-1])/
                        (Seg2[-1]-Seg2[0])*(bias_Seg[-1]-bias_Seg[0]))
        # New bias Steps uses smallest step as a new stpe size. 
        bias_Nsteps_size = (Seg2[-1]-Seg2[0])/(Segments[1,-1])
        # (Segments[1,0]-Segments[1,1])/int(Segments[1,-1]) # bias step size    
        Neg_bias=-1*np.arange(
            0,bias_Nsteps_size*bias_Nsteps/2, bias_Nsteps_size)
        Pos_bias=np.flip(
            np.arange(0,bias_Nsteps_size*bias_Nsteps/2,bias_Nsteps_size))
        bias_new = np.flip( np.append(Pos_bias,Neg_bias[1:])) 
        # after segments, 
        # bias is called as  bias_new
        ##################################
        # now make the bias_new as an odd number. 
        ###################################
        if len(bias_new)%2==0:
            bias_new = np.linspace(bias_new[0],bias_new[-1],num=(len(bias_new)+1)) 
        else:
            bias_new = np.linspace(bias_new[0],bias_new[-1],num=(len(bias_new))) 
        # check  bias_new contians "zero" 
        nearest_zero_bias = np.where(abs(bias_new) == np.amin(abs(bias_new))) 
        # check index of the nearest value to zero "0"
        bias_new = bias_new - bias_new[nearest_zero_bias] 
        # adjust bias range for bias_new has "zero" 
        print ('bias_new size = ' + str(len(bias_new)))
        # bias 
    # make a new list for Bias
    else:
        print ("Segment error /n code a 5 Sements case")
    #
    ######################################################################
    # make a new bias length (including Segments) as a odd number, including zero
    ######################################################################


    ######################################################################
    # interpolation using bias_new 
    # I_fwd, I_bwd, LIX_fwd, LIX_bwd
    # => I_fwd_interpolate
    #######################################################################
    # assign a function using interpolation 
    # the same as original bias values 
    # make empty np array  & interpolate using scipy
    # xy dim is not changed here, 
    # only 3rd axis changed as new bias 
    ###########################
    def sweep_interpolation(np3Ddata, bias, bias_new):
        np3Ddata_interpolate = np.empty(
                    (np3Ddata.shape[0],np3Ddata.shape[1],bias_new.shape[0])) 

        for x_i,np3Ddata_xi in enumerate(np3Ddata):
            for y_j,np3Ddata_xi_yj in enumerate(np3Ddata_xi):
                #print (np3Ddata_xi_yj.shape)
                Interpolation1D_i_f = sp.interpolate.interp1d(
                    bias,
                    np3Ddata_xi_yj,
                    fill_value = "extrapolate",
                    kind = 'cubic')
                np3Ddata_interpolate[x_i,y_j,:] = Interpolation1D_i_f(bias_new)
        return np3Ddata_interpolate

    I_fwd_interpolate = sweep_interpolation (I_fwd, bias, bias_new)
    I_bwd_interpolate = sweep_interpolation (I_bwd, bias, bias_new)
    LIX_fwd_interpolate = sweep_interpolation (LIX_fwd, bias, bias_new)
    LIX_bwd_interpolate = sweep_interpolation (LIX_bwd, bias, bias_new)

    ####################################################
    # to prevent error for bias direction 
    # 
    ##
    #  assign the bias direction 
    ## up or down ==> up anyway. 
    ###################################################
    if bias[0]>bias[-1]: 
        # if starting point is larger than end point. 
        # start from pos & end to neg
        # no changes. 
        print ('start from POS bias')
        I_fwd = I_fwd_interpolate
        I_bwd = I_bwd_interpolate
        LIX_fwd = LIX_fwd_interpolate
        LIX_bwd = LIX_bwd_interpolate
        bias_mV = bias_new*1000
    else:  # if end point is larger than start point. 
        # start from neg & end to pos
        # change to negative 
        print ('start from NEG bias')
        I_fwd = np.flip(I_fwd_interpolate,2)
        I_bwd = np.flip(I_bwd_interpolate,2)
        LIX_fwd = np.flip(LIX_fwd_interpolate,2)
        LIX_bwd = np.flip(LIX_bwd_interpolate,2)
        bias_new_flip = np.flip(bias_new)
        bias_mV = bias_new_flip*1000
        print ('Flip => start from POS bias')
    ####################################################

    ###################################################
    # convert data XR DataSet
    ####################################################
    

    # col = x 
    # row = y
    # I_fwd grid data ==> [Y, X, bias]
    grid_xr = xr.Dataset(
        {
            "I_fwd" : (["Y","X","bias_mV"], I_fwd),
            "I_bwd" : (["Y","X","bias_mV"], I_bwd),
            "LIX_fwd" : (["Y","X","bias_mV"], LIX_fwd),
            "LIX_bwd" : (["Y","X","bias_mV"], LIX_bwd),
            "topography" : (["Y","X"], topography)
        },
        coords = {
            "X": (["X"], x),
            "Y": (["Y"], y),
            "bias_mV": (["bias_mV"], bias_mV)
        }
    )
    grid_xr.attrs["title"] = title
    #grid_xr.attrs['image_size'] = 
    #grid_xr.attrs['samlpe'] = 
    
    grid_xr.attrs['image_size']= [size_x,size_y]
    grid_xr.attrs['X_spacing']= step_dx
    grid_xr.attrs['Y_spacing']= step_dy    
    #grid_xr.attrs['freq_X_spacing']= 1/step_dx
    #grid_xr.attrs['freq_Y_spacing']= 1/step_dy
    # use the complex128 = True for xrft, 
    # then xrdata_fft.freq_X.spacing 
    # use the attrs in axis info 
    # in case of real X Y ( center & size of XY)
    if center_offset == True:
        # move the scan center postion in real scanner field of view
        grid_xr.assign_coords( X = (grid_xr.X + cntr_x -  size_x/2))
        grid_xr.assign_coords( Y = (grid_xr.Y + cntr_y -  size_y/2))
    else :
        pass
        # (0,0) is the origin of image 
    

    ############################
    # check the XY ratio 
    ############################
    #    if  size_x == size_y : 
    if  dim_px == dim_py : 

        pass
    else : 
        print ('dim_px != dim_py')
    # if xy size is not same, report it! 

    if step_dx != step_dy :
        xystep_ratio = step_dy/step_dx # check the XY pixel_ratio
        X_interp = np.linspace(grid_xr.X[0], grid_xr.X[-1], grid_xr.X.shape[0]*1)
        step_dx = step_dx # step_dx check 

        Y_interp = np.linspace(grid_xr.Y[0], grid_xr.Y[-1], int(grid_xr.Y.shape[0]*xystep_ratio)) 
        step_dy = step_dy/ xystep_ratio # step_dy check 

        # interpolation ratio should be int
        grid_xr= grid_xr.interp(X = X_interp, Y = Y_interp, method="linear")
        print('step_dx/step_dy = ', xystep_ratio)
        print ('grid_xr ==> reshaped')
    else: 
        grid_xr =grid_xr
        print('step_dx == step_dy')
    #print('z_LIX_fNb_xr', 'step_dx, step_dy = ',  z_LIX_fNb_xr.dims)
    print('grid_xr', 'step_dx, step_dy = ', 
          re.findall('\{([^}]+)', str(grid_xr.dims)))
    # regex practice
    
    
    return grid_xr

# -


# ## <font color=blue>4. Grid Line to xarray </font>
#
#

def grid_line2xr(griddata_file, center_offset = True): 
    """
    Convert 3D scan data from Nanonis file to an xarray DataSet.

    Parameters:
        griddata_file (str): The path to the Nanonis file containing the 3D scan data.
        center_offset (bool, optional): Whether to adjust the scan's center position in real scanner field of view.
            If True, the scan's center position is moved to the real scanner field of view. If False, the origin (0,0)
            is set as the image's origin. Default is True.

    Returns:
        xarray.Dataset: An xarray DataSet containing the scan data with dimensions for X, Y, and bias values.
            The dataset includes the following variables:
            - 'I_fwd': Forward current data (3D array with dimensions [Y, X, bias_mV])
            - 'I_bwd': Backward current data (3D array with dimensions [Y, X, bias_mV])
            - 'LIX_fwd': Forward lock-in-X data (3D array with dimensions [Y, X, bias_mV])
            - 'LIX_bwd': Backward lock-in-X data (3D array with dimensions [Y, X, bias_mV])
            - 'topography': Topography data (2D array with dimensions [Y, X])

        The dataset also includes metadata attributes:
        - 'title': A descriptive title for the scan data.
        - 'image_size': The size of the scan image in nanometers [X_size, Y_size].
        - 'X_spacing': The spacing between X values in nanometers.
        - 'Y_spacing': The spacing between Y values in nanometers.
        - 'freq_X_spacing': The reciprocal of X spacing (frequency domain spacing).
        - 'freq_Y_spacing': The reciprocal of Y spacing in the frequency domain.

    Example:
        grid_data = grid_line2xr("path/to/grid_data.dat", center_offset=True)
    """
    file = griddata_file
    #####################
    # conver the given 3ds file
    # to  xarray DataSet (check the attributes)

    import os
    import glob
    import numpy as np
    import numpy.fft as npf
    #import xarray as xr
    import pandas as pd
    import scipy as sp
    import matplotlib.pyplot as plt
    import nanonispy as nap
    import xarray as xr
    import seaborn_image as isns
    import xrft
    

    NF = nap.read.NanonisFile(file)
    Gr = nap.read.Grid(NF.fname)#
    channel_name = Gr.signals.keys()  
    #print (channel_name)
    N = len(file);
    f_name = file[0:N-4]
    print (f_name) # Gr.basename

    #####################################
    #Header part
    #####################################
    #  Gr.header
    #####################################
    [dim_px,dim_py] = Gr.header['dim_px'] 
    [cntr_x, cntr_y] = Gr.header['pos_xy']
    [size_x,size_y] = Gr.header['size_xy']
    [step_dx,step_dy] = [ size_x/dim_px, size_y/dim_py] 
    
    ###   nX, nY --> x,y real scale  np array 
    nX = np.array([step_dx*(i+1/2) for i in range (0,dim_px)])# dimesion맞춘 xstep 
    nY = np.array([step_dy*(i+1/2) for i in range (0,dim_py)])# dimesion맞춘 ystep 

    x = cntr_x - size_x + nX
    y = cntr_y - size_y + nY
    # real XY position in nm scale, Center position & scan_szie + XY position
    
    #####################################
    # signal part
    # Gr.signals
    #####################################
    topography = Gr.signals['topo']
    params_v = Gr.signals['params'] 
    # params_v.shape = (dim_px,dim_py,15) 
    # 15: 3ds infos. 
    bias = Gr.signals['sweep_signal']
    # check the shape (# of 'original' bias points)
    I_fwd = Gr.signals['Current (A)'] # 3d set (dim_px,dim_py,bias)
    I_bwd = Gr.signals['Current [bwd] (A)'] # I bwd
    # sometimes, LI channel names are inconsistent depends on program ver. 
    # find 'LI Demod 1 X (A)'  or  'LI X 1 omega (A)'

    #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ])
    # 'LI' & 'X' in  channel name (signal.keys) 
    LIX_keys = [s  for s in Gr.signals.keys()  if "LI"  in s  if "X" in s ]
    # 0 is fwd, 1 is bwd 
    LIX_fwd, LIX_bwd = Gr.signals[LIX_keys[0]] ,Gr.signals[LIX_keys[1] ]

    # same for LIY
    #print( [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ])
    # 'LI' & 'Y' in  channel name (signal.keys) 
    LIY_keys = [s  for s in Gr.signals.keys()  if "LI"  in s  if "Y" in s ]
    # 0 is fwd, 1 is bwd 
    LIY_fwd, LIY_bwd = Gr.signals[LIY_keys[0]] ,Gr.signals[LIY_keys[1] ]


    ###########################################################
    #plt.imshow(topography) # toppography check
    #plt.imshow(I_fwd[:,:,0]) # LIX  check
    ###########################################################

    ##########################################################
    # Title for Grid data 
    #############################################################
    # Gr.header.get('Bias>Bias (V)') # bias condition 
    # Gr.header.get('Z-Controller>Setpoint') # current set  condition
    # Gr.header.get('dim_px')  # jpixel dimension 
    title = Gr.basename +' ('  + str(
        float(Gr.header.get('Bias Spectroscopy>Sweep Start (V)'))
    ) +' V ~ ' +str( 
        float(Gr.header.get('Bias Spectroscopy>Sweep End (V)'))
    )+ ' V) \n at Bias = '+ Gr.header.get(
        'Bias>Bias (V)'
    )[0:-3]+' mV, I_t =  ' + Gr.header.get(
        'Z-Controller>Setpoint'
    )[0:-4]+ ' pA, '+str(
        Gr.header.get('dim_px')[0]
    )+' x '+str(
        Gr.header.get('dim_px')[1]
    )+' points' + '1D line spectroscopy'
    #############################################################       

    ### some times the topography does not look right. 
    # * then use the reshaping function 
    # only for asymmetry grid data set

    # eg) JW's MoS2 on HOPG exp. data 

    ###########################################################
    # assign topography as topography_reshape
    ###########################################################
    topo_dimension_true = True
    # if topography looks normal.
    ################################
    if topo_dimension_true == True:
        topography_reshape = topography   
        #################################
        I_fwd_copy = I_fwd
        I_bwd_copy = I_bwd
        LIX_fwd_copy = LIX_fwd 
        LIX_bwd_copy = LIX_bwd 	
        
    else:
        # if a topography looks abnormal
        # it is very rare case, 
        # but I leave manual setting to remind "mistake!"
        
        
        ##########################################################
        # if there is an error or mixed array for 
        ##########################################################
        # adjust lattice manually 
        ##########################################################
        # for example
        # some times 40 x 80 array shape --> 40x40 + 40 x40
        # because of mischoosen step & shape setting 
        # X one line = 0-39: 1st line + 40-79 
        # in this case 
        # make a new arrary (vertically)
        # 0-39 --> 2n & 40-79 -->  2n+1 
        # topo # LIX f&b # I f&b #
        ##########################################################

        
        topography_reshape = np.transpose(np.copy(topography),(1,0)) 
        # make a new lattcie with reshaped dimension 
        for x_indx, y_indx in enumerate (topography):
        # print(x_indx) # 0-39 # print(y_indx.shape)
            topography_reshape[2*x_indx,:] = y_indx[:40] # reshaping first half
            topography_reshape[2*x_indx+1,:] = y_indx[40:80] # reshaping second half
        #################################
        # same deformation for I& LIX 
        #################################
        # check the topographyt 
        plt.imshow(topography_reshape) # 80 * 40 OK
        # topography_reshape is done. 
        
        #################################
        # make a new lattcie with reshaped dimension 
        I_fwd_copy = np.transpose(np.copy(I_fwd),(1,0,2))
        I_bwd_copy = np.transpose(np.copy(I_bwd),(1,0,2)) 
        
        for x_indx, yNbias_plane in enumerate (I_fwd): 
            # make a new lattcie with reshaped dimension 
            print(x_indx) # 0-39 
            I_fwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            I_fwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half

        for x_indx, yNbias_plane in enumerate (I_bwd): 
            # make a new lattcie with reshaped dimension 
            print(x_indx) # 0-39 
            I_bwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            I_bwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        #################################
        # I reshape is done 
        #################################
        LIX_fwd_copy = np.transpose(np.copy(LIX_fwd),(1,0,2)) 
        LIX_bwd_copy = np.transpose(np.copy(LIX_bwd),(1,0,2)) 
        # make a new lattcie with reshaped dimension 
        for x_indx, yNbias_plane in enumerate (LIX_fwd): 
            LIX_fwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            LIX_fwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        for x_indx, yNbias_plane in enumerate (LIX_bwd): 
            LIX_bwd_copy[2*x_indx,:,:] = yNbias_plane[:40,:] 
            # reshaping first half
            LIX_bwd_copy[2*x_indx+1,:,:] = yNbias_plane[40:80,:] 
            # reshaping second half
        #################################
        # LIX reshape is done 
        #################################

    # after reshaping 

    topography = topography_reshape 
    #################################
    I_fwd = I_fwd_copy 
    I_bwd = I_bwd_copy 
    LIX_fwd  = LIX_fwd_copy 
    LIX_bwd  = LIX_bwd_copy
    ##########################################################


    ###########################
    # Bias segment check      #
    ###########################
    Segment = Gr.header['Bias>Bias (V)']
    # bias unit : '(V)' 

    if type(Segment) == str: # single segment case
        print ('No Segments\n'+ 'Grid data acquired at bias = '+  str(float(Segment)) + 'V')    
    ## No Segments # +  bias setting 

    ########################
    # bias interpolation to have a "zero" bias 
    # interpolate bias_mV that include "zero" bias 
    # in 3D data : center x,y bias interpolation 
    # e.g  256--> including end points + zero  = 256+1 ( the center is "0")
        if len(bias)%2==0:
            bias_new = np.linspace(bias[0],bias[-1],num=(len(bias)+1)) 
            # if bias length is even_number 
            # including "0", total size is "len+1" 
        else:# if bias length is odd_number 
            bias_new = np.linspace(bias[0],bias[-1],num=(len(bias))) 
            # bias_new make a odd number of length
            # make only one value is closest to the zero. 
            
        nearest_zero_bias = np.where(abs(bias_new) == np.amin(abs(bias_new))) 
        # find the index of closest to "0" bias 
        bias_new = bias_new - bias_new[nearest_zero_bias] 
        # assign closest zero vavlue as a zero. 
        #bias_new[np.where(bias_new == np.amin(abs(bias_new)))]=0

    ##############################################
    #'Segment Start (V), Segment End (V), Settling (s), Integration (s), Steps (xn)'
    elif len(Segment) == 3:
        print('Number of Segments =' + str(len(Segment))) 
        Segments = np.array([[ float(Segments) 
                              for Segments in Seg.split(',') ] 
                             for Seg in Segment], dtype = np.float64)
        # in the Segment, split strings sith "," 
        #  make a array after change it as float. 
        # check Nanonispy version
        # bias value could be not correct. 
        
        Seg1 = np.linspace(Segments[0,0],Segments[0,1],int(Segments[0,-1]))
        Seg2 = np.linspace(Segments[1,0],Segments[1,1],int(Segments[1,-1]))
        Seg3 = np.linspace(Segments[2,0],Segments[2,1],int(Segments[2,-1]))
        # except boundary end points,  combine segments ([1:]), Seg1, Seg2[1:], Seg3[1:] 
        bias_Seg = np.append(np.append(Seg1,Seg2[1:]),Seg3[1:]) 
        # Seg1 +  Seg2[1:] +  Se3[1:] 
        # make a clever & shoter way 'later...'
        print ('bias_Seg size = ' + str(len(bias_Seg)))
        bias_Nsteps=int(int(Segments[1,-1])/
                        (Seg2[-1]-Seg2[0])*(bias_Seg[-1]-bias_Seg[0]))
        # New bias Steps uses smallest step as a new stpe size. 
        bias_Nsteps_size = (Seg2[-1]-Seg2[0])/(Segments[1,-1])
        # (Segments[1,0]-Segments[1,1])/int(Segments[1,-1]) # bias step size    
        Neg_bias=-1*np.arange(
            0,bias_Nsteps_size*bias_Nsteps/2, bias_Nsteps_size)
        Pos_bias=np.flip(
            np.arange(0,bias_Nsteps_size*bias_Nsteps/2,bias_Nsteps_size))
        bias_new = np.flip( np.append(Pos_bias,Neg_bias[1:])) 
        # after segments, 
        # bias is called as  bias_new
        ##################################
        # now make the bias_new as an odd number. 
        ###################################
        if len(bias_new)%2==0:
            bias_new = np.linspace(bias_new[0],bias_new[-1],num=(len(bias_new)+1)) 
        else:
            bias_new = np.linspace(bias_new[0],bias_new[-1],num=(len(bias_new))) 
        # check  bias_new contians "zero" 
        nearest_zero_bias = np.where(abs(bias_new) == np.amin(abs(bias_new))) 
        # check index of the nearest value to zero "0"
        bias_new = bias_new - bias_new[nearest_zero_bias] 
        # adjust bias range for bias_new has "zero" 
        print ('bias_new size = ' + str(len(bias_new)))
        # bias 
    # make a new list for Bias
    else:
        print ("Segment error /n code a 5 Sements case")
    #
    ######################################################################
    # make a new bias length (including Segments) as a odd number, including zero
    ######################################################################


    ######################################################################
    # interpolation using bias_new 
    # I_fwd, I_bwd, LIX_fwd, LIX_bwd
    # => I_fwd_interpolate
    #######################################################################
    # assign a function using interpolation 
    # the same as original bias values 
    # make empty np array  & interpolate using scipy
    # xy dim is not changed here, 
    # only 3rd axis changed as new bias 
    ###########################
    def sweep_interpolation(np3Ddata, bias, bias_new):
        np3Ddata_interpolate = np.empty(
                    (np3Ddata.shape[0],np3Ddata.shape[1],bias_new.shape[0])) 

        for x_i,np3Ddata_xi in enumerate(np3Ddata):
            for y_j,np3Ddata_xi_yj in enumerate(np3Ddata_xi):
                #print (np3Ddata_xi_yj.shape)
                Interpolation1D_i_f = sp.interpolate.interp1d(
                    bias,
                    np3Ddata_xi_yj,
                    fill_value = "extrapolate",
                    kind = 'cubic')
                np3Ddata_interpolate[x_i,y_j,:] = Interpolation1D_i_f(bias_new)
        return np3Ddata_interpolate

    I_fwd_interpolate = sweep_interpolation (I_fwd, bias, bias_new)
    I_bwd_interpolate = sweep_interpolation (I_bwd, bias, bias_new)
    LIX_fwd_interpolate = sweep_interpolation (LIX_fwd, bias, bias_new)
    LIX_bwd_interpolate = sweep_interpolation (LIX_bwd, bias, bias_new)

    ####################################################
    # to prevent error for bias direction 
    # 
    ##
    #  assign the bias direction 
    ## up or down ==> up anyway. 
    ###################################################
    if bias[0]>bias[-1]: 
        # if starting point is larger than end point. 
        # start from pos & end to neg
        # no changes. 
        print ('start from POS bias')
        I_fwd = I_fwd_interpolate
        I_bwd = I_bwd_interpolate
        LIX_fwd = LIX_fwd_interpolate
        LIX_bwd = LIX_bwd_interpolate
        bias_mV = bias_new*1000
    else:  # if end point is larger than start point. 
        # start from neg & end to pos
        # change to negative 
        print ('start from NEG bias')
        I_fwd = np.flip(I_fwd_interpolate,2)
        I_bwd = np.flip(I_bwd_interpolate,2)
        LIX_fwd = np.flip(LIX_fwd_interpolate,2)
        LIX_bwd = np.flip(LIX_bwd_interpolate,2)
        bias_new_flip = np.flip(bias_new)
        bias_mV = bias_new_flip*1000
        print ('Flip => start from POS bias')
    ####################################################

    ###################################################
    # convert data XR DataSet
    ####################################################
    

    # col = x 
    # row = y
    # I_fwd grid data ==> [Y, X, bias]
    grid_xr = xr.Dataset(
        {
            "I_fwd" : (["Y","X","bias_mV"], I_fwd),
            "I_bwd" : (["Y","X","bias_mV"], I_bwd),
            "LIX_fwd" : (["Y","X","bias_mV"], LIX_fwd),
            "LIX_bwd" : (["Y","X","bias_mV"], LIX_bwd),
            "topography" : (["Y","X"], topography)
        },
        coords = {
            "X": (["X"], x),
            "Y": (["Y"], y),
            "bias_mV": (["bias_mV"], bias_mV)
        }
    )
    grid_xr.attrs["title"] = title
    #grid_xr.attrs['image_size'] = 
    #grid_xr.attrs['samlpe'] = 
    
    grid_xr.attrs['image_size']= [size_x,size_y]
    grid_xr.attrs['X_spacing']= step_dx
    grid_xr.attrs['Y_spacing']= step_dy    
    grid_xr.attrs['freq_X_spacing']= 1/step_dx
    grid_xr.attrs['freq_Y_spacing']= np.nan
    
    # in case of real X Y ( center & size of XY)
    if center_offset == True:
        # move the scan center postion in real scanner field of view
        grid_xr.assign_coords( X = (grid_xr.X + cntr_x -  size_x/2))
        grid_xr.assign_coords( Y = (grid_xr.Y + cntr_y -  size_y/2))
    else :
        pass
        # (0,0) is the origin of image 
    
    
    return grid_xr

# ## <font color=blue>5. Gwyddion 2D image to PANDAS Dataframe or Xarray </font>
# ### 5.1. gwy_image2df 
# * convert to df 
# ### 5.2. gwy_df_channel2xr 
# * convert to xr
# * need some upgrade.. (later) 
#
#

# +


def gwy_img2df(gwy_file_name):
    """
    Load data from a Gwyddion file and convert it into a Pandas DataFrame.

    Parameters:
    gwy_file_name (str): The name of the Gwyddion file to be loaded.

    Returns:
    pd.DataFrame: A Pandas DataFrame containing the data from the Gwyddion file.

    This function loads data from a Gwyddion file specified by `gwy_file_name` and converts
    it into a Pandas DataFrame. It first checks if the required 'gwyfile' module is installed
    and installs it if not. The resulting DataFrame contains the data fields from the Gwyddion
    file.
    """
    try:
        import gwyfile
    except ModuleNotFoundError:
        warn('ModuleNotFoundError: No module named gwyfile')
        # %pip install gwyfile
        import gwyfile

    gwyfile_df = pd.DataFrame(gwyfile.util.get_datafields(gwyfile.load(gwy_file_name)))

    # Set display format for scientific notation
    pd.set_option('display.float_format', '{:.3e}'.format)

    return gwyfile_df


#gwy_df = gwyImage2df( file_list_df.file_name[1])

# +
import pandas as pd
import xarray as xr

def gwy_df_ch2xr(gwy_df, ch_N=0):
    """
    Convert channel data from a Pandas DataFrame to an xarray DataArray format.

    Parameters:
    gwy_df (pd.DataFrame): The input Pandas DataFrame containing channel data.
    ch_N (int, optional): The channel index to convert (default is 0).

    Returns:
    xr.DataArray: An xarray DataArray containing the channel data with proper coordinates.
    
    This function takes a DataFrame (`gwy_df`) and an optional `ch_N` parameter to specify
    which channel to convert into an xarray DataArray format. It reshapes the channel data
    into a 2D DataFrame, stacks it, and assigns 'Y' and 'X' coordinates with proper scaling.
    
    Parameters:
    - gwy_df (pd.DataFrame): The input Pandas DataFrame containing channel data.
    - ch_N (int, optional): The channel index to convert (default is 0).

    Returns:
    - xr.DataArray: An xarray DataArray containing the channel data with proper coordinates.

    This function takes a Pandas DataFrame (`gwy_df`) containing channel data and an optional
    parameter `ch_N` to specify the channel index to convert. It reshapes the channel data into
    a 2D DataFrame, stacks it, and assigns 'Y' and 'X' coordinates with proper scaling. The result
    is returned as an xarray DataArray.

    Example:
    ch_data = gwy_df_ch2xr(my_dataframe, ch_N=1)
    print(ch_data)
    """
    # Extract the channel data from the DataFrame
    chN_df = gwy_df.iloc[:, ch_N]

    # Reshape the channel data into a 2D DataFrame and stack it
    chNdf_temp = pd.DataFrame(chN_df.data.reshape((chN_df.yres, chN_df.xres))).stack()

    # Rename the indices as 'Y' and 'X'
    chNdf_temp = chNdf_temp.rename_axis(['Y', 'X'])

    # Calculate the x and y step sizes
    x_step = chN_df.xreal / chN_df.xres
    y_step = chN_df.yreal / chN_df.yres

    # Convert the DataFrame to an xarray DataArray
    chNxr = chNdf_temp.to_xarray()

    # Assign coordinates 'X' and 'Y' with proper scaling
    if np.isnan(chN_df['xoff']):
        chN_df.xoff = 0
    else : pass
    if np.isnan(chN_df['yoff']):
        chN_df.yoff = 0
    else : pass
    chNxr = chNxr.assign_coords(X=chNxr.X.values * x_step+chN_df.xoff, Y=chNxr.Y.values * y_step+chN_df.xoff)

    return chNxr



# -

def gwy_df2xr (gwy_df):
    """
    Convert a Pandas DataFrame into a dictionary of Xarray DataArrays and Xarray Datasets.

    Parameters:
    gwy_df (pandas.DataFrame): The input DataFrame to be converted.

    Returns:
    dict: A dictionary containing Xarray DataArrays and Xarray Datasets.

    This function takes a Pandas DataFrame 'gwy_df' and performs the following steps:
    1. Extracts unique 'xres' values from the DataFrame.
    2. Creates a list to store the results.
    3. Groups the DataFrame by each unique 'xres' value and creates a separate DataFrame for each group.
    4. Checks if each group has the same 'yres' values; if yes, it appends the group to the results list.
    5. Initializes an empty dictionary to store Xarray DataArrays and Xarray Datasets.
    6. Prepares empty Xarray DataArrays and adds them to the dictionary.
    7. Iterates through the dictionary, creating Xarray Datasets and populating them with converted DataArrays.
    8. Returns a dictionary containing different-sized Xarray Datasets.

    Note: This function relies on 'gwy_df_ch2xr', which should be defined separately to convert DataFrames to Xarray DataArrays.

    Example:
    gwy_dict = gwy_df2xr(my_dataframe)
    for key, value in gwy_dict.items():
        print(f"Name: {key}, Data: {value}")
    """
    # Get unique xres values.
    unique_xres_values = gwy_df.loc['xres'].unique()

    # Create a list to store the results.
    result_dfs = []
    # Create groups for each xres value and create a separate DataFrame for each group.
    for xres_value in unique_xres_values:
        group_df = gwy_df[gwy_df.columns[gwy_df.loc['xres'] == xres_value]]
        # group_df with the same xres
        unique_yres_values = group_df.loc['yres'].unique()
        if len(unique_yres_values) == 1:
            result_dfs.append(group_df)
        else:
            for yres_value in unique_yres_values:
                group_df = gwy_df[gwy_df.columns[gwy_df.loc['yres'] == yres_value]]
                result_dfs.append(group_df)
        
    # result_dfs is group_dfs list with different 'xres'
    # group_dfs = channels with unique xres&yres
    gwy_xr_dict = {}
    # prepare empty dictionary for gwy_xrs 
    # this is because of different X&Y size of eqch group.  
    for results_df_i in range(1,len(result_dfs)+1):
        # number of unique groups in result_df 

        gwy_xr_dict[f'gwy_xr{results_df_i}'] = xr.DataArray()
        #prepare Data Set
        # Create a dictionary to store empty Xarrays (DataArrays)


    for i, gwy_xr_i in enumerate(gwy_xr_dict.keys()):
        # call each gwy_xrs
        # use keys() 
        print(gwy_xr_i)
        gwy_xr_j  = xr.Dataset()
        for j, group_df in enumerate(result_dfs[i]):
            # call group_df from results_dfs
            print (j)
            xr_array = gwy_df_ch2xr(result_dfs[i], ch_N=j)
            gwy_xr_j[result_dfs[i].columns[j]] = xr_array
            # convert single dataframe, ch_N = j as a xr_array 

            gwy_xr_dict[gwy_xr_i] = gwy_xr_j
            # save Data array in empty DataSet
    # Xarray dictionary consist of different size DataSet     
    return gwy_xr_dict



# +
def rename_gwy_xr_data_vars(variable):
    # Check if "Corrected" is included
    if "FFT" in variable or "fft" in variable:
        return variable
    else :
        if "Corrected" in variable:
            variable = variable.replace("Corrected", "_C")
            # Check if "Z" is included
            if "Z" in variable or "z(" in variable:
                # Check if "forward" is included
                if "Forward" in variable or "fwd" in variable:            
                    # Get the index of the last '_C'.
                    #index = variable.rfind("_C")
                    #return variable.replace(variable[:index], "z_f")
                    return variable.replace(variable, "z_f_C")
                # Check if "backward" is included
                elif "Backward" in variable or "bwd" in variable:
                    # Get the index of the last '_C'.
                    #index = variable.rfind("_C")
                    #return variable.replace(variable[:index], "z_b")
                    return variable.replace(variable, "z_b_C")

            # Check if "LI" is included
            elif "LI" in variable:
                # Check if "X" and "forward" are included
                if "X" in variable : 
                    if "Forward" in variable or "fwd" in variable:
                        # Get the index of the last '_C'.
                        #index = variable.rfind("_C")
                        #return variable.replace(variable[:index], "LIX_f")
                        return variable.replace(variable, "LIX_f_C")
                    if "Backward" in variable or "bwd" in variable:
                        # Get the index of the last '_C'.
                        #index = variable.rfind("_C")
                        #return variable.replace(variable[:index], "LIX_b")
                        return variable.replace(variable, "LIX_b_C")

                elif "Y" in variable : 
                    if "Forward" in variable or "fwd" in variable:
                        # Get the index of the last '_C'.
                        #index = variable.rfind("_C")
                        #return variable.replace(variable[:index], "LIY_f")
                        return variable.replace(variable, "LIY_f_C")
                    if "Backward" in variable or "bwd" in variable:
                        # Get the index of the last '_C'.
                        #index = variable.rfind("_C")
                        #return variable.replace(variable[:index], "LIY_b")
                        return variable.replace(variable, "LIY_b_C")
            else:
                return variable
        else:
            if "Z" in variable or  "z(" in variable:
                # Check if "forward" is included
                if "Forward" in variable or "fwd" in variable:            
                    return variable.replace(variable, "z_f")
                # Check if "backward" is included
                elif "Backward" in variable or "bwd" in variable:
                    return variable.replace(variable, "z_b")

            elif "LI" in variable:
                # Check if "X" and "forward" are included
                if "X" in variable : 
                    if "Forward" in variable or "fwd" in variable:
                        return variable.replace(variable, "LIX_f")
                    if "Backward" in variable or "bwd" in variable:
                        return variable.replace(variable, "LIX_b")
        return variable

# Rename the data variables.



# -

def crop_square(image_xr, ch_name = 'z_f_C'):
    """
    Crop a square from the input image_xr centered at the center of the image.
    # DO NOT APPLY WHEN PIXEL ASPECT RATIO IS NOT 1 
    # ( eg. 1024x512 case==> not apply ) 
    # Use it for after affine transformed lattice 
    
    Args:
        image (ndarray): Input image as a numpy array.

    Returns:
        ndarray: Cropped square from the input image.
    """
    # Create the image size and generate nan values in a rectangle
    image_size = image_xr[ch_name].shape
    image_copy = np.copy(image_xr[ch_name])
    #image_copy[np.random.choice(image_size[0], 10), np.random.choice(image_size[1], 10)] = np.nan

    # Find the largest square without nan values
    max_square_size = 0
    for size in range(min(image_size)):
        y_start = (image_size[0]) // 2 - size // 2
        y_end = (image_size[0]) // 2 + size // 2
        x_start = (image_size[1]) // 2 - size // 2
        x_end = (image_size[1]) // 2 + size // 2
        if np.isnan(image_copy[y_start:y_end+1, x_start:x_end+1]).any():
            break
    may_square_size = size

    # Create a small square with the same size as the large image
    #square = np.zeros((may_square_size, may_square_size))

    # Set the center coordinates to match the large image and draw the small square
    center_y = (image_size[0]+1) // 2
    center_x = (image_size[1]+1) // 2
    center = (center_y, center_x)
    y_start = center_y - may_square_size // 2
    y_end = center_y + may_square_size // 2 
    x_start = center_x - may_square_size // 2
    x_end = center_x + may_square_size // 2 
    print(center, 'may_square_size', may_square_size)
    print ('X',x_start,y_end,'Y',y_start, y_end)
    image_xr_xycrop = image_xr.isel(Y = slice (y_start-1, y_end+1), X = slice (x_start-1,x_end+1))
    #image_xr_xycrop = image_xr_xcrop.isel(Y = slice (y_start-1, y_end+1))
    
    
    # Adjust XY size for 1:1 ratio. 
    size_min = min(image_xr_xycrop.X.shape, image_xr_xycrop.Y.shape)[0]
    image_xr_xycrop = image_xr_xycrop.isel( Y = slice (0,size_min),X = slice (0,size_min))
    # strangely without this line Y_size != X size 
    
    return image_xr_xycrop


# +
def gwy_intrplt_xr(xrdata):
    """
    Perform interpolation on the given xrdata.

    Parameters:
    - xrdata (xarray.Dataset): Input xr dataset to be interpolated.

    Returns:
    - xrdata (xarray.Dataset): Interpolated xr dataset.
    """
    ############################
    # check the XY ratio /w spacing size
    ############################ 
    if  xrdata.X.X_spacing == xrdata.Y.Y_spacing: 
        pass
    else : 
        print ('X_spacing != Y_spacing')
    # if xy size is not same, report it! 
    step_dx = xrdata.X.X_spacing
    step_dy = xrdata.Y.Y_spacing
    if step_dx != step_dy :
        xystep_ratio = xrdata.dims['X']/xrdata.dims['Y'] # check the XY pixel_ratio
        X_interp = np.linspace(xrdata.X[0], xrdata.X[-1], xrdata.X.shape[0]*1)
        step_dx = step_dx # step_dx check 

        Y_interp = np.linspace(xrdata.Y[0], xrdata.Y[-1], int(xrdata.Y.shape[0]*xystep_ratio)) 
        step_dy = step_dy/ xystep_ratio # step_dy check 

        # interpolation ratio should be int
        xrdata= xrdata.interp(X = X_interp, Y = Y_interp, method="linear")
        print('step_dx/step_dy = ', xystep_ratio)
        print ('xrdata ==> reshaped')
    else: print('step_dx == step_dy')
        
    print('gwy_xr', 'step_dx, step_dy = ', 
      re.findall('\{([^}]+)', str(xrdata.dims)))
    return xrdata

#gwy_intrplt_xr(gwy_xr)
# -




