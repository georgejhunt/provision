#!/usr/bin/python
# read through kiwix catalog json

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date
from sqlalchemy import create_engine, text

import json
import os
import sys
import urllib2

# create the database if it does not exist
metadata = MetaData()
catalog = Table('catalog', metadata,
    Column('recno', Integer, primary_key=True),
    Column(u'publisher', String),
    Column(u'mediaCount', String),
    Column(u'perma_ref', String),
    Column(u'description', String),
    Column(u'lang3', String),
    Column(u'iso2', String),
    Column(u'creator',  String),
    Column(u'url', String),
    Column(u'title', String),
    Column(u'publisher', String),
    Column(u'download_url', String),
    Column(u'file_ref', String),
    Column(u'articleCount', String),
    Column(u'date', String),
    Column(u'id', String),
    Column(u'module_id', String),
    Column(u'size', String),
    Column(u'age_range', String),
    Column(u'rating', String),
    Column(u'zip_http_url', String),
    Column(u'zip_ftp_url', String),
    Column(u'rsync_url', String),
    Column(u'source_url', String),
    Column(u'logo_url', String),
    Column(u'category', String),
    Column(u'moddir', String),
    Column(u'version', String),
    Column(u'uuid', String)
)
if os.path.isfile( '{{ provision_assets_dir }}/catalog.sqlite' ):
   os.remove('{{ provision_assets_dir }}/catalog.sqlite')

engine=create_engine('sqlite:///{{ provision_assets_dir }}/catalog.sqlite')
engine_languages = create_engine('sqlite:///{{ provision_assets_dir }}/languages.sqlite')

if not os.path.isfile('{{ provision_assets_dir }}/catalog.sqlite'):
   metadata.create_all(engine)
in_path = '/etc/iiab/kiwix_catalog.json'
with open(in_path,'r') as jf:
   data = json.loads(jf.read())
zimlist = data['zims']
for zimkey in zimlist:
   try:
      ins = catalog.insert().values({
         u'publisher': data['zims'][zimkey][u'publisher'],
         u'mediaCount': data['zims'][zimkey][u'mediaCount'],
         u'perma_ref': data['zims'][zimkey][u'perma_ref'],
         u'description': data['zims'][zimkey][u'description'],
         u'lang3': data['zims'][zimkey][u'language'],
         u'creator': data['zims'][zimkey][u'creator'],
         u'url': data['zims'][zimkey][u'url'],
         u'title': data['zims'][zimkey][u'title'],
         u'download_url': data['zims'][zimkey][u'download_url'],
         u'file_ref': data['zims'][zimkey][u'file_ref'],
         u'articleCount': data['zims'][zimkey][u'articleCount'],
         u'date': data['zims'][zimkey][u'date'],
         u'id': data['zims'][zimkey][u'id'],
         u'size': data['zims'][zimkey][u'size'],
         #u'uuid': data['zims'][zimkey][u'uuid']
      })
      conn = engine.connect()
      result = conn.execute(ins)
   except Exception as e:
      print(str(e))
      print(zimkey) 

# excerpted from iiab-factory/content/gen-rachel-menus

"""

   Reads rachel menu fragments for every item in catalog at http://dev.worldpossible.org/cgi/json_api_v1.pl

   Author: Tim Moody <tim(at)timmoody(dot)com>

"""
rachel_catalog_url = "http://dev.worldpossible.org/cgi/json_api_v1.pl"
response = urllib2.urlopen(rachel_catalog_url)
rachel_catalog = json.loads(response.read())
response.close()

langconn = engine_languages.connect()
for item in rachel_catalog:
   # look up the three character language code
   sql = text("select iso3,engname from languages where iso2= :ch2;")
   rs = langconn.execute(sql, ch2=item[u'lang'])
   row = rs.fetchone()
   print(row['iso3'],row['engname'])
   try:
      ins = catalog.insert().values({
         u'publisher': 'rachel',
         u'mediaCount': item[u'file_count'],
         u'perma_ref': item[u'moddir'],
         u'description': item[u'description'],
         u'iso2': item[u'lang'],
         u'lang3': row['iso3'],
         #u'creator': item[u'creator'],
         u'url': item[u'rsync_url'],
         u'title': item[u'title'],
         u'download_url': item[u'zip_http_url'],
         u'file_ref': item[u'moddir'],
         u'articleCount': item[u'file_count'],
         #u'date': item[u'date'],
         #u'id': item[u'id'],
         u'size': str(int(item[u'ksize']) * 1000),
         #u'uuid': item[u'uuid']
         u'age_range': item[u'age_range'],
         u'rating': item[u'rating'],
         u'zip_ftp_url': item[u'zip_ftp_url'],
         u'source_url': item[u'source_url'],
         u'logo_url': item[u'logo_url'],
         u'category': item[u'category'],
         u'version': item[u'version'] })
   except Exception as e:
      print(e)
   try:
      conn = engine.connect()
      result = conn.execute(ins)
   except Exception as e:
      print(str(e))
#create table summary as select lan.iso2 as iso2,c.lang3 as lang3,engname,count(recno) as num from catalog as c left join lan.languages as lan  on c.lang3 = lan.iso3 group by lang3 order by num desc;
