"""
Metaclass for PyQt abstract class
"""

from abc import ABCMeta
from PyQt5.QtCore import QObject

class QtABCMeta(type(QObject), ABCMeta):
    pass
