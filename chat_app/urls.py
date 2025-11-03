from django.urls import path
from .views import AgentCardView, A2AAgentView

urlpatterns = [
    # Path for the discovery file
    path('.well-known/agent.json', AgentCardView.as_view(), name='agent_card'),
    
    # FIX: The path must include the agent ID for the A2A standard
    # We will use 'mice-info-agent' as the static ID here.
    path('a2a/agent/mice-info-agent', A2AAgentView.as_view(), name='a2a_agent'),
]