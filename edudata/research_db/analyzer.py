import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import cStringIO
import matplotlib.pyplot as plt
import pandas as pd

class Analyzer:
	def __init__(self,json_var):
		self.var = pd.read_json(json_var,typ='series')

	def histogram(self):
		fig = plt.figure()
		ax = fig.add_subplot(111)
		self.var.hist(ax=ax)
		canvas = FigureCanvas(fig)
		output = cStringIO.StringIO()
		canvas.print_png(output)
		output.seek(0)
		return output.read()
