'''
planet database, saves the data in nested dictionaries.
Downloads, unpacks and "pickles" (saves a python binary) of the exoplanets.org

For exoplanets.org's parameter field keywords, see Table 1 of 
Wright et al. 2011: http://arxiv.org/pdf/1012.5676v3.pdf

Brett Morris
'''
import numpy as np
import os
from urllib import urlopen
from matplotlib import pyplot as plt
import pandas
from datetime import datetime

mplplot = False
bokehplot = False
mpld3plot = True

# Save the exoplanet.org database to the directory that this file is saved in
exodbPath = os.path.dirname(os.path.abspath(__file__))
csvDatabaseName = os.path.join(exodbPath,'exoplanets.csv')  

def lastupdate(path):
    t = os.path.getmtime(path)
    return datetime.fromtimestamp(t)

def download(csvDatabaseName=csvDatabaseName):
    '''
    If there's a previously archived database pickle in this current working 
    directory then use it, if not, grab the data from exoplanets.org in one big
    CSV file and make one. If the old archive is >14 days old, grab a fresh 
    version of the database from exoplanets.org.
    '''

    if not os.path.exists(csvDatabaseName):
        print 'No local copy of exoplanets.org database. Downloading one...'
        rawCSV = urlopen('http://www.exoplanets.org/csv-files/exoplanets.csv').read()
        saveCSV = open(csvDatabaseName,'w')
        saveCSV.write(rawCSV)
        saveCSV.close()
    else: 
        #If the local copy of the exoplanets.org database is >14 days old, 
        #download a new one
        timesincemod = datetime.now() - lastupdate(csvDatabaseName)
        Ndays = 7
        if timesincemod.days > Ndays:
            print('Your local copy of the exoplanets.org database is' + 
                  ' >{0} days old. Downloading a fresh one...'.format(Ndays))
            rawCSV = urlopen(
                  'http://www.exoplanets.org/csv-files/exoplanets.csv').read()
            saveCSV = open(csvDatabaseName,'w')
            saveCSV.write(rawCSV)
            saveCSV.close()
        else: 
            print('Your local copy of the exoplanets.org database is' + 
                  " <{0} days old. That'll do...".format(Ndays))
    return pandas.read_csv(csvDatabaseName)

def plottimestamp(axis, csvDatabaseName=csvDatabaseName, **kwargs):
    '''
    Add annotation to `axis` with the date of last exoplanets.org access
    '''
    t = lastupdate(csvDatabaseName).strftime('%Y-%m-%d')
    note = 'exoplanets.org\n{0}'.format(t)
    axis.annotate(note, xy=(0.02, 0.98), xycoords='axes fraction',
                  va='top', ha='left')

# Download/load exoplanets.org database
db = download()

# Filter out the calculated values -- use empirical measurements only
Mp_measured = db.MASSREF != 'estimated from radius; see EOD documentation'
Rp_measured = (~db.RREF.isnull()) & (db.RREF != 'Calculated')

bothmeasured = Mp_measured & Rp_measured

# Make a plot!
if mplplot:
    fig, ax = plt.subplots()
    ax.semilogx(db[bothmeasured].MASS, db[bothmeasured].R, '.')
    ax.set_xlabel('Log Mass [$M_J$]')
    ax.set_ylabel('Radius [$R_J$]')
    plottimestamp(ax)
    plt.show()

if bokehplot:
    
    from bokeh.plotting import ColumnDataSource, figure, output_file, show
    from bokeh.models import HoverTool
    
    # Create a set of tools to use
    TOOLS="pan,wheel_zoom,box_zoom,reset,hover"
    
    x, y = db[bothmeasured].MASS, db[bothmeasured].R
    N = len(x)
    inds = [str(i) for i in range(N)]
    #radii = np.random.random(size=N)*0.4 + 1.7
    names = db[bothmeasured].NAME
    
    source = ColumnDataSource(
        data=db[bothmeasured].to_dict('list')
    )
    
    output_file("scatter.html")
    p = figure(title="exoplanets.org ({0})".format(
               lastupdate(csvDatabaseName).strftime('%Y-%m-%d')), 
               tools=TOOLS,
               x_axis_label = "Mass [M_J]",
               y_axis_label = "Radius [R_J]")
    p.circle(x, y, source=source, #radius=1
             fill_alpha=0.6, line_color=None) # fill_color
    #p.text(x, y, text=inds, alpha=0.5, text_font_size="5pt",
    #       text_baseline="middle", text_align="center")
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [
        # add to this
        ("Planet", "@NAME"),
        ("Mass", "@MASS M_J"),
        ("Radius", "@R R_J"),
        ("Period", "@PER days"),
        ("T_eff", "@TEFF K"),
        #("fill color", "$color[hex, swatch]:fill_color"),
    ]
    show(p)
    
if mpld3plot:
    import mpld3

    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
    x, y = db[bothmeasured].MASS, db[bothmeasured].R
    N = len(x)
    scatter = ax.scatter(x, y,
                         c=np.random.random(size=N),
                         s=1000 * np.random.random(size=N),
                         alpha=0.3,
                         cmap=plt.cm.jet)
    ax.grid(color='white', linestyle='solid')
    
    ax.set_title("exoplanets.org ({0})".format(
               lastupdate(csvDatabaseName).strftime('%Y-%m-%d')), size=20)
    ax.set_xlabel('Mass [$M_J$]')
    ax.set_ylabel('Radius [$R_J$]')
    labels = list(db[bothmeasured].NAME)
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    
    mpld3.show()