from django.urls import path
from .views import AgentCardView, A2AAgentView # Imports only the two required views

urlpatterns = [
    # Path for the discovery file
    path('.well-known/agent.json', AgentCardView.as_view(), name='agent_card'),
    
    # Path for the A2A webhook endpoint (The primary endpoint for Telex)
    path('api/a2a/agent', A2AAgentView.as_view(), name='a2a_agent'),
]