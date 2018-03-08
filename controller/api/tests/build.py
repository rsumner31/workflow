"""
Unit tests for the Deis api app.

Run the tests with "./manage.py test api"
"""

from __future__ import unicode_literals

import json
import uuid

from django.test import TestCase

# pylint: disable=R0904


class BuildTest(TestCase):

    """Tests build notification from build system"""

    fixtures = ['tests.json']

    def setUp(self):
        self.assertTrue(
            self.client.login(username='autotest', password='password'))
        url = '/api/providers'
        creds = {'secret_key': 'x'*64, 'access_key': 1*20}
        body = {'id': 'autotest', 'type': 'mock', 'creds': json.dumps(creds)}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        url = '/api/flavors'
        body = {'id': 'autotest', 'provider': 'autotest', 'ssh_username': 'ubuntu',
                'params': json.dumps({'region': 'us-west-2', 'instance_size': 'm1.medium'})}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    def test_build(self):
        """
        Test that a null build is created on a new formation, and that users
        can post new builds to a formation
        """
        url = '/api/formations'
        body = {'id': 'autotest', 'flavor': 'autotest', 'image': 'deis/autotest'}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        formation_id = response.data['id']
        # check to see that an initial/null build was created
        url = '/api/formations/{formation_id}/build'.format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['version'], 1)
        # post a new build
        body = {'sha': uuid.uuid4().hex, 'slug_size': 4096000, 'procfile': json.dumps({'web': 'node server.js'}),
                'url': 'http://deis.local/slugs/1c52739bbf3a44d3bfb9a58f7bbdd5fb.tar.gz',
                'checksum': uuid.uuid4().hex}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        build1 = response.data
        self.assertEqual(response.data['url'], body['url'])
        # read the build
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        build2 = response.data
        self.assertEqual(build1, build2)
        # post a new build
        body = {'sha': uuid.uuid4().hex, 'slug_size': 4096000, 'procfile': json.dumps({'web': 'node server.js'}),
                'url': 'http://deis.local/slugs/1c52739bbf3a44d3bfb9a58f7bbdd5fb.tar.gz',
                'checksum': uuid.uuid4().hex}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        build3 = response.data
        self.assertEqual(response.data['url'], body['url'])
        self.assertNotEqual(build2['uuid'], build3['uuid'])
        # disallow put/patch/delete
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.patch(url).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)

