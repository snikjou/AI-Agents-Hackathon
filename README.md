# AI-Agents-Hackathon
AI Agents Hackathon

## Setup Instructions

### Code Setup
Create codespace on main

### Environment Configuration
Rename `copy.env` to `.env`

On the `.env` file replace the variables with your `AZURE_AGENT_IA` and `AZURE_ENDPOINT`

### Install Azure CLI
Run the following command on the terminal:

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Azure Login
On the terminal:
```bash
az login --use-device-code
```

Select your azure subscription. Just type 1

### Run the Application

```bash
python run_agent.py
```

```bash
python app.py
```

Click on Running on http://127.0.0.1:5000

### Test the Application

Ask this question:

**What's the maximum I can claim for meals?**
