from Kamthe.GoogleSearch import search_and_analyze
from openai_websearch import get_block_number
from property_search import get_owner_name

def are_names_similar(name, potential_name):
    potential_name_words = potential_name.split(' ')
    name_words = name.split(' ')
    return False
 
def check_if_scammer(name, address,listing_url, other_details, **kwargs):
    google_results = search_and_analyze(name, address)
    block_details = get_block_number(address)
    potential_owner_names = get_owner_name(block_number=block_details.block_number, lot_number=block_details.lot_number)
    
    flag = False
    for potential_owner in potential_owner_names:
        if are_names_similar(name, potential_owner):
            flag=True
            break
    
    if not flag:
        name_suspicious = True
    
    
    
    
    
    
    
    