import os
import nibabel as nb
import numpy as np
import pandas as pd
import regex as re
import matplotlib.pyplot as plt
from nilearn.plotting.displays import PlotlySurfaceFigure
import plotly.graph_objs as go
from mne.transforms import apply_trans


AXIS_CONFIG = {
    "showgrid": False,
    "showline": False,
    "ticks": "",
    "title": "",
    "showticklabels": False,
    "zeroline": False,
    "showspikes": False,
    "spikesides": False,
    "showbackground": False,
}

LAYOUT = {
	"scene": {f"{dim}axis": AXIS_CONFIG for dim in ("x", "y", "z")},
	"paper_bgcolor": "#fff",
	"hovermode": False,
	"showlegend":True,
	"legend":{
		"itemsizing": "constant",
		"groupclick":"togglegroup",
		"yanchor":"top",
		"y":0.8,
		"xanchor":"left",
		"x":0.05,
		"title_font_family":"Times New Roman",
		"font":{
			"size":20
		},
		"bordercolor":"Black",
		"borderwidth":1
	},
	"margin": {"l": 0, "r": 0, "b": 0, "t": 0, "pad": 0},
}

CAMERAS = {
    "left": {
        "eye": {"x": -1.5, "y": 0, "z": 0},
        "up": {"x": 0, "y": 0, "z": 1},
        "center": {"x": 0, "y": 0, "z": 0},
    },
    "right": {
        "eye": {"x": 1.5, "y": 0, "z": 0},
        "up": {"x": 0, "y": 0, "z": 1},
        "center": {"x": 0, "y": 0, "z": 0},
    },
    "dorsal": {
        "eye": {"x": 0, "y": 0, "z": 1.5},
        "up": {"x": 0, "y": 1, "z": 0},
        "center": {"x": 0, "y": 0, "z": 0},
    },
    "ventral": {
        "eye": {"x": 0, "y": 0, "z": -1.5},
        "up": {"x": 0, "y": 1, "z": 0},
        "center": {"x": 0, "y": 0, "z": 0},
    },
    "anterior": {
        "eye": {"x": 0, "y": 1.5, "z": 0},
        "up": {"x": 0, "y": 0, "z": 1},
        "center": {"x": 0, "y": 0, "z": 0},
    },
    "posterior": {
        "eye": {"x": 0, "y": -1.5, "z": 0},
        "up": {"x": 0, "y": 0, "z": 1},
        "center": {"x": 0, "y": 0, "z": 0},
    },
}

lighting_effects = dict(ambient=0.4, diffuse=0.5, roughness = 0.9, specular=0.6, fresnel=0.2)

def determine_groups(iterable, numbered_labels=False):
	values = []
	for item in iterable:
		temp=None
		if re.findall(r"([a-zA-Z]+)([0-9]+)([a-zA-Z]+)", item):
			temp = "".join(list(re.findall(r"([a-zA-Z]+)([0-9]+)([a-zA-Z]+)", item)[0]))
		elif '-' in item:
			temp=item.split('-')[0]
		else:
			if numbered_labels:
				temp=''.join([x for x in item if not x.isdigit()])
				for sub in ("T1","T2"):
					if sub in item:
						temp=item.split(sub)[0] + sub
			else:
				temp=item
		if temp is None:
			temp=item
		
		values.append(temp)
	
	vals,indexes,count = np.unique(values, return_index=True, return_counts=True)
	vals=vals[indexes.argsort()]
	count=count[indexes.argsort()]
	return vals,count

def get_vox2ras_tkr(img):
	'''Get the vox2ras-tkr transform. Inspired
	by get_vox2ras_tkr in
	'''
	ds = img.header.get_zooms()[:3]
	ns = np.array(img.shape[:3]) * ds / 2.0
	v2rtkr = np.array([[-ds[0], 0, 0, ns[0]],
					   [0, 0, ds[2], -ns[2]],
					   [0, -ds[1], 0, ns[1]],
					   [0, 0, 0, 1]], dtype=np.float32)
	return v2rtkr

hemi = ["lh", "rh"]
surf_suffix = ["pial", "white", "inflated"]

def readRegMatrix(trsfPath):
	with open(trsfPath) as (f):
		return np.loadtxt(f.readlines())

#%%


