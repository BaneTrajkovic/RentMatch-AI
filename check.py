from google import genai
from constants import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="explain who you are and whether you are capable of taking image input?"
)
print(response.text)