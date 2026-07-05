# 🚀 Deploy EmoMemory to Streamlit Cloud

## Step 1: Push to GitHub as "emomemory"

```bash
# Navigate to your project
cd e:\modelspeech

# Initialize git if not already
git init

# Add all files
git add .

# Commit
git commit -m "EmoMemory: Memory-Enabled Emotion AI for WeMakeDevs Hackathon"

# Create a NEW repository on GitHub named "emomemory"
# Then:
git remote add origin https://github.com/YOUR_USERNAME/emomemory.git
git branch -M main
git push -u origin main
```

**Important**: Create the GitHub repository with the name **"emomemory"** before running the push commands.

---

## Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub repository (select "emomemory")
4. Configure:
   - **Repository**: emomemory
   - **Branch**: main
   - **Main file path**: `streamlit_app.py`
5. Click **"Advanced settings"**
6. Add Secret:
   - **Key**: `COGNEE_API_KEY`
   - **Value**: `fb15975b3b414ea303b7235c522f7ab0421b3ee86c1fe85097c5329d1ec2f503`
7. Click **"Deploy"**

---

## Step 3: Your App Goes Live

Wait 2-3 minutes for deployment. Your app will be live at:
```
https://emomemory.streamlit.app
```

---

## ✅ Verification

Once deployed, test:
1. Enter text in the chat
2. Verify emotion detection works
3. Check memory context is building
4. Test "Improve Memory" button
5. Test "Forget My Data" button

---

## 🎯 Hackathon Submission Links

After deployment, you'll have:
- **GitHub Repo**: https://github.com/YOUR_USERNAME/emomemory
- **Live Demo**: https://emomemory.streamlit.app

Use these for your hackathon submission!
