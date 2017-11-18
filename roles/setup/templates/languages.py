#!/usr/bin/python
# read through language json, create sqlite replica

import json
import os
import sys
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date
from sqlalchemy import create_engine

# create the database if it does not exist
metadata = MetaData()
ltable = Table('languages', metadata,
    Column('id', Integer, primary_key=True),
    Column('iso2', String, index=True),
    Column('iso3', String, index=True),
    Column('engname', String),
    Column('locname', String),
    Column('native_spkrs', Integer)
)
engine=create_engine('sqlite:///{{ provision_assets_dir}}/languages.sqlite')
if not os.path.isfile('{{ provision_assets_dir }}/languages.sqlite'):
   metadata.create_all(engine)

json_file = '/library/www/html/common/assets/lang_codes.json'
with open(json_file,'r') as jf:
   try:
      langs = json.loads(jf.read())
   except Exception as e:
      print(e)
      sys.exit(1)

conn = engine.connect()
for lang in langs.keys():
   try:
      ins = ltable.insert().values({
         'iso3': lang,
         'iso2': langs[lang]['iso2'],
         'engname': langs[lang]['engname'],
         'locname': langs[lang]['locname']
      })
      result = conn.execute(ins)
   except Exception as e:
      print(str(e))

