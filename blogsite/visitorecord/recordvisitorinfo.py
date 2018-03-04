import time
import chardet
from visitorecord.models import VisitorInfo

'''
{SERVER_ADMIN: webmaster@localhost,
 HTTP_ACCEPT_ENCODING: gzip,
 deflate,
 SERVER_NAME: copycat.imwork.net, mod_wsgi.version: (4, 3, 0),
 wsgi.errors: <_io.TextIOWrapper encoding=utf-8>,
 mod_wsgi.script_start: 1517895430298260,
 SERVER_SIGNATURE: <address>Apache/2.4.18 (Ubuntu) Server at copycat.imwork.net Port 80</address>\\n,
 mod_wsgi.listener_host: ,
 CONTEXT_DOCUMENT_ROOT: /var/www/blogsite,
 REMOTE_ADDR: 192.168.1.107,
 mod_wsgi.script_reloading: 1,
 HTTP_X_REAL_IP: 113.104.197.94,
 mod_wsgi.listener_port: 80,
 mod_wsgi.application_group: 127.0.1.1|,
 wsgi.url_scheme: http,
 mod_wsgi.process_group: ,
 QUERY_STRING: ,
 CONTEXT_PREFIX: ,
 SERVER_PORT: 80,
 GATEWAY_INTERFACE: CGI/1.1,
 mod_wsgi.request_start: 1517895430269346,
 HTTP_HOST: copycat.imwork.net,
 mod_wsgi.input_chunked: 0,
 mod_wsgi.request_handler: wsgi-script,
 HTTP_DNT: 1,
 REQUEST_SCHEME: http,
 apache.version: (2, 4, 18),
 wsgi.multiprocess: True,
 mod_wsgi.enable_sendfile: 0,
 HTTP_ACCEPT_LANGUAGE: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,
 DOCUMENT_ROOT: /var/www/blogsite,
 wsgi.version: (1, 0),
 SCRIPT_FILENAME: /var/www/blogsite/blogsite/wsgi.py,
 HTTP_CONNECTION: keep-alive,
 wsgi.file_wrapper: <class mod_wsgi.FileWrapper>,
 REQUEST_URI: /classify/general/,
 wsgi.input: <mod_wsgi.Input object at 0x7f8cf2a99130>,
 HTTP_ACCEPT: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,
 HTTP_X_FORWARDED_FOR: 113.104.197.94, 103.44.145.245,
 REMOTE_PORT: 47446,
 mod_wsgi.callable_object: application,
 SERVER_PROTOCOL: HTTP/1.1,
 REQUEST_METHOD: GET,
 HTTP_USER_AGENT: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36,
 SCRIPT_NAME: ,
 SERVER_SOFTWARE: Apache/2.4.18 (Ubuntu),
 HTTP_REFERER: http://copycat.imwork.net/,
 mod_wsgi.handler_script: ,
 HTTP_PROXYAGENT: oray phfw 22057,
 PATH_INFO: /classify/general/,
 SERVER_ADDR: 192.168.1.107,
 HTTP_UPGRADE_INSECURE_REQUESTS: 1,
 wsgi.run_once: False,
 wsgi.multithread: True,
 PATH_TRANSLATED: /var/www/blogsite/blogsite/wsgi.py/classify/general/}
 '''

def recordinfo(httprequestinstance):
    try:
        ipinfo = httprequestinstance.get_host().replace(':', '::')
    except:
        ipinfo = 'usingproxy'
    fullrequest = httprequestinstance.META
    try:
        remoteaddr = fullrequest['REMOTE_ADDR']
    except:
        remoteaddr = 'NotDetected'
    try:
        proxyremoteip = fullrequest['HTTP_X_REAL_IP']
    except:
        proxyremoteip = 'NotDetectedOrNotHave'
    try:
        useragent = fullrequest['HTTP_USER_AGENT']
    except:
        useragent = 'None'
    visitime = time.asctime()
    info = VisitorInfo(host = ipinfo, full_request = str(fullrequest), remote_addr = remoteaddr, proxy_remote_ip = proxyremoteip, user_agent = useragent, visitime = visitime)
    info.save()