from Kamthe.GoogleSearch import search_and_analyze_landlord
from openai_websearch import get_block_number
from property_search import get_owner_name
from Kamthe.SerperAPICall import search_google
import asyncio 

def are_names_similar(name, potential_name):
    potential_name_words = potential_name.lower().split(' ')
    name_words = name.lower().split(' ')
    for w in name_words:
        if w in potential_name_words:
            return True
    return False
                
async def check_if_scammer(name, address,listing_url, other_details, **kwargs):
    print(f"🔎 Searching Online")
    query = f"{name} {address}"
    google_results = search_and_analyze_landlord(name, address, query)
    
    # zillow search
    zillow_results = search_google(f"{address} zillow")
    analyze_zillow_results = analyze_zillow_results(zillow_results)
    
    print(f"📜🏠 Checking San Francisco Planning Department records")
    block_details = get_block_number(address)
    print(f"📋 Found tax block number '{block_details.block_number}', Lot number '{block_details.lot_number}'")
    print(f"🧭 Finding owner details from County of San Francisco Assessor-Recorder Public Index Search")
    print("<display browser use agent recorded video>")
    potential_owner_names = await get_owner_name(block_number=block_details.block_number, lot_number=block_details.lot_number)
    print(f"🪪 Found previous owner names {', '.join(potential_owner_names)}")
    flag = False
    matched_name = None
    for potential_owner in potential_owner_names:
        if are_names_similar(name, potential_owner):
            flag=True
            matched_name = potential_owner
            break
    
    if not flag:
        print(f"🚩🚩🚩 RED FLAG ALERT: Declared owner does not match owner names in county records!! 🚩🚩🚩")
    else:
        print(f"✅ Declared name '{name}' matches with country record name '{matched_name}'")
    
    print("====== SUMMARY =====")
    if google_results['green_flag']:
        print(f"🟢 Found the following green flags from search results: 🟢")
        for k,v in google_results['green_flag'].items():
            print(f"🟢 Proof of {k}")
            for source in v:
                print(f"- {source['title']}")
                print(f"- 🔗 {source['link']}")
    if google_results['red_flag']:
        print(f"🚩🚩🚩 RED FLAGS: Found the following green flags from search results: 🚩🚩🚩")
        for k,v in google_results['red_flag'].items():
            print(f"🚩 Contradictory proof found for {k}")
            for source in v:
                print(f"- {source['title']}")
                print(f"- 🔗 {source['link']}")
        
    
    
async def main():
    # name = "Mary McClelland"
    # address = "1300 Lawton St #307, San Francisco, CA 94122"
    name = "Sonia Riley"
    address = "1106 Bush St #504, San Francisco, CA 94109"
    listing_url = ""
    other_details = ""
    result = await check_if_scammer(name, address, listing_url, other_details)

if __name__ == "__main__":
    asyncio.run(main())