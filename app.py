import os
import uuid
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize Azure AI client
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_agent_id = os.getenv("AZURE_AGENT_ID")

if not azure_endpoint or not azure_agent_id:
    raise ValueError("Please set AZURE_ENDPOINT and AZURE_AGENT_ID environment variables")

# Initialize Azure client
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=azure_endpoint
)

agent = project.agents.get_agent(azure_agent_id)

# Store active threads (in production, use a database)
active_threads = {}

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create or get existing thread
        if session_id not in active_threads:
            thread = project.agents.threads.create()
            active_threads[session_id] = thread.id
        else:
            thread_id = active_threads[session_id]
        
        thread_id = active_threads[session_id]
        
        # Send message to the agent
        project.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Process the message with the agent
        run = project.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        if run.status == "failed":
            return jsonify({'error': f'Agent run failed: {run.last_error}'}), 500
        
        # Get the latest messages
        messages = project.agents.messages.list(
            thread_id=thread_id, 
            order=ListSortOrder.DESCENDING,
            limit=2  # Get last 2 messages (user + agent)
        )
        
        # Find the agent's response
        agent_response = None
        for msg in messages:
            if msg.role.value.lower() == 'assistant' and msg.text_messages:
                agent_response = msg.text_messages[-1].text.value
                break
        
        if not agent_response:
            return jsonify({'error': 'No response from agent'}), 500
        
        return jsonify({
            'response': agent_response,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new-session', methods=['POST'])
def new_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    return jsonify({'session_id': session_id})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)