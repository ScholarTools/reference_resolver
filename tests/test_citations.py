#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

from reference_resolver import citations

c1 = "Cruz F, Herschorn S, Aliotta P et al: Efficacy and safety of onabotulinumtoxinA in patients with urinary incontinence due to neurogenic detrusor overactivity: a randomised, double- blind, placebo-controlled trial. Eur Urol 2011; 60: 742"
c2 = 'Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering: An adeno‐associated viral (AAV) vector toolbox. Biotechnology journal 9.11 (2014): 1402-1412.'

#TODO: Add a few nonsense ones and iterate through all of them
temp = citations.citation_to_doi(c1)

temp = citations.citation_to_doi(c2)


