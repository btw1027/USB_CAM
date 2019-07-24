import numpy
from matplotlib import pyplot as plt
import PySpin
from datetime import datetime
import os
import math

class LineDrawer(object):
    lines = []
    def draw_line(self):
        ax = plt.gca()
        xy = plt.ginput(2)        
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        print(x)
        line = plt.plot(x,y)
        ax.figure.canvas.draw()
        self.lines.append(line)
        distance = math.sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2)
        distance_s = '%4.3f' % distance
        bbox_props = dict(boxstyle="round,pad=0.3", ec="b", lw=2)
        t = ax.text(0, 0, 'The distance is '+distance_s+' px', ha="center", va="center", size=15,bbox=bbox_props)
        ax.annotate('The distance is '+distance_s+' px', (0,0), horizontalalignment='right', verticalalignment='top')
        print('The distance in pixels is %4.3f' % distance)

fig, current_ax = plt.subplots(figsize=(10,10))             
ld = LineDrawer()
ld.draw_line() # here you click on the plot
plt.show()