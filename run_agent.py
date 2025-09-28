import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# Load environment variables from .env file
load_dotenv()

# Get environment variables
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_agent_id = os.getenv("AZURE_AGENT_ID")

if not azure_endpoint or not azure_agent_id:
    raise ValueError("Please set AZURE_ENDPOINT and AZURE_AGENT_ID environment variables")

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=azure_endpoint)

agent = project.agents.get_agent(azure_agent_id)

thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the maximum I can claim for meals?"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")