from gradio_client import Client

SPACE = "Pepe104/MiniMax-H3-Turbo-LoRA-UNCENSORED"

client = Client(SPACE)

print("Testing video generation...")

result = client.predict(
    prompt="A cinematic shot of a mysterious woman walking through a dark forest at night, realistic lighting, thriller atmosphere",
    api_name="/generate"
)

print("\n========== RESULT ==========")
print(result)
print("============================")