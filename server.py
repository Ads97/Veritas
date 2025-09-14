# from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
# Basics

from browser_use import Agent, Browser, ChatOpenAI

browser = Browser(
	headless=False,  # Show browser window
	window_size={'width': 1000, 'height': 700},  # Set window size
)

agent = Agent(
	task='Search for Browser Use',
	browser=browser,
	llm=ChatOpenAI(model='gpt-4.1-mini'),
)


async def main():
	await agent.run()


# # Connect to your existing Chrome browser
# async def main():
#     # print("hi1")
#     browser = Browser(
# 	headless=False,  # Show browser window
# 	window_size={'width': 1000, 'height': 700},  # Set window size
# )
# #     browser = Browser(
# #     executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
# #     user_data_dir='~/Library/Application Support/Google/Chrome',
# #     profile_directory='Advaith',
# # )
#     agent = Agent(
#     task='Visit https://duckduckgo.com and search for "browser-use founders"',
#     browser=browser,
#     llm=ChatOpenAI(model='gpt-5'),
# )
#     history = await agent.run(max_steps=1000)
#     # print("hi")
#     # print(f"{history.is_successful()=}")       # Check if agent completed successfully (returns None if not done)
#     # print(f"{history.urls()=}")
#     # print(f"{history.action_names()=}")
#     # print(f"{history.errors()=}")
#     # print(f"{history.model_actions()=}")
