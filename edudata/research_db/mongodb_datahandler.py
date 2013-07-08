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

    def mongodb_prepare(self,cb_reader, pandas_df, df_name):
        data = dict()
        data['df_name'] = df_name
        data['columns'] = []
        for nr,row in enumerate(cb_reader):
            column = dict()
            
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
                
                column['data'] = dict((str(key), value) for (key, value) in var_data.items()) 
            except KeyError:
                e= "Failed to locate '{}' var in {} df columns ".format(column['name'], pandas_df.columns)
                raise KeyError, e
            data['columns'].append(column)
            
        return data

    def process_data(self, df_name, codebook, df):
        #codebook = open("codebook.csv", "r")
        #df = open ("df.csv","r")
        cb_reader = csv.reader(codebook, delimiter = ';', quotechar = '"')
        cb_reader.next() ## skip the header of the codebook!
        data_reader =  csv.reader(df,delimiter=";",quotechar='"')
        data_header = data_reader.next() ## get header
        df_rows = [row for row in data_reader]                 
        pandas_df = psDataFrame(df_rows,columns=data_header)
        insert_query  =self.mongodb_prepare(cb_reader,pandas_df, df_name)
        dataframes = self.db.dataframes
        status = dataframes.insert(insert_query)
        return status


    def get_dataframe(self,df_name):
        cursor = self.db.dataframes.find({'df_name':df_name})
        df = cursor.next()
        dfdict = dict()
        rownames = []
        

        # TU MUSI BYĆ SORTOWANIE po kluczu i to kluczu INTEGER!!
        for nr,column in enumerate(df['columns']): # type(df['columns']) == type([])
            #print column['name'], " - ",nr
            if nr == 0:
                rownames = column['data'].keys()

            #TODO konwersja na liczby calkowite /zmiennoprzecinkowe - mongdoDB standradowo trzyma WSZYSTKO jako tekst
            rows = dict((int(key), value) for (key, value) in column['data'].items()) 
            dfdict[column['name']] = [value for (key,value) in rows.iteritems()]
    
        return psDataFrame(dfdict, index = rownames )

    def get_csv(self, df_name,sep,decimal):
        pandas_df = self.get_dataframe(df_name)
        buffer = StringIO.StringIO()
        
        pandas_df.to_csv(buffer, sep=sep, quoting=csv.QUOTE_NONNUMERIC,encoding="utf-8",float_format=decimal)
        return buffer.getvalue()
            #data.append(columns['data'])
            
        
    #client = MongoClient()
    #db = client.dataframes
    #process_data(db)





