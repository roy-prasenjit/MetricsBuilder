# coding: utf-8

"""
    MetricsBuilder API

    An API for accessing High Performance Computing(HPC) system monitoring metrics.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Contact: jie.li@ttu.edu
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class UnifiedMetricsNodesInfoMetrics(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'memory_usage': 'list[float]',
        'cpu_usage': 'list[float]',
        'power_usage': 'list[float]',
        'fan_speed': 'list[list[int]]',
        'cpu_int_temp': 'list[list[float]]'
    }

    attribute_map = {
        'memory_usage': 'memory_usage',
        'cpu_usage': 'cpu_usage',
        'power_usage': 'power_usage',
        'fan_speed': 'fan_speed',
        'cpu_int_temp': 'cpu_int_temp'
    }

    def __init__(self, memory_usage=None, cpu_usage=None, power_usage=None, fan_speed=None, cpu_int_temp=None, local_vars_configuration=None):  # noqa: E501
        """UnifiedMetricsNodesInfoMetrics - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._memory_usage = None
        self._cpu_usage = None
        self._power_usage = None
        self._fan_speed = None
        self._cpu_int_temp = None
        self.discriminator = None

        self.memory_usage = memory_usage
        self.cpu_usage = cpu_usage
        self.power_usage = power_usage
        self.fan_speed = fan_speed
        self.cpu_int_temp = cpu_int_temp

    @property
    def memory_usage(self):
        """Gets the memory_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501


        :return: The memory_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: list[float]
        """
        return self._memory_usage

    @memory_usage.setter
    def memory_usage(self, memory_usage):
        """Sets the memory_usage of this UnifiedMetricsNodesInfoMetrics.


        :param memory_usage: The memory_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and memory_usage is None:  # noqa: E501
            raise ValueError("Invalid value for `memory_usage`, must not be `None`")  # noqa: E501

        self._memory_usage = memory_usage

    @property
    def cpu_usage(self):
        """Gets the cpu_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501


        :return: The cpu_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: list[float]
        """
        return self._cpu_usage

    @cpu_usage.setter
    def cpu_usage(self, cpu_usage):
        """Sets the cpu_usage of this UnifiedMetricsNodesInfoMetrics.


        :param cpu_usage: The cpu_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and cpu_usage is None:  # noqa: E501
            raise ValueError("Invalid value for `cpu_usage`, must not be `None`")  # noqa: E501

        self._cpu_usage = cpu_usage

    @property
    def power_usage(self):
        """Gets the power_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501


        :return: The power_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: list[float]
        """
        return self._power_usage

    @power_usage.setter
    def power_usage(self, power_usage):
        """Sets the power_usage of this UnifiedMetricsNodesInfoMetrics.


        :param power_usage: The power_usage of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and power_usage is None:  # noqa: E501
            raise ValueError("Invalid value for `power_usage`, must not be `None`")  # noqa: E501

        self._power_usage = power_usage

    @property
    def fan_speed(self):
        """Gets the fan_speed of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501


        :return: The fan_speed of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: list[list[int]]
        """
        return self._fan_speed

    @fan_speed.setter
    def fan_speed(self, fan_speed):
        """Sets the fan_speed of this UnifiedMetricsNodesInfoMetrics.


        :param fan_speed: The fan_speed of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type: list[list[int]]
        """
        if self.local_vars_configuration.client_side_validation and fan_speed is None:  # noqa: E501
            raise ValueError("Invalid value for `fan_speed`, must not be `None`")  # noqa: E501

        self._fan_speed = fan_speed

    @property
    def cpu_int_temp(self):
        """Gets the cpu_int_temp of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501


        :return: The cpu_int_temp of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :rtype: list[list[float]]
        """
        return self._cpu_int_temp

    @cpu_int_temp.setter
    def cpu_int_temp(self, cpu_int_temp):
        """Sets the cpu_int_temp of this UnifiedMetricsNodesInfoMetrics.


        :param cpu_int_temp: The cpu_int_temp of this UnifiedMetricsNodesInfoMetrics.  # noqa: E501
        :type: list[list[float]]
        """
        if self.local_vars_configuration.client_side_validation and cpu_int_temp is None:  # noqa: E501
            raise ValueError("Invalid value for `cpu_int_temp`, must not be `None`")  # noqa: E501

        self._cpu_int_temp = cpu_int_temp

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, UnifiedMetricsNodesInfoMetrics):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, UnifiedMetricsNodesInfoMetrics):
            return True

        return self.to_dict() != other.to_dict()
