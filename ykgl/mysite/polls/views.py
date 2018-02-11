# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .util.proputil import getIniConfig
from .util.ldapLogon import Ldap
import ldap

# Create your views here.

from django.http import HttpResponse



def index(request):
    return render(request,'index.html')

def login(request):
    return render(request,'login.html')
    
def login_verify(request):
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    admin_user = getIniConfig(config_file,'sys_config','user')
    admin_pass = getIniConfig(config_file,'sys_config','password')
    #print ('admin user : %s' % admin_user)
    #print ('admin pass : %s' % admin_pass)
   
    useri = request.GET['useri']
    passwordi = request.GET['passwordi']
    #print ('input user : %s' % useri)
    #print ('input pass : %s' % passwordi)   
    #print(admin_user==useri)
    if(admin_user==useri and admin_pass==passwordi):
        return HttpResponse('ok')
    else:
        return HttpResponse('notok')
    
def home(request):
	
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    l = Ldap(uri, port, admin_user , admin_password)
    #print ('domain : %s' % base)
    users = l.ldap_search(base,'*','sAMAccountName')    
    #users = l.ldap_search(base,'FALSE','isCriticalSystemObject')    
    users = users[1]
    
    #users = users[0:len(users)-3]
    user_array = []
    user_names = []
    user_members = []
    user_admin_if = []
    i = 0
    #print (len(users))
    while i < len(users):     
        if(str(users[i][0])!='None') :
            if 'memberOf' in users[i][1] :
              memberof = users[i][1]['memberOf']
              memberof0 = str(memberof[0],encoding='UTF-8')
              memberofL = str(memberof[len(memberof)-1],encoding='UTF-8')
              #print(users[i][1]['name'][0])
              print( '%s , %s' % (memberof0,memberofL) )           
              if memberof0.startswith('CN=Domain Admins,CN=Users') :
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(True)            
            else:
              name = str(users[i][1]['name'][0],encoding='UTF-8')
              if 'isCriticalSystemObject' in users[i][1]:
                is_critical = str(users[i][1]['isCriticalSystemObject'][0],encoding='UTF-8')
                if is_critical == 'FALSE' and not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Computer')) and not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Group')): 
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(False)
              else:
                if not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Group')):
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(False)
        i = i+1
    #users = users[1]
    #users = users.value()
    
    return render(request,'home.html',{'users':user_names})
 

def auth(request):
    user = request.GET['user']
    print ('收到请求授权用户[%s]为管理员' % user)
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')

    try:
        uri = 'ldap://%s:%s' % (ip,port)
        #print ('uri : %s' % uri)
        admin_user = admin_user+'@'+domain_name
        #print('admin user : %s' % admin_user)
        l = Ldap(uri, port, admin_user , admin_password)
        
        #在域管理员中添加成员
        dn = 'CN=Domain Admins,CN=Users,DC=corp,DC=607,DC=com'
        u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
        attr_list=[( ldap.MOD_ADD, 'member', bytes(u, encoding='UTF-8' )  )]     
       # attr_list=[( ldap.MOD_REPLACE, 'memberOf', bytes('CN=Domain Admins,CN=Users,DC=corp,DC=607,DC=com , CN=Domain Admins,CN=Users,DC=corp,DC=607,DC=com', encoding='UTF-8' )  )]    
        l.modify_user(dn,attr_list)
        dn = 'CN=Administrators,CN=Builtin,DC=corp,DC=607,DC=com'
        l.modify_user(dn,attr_list)
    except (ldap.LDAPError):
        return HttpResponse('notok')
    return HttpResponse('ok')

def cancel(request):
    user = request.GET['user']
    print ('收到请求取消用户[%s]的管理员权限' % user)
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    try:
        l = Ldap(uri, port, admin_user , admin_password)
        
        #在域管理员中删除成员
        dn = 'CN=Domain Admins,CN=Users,DC=corp,DC=607,DC=com'
        u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
        attr_list=[( ldap.MOD_DELETE, 'member', bytes(u, encoding='UTF-8' )  )]
        l.modify_user(dn,attr_list)
        dn = 'CN=Administrators,CN=Builtin,DC=corp,DC=607,DC=com'
        l.modify_user(dn,attr_list)
    except (ldap.LDAPError):
        return HttpResponse('notok')
    return HttpResponse('ok')




def user(request):	
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    l = Ldap(uri, port, admin_user , admin_password)
    #print ('domain : %s' % base)
    users = l.ldap_search(base,'*','sAMAccountName')    
    #users = l.ldap_search(base,'FALSE','isCriticalSystemObject')    
    users = users[1]

    #f = open('users.txt','w+')
    #f.write(str(users))
    #f.close()
    
    #users = users[0:len(users)-3]
    user_array = []
    user_names = []
    user_members = []
    user_admin_if = []
    i = 0
    #print (len(users))
    while i < len(users):     
        if(str(users[i][0])!='None') :
            if 'memberOf' in users[i][1] :
              memberof = users[i][1]['memberOf']
              memberof0 = str(memberof[0],encoding='UTF-8')
              memberofL = str(memberof[len(memberof)-1],encoding='UTF-8')
              #print(users[i][1]['name'][0])
              #print( '%s , %s' % (memberof0,memberofL) )           
              if memberof0.startswith('CN=Domain Admins,CN=Users') :
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(True)            
            else:
              name = str(users[i][1]['name'][0],encoding='UTF-8')
              if 'isCriticalSystemObject' in users[i][1]:
                is_critical = str(users[i][1]['isCriticalSystemObject'][0],encoding='UTF-8')
                if is_critical == 'FALSE' and not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Computer')) and not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Group')): 
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(False)
              else:
                if not ( str(users[i][1]['objectCategory'][0],encoding='UTF-8').startswith('CN=Group')):
                  user_array.append(users[i][1]['sAMAccountName'])
                  user_names.append(str(users[i][1]['name'][0],encoding='UTF-8'))
                  user_admin_if.append(False)
        i = i+1
    #users = users[1]
    #users = users.value()
    
    return render(request,'user.html',{'users':user_names})

