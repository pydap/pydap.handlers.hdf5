import os
import re
import time
from stat import ST_MTIME
from email.utils import formatdate

import numpy
import h5py

from arrayterator import Arrayterator

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError
from pydap.lib import quote


class Handler(BaseHandler):

    extensions = re.compile(r"^.*\.(h5|hdf5)$", re.IGNORECASE)

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_constraints(self, environ):
        buf_size = int(environ.get('pydap.handlers.netcdf.buf_size', 10000))

        try:
            fp = h5py.File(self.filepath, 'r')
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        last_modified = formatdate( time.mktime( time.localtime( os.stat(self.filepath)[ST_MTIME] ) ) )
        environ['pydap.headers'].append( ('Last-modified', last_modified) )

        dataset = DatasetType(name=os.path.split(self.filepath)[1],
                attributes={'NC_GLOBAL': dict(fp.attrs)})

        fields, queries = environ['pydap.ce']
        fields = fields or [[(name, ())] for name in fp.keys()]
        for var in fields:
            get_child(fp, dataset, var, buf_size)

        dataset._set_id()
        dataset.close = fp.close
        return dataset


def get_child(source, target, var, buf_size):
    for name, slice_ in var:
        if name not in source or name.startswith('_i_'):  # hide pytables indexes
            break

        if isinstance(source[name], (h5py.Dataset, numpy.ndarray)):
            dtype = source[name].dtype
            if len(dtype):
                # array has composite dtype, we need to transform it in a Structure
                attrs = dict(getattr(source[name], 'attrs', {}))
                target.setdefault(name, StructureType(name=name, attributes=attrs))
                target = target[name]
                data = source[name]
                source = {}
                for child in dtype.names:
                    source[child] = data[child]
            else:
                # regular array, return data and exit
                target[quote(name)] = get_var(name, source, slice_, buf_size)
                break
        elif name in source and isinstance(source[name], h5py.Group):
            # group, return Structure
            attrs = dict(source[name].attrs)
            target.setdefault(name, StructureType(name=name, attributes=attrs))
            target = target[name]
            source = source[name]
    else:
        # when a group is requested by itself, return with all children
        for name in source.keys():
            get_child(source, target, [(name, ())], buf_size)


def get_var(name, source, slice_, buf_size=10000):
    var = source[name]
    if var.dtype == numpy.complex:
        data = var = numpy.dstack((var.real, var.imag))
    elif var.shape:
        data = Arrayterator(var, buf_size)[slice_]
    else:
        data = numpy.array(var.value)
    typecode = var.dtype.char
    attrs = dict(getattr(source[name], 'attrs', {}))
    if hasattr(var, 'fillvalue'):
        attrs['_FillValue'] = var.fillvalue

    return BaseType(name=name, data=data, shape=data.shape,
            type=typecode, attributes=attrs)


if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
