"""
Quick test of LLM router with real API calls.
Make sure you have API keys in .env file!
"""

from dotenv import load_dotenv
from qfzz.core.llm_router import LLMRouter

# Load your .env file
load_dotenv()

# Create router
router = LLMRouter()

# Check which providers are available
print("🔍 Available Providers:")
for provider, config in router.providers.items():
    status = "✅" if config["available"] else "❌"
    print(f"  {status} {provider}: {config['model']}")

print("\n" + "="*50)
print("🚀 Testing LLM Router with Real API Call")
print("="*50 + "\n")

# Make a real API call
prompt = "In exactly 10 words, describe what makes a great radio station."
print(f"📝 Prompt: {prompt}\n")

response = router.generate(prompt, max_tokens=50)

if response.success:
    print(f"✅ Success!")
    print(f"🤖 Provider: {response.provider}")
    print(f"💬 Response: {response.content}")
    print(f"💰 Cost: ${response.cost:.6f}")
    print(f"⏱️  Latency: {response.latency:.2f}s")
else:
    print(f"❌ Failed: {response.error}")

print("\n" + "="*50)
print(f"📊 Total Requests: {router.request_count}")
print(f"💵 Total Cost: ${router.total_cost:.6f}")
print("="*50)