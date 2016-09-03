#!/usr/bin/env python

import argparse
import datetime
import json
import os
import sys

import requests

def parse_args(args):
  parser = argparse.ArgumentParser()
  parser.add_argument('inputdir', type=str,
                      help='Input directory of files you want renamed')
  parser.add_argument('-d', '--dev', help='Switches APIs to dev instances',
                      action='store_true')
  args = parser.parse_args()
  return args

def episodecontroller(filename, originalpath):
  """ Controler that handles episodes of WWE shows.

  Args:
    filename: Input filename of WWE Show - SxxExx - <dd-mm-yyyy>.mp4
    dirpath: Full Directory path for rename purposes
  """
  originalfile = os.path.basename(filename)
  originalname, ext = os.path.splitext(originalfile)
  showname = originalname.split(' - ')[0]
  showjson = json.loads(TVMazeSearch(showname).text)
  episodedate = filedate(filename)
  episodedata = finddate(episodedate, showjson)
  return showname, episodedate, episodedata

def finddate(episodedate, showjson):
  """ Finds the airdate within the Show Json object.

  Args:
    episodedate: The file-name episode date
    showjson: The showjson object
  """
  mindatecush = episodedate - datetime.timedelta(days=2)
  maxdatecush = episodedate + datetime.timedelta(days=2)
  for item in showjson['_embedded']['episodes']:
    datetimejson = datetime.datetime.strptime(item['airdate'], '%Y-%m-%d')
    if mindatecush <= datetimejson <= maxdatecush:
      season = "%02d" % item['season']
      episode = "%02d" % item['number']
      episodename = item['name']
      return season, episode, episodename


def filedate(originalname):
  datestring = originalname.split(' - ')[2][:-4]
  episodedate = datetime.datetime.strptime(datestring, '%d-%m-%Y')
  return episodedate 

def TVMazeSearch(showname):
  """ Performs embedded episode single show search on TVMaze.com

  Args:
    showname: Query of the Show name
  """
  baseurl = 'http://api.tvmaze.com'
  searchurl = '/singlesearch/shows?q='
  showjson = requests.get(baseurl + searchurl + showname + '&embed=episodes')
  return showjson


def main():
  parser = parse_args(sys.argv[1:])
  for (dirpath, dirname, filenames) in os.walk(parser.inputdir):
    for filename in filenames:
      originalpath = dirpath + '/'
      originalfile = os.path.basename(filename)
      originalname, ext = os.path.splitext(originalfile)
      if originalfile.startswith('.'):
        pass
      if originalfile.startswith('WWE'):
        print 'Original Filename -', originalfile
        finalname = episodecontroller(originalfile, originalpath)
        date = str(finalname[1].strftime('%Y-%m-%d'))
        renamed = str(finalname[0]) + ' - S' + str(finalname[2][0]) + \
                  'E' + str(finalname[2][1]) + ' - ' + date + ' - '\
                  + str(finalname[2][2])
        print 'Renaming to -', renamed
        os.rename(originalpath + originalfile, originalpath + renamed + str(ext))

if __name__ == '__main__':
  main()