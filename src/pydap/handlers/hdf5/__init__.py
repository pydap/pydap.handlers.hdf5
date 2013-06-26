"""Pydap handler for HDF5 files using h5py."""

import os
import re
import time
from stat import ST_MTIME
from email.utils import formatdate

import numpy as np
import h5py
from pkg_resources import get_distribution

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError


class HDF5Handler(BaseHandler):

    """A simple handler for HDF5 files based on h5py."""

    __version__ = get_distribution("pydap.handlers.hdf5").version
    extensions = re.compile(r"^.*\.(h5|hdf5)$", re.IGNORECASE)

    def __init__(self, filepath):
        BaseHandler.__init__(self)

        try:
            self.fp = h5py.File(filepath, 'r')
        except Exception, exc:
            message = 'Unable to open file %s: %s' % (filepath, exc)
            raise OpenFileError(message)

        self.additional_headers.append(
            ('Last-modified', (
                formatdate(
                    time.mktime(
                        time.localtime(os.stat(filepath)[ST_MTIME]))))))

        # build dataset
        name = os.path.split(filepath)[1]
        self.dataset = DatasetType(name, attributes={
            "NC_GLOBAL": dict(self.fp.attrs),
        })
        build_dataset(self.dataset, self.fp)


def get_axes(attrs):
    """Return lat and lon axes."""
    lat_bnds = np.linspace(
        attrs['Northernmost Latitude'],
        attrs['Southernmost Latitude'],
        attrs['Number of Lines']+1)
    lat = (lat_bnds[:-1] + lat_bnds[1:])/2.
    lon_bnds = np.linspace(
        attrs['Westernmost Longitude'],
        attrs['Easternmost Longitude'],
        attrs['Number of Columns']+1)
    lon = (lon_bnds[:-1] + lon_bnds[1:])/2.

    return lat, lon


def build_dataset(target, group):
    """Recursively build a dataset, mapping groups to structures."""
    for name in group:
        if isinstance(group[name], h5py.Group):
            target[name] = StructureType(name)
            build_dataset(target[name], group[name])
        else:
            # add extra dimensions if possible
            if group.attrs.get("Map Projection") == "Equidistant Cylindrical":
                lat, lon = get_axes(group.attrs)
                g = target[name] = GridType(name, dict(group[name].attrs))
                g[name] = BaseType(
                    name, group[name], ('lat', 'lon'), dict(group[name].attrs))
                g['lat'] = target['lat'] = BaseType(
                    'lat', lat, None,
                    dict(axis='Y', units='degrees_north'))
                g['lon'] = target['lon'] = BaseType(
                    'lon', lon, None, dict(axis='X', units='degrees_east'))
            else:
                target[name] = BaseType(
                    name, group[name], None, dict(group[name].attrs))


if __name__ == "__main__":
    import sys
    from werkzeug.serving import run_simple

    application = HDF5Handler(sys.argv[1])
    run_simple('localhost', 8001, application, use_reloader=True)
