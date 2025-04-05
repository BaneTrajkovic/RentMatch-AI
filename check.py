from google import genai
from constants import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

contents = input()
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=contents
)
print(response.text)