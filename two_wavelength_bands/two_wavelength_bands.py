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
from plantcv import plantcv as pcv
import rayn_utils


def create_mask(settings, mask_preview=True):

    # extract masking setting
    mask_options = settings["experimentSettings"]["analysis"]["maskOptions"]
    wavelength1 = mask_options["wavelength1"]
    wavelength2 = mask_options["wavelength2"]
    logic_input = mask_options["logic_input"]
    wl1_thresh = mask_options["wl1_thresh"]
    wl2_thresh = mask_options["wl2_thresh"]
    fill_size = mask_options["fill_size"]
    dilate_pixel = mask_options["dilate_pixel"]
    invert_mask = mask_options["invert_mask"]
    overlay_mask = settings["experimentSettings"]["analysis"]["maskOptions"]["overlay_mask"]

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings)

    # extract data of the selected wavelength bands
    if (wavelength1 != "None") and (wavelength1 != ""):
        wavelength1 = float(wavelength1)
        selected_layer1 = spectral_array.array_data[:, :, int(float(spectral_array.wavelength_dict[wavelength1]))]

    else:
        selected_layer1 = spectral_array.array_data[:, :, 0]
        warnings.warn("No wavelength for mask selected. Defaulting to first in list")

    if (wavelength2 != "None") and (wavelength2 != ""):
        wavelength2 = float(wavelength2)
        selected_layer2 = spectral_array.array_data[:, :, int(float(spectral_array.wavelength_dict[wavelength2]))]
    else:
        selected_layer2 = spectral_array.array_data[:, :, 0]
        warnings.warn("No wavelength for mask selected. Defaulting to first in list")

    # creating binary masks from the selected wavelength bands
    binary_img1 = pcv.threshold.binary(gray_img=selected_layer1, threshold=wl1_thresh)
    binary_img2 = pcv.threshold.binary(gray_img=selected_layer2, threshold=wl2_thresh)

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

    rayn_utils.create_mask_preview(combined_binary_img, spectral_array.pseudo_rgb, settings, mask_preview)

    return spectral_array, rvs_metadata, combined_binary_img
