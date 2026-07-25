# import required libraries
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import RobustScaler
from math import log as ln

print('\nreading in data')

#read in parquet data
sland = pd.read_parquet('data/parquets/scotland.parquet')
gland = pd.read_parquet('data/parquets/greenland.parquet')

# sland = pd.read_parquet('Output/Scotland_Sample_Data.parquet')
# gland = pd.read_parquet('Output/Greenland_Sample_Data.parquet')

datasets = [gland, sland]

# merge the two datasets
full_dataset = pd.concat(datasets, ignore_index=True)

print('\ncleaning and prepping data')

# define a function to scale continuous variables
def scale_data(df):
    categoricals = ['bedrock_metamorphic',
                 'bedrock_sedimentary',
                 'landscape classification_linear erosion',
                 'landscape classification_mountain valley',
                 'landscape classification_unmodified'
                 ]

    continuous = ['precipitation'
                ,'temperature']

    cats = df[categoricals]
    conts = df[continuous]
    scaler = RobustScaler()
    conts_scaled = scaler.fit_transform(conts)
    scaled_df = pd.DataFrame(conts_scaled, index=conts.index, columns=conts.columns)
    final_df = pd.concat([scaled_df, cats], axis=1)
    return final_df

# define a function to remove rows with missing values, transform values in 'time since deglaciation' column to float format,
# remove x, y and roughness variables, get dummy values for categorical variables and scale continuous variables
def prep_data(df):
    df = df.dropna()
    df['time since deglaciation'] = df['time since deglaciation'].astype(float)

    df['temperature'] = df['temperature'].astype(float)
    df['precipitation'] = df['precipitation'].astype(float)

    dropped = df.drop(['x', 'y', 'elevation', 'roughness_15', 'roughness_150', 'roughness_1500', 'roughness_3000'], axis=1)
    dummied = pd.get_dummies(dropped, dtype=float, drop_first=True)
    scaled = scale_data(dummied)
    return scaled

gxscaled = prep_data(gland)
sxscaled = prep_data(sland)
fullxscaled = prep_data(full_dataset)

gY15 = gland['roughness_15']
gY150 = gland['roughness_150']
gY1500 = gland['roughness_1500']
gY3000 = gland['roughness_3000']
sY15 = sland['roughness_15']
sY150 = sland['roughness_150']
sY1500 = sland['roughness_1500']
sY3000 = sland['roughness_3000']
fY15 = full_dataset['roughness_15']
fY150 = full_dataset['roughness_150']
fY1500 = full_dataset['roughness_1500']
fY3000 = full_dataset['roughness_3000']

def get_tsd_dict(data):
    data['time since deglaciation'] = data['time since deglaciation'].astype(float)
    tsd = list(data['time since deglaciation'].unique())
    tsd.sort()

    tsd_dict = {}

    for i in tsd:
        tsd_dict[i] = data[data['time since deglaciation'] == i]
    return tsd_dict

def prep_tsd(data):
    prepped_tsd = {}
    for key in data.keys():
        prepped_tsd[key] = prep_data(data[key])
    return prepped_tsd

def get_x(data):
    tsd_dict = get_tsd_dict(data)
    prepped_tsd = prep_tsd(tsd_dict)
    # scaled_tsd = scale_tsd(prepped_tsd)
    # return scaled_tsd
    return prepped_tsd

def get_vif(df):
    vif = pd.DataFrame()
    vif['Feature'] = df.columns
    vif['VIF'] = [variance_inflation_factor(df, i) for i in range(df.shape[1])]
    return vif

resolutions = ['15', '150', '1500', '3000']

def get_ys(data):
    ys = {}
    tsd_dict = get_tsd_dict(data)
    for res in resolutions:
        for key in tsd_dict.keys():
            ys[str(key) + 'y' + res] = tsd_dict[key]['roughness_' + res]
    return ys

def run_ols(df, dfy):
    df_constant = sm.add_constant(df)
    df_model = sm.OLS(dfy, df_constant).fit()
    return df_model

