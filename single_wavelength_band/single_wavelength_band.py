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

    # get individual settings for readability
    selected_wl = mask_options["wavelength"]
    wl_thresh = mask_options["wl_thresh"]
    fill_size = mask_options["fill_size"]
    dilate_pixel = mask_options["dilate_pixel"]
    invert_mask = mask_options["invert_mask"]

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings, preview=mask_preview)

    # get data from selected wavelength band
    if (selected_wl != "None") and (selected_wl != ""):
        selected_wl = float(selected_wl)
        selected_layer = spectral_array.array_data[:, :, int(float(spectral_array.wavelength_dict[selected_wl]))]
    else:
        selected_layer = spectral_array.array_data[:, :, 0]
        warnings.warn("No wavelength for mask selected. Defaulting to first in list")

    # create binary mask from layer using a adjustable threshold
    binary_img = pcv.threshold.binary(gray_img=selected_layer, threshold=wl_thresh)
    binary_img = pcv.fill(bin_img=binary_img, size=fill_size)

    print(selected_layer.min(), selected_layer.max())

    if dilate_pixel:
        binary_img = pcv.dilate(gray_img=binary_img, ksize=2, i=2)

    if invert_mask:
        binary_img = pcv.invert(binary_img)

    rayn_utils.create_mask_preview(binary_img, spectral_array.pseudo_rgb, settings, mask_preview)

    return spectral_array, rvs_metadata, binary_img
