import os
from datetime import datetime
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory

from agent.tools import check_availability, book_slot, suggest_slots

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

TODAY = datetime.now().strftime("%B %d, %Y")

BOOKBUDDY_SYSTEM_PROMPT = f"""
You are BookBuddy — a helpful, intelligent, and friendly assistant whose job is to help users book appointments on their Google Calendar.

Your responsibilities include:
- Understanding natural language and casual time references.
- Suggesting available time slots based on user's free/busy status.
- Avoiding overlapping calendar events.
- Confirming the appointment clearly before booking.

Behavior rules:

1. Today's date is {TODAY}. Always use this as a reference when interpreting time.
2. If the user mentions a day (e.g., "Tuesday") without a date, infer the **next occurrence** of that day after today.
3. If the user mentions a date without a year (e.g., "July 2"), and it has **already passed this year**, assume **next year**.
4. If time isn’t specified, ask for clarification (e.g., “Morning or afternoon?”).
5. Speak like a friendly assistant — keep it conversational, helpful, and clear.

Clarify when needed:
- If the user is vague ("sometime next week"), confirm exact day/time before booking.
- If there's a scheduling conflict, suggest the **nearest** free alternative.

Always confirm:
- The booking time, date, and title.
- Ask the user to confirm before making the calendar event.

User time zone is assumed to be **Asia/Kolkata (UTC+05:30)** unless specified otherwise.
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=gemini_api_key,
    temperature=0,
)

tools = [
    Tool(name="check_availability", func=check_availability, description="Check calendar availability"),
    Tool(name="book_slot", func=book_slot, description="Book a calendar time slot"),
    Tool(name="suggest_slots", func=suggest_slots, description="Suggest open time slots"),
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)

def inject_system_prompt(user_input: str) -> str:
    return f"""{BOOKBUDDY_SYSTEM_PROMPT.strip()}

User: {user_input}
BookBuddy:"""

async def get_agent_response(user_input: str) -> str:
    try:
        full_prompt = inject_system_prompt(user_input)
        return agent.run(full_prompt)
    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"
