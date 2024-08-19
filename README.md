# RAYN Vision System Analytics - Mask Scripts
Collection of mask scripts for RAYN Vision System (RVS) Analytics that are maintained by RAYN.

## Description
Masks are binary 2D-arrays, segmenting the objects of interest. Each mask script provides different filtering options 
for segmenting plants from background data.

The mask scripts use functions from [PlantCV](https://plantcv.readthedocs.io/en/stable/).

## Usage
Each mask script consists of a folder containing three files:
- MASK_NAME.py - Actual python script, containing the masking workflow
- MASK_NAME.config - Configuration file setting the UI elements in the mask UI interface
- README.md - Describes the function and purpose of the respective mask script

Pull this repository or add the mask folders to the "Mask" folder of RVS Analytics.

While a default mask script is applied when an analysis script is chosen, all available mask scripts are listed in a 
drop-down menu and can be selected from there.

## Support
If you experience any problems or have feedback on the mask scripts, please add an issue to this 
[repository](https://github.com/rayngrowingsystems/RVS-A_mask_scripts/issues) or contact 
[RAYN Vision Support](mailto:RAYNVisionSupport@rayngrowingsystems.com).

## Contributing
Whether it's fixing bugs, adding functionality to existing mask scripts or adding entirely new mask
scripts, we welcome contributions.

## Create Your Own RVS Mask Scripts
Instructions on how to create your own mask scrips will be linked here.

## License and Copyright
© 2024 ETC Inc d/b/a RAYN Growing Systems. Licensed under the Apache License, Version 2.0
You may not use the files in this repository except in compliance with the License.

Trademark and patent info: [rayngrowingsystems.com/ip](https://rayngrowingsystems.com/ip/) \
Third-party license agreement info: [etcconnect.com/licenses](https://www.etcconnect.com/licenses/) \
Product and specifications subject to change.

