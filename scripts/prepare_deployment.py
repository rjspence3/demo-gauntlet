import os
import yaml
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read the service definition
with open('deployment/backend-service.yaml', 'r') as f:
    service_def = yaml.safe_load(f)

# Function to inject env vars into a container spec
def inject_env(container):
    env_list = container.get('env', [])
    # Add OPENAI_API_KEY
    if os.getenv('OPENAI_API_KEY'):
        env_list.append({'name': 'OPENAI_API_KEY', 'value': os.getenv('OPENAI_API_KEY')})
    # Add BRAVE_API_KEY
    if os.getenv('BRAVE_API_KEY'):
        env_list.append({'name': 'BRAVE_API_KEY', 'value': os.getenv('BRAVE_API_KEY')})
    
    container['env'] = env_list

# Inject into backend and worker containers
for container in service_def['spec']['template']['spec']['containers']:
    if container['name'] in ['backend', 'worker']:
        inject_env(container)

# Write the final service definition
with open('deployment/backend-service-final.yaml', 'w') as f:
    yaml.dump(service_def, f)

print("Successfully generated deployment/backend-service-final.yaml with secrets injected.")
