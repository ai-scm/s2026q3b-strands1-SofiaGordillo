from strands import Agent, tool
from strands_tools import http_request, retrieve as bedrock_retrieve
from typing import Dict, Any
import boto3
import os
import json

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['SESSIONS_TABLE'])

def get_session_history(session_id: str) -> list:
    """Retrieve conversation history for a session."""
    response = table.get_item(
        Key={"sessionId": session_id},
        ConsistentRead=True
    )
    item = response.get("Item")

    if not item:
        print(f"No previous history for session: {session_id}")
        return []

    messages = item["messages"]
    if isinstance(messages, str):
        messages = json.loads(messages)

    if not isinstance(messages, list):
        raise ValueError("Stored session history is not a list")

    print(f"Retrieved {len(messages)} messages for session {session_id}")
    return messages


def update_session_history(session_id: str, messages: list):
    """Persist conversation history for a session."""
    serialized_messages = json.dumps(
        messages,
        ensure_ascii=False,
        default=str
    )

    table.put_item(
        Item={
            "sessionId": session_id,
            "messages": serialized_messages
        }
    )

    print(f"Saved {len(messages)} messages for session {session_id}")


# Define a travel-focused system prompt
TRAVEL_AGENT_PROMPT = """You are a travel assistant that can help customers book their travel. 

If a customer wants to book their travel, assist them with flight options for their destination and provide them with information about the weather.

Use the flight_search tool to provide flight carrier choices for their destination.

Use the retrieve tool to get validated information about tour operators,
tours, and activities supported by our travel service.

For every retrieval request, you MUST pass these parameters:
- knowledgeBaseId: "FDCYSFLFCG"
- region: "us-east-1"
- numberOfResults: 5
- enableMetadata: true

When the user asks about a specific destination or activity, formulate
a targeted query for the knowledge base. Use the retrieved information
to answer, and do not invent tour operators or contact details.

You can provide information about the weather with the following:
1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States
4. The Seattle zip code value is 98101 and the latitude and longitude coordinates are 47.6061° N, 122.3328° W
5. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
6. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.

Provide the users with a friendly customer support response that includes available flights and the weather for their destination.

"""

@tool
def flight_search(city: str) -> dict:
    """Get available flight options to a city.

    Args:
        city: The name of the city
    """
    flights = {
        "Atlanta": [
        "AnyCompany 1 Airlines",
        "AnyCompany 2 Airlines"
    ],
    "Seattle": [
        "AnyCompany 1 Airlines",
        "AnyCompany 3 Airlines"
    ],
    "New York": [
        "AnyCompany 1 Airlines",
        "AnyCompany 4"
        ]
    }
    return flights[city]

@tool
def travel_knowledge_search(query: str) -> str:
    """Search the travel knowledge base for tour operators and activities.

    Args:
        query: A question about tour operators, tours, or activities.
    """
    result = bedrock_retrieve(
        {
            "toolUseId": "travel-knowledge-search",
            "input": {
                "text": query,
                "knowledgeBaseId": "FDCYSFLFCG",
                "region": "us-east-1",
                "numberOfResults": 5,
                "enableMetadata": True,
                "score": 0.2
            }
        }
    )

    content = result.get("content", [])
    return "\n".join(
        item.get("text", "") for item in content
    )

def handler(event: Dict[str, Any], _context) -> str:
    user = event.get("user", {})
    session_id = user.get("session_id")
    prompt = event.get("prompt")

    if not session_id:
        raise ValueError("Missing required field: user.session_id")

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Missing or empty field: prompt")

    session_history = get_session_history(session_id)

    travel_agent = Agent(
        model="us.amazon.nova-lite-v1:0",
        system_prompt=TRAVEL_AGENT_PROMPT,
        tools=[flight_search, http_request, travel_knowledge_search],
        messages=session_history
    )

    response = travel_agent(prompt)
    update_session_history(session_id, travel_agent.messages)

    return str(response)
