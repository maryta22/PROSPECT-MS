# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Email(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, id: int=None, prospection_id: int=None, sender: str=None, message: str=None, _date: date=None):  # noqa: E501
        """Email - a model defined in Swagger

        :param id: The id of this Email.  # noqa: E501
        :type id: int
        :param prospection_id: The prospection_id of this Email.  # noqa: E501
        :type prospection_id: int
        :param sender: The sender of this Email.  # noqa: E501
        :type sender: str
        :param message: The message of this Email.  # noqa: E501
        :type message: str
        :param _date: The _date of this Email.  # noqa: E501
        :type _date: date
        """
        self.swagger_types = {
            'id': int,
            'prospection_id': int,
            'sender': str,
            'message': str,
            '_date': date
        }

        self.attribute_map = {
            'id': 'id',
            'prospection_id': 'prospection_id',
            'sender': 'sender',
            'message': 'message',
            '_date': 'date'
        }
        self._id = id
        self._prospection_id = prospection_id
        self._sender = sender
        self._message = message
        self.__date = _date

    @classmethod
    def from_dict(cls, dikt) -> 'Email':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Email of this Email.  # noqa: E501
        :rtype: Email
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this Email.


        :return: The id of this Email.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this Email.


        :param id: The id of this Email.
        :type id: int
        """

        self._id = id

    @property
    def prospection_id(self) -> int:
        """Gets the prospection_id of this Email.


        :return: The prospection_id of this Email.
        :rtype: int
        """
        return self._prospection_id

    @prospection_id.setter
    def prospection_id(self, prospection_id: int):
        """Sets the prospection_id of this Email.


        :param prospection_id: The prospection_id of this Email.
        :type prospection_id: int
        """

        self._prospection_id = prospection_id

    @property
    def sender(self) -> str:
        """Gets the sender of this Email.


        :return: The sender of this Email.
        :rtype: str
        """
        return self._sender

    @sender.setter
    def sender(self, sender: str):
        """Sets the sender of this Email.


        :param sender: The sender of this Email.
        :type sender: str
        """

        self._sender = sender

    @property
    def message(self) -> str:
        """Gets the message of this Email.


        :return: The message of this Email.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this Email.


        :param message: The message of this Email.
        :type message: str
        """

        self._message = message

    @property
    def _date(self) -> date:
        """Gets the _date of this Email.


        :return: The _date of this Email.
        :rtype: date
        """
        return self.__date

    @_date.setter
    def _date(self, _date: date):
        """Sets the _date of this Email.


        :param _date: The _date of this Email.
        :type _date: date
        """

        self.__date = _date
