# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 16:10:54 2017

@author: Star
"""
import re


def get_links(html):
    #get all the links in specific page
    webpage_regex = re.compile('http.*?\"',re.IGNORECASE)
    links_o = webpage_regex.findall(html)
    links = []
    for elements in links_o:
        elements = elements[:-1]
        links.append(elements)
    return links

def getpiclinks(oarticle):
    links = re.findall('src=[\'\"].*?[\'\"]',str(oarticle))
    return links