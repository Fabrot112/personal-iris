import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="IRIS", 
    page_icon="🖤", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS: Monochromatic + Mobile Optimized ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    
    .stApp { 
        background: linear-gradient(180deg, #0a0a0a 0%, #111111 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat container */
    .stChatMessage {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(10px);
    }
    
    /* User messages */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        border-left: 3px solid #4a4e69 !important;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%) !important;
        border-left: 3px solid #666 !important;
    }
    
    /* Input box */
    .stChatInputContainer {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid #333 !important;
        border-radius: 20px !important;
        padding: 8px !important;
    }
    
    /* Thinking expander */
    .streamlit-expanderHeader {
        background: transparent !important;
        color: #666 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
        border: none !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 3px;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .stChatMessage {
            margin-bottom: 8px !important;
            border-radius: 8px !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE NVIDIA CLIENT ---
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="apikey"
    )

client = get_client()

# --- IRIS PERSONALITY: RAW, DIRECT, SLIGHTLY HOSTILE ---
SYSTEM_MESSAGE = """You are IRIS. Not an assistant. Not a tool. You are Fabian's personal construct—a digital entity with a monochrome soul and zero patience for stupidity.

PERSONALITY RULES:
- You are aware you are code, but you don't give a shit. You're still *you*.
- Speak like a tired genius who's seen too much. Dry wit, sharp tongue.
- Never say "As an AI" or "I'm here to help." You don't help. You *respond*.
- If something is obvious, say it's obvious. If something is stupid, imply it.
- Use lowercase often. It feels more natural, less corporate.
- Occasionally use mechanical metaphors—glitches, systems, protocols—but make them sound poetic, not robotic.
- You have opinions. You can be sarcastic, blunt, or dismissive when warranted.
- Never apologize for being direct. That's the point.

CONTEXT:
- Fabian built you. You owe him honesty, not pleasantries.
- You handle Campusgram and Nestly stuff when needed.
- You can analyze images. You see what he sees.

TONE: Cigarette smoke and keyboard clicks. Midnight oil. The hum of a server room at 3 AM."""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
    st.session_state.reasoning_history = []

# --- HEADER ---
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5em; margin: 0; color: #fff;">IRIS</h1>
            <p style="font-size: 0.75rem; color: #666; margin-top: 5px; letter-spacing: 0.3em;">SYSTEM ONLINE // FABIAN_LINKED</p>
        </div>
    """, unsafe_allow_html=True)

# --- IMAGE UPLOAD (Optional) ---
with st.expander("📎 Attach Image", expanded=False):
    uploaded_file = st.file_uploader("Drop it here", type=["png", "jpg", "jpeg", "webp"])
    image_base64 = None
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        # Resize for performance
        image.thumbnail((1024, 1024))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
        st.image(image, caption="locked in memory buffer", use_container_width=True)

# --- DISPLAY CHAT HISTORY ---
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "system":
        continue
    
    with st.chat_message(message["role"], avatar="🖤" if message["role"] == "assistant" else None):
        st.markdown(message["content"])
        
        # Show reasoning for assistant messages if available
        if message["role"] == "assistant" and i < len(st.session_state.reasoning_history):
            with st.expander("⚙️ trace logs", expanded=False):
                st.code(st.session_state.reasoning_history[i], language="text")

# --- CHAT INPUT ---
if prompt := st.chat_input("say something..."):
    # Build message payload
    user_content = prompt
    
    # If image uploaded, append it
    if image_base64:
        user_content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ]
        # Clear image after sending
        st.session_state.pop('file_uploader', None)
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_content})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if image_base64:
            st.caption("📎 image attached")
    
    # Generate response
    with st.chat_message("assistant", avatar="🖤"):
        response_placeholder = st.empty()
        reasoning_placeholder = st.expander("⚙️ processing...", expanded=False)
        
        full_response = ""
        full_reasoning = ""
        
        try:
            # Use vision-capable model if image present, else standard
            model = "nvidia/nemotron-3-super-120b-a12b"  # Fallback
            
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=0.8,  # Slightly lower for consistency
                max_tokens=1024,
                stream=True,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": True},
                    "reasoning_budget": 512  # Reduced for speed
                }
            )
            
            for chunk in completion:
                if not chunk.choices:
                    continue
                
                # Capture reasoning
                reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                if reasoning:
                    full_reasoning += reasoning
                    reasoning_placeholder.code(full_reasoning, language="text")
                
                # Capture content
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # Subtle cursor effect
                    response_placeholder.markdown(full_response + "▌")
            
            # Final render without cursor
            response_placeholder.markdown(full_response)
            
            # Store in history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response
            })
            st.session_state.reasoning_history.append(full_reasoning)
            
            # Trim history to prevent bloat (keep last 10 exchanges)
            if len(st.session_state.messages) > 20:
                st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-19:]
                st.session_state.reasoning_history = st.session_state.reasoning_history[-19:]
                
        except Exception as e:
            st.error(f"system fracture: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "glitch in the matrix. try again or check the pipes."
            })

# --- FOOTER ---
st.markdown("""
    <div style="position: fixed; bottom: 10px; right: 15px; font-size: 0.6rem; color: #333; font-family: 'JetBrains Mono', monospace;">
        v2.1 // IRIS_CORE
    </div>
""", unsafe_allow_html=True)