def partial_r_squared(df, dfy):
    values = []
    for item in list(df.columns):
        newdf = df.copy()
        if 'bedrock' in item:
            newdf.drop(['bedrock_metamorphic', 'bedrock_sedimentary'], axis=1, inplace=True)
        elif 'classification' in item:
            newdf.drop(['classification_linear erosion', 'classification_mountain valley', 'classification_unmodified'], axis=1, inplace=True)
        else:
            newdf.drop([item], axis=1, inplace=True)
        #newdf.drop([item], axis=1, inplace=True)
        ols = run_ols(newdf, dfy)
        rsquare = ols.rsquared_adj
        values.append(rsquare)
    return values

def get_model_summary(df, dfy, vif):
    model_results = run_ols(df, dfy)
    overall_r = model_results.rsquared_adj
    df_summary = model_results.params.drop('const')
    partial_r = partial_r_squared(df, dfy)
    new_vif = vif.copy()
    new_vif['OLS Correlation Coefficient'] = df_summary.to_frame().reset_index(drop=True)
    new_vif['Partial R'] = partial_r
    new_vif['Full R'] = overall_r
    new_vif['Partial R Squared'] = ((new_vif['Full R'] - new_vif['Partial R']) / (1 - new_vif['Partial R'])).round(4)
    # new_vif.drop(['VIF'], axis=1, inplace=True)
    return new_vif

# Workaround to avoid fixing the 27.0 dataset issue...
def get_model_summary_27(df, dfy, vif):
    model_results = run_ols(df, dfy)
    overall_r = model_results.rsquared_adj
    df_summary = model_results.params
    partial_r = partial_r_squared(df, dfy)
    new_vif = vif.copy()
    new_vif['OLS Correlation Coefficient'] = df_summary.to_frame().reset_index(drop=True)
    new_vif['Partial R'] = partial_r
    new_vif['Full R'] = overall_r
    new_vif['Partial R Squared'] = ((new_vif['Full R'] - new_vif['Partial R']) / (1 - new_vif['Partial R'])).round(4)
    # new_vif.drop(['VIF'], axis=1, inplace=True)
    return new_vif


# There's something odd going on here in that the 27.0 dataset doesn't generate a 'const' value. Not sure why. Have excluded it for now, but would be good to resolve.
def get_summaries(x_dataset, y_dataset, vif, resolutions=resolutions):
    summary_dict = {}
    for resolution in resolutions:
        if resolution == '15':
            for y in y_dataset.keys():
                if 'y150' not in y and 'y3000' not in y:
                    for x in x_dataset.keys():
                        if x == y[:-3] and x != '27.0':
                            summary_dict[x + '_' + resolution] = get_model_summary(x_dataset[x], y_dataset[y], vif)
                        elif x == y[:-3] and x == '27.0':
                            summary_dict[x + '_' + resolution] = get_model_summary_27(x_dataset[x], y_dataset[y], vif)
        elif resolution == '150':
            for y in y_dataset.keys():
                if 'y150' in y and 'y1500' not in y and 'y3000' not in y:
                    for x in x_dataset.keys():
                        if x == y[:-4] and x != '27.0':
                            summary_dict['+' + x + '_' + resolution] = get_model_summary(x_dataset[x], y_dataset[y], vif)
                        elif x == y[:-4] and x == '27.0':
                            summary_dict[x + '_' + resolution] = get_model_summary_27(x_dataset[x], y_dataset[y], vif)
        elif resolution == '1500':
            for y in y_dataset.keys():
                if 'y1500' in y:
                    for x in x_dataset.keys():
                        if x == y[:-5] and x != '27.0':
                            summary_dict['*' + x + '_' + resolution] = get_model_summary(x_dataset[x], y_dataset[y], vif)
                        elif x == y[:-5] and x == '27.0':
                            summary_dict[x + '_' + resolution] = get_model_summary_27(x_dataset[x], y_dataset[y], vif)
        else:
            for y in y_dataset.keys():
                if 'y15' not in y:
                    for x in x_dataset.keys():
                        if x == y[:-5] and x != '27.0':
                            summary_dict['_' + x + '_' + resolution] = get_model_summary(x_dataset[x], y_dataset[y], vif)
                        elif x == y[:-5] and x == '27.0':
                            summary_dict[x + '_' + resolution] = get_model_summary_27(x_dataset[x], y_dataset[y], vif)
    return summary_dict

