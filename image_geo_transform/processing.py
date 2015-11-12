import os
import tempfile
import re

from twisted.web.client import Agent
from twisted.internet import reactor, defer, protocol
from twisted.internet.defer import inlineCallbacks, returnValue

from .fs import write_body_to_file


class ProcessProtocolDeferred(protocol.ProcessProtocol):
    def __init__(self, deferred):
        self.deferred = deferred
        self.result = []
    
    def outReceived(self, data):
        self.result.append(data)
    
    def processEnded(self, reason):
        self.deferred.callback(''.join(self.result))

class ImageProcessingError(Exception):
    pass

class ImageProcessing(object):
    
    def __init__(self, save_dir):
        self.save_dir = save_dir
    
    @inlineCallbacks
    def get_source_image(self, url):
        agent = Agent(reactor)
        resp = yield agent.request('GET', url)
        fp = tempfile.NamedTemporaryFile()
        result = yield write_body_to_file(resp, fp)
        returnValue(fp)

    @inlineCallbacks
    def get_image_size(self, filepath):
        d = defer.Deferred()
        yield reactor.spawnProcess(ProcessProtocolDeferred(d), "gdalinfo", ['gdalinfo', filepath], {})
        image_info = yield d
        groups = re.search('Size is (?P<x_size>\d+), (?P<y_size>\d+)', image_info)
        if not groups:
            raise ImageProcessingError(u'could not open image')
        x_size = groups.group('x_size')
        y_size = groups.group('y_size')
        
        returnValue((x_size, y_size))

    def get_gcps(self, form, x_size, y_size):
        f = form.data
        gcps = (
            (0, 0, f['upper_left_x'], f['upper_left_y']),
            (x_size, 0, f['upper_right_x'], f['upper_right_y']),
            (x_size, y_size, f['lower_right_x'], f['lower_right_y']),
            (0, y_size, f['lower_left_x'], f['lower_left_y']),
        )
        return gcps

    @inlineCallbacks
    def get_georeferenced_image(self, form):
        georef_file = os.path.join(self.save_dir, '%s.tif' % form.get_hash())
        
        if os.path.exists(georef_file):
            returnValue(georef_file)
        
        fp = yield self.get_source_image(form.data['image_url'])
        filepath = fp.name
        x_size, y_size = yield self.get_image_size(filepath)
        d = defer.Deferred()
        args = '-of GTiff -a_srs EPSG:4326'
        for gcp in self.get_gcps(form, x_size, y_size):
            args += ' -gcp %s %s %s %s' % gcp
        args = args.split(' ')
        args = ['gdal_translate'] + args + [filepath, georef_file]
        yield reactor.spawnProcess(ProcessProtocolDeferred(d), "gdal_translate", args, {})
        yield d
        if not os.path.exists(georef_file):
            raise ImageProcessingError('could not process image')
        returnValue(georef_file)

    @inlineCallbacks
    def get_web_image(self, form):
        web_image = os.path.join(self.save_dir, '%s.png' % form.get_hash())
        
        if os.path.exists(web_image):
            returnValue(web_image)
            
        georeferenced_image = yield self.get_georeferenced_image(form)
        tmp_tif = tempfile.NamedTemporaryFile()
        
        args = 'gdalwarp -of GTiff -t_srs EPSG:3857 -dstalpha'.split(' ')
        args += [georeferenced_image, tmp_tif.name]
        d = defer.Deferred()
        yield reactor.spawnProcess(ProcessProtocolDeferred(d), "gdalwarp", args, {})
        yield d
        
        args = 'gdal_translate -of PNG'.split(' ')
        args += [tmp_tif.name, web_image]
        d = defer.Deferred()
        yield reactor.spawnProcess(ProcessProtocolDeferred(d), "gdal_translate", args, {})
        yield d
        
        if not os.path.exists(web_image):
            raise ImageProcessingError('could not process image')
        returnValue(web_image)
        