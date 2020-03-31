#!/usr/bin/env python
# coding: utf-8
# Some code taken from https://gist.github.com/TheWaWaR/bd26ef76dabca2d410dd
import os
import sys
import json
import uuid
import tempfile
import argparse
from flask import Flask, request, Response, jsonify, g
from flask_selfdoc import Autodoc

app = Flask(__name__)
auto = Autodoc(app)
app.debug = False


def save_request(uuid, request):
  req_data = {}
  req_data['uuid'] = uuid
  req_data['endpoint'] = request.endpoint
  req_data['method'] = request.method
  req_data['cookies'] = request.cookies
  req_data['data'] = str(request.data,'utf-8')
  req_data['headers'] = dict(request.headers)
  req_data['headers'].pop('Cookie', None)
  req_data['args'] = request.args
  req_data['form'] = request.form
  req_data['remote_addr'] = request.remote_addr
  if request.files:
    files = []
    for name, fs in request.files.iteritems():
      dst = tempfile.NamedTemporaryFile()
      fs.save(dst)
      dst.flush()
      filesize = os.stat(dst.name).st_size
      dst.close()
      files.append({'name': name, 'filename': fs.filename, 'filesize': filesize,
       'mimetype': fs.mimetype, 'mimetype_params': fs.mimetype_params})
    req_data['files'] = files
  return req_data

@app.after_request
def after_request(resp):
  resp.headers.add('Access-Control-Allow-Origin', '*')
  resp.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Token')
  resp.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
  return resp

# Return documentation
@app.route('/', defaults={'u_path': ''})
@app.route('/<path:u_path>')
def default(u_path):
  return auto.html()

# Return client IP
@auto.doc()
@app.route('/ip', methods=['GET'])
def ip():
  """
  Returns the requester IP
  """
  g.uuid = uuid.uuid1().hex
  try:
    headers_list = request.headers.getlist("X-Forwarded-For")
    user_ip = headers_list[0] if headers_list else request.remote_addr
    return jsonify({'ip': user_ip}), 200
  except:
    return "IP not available", 501

# Return data about the request
@app.route('/log', methods=['GET', 'POST'])
@auto.doc()
def log():
  """
  Log and print the HTTP request
  """
  g.uuid = uuid.uuid1().hex
  req_data = save_request(g.uuid, request)
  resp = Response(json.dumps(req_data, indent=4), mimetype='application/json')
  resp.set_cookie('cookie-name', value='cookie-value')
  return resp

# Return current hostname
@app.route('/name', methods=['GET'])
@auto.doc()
def myname():
  """
  Hostname of current server
  """
  g.uuid = uuid.uuid1().hex
  try:
    return os.environ.get('NAME','Name not set')
  except:
    return "Name not available", 501
  
# Document doh-proxy
@app.route('/dns-query', methods=['GET'])
@auto.doc()
def dnsquery():
  """
  Dns over HTTP: example: /dns-query?name=cnn.com
  """
  g.uuid = uuid.uuid1().hex
  return "Documentation", 200
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Process cli options')
  parser.add_argument('-l', '--listen', type=str, default='0.0.0.0',
                      help='IP to listen on')
  parser.add_argument('-p', '--port', type=int, default=80,
                      help='port to listen on')
  parser.add_argument('-d', '--debug', type=bool, default=False,
                      help='Set Debug on/off')
  args = parser.parse_args()
  app.run(host=args.listen, port=args.port, debug=args.debug)
