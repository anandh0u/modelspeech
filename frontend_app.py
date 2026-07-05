"""
Modern ChatGPT-like Interface using Gradio Blocks

Production-ready UI with authentication, wallet display, and chat interface.
"""

import gradio as gr
import requests
from typing import Optional, List, Tuple
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Global state
current_token: Optional[str] = None
current_user: Optional[dict] = None


# API Helper Functions

def api_request(endpoint: str, method: str = "GET", data: dict = None, auth: bool = True):
    """Make API request with authentication."""
    headers = {}
    
    if auth and current_token:
        headers["Authorization"] = f"Bearer {current_token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# Authentication Functions

def register_user(email: str, username: str, password: str, full_name: str) -> Tuple[str, bool]:
    """Register new user."""
    global current_token, current_user
    
    if not email or not username or not password:
        return "Please fill all required fields", False
    
    result = api_request("/auth/register", "POST", {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name
    }, auth=False)
    
    if "error" in result:
        return f"Registration failed: {result['error']}", False
    
    # Auto-login after registration
    login_result = api_request("/auth/login", "POST", {
        "email": email,
        "password": password
    }, auth=False)
    
    if "access_token" in login_result:
        current_token = login_result["access_token"]
        
        # Get user profile
        current_user = api_request("/auth/me")
        
        return f"✅ Welcome {username}! You have {current_user['wallet_balance']} free credits.", True
    
    return "✅ Registration successful! Please login.", True


def login_user(email: str, password: str) -> Tuple[str, bool, dict]:
    """Login user."""
    global current_token, current_user
    
    if not email or not password:
        return "Please enter email and password", False, gr.update()
    
    result = api_request("/auth/login", "POST", {
        "email": email,
        "password": password
    }, auth=False)
    
    if "error" in result:
        return f"Login failed: {result['error']}", False, gr.update()
    
    current_token = result["access_token"]
    
    # Get user profile
    current_user = api_request("/auth/me")
    
    if "error" in current_user:
        return f"Failed to load profile: {current_user['error']}", False, gr.update()
    
    welcome_msg = f"✅ Welcome back, {current_user['username']}!\n\n"
    welcome_msg += f"💰 Balance: {current_user['wallet_balance']:.2f} credits\n"
    welcome_msg += f"📦 Plan: {current_user['subscription_plan'].upper()}\n"
    
    # Show chat interface
    return welcome_msg, True, gr.update(visible=True)


def logout_user():
    """Logout user."""
    global current_token, current_user
    current_token = None
    current_user = None
    return "Logged out successfully", gr.update(visible=False)


# Chat Functions

def send_chat_message(
    message: str,
    chat_history: List,
    session_id: Optional[str]
) -> Tuple[List, str, str, str]:
    """Send chat message and get response."""
    global current_token
    
    if not current_token:
        return chat_history, "", "Please login first", session_id
    
    if not message:
        return chat_history, "", "Please enter a message", session_id
    
    # Call API
    result = api_request("/chat", "POST", {
        "message": message,
        "session_id": session_id,
        "input_type": "text"
    })
    
    if "error" in result:
        return chat_history, "", f"Error: {result['error']}", session_id
    
    # Format response
    emotion = result["emotion"]
    confidence = result["confidence"]
    has_memory = result["has_memory_context"]
    memory_count = result["memory_contexts_used"]
    credits_used = result["credits_used"]
    
    response = f"**Emotion Detected:** {emotion.upper()} ({confidence:.1%} confidence)\n\n"
    
    if has_memory:
        response += f"🧠 **Memory Context:** Using {memory_count} past interaction(s)\n\n"
    else:
        response += "💭 **No Prior Context** (First interaction or new session)\n\n"
    
    response += f"💰 Credits used: {credits_used}"
    
    # Add to chat history
    chat_history.append((message, response))
    
    # Update wallet balance
    wallet_info = api_request("/wallet")
    balance_msg = f"Balance: {wallet_info['balance']:.2f} credits"
    
    return chat_history, "", balance_msg, result["session_id"]


