from browser_use import Agent, ChatOpenAI, Browser
from dotenv import load_dotenv
import asyncio
import os 

load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = "false"

fb_user = os.environ['FB_EMAIL']
fb_password = os.environ['FB_PASSWORD']

async def main():
    
    company_credentials = {'x_user': fb_user, 'x_pass': fb_password}
    llm = ChatOpenAI(model="gpt-4.1")
    task = "Go to this url https://www.facebook.com/groups/746424749257725/user/100066500240746 and find the user's name. Use login credentials x_user for email and x_pass for password"
    browser = Browser(
    executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    user_data_dir='~/Library/Application Support/Google/Chrome',
    profile_directory='Advaith',
)
    agent = Agent(task=task, llm=llm, sensitive_data=company_credentials, browser=browser)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
