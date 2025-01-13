# Copyright 2024 ETC Inc d/b/a RAYN Growing Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import numpy as np
from plantcv import plantcv as pcv
import rayn_utils


def dropdown_values(setting, wavelengths):  # fills the index dropdown (see .config file)

    if setting == "index_list":  # defines the UI element this is applied to
        index_dict_dd = rayn_utils.get_index_functions()
        name_list = list(index_dict_dd)
        display_name_list = [item[0] for item in index_dict_dd.values()]

        return display_name_list, name_list

    else:
        return


def range_values(setting, name, index):  # sets the slider ranges (see .config file)
    print("range_values", setting, name, index)

    # set default values
    value = 0.5
    minimum = 0
    maximum = 1
    steps = 10

    if setting == "mask_index":  # defines the UI element this is applied to
        index_functions = rayn_utils.get_index_functions()
        minimum = index_functions[name][2]
        maximum = index_functions[name][3]
        value = (maximum - minimum)/2 + minimum
        steps = 500
        print(f"index settings: min {minimum}, max {maximum}, steps {steps}, value {value}")
            
    return minimum, maximum, steps, value


def create_mask(settings, mask_preview=True):
    # file and folder
    img_file = settings["inputImage"]

    # extract masking setting
    mask_index = settings["experimentSettings"]["analysis"]["maskOptions"]["mask_index"]
    index_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["index_thresh"]
    fill_size = settings["experimentSettings"]["analysis"]["maskOptions"]["fill_size"]
    dilate_pixel = settings["experimentSettings"]["analysis"]["maskOptions"]["dilate_pixel"]
    if settings["experimentSettings"]["analysis"]["maskOptions"]["invert_mask"]:
        mask_object = "dark"
    else:
        mask_object = "light"

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings)

    # calculating index for mask
    index_functions = rayn_utils.get_index_functions()
    index_array = index_functions[mask_index][1](spectral_array, distance=20)  # TODO: expose the distance parameter
    print(f"min: {np.ma.masked_invalid(index_array.array_data).min()}, "
          f"max: {np.ma.masked_invalid(index_array.array_data).max()}, "
          f"mean: {np.ma.masked_invalid(index_array.array_data).mean()}")
    binary_img = pcv.threshold.binary(gray_img=index_array.array_data, threshold=index_thresh, object_type=mask_object)
    binary_img = pcv.fill(bin_img=binary_img, size=fill_size)  # fill pixel

    if dilate_pixel:
        binary_img = pcv.dilate(gray_img=binary_img, ksize=2, i=2)

    if mask_preview:
        out_image = settings["outputImage"]
        image_file_name = os.path.normpath(out_image)
        print("Writing image to " + image_file_name)
        pcv.print_image(img=binary_img, filename=image_file_name)

    return spectral_array, rvs_metadata, binary_img
