import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import cStringIO
import matplotlib.pyplot as plt
import pandas
import numpy as np



labels = ['a', 'b', 'c', 'd', 'e']
s = pandas.Series(np.random.randn(5), index=labels)
fig = plt.figure()
ax = fig.add_subplot(111)
s.plot(ax=ax)
canvas = FigureCanvas(fig)
output = cStringIO.StringIO()
canvas.print_png(output)
output.read()
output.flush()
canvas.print_png(output)
output.seek(0)
output.read()

_ip.magic("save aa.py 1-23")