def load_sessions() -> List[List[str]]:
    """Load user's chat sessions."""
    if not current_token:
        return []
    
    result = api_request("/chat/sessions")
    
    if "error" in result or "sessions" not in result:
        return []
    
    sessions = []
    for s in result["sessions"]:
        sessions.append([
            s["session_id"],
            s["title"],
            str(s["message_count"]),
            f"{s['credits_used']:.2f}",
            s["last_activity"]
        ])
    
    return sessions


def load_session_messages(session_id: str) -> Tuple[List, str]:
    """Load messages from a session."""
    if not current_token or not session_id:
        return [], ""
    
    result = api_request(f"/chat/sessions/{session_id}/messages")
    
    if "error" in result:
        return [], f"Error: {result['error']}"
    
    chat_history = []
    for msg in result["messages"]:
        if msg["role"] == "user":
            # Find next assistant message
            continue
        else:
            # This is assistant message, find previous user message
            user_msg = None
            for m in result["messages"]:
                if m["created_at"] < msg["created_at"] and m["role"] == "user":
                    user_msg = m["content"]
            
            if user_msg:
                emotion_info = f"**Emotion:** {msg['emotion']} ({msg['confidence']:.1%})"
                if msg["had_memory"]:
                    emotion_info += f"\n🧠 Memory context used"
                
                chat_history.append((user_msg, emotion_info))
    
    return chat_history, session_id


def delete_session_func(session_id: str) -> str:
    """Delete a chat session."""
    if not current_token or not session_id:
        return "No session selected"
    
    result = api_request(f"/chat/sessions/{session_id}", "DELETE")
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    return "✅ Session deleted"


# Wallet Functions

def get_wallet_info() -> str:
    """Get wallet information."""
    if not current_token:
        return "Please login to view wallet"
    
    result = api_request("/wallet")
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    info = f"💰 **Current Balance:** {result['balance']:.2f} credits\n\n"
    info += f"📊 **Lifetime Statistics:**\n"
    info += f"   • Total Spent: {result['lifetime_spent']:.2f} credits\n"
    info += f"   • Total Purchased: {result['lifetime_purchased']:.2f} credits\n"
    info += f"   • Currency: {result['currency']}"
    
    return info


def purchase_credits(amount: float) -> str:
    """Purchase credits."""
    if not current_token:
        return "Please login first"
    
    if amount <= 0:
        return "Please enter a valid amount"
    
    result = api_request("/wallet/purchase", "POST", {
        "amount": amount,
        "payment_method": "demo_payment"
    })
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    return f"✅ Successfully purchased {result['credits_added']:.2f} credits!\n\nNew balance: {result['new_balance']:.2f} credits"


def get_subscription_plans() -> str:
    """Get available subscription plans."""
    result = api_request("/subscription/plans", auth=False)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    plans_text = "## Available Plans\n\n"
    
    for plan_id, plan in result["plans"].items():
        plans_text += f"### {plan['name']}\n"
        plans_text += f"**Price:** ${plan['price']}/month\n"
        plans_text += f"**Credits:** {plan['monthly_credits']}/month\n"
        plans_text += f"**Features:**\n"
        for feature in plan['features']:
            plans_text += f"  • {feature}\n"
        plans_text += "\n"
    
    return plans_text


def change_subscription(plan: str) -> str:
    """Change subscription plan."""
    if not current_token:
        return "Please login first"
    
    result = api_request("/subscription/change", "POST", {"plan": plan})
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    return f"✅ {result['message']}"


# Usage Stats

def get_usage_stats() -> str:
    """Get usage statistics."""
    if not current_token:
        return "Please login to view stats"
    
    result = api_request("/stats/usage")
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    stats = "## Your Usage Statistics\n\n"
    stats += f"📊 **Total Predictions:** {result['total_predictions']}\n"
    stats += f"💬 **Total Chats:** {result['total_chats']}\n"
    stats += f"💰 **Total Credits Used:** {result['total_credits_used']:.2f}\n"
    stats += f"📅 **This Month:** {result['this_month_credits']:.2f} credits\n"
    stats += f"🎯 **Avg Confidence:** {result['average_emotion_confidence']:.1%}\n"
    
    return stats


# Build Gradio Interface