def mega_summary(data):
    x = get_x(data)
    tsd = list(data['time since deglaciation'].unique())
    tsd.sort()
    vif = get_vif(x[str(tsd[0])])
    y = get_ys(data)
    summaries = get_summaries(x, y, vif=vif)
    return summaries

def extract_r2(dataset, filename):
    # Create a new dataframe to hold the summary data
    data = pd.DataFrame()

    # Add columns for time since deglaciation and resolution
    data['time'] = []
    data['resolution'] = []
    single_key = list(dataset.keys())[0]

    # Add columns for each variable
    for v in range(len(dataset[single_key]['Feature'])):
        data[dataset[single_key]['Feature'][v]] = []

    # Iterate through each list in the dictionary and pull out the values of R2, then add them to the dataframe
    for i in range(len(dataset)):
        # Extract the dictionary key
        key = list(dataset.keys())[i]
        # Use the key to pull out the R2 values for each variable
        r2_data = [dataset[key]['Partial R Squared'].iloc[v] for v in range(len(dataset[key]['Feature']))]
        # Get rid of characters at start of key
        key_stripped = key.lstrip('+*_')
        # Add row to dataframe including appropriately formatted values for time and resolution columns
        data.loc[len(data)] = [float(key_stripped.split('_')[0]), float(key_stripped.split('_')[1])] + r2_data
    
    return data

gland_summary = mega_summary(gland)
sland_summary = mega_summary(sland)
massive_summary = mega_summary(full_dataset)

gr2 = extract_r2(gland_summary, 'gland')
sr2 = extract_r2(sland_summary, 'sland')
mr2 = extract_r2(massive_summary, 'massive')

def f(row):
    if row['resolution'] == 15.0:
        val = 'red' 
    elif row['resolution'] == 150.0:
        val = 'yellow'
    elif row['resolution'] == 1500.0:
        val = 'green'
    else:
        val = 'blue'
    return val

def add_colours(dataset):
    dataset['colour'] = dataset.apply(f, axis=1)
    return dataset

add_colours(gr2)
add_colours(sr2)
add_colours(mr2)

gr2_15, gr2_150, gr2_1500, gr2_3000 = gr2[gr2['resolution'] == 15.0], gr2[gr2['resolution'] == 150.0], gr2[gr2['resolution'] == 1500.0], gr2[gr2['resolution'] == 3000.0]
sr2_15, sr2_150, sr2_1500, sr2_3000 = sr2[sr2['resolution'] == 15.0], sr2[sr2['resolution'] == 150.0], sr2[sr2['resolution'] == 1500.0], sr2[sr2['resolution'] == 3000.0]
mr2_15, mr2_150, mr2_1500, mr2_3000 = mr2[mr2['resolution'] == 15.0], mr2[mr2['resolution'] == 150.0], mr2[mr2['resolution'] == 1500.0], mr2[mr2['resolution'] == 3000.0]

mr2['landscape classification'] = mr2['classification_linear erosion']

rows = mr2[mr2['time'] > 18].index
mr2pruned = mr2.drop(rows)
mr2pruned

mr2pruned_15, mr2pruned_150, mr2pruned_1500, mr2pruned_3000 = mr2pruned[mr2pruned['resolution'] == 15.0], mr2pruned[mr2pruned['resolution'] == 150.0].reset_index(drop=True), mr2pruned[mr2pruned['resolution'] == 1500.0].reset_index(drop=True), mr2pruned[mr2pruned['resolution'] == 3000.0].reset_index(drop=True)

