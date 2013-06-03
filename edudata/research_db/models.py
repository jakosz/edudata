import datetime
from django.utils import timezone
from django.db import models

"""
 This class represents generalized dataframe: it points to df file and it's codebook (description of the variables that are stored inside the dataframe) 
 FUTURE: It provides some metadata about the dataframe, e.i.  authors of the research, a questionnaire, link to publications that are connected to this dataframe, etc. (maybe it should be an XML file ? - it would be easy to add some new metadata without having to change whole model)
"""

class ResearchProject(models.Model):
    name = models.CharField(max_length=200)
    subcontractor = models.CharField(max_length=200)
    team = models.CharField(max_length=100)

    def __unicode__(self):
            return(self.name)



class DataFrame(models.Model):
    name = models.CharField(max_length=200)
    
    research_project = models.ForeignKey(ResearchProject)
    
    observation_unit = models.CharField(max_length=200) # TODO: Zdecydowac czy ENUM czy TEXT
    
    df = models.FileField(
            upload_to="data/%Y/%m/%d/dataframes",
            max_length=100,
    )

    codebook = models.FileField(
            upload_to="data/%Y/%m/%d/codebooks",
            max_length=100,
    )

    metadata = models.FileField(
            upload_to="data/%Y/%m/%d/metadata",
            max_length=100,
            blank = True
    )


