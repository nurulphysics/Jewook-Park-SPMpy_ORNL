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

# # SPMpy data analysis procedure 
#
# * 2023 0723 update 
#     * Jewook Park 
#
#
# * xarray : data container  (metadata + dataframe)  
# * processing dat ""
#
# ## Image data 
# * sxm/gwy files $ \to $ xarray DataSet
#     * file_loading (img2xr)
# ## 3DS data 
# * 3ds $ \to $ xarray DataSet
#     * file_loading (grid2xr, line2xr
#
# ## xr data pretreatment  
# * automated process 
#     * selected process: fwd/bwd, crop, rotation, drift correction. 
#
# ## xr dat analysis 
# * fft
# * affine 
# * piecewise affine 
#
# ## save xr 
# * data saving format **netCDF**
#
#

# ## Xarray as a data container 
# * xarray document [page](https://docs.xarray.dev/en/stable/index.html)
#     * SPM data is multi-dimensional: 
#     * xr DataSet is more convinient than PANDAS MultIndex
# * SPM data is composed of **MetaData** & **DataFrame** 
#     * MetaData 
#         * Data of Data
#     * DataFrame 
#         * Data with cooridinates 
#
#

# +
# SPMpy functions


# -

# ## line profile 
# * from SPMpy_2D_data_analysis_funcs
#
#     * line_profile_xr_GUI(xrdata, ch_N = 0, profile_width = 3)
#         * single channel (topo: cmap = 'copper')
#     * line_profile2_xr_GUI(xrdata, ch_N = [0,2], profile_width = 3):
#         * two channel 
#         
#     * use magic command first "%matplotlib qt5"
#         * use magic command after drawing  "%matplotlib inline"
#     
#
#


