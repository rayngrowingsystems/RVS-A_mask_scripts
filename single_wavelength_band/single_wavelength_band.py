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
    # file and folder
    img_file = settings["inputImage"]

    # extract masking setting
    selected_wl = settings["experimentSettings"]["analysis"]["maskOptions"]["wavelength"]
    wl_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["wl_thresh"]
    fill_size = settings["experimentSettings"]["analysis"]["maskOptions"]["fill_size"]
    dilate_pixel = settings["experimentSettings"]["analysis"]["maskOptions"]["dilate_pixel"]

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings)

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

    if mask_preview:
        out_image = settings["outputImage"]
        image_file_name = os.path.normpath(out_image)
        print("Writing image to " + image_file_name)
        pcv.print_image(img=binary_img, filename=image_file_name)

    return spectral_array, binary_img
