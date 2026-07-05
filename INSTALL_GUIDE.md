# 🚀 Quick Installation Guide

## Problem with Slow Network?

If `pip install gradio` is taking too long, here are alternatives:

---

## ⚡ Option 1: Install from requirements (recommended if download works)

```bash
pip install -r requirements_minimal.txt
```

This installs only what you need for the hackathon demo.

---

## 🎯 Option 2: Install packages one by one

```bash
# Install Gradio (this is the one that's slow ~31MB)
pip install gradio

# Install Cognee
pip install cognee
```

**Note:** The gradio download is ~31MB and may take 5-10 minutes on slow connections.

---

## 🌐 Option 3: Use conda (if you have conda)

```bash
conda install -c conda-forge gradio
pip install cognee
```

---

## 💡 Option 4: Run without Gradio (CLI mode)

If Gradio installation fails, you can still demo the core Cognee functionality:

```bash
# Run the CLI demo instead
python chat_interface.py
```

This runs the command-line chat interface without needing Gradio!

---

## 🔥 Option 5: Use pip with timeout and retry

```bash
# Increase timeout and use retries
pip install --timeout=300 --retries=10 gradio
```

---

## 🎬 Quick Test After Installation

### Test 1: CLI Demo (No Gradio needed)
```bash
python chat_interface.py
```

### Test 2: Web Demo (Requires Gradio)
```bash
python web_demo.py
```

---

## 📦 What Each Package Does

- **gradio**: Web interface (31MB) - only needed for web demo
- **cognee**: Memory layer (small) - REQUIRED for hackathon

---

## ⏰ Installation Time Estimates

**Fast internet (10+ Mbps):**
- gradio: 1-2 minutes
- cognee: 30 seconds
- Total: ~3 minutes

**Slow internet (1-2 Mbps):**
- gradio: 10-15 minutes
- cognee: 1-2 minutes
- Total: ~15 minutes

**Very slow internet (<1 Mbps):**
- Use Option 4 (CLI mode) and skip Gradio!

---

## 🆘 Still Having Issues?

### Error: "No module named 'gradio'"
**Solution:** Gradio didn't install. Use Option 4 (CLI mode).

### Error: Download timeout
**Solution:** Run:
```bash
pip install --timeout=600 gradio
```

### Error: Network error
**Solution:** Check internet connection, or use Option 4.

---

## ✅ Verify Installation

```bash
# Check if gradio installed
python -c "import gradio; print('✓ Gradio OK')"

# Check if cognee installed
python -c "import cognee; print('✓ Cognee OK')"
```

---

## 🎉 You're Ready!

Once installation completes, run:

```bash
# For web interface (if gradio installed)
python web_demo.py

# For CLI interface (works without gradio)
python chat_interface.py
```

---

**Tip:** The CLI demo (`chat_interface.py`) is perfect for the hackathon and doesn't require Gradio!
