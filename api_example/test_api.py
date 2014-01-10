import json
import urlparse
import requests
import dateutil

API_KEY = '9bda8ec7-aa43-4b08-a852-b2dc4e6d3e71'

def get_package_list():
    res = requests.post(
        'http://10.48.1.40:5000/api/action/package_list', json.dumps({}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to get package list, status_code (%s), error %s' % (res.status_code, res.content)
        return ()

def get_package_info(package_name):
    res = requests.post(
        'http://10.48.1.40:5000/api/action/package_show', json.dumps({'id': package_name}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        return json.loads(res.content)['result']
    else:
        print 'ckan failed to show package information, status_code (%s), error %s' % (res.status_code, res.content)
        return {}

def get_metadata_properties(package_id):
    res = requests.post(
        'http://10.48.1.40:5000/api/2/get/get_metadata_properties', json.dumps({'package_id': package_id}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        result = json.loads(res.content)
        if len(result) > 0:
            return result['result']
        else:
            return None
    else:
        print 'ckan failed to get metadata timestamp, status_code (%s), error %s' % (res.status_code, res.content)
        return None

def get_metadata_timestamp(package_id):
    res = requests.post(
        'http://10.48.1.40:5000/api/2/get/get_metadata_timestamp', json.dumps({'package_id': package_id}),
        headers = {'Authorization': API_KEY,
                   'Content-Type': 'application/json'}
    )

    if res.status_code == 200:
        result = json.loads(res.content)
        if len(result) > 0:
            return result['result']['timestamp']
        else:
            return None
    else:
        print 'ckan failed to get metadata timestamp, status_code (%s), error %s' % (res.status_code, res.content)
        return None

print 'Package list'
print get_package_list()

print ''
print ''
print ''

package_info = get_package_info('prueba')
print "Package 'prueba' information"
print package_info

print ''
print ''
print ''

print "Package 'prueba' properties"
print get_metadata_properties(package_info['id'])

print ''
print ''
print ''

print "Package 'prueba' timestamp"
print get_metadata_timestamp(package_info['id'])