#!/usr/bin/python

import sqlite3
import sys,os,json
from flask import Flask,request,jsonify

app = Flask(__name__)
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s" % (num, suffix)

@app.route('/')
def hello():
   return("hello George")

@app.route('/starter')
def get_one():
   db = sqlite3.connect('{{ provision_assets_dir }}/catalog.sqlite')
   db.row_factory = sqlite3.Row
   iso3 = request.args.get('language','eng')
   cursor = db.cursor()
   cursor.execute('attach database "{{ provision_assets_dir }}/languages.sqlite" as languages')
   sql = "select  engname, locname, size, native_spkrs,publisher,file_ref,date, recno from catalog as c left join languages as l on c.iso3 = l.iso3 where c.iso3 = ? order by file_ref"
   cur = cursor.execute(sql,(iso3,))
   rows = cur.fetchall()
   tree=[]
   for row in rows:
       child = {}
       child['title'] = row['file_ref'] 
       tree.append(child)
   return(jsonify(tree))

def get_kiwix_data():
   global db,cursor
   
   parent = {}
   parent["title"] = "Kiwix"
   parent["children"] =[]

   # use the creator field to generate smaller lists in kiwix
   cursor.execute('select publisher,creator,max(creator) from curlang  group by creator')
   subjects = cursor.fetchall()
   itemcursor = db.cursor()
   for subject in subjects:
      # add the creator to the list of children of parent
      subject_name = {}
      if not subject['creator']:continue
      subject_name['title'] = subject['creator']
      subject_name['children'] = []
      parent['children'].append(subject_name)
      sql = 'select * from curlang where creator = (?) order by file_ref' 
      itemcursor.execute(sql, (subject['creator'],))
      children = itemcursor.fetchall()
      for child in children:
         item = {}
         try:
            size = int(child['size']) * 1000.0
         except:
            size = 0
         item['title'] = child['file_ref'] +" " + child['articleCount'] + ' articles ' + \
                         sizeof_fmt(size) 
         subject_name['children'].append(item)
      
   return ((parent))

def get_rachel_data():
   global db,cursor

   parent = {}
   parent["title"] = "Rachel"
   parent["children"] =[]
   sql = 'select * from curlang where publisher = (?) order by file_ref' 
   cursor.execute(sql,['rachel'])
   children = cursor.fetchall()
   for child in children:
      item = {}
      try:
         size = int(child['size']) 
      except:
         size = 0
      item['title'] = child['file_ref'] +" "  + sizeof_fmt(size) 
      parent['children'].append(item)
   return ((parent))

@app.route('/data')
def get_lang():
   global db,cursor
   db = sqlite3.connect(':memory:')
   #db = sqlite3.connect('sqlite:////opt/provision/temp.sqlite')
   db.row_factory = sqlite3.Row
   iso3 = request.args.get('language','eng')
   cursor = db.cursor()
   #cursor.execute('attach database "{{ provision_assets_dir }}/languages.sqlite" as languages')
   cursor.execute('attach database "{{ provision_assets_dir }}/catalog.sqlite" as cat')
   cursor.execute('create table curlang as SELECT * from cat.catalog where iso3 = "%s"'%iso3)

   #start generating the list of items for tree
   tree=[]
   tree.append(get_kiwix_data())
   tree.append(get_rachel_data())

   cursor.close()
   #print(tree)
   return(jsonify(tree))

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
