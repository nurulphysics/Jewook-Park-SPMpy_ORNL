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

import numpy as np
import matplotlib.pyplot as plt
# !pip install latticegen
import latticegen

lattice = latticegen.anylattice_gen(r_k=0.01, theta=0,
                                    order=1, symmetry=4)
lattice.to_dask_dataframe()

import xarray as xr


# +
#to make an np array 

lattice_np = np.array(lattice).shape
# -

xr.DataArray (lattice_np)

import seaborn_image as isns
isns.imshow(lattice)

fete_lttc = latticegen.latticegeneration.physical_lattice_gen(a_0=0.3975,
                                                              theta=0, 
                                                              order=2, 
                                                              pixelspernm=512/8, 
                                                              symmetry='square', 
                                                              size=512, epsilon=None,) 
                                                              #delta=0.16, )


plt.imshow(fete_lttc)
#plt.imshow(fete_lttc[0:30, 0:30])


