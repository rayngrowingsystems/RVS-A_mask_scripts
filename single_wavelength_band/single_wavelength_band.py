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
import numpy as np
import rayn_utils


def create_mask(settings, mask_preview=True):
    # file and folder
    img_file = settings["inputImage"]

    # extract masking setting
    selected_wl = settings["experimentSettings"]["analysis"]["maskOptions"]["wavelength"]
    wl_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["wl_thresh"]
    fill_size = settings["experimentSettings"]["analysis"]["maskOptions"]["fill_size"]
    dilate_pixel = settings["experimentSettings"]["analysis"]["maskOptions"]["dilate_pixel"]

    # undistort (lens angle) and normalize
    lens_angle = settings["experimentSettings"]["imageOptions"]["lensAngle"]
    dark_normalize = settings["experimentSettings"]["imageOptions"]["normalize"]

    # check if a .hdr file name was provided and set img_file to the binary location
    if os.path.splitext(img_file)[1] == ".hdr":
        img_file = os.path.splitext(img_file)[0]

    else:
        warnings.warn("No header file provided. Processing not possible.")
        return

    # begin masking workflow
    spectral_array = pcv.readimage(filename=img_file, mode='envi')
    spectral_array.array_data = spectral_array.array_data.astype("float32")  # required for further calculations
    if spectral_array.d_type == np.uint8:  # only convert if data seems to be uint8
        spectral_array.array_data = spectral_array.array_data / 255  # convert 0-255 (orig.) to 0-1 range

    # normalize the image cube
    if dark_normalize:
        spectral_array.array_data = rayn_utils.dark_normalize_array_data(spectral_array)

    # undistort the image cube
    if lens_angle != 0:  # only undistort if angle is selected
        cam_calibration_file = f"calibration_data/{lens_angle}_calibration_data.yml"  # select the data set
        mtx, dist = rayn_utils.load_coefficients(cam_calibration_file)  # depending on the lens angle
        spectral_array.array_data = rayn_utils.undistort_data_cube(spectral_array.array_data, mtx, dist)
        spectral_array.pseudo_rgb = rayn_utils.undistort_data_cube(spectral_array.pseudo_rgb, mtx, dist)

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
