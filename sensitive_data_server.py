import os
from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = "false"

# Option 1: Secrets available for all websites
sensitive_data = company_credentials

# Option 2: Secrets per domain with regex
# sensitive_data = {
#     'https://*.example-staging.com': company_credentials,
#     'http*://test.example.com': company_credentials,
#     'https://example.com': company_credentials,
#     'https://google.com': {'g_email': 'user@gmail.com', 'g_pass': 'google_password'},
# }


agent = Agent(
    task='Log into facebook.com with email ID x_user and password x_pass',
    sensitive_data=sensitive_data,
    use_vision=False,  #  Disable vision to prevent LLM seeing sensitive data in screenshots
    llm=ChatOpenAI(model='gpt-4.1'),
)
async def main():
    await agent.run()