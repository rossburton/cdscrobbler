#!/usr/bin/python

# Audioscrobbler python module
# Copyright (C) Matt Biddulph
# Licensed under the BSD
# http://www.hackdiary.com/archives/000052.html

import urllib2,urllib,re,time,md5,datetime,sys

class Scrobbler(object):
    def __init__(self,user,password,client="tst",version="1.0",url="http://post.audioscrobbler.com/"):
        self.url = url
        self.user = user
        self.password = password
        self.client = client
        self.version = version
    def handshake(self):
        url = self.url+"?"+urllib.urlencode({
            "hs":"true",
            "p":"1.1",
            "c":self.client,
            "v":self.version,
            "u":self.user
            })
        result = urllib2.urlopen(url).readlines()
        if result[0].startswith("BADUSER"):
            return self.baduser(result[1:])
        if result[0].startswith("UPTODATE"):
            return self.uptodate(result[1:])
        if result[0].startswith("FAILED"):
            return self.failed(result)
    def uptodate(self,lines):
        self.md5 = re.sub("\n$","",lines[0])
        self.submiturl = re.sub("\n$","",lines[1])
        self.interval(lines[2])
    def baduser(self,lines):
        print "Bad user"
    def failed(self,lines):
        print lines[0]
        self.interval(lines[1])
    def interval(self,line):
        match = re.match("INTERVAL (\d+)",line)
        if match is not None:
            print "[audioscrobbler] Sleeping for",match.group(1),"secs"
            time.sleep(int(match.group(1)))
    def submit(self,tracks):
        print "[audioscrobbler] Submitting"
        md5response = md5.md5(md5.md5(self.password).hexdigest()+self.md5).hexdigest()
        post = "u="+self.user+"&s="+md5response
        count = 0
        for track in tracks:
            post += "&"
            post += track.urlencoded(count)
            count += 1
        post = unicode(post)
        print post
        result = urllib2.urlopen(self.submiturl,post)
        results = result.readlines()
        if results[0].startswith("OK"):
            print "OK"
            self.interval(results[1])
        if results[0].startswith("FAILED"):
            self.failed([results[0],"INTERVAL 0"])

class Track(object):
    def __init__(self,artist,name,album,length,mbid=None,tracktime=None):
        self.params = {}
        self.artist = artist
        self.name = name
        self.album = album
        self.length = length
        self.mbid = mbid
        if tracktime:
            self.tracktime = tracktime
        else:
            self.tracktime = datetime.datetime.utcnow().isoformat(' ')

    def __repr__(self):
        return "'"+self.name+"' by '"+self.artist+"' from '"+self.album+"'"

    def urlencoded(self,num):
        def quote(s):
            return urllib.quote_plus(s.encode("utf_8"))
        encode = ""
        encode += "a["+str(num)+"]="+quote(self.artist)
        encode += "&t["+str(num)+"]="+quote(self.name)
        encode += "&l["+str(num)+"]="+quote(str(self.length))
        encode += "&i["+str(num)+"]="+ quote(self.tracktime.isoformat(' '))
        if self.mbid is not None:
            encode += "&m["+str(num)+"]="+quote(self.mbid)
        else:
            encode += "&m["+str(num)+"]="
        encode += "&b["+str(num)+"]="+quote(self.album)
        return encode
