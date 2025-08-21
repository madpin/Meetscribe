import os
import openai
from typing import Dict

async def generate_notes(context: Dict) -> str:
    """
    Generates meeting notes using an LLM (OpenAI's GPT model).

    Args:
        context: A dictionary containing the transcript and other context
                 (calendar event, Jira ticket).

    Returns:
        A string containing the generated notes in Markdown format.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[OpenAI] Warning: OPENAI_API_KEY not set. Skipping note generation.")
        return "Note generation skipped: OPENAI_API_KEY not set."

    if not context.get('transcript'):
        return "Note generation skipped: Transcript is empty."

    # Use the async client from the openai library
    client = openai.AsyncOpenAI(api_key=api_key)

    prompt = _build_prompt(context)

    try:
        print("\n[OpenAI] Generating notes with LLM...")
        response = await client.chat.completions.create(
            model="gpt-4o",  # A powerful and cost-effective choice
            messages=[
                {"role": "system", "content": "You are an expert assistant that creates structured, concise, and actionable meeting notes from transcripts."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        notes = response.choices[0].message.content
        return notes.strip()
    except Exception as e:
        print(f"[OpenAI] Error during note generation: {e}")
        return f"Error generating notes: {e}"

def _build_prompt(context: Dict) -> str:
    """Builds a detailed prompt for the LLM based on the available context."""

    transcript = context.get('transcript')

    prompt_parts = [
        "Please generate structured meeting notes in Markdown format from the following transcript.",
        "The notes must include the following sections: '## Summary', '## Key Decisions', and '## Action Items'.",
        "Ensure the action items are clear and assignable.",
    ]

    # Add context from Google Calendar if available
    if context.get('calendar_event'):
        event = context['calendar_event']
        prompt_parts.append("\nUse the following calendar event details for context:")
        prompt_parts.append(f"- Meeting Title: {event.get('summary', 'N/A')}")
        prompt_parts.append(f"- Start Time: {event.get('start', 'N/A')}")
        if event.get('description'):
            # Truncate long descriptions to keep the prompt focused
            prompt_parts.append(f"- Description: {event['description'][:250]}...")

    # Add context from Jira if available
    if context.get('jira_ticket'):
        ticket = context['jira_ticket']
        prompt_parts.append("\nThis meeting is directly related to the following Jira ticket:")
        prompt_parts.append(f"- Ticket: {ticket.get('key', 'N/A')} ({ticket.get('url', 'N/A')})")
        prompt_parts.append(f"- Summary: {ticket.get('summary', 'N/A')}")
        prompt_parts.append(f"- Status: {ticket.get('status', 'N/A')}")

    prompt_parts.append("\n--- MEETING TRANSCRIPT ---")
    prompt_parts.append(transcript)
    prompt_parts.append("--- END TRANSCRIPT ---")

    prompt_parts.append("\nNow, generate the notes based on all the provided information.")

    return "\n".join(prompt_parts)
