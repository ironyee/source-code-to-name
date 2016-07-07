# -*- coding: utf-8 -*-
import json
import unittest

import codetoname


class TestFeature(unittest.TestCase):
    def test_feature_no_file(self):
        self.assertRaises(Exception, codetoname.features.extract_feature, '')

    def test_feature_no_func(self):
        self.assertFalse(codetoname.features.extract_feature('./test/samples/no_function.py'))

    def test_feature_one_func(self):
        features = codetoname.features.extract_feature('./test/samples/one_function.py')
        self.assertTrue(features)
        self.assertIn('name', features[0])
        self.assertIn('body', features[0])
        self.assertIn('args', features[0])
        self.assertIn('cls', features[0])
        self.assertEqual('get_wsgi_application', features[0]['name'])
        self.assertEqual(2, len(features[0]['body']))
        self.assertEqual('Expr', features[0]['body'][0])
        self.assertEqual('Return', features[0]['body'][1])
        self.assertTrue(json.dumps(features[0]))

    def test_feature_name_none_camelcase(self):
        features = codetoname.features.extract_feature('./test/samples/one_function_camelcase.py')
        self.assertTrue(features)
        self.assertEqual('get_wsgi_application', features[0]['name'])

    def test_from_gitrepo_none(self):
        features = codetoname.features.from_repo({}, 'python')
        self.assertFalse(features)

    def test_from_gitrepo_one(self):
        gitrepo = {'url': 'https://github.com/geekcomputers/Python.git'}
        features = codetoname.features.from_repo(gitrepo, 'python')
        self.assertTrue(features)

    def test_from_gitrepo_unsupported(self):
        self.assertRaises(KeyError, codetoname.features.from_repo, {}, 'c++')

    def test_fromfile(self):
        features = codetoname.features.from_file('./test/samples/one_function.py')
        self.assertTrue(features)
