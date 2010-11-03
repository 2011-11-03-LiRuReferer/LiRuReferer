#!/usr/bin/env python2
#-*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

if __name__ == '__main__':
    setup(
        console=['LiRuReferer-winc'],
        windows=['LiRuRefererw-winw'],
        options={
                'py2exe':{
                        'includes': [
                            'weakref',
                            'contextlib',
                            'random',
                            'urllib',
                            'urllib2',
                        ],
                        'excludes': ['_liru_referer_lib__api_2655426353'],
                }
        }
    ) 

