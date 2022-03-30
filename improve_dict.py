"""

This is meant to extend the doi_prefix_dict.txt dictionary by adding
either base URLs or some other standard identifier besides the full publisher
name to get from the DOI prefix to a site.

Starting point for popular DOI prefixes:
https://webhome.weizmann.ac.il/home/comartin/doi.html

Wiley: 10.1002, 10.1111
ScienceDirect: 10.1006, 10.1016, 10.1097

10.1002 - Wiley
10.1006 - Science Direct (Academic Press, which was absorbed by Elsevier, which uses ScienceDirect)
10.1007 - Springer
10.1016 - Science Direct (Elsevier)
10.1017 - Cambridge University Press
10.1021 - American Chemical Society (ACS)
10.1038 - Nature
10.1039 - Royal Society of Chemistry (RSoC)
10.1046 - Blackwell Publishers (Wiley-Blackwell - different from Wiley Online Library)
10.1055 - Synthesis
10.1063 - American Institute of Physics
10.1073 - PNAS
10.1074 - Journal of Biological Chemistry
10.1080 - Taylor and Francis
10.1083 - Rockefeller University Press
10.1092 - Laser Pages Publishing
10.1093 - Oxford University Press
10.1097 - Science Direct
10.1103 - American Physical Society
10.1111 - Wiley
10.1126 - Science
10.1161 - American Heart Association
10.1182 - American Society of Hematology

"""

import json

with open('doi_prefix_dict.txt', 'r') as f:
    str_dict = f.read()
prefix_dict = json.loads(str_dict)

print(prefix_dict['10.1111'])
print(prefix_dict)

for v in prefix_dict.values():
    if len(v) > 1:
        print(v)

wy_prefixes = ['10.1002', '10.1111']
sd_prefixes = ['10.1006', '10.1016', '10.1097']

for x in wy_prefixes:
    if len(prefix_dict[x]) == 1:
        prefix_dict[x].append('http://onlinelibrary.wiley.com')

for x in sd_prefixes:
    if len(prefix_dict[x]) == 1:
        prefix_dict[x].append('http://sciencedirect.com')


# Write to file
with open('doi_prefix_dict.txt', 'w') as f:
    json.dump(prefix_dict, f)