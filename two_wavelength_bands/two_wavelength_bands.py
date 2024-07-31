# Copyright 2024 RAYN Growing Systems
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
    mask_options = settings["experimentSettings"]["analysis"]["maskOptions"]
    wavelength1 = mask_options["wavelength1"]
    wavelength2 = mask_options["wavelength2"]
    logic_input = mask_options["logic_input"]
    wl1_thresh = mask_options["wl1_thresh"]
    wl2_thresh = mask_options["wl2_thresh"]
    fill_size = mask_options["fill_size"]
    dilate_pixel = mask_options["dilate_pixel"]

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
        cam_calibration_file = f"calibration_data/{lens_angle}_calibration_data.yml"   # select the data set
        mtx, dist = rayn_utils.load_coefficients(cam_calibration_file)                 # depending on the lens angle
        spectral_array.array_data = rayn_utils.undistort_data_cube(spectral_array.array_data, mtx, dist)
        spectral_array.pseudo_rgb = rayn_utils.undistort_data_cube(spectral_array.pseudo_rgb, mtx, dist)

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

    if mask_preview:
        out_image = settings["outputImage"]
        image_file_name = os.path.normpath(out_image)
        print("Writing image to " + image_file_name)
        pcv.print_image(img=combined_binary_img, filename=image_file_name)

    return spectral_array, combined_binary_img
