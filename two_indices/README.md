# Combine Two Index Masks into One Mask

This masking script combines two reflection indices and respective thresholds to create a binary mask. 
The reflection indices can be selected from a drop-down menu and the threshold can be adjusted via a slider.
The logical operation (combination) can be selected via a drop-down menu.

AND = pixels are white where both single-index masks are white 
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_and/)\
OR = pixels are white where either single-index mask is white
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_or/) \
XOR = differences between both single-index masks
[(plantCV documentation)](https://plantcv.readthedocs.io/en/stable/logical_xor/)

Note: Different reflection indices have different ranges. The slider ranges are adjusted accordingly.
(See file rayn_utils.py for available indices and the respective ranges)

© 2024 ETC Inc d/b/a RAYN Growing Systems. Licensed under the Apache License, Version 2.0

Trademark and patent info: [rayngrowingsystems.com/ip](https://rayngrowingsystems.com/ip/) \
Third-party license agreement info: [etcconnect.com/licenses](https://www.etcconnect.com/licenses/) \
Product and specifications subject to change.