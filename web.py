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
from flask_restx import Resource, Api, reqparse, fields
from werkzeug.middleware.proxy_fix import ProxyFix
import whois as whois_query
import pydig
import requests

app = Flask(__name__)
api = Api(app)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.debug = False

doh_host=os.environ.get('DOHHOST',"127.0.0.1")
doh_port=os.environ.get('DOHPORT',"8053")
doh_scheme=os.environ.get('DOHSCHEME',"http")

api_parser = reqparse.RequestParser()
api_parser.add_argument('host', type=str, help='DNS over http host', default=doh_host)
api_parser.add_argument('port', type=str, help='DNS over http port', default=doh_port)
api_parser.add_argument('scheme', type=str, help='DNS over http scheme', choices=['http', 'https'], default=doh_scheme)

api_dig_parser = reqparse.RequestParser()
api_dig_parser.add_argument('type', type=str, help='Type of Record to Query', 
                            choices=['A','AAAA','CNAME','MX','NS','PTR','TXT','DNSKEY','DS','CDNSKEY','CDS','SOA'], default="A")

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
  resp.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, HEAD')
  return resp

# Return client IP
@api.route('/ip')
class ip(Resource):
  """
  Returns the requester IP
  """
  def get(self):
    g.uuid = uuid.uuid1().hex
    try:
      headers_list = request.headers.getlist("X-Forwarded-For")
      user_ip = headers_list[0] if headers_list else request.remote_addr
      return {'ip': user_ip}
    except:
      return "IP not available", 501

# Return data about the request
@api.route('/log')
class log(Resource):
  
  def return_data(self):
    """
    Log and print the HTTP request for POST
    """
    g.uuid = uuid.uuid1().hex
    req_data = save_request(g.uuid, request)
    self.resp = Response(json.dumps(req_data, indent=4), mimetype='application/json')
    self.resp.set_cookie('cookie-name', value='cookie-value')
    return(self.resp)
    
  def get(self):
    """
    Log and print the HTTP request for GET
    """
    return self.return_data()
  def post(self):
    """
    Log and print the HTTP request for POST
    """
    return self.return_data()
  def put(self):
    """
    Log and print the HTTP request for PUT
    """
    return self.return_data()
  def delete(self):
    """
    Log and print the HTTP request for DELETE
    """
    return self.return_data()
  def patch(self):
    """
    Log and print the HTTP request for PATCH
    """
    return self.return_data()
  
  
# Return current hostname
@api.route('/name', methods=['GET'])
class myname(Resource):
  def get(self):
    """
    Hostname of current server
    """
    try:
      return os.environ.get('NAME','Name not set')
    except:
      return "Name not available", 501
  
# DNS over HTTP 
@api.route('/dnsq/<string:name>')
class dnsq(Resource):
  @api.expect(api_parser)
  def get(self,name):
    
    """
    Dns over HTTP
    """
    api_args = api_parser.parse_args()
    scheme = api_args.get('scheme', doh_scheme ) 
    host = api_args.get('host', doh_host)
    port = api_args.get('port', doh_port)
    name = name
    url = "{}://{}:{}/dns-query?name={}".format( scheme.lower(), host.lower(), port, name.lower() )
    print(url)
    try: 
      r = requests.get(url)
      return Response(json.dumps(r.json(), indent=4), mimetype='application/json')
    except: 
      return "Cannot contact Dns over HTTP server", 501                                                                        

  
# Whois endpoint
@api.route('/whois/<string:whois_name>')
class whois(Resource,):
  def get(self, whois_name):
    try:
      domain = whois_query.query(whois_name)
      retval = { 'registrar': domain.registrar, 
                 'name_servers': list(domain.name_servers),
                 'status': domain.status,
                 'name': domain.name, 
               }
      retval['expiration_date'] = "" if domain.expiration_date is None else domain.expiration_date.strftime("%m/%d/%Y, %H:%M:%S") 
      retval['last_updated'] =  "" if domain.last_updated is None else domain.last_updated.strftime("%m/%d/%Y, %H:%M:%S")
      retval['creation_date'] =  "" if domain.creation_date is None else domain.creation_date.strftime("%m/%d/%Y, %H:%M:%S")
      return Response(json.dumps(retval, indent=4), mimetype='application/json')
    except:
      return "Whois not available", 501
    
    
# Dig endpoint
@api.route('/dig/<string:dig_name>')
class dig(Resource):
  answer={}
  @api.expect(api_dig_parser)
  def get(self, dig_name):
    """
    Returns the results of a dig
    """
    api_dig_args = api_dig_parser.parse_args()
    g.uuid = uuid.uuid1().hex
    try:
      answer['answer']=pydig.query(dig_name,api_dig_args.type)
      return  Response(json.dumps(answer, indent=4), mimetype='application/json')
    except:
      return "Dig not available", 501
    
    
if __name__ == '__main__':
  cli_parser = argparse.ArgumentParser(description='Process cli options')
  cli_parser.add_argument('-l', '--listen', type=str, default='0.0.0.0',
                      help='IP to listen on')
  cli_parser.add_argument('-p', '--port', type=int, default=5000,
                      help='port to listen on')
  cli_parser.add_argument('-d', '--debug', type=bool, default=False,
                      help='Set Debug on/off')                                                                         
  args = cli_parser.parse_args()
  app.run(host=args.listen, 
          port=args.port, 
          debug=args.debug
         )
