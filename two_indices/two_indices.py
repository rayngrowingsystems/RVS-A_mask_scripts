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
    # file and folder
    img_file = settings["inputImage"]

    # extract masking setting
    mask_index1 = settings["experimentSettings"]["analysis"]["maskOptions"]["mask_index1"]
    mask_index2 = settings["experimentSettings"]["analysis"]["maskOptions"]["mask_index2"]
    logic_input = settings["experimentSettings"]["analysis"]["maskOptions"]["logic_input"]
    index1_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["index1_thresh"]
    index2_thresh = settings["experimentSettings"]["analysis"]["maskOptions"]["index2_thresh"]
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
    spectral_array.array_data = spectral_array.array_data.astype("float32")  # required for index calculations
    if spectral_array.d_type == np.uint8:  # only convert if original data seems to be uint8
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

    if mask_preview:
        out_image = settings["outputImage"]
        image_file_name = os.path.normpath(out_image)
        print("Writing image to " + image_file_name)
        pcv.print_image(img=combined_binary_img, filename=image_file_name)

    return spectral_array, combined_binary_img
