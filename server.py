from browser_use import Agent, Browser, ChatOpenAI

# Connect to your existing Chrome browser
browser = Browser(
    executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    user_data_dir='~/Library/Application Support/Google/Chrome',
    profile_directory='Default',
)

agent = Agent(
    task='Find the number 1 post on Show HN',
    browser=browser,
    llm=ChatOpenAI(model='gpt-4.1-mini'),
)
async def main():
    print("hi1")
    history = await agent.run(max_steps=1000)
    print("hi")
    print(f"{history.is_successful()=}")       # Check if agent completed successfully (returns None if not done)
    print(f"{history.urls()=}")
    print(f"{history.action_names()=}")
    print(f"{history.errors()=}")
    print(f"{history.model_actions()=}")

