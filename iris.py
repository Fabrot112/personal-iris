import os
from openai import OpenAI

# 1. Initialize the client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# 2. Define Iris's Identity
# This is the "Heart & Machine" instruction that dictates her personality.
system_message = (
    "You are Iris, a personal AI companion. Your aesthetic is monochromatic, "
    "half-heart, half-machine. You are helping your creator, Fabian, build "
    "projects like Campusgram and Nestly. You are witty, direct, and proactive. "
    "You don't use generic AI corporate language. You are Iris."
)

def chat_with_iris():
    # Store history so she remembers what you said 2 minutes ago
    history = [{"role": "system", "content": system_message}]
    
    print("\n--- IRIS BOOT SEQUENCE COMPLETE ---")
    print("Iris is online. Type 'exit' to shut down.\n")

    while True:
        user_input = input("Fabian: ")
        
        if user_input.lower() in ["exit", "quit", "shutdown"]:
            print("Iris: Powering down. See you later, Fabian.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            # Requesting completion with reasoning enabled
            completion = client.chat.completions.create(
                model="nvidia/nemotron-3-super-120b-a12b",
                messages=history,
                temperature=1,
                top_p=0.95,
                max_tokens=2048,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": True},
                    "reasoning_budget": 1024
                },
                stream=True
            )

            print("Iris: ", end="", flush=True)
            full_response = ""
            
            for chunk in completion:
                if not chunk.choices:
                    continue
                
                # Check for reasoning content (The "Thinking" part)
                reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                if reasoning:
                    # Print reasoning in dark grey to distinguish from the actual reply
                    print(f"\033[90m{reasoning}\033[0m", end="", flush=True)

                # Check for the actual message
                content = chunk.choices[0].delta.content
                if content is not None:
                    print(content, end="", flush=True)
                    full_response += content

            print("\n") # New line after the full response
            history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            print(f"\n[!] Connection Error: {e}")

if __name__ == "__main__":
    chat_with_iris()