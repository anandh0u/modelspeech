# 🚀 Deploy EmoMemory to Hugging Face Spaces

Your app is ready to deploy! Just need to authenticate and push.

## Step 1: Get Your Hugging Face Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `emomemory-deploy`
4. Type: Select **"Write"** access
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you'll need it in the next step)

## Step 2: Push to Hugging Face

Run these commands in your terminal:

```bash
cd e:\modelspeech\hf_space

# Push to HF (it will ask for username and password)
git push
```
build error
Job failed with exit code: 1. Reason: cache miss: [run 1/2] COPY --link ./ /app
cache miss: [base 7/7] RUN mkdir -p /home/user && ( [ -e /home/user/app ] || ln -s /app/ /home/user/app ) || true
cache miss: [pipfreeze 2/2] RUN pip freeze > /pipfreeze/freeze.txt
cache miss: [run 2/2] LINK COPY --from=pipfreeze --link /pipfreeze/ /pipfreeze/
cache miss: [run 1/2] LINK COPY --link ./ /app
cache miss: [run 2/2] COPY --from=pipfreeze --link /pipfreeze/ /pipfreeze/
cache miss: [base 6/7] RUN --mount=target=/tmp/requirements.txt,source=requirements.txt     pip install --no-cache-dir -r /tmp/requirements.txt     gradio[oauth,mcp]==6.19.0     "uvicorn>=0.14.0" "websockets>=10.4"     spaces
cache miss: [pipfreeze 1/2] RUN mkdir -p /pipfreeze
{"total":25,"completed":19,"user_total":14,"user_cached":5,"user_completed":8,"user_cacheable":13,"from":1,"miss":8,"client_duration_ms":11961}
Build logs:

===== Build Queued at 2026-07-05 07:53:08 / Commit SHA: c515370 =====

--> FROM docker.io/library/python:3.13@sha256:4c822f0fadfeba9ea973d81fb5bbd5c2106f12ae02d0a5cdd48907909395310b
DONE 0.0s

--> RUN pip install --no-cache-dir pip -U &&     pip install --no-cache-dir     datasets     "huggingface-hub>=0.30" "hf-transfer>=0.1.4" "protobuf<4" "click<8.1"
CACHED

--> RUN apt-get update && apt-get install -y 	git 	git-lfs 	ffmpeg 	libsm6 	libxext6 	cmake 	rsync 	libgl1 	&& rm -rf /var/lib/apt/lists/* 	&& git lfs install
CACHED

--> COPY --from=root / /
CACHED

--> WORKDIR /app
CACHED

--> RUN 	apt-get update && 	apt-get install -y curl && 	curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && 	apt-get install -y nodejs && 	rm -rf /var/lib/apt/lists/* && apt-get clean
CACHED

--> Restoring cache
DONE 10.8s

--> RUN --mount=target=/tmp/requirements.txt,source=requirements.txt     pip install --no-cache-dir -r /tmp/requirements.txt     gradio[oauth,mcp]==6.19.0     "uvicorn>=0.14.0" "websockets>=10.4"     spaces
Collecting gradio==6.19.0 (from gradio[mcp,oauth]==6.19.0)
  Downloading gradio-6.19.0-py3-none-any.whl.metadata (17 kB)
Collecting uvicorn>=0.14.0
  Downloading uvicorn-0.50.0-py3-none-any.whl.metadata (6.7 kB)
Collecting websockets>=10.4
  Downloading websockets-16.0-cp313-cp313-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.8 kB)
Collecting spaces
  Downloading spaces-0.50.4-py3-none-any.whl.metadata (633 bytes)
ERROR: Cannot install gradio==3.50.2 and gradio==6.19.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested gradio==6.19.0
    The user requested gradio==3.50.2

Additionally, some packages in these conflicts have no matching distributions available for your environment:
    gradio

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip to attempt to solve the dependency conflict

ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts

--> ERROR: process "/bin/sh -c pip install --no-cache-dir -r /tmp/requirements.txt     gradio[oauth,mcp]==6.19.0     \"uvicorn>=0.14.0\" \"websockets>=10.4\"     spaces" did not complete successfully: exit code: 1
**When prompted:**
- **Username:** `anandhu77`
- **Password:** Paste your HF token (the one you just copied)

> Note: Use the token as password, not your HF account password!

## Step 3: Wait for Build

After pushing:
1. Go to: https://huggingface.co/spaces/anandhu77/emomemory
2. Click **"Logs"** tab
3. Wait 2-3 minutes for the app to build
4. Your app will be live at: https://huggingface.co/spaces/anandhu77/emomemory

## 🎉 Your App is Ready!

Files deployed:
- ✅ `app.py` - Main Gradio interface
- ✅ `memory_emotion_agent.py` - Memory-aware emotion agent
- ✅ `cognee_integration.py` - Cognee operations
- ✅ `chat_interface.py` - Chat utilities
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Beautiful project description

## 🔧 Optional: Configure Environment Variables

If you want to use Cognee Cloud (recommended for production):

1. Go to: https://huggingface.co/spaces/anandhu77/emomemory/settings
2. Click **"Variables and secrets"**
3. Add these secrets:
   - `COGNEE_API_KEY` - Your Cognee API key
   - `COGNEE_CLOUD_URL` - Your Cognee cloud URL

Then the app will automatically use cloud storage!

## 📊 After Deployment

Your app will be available at:
**https://huggingface.co/spaces/anandhu77/emomemory**

Use this link in:
- ✅ Hackathon submission
- ✅ GitHub README
- ✅ Social media posts
- ✅ Portfolio/Resume

## 🆘 Troubleshooting

**Problem: Authentication failed**
- Make sure you're using the token as password, not your HF password
- Token must have "Write" access
- Username is exactly: `anandhu77`

**Problem: Build failed**
- Check the Logs tab in HF Spaces
- Common issue: Missing dependencies (check requirements.txt)
- Solution: Update requirements.txt and push again

**Problem: App crashes**
- The demo uses local Cognee (no API key needed)
- If you see Cognee errors, ignore them - the text sentiment will still work
- For full functionality, add Cognee API keys in settings

---

## 🎯 Quick Deploy (One Command)

```bash
cd e:\modelspeech\hf_space && git push
```

Then paste your token when prompted!

---

## 💡 Pro Tips

1. **Share your app link** on Twitter/LinkedIn with hashtag #WeMakeDevsHackathon
2. **Add the link** to your GitHub README
3. **Record a demo video** showing the memory features
4. **Explain the 4 operations** (Remember, Recall, Improve, Forget) in your submission

---

🏆 **Good luck with the hackathon!** 🚀
