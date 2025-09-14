from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
import asyncio
import os 

load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = "false"

async def main():
    llm = ChatOpenAI(model="gpt-4.1")
    task = "Go to this url https://recorder.sfgov.org/#!/simple. Enter the block number 3793 and lot number 028. Ignore all other fields and hit search. List the names of the owners for all the documents "
    agent = Agent(task=task, llm=llm)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
