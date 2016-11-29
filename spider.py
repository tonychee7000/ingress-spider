#!/usr/bin/env python3
# Ingress Spider
# For collection codes from investigate
# By: TonyChyi <tonychee1989@gmail.com>

import sys
import urllib.request
import time
import xml.etree.ElementTree as XML
from pyquery.pyquery import PyQuery as pq


def get_xml_from_investigate():
    try:
        url = 'http://investigate.ingress.com/feed/'
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req)
        return res.read().decode('utf-8')
    except Exception as e:
        print(e, file=sys.stderr)
        return None


def analize_xml():
    try:
        xml_str = get_xml_from_investigate()
        assert isinstance(xml_str, str)

        xml_tree = XML.fromstring(xml_str)
        channel = xml_tree.find('channel')
        items = channel.findall('item')
        return items
    except Exception as e:
        print(e, file=sys.stderr)
        return None


def find_code():
    items = analize_xml()
    code_info = []
    for item in items:
        title = item.find('title').text
        pubDate = item.find('pubDate').text
        content = item.find('content:encoded',
                            namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'}).text
        code_info.append({
            'title': title,
            'time': time.strptime(pubDate, "%a, %d %b %Y %H:%M:%S +0000"),
            'codes': analyze_html(content),
            'origin': content})
    return code_info


def analyze_html(html_content):
    code_list = []

    def update_list(ele):
        if ele is not None and len(ele) >= 10:
            code_list.append(ele)

    html = pq(html_content, parser='html_fragments')
    # Step 1: find in <img>
    imgs = html('img')
    if imgs is not None:
        for img in imgs:
            code = img.attrib['alt']
            update_list(code)

    # Step 2: find in <span>
    spans = html('span')
    if spans is not None:
        for span in spans:
            code = span.text
            update_list(code)

    # Step 3: find in <a>
    alinks = html('a')
    if alinks is not None:
        for link in alinks:
            url = link.attrib['href']
            urls = url.split('#', 1)
            if len(urls) == 2:
                code = urls[1]
                update_list(code)

    # Step 4: find all elements with 'id'
    html_ids = html('[id!=""]')
    if html_ids is not None:
        for html_id in html_ids:
            code = html_id.attrib['id']
            update_list(code)

    return code_list


if __name__ == '__main__':
    pn = find_code()
    for p in pn:
        print("Title: {0}".format(p['title']))
        print("Date: {0}".format(time.strftime('%Y-%m-%d %H:%M:%S', p['time'])))
        print("Found {0} code(s) in article:".format(len(p['codes'])))
        for i in p['codes']:
            print("\t* {0}".format(i))

        print("\n================\n")
