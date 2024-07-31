# Combine Two Wavelength Band Masks into One Mask

This masking script combines the binary sub-masks of two wavelength bands and respective thresholds into one binary mask. 
The wavelength bands can be selected from a drop-down menu and the thresholds can be adjusted via sliders.
The logical operation (combination) can be selected via a drop-down menu.

AND = pixels are white where both single-index masks are white 
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_and/)\
OR = pixels are white where either single-index mask is white
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_or/) \
XOR = differences between both single-index masks
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_xor/)


© 2024 RAYN Growing Systems, All Rights Reserved. Licensed under the Apache License, Version 2.0

Trademark and patent info: [rayngrowingsystems.com/ip](https://rayngrowingsystems.com/ip/) \
Third-party license agreement info: [etcconnect.com/licenses](https://www.etcconnect.com/licenses/) \
Product and specifications subject to change.