from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
import asyncio
import os 
from typing import List
from pydantic import BaseModel

load_dotenv()

class Owners(BaseModel):
    owners: List[str]
    
async def get_owner_name(block_number, lot_number):
    llm = ChatOpenAI(model="gpt-4.1")
    url = "https://recorder.sfgov.org/#!/simple"
    task = f"Go to this url {url}. Enter the block number '{block_number}' and lot number '{lot_number}'. IMPORTANT: Leave all other fields blank. Hit search. return the list of names that appears on the page and end immediately - don't navigate on the page."
    agent = Agent(task=task, llm=llm, output_model_schema=Owners)
    history=await agent.run(max_steps=20)
    owners: Owners = history.structured_output
    return owners.owners

async def main():
    block_number = "1865"
    lot_number = "012"
    await get_owner_name(block_number=block_number, lot_number=lot_number)

if __name__=="__main__":
    asyncio.run(main())
