import numpy as np
import nibabel as nib
import copy


def set_new_data(image, new_data):
    """
    From a nibabel image and a numpy array it creates a new image with
    the same header of the image and the new_data as its data.
    :param image: nibabel image
    :param new_data: numpy array
    :return: nibabel image
    """
    # if nifty1
    if image.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(new_data, image.affine, header=image.header)
    # if nifty2
    elif image.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(new_data, image.affine, header=image.header)
    else:
        raise IOError('input_image_problem')
    # update data type:
    new_image.set_data_dtype(new_data.dtype)

    return new_image


def label_selector(path_input_image, path_output_image, labels_to_keep, binarize=True):
    """
    Given an label of image and a list of labels to keep, a new image with only the labels to keep will be created.
    New image can still have the original labels, or can binarize them.
    :param path_input_image:
    :param path_output_image:
    :param labels to keep: list of labels
    :param binarize: True if you want the output to be a binary images. Original labels are otherwise kept.
    """
    im = nib.load(path_input_image)
    im_data = im.get_data()[:]
    new_data = np.zeros_like(im_data)

    for i in xrange(im_data.shape[0]):
        for j in xrange(im_data.shape[1]):
            for k in xrange(im_data.shape[2]):
                if im_data[i, j, k] in labels_to_keep:
                    if binarize:
                        new_data[i, j, k] = 1
                    else:
                        new_data[i, j, k] = im_data[i, j, k]

    new_im = set_new_data(im, new_data)
    nib.save(new_im, path_output_image)
    print('Output image saved in ' + str(path_output_image))


def compare_two_nib(im1, im2, toll=1e-3):
    """
    :param im1: one nibabel image
    :param im2: another nibabel image
    :param toll: tolerance to the dissimilarity in the data - if headers are different images are different.
    :return: true false and plot to console if the images are the same or not (up to a tollerance in the data)
    """

    im1_name = 'First argument'
    im2_name = 'Second argument'

    hd1 = im1.header
    hd2 = im1.header

    images_are_equals = True

    # compare nifty version:
    if not hd1['sizeof_hdr'] == hd2['sizeof_hdr']:

        if hd1['sizeof_hdr'] == 348:
            msg = '{0} is nifty1\n{1} is nifty2.'.format(im1_name, im2_name)
        else:
            msg = '{0} is nifty2\n{1} is nifty1.'.format(im1_name, im2_name)
        print(msg)

        images_are_equals = False

    # Compare headers:

    for k in hd1.keys():
        if k not in ['scl_slope', 'scl_inter']:
            val1, val2 = hd1[k], hd2[k]
            are_different = val1 != val2
            if isinstance(val1, np.ndarray):
                are_different = are_different.any()

            if are_different:
                images_are_equals = False
                print(k, hd1[k])

        elif not np.isnan(hd1[k]) and np.isnan(hd2[k]):
            images_are_equals = False
            print(k, hd1[k])

    '''
    # Compare values and type:

    im1_data = im1.get_data()
    im2_data = im2.get_data()

    if not im1_data.dtype == im2_data.dtype:
        images_are_equals = False

    # Compare values
    if np.max(im1_data - im2_data) > toll:
        images_are_equals = False
    '''

    return images_are_equals


def compare_two_nifti(path_img_1, path_img_2):
    """
    ... assuming nibabel take into account all the information in the nifty header properly!
    :param path_img_1:
    :param path_img_2:
    :return:
    """
    im1 = nib.load(path_img_1)
    im2 = nib.load(path_img_2)

    return compare_two_nib(im1, im2)


def reproduce_slice_fourth_dimension(nib_image, num_slices=10):
    # can be optimised...!

    im_sh = nib_image.shape
    if not (len(im_sh) == 2 or len(im_sh) == 3):
        raise IOError('Methods can be used only for 2 or 3 dim images. No conflicts with existing multi, slices')
    im_hd = nib_image.get_header()

    new_data = np.zeros(list(im_sh) + [num_slices], dtype=im_hd['datatype'].dtype)
    a_slice = copy.deepcopy(nib_image.get_data())

    for d in xrange(num_slices):
        new_data[..., d] = a_slice

    im_output = set_new_data(nib_image, new_data)

    output_im = set_new_data(nib_image, new_data)

    return output_im


def reproduce_slice_fourth_dimension_path(pfi_input_image, pfi_output_image, num_slices=10):
    old_im = nib.load(pfi_input_image)
    new_im = reproduce_slice_fourth_dimension(old_im, num_slices)
    nib.save(new_im, pfi_output_image)
    return 'copied!'


'''
tmp_path = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pipelines/ex_vivo_DWI/zz_test'
test_obj = os.path.join(tmp_path, 'ciccione_1305_on_1201_3D_mask_affine.nii.gz')
test_obj_output = os.path.join(tmp_path, 'ciccione_1305_on_1201_3D_mask_affine_output.nii.gz')

d = 12
copy_and_paste_on_slice_path(test_obj, test_obj_output, d)
'''


def cut_dwi_image_from_first_slice_mask(input_dwi, input_mask):

    data_dwi  = input_dwi.get_data()
    data_mask = input_mask.get_data()

    data_masked_dw = np.zeros_like(data_dwi)

    for t in xrange(input_dwi.shape[-1]):
        data_masked_dw[..., t] = np.multiply(data_mask, data_dwi[..., t])

    # image with header of the dwi and values under the mask for each slice:
    return set_new_data(input_dwi, data_masked_dw)


def cut_dwi_image_from_first_slice_mask_path(path_input_dwi, path_input_mask, path_output_masked_dwi):

    im_dwi = nib.load(path_input_dwi)
    im_mask = nib.load(path_input_mask)

    im_masked = cut_dwi_image_from_first_slice_mask(im_dwi, im_mask)

    nib.save(im_masked, path_output_masked_dwi)


def eliminates_consecutive_duplicates(input_list):
    output_list = [input_list[0],]
    for i in xrange(1, len(input_list)):
        if not input_list[i] == input_list[i-1]:
            output_list.append(input_list[i])

    return output_list


# ---------- O C generators experiments ---------------

def generate_o(omega=(250, 250), radius=50,
               background_intensity=0, foreground_intensity=20, dtype=np.uint8):

    m = background_intensity * np.ones(omega, dtype=dtype)

    if len(omega) == 2:
        c = [omega[j] / 2 for j in range(len(omega))]
        for x in xrange(omega[0]):
            for y in xrange(omega[1]):
                if (x - c[0])**2 + (y - c[1])**2 < radius**2:
                    m[x, y] = foreground_intensity
    elif len(omega) == 3:
        c = [omega[j] / 2 for j in range(len(omega))]
        for x in xrange(omega[0]):
            for y in xrange(omega[1]):
                for z in xrange(omega[2]):
                    if (x - c[0])**2 + (y - c[1])**2 + (z - c[2])**2 < radius**2:
                        m[x, y, z] = foreground_intensity
    return m


def generate_c(omega=(250, 250), internal_radius=40, external_radius=60, opening_height=50,
               background_intensity=0, foreground_intensity=20, dtype=np.uint8, margin=None):

    def get_a_2d_c(omega, internal_radius, external_radius, opening_height, background_intensity, foreground_intensity, dtype):

        m = background_intensity * np.zeros(omega[:2], dtype=dtype)

        c = [omega[j] / 2 for j in range(len(omega))]
        # create the crown
        for x in xrange(omega[0]):
            for y in xrange(omega[1]):
                if internal_radius**2 < (x - c[0])**2 + (y - c[1])**2 < external_radius**2:
                    m[x, y] = foreground_intensity

        # open the c
        low_lim = int(omega[0] / 2) - int(opening_height / 2)
        high_lim = int(omega[0] / 2) + int(opening_height / 2)

        for x in xrange(omega[0]):
            for y in xrange(int(omega[1] / 2), omega[1]):
                if low_lim < x < high_lim and m[x, y] == foreground_intensity:
                    m[x, y] = background_intensity

        return m

    c_2d = get_a_2d_c(omega=omega[:2], internal_radius=internal_radius, external_radius=external_radius,
                      opening_height=opening_height, background_intensity=background_intensity,
                      foreground_intensity=foreground_intensity, dtype=dtype)

    if len(omega) == 2:
        return c_2d

    elif len(omega) == 3:
        if margin is None:
            return np.repeat(c_2d, omega[2]).reshape(omega)
        else:
            res = np.zeros(omega, dtype=dtype)
            for z in xrange(margin, omega[2] - 2 * margin):
                res[..., z] = c_2d
            return res
