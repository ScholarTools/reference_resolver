"""

Reference Resolver
------------------

Goal:
    Take something like this:
        Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering: An adeno‐associated viral (AAV) vector toolbox."
        Biotechnology journal 9.11 (2014): 1402-1412.

    and retrieve the entry data and/or that paper's references from the corresponding site where it is hosted.

------------------

Basically follow the method outlined here:
    http://labs.crossref.org/resolving-citations-we-dont-need-no-stinkin-parser/

Another super helpful link about DOIs and publishers:
    https://webhome.weizmann.ac.il/home/comartin/doi.html

Steps:
    1) Search for the original reference on CrossRef
    2) Extract DOI from CrossRef
    3) Match DOI with provider
    4) Call appropriate scraper with DOI and get info
    5) Return info

"""

# The below comment block is copied from crossref.py
"""

Tools related to crossref (DOIs)

See:
http://www.crosscite.org/cn/
http://labs.crossref.org/


TODO: List relevant GitHub repos

List is Unfinished:
- https://github.com/MartinPaulEve/crossRefQuery
- https://github.com/total-impact/total-impact-core/blob/master/totalimpact/providers/crossref.py

CrossRef Organization:
https://github.com/CrossRef

===============================================================================
crossref help
http://help.crossref.org/#home

crossref SimpleText query:
----------------------------------
- http://www.crossref.org/SimpleTextQuery/
- cut and paste references into the box - returns DOIs
- requires registered email

OpenURL
----------------------------------
- http://help.crossref.org/#using_the_open_url_resolver
-

HTTP
----------------------------------
- http://help.crossref.org/#using_http

"""

import sys
import requests
import json
import csv
import os.path
import importlib

#TODO: Move this into a compatability module
#-----------------------------------------------------
PY2 = sys.version_info.major == 2

if PY2:
    from urllib import unquote as urllib_unquote
    from urllib import quote as urllib_quote
else:
    from urllib.parse import unquote as urllib_unquote
    from urllib.parse import quote as urllib_quote
#-----------------------------------------------------


citation = 'Senís, Elena, et al. "CRISPR/Cas9‐mediated genome engineering: An adeno‐associated viral (AAV) vector ' + \
           'toolbox. Biotechnology journal 9.11 (2014): 1402-1412.'
citation = urllib_quote(citation)

api_search_url = 'http://search.labs.crossref.org/dois?q=' + citation
response = requests.get(api_search_url).json()
doi = response[0]['doi']
print(doi)

# If crossref returns a http://dx.doi.org/ link, retrieve the doi from it
if doi[0:18] == 'http://dx.doi.org/':
    doi = doi[18:]

doi_prefix = doi[0:7]

print(doi)
print(doi_prefix)


# TODO: Implement DOI to provider matching

# Import current prefix dict
with open('doi_prefix_dict.txt', 'r') as f:
    str_dict = f.read()
prefix_dict = json.loads(str_dict)


# With the DOI prefix we got from the CrossRef search,
# look in the prefix_dict to get the corresponding base URL.
# The url should be in index 1
if len(prefix_dict[doi_prefix]) > 1:
    pub_url = prefix_dict[doi_prefix][1]
else:
    raise IndexError('The corresponding url is not yet set within prefix_dict')

print(pub_url)


# Now search the site_features.csv file to get information relevant to that provider
with open(os.path.dirname(__file__) + '/../site_features.csv') as f:
    reader = csv.reader(f)
    headings = next(reader)  # Save the first line as the headings
    for row in enumerate(reader):
        if pub_url in row[1]:
            values = row[1]  # Once the correct row is found, save it as values
            break

# Turn the headings and values into a callable dict
pub_dict = dict(zip(headings, values))
print(pub_dict)

# Get the name of the scraper .py file from the dictionary
# Import the correct scraper file
scrapername = 'scrapers.' + pub_dict['scraper']
scraper = importlib.import_module(scrapername)

# Construct the correct direct URL from the dictionary
full_url = pub_dict['provider_root_url'] + pub_dict['url_prefix'] + str(doi) + pub_dict['article_page_suffix']

# Call the scraper to get entry info and reference information
entry_info = scraper.get_entry_info(full_url)
references = scraper.get_references(doi)


print(entry_info)
print(references[0])



'''
DOI_SEARCH = 'http://doi.crossref.org/search/doi'

crossref_email = 'jim.hokanson@gmail.com'

#TODO: Support multiple dois ...
def getMeta(doi, format='unixsd'):

    """

    Given a doi, return article meta data

    #Output formats:
    #-------------------------
    #1) xsd_xml - default - 'unixsd' - recommended for future use
    #http://help.crossref.org/#unixsd
    #DOC: query_output3.0
    #http://www.crossref.org/schema/documentation/crossref_query_output3.0/query_output3.0.html
    #2) 'unixref'
    #http://help.crossref.org/#unixref-query-result-format

    #TODO: Document why unixref might be preferable
    #TODO: Finish parsing of xsd


    """

    #pid    - email
    #format - unixsd
    #doi    - doi
    payload = {'pid':crossref_email, 'format':format, 'doi':doi}
    r = requests.get(DOI_SEARCH, params=payload)

    #XSD code generation
    #http://www.rexx.com/~dkuhlman/generateDS.html
    #generateds_gui.py

'''