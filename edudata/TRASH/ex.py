
variables =[0,2,4]# request.POST.getlist('choice')
	if variables:
        	reader = csv.read(df.df,delimiter=';')
                header = ['a','b','c','d','e']
                columns = dict()
                for cnt, colname in enumerate(header):
                	if cnt in variables:
                        	columns[colname] = []
                        else:
                        	#do nothing
                                pass
		reader = [[1,2,3,4,5],[5,4,3,2,1],[1,2,3,4,5]]
		for lnumber, line in enumerate(reader):
                	for colnum , col in enumerate(line):
                        	if colnum in variables:
                                	columns[header[colnum]].append(col)
                                else:
                                	pass
	return render_to_response('analyzer/dataframe/plot.html',
                                                        { 'dataframe' : df,
                                                          'vars' : variables,
                                                          'columns' : columns, },
                                                        context_instance=RequestContext(request))
        else:
		return render_to_response('analyzer/dataframe/plot.html',
                                                                { 'dataframe' : df,
                                                                  'error_message': "No variables passed to plot",}
                                                                context_instance=RequestContext(request))


