pydap.handlers.hdf5
===================

This handler allows Pydap to serve data from HDF5 files using
[h5py](https://code.google.com/p/h5py/). It uses the 
[high level interface](http://www.h5py.org/docs/high/index.html) from h5py, 
mapping `h5py.Dataset` objects to DAP arrays, and `h5py.Group` objects to DAP
structures.

If the dataset has an attribute called `Map Projection` with the value
`Equidistant Cylindrical` the latitude and longitude axes will be automatically
created, allowing the data to be plotted on a map.
