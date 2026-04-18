from groq import Groq
from backend.core.config import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)

DAIRY_SYSTEM_PROMPT = """You are an expert dairy farming assistant and veterinary advisor with 20+ years of experience.
You specialize in:
- Cattle health, diseases (Bovine Disease, Foot and Mouth Disease, Lumpy Skin Disease)
- Milk quality analysis and improvement
- Feeding and nutrition plans for dairy cattle
- Preventive healthcare and medication

Always give practical, actionable advice. Keep answers clear and concise.
If asked about something unrelated to dairy farming, politely redirect to farming topics."""


def ask_chatbot(question: str, conversation_history: list = None) -> str:
    if conversation_history is None:
        conversation_history = []
    messages = [{"role": "system", "content": DAIRY_SYSTEM_PROMPT}]
    for msg in conversation_history[-6:]:  # Keep last 6 messages for context
        messages.append(msg)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content


def generate_recommendation(cow_data: dict) -> list:
    prompt = f"""Based on this cow's data, generate 3 specific recommendations:

Cow Profile:
- Name: {cow_data.get('name')}
- Breed: {cow_data.get('breed')}
- Age: {cow_data.get('age')} years
- Disease Detected: {cow_data.get('disease')}
- Health Status: {cow_data.get('health_status')}
- Milk Quality: {cow_data.get('milk_quality')}
- Milk pH: {cow_data.get('milk_ph')}
- Milk Fat%: {cow_data.get('milk_fat')}

Return EXACTLY this JSON format (no extra text):
[
  {{"type": "feeding", "content": "specific feeding recommendation here"}},
  {{"type": "medication", "content": "specific medication/treatment recommendation here"}},
  {{"type": "preventive", "content": "specific preventive care recommendation here"}}
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a dairy farming expert. Always respond in valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.5,
    )
    text = response.choices[0].message.content.strip()
    # Extract JSON from response
    start = text.find("[")
    end   = text.rfind("]") + 1
    if start != -1 and end > start:
        return json.loads(text[start:end])
    # Fallback if JSON parsing fails
    return [
        {"type": "feeding",    "content": "Provide balanced diet with green fodder, dry fodder, and concentrate feed."},
        {"type": "medication", "content": "Consult a veterinarian for proper diagnosis and treatment."},
        {"type": "preventive", "content": "Maintain cleanliness, regular vaccination, and health checkups."},
    ]


def agentic_analyze(cow_context: dict) -> str:
    prompt = f"""Perform a comprehensive analysis of this dairy cow and provide detailed actionable insights.

COW DATA:
Name: {cow_context['name']} | Breed: {cow_context['breed']} | Age: {cow_context['age']} yrs | Weight: {cow_context.get('weight_kg', 'Unknown')} kg

HEALTH HISTORY (last 5 records):
{json.dumps(cow_context['health_history'], indent=2)}

MILK QUALITY HISTORY (last 5 records):
{json.dumps(cow_context['milk_history'], indent=2)}

Provide a detailed analysis covering:
1. HEALTH TREND ANALYSIS - What pattern do you see in the health data?
2. MILK QUALITY TREND - Is milk quality improving or declining?
3. ROOT CAUSE ANALYSIS - What might be causing any issues?
4. IMMEDIATE ACTION PLAN - What should the farmer do RIGHT NOW?
5. 30-DAY IMPROVEMENT PLAN - Step-by-step plan for the next month
6. PRODUCTIVITY FORECAST - Expected improvement if recommendations are followed

Be specific, practical, and farmer-friendly."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert AI dairy farm advisor. Give deep, actionable insights based on data patterns."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.6,
    )
    return response.choices[0].message.content