debug = True
if debug:
	class dotdict(dict):
		"""dot.notation access to dictionary attributes"""
		__getattr__ = dict.get
		__setattr__ = dict.__setitem__
		__delattr__ = dict.__delitem__
	
	class Namespace:
		def __init__(self, **kwargs):
			self.__dict__.update(kwargs)
	
	isub="166"
	datap=r'/home/arun/Documents/data/seeg/derivatives'
	
	input=dotdict({
		't1_fname':datap+f'/fastsurfer/sub-P{isub}/mri/orig.mgz',
		'fcsv':datap+ f'/seeg_coordinates/sub-P{isub}/sub-P{isub}_space-native_SEEGA.tsv',
		'xfm_noncontrast':datap+f'/atlasreg/sub-P{isub}/sub-P{isub}_desc-rigid_from-noncontrast_to-contrast_type-ras_xfm.txt',
	})
	
	output=dotdict({
		'html':datap+f'/atlasreg/sub-P{isub}/qc/sub-P{isub}_space-native_electrodes.html',
	})
	
	params=dotdict({
		'lh_pial':datap+f'/fastsurfer/sub-P{isub}/surf/lh.pial',
		'rh_pial':datap+f'/fastsurfer/sub-P{isub}/surf/rh.pial',
		'lh_sulc':datap+f'/fastsurfer/sub-P{isub}/surf/lh.sulc',
		'rh_sulc':datap+f'/fastsurfer/sub-P{isub}/surf/rh.sulc',
	})

	snakemake = Namespace(output=output, input=input,params=params)

t1_obj = nb.load(snakemake.input.t1_fname)
Torig = get_vox2ras_tkr(t1_obj)
fs_transform=np.dot(t1_obj.affine, np.linalg.inv(Torig))

verl,facel=nb.freesurfer.read_geometry(snakemake.params.lh_pial)
verr,facer=nb.freesurfer.read_geometry(snakemake.params.rh_pial)

all_ver = np.concatenate([verl, verr], axis=0)
all_face = np.concatenate([facel, facer+verl.shape[0]], axis=0)
surf_mesh = [all_ver, all_face]

all_ver_shift=(apply_trans(fs_transform, all_ver))

if len(snakemake.input.xfm_noncontrast)>0:
	if os.path.exists(snakemake.input.xfm_noncontrast):
		t1_transform=readRegMatrix(snakemake.input.xfm_noncontrast)
		#all_ver_shift=(apply_trans(np.linalg.inv(t1_transform), all_ver_shift))
		all_ver_shift=(apply_trans(t1_transform, all_ver_shift))


lh_sulc_data = nb.freesurfer.read_morph_data(snakemake.params.lh_sulc)
rh_sulc_data = nb.freesurfer.read_morph_data(snakemake.params.rh_sulc)
bg_map = np.concatenate((lh_sulc_data, rh_sulc_data))


mesh_3d = go.Mesh3d(x=all_ver_shift[:,0], y=all_ver_shift[:,1], z=all_ver_shift[:,2], i=all_face[:,0], j=all_face[:,1], k=all_face[:,2],opacity=.1,color='grey',alphahull=-10)

value=[np.round(x,2) for x in np.arange(.1,.6-.05,.05)]

df = pd.read_table(os.path.splitext(snakemake.input.fcsv)[0]+".tsv",sep='\t',header=0)
groups,n_members=determine_groups(df['label'].tolist(), True)
df['group']=np.repeat(groups,n_members)

cmap = plt.get_cmap('rainbow')
color_maps=cmap(np.linspace(0, 1, len(groups))).tolist()
res = dict(zip(groups, color_maps))

colors=[]
for igroup in df['group']:
	colors.append(res[igroup])

colors=np.vstack(colors)

data=[mesh_3d]
for igroup in groups:
	idx = [i for i,x in enumerate(df['label'].tolist()) if igroup in x]
	data.append(go.Scatter3d(
		x = df['x'][idx].values,
		y = df['y'][idx].values,
		z = df['z'][idx].values,
		name=igroup,
		mode = "markers+text",
		text=df['label'][idx].tolist(),
		textfont=dict(
			family="sans serif",
			size=16,
			color="black"
		),
		textposition = "middle left",
		marker=dict(
			size=5,
			line=dict(
				width=1,
			),
			color=['rgb({},{},{})'.format(int(r*256),int(g*256),int(b*256)) for r,g,b,h in colors[idx]],
			opacity=1
			)))

fig = go.Figure(data=data)
fig.update_layout(scene_camera=CAMERAS['left'],
				  legend_title_text="Electrodes",
				  **LAYOUT)

steps = []
for i in range(len(value)):
	step = dict(
		label = str(f"{value[i]:.2f}"),
		method="restyle",
		args=[{'opacity': [value[i]]+(len(data)-1)*[1],
			 'alphahull': [-10]+(len(data)-1)*[1]
		 }]
	)
	steps.append(step)

sliders = [dict(
	currentvalue={"visible": True,"prefix": "Opacity: ","font":{"size":16}},
	active=0,
	steps=steps,
	x=.35,y=.1,len=.3,
	pad={"t": 8},
)]

fig.update_layout(sliders=sliders)
fig.write_html(snakemake.output.html)


#fig.show('firefox')


