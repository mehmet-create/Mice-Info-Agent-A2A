import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import MiceInfoAgent
from django.http import JsonResponse
from django.conf import settings

# This key is currently unused here but kept for completeness, 
# as it will be used inside the MiceInfoAgent service.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 

# Instantiate the agent once for efficiency.
# NOTE: This agent class MUST be defined in chat_app/services.py
AGENT_INSTANCE = MiceInfoAgent()

class AgentCardView(APIView):
    """
    Handles the /.well-known/agent.json request.
    This view reads the static agent.json file and serves it with the correct
    Content-Type.
    """
    # Webhooks and discovery endpoints must allow unauthenticated access.
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        """Reads and returns the agent.json file content."""
        agent_card_path = os.path.join(settings.BASE_DIR, 'chat_app', 'agent.json')
        
        if not os.path.exists(agent_card_path):
            return Response({"error": "Agent card file not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(agent_card_path, 'r') as f:
                agent_data = json.load(f)
            
            # JsonResponse is used to ensure the Content-Type is application/json
            return JsonResponse(agent_data)
        except Exception as e:
            print(f"Error reading agent.json: {e}")
            return Response({"error": "Error processing agent card."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class A2AAgentView(APIView):
    """
    Handles the main Agent-to-Agent webhook endpoint (/api/a2a/agent).
    This view processes the incoming A2A message (POST request) and returns 
    the agent's response, using the logic previously defined in AgentWebhookView.
    """
    # This is the webhook, so authentication must be disabled.
    permission_classes = ()
    authentication_classes = ()
    
    def post(self, request, *args, **kwargs):
        """Processes an incoming A2A message from Telex."""
        data = request.data
        
        # 1. Input Parsing (Extracting critical A2A fields)
        try:
            # A2A payloads wrap the text in message.content.text
            user_message_text = data['message']['content']['text']
            conversation_id = data['conversation_id']
            incoming_message_id = data['message']['message_id']
        except KeyError as e:
            print(f"A2A Payload Error: Missing key {e}")
            return Response(
                {"error": "Invalid A2A payload format. Check for missing keys."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Core Logic Execution - Delegation to the service class
            ai_response_text = AGENT_INSTANCE.get_mouse_info(user_message_text)

            # 3. Output Formatting (Construct the required A2A response payload)
            response_payload = {
                "role": "agent",
                "content": {
                    "type": "text",
                    "text": ai_response_text
                },
                # CRUCIAL: IDs must match the incoming message for Telex.im to route the reply
                "parent_message_id": incoming_message_id, 
                "conversation_id": conversation_id,
                "message_id": os.urandom(16).hex() # Generate a simple unique response ID
            }

            # Return the A2A JSON payload with a 200 OK status
            return Response(response_payload, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch errors during agent execution or response construction
            print(f"Error processing A2A request: {e}")
            return Response({"error": f"Agent processing failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
