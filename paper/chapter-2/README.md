# Chapter 2 (public artifact)

- Place the public version of your chapter here (Markdown or PDF).
- Figures go to `figures/`.
- Consider removing sensitive details (e.g., subject IDs).

Suggested workflow to convert `.docx` to Markdown:

```bash
# install pandoc (macOS/brew example)
brew install pandoc

# convert
pandoc "Chapter 2.docx" -o chapter-2.md --extract-media=figures
```
