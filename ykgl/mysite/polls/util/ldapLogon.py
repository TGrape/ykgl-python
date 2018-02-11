# -*- coding: utf-8 -*-
import ldap  
from rest_framework.exceptions import APIException, ValidationError  
  
  
class Ldap(object):  
    def __init__(self, server_uri, server_port=389, bind_name='', bind_passwd=''):  
        self.server_uri = server_uri  
        self.server_port = server_port  
        self.ldap_obj = None  
  
        self.ldap_connect(bind_name, bind_passwd)  
  
    def ldap_connect(self, bind_name='', bind_passwd=''):  
        """ 
        :param bind_name: 绑定的ldap用户，可为空; 添加，删除用户时 bind_name 要有root权限 
        :param bind_passwd: 
        :return: 
        """  
        url = self.server_uri
        print('url : %s' % url)
        
        conn = ldap.initialize(url)  
        # try:  
        #     conn.start_tls_s()  
        # except ldap.LDAPError as exc:  
        #     raise APIException(exc.message)  
        if bind_name and not bind_passwd:  
            raise APIException("请输入LDAP密码")  
        try:  
            rest = conn.simple_bind_s(bind_name, bind_passwd)  
        except ldap.SERVER_DOWN:  
            raise APIException("无法连接到LDAP")  
        except ldap.INVALID_CREDENTIALS:  
            raise APIException("LDAP账号错误")  
        except (Exception) as ex:  
            raise APIException(type(ex))  
        if rest[0] != 97:  # 97 表示success  
            raise APIException(rest[1])  
        self.ldap_obj = conn  
  
    def ldap_search(self, base='', keyword=None, rdn='cn'):  
        """ 
        base: 域 ou=test, dc=test, dc=com 
        keyword: 搜索的用户 
        rdn: cn/uid 
        """  
        scope = ldap.SCOPE_SUBTREE  
        filter = "%s=%s" % (rdn, keyword)  
        retrieve_attributes = None  
        try:  
            result_id = self.ldap_obj.search(base, scope, filter, retrieve_attributes)  
            result_type, result_data = self.ldap_obj.result(result_id)  
            if not result_data:  
                return False, []  
        except (ldap.LDAPError) as error_message:  
            raise APIException(error_message)  
        return True, result_data  
  
    def add_user(self, base_dn,user_dn, password,fn='',ln=''):  
        """ 
        base_dn: cn=test, ou=magicstack,dc=test,dc=com  NOT NONE 
        """  
        if not base_dn:  
            raise ValidationError(u"DN不能为空")  
        dn_list = base_dn.split(',')  
        user_info = dict()

        
        i = 0
        for item in dn_list:  
            attr, value = item.split('=')  
            if not value:  
                raise ValidationError(u"DN输入错误:属性的值为空")  
            user_info[attr] = value
           
        #b'top', b'person', b'organizationalPerson', b'user'  'userPrincipalName': [b'liuyuding9@corp.607.com'], 'lockoutTime': [b'0']
        #bytes(u, encoding='UTF-8' )
        add_record = [('objectClass', [bytes('top', encoding='UTF-8' ),bytes('person', encoding='UTF-8' ), bytes('organizationalPerson', encoding='UTF-8' ),bytes('user', encoding='UTF-8' )]),  
                      ('cn', [bytes('%s' % user_info.get("CN"), encoding='UTF-8' )]),  
                      ('sn', [bytes(fn, encoding='UTF-8' )]),
                      ('givenName', [bytes(ln, encoding='UTF-8' )]),
                      #('userPassword', [bytes('%s' % password, encoding='UTF-8' )]),
                      ('userAccountControl', [bytes('66050', encoding='UTF-8' )]),
                      ('sAMAccountName', [bytes('%s' % user_info.get("CN"), encoding='UTF-8' )]),
                      ('lockoutTime', [bytes('0', encoding='UTF-8' )]),
                      ('userPrincipalName', [bytes(user_dn, encoding='UTF-8' )]),
                      ('displayName', [bytes(user_info.get("CN"), encoding='UTF-8' )])]  
        try:  
            result = self.ldap_obj.add_s(base_dn, add_record)
            
        except (ldap.LDAPError) as error_message:  
            raise APIException(error_message)
        
          
        if result[0] == 105:  
            return True, []  
        else:  
            return False, result[1]  
  
    def modify_user(self, dn, attr_list):  
        """ 
        MOD_ADD: 如果属性存在，这个属性可以有多个值，那么新值加进去，旧值保留 
        MOD_DELETE ：如果属性的值存在，值将被删除 
        MOD_REPLACE ：这个属性所有的旧值将会被删除，这个值被加进去 
 
        dn: cn=test, ou=magicstack,dc=test, dc=com 
        attr_list: [( ldap.MOD_REPLACE, 'givenName', 'Francis' ), 
                    ( ldap.MOD_ADD, 'cn', 'Frank Bacon' ) 
                   ] 
        """  
        try:  
            result = self.ldap_obj.modify_s(dn, attr_list)  
        except (ldap.LDAPError) as error_message:  
            raise APIException(error_message)  
        else:  
            if result[0] == 103:  
                return True, []  
            else:  
                return False, result[1]  
  
    def delete_user(self, dn):  
        """ 
        dn: cn=test, ou=magicstack,dc=test, dc=com 
        """  
        try:  
            result = self.ldap_obj.delete_s(dn)  
        except (ldap.LDAPError) as error_message:  
            raise APIException(error_message)  
        else:  
            if result[0] == 107:  
                return True, []  
            else:  
                return False, result[1]  
