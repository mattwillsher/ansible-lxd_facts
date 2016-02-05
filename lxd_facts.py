#!/usr/bin/python

import socket
import httplib
import json

socket.setdefaulttimeout(5)

class UnixStreamHTTPConnection(httplib.HTTPConnection):
    
    def __init__(self, path, host='localhost/rg_cli',port=None, strict=None,
                 timeout=None):
        httplib.HTTPConnection.__init__(self, host, port=port, strict=strict,
                                        timeout=timeout)
        self.path=path
    
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


class LxdMetadata(object):

    lxd_api_socket   = '/dev/lxd/sock'
    lxd_config_uri   = 'http://lxd/1.0/config'
    lxd_metadata_key = 'user.tag-data'

    def _fetch_sock(self, url):
        s = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        s.connect( self.lxd_api_socket )
        s.sendall( 'GET /1.0/config/' + self.lxd_metadata_key )
        data = s.recv(1024)
        s.close
        return data

    def _fetch(self, url):
        stream = UnixStreamHTTPConnection( self.lxd_api_socket )
        stream.request('GET', url )
        response = stream.getresponse()
        if response:
            data = response.read()
        else:
            data = None

        return json.loads( data )

    def _rename_keys(self, data):
        new_data={}
        for key, value in data.iteritems():
            new_data[self._prefix % key] = value
        return new_data


#    def _fetch(self, url):
#        filehandle = urllib.urlopen(self.lxd_api_socket)
#        data = urllib.geturl(lxd_config_uri)
#        (response, info) = fetch_url(self.module, url, force=True)
#        if response:
#            data = response.read()
#        else:
#            data = None
#        return data

    def __init__(self, module, lxd_api_socket=None, lxd_metadata_key=None):
        self.module           = module
        self.lxd_api_socket   =   lxd_api_socket or self.lxd_api_socket
        self.lxd_metadata_key = lxd_metadata_key or self.lxd_metadata_key
        self._data            = {}
        self._prefix          = 'tag_%s'

    def run(self):
        data = self._fetch( self.lxd_config_uri + '/' + self.lxd_metadata_key )
        return self._rename_keys( data )


def main():
    argument_spec = url_argument_spec()

    module = AnsibleModule(
        argument_spec = argument_spec,
        supports_check_mode = True,
    )
    
    lxd_facts = LxdMetadata(module).run()

    module.exit_json(**dict(changed=False,ansible_facts=lxd_facts))

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()

main()

