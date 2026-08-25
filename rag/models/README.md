# Local model cache — model weights will be downloaded here on first run
# (~80 MB for all-MiniLM-L6-v2)
# After download, the system works fully offline.

## Model: sentence-transformers/all-MiniLM-L6-v2

### Download location
Weights are cached automatically by the HuggingFace Hub library at:

- **Windows:** `%USERPROFILE%\.cache\huggingface\hub\`
- **Linux/Mac:** `~/.cache/huggingface/hub/`

### Override cache location
Set the `HF_HOME` environment variable before running:
```bash
set HF_HOME=D:\models   # Windows
export HF_HOME=/data/models  # Linux
```

### Offline mode (after first download)
Set `TRANSFORMERS_OFFLINE=1` to prevent any internet lookups:
```bash
set TRANSFORMERS_OFFLINE=1  # Windows
```

### Model card
- **Name:** all-MiniLM-L6-v2
- **Dimensions:** 384
- **Max input length:** 256 word pieces
- **Speed:** ~14,000 sentences/second on CPU
- **License:** Apache 2.0
- **HuggingFace:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
