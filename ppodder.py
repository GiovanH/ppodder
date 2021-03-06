#!/usr/bin/env python3

import os
import urllib.request
from xml.dom import minidom
import subprocess
import collections

class Podcast(collections.namedtuple("Podcast", ["channel", "title", "description", "link", "pubDate", "enclosureUrl"])):

    @staticmethod
    def from_item(item, channel):
        try:
            tag_names = ['title','description','link','pubDate']
            attrs = {}
            for tag_name in tag_names:
                attrs[tag_name] = item.getElementsByTagName(tag_name)[0].firstChild.data
            attrs["enclosureUrl"] = item.getElementsByTagName('enclosure')[0].getAttribute("url")
            return Podcast(channel=channel, **attrs)
        except IndexError:
            return None

class Channel:
    def __init__(self, url, podsdir=None):
        self.url = url
        self.parse()
        self.poddir = os.path.join(podsdir, self.title)
        self.logfile = os.path.join(self.poddir,"podcasts.log")
        try:
            os.makedirs(self.poddir, exist_ok=True)
        except OSError:
            pass
        os.chdir(self.poddir)

    def parse(self):
        dom = minidom.parse(urllib.request.urlopen(self.url))
        try:
            self.node = dom.getElementsByTagName('channel')[0]
            self.title = self.node.getElementsByTagName('title')[0].firstChild.data
        except IndexError:
            self.title = self.url.replace("/","_")

    def get_items(self):
        return self.node.getElementsByTagName("item")

    def __str__(self):
        return "Channel \"%s\"" % (self.title)

class PodcastManager:
    def __init__( self, podslist="rss.conf", home=os.path.join(os.getenv("HOME"), "Podcasts") ):
        self.podslist = podslist
        self.home = home
        self.incomplete_downloads = os.path.join(home,"incomplete downlods")

    def __add_to_store(self, podcast):
        if podcast.enclosureUrl != None and podcast.enclosureUrl != "":
            podsstore = open(podcast.channel.logfile, "a+")
            podsstore.write(podcast.enclosureUrl + os.linesep)
            podsstore.close()

    def add_to_skipped(self, podcast):
        self.__add_to_store(podcast)

    def download(self, podcast):
        filename = podcast.enclosureUrl.split('/')[-1]
        subprocess.Popen("mkdir -p \"{incomplete_downloads}\" && cd \"{incomplete_downloads}\" && wget -c \"{episode_url}\" -O \"{filename}\" && mv \"{filename}\" \"{channel_home}\" && echo \"{episode_url}\" >> \"{logfile}\"".format(incomplete_downloads=self.incomplete_downloads, episode_url=podcast.enclosureUrl, filename=filename, channel_home=podcast.channel.poddir, logfile=podcast.channel.logfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def is_downloaded(self, podcast):
        if os.path.exists(podcast.channel.logfile):
            fd = open(podcast.channel.logfile, "r")
        else:
            return False
        result = False
        line = podcast.enclosureUrl
        for raw in fd:
            if line == raw.strip():
                result = True
                break
        fd.close()
        return result

    def check_channel( self, channel ):
        skip_all = False
        download_all = False
        try:
            items = channel.get_items()
        except AttributeError:
            print("Problems with {channel}!".format(channel=channel))
            return
        for item in items:
            podcast = Podcast.from_item(item, channel)
            if not podcast:
                continue
            if skip_all:
                self.add_to_skipped(podcast)
                continue
            if download_all:
                self.download(podcast)
                continue
            if not self.is_downloaded(podcast):
                action = self.prompt_for_action(podcast)
                if action == 1:
                    self.download(podcast)
                elif action == 2:
                    download_all = True
                    self.download(podcast)
                    continue
                elif action == 3:
                    self.add_to_skipped(podcast)
                elif action == 4:
                    skip_all = True
                    self.add_to_skipped(podcast)
                    continue
                else:
                    exit()

    def prompt_for_action(self,podcast):
        print("Title: %s\nLink: %s\nDate: %s" % (podcast.title, podcast.enclosureUrl, podcast.pubDate))
        return int(input("Choose an action for this podcast (1. Download, 2. Download All, 3. Skip, 4. Skip All 5. Abort): "))

    def check_all_channels(self):
        podsfd = open(self.podslist, "r")
        for url in podsfd:
            channel = Channel(url, self.home)
            print("Checking for new episodes in %s" % (channel))
            self.check_channel(channel)
        podsfd.close()

if __name__ == "__main__":
    PodcastManager().check_all_channels()
