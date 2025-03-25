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
    ari_thresh = mask_options["ari_thresh"]
    fr_thresh = mask_options["fr_thresh"]
    green_thresh = mask_options["green_thresh"]
    blue_thresh = mask_options["blue_thresh"]
    fill_size = mask_options["fill_size"]
    dilate_pixel = mask_options["dilate_pixel"]
    show_mask = mask_options["show_mask"]

    spectral_array, rvs_metadata = rayn_utils.prepare_spectral_data(settings, preview=mask_preview)

    index_array_ari = pcv.spectral_index.ari(hsi=spectral_array, distance=20)
    ari_mask = pcv.threshold.binary(gray_img=index_array_ari.array_data, threshold=ari_thresh, object_type="dark")
    fr_mask = pcv.threshold.binary(gray_img=spectral_array.array_data[:, :, 7], threshold=fr_thresh)
    ari_fr = pcv.logical_and(ari_mask, fr_mask)
    green_mask = pcv.threshold.binary(gray_img=spectral_array.array_data[:, :, 3], threshold=green_thresh)
    ari_fr_green = pcv.logical_and(ari_fr, green_mask)
    blue_mask = pcv.threshold.binary(gray_img=spectral_array.array_data[:, :, 1], threshold=blue_thresh,
                                     object_type="dark")
    ari_fr_green_blue = pcv.logical_and(ari_fr_green, blue_mask)

    combined_mask = pcv.fill(ari_fr_green_blue, size=fill_size)

    if dilate_pixel:
        combined_mask = pcv.dilate(gray_img=combined_mask, ksize=2, i=1)

    output_dict = {
        "ari_mask": ari_mask,
        "fr_mask": fr_mask,
        "green_mask": green_mask,
        "blue_mask": blue_mask,
        "ari_fr": ari_fr,
        "ari_fr_green": ari_fr_green,
        "ari_fr_green_blue": ari_fr_green_blue,
        "combined_mask": combined_mask
    }

    if mask_preview:
        out_image = settings["outputImage"]
        image_file_name = os.path.normpath(out_image)
        print("Writing image to " + image_file_name)
        pcv.print_image(img=output_dict[show_mask], filename=image_file_name)

    return spectral_array, rvs_metadata, combined_mask


def dropdown_values(setting, wavelengths):  # fills the index dropdown (see .config file)

    if setting == "mask_list":  # defines the UI element this is applied to

        mask_dict = {
            "ari_mask": "ARI mask",
            "fr_mask": "Far red band mask",
            "green_mask": "Green band mask",
            "blue_mask": "Blue band mask",
            "ari_fr": "ARI + far red",
            "ari_fr_green": "ARI + far red + green",
            "ari_fr_green_blue": "ARI + far red + green + blue",
            "combined_mask": "Final combined mask"
        }

        name_list = list(mask_dict)
        display_name_list = [item for item in mask_dict.values()]

        return display_name_list, name_list

    else:
        return