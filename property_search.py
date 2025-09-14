from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
import asyncio
import os 

load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = "false"

async def main():
    llm = ChatOpenAI(model="gpt-4.1")
    task = "Go to this url https://recorder.sfgov.org/#!/simple. Enter the block number 3793 and lot number 028. IMPORTANT: Leave all other fields blank. Hit search. return the list of names that appears on the page and end immediately - don't navigate on the page."
    agent = Agent(task=task, llm=llm)
    history=await agent.run(max_steps=20)
    result = history.final_result()
    if not result:
        raise Exception(f"Browser use returned None!")
    print(f"{result=}")

if __name__ == "__main__":
    asyncio.run(main())
