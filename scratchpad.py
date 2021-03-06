
'''
#Default
selected_datasets = []
colors = cycle(['red', 'blue', 'green', 'orange'])

#load the saved plots from file
savedPlots = json.load(open("savedPlots.json"))

def determine(data):
if data is None:
return False;
else:
return True;

def allowed_file(filename):
return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getSavedPlots():
plots = savedPlots
return plots

def getSimplifiedPlot():
plot = figure(
title='Simplified Model Plane',
tools='wheel_zoom, pan, save',
toolbar_location="above",
x_axis_label='mMed',
x_axis_type="log",
y_axis_label="mDM",
y_axis_type="log",
plot_width=500,
plot_height=500,
)
plot.title.text_font_size = "1.2em"
plot.xaxis.axis_label_text_font_size = "14pt"
plot.yaxis.axis_label_text_font_size = "14pt"
return plot

def getDDPlot():
plot = figure(
title='Direct Detection Plane',
tools='wheel_zoom, pan, save',
toolbar_location="above",
x_axis_label='mDM',
x_axis_type="log",
#y_axis_label="$\sigma_{DM}$ (cross-section)",
y_axis_label="σDM (cross-section)",
y_axis_type="log",
plot_width=500,
plot_height=500,
)
plot.title.text_font_size = "1.2em"
plot.xaxis.axis_label_text_font_size = "14pt"
plot.yaxis.axis_label_text_font_size = "14pt"
return plot

def getLegendPlot():
legendPlot = figure(
plot_width=500,
plot_height=250,
tools="",
toolbar_location=None
)
legendPlot.axis.visible = False
legendPlot.xgrid.visible = False
legendPlot.ygrid.visible = False
legendPlot.outline_line_color = None
return legendPlot

@app.route('/')
def main():
return redirect('/index')

@app.route('/updateValues', methods=['GET', 'POST'])
def updateValues():
gSM_refresh = Set_gSM_Form()
gSM = gSM_refresh.gSM_input.data
set_gSM(gSM,gSM,gSM)
#Future: Individually set coupling constant
#gU = gSM_refresh.gU_input.data
#gD = gSM_refresh.gD_input.data
#gS = gSM_refresh.gS_input.data
#set_gSM(gU,gD,gS)
return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
return render_template('index.html')

@app.route('/dmplotter', methods=['GET', 'POST'])
def dmplotter():
known_datasets = get_datasets()
gu, gd, gs = get_gSM()
si_modifier = get_SI_modifier()

#Generate Array of options
options = list(getSavedPlots().keys())

dataset_selection = DatasetForm(gSM_input=gu)
dataset_selection.datasets.choices = zip(get_datasets(), get_datasets())
dataset_selection.savedPlots.choices = zip(options, options)
dataset_upload = UploadForm()

global selected_datasets

if request.method == 'POST':
# check if the post request has the file part
# print(request.values, request.data, request.form)
print(dataset_selection.datasets.data)
if dataset_selection.validate():
selected_datasets = dataset_selection.datasets.data
gSM = dataset_selection.gSM_input.data
set_gSM(gSM,gSM,gSM)
gu, gd, gs = get_gSM()
si_modifier = dataset_selection.radio_inputSI.data
set_SI_modifier(si_modifier)

datasets = selected_datasets
dfs = map(get_data, datasets)

#Filter, TODO: Apply filter to selected_datasets prior to conversion (attempt)
#get_data will return a 'None' object if the selected dataset could not be converted, (bad experiement string..)
dfs = [x for x in dfs if determine(x)]

metadata = map(get_metadata, datasets)
allmetadata = map (get_metadata,known_datasets)

p1 = getSimplifiedPlot()
p2 = getDDPlot()
legendPlot = getLegendPlot()

legendItems = []
x = 1
y = 2*x
for df, color in zip(dfs, colors):
label = df['label'].any()
df['color'] = color
p1.line(df['m_med'], df['m_DM'], line_width=2, color=color)
p2.line(df['m_DM'], df['sigma'], line_width=2, color=color)
line = legendPlot.line(x,y,line_width=2, color=color)
legendItems.append((label,[line]))

#Initialize all_data in the case that all datasets selected where invalid
all_data = pd.DataFrame()
if(len(dfs) > 0):
all_data = pd.concat(dfs)

legend = Legend(items=legendItems, location=(0, 0))
legendPlot.add_layout(legend, 'above')

script1, div1 = components(p1, CDN)
script2, div2 = components(p2, CDN)
script3, div3 = components(legendPlot,CDN)
return render_template('dmplotter.html',
plot_script1=script1, plot_div1=div1,
plot_script2=script2, plot_div2=div2,
plot_script3=script3, plot_div3=div3,
bokeh_version=bokeh.__version__,
data_table=all_data.to_html(),
datasets = known_datasets,
metadata = metadata,
dataset_selection = dataset_selection,
selected_datasets = selected_datasets,
allmetadata = allmetadata,
savedPlots = getSavedPlots(),
dataset_upload = dataset_upload,
si_modifier = si_modifier,
gSM_gSM=gu,
gSM_gU=gu,gSM_gD=gd,gSM_gS=gs)

@app.route('/pdf', methods=['GET', 'POST'])
def pdf():
gu, gd, gs = get_gSM()
si_modifier = get_SI_modifier()

global selected_datasets
#Will re-use the previously selected values for the dataset
#Optional: provide dataset files in the post parameters
if request.method == 'POST':
print('Use this area to parse for posted datasets');

datasets = selected_datasets

dfs = map(get_data, datasets)
dfs = [x for x in dfs if determine(x)]
metadata = map(get_metadata, datasets)

p1 = getSimplifiedPlot()
p2 = getDDPlot()
legendPlot = getLegendPlot()

legendItems = []
x = 1
y = 2*x
for df, color in zip(dfs, colors):
label = df['label'].any()
df['color'] = color
p1.line(df['m_med'], df['m_DM'], line_width=2, color=color)
p2.line(df['m_DM'], df['sigma'], line_width=2, color=color)
line = legendPlot.line(x,y,line_width=2, color=color)
legendItems.append((label,[line]))

#Initialize all_data in the case that all datasets selected where invalid
all_data = pd.DataFrame()
if(len(dfs) > 0):
all_data = pd.concat(dfs)

legend = Legend(items=legendItems, location=(0, 0))
legendPlot.add_layout(legend, 'above')

script1, div1 = components(p1, CDN)
script2, div2 = components(p2, CDN)
script3, div3 = components(legendPlot,CDN)
#ToDo: Turn this render_template into a PDF file and download
html = render_template('pdf.html',
plot_script1=script1, plot_div1=div1,
plot_script2=script2, plot_div2=div2,
plot_script3=script3, plot_div3=div3,
bokeh_version=bokeh.__version__,
data_table=all_data.to_html(),
metadata = metadata,
si_modifier = si_modifier,
gSM_gSM=gu)
return html

@app.route('/savePlot', methods=['GET', 'POST'])
def savePlot():
global savedPlots

savedPlotName = request.form['name']
selected_datasets = request.form['data'].split(",")

#Save to local copy and then flush to disk
savedPlots[savedPlotName] = selected_datasets
with open('savedPlots.json', 'w') as f:
json.dump(savedPlots, f)
return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
form = UploadForm(CombinedMultiDict((request.files, request.form)))
if form.validate_on_submit():
f = form.data_file.data
filename = secure_filename(f.filename)
t = form.radio_inputType.data
session[filename] = t
f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
return redirect(url_for('index'))
'''


<div class="row justify-content-start" style="margin-top:5%;">
 <div class="col justify-content-center">
   <h3>Login to View Datasets</h3>
   <a id="loginBtn" href={{ url_for('user.login') }} class="btn btn-outline-primary plotBtn">Login</a>
   <a id="registerBtn" href={{ url_for('user.register') }} class="btn btn-outline-primary plotBtn">Register Account</a>
 </div>
</div>
