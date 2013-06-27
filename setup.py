from setuptools import setup, find_packages
import sys, os


version = '0.2'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'h5py',
    'Pydap>=3.2',
    'Numpy',
]


setup(name='pydap.handlers.hdf5',
    version=version,
    description="HDF5 handler for Pydap",
    long_description="""
This handler allows Pydap to serve data from HDF5 files using                   
`h5py <https://code.google.com/p/h5py/>`_. It uses the                            
`high level interface <http://www.h5py.org/docs/high/index.html>`_ from h5py,     
mapping ``h5py.Dataset`` objects to DAP arrays, and ``h5py.Group`` objects to
DAP  structures.                                                                     
                                                                                
If the dataset has an attribute called ``Map Projection`` with the value          
``Equidistant Cylindrical`` the latitude and longitude axes will be automatically 
created, allowing the data to be plotted on a map.
""",
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='HDF5 opendap dods dap science meteorology oceanography',
    author='Roberto De Almeida',
    author_email='roberto@dealmeida.net',
    url='https://github.com/robertodealmeida/pydap.handlers.hdf5',
    license='MIT',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['pydap', 'pydap.handlers'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points="""
        [pydap.handler]
        hdf5 = pydap.handlers.hdf5:HDF5Handler
    """,
)
