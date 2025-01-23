import matplotlib
import ants
from nilearn import plotting,image
import nibabel as nib
import numpy as np

# snakemake.input.
# snakemake.output.
# html_view.open_in_browser()

def get_ras_affine(rotation, spacing, origin) -> np.ndarray:
    rotation_zoom = rotation * spacing
    translation_ras = rotation.dot(origin)
    affine = np.eye(4)
    affine[:3, :3] = rotation_zoom
    affine[:3, 3] = translation_ras
    return affine

def to_nibabel(img: "ants.core.ants_image.ANTsImage",header=None):
    try:
        from nibabel.nifti1 import Nifti1Image
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "Could not import nibabel, for conversion to nibabel. Install nibabel with pip install nibabel"
        ) from e
    affine = get_ras_affine(rotation=img.direction, spacing=img.spacing, origin=img.origin)
    return Nifti1Image(img.numpy(), affine, header)

template = ants.image_read(ants.get_ants_data('mni'))

debug = True
subject = 'sub-P165'

if debug:
	ct_img=nib.load('/home/arun/Documents/data/seeg/derivatives/atlasreg/{subject}/{subject}_space-T1w_desc-rigid_ses-post_ct.nii.gz')
	if (np.isnan(ct_img.get_fdata())).any():
		ct_img=nib.Nifti1Image(np.nan_to_num(ct_img.get_fdata()), header=ct_img.header, affine=ct_img.affine)
		nib.save(ct_img,snakemake.input.ct)
	
	ct_ants = ants.image_read('/home/arun/Documents/data/seeg/derivatives/atlasreg/{subject}/{subject}_space-T1w_desc-rigid_ses-post_ct.nii.gz')
	mask_ants = ants.image_read('/home/arun/Documents/data/seeg/derivatives/atlasreg/{subject}/{subject}_space-ct_desc-mask_contacts.nii.gz')
	mask_img = nib.load('/home/arun/Documents/data/seeg/derivatives/atlasreg/{subject}/{subject}_space-ct_desc-mask_contacts.nii.gz')
	
	ct_ants_reg = ants.registration(template, ct_ants, type_of_transform='QuickRigid')
	ct_ants_reg_applied=ants.apply_transforms(template, ct_ants, transformlist=ct_ants_reg['fwdtransforms'])
	#ct_resample = ants.to_nibabel(ct_ants_reg_applied) #to_nibabel deprecated in antspy 0.5.3
	ct_resample = to_nibabel(ct_ants_reg_applied, ct_img.header)
	
	mask_ants_reg_applied = ants.apply_transforms(ct_ants, mask_ants, transformlist=ct_ants_reg['fwdtransforms'])
	# mask_resample = ants.to_nibabel(mask_ants_reg_applied) #to_nibabel deprecated in antspy 0.5.3
	mask_resample = to_nibabel(mask_ants_reg_applied, mask_img.header)
	
	mask_params = {
				'symmetric_cmap': True,
				'cut_coords':[0,0,0],
				'dim': 1,
				'cmap':'viridis',
				'opacity':0.7
				}
	
	html_view = plotting.view_img(stat_map_img=mask_resample,bg_img=ct_resample,**mask_params)
	html_view.save_as_html('/home/arun/Documents/data/seeg/derivatives/atlasreg/{subject}/qc/{subject}_space-ct_desc-mask_contacts.html')



ct_img=nib.load(snakemake.input.ct)
if (np.isnan(ct_img.get_fdata())).any():
	ct_img=nib.Nifti1Image(np.nan_to_num(ct_img.get_fdata()), header=ct_img.header, affine=ct_img.affine)
	nib.save(ct_img,snakemake.input.ct)

ct_ants = ants.image_read(snakemake.input.ct)
mask_ants = ants.image_read(snakemake.input.mask)
mask_img = nib.load(snakemake.input.mask)

ct_ants_reg = ants.registration(template, ct_ants, type_of_transform='QuickRigid')
ct_ants_reg_applied=ants.apply_transforms(template, ct_ants, transformlist=ct_ants_reg['fwdtransforms'])
#ct_resample = ants.to_nibabel(ct_ants_reg_applied) #to_nibabel deprecated in antspy 0.5.3
ct_resample = to_nibabel(ct_ants_reg_applied, ct_img.header)

mask_ants_reg_applied = ants.apply_transforms(ct_ants, mask_ants, transformlist=ct_ants_reg['fwdtransforms'])
# mask_resample = ants.to_nibabel(mask_ants_reg_applied) #to_nibabel deprecated in antspy 0.5.3
mask_resample = to_nibabel(mask_ants_reg_applied, mask_img.header)

mask_params = {
			'symmetric_cmap': True,
			'cut_coords':[0,0,0],
			'dim': 1,
			'cmap':'viridis',
			'opacity':0.7
			}

html_view = plotting.view_img(stat_map_img=mask_resample,bg_img=ct_resample,**mask_params)
html_view.save_as_html(snakemake.output.html)