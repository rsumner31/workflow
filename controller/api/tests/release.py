"""
Unit tests for the Deis api app.

Run the tests with "./manage.py test api"
"""

from __future__ import unicode_literals

import json

from django.test import TestCase
import uuid


class ReleaseTest(TestCase):

    """Tests push notification from build system"""

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
    
    def test_release(self):
        """
        Test that a release is created when a formation is created, and
        that updating config, build, image, args or triggers a new release
        """
        url = '/api/formations'
        body = {'id': 'autotest', 'flavor': 'autotest', 'image': 'deis/autotest'}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        formation_id = response.data['id']
        # check to see that an initial release was created
        url = '/api/formations/{formation_id}/release'.format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        release1 = response.data
        self.assertIn('image', response.data)
        self.assertIn('config', response.data)
        self.assertIn('build', response.data)
        self.assertIn('args', response.data)
        self.assertIn('command', response.data)
        self.assertEquals(release1['version'], 1)
        # check that updating config rolls a new release
        url = '/api/formations/{formation_id}/config'.format(**locals())
        body = {'values': json.dumps({'NEW_URL1': 'http://localhost:8080/'})}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('NEW_URL1', json.loads(response.data['values']))
        # check to see that a new release was created
        url = '/api/formations/{formation_id}/release'.format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        release2 = response.data
        self.assertNotEqual(release1['uuid'], release2['uuid'])
        self.assertNotEqual(release1['config'], release2['config'])
        self.assertEqual(release1['image'], release2['image'])
        self.assertEqual(release1['build'], release2['build'])
        self.assertEqual(release1['args'], release2['args'])
        self.assertEqual(release1['command'], release2['command'])
        self.assertEquals(release2['version'], 2)
        # check that updating the build rolls a new release
        url = '/api/formations/{formation_id}/build'.format(**locals())
        build_config = json.dumps({'PATH': 'bin:/usr/local/bin:/usr/bin:/bin'})
        body = {'sha': uuid.uuid4().hex, 'slug_size': 4096000, 'procfile': json.dumps({'web': 'node server.js'}),
                'url': 'http://deis.local/slugs/1c52739bbf3a44d3bfb9a58f7bbdd5fb.tar.gz',
                'checksum': uuid.uuid4().hex, 'config': build_config}
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['url'], body['url'])
        # check to see that a new release was created
        url = '/api/formations/{formation_id}/release'.format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        release3 = response.data
        self.assertNotEqual(release2['uuid'], release3['uuid'])
        self.assertNotEqual(release2['build'], release3['build'])
        self.assertEqual(release2['image'], release3['image'])
        self.assertEqual(release2['args'], release3['args'])
        self.assertEqual(release2['command'], release3['command'])
        self.assertEquals(release3['version'], 3)
        # check that build config was respected
        self.assertNotEqual(release2['config'], release3['config'])
        url = '/api/formations/{formation_id}/config'.format(**locals())
        response = self.client.get(url)
        config3 = response.data
        config3_values = json.loads(config3['values'])
        self.assertIn('NEW_URL1', config3_values)
        self.assertIn('PATH', config3_values)
        self.assertEqual(config3_values['PATH'], 'bin:/usr/local/bin:/usr/bin:/bin')
        # check that updating the image rolls a new release
        url = '/api/formations/{formation_id}/image'.format(**locals())
        body = {'image': 'deis/autotest2'} 
        response = self.client.post(url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        # check to see that a new release was created
        url = '/api/formations/{formation_id}/release'.format(**locals())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        release4 = response.data
        self.assertNotEqual(release3['uuid'], release4['uuid'])
        self.assertNotEqual(release3['image'], release4['image'])
        self.assertEqual(release3['build'], release4['build'])
        self.assertEqual(release3['config'], release4['config'])
        self.assertEqual(release3['args'], release4['args'])
        self.assertEqual(release3['command'], release4['command'])
        self.assertEquals(release4['version'], 4)
        # TODO: add tests for updating args/command
        
        # disallow post/put/patch/delete
        self.assertEqual(self.client.post(url).status_code, 405)
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.patch(url).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)
