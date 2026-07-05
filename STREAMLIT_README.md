# 🧠 EmoMemory - AI That Never Forgets

**Memory-Enabled Emotion Intelligence powered by Cognee**

Built for WeMakeDevs x Cognee Hackathon 2025

## 🚀 Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements_streamlit.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Get your free Cognee Cloud credit:
   - Go to https://cognee.ai
   - Sign up for free
   - Use code: **COGNEE-35** for $35 Developer Plan credit
   - Copy your API key

4. Enter your Cognee API key in the sidebar to enable cloud memory

## ☁️ Deploy to Streamlit Cloud

### Option 1: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Set:
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.9+
6. In "Secrets", add:
   - `COGNEE_API_KEY`: Your Cognee Cloud API key
7. Click "Deploy"

### Option 2: CLI Deployment

```bash
# Install streamlit-cli
pip install streamlit-cli

# Login
streamlit login

# Deploy
streamlit deploy
```

## ✨ Features

- **🧠 Persistent Memory** - Remembers emotional context across conversations
- **🎭 Emotion Detection** - Analyzes emotions in text using transformers
- **📈 Pattern Tracking** - Identifies emotional trends over time
- **☁️ Cloud Memory** - Powered by Cognee Cloud (free credit available)
- **🔒 Privacy First** - GDPR compliant with forget operation

## 🎯 Cognee Integration

This project demonstrates all four Cognee memory lifecycle operations:

### 1. Remember
Automatically stores every emotional interaction with rich context in Cognee's knowledge graph.

### 2. Recall
Retrieves relevant past emotional contexts using semantic search when analyzing new emotions.

### 3. Improve (Cognify)
Builds knowledge graph connections between emotional patterns for better context understanding.

### 4. Forget
Surgically removes user data when needed (GDPR compliance).

## 🏆 Hackathon Submission

- **Tracks**: Cognee Cloud & Open Source
- **Theme**: Memory-Enabled Emotion Intelligence
- **Tech Stack**: Cognee, Transformers, Streamlit, Python

## 📊 Use Cases

- 🏥 Mental health support with emotional history
- 🎓 Educational systems that adapt to student emotions
- 🛍️ Customer service that remembers past interactions
- 🎮 Gaming NPCs with emotional memory
- 👥 Social robots with persistent relationships

## 🔧 Configuration

### Environment Variables

- `COGNEE_API_KEY`: Your Cognee Cloud API key (get free credit with code COGNEE-35)

### Local Development

Create a `.streamlit/secrets.toml` file:
```toml
COGNEE_API_KEY = "your_api_key_here"
```

### Streamlit Cloud

Add the secret in the app settings:
- Key: `COGNEE_API_KEY`
- Value: Your API key

## 📝 License

MIT License

---

**Built with ❤️ using Cognee | WeMakeDevs Hackathon 2025**