def create_app():
    """Create the Gradio application."""
    
    with gr.Blocks(
        title="EmoMemory - AI That Never Forgets",
        theme=gr.themes.Soft(primary_hue="blue"),
        css="""
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .wallet-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #667eea;
        }
        """
    ) as app:
        
        # Header
        with gr.Row():
            gr.HTML("""
                <div class="header">
                    <h1>🧠 EmoMemory</h1>
                    <p>Memory-Enabled Emotion AI | Powered by Cognee</p>
                </div>
            """)
        
        # State variables
        session_id_state = gr.State(None)
        
        # Auth Section (visible initially)
        with gr.Group(visible=True) as auth_section:
            gr.Markdown("## 🔐 Login or Register")
            
            with gr.Tabs():
                # Login Tab
                with gr.Tab("Login"):
                    login_email = gr.Textbox(label="Email", placeholder="user@example.com")
                    login_password = gr.Textbox(label="Password", type="password")
                    login_btn = gr.Button("Login", variant="primary")
                    login_status = gr.Textbox(label="Status", interactive=False)
                
                # Register Tab
                with gr.Tab("Register"):
                    reg_email = gr.Textbox(label="Email*", placeholder="user@example.com")
                    reg_username = gr.Textbox(label="Username*", placeholder="yourusername")
                    reg_password = gr.Textbox(label="Password*", type="password")
                    reg_full_name = gr.Textbox(label="Full Name", placeholder="John Doe")
                    register_btn = gr.Button("Register", variant="primary")
                    register_status = gr.Textbox(label="Status", interactive=False)
        
        # Main App (hidden initially)
        with gr.Group(visible=False) as main_app:
            
            # Top Bar with User Info
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("## 💬 Chat with EmoMemory")
                with gr.Column(scale=1):
                    wallet_display = gr.Textbox(
                        label="💰 Wallet",
                        value="Balance: 0.00 credits",
                        interactive=False
                    )
                    logout_btn = gr.Button("Logout", size="sm")
            
            # Main Chat Interface
            with gr.Tabs() as tabs:
                
                # Chat Tab
                with gr.Tab("💬 Chat"):
                    with gr.Row():
                        with gr.Column(scale=4):
                            chatbot = gr.Chatbot(
                                label="Conversation",
                                height=500,
                                show_label=False
                            )
                            with gr.Row():
                                chat_input = gr.Textbox(
                                    label="Your Message",
                                    placeholder="Type your message here...",
                                    lines=2,
                                    scale=4
                                )
                                send_btn = gr.Button("Send", scale=1, variant="primary")
                            
                            gr.Examples(
                                examples=[
                                    "I'm so excited about my new project!",
                                    "I'm feeling anxious about tomorrow...",
                                    "Everything is going great today!",
                                    "I'm frustrated with this situation.",
                                    "I feel grateful for all the support."
                                ],
                                inputs=chat_input
                            )
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### 💡 Tips")
                            gr.Markdown("""
                            - Each message costs 0.05 credits
                            - EmoMemory remembers context
                            - First message has no context
                            - Subsequent messages use memory
                            - See emotional patterns over time
                            """)
                            
                            new_chat_btn = gr.Button("🆕 New Chat Session")
                
                # Sessions Tab
                with gr.Tab("📚 Sessions"):
                    sessions_table = gr.Dataframe(
                        headers=["Session ID", "Title", "Messages", "Credits", "Last Activity"],
                        label="Your Chat Sessions",
                        interactive=False
                    )
                    with gr.Row():
                        load_sessions_btn = gr.Button("🔄 Refresh Sessions")
                        delete_session_btn = gr.Button("🗑️ Delete Selected", variant="stop")
                    
                    selected_session = gr.Textbox(label="Selected Session ID", visible=False)
                
                # Wallet Tab
                with gr.Tab("💰 Wallet"):
                    wallet_info_display = gr.Markdown()
                    
                    gr.Markdown("### 💳 Purchase Credits")
                    with gr.Row():
                        purchase_amount = gr.Number(
                            label="Amount (USD)",
                            value=10.0,
                            minimum=1.0,
                            step=1.0
                        )
                        purchase_btn = gr.Button("Purchase", variant="primary")
                    
                    purchase_status = gr.Textbox(label="Status", interactive=False)
                    
                    gr.Markdown("### 📋 Pricing")
                    gr.Markdown("**$1 = 10 credits**")
                    gr.Markdown("""
                    - Chat message: 0.05 credits
                    - Emotion prediction: 0.10 credits
                    - Memory query: 0.02 credits
                    - Cognify operation: 1.00 credits
                    """)
                
                # Subscription Tab
                with gr.Tab("📦 Subscription"):
                    plans_display = gr.Markdown()
                    
                    gr.Markdown("### Change Plan")
                    plan_choice = gr.Radio(
                        choices=["free", "starter", "professional", "enterprise"],
                        label="Select Plan",
                        value="free"
                    )
                    change_plan_btn = gr.Button("Change Plan", variant="primary")
                    plan_status = gr.Textbox(label="Status", interactive=False)
                
                # Stats Tab
                with gr.Tab("📊 Usage Stats"):
                    stats_display = gr.Markdown()
                    refresh_stats_btn = gr.Button("🔄 Refresh Stats")
                
                # About Tab
                with gr.Tab("ℹ️ About"):
                    gr.Markdown("""
                    # About EmoMemory
                    
                    **EmoMemory** is a memory-enabled emotion intelligence system powered by Cognee.
                    
                    ## Key Features
                    
                    - 🧠 **Persistent Memory** - Remembers your emotional context across sessions
                    - 🎭 **Emotion Detection** - Analyzes emotions in text, audio, and video
                    - 📈 **Pattern Analysis** - Identifies emotional trends over time
                    - 🔒 **Privacy First** - Your data is secure and GDPR compliant
                    
                    ## How It Works
                    
                    1. **You chat** - Share your thoughts and feelings
                    2. **We analyze** - Detect emotions with AI
                    3. **Memory saves** - Context stored in Cognee
                    4. **Context flows** - Future chats use past context
                    
                    ## Pricing
                    
                    - **Free Tier:** 100 credits/month
                    - **Starter:** $9.99/month - 1,000 credits
                    - **Professional:** $49.99/month - 10,000 credits
                    - **Enterprise:** $199.99/month - 100,000 credits
                    
                    ## Built With
                    
                    - **Cognee** - Hybrid graph-vector memory
                    - **FastAPI** - High-performance API
                    - **Gradio** - Interactive UI
                    - **PostgreSQL** - Reliable database
                    
                    ---
                    
                    **Version:** 1.0.0 | **Support:** support@emomemory.app
                    """)
        
        # Event Handlers
        
        # Authentication
        login_btn.click(
            fn=login_user,
            inputs=[login_email, login_password],
            outputs=[login_status, auth_section, main_app]
        )
        
        register_btn.click(
            fn=register_user,
            inputs=[reg_email, reg_username, reg_password, reg_full_name],
            outputs=[register_status, auth_section]
        )
        
        logout_btn.click(
            fn=logout_user,
            outputs=[login_status, main_app]
        ).then(
            fn=lambda: gr.update(visible=True),
            outputs=[auth_section]
        )
        
        # Chat
        send_btn.click(
            fn=send_chat_message,
            inputs=[chat_input, chatbot, session_id_state],
            outputs=[chatbot, chat_input, wallet_display, session_id_state]
        )
        
        chat_input.submit(
            fn=send_chat_message,
            inputs=[chat_input, chatbot, session_id_state],
            outputs=[chatbot, chat_input, wallet_display, session_id_state]
        )
        
        new_chat_btn.click(
            fn=lambda: ([], None, "Started new chat session"),
            outputs=[chatbot, session_id_state, wallet_display]
        )
        
        # Sessions
        load_sessions_btn.click(
            fn=load_sessions,
            outputs=[sessions_table]
        )
        
        # Wallet
        tabs.select(
            fn=get_wallet_info,
            outputs=[wallet_info_display],
            inputs=None
        )
        
        purchase_btn.click(
            fn=purchase_credits,
            inputs=[purchase_amount],
            outputs=[purchase_status]
        ).then(
            fn=get_wallet_info,
            outputs=[wallet_info_display]
        )
        
        # Subscription
        tabs.select(
            fn=get_subscription_plans,
            outputs=[plans_display],
            inputs=None
        )
        
        change_plan_btn.click(
            fn=change_subscription,
            inputs=[plan_choice],
            outputs=[plan_status]
        )
        
        # Stats
        refresh_stats_btn.click(
            fn=get_usage_stats,
            outputs=[stats_display]
        )
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
