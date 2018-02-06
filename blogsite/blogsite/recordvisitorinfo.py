from blogsite import postgresql

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
    postgresql.Connpsql().writedata('visitorinfo', {'host': ipinfo, 'full_request': str(fullrequest), 'remote_addr': remoteaddr, 'proxy_remote_ip': proxyremoteip, 'user_agent': useragent})
