#! /usr/bin/python

# Copyright (C) 2005 Ross Burton <ross@burtonini.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys, datetime

import musicbrainz
from musicbrainz.queries import *

import scrobbler

mb = musicbrainz.mb()

if len(sys.argv) == 2:
    mb.SetDepth(4)
    mb.QueryWithArgs(MBQ_GetAlbumById, [sys.argv[1]])
else:
    mb.SetDepth(2)
    mb.Query(MBQ_GetCDTOC)
    cdid = mb.GetResultData(MBE_TOCGetCDIndexId)
    mb.QueryWithArgs(MBQ_GetCDInfoFromCDIndexId, [cdid])

count = mb.GetResultInt(MBE_GetNumAlbums)
if count == 0:
    print "Found no albums"
    sys.exit(1)
if count > 1:
    print "TODO: found %d albums" % count
    sys.exit(2)
    
tracks = []

mb.Select1(MBS_SelectAlbum, 1)
album = mb.GetResultData(MBE_AlbumGetAlbumName)
for ii in range(1, mb.GetResultInt(MBE_AlbumGetNumTracks) + 1):
    mbid = mb.GetIDFromURL(mb.GetResultData1(MBE_AlbumGetTrackId, ii))
    artist = mb.GetResultData1(MBE_AlbumGetArtistName, ii)
    name = mb.GetResultData1(MBE_AlbumGetTrackName, ii)
    dura = mb.GetResultInt1(MBE_AlbumGetTrackDuration, ii) / 1000
    track = mb.GetResultInt1(MBE_AlbumGetTrackNum, ii)
    tracks.append(scrobbler.Track(artist, name, album, dura, mbid, None))

# Fix up times on tracks
current = datetime.datetime.now()
tracks.reverse()
for t in tracks:
    current = current - datetime.timedelta(seconds=t.length)
    t.tracktime = current
tracks.reverse()

scrob = scrobbler.Scrobbler("username", "password")
scrob.handshake()
scrob.submit(tracks)