pruned_dataframes = [mr2pruned_15, mr2pruned_150, mr2pruned_1500, mr2pruned_3000]

fig, axs = plt.subplots(1, 2, layout='constrained', figsize=(16, 8), sharey=True
)

plt.rcParams.update({'font.size': 20})

ax1, ax2 = axs[0], axs[1]

ax1.annotate('a', xy=(0.95, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')
ax2.annotate('b', xy=(0.95, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')

x = 'time'
y = 'precipitation'
z = 'landscape classification'
#z = 'classification_mountain valley'
colours = ['red', 'yellow', 'green', 'blue']


def plotit(axa, axb, dataseta, datasetb):
    axa.scatter(dataseta[x], dataseta[z], c=dataseta['colour'], edgecolor='k', lw=0.5, zorder=5)
    axb.scatter(datasetb[x], datasetb[y], c=datasetb['colour'], edgecolor='k', lw=0.5, zorder=5)
    axa.grid(alpha=0.5, zorder=-1)
    axb.grid(alpha=0.5, zorder=-1)

plotit(ax1, ax2, mr2pruned, mr2pruned)

tsd = list(mr2['resolution'].unique())
tsd.sort()

patches = []

for i in range(len(tsd)):
    patches.append(mpatches.Patch(color=colours[i], label=tsd[i]))

ax2.legend(handles=patches, title='Scale (m)', fontsize='small')

ax1.set_title('Landscape Classification')
ax2.set_title('Total Annual Precipitation (mm)')

plt.rc('xtick', labelsize=20) 
plt.rc('ytick', labelsize=20) 

fig.supylabel('Partial $R^2$', fontsize=25)
fig.supxlabel('Time since deglaciation (thousand years)', fontsize=25)

plt.savefig('figures/precipitation_vs_classification.png', dpi=300)

svif = get_vif(sxscaled)
gvif = get_vif(gxscaled)
mvif = get_vif(mxscaled)

summarym15 = get_model_summary(mxscaled, mY15, mvif)
summarym150 = get_model_summary(mxscaled, mY150, mvif)
summarym1500 = get_model_summary(mxscaled, mY1500, mvif)
summarym3000 = get_model_summary(mxscaled, mY3000, mvif)

summaryg15 = get_model_summary(gxscaled, gY15, gvif)
summaryg150 = get_model_summary(gxscaled, gY150, gvif)
summaryg1500 = get_model_summary(gxscaled, gY1500, gvif)
summaryg3000 = get_model_summary(gxscaled, gY3000, gvif)
summarys15 = get_model_summary(sxscaled, sY15, svif)
summarys150 = get_model_summary(sxscaled, sY150, svif)
summarys1500 = get_model_summary(sxscaled, sY1500, svif)
summarys3000 = get_model_summary(sxscaled, sY3000, svif)

def getr2forclassification(scale):
    totalr2 = scale['Partial R Squared'][4] + scale['Partial R Squared'][5] + scale['Partial R Squared'][6]
    return totalr2.round(3)

getr2forclassification(summarys3000)

greenland = [summaryg15, summaryg150, summaryg1500, summaryg3000]
scotland = [summarys15, summarys150, summarys1500, summarys3000]
precipitation = [0]
temperature = [1]
climate = [0, 1]
bedrock = [2, 3]
classification = [4, 5, 6]

def get_avg(area, variables):
    R2 = 'Partial R Squared'
    mean = 0
    for variable in variables:
        mean += (area[0][R2][variable] + area[1][R2][variable] + area[2][R2][variable] + area[3][R2][variable]) / 4
    return mean.round(3)

mean_values = pd.DataFrame({'Region': ['Greenland', 'Scotland'], 
'Precipitation': [get_avg(greenland, precipitation), get_avg(scotland, precipitation)],
'Temperature': [get_avg(greenland, temperature), get_avg(scotland, temperature)],
'Climate': [get_avg(greenland, climate), get_avg(scotland, climate)],
'Bedrock': [get_avg(greenland, bedrock), get_avg(scotland, bedrock)],
'Classification': [get_avg(greenland, classification), get_avg(scotland, classification)]})

summaries = [summarys15, summaryg15, summarys150, summaryg150, summarys1500, summaryg1500, summarys3000, summaryg3000]

for summary in summaries:
    summary.loc[len(summary)] = ['landscape\nclassification', 'Nan', 'Nan', 'Nan', 'Nan', summary['Partial R Squared'][4]]
    summary.loc[len(summary)] = ['bedrock', 'Nan', 'Nan', 'Nan', 'Nan', summary['Partial R Squared'][2]]
    summary.drop([2, 3, 4, 5, 6], inplace=True)

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20), sharex=True, 
                         #sharey=True, 
                         layout='constrained')
plt.rcParams.update({'font.size': 20})

ax1 = axes[0, 0]
ax1.annotate('15 m', xy=(0.82, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')
ax2 = axes[0, 1]
ax2.annotate('150 m', xy=(0.82, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')
ax3 = axes[1, 0]
ax3.annotate('1500 m', xy=(0.82, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')
ax4 = axes[1, 1]
ax4.annotate('3000 m', xy=(0.82, .95), xycoords='axes fraction', fontsize=20, fontweight='bold')

variables = (summaryg15['Feature'])
r2values = {
    'Greenland': (summaryg15['Partial R Squared']),
    'Scotland': (summarys15['Partial R Squared'])
}

x = np.arange(len(variables))  # the label locations
width = 0.25  # the width of the bars
offset = 0.25

def plotsy(ax, df1, df2):
    ax.bar(x, df1['Partial R Squared'], width, zorder=5, edgecolor='k')
    ax.bar(x + offset, df2['Partial R Squared'], width, zorder=5, edgecolor='k')
    ax.set_xticks(x + width, variables)

plotsy(ax1, summaryg15, summarys15)
plotsy(ax2, summaryg150, summarys150)
plotsy(ax3, summaryg1500, summarys1500)
plotsy(ax4, summaryg3000, summarys3000)

axes = [ax1, ax2, ax3, ax4]

for ax in axes:
    ax.grid(alpha=0.5, zorder=-1)
    ax.tick_params('x', rotation=90)

ax2.legend(['Greenland', 'Scotland'
            #, 'North Greenland', 'South Greenland'
            ]#, loc='center right'
            )

plt.rc('xtick', labelsize=20) 
plt.rc('ytick', labelsize=20) 

fig.supxlabel('Variable', fontsize=25)
fig.supylabel('Partial $R^2$', fontsize=25)

plt.savefig('figures/Partial_R2.png', dpi=300)

test = massive.groupby(by='time since deglaciation').sum()
test.drop(['x', 'y', 'elevation', 'roughness_15', 'roughness_150', 'roughness_1500', 'roughness_3000', 'precipitation', 'temperature', 'bedrock_metamorphic', 'bedrock_sedimentary'], axis=1, inplace=True)
test['total'] = count['x']
test.columns = ['Linear Erosion', 'Mountain Valley', 'Unmodified', 'Total']
test['Areal Scour'] = test['Total'] - (test['Linear Erosion'] + test['Mountain Valley'] + test['Unmodified'])
plotty = test.drop('Total', axis=1)
plotty['Time since deglaciation (kya)'] = plotty.index
fig = plotty.plot(x='Time since deglaciation (kya)', kind='bar', stacked=True, figsize=(17, 17), zorder=5, edgecolor='k')

fig.grid(alpha=0.5, zorder=-1)

plt.rc('xtick', labelsize=20) 
plt.rc('ytick', labelsize=20) 

fig.set_xlabel('Time since deglaciation (thousand years)', fontsize=25)
fig.set_ylabel('Number of points', fontsize=25)

plt.savefig('figures/tsd_vs_classification.png', dpi=300)