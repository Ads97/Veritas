from Kamthe.GoogleSearch import search_and_analyze
from openai_websearch import get_block_number
from property_search import get_owner_name

def are_names_similar(name, potential_name):
    potential_name_words = potential_name.split(' ')
    name_words = name.split(' ')
    return False

def pretty_print_search_results(results):
    print(    f"""
    ==== 🔎 Online Search Execution Summary ====

    Analyses:
    {analyses}
    
    Queries Tried:
    {query}

    Search Results:
    {results}

    Status:
    {"✅ Success" if True else "❌ Failed"}

    Error:
    {None if None else "N/A"}
    """)
     
def check_if_scammer(name, address,listing_url, other_details, **kwargs):
    google_results = search_and_analyze(name, address)
    pretty_print_search_results(google_results)
    block_details = get_block_number(address)
    potential_owner_names = get_owner_name(block_number=block_details.block_number, lot_number=block_details.lot_number)
    
    flag = False
    for potential_owner in potential_owner_names:
        if are_names_similar(name, potential_owner):
            flag=True
            break
    
    if not flag:
        name_suspicious = True

def check_if_scammer_mock(name, address,listing_url, other_details, **kwargs):
    is_high_risk = True
    is_low_risk = not is_high_risk
    if is_high_risk:
        return {
            "clear_outcome": True,
            "scam_likelihood": 0.85,
            "address": address,
            "reasons": [
                ["bad", "Landlord requesting wire transfer before viewing property"],
                ["bad", "Price significantly below market rate for the area"],
                ["bad", "Landlord claims to be out of country"],
                ["bad", "Pressure to send money quickly"],
                ["good", "Property photos appear to be legitimate"]
            ],
            "analyzed_data": [
                ["Rental Price", "$1,200/month (65% below market average)"],
                ["Market Average", "$3,400/month for similar properties"],
                ["Landlord Contact", "Email only, no phone verification"],
                ["Property History", "Recently listed on multiple platforms"],
                ["Payment Method", "Wire transfer requested (high risk)"]
            ],
            "additional_questions": [
                "Have you been able to verify the landlord's identity through official channels?",
                "Can you schedule an in-person viewing of the property?",
                "Has the landlord provided verifiable references or credentials?",
                "Are there any official property management companies associated with this listing?"
            ]
        }
    elif is_low_risk:
        return {
            "clear_outcome": True,
            "scam_likelihood": 0.15,
            "address": address,
            "reasons": [
                ["good", "Landlord provided verifiable contact information"],
                ["good", "Property price is within market range"],
                ["good", "In-person viewing scheduled and confirmed"],
                ["bad", "Limited online presence for the property"]
            ],
            "analyzed_data": [
                ["Rental Price", "$2,800/month (within market range)"],
                ["Market Average", "$3,200/month for similar properties"],
                ["Landlord Contact", "Phone and email verified"],
                ["Property History", "Listed by established real estate agency"],
                ["Payment Method", "Standard lease agreement and deposit"]
            ],
            "additional_questions": [
                "Have you completed the background check process?",
                "Are all lease terms clearly documented?",
                "Have you verified the property management company's credentials?"
            ]
        }
    else:
        # Default inconclusive case
        return {
            "clear_outcome": False,
            "scam_likelihood": 0.5,
            "address": address,
            "reasons": [
                ["bad", "Limited information available for analysis"],
                ["good", "No obvious red flags detected"]
            ],
            "analyzed_data": [
                ["Information Available", "Insufficient data for complete analysis"],
                ["Recommendation", "Gather more information before proceeding"]
            ],
            "additional_questions": [
                "Can you provide more details about the landlord?",
                "What payment methods are being requested?",
                "Have you been able to view the property in person?",
                "Are there any unusual requests or pressure tactics?"
            ]
        }


    
if __name__ == "__main__":
    name = "Dustin Suchter"
    address = "88 King Street, Unit 116, San Francisco 94107"
    listing_url = ""
    other_details = ""
    check_if_scammer(name, address,listing_url, other_details)
    
    
    