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
import warnings
import numpy as np
from plantcv import plantcv as pcv
import rayn_utils


def dropdown_values(name, wavelengths):  # fills the index dropdown (see .config file)

    if name == "index_list":  # defines the UI element this is applied to
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

    if setting == "mask_index1" or "mask_index2":  # defines the UI elements this is applied to
        index_functions = rayn_utils.get_index_functions()
        minimum = index_functions[name][2]
        maximum = index_functions[name][3]
        value = (maximum - minimum) / 2 + minimum
        steps = 500
        print(f"index settings: min {minimum}, max {maximum}, steps {steps}, value {value}")

    return minimum, maximum, steps, value


def create_mask(settings, mask_preview=True):

    # extract masking setting
    mask_index1 = settings["experimentSettings"]["analysis"]["maskOptions"]["mask_index1"]
    mask_index2 = settings["experimentSettings"]["analysis"]["maskOptions"]["mask_index2"]
    logic_input = settings["experimentSettings"]["analysis"]["maskOptions"]["logic_input"]
    index1_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["index1_thresh"]
    index2_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["index2_thresh"]
    fill_size = settings["experimentSettings"]["analysis"]["maskOptions"]["fill_size"]
    dilate_pixel = settings["experimentSettings"]["analysis"]["maskOptions"]["dilate_pixel"]
    invert_mask = settings["experimentSettings"]["analysis"]["maskOptions"]["invert_mask"]
    overlay_mask = settings["experimentSettings"]["analysis"]["maskOptions"]["overlay_mask"]

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings)

    # calculating index for mask
    index_functions = rayn_utils.get_index_functions()
    index1_array = index_functions[mask_index1][1](spectral_array, 20)  # TODO: expose the distance parameter
    binary_img1 = pcv.threshold.binary(gray_img=index1_array.array_data, threshold=index1_thresh)
    index2_array = index_functions[mask_index2][1](spectral_array, 20)  # TODO: expose the distance parameter
    binary_img2 = pcv.threshold.binary(gray_img=index2_array.array_data, threshold=index2_thresh)

    if logic_input == "logic_and":
        combined_binary_img = pcv.logical_and(binary_img1, binary_img2)
    elif logic_input == "logic_or":
        combined_binary_img = pcv.logical_or(binary_img1, binary_img2)
    elif logic_input == "logic_xor":
        combined_binary_img = pcv.logical_xor(binary_img1, binary_img2)
    else:
        warnings.warn("Input error. Using only first index for masking.")
        combined_binary_img = binary_img1

    combined_binary_img = pcv.fill(bin_img=combined_binary_img, size=fill_size)  # fill pixel

    if dilate_pixel:
        combined_binary_img = pcv.dilate(gray_img=combined_binary_img, ksize=2, i=2)

    if invert_mask:
        combined_binary_img = pcv.invert(combined_binary_img)

    rayn_utils.create_mask_preview(binary_img, spectral_array.pseudo_rgb, settings, mask_preview, overlay_mask)

    return spectral_array, rvs_metadata, combined_binary_img
