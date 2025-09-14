import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

client = OpenAI()

class HouseID(BaseModel):
    block_number: str
    lot_number: str
    
def get_block_number(address):
    response = client.responses.parse(
    model="gpt-5",
    input=f"Find the block number and lot number for this SF apartment address: {address}. Return them exactly as found (including leading zeros)",
    tools=[
        {
            "type": "web_search"
        }
    ],
    text_format=HouseID,
    )

    return response.output_parsed

# Run the async function
if __name__ == "__main__":
    print(get_block_number(address="88 king street, unit 116, san francisco 94107"))
