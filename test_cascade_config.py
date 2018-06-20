# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath
from os.path import join
from os.path import normpath

from cascade_config import load_config

my_path = normpath(join(abspath(__file__), '../'))

config1 = join(my_path, 'testconf1.conf')
config2 = join(my_path, 'testconf2.conf')


def test_single_config():
    conf = load_config('myapp', [config1])

    assert conf.get('section1', 'herp') == 'derp'
    assert conf.get('section2', 'herp2') == 'derp2'


def test_double_config():
    conf = load_config('myapp', [config1, config2])

    assert conf.get('section1', 'herp') == 'derp'
    assert conf.get('section2', 'herp2') == 'nope2'