def create(request):

    user = request.GET['useri']
    password = request.GET['passwordi']
    u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
    fn = request.GET['first_name']
    ln = request.GET['last_name']
    print ('收到请求添加用户[%s]' % user)

    if not fn:
        fn = user
    if not ln:
        ln = user
    try:
        #get config
        config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
        domain_name = getIniConfig(config_file,'domain_server_config','name')
        ip = getIniConfig(config_file,'domain_server_config','ip')
        port = getIniConfig(config_file,'domain_server_config','port')
        base = getIniConfig(config_file,'domain_server_config','base')		
        admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
        admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


        uri = 'ldap://%s:%s' % (ip,port)
        #print ('uri : %s' % uri)
        admin_user = admin_user+'@'+domain_name
        #print('admin user : %s' % admin_user)
        l = Ldap(uri, port, admin_user , admin_password)
       
        user_dn = user+'@'+domain_name
        #create user here
        result = l.add_user(u,user_dn,password,fn,ln)
    except (ldap.LDAPError):
        return HttpResponse('notok')


    try:
        uri = 'ldaps://%s:%s' % (ip,636)
        #print ('uri : %s' % uri)
        admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
        #print('admin user : %s' % admin_user)
           
        #ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,ldap.OPT_X_TLS_NEVER)
        conn = ldap.initialize(uri)
        conn.set_option(ldap.OPT_PROTOCOL_VERSION,3)
        conn.set_option(ldap.OPT_NETWORK_TIMEOUT,10.0)
        conn.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        conn.set_option(ldap.OPT_X_TLS_DEMAND,True)
        conn.set_option(ldap.OPT_DEBUG_LEVEL,255)
        admin_u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % admin_user    
        conn.simple_bind_s(admin_u, admin_password)
        
        pass_uni = '\"'+password+'\"'    
        pass_uni = pass_uni.encode("utf-16-le")
        #print (pass_uni)
        
        attr_list=[( ldap.MOD_REPLACE, 'unicodePwd', [pass_uni] ),
                   ( ldap.MOD_REPLACE, 'unicodePwd', [pass_uni] ),
                   ( ldap.MOD_REPLACE, 'userAccountControl', bytes('66048', encoding='UTF-8')  )]
        conn.modify_s(u, attr_list)
    except (ldap.LDAPError):
        conn.delete_s(u)
        return HttpResponse('notok')
    
    if(result[0]):
        return HttpResponse('ok')
    else:
        return HttpResponse('notok')


def delete(request):

    user = request.GET['useri']
    u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
    print ('收到请求删除用户[%s]' % user)
    
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    l = Ldap(uri, port, admin_user , admin_password)
   
    
    
    #delete user here
    result = l.delete_user(u)
    
    if(result[0]):
        return HttpResponse('ok')
    else:
        return HttpResponse('notok')


def forbidden(request):

    user = request.GET['useri']
    u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
    print ('收到请求禁用用户[%s]' % user)
    
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    l = Ldap(uri, port, admin_user , admin_password)

    #forbidden user here
    #'userAccountControl': [b'66050']    
    attr_list=[( ldap.MOD_REPLACE, 'userAccountControl', bytes('66050', encoding='UTF-8' )  )]
    result = l.modify_user(u,attr_list)
    
    
    
    if(result[0]):
        return HttpResponse('ok')
    else:
        return HttpResponse('notok')
    
def active_user(request):

    user = request.GET['useri']
    u = 'CN=%s, CN=Users,DC=corp,DC=607,DC=com' % user
    print ('收到请求启用用户[%s]' % user)
    
    #get config
    config_file = 'C:\\Users\\Administrator\\Desktop\\install\\ldap-admin\\mysite\\polls\\util\\domain_server.ini'
    domain_name = getIniConfig(config_file,'domain_server_config','name')
    ip = getIniConfig(config_file,'domain_server_config','ip')
    port = getIniConfig(config_file,'domain_server_config','port')
    base = getIniConfig(config_file,'domain_server_config','base')		
    admin_user = getIniConfig(config_file,'domain_server_config','admin_user')
    admin_password = getIniConfig(config_file,'domain_server_config','admin_password')


    uri = 'ldap://%s:%s' % (ip,port)
    #print ('uri : %s' % uri)
    admin_user = admin_user+'@'+domain_name
    #print('admin user : %s' % admin_user)
    l = Ldap(uri, port, admin_user , admin_password)

    #forbidden user here
    #'userAccountControl': [b'66050']    
    #attr_list=[( ldap.MOD_REPLACE, 'userAccountControl', bytes('66048', encoding='UTF-8' )  )]
    attr_list=[ ( ldap.MOD_REPLACE, 'userAccountControl', bytes('66048', encoding='UTF-8')  ) ]
    result = l.modify_user(u,attr_list)
    
    
    
    if(result[0]):
        return HttpResponse('ok')
    else:
        return HttpResponse('notok')

