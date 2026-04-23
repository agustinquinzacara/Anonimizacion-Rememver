import nibabel as nib
import numpy as np

def fix_dtype(nifti_path):

    nii = nib.load(nifti_path)
    data = nii.get_fdata()

    # convertir a int16 (compatible con FSL)
    data = data.astype(np.int16)

    new_img = nib.Nifti1Image(data, nii.affine, nii.header)
    nib.save(new_img, nifti_path)

    print("🧠 dtype corregido → int16")