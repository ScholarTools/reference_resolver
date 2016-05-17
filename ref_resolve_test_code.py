import reference_resolver as rr

citation = 'Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering: An adeno‐associated viral (AAV) vector ' + \
           'toolbox. Biotechnology journal 9.11 (2014): 1402-1412.'

link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'

paper_info = rr.resolve_citation(citation)
print(paper_info['entry'])
print(paper_info['references'][0])
print(paper_info.keys())