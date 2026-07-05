# ⚡ EmoMemory Quick Start Guide

**Get up and running in 5 minutes!**

---

## 🚀 Installation (2 minutes)

### Option 1: Automated Setup
```bash
cd e:\modelspeech
python setup.py
```

### Option 2: Manual Setup
```bash
cd e:\modelspeech

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🎮 Run Demos (3 minutes)

### Demo 1: Web Application (Recommended)
```bash
python web_demo.py
```
Then open: **http://localhost:7860**

**Try this:**
1. Go to "Stateless vs Stateful Comparison" tab
2. Type: "I just started a new job!"
3. Click "Compare Predictions"
4. Type: "I'm nervous about my team..."
5. Click "Compare Predictions" again
6. **See the difference!** ⚡

### Demo 2: CLI Conversation
```bash
python chat_interface.py
```

Watch a pre-scripted conversation that demonstrates memory in action!

### Demo 3: Interactive Chat
```bash
python chat_interface.py interactive
```

Chat with the AI yourself and see it remember your context!

---

## 🧪 Test Memory Operations

### Test REMEMBER
```python
import asyncio
from cognee_integration import create_memory_manager, EmotionalMemory

async def test():
    manager = create_memory_manager()
    
    memory = EmotionalMemory(
        user_id="test_user",
        timestamp="2025-07-05T10:00:00Z",
        input_type="text",
        emotion_label="happy",
        emotion_confidence=0.92,
        raw_input_summary="Testing remember operation",
        context={}
    )
    
    await manager.remember(memory)
    print("✅ Memory stored!")

asyncio.run(test())
```

### Test RECALL
```python
import asyncio
from cognee_integration import create_memory_manager

async def test():
    manager = create_memory_manager()
    
    results = await manager.recall(
        query="test_user emotional history",
        user_id="test_user",
        limit=5
    )
    
    print(f"✅ Recalled {len(results)} memories")

asyncio.run(test())
```

### Test IMPROVE
```python
import asyncio
from cognee_integration import create_memory_manager

async def test():
    manager = create_memory_manager()
    
    await manager.improve()
    print("✅ Memory improved (knowledge graph built)")

asyncio.run(test())
```

### Test FORGET
```python
import asyncio
from cognee_integration import create_memory_manager

async def test():
    manager = create_memory_manager()
    
    await manager.forget(user_id="test_user")
    print("✅ User data forgotten")

asyncio.run(test())
```

---

## 🌐 For Cognee Cloud

If you have the $35 Developer Plan:

```bash
# Windows
set COGNEE_API_KEY=your_api_key_here

# Linux/Mac
export COGNEE_API_KEY=your_api_key_here
```

Or create `.env` file:
```
COGNEE_API_KEY=your_api_key_here
```

Then run with cloud enabled:
```python
from memory_emotion_agent import create_memory_agent

agent = await create_memory_agent(
    api_key="your_api_key",
    use_cloud=True  # Enable cloud
)
```

---

## 🎬 Quick Web Demo Tour

### Tab 1: Stateless vs Stateful Comparison
**Purpose:** See the difference memory makes

**Test Flow:**
1. Enter user ID: `demo_user`
2. Message 1: "I'm excited about my new project!"
3. Compare → See both predictions
4. Message 2: "But I'm worried about the deadline..."
5. Compare → See memory context kick in!

### Tab 2: Memory-Enabled Chat
**Purpose:** Have a conversation with memory

**Test Flow:**
1. Start new session for `demo_user`
2. Send: "I just got promoted!"
3. Send: "I'm nervous about managing a team"
4. Send: "My first day went well!"
5. See how context builds across messages

### Tab 3: Memory Management
**Purpose:** Explore memory operations

**Test Flow:**
1. View history for `demo_user`
2. Click "Improve Memory" → Run cognify
3. (Optional) Test "Forget User"

---

## 🐛 Troubleshooting

### Error: "cognee not found"
```bash
pip install cognee
```

### Error: "gradio not found"
```bash
pip install gradio
```

### Error: "Port 7860 already in use"
Edit `web_demo.py`, change:
```python
demo.launch(server_port=7860)  # Change to 7861, 7862, etc.
```

### Web demo not loading?
1. Check if Python process is running
2. Try http://127.0.0.1:7860 instead
3. Check firewall settings
4. Try different port

### "No module named 'agents'"
Your existing emotion detection agents may not be fully implemented.
The demo will work with mock predictions!

---

## 📊 Quick Verification Checklist

After setup, verify these work:

- [ ] `python setup.py` runs without errors
- [ ] `python chat_interface.py` shows demo conversation
- [ ] `python web_demo.py` opens web interface
- [ ] Web interface loads at localhost:7860
- [ ] Can send messages in chat tab
- [ ] Can compare stateless vs stateful
- [ ] Can view memory history

All checked? **You're ready for the hackathon!** 🎉

---

## 🎯 For Judges/Reviewers

**Fastest way to see the project:**

```bash
# 1. Install
cd e:\modelspeech
pip install -r requirements.txt

# 2. Run web demo
python web_demo.py

# 3. Open browser
http://localhost:7860

# 4. Go to "Stateless vs Stateful" tab
# 5. Try a few messages!
```

**Expected time:** 3-5 minutes from clone to demo

---

## 📚 Next Steps

After quick start:

1. **Read README.md** - Full documentation
2. **Read HACKATHON_SUBMISSION.md** - Submission details
3. **Read DEMO_VIDEO_SCRIPT.md** - Video production guide
4. **Explore the code** - See implementation details

---

## 🆘 Need Help?

Check these files:
- `README.md` - Complete guide
- `PROJECT_SUMMARY.md` - Overview
- Code comments - Inline documentation

Or test each component individually:
```bash
# Test memory manager
python -c "from cognee_integration import create_memory_manager; print('✅')"

# Test emotion agent
python -c "from memory_emotion_agent import create_memory_agent; print('✅')"

# Test chat interface
python -c "from chat_interface import ConversationalInterface; print('✅')"
```

---

<div align="center">

## ⚡ You're all set!

**EmoMemory is ready to demonstrate Cognee's power.**

Start with: `python web_demo.py`

Good luck with your hackathon submission! 🚀

</div>
