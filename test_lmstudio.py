from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct-v0.3",
    messages=[
        {"role": "user", "content": "Explain AI in simple words"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
