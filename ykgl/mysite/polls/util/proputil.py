
# -*- coding:utf-8 -*-

try:
    import configparser
except:
    from six.moves import configparser 
import os

def getIniConfig(filename,sec,prop):
    #os.chdir('C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\')

    cf = configparser.ConfigParser()

    #cf.read('domain_server.ini')
    cf.read(filename)

    secs = cf.sections()
    #print ('sections : ', secs, type(secs))

    value = cf.get(sec,prop)
    #print ('sec %s prop %s value %s' % (sec,prop,value))
    return value
    #domain_server_ip = cf.get('domain_server_config','ip')
    #domain_server_port = cf.get('domain_server_config','port')

    #domain_server_admin_user = cf.get('domain_server_config','admin_user')
    #domain_server_admin_password = cf.get('domain_server_config','admin_password')

    #print ('ip : %s' % domain_server_ip)
    #print ('port : %s' % domain_server_port )
    #print ('user : %s' % domain_server_admin_user)
    #print ('password : %s' % domain_server_admin_in_password)
