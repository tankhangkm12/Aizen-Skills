# Trusted Sources & Search Strategy

**Rule:** When researching technical solutions, architectural patterns, or debugging issues, you MUST prioritize the user's curated trusted sources before searching the open web.

1. **Read `.aizen/sources/` first:**
   Check files like `trusted-architects.md` or `.txt` inside the `.aizen/sources/` directory.

2. **Follow Priority Hierarchy:**
   - **Priority 1:** You MUST search these domains/channels first (e.g., using `site:bytebytego.com` or `site:youtube.com/c/ByteByteGo`). If it's a YouTube video, use `aizen-video-to-skill` or equivalent transcript extraction tools to read the content.
   - **Priority 2:** Only if Priority 1 yields no results, move to Priority 2 sources.
   - **Priority 3 & Open Web:** If all trusted sources fail, search the open web but strictly prioritize Official Documentation (e.g., `docs.microsoft.com`, `react.dev`).

3. **Cite Your Sources:**
   When logging the final decision in `.aizen/decisions/`, you MUST include a citation line:
   *Example: "Solution based on [Priority 1] - ByteByteGo (youtube.com/watch?v=...)"*
