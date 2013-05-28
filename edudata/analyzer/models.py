import datetime
from django.utils import timezone
from django.db import models

"""
 This class represents generalized dataframe: it points to df file and it's codebook (description of the variables that are stored inside the dataframe) 
 FUTURE: It provides some metadata about the dataframe, e.i.  authors of the research, a questionnaire, link to publications that are connected to this dataframe, etc. (maybe it should be an XML file ? - it would be easy to add some new metadata without having to change whole model)
"""

class Dataframe(models.Model):
	name = models.CharField(max_length=200)
	def __unicode__(self):
		return(self.name)

	# This points to a file that contains the dataframe
	df = models.FileField(
		upload_to="data/%Y/%m/%d/dataframes",
		max_length=100,
	)
	
	description = models.CharField(max_length=100)
	
	# This points to a codebook that contains the description of variables in a dataframe
	codebook = models.FileField(
		upload_to="data/%Y/%m/%d/codebooks",
		max_length=100,
	)
	pub_date = models.DateTimeField('upload date', default=datetime.datetime.now())

	# Metadata - an XML file that contains additional information about that dataframe
	metadata = models.FileField(
		upload_to="data/%Y/%m/%d/metadata",
		max_length=100,
		blank = True,
	)	
