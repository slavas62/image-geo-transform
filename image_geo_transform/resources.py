import os
import json
import urlparse

from twisted.web import resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from .processing import ImageProcessing, ImageProcessingError
from .forms import Form

class MainResource(resource.Resource):
    isLeaf = True

    def __init__(self, save_dir, save_dir_url='/files/'):
        self.save_dir = save_dir
        self.save_dir_url = save_dir_url
        self.image_processing = ImageProcessing(self.save_dir)

    def error(self, data):
        data = {
            'success': False,
            'errors': data,
        }
        return data

    def success(self, data):
        data = {
            'success': True,
            'result': data,
        }
        return data

    def make_absolute_url(self, request, uri):
        netloc = request.getHeader('host')
        if not netloc:
            return uri
        scheme = 'https' if request.getHeader('X_FORWARDED_PROTO') == 'https' else 'http'
        url_parts = [scheme, netloc, uri, '', '', '']
        return urlparse.urlunparse(url_parts)

    def make_file_url(self, request, filepath):
        rel_path = os.path.relpath(filepath, self.save_dir)
        url = os.path.join(self.save_dir_url, rel_path)
        
        url_parts = urlparse.urlparse(url)
        if not url_parts.netloc:
            url = self.make_absolute_url(request, url)
        
        return url

    @inlineCallbacks
    def get_data(self, request):
        form = Form(request.args)
        if not form.validate():
            request.setResponseCode(400)
            returnValue(self.error(form.errors))
        try:
            georeferenced_image = yield self.image_processing.get_georeferenced_image(form)
            web_image = yield self.image_processing.get_web_image(form)
        except ImageProcessingError as e:
            returnValue(self.error(str(e.message)))
        except Exception as e:
            import traceback
            traceback.print_stack()
            request.setResponseCode(500)
            returnValue(self.error('internal server error'))
        result = {
            'georeferenced_image': self.make_file_url(request, georeferenced_image),
            'web_image': self.make_file_url(request, web_image),
        }
        returnValue(self.success(result))
        
    @inlineCallbacks
    def defer_POST(self, request):
        resp = yield self.get_data(request)
        request.setHeader("content-type", "application/json")
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.write(json.dumps(resp))
        request.finish()

    def render_POST(self, request):
        reactor.callLater(0, self.defer_POST, request)
        return NOT_DONE_YET
