from django.urls import path
from .views import AgentCardView, A2AAgentView # Imports only the two required views

urlpatterns = [
    # Path for the discovery file
    path('.well-known/agent.json', AgentCardView.as_view(), name='agent_card'),
    
    # CRITICAL FIX: Use a dynamic path to capture the agent ID.
    # This allows the URL to be: .../a2a/agent/mice-info-agent
    path('a2a/agent/<str:agent_id>', A2AAgentView.as_view(), name='a2a_agent'),
]