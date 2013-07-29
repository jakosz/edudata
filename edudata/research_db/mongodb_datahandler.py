# -*- coding:utf-8 -*-
import csv
import StringIO
import json
from pandas import DataFrame as psDataFrame
from pymongo import MongoClient



class MongoHandler:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.research_data

    def mongodb_insert_columns(self,cb_reader, pandas_df, df_name):
        dataframes = self.db.dataframes
        for nr,row in enumerate(cb_reader):
            column = dict()
            column['df_name'] = df_name
            #data[df_name] = 
            #data[var_name] = dict()
            #data[var_name]['df_name']=df_name        
            #print row
            column['name'],column['desc_short'], column['desc_long'],\
                column['keywords'], column['type'],\
                column['scale'], column['value_len'],\
                column['precision'], column['min_value'],\
                column['max_value'], column['labels'],column['condition'] = row
                
            try:
                var_data = pandas_df[ column['name'] ].to_dict()
                
                column['data'] = dict((unicode(key), value) for (key, value) in var_data.items()) 
            except KeyError:
                e= "Failed to locate '{}' var in {} df columns ".format(column['name'], pandas_df.columns)
                raise KeyError, e
            dataframes.insert(column)
            #data['columns'].append(column)
            

    def process_data(self, df_name, codebook, df):
        #codebook = open("codebook.csv", "r")
        #df = open ("df.csv","r")
        cb_reader = csv.reader(codebook, delimiter = ';', quotechar = '"')
        cb_reader.next() ## skip the header of the codebook!
        data_reader =  csv.reader(df,delimiter=";",quotechar='"')
        data_header = data_reader.next() ## get header
        df_rows = [row for row in data_reader] 
        pandas_df = psDataFrame(df_rows,columns=data_header)
        self.mongodb_insert_columns(cb_reader,pandas_df, df_name)
        #dataframes = self.db.dataframes
        #status = dataframes.insert(insert_query)


    def get_dataframe_and_info(self,df_name):
        cursor = self.db.dataframes.find({'df_name':df_name})
        df = cursor.next()
        dfdict = dict()
        rownames = []
        info = dict()
        # TU MUSI BYĆ SORTOWANIE po kluczu i to kluczu INTEGER!!
        for nr,column in enumerate(df['columns']): # type(df['columns']) == type([])
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
                pass
        # return dictionary for views.py
        return {'info':info,'df': psDf}

    def get_csv(self, df_name,sep,decimal):
        pandas_df = self.get_dataframe(df_name)["df"] # get only DataFrame
        buffer = StringIO.StringIO()
        pandas_df.to_csv(buffer, sep=sep, quoting=csv.QUOTE_NONNUMERIC,encoding="utf-8",float_format=decimal)
        return buffer.getvalue()






