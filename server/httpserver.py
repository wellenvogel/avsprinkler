import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import cgi
import json
import logging
import os
import posixpath
import traceback
import urllib
import urlparse

import Constants


class HTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

  def __init__(self, RequestHandlerClass,controller):
    self.basedir =os.path.join(os.path.dirname(os.path.relpath(__file__)),"gui")
    self.overwrite_map = ({
      '.png': 'image/png',
      '.js': 'text/javascript; charset=utf-8'
    })
    self.controller=controller
    BaseHTTPServer.HTTPServer.__init__(self, ("0.0.0.0",8080), RequestHandlerClass, True)
    self.serve_forever()

  def getUrlPath(self, path):
    '''
    get an url path that can be used to obtain a file given

    :param path:
    :return: None if no mapping is possible
    '''
    fp = os.path.realpath(path)
    return fp



class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  CONTROLURL="/control"
  def __init__(self, request, client_address, server):
    self.logger=logging.getLogger(Constants.LOGNAME)
    # allow write buffering
    # see https://lautaportti.wordpress.com/2011/04/01/basehttprequesthandler-wastes-tcp-packets/
    self.wbufsize = -1
    self.id = None
    self.logger.debug("receiver thread started", client_address)
    SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

  def do_POST(self):
    maxlen = 5000000
    (path, sep, query) = self.path.partition('?')
    if not path.startswith(self.CONTROLURL):
      self.send_error(404, "unsupported post url")
      return
    try:
      ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
      if ctype == 'multipart/form-data':
        postvars = cgi.parse_multipart(self.rfile, pdict)
      elif ctype == 'application/x-www-form-urlencoded':
        length = int(self.headers.getheader('content-length'))
        if length > maxlen:
          raise Exception("too much data" + unicode(length))
        postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
      elif ctype == 'application/json':
        length = int(self.headers.getheader('content-length'))
        if length > maxlen:
          raise Exception("too much data" + unicode(length))
        postvars = {'_json': self.rfile.read(length)}
      else:
        postvars = {}
      requestParam = urlparse.parse_qs(query, True)
      requestParam.update(postvars)
      self.handleControlRequest(path, requestParam)
    except Exception as e:
      txt = traceback.format_exc()
      self.logger.debug("unable to process request for ", path, query, txt)
      self.send_response(500, txt)
      self.end_headers()
      return

  # overwrite this from SimpleHTTPRequestHandler
  def send_head(self):
    path = self.translate_path(self.path)
    if path is None:
      return
    """Common code for GET and HEAD commands.

    This sends the response code and MIME headers.

    Return value is either a file object (which has to be copied
    to the outputfile by the caller unless the command was HEAD,
    and must be closed by the caller under all circumstances), or
    None, in which case the caller has nothing further to do.

    """

    f = None
    if os.path.isdir(path):
      if not self.path.endswith('/'):
        # redirect browser - doing basically what apache does
        self.send_response(301)
        self.send_header("Location", self.path + "/")
        self.end_headers()
        return None
      for index in "index.html", "index.htm":
        index = os.path.join(path, index)
        if os.path.exists(index):
          path = index
          break
      else:
        return self.list_directory(path)
    base, ext = posixpath.splitext(path)
    if ext in self.server.overwrite_map:
      ctype = self.server.overwrite_map[ext]
    else:
      ctype = self.guess_type(path)
    try:
      # Always read in binary mode. Opening files in text mode may cause
      # newline translations, making the actual size of the content
      # transmitted *less* than the content-length!
      f = open(path, 'rb')
    except IOError:
      self.send_error(404, "File not found")
      return None
    self.send_response(200)
    self.send_header("Content-type", ctype)
    fs = os.fstat(f.fileno())
    self.send_header("Content-Length", str(fs[6]))
    if path.endswith(".js") or path.endswith(".less"):
      self.send_header("cache-control", "private, max-age=0, no-cache")
    self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
    self.end_headers()
    return f

  # overwrite this from SimpleHTTPRequestHandler
  def translate_path(self, path):
    """Translate a /-separated PATH to the local filename syntax.

    Components that mean special things to the local file system
    (e.g. drive or directory names) are ignored.  (XXX They should
    probably be diagnosed.)

    """
    # abandon query parameters
    (path, sep, query) = path.partition('?')
    path = path.split('#', 1)[0]
    path = posixpath.normpath(urllib.unquote(path).decode('utf-8'))
    if path.startswith(self.CONTROLURL):
      requestParam = urlparse.parse_qs(query, True)
      self.handleControlRequest(path, requestParam)
      return None
    if path == "" or path == "/":
      path = "/index.html"
      self.send_response(301)
      self.send_header("Location", path)
      self.end_headers()
      return None
    words = path.split('/')
    words = filter(None, words)
    path = ""
    for word in words:
      drive, word = os.path.splitdrive(word)
      head, word = os.path.split(word)
      if word in (".", ".."): continue
      path = os.path.join(path, word)
    self.logger.debug("request path/query", path, query)
    # pathmappings expect to have absolute pathes!
    return os.path.join(self.server.basedir, path)



  # send a json encoded response
  def sendJsonResponse(self, rtj, requestParam):
    if not rtj is None:
      self.send_response(200)
      if not requestParam.get('callback') is None:
        rtj = "%s(%s);" % (requestParam.get('callback'), rtj)
        self.send_header("Content-type", "text/javascript")
      else:
        self.send_header("Content-type", "application/json")
      self.send_header("Content-Length", str(len(rtj)))
      self.send_header("Last-Modified", self.date_time_string())
      self.end_headers()
      self.wfile.write(rtj)
      self.logger.debug("nav response", rtj)
    else:
      raise Exception("empty response")


  def handleControlRequest(self, path, requestParam):
    '''
    control requests
    :param path:
    :param requestParam:
    :return:
    '''
    try:
      rtj=self.server.controller.handleRequest(requestParam)
      self.sendJsonResponse(json.dumps(rtj), requestParam)
    except Exception as e:
      text = e.message + "\n" + traceback.format_exc()
      self.logger.debug("unable to process request for controlrequest ", text)
      self.sendJsonResponse(json.dumps({
        "status":"ERROR",
        "info":text
      }),requestParam)
      return

