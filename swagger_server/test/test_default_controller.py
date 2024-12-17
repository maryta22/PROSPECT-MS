# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.prospect import Prospect  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_prospects_get(self):
        """Test case for prospects_get

        Obtener todos los prospectos
        """
        response = self.client.open(
            '/prospects',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_prospects_id_delete(self):
        """Test case for prospects_id_delete

        Eliminar un prospecto
        """
        response = self.client.open(
            '/prospects/{id}'.format(id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_prospects_id_get(self):
        """Test case for prospects_id_get

        Obtener un prospecto por ID
        """
        response = self.client.open(
            '/prospects/{id}'.format(id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_prospects_id_put(self):
        """Test case for prospects_id_put

        Actualizar un prospecto
        """
        body = Prospect()
        response = self.client.open(
            '/prospects/{id}'.format(id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_prospects_post(self):
        """Test case for prospects_post

        Crear un prospecto
        """
        body = Prospect()
        response = self.client.open(
            '/prospects',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_prospects_seller_seller_id_get(self):
        """Test case for prospects_seller_seller_id_get

        Obtener prospectos por vendedor
        """
        response = self.client.open(
            '/prospects/seller/{sellerId}'.format(seller_id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
