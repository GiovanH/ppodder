#!/usr/bin/python

import os
import urllib
from xml.dom import minidom
import subprocess


class Podcast:
    def __init__(self, title=None, description=None, link=None, pubDate=None, enclosureUrl=None, valid=False):
        self.title = title
        self.description = description
        self.link = link
        self.pubDate = pubDate
        self.enclosureUrl = enclosureUrl
        self.valid = valid

    def fillFromItem(self, item):
        try:
            self.title = item.getElementsByTagName('title')[0].firstChild.data
            self.description = item.getElementsByTagName('description')[0].firstChild.data
            self.link = item.getElementsByTagName('link')[0].firstChild.data
            self.enclosureUrl = item.getElementsByTagName('enclosure')[0].getAttribute("url")
            self.pubDate = item.getElementsByTagName('pubDate')[0].firstChild.data
            self.valid = True
        except IndexError:
            self.valid = False

    def download(self):
            subprocess.Popen("wget -c %s" % (podcast.enclosureUrl), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __str__(self):
        return "Podcast(title=%s)" % (self.title)

class Channel:
    def __init__(self, url, podsdir=None):
        self.url = url
        parse()
        self.poddir = os.path.join(self.podsdir, self.title)
        self.logfile = os.path.join(poddir,"podcasts.log")

    def parse(self):
        dom = minidom.parse(urllib.urlopen("http://" + url))
        try:
            self.node = dom.getElementsByTagName('channel')[0]
            self.title = self.node.getElementsByTagName('title')[0].firstChild.data
        except IndexError:
            self.title = url.replace("/","_")

    def get_items(self):
        return self.node.getElementsByTagName("item")

    def add_to_log(self, podcast):
        podsstore = open(self.logfile, "a+")
        podsstore.write(podcast.enclosureUrl + "\n")
        podsstore.close()

    def is_downloaded(self, podcast):
        fd = open(self.logfile, "r+")
        result = False
        line = podcast.enclosureUrl
        for raw in fd:
            if line == raw.strip():
                result = True
                break
        fd.close()
        return result

podsdir = os.path.join(os.getenv("HOME"),"Podcasts")

rssfile = open("rss.conf", "r")
for url in rssfile:
    channel = Channel(url)
    try:
        os.mkdir(poddir)
    except OSError:
        pass
    os.chdir(poddir)
    for item in channel.get_items():
        podcast = Podcast()
        podcast.fillFromItem(item)
        print podcast.enclosureUrl
        if not channel.is_downloaded(podcast) and podcast.valid:
            print "Title: %s\nLink: %s" % (podcast.title, podcast.link)
            action = int(raw_input("Choose an action for this podcast (1. Download, 2. Skip, 3. Abort): "))
            if action == 1:
                podcast.download()
                channel.add_to_log(podcast)
            elif action == 2:
                channel.add_to_log(podcast)
            else:
                exit()
