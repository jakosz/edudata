# -*- coding:utf-8 -*-
import csv
import StringIO
import json
from pandas import DataFrame as psDataFrame
from pymongo import MongoClient
from cython_edudata_helpers import int2str


class MongoHandler:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.research_data

    def mongodb_insert_columns(self,cb_reader, pandas_df, df_name):
        """
        Insert columns to MongoDB in a loop ( TODO: parallel insert should be easy)
        Profiling showed that conversion to Unicode adds a lot of complexity in :
        dict((key,value) for (key, value) in var_data.items()) slowing down from 0.39 sec
        to 10 seconds for 4000 column file!
        """
        dataframes = self.db.dataframes
        for nr,row in enumerate(cb_reader):
            column = dict()
            column['df_name'] = df_name
            column['name'],column['desc_short'], column['desc_long'],\
                column['keywords'], column['type'],\
                column['scale'], column['value_len'],\
                column['precision'], column['min_value'],\
                column['max_value'], column['labels'],column['condition'] = row
                
            try:
                var_data = pandas_df[ column['name'] ].to_dict()
                
                column['data'] = dict((int2str(key), value) for (key, value) in var_data.items()) 
            except KeyError:
                e= "Failed to locate '{}' var in {} df columns ".format(column['name'], pandas_df.columns)
                raise KeyError, e
            dataframes.insert(column)
            #data['columns'].append(column)
            

    def process_data(self, df_name, codebook, df):
        """
        get codebook and dataframe, convert df into pandas object and 
        insert it into mongoDB. This can be much improved :
        TODO find a way to chop df into columns w/o pandas and make a json object
        directly keeping row numbers.
        """
        cb_reader = csv.reader(codebook, delimiter = ';', quotechar = '"')
        cb_reader.next() ## skip the header of the codebook!
        data_reader =  csv.reader(df,delimiter=";",quotechar='"')
        data_header = data_reader.next() ## get header
        df_rows = [row for row in data_reader] 
        pandas_df = psDataFrame(df_rows,columns=data_header)
        self.mongodb_insert_columns(cb_reader,pandas_df, df_name)


    def get_dataframe_and_info(self,df_name):
        cursor = self.db.dataframes.find({'df_name':df_name})
        df  = [ column for column in cursor ]
        dfdict = dict()
        rownames = []
        info = dict()
        # TU MUSI BYĆ SORTOWANIE po kluczu i to kluczu INTEGER!!
        for nr,column in enumerate(df): # type(df['columns']) == type([])
            # first, get rownames
            if nr == 0:
                rownames = column['data'].keys()
            # Replace decimal point ',' with '.' to convert it later to type 'float' 
            if column['type'] == u'liczba rzeczywista':
                column['data'] = dict((k, v.replace(',','.')) for (k, v) in column['data'].iteritems())
            #convert rows from string to INTEGER
            rows = dict((int(key), value) for (key, value) in column['data'].items()) 
            # prepare dictionary of columns to convert them into pandas.DataFrame
            dfdict[column['name']] = [value for (key,value) in rows.iteritems()]
            info[column['name']] = dict((key,value) for key, value in column.iteritems() if key != 'data') # Copy everything but data
        psDf = psDataFrame(dfdict, index = rownames )
        """
        If codebook states that the column is numeric than convert it to numeric
        """
        for column in df['columns']:
            if column['type'] == u'liczba całkowita':
                psDf[column['name']] = psDf[column['name']].astype(int)
            elif column['type'] == u'liczba rzeczywista': 
                psDf[column['name']] = psDf[column['name']].astype(float)
            else:
                psDf[column['name']] = psDf[column['name']].astype(str)
        # return dictionary for views.py
        return {'info':info,'df': psDf}

    def get_csv(self, df_name,sep,decimal):
        pandas_df = self.get_dataframe(df_name)["df"] # get only DataFrame
        buffer = StringIO.StringIO()
        pandas_df.to_csv(buffer, sep=sep, quoting=csv.QUOTE_NONNUMERIC,encoding="utf-8",float_format=decimal)
        return buffer.getvalue()






