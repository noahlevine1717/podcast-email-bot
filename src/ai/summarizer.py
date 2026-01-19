"""Claude-powered summarization and insight extraction."""

import json
import logging
from typing import Optional

import anthropic

from src.config import Config

logger = logging.getLogger(__name__)


class Summarizer:
    """Handles AI-powered summarization using Claude."""

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ai.anthropic_api_key)
        self.model = config.ai.model

    async def summarize_podcast(
        self,
        transcript: str,
        title: str,
        show_name: Optional[str] = None,
    ) -> dict:
        """Generate summary, key points, and soundbites for a podcast.

        Returns dict with:
            - summary: str
            - key_points: list[str]
            - soundbites: list[dict] with text, speaker, context
            - tags: list[str]
        """
        # Truncate very long transcripts to avoid token limits
        max_chars = 100000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[Transcript truncated due to length...]"

        prompt = f"""Analyze this podcast transcript and provide:

1. A concise summary (2-3 paragraphs) capturing the main ideas and takeaways
2. 5-7 key points or insights as bullet points
3. 2-3 of the most valuable soundbites/quotes - these should be memorable, quotable passages that:
   - Capture a core insight or unique perspective
   - Are self-contained and make sense out of context
   - Would be worth sharing or remembering
4. 3-5 relevant topic tags for organization

Podcast: {title}
{f"Show: {show_name}" if show_name else ""}

TRANSCRIPT:
{transcript}

Respond in JSON format:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "soundbites": [
        {{
            "text": "The exact quote from the transcript",
            "speaker": "Speaker name if identifiable, otherwise null",
            "context": "Brief context about why this is valuable (1 sentence)"
        }},
        ...
    ],
    "tags": ["tag1", "tag2", ...]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Try to parse JSON, handling markdown code blocks if present
        try:
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text.strip())
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return a basic structure
            result = {
                "summary": response_text[:1000],
                "key_points": [],
                "soundbites": [],
                "tags": [],
            }

        return result

    async def summarize_article(
        self,
        content: str,
        title: str,
        author: Optional[str] = None,
        url: Optional[str] = None,
    ) -> dict:
        """Generate summary and key points for an article.

        Returns dict with:
            - summary: str
            - key_points: list[str]
            - tags: list[str]
        """
        max_chars = 50000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated...]"

        prompt = f"""Analyze this article and provide:

1. A concise summary (1-2 paragraphs) capturing the main argument/information
2. 3-5 key points or takeaways
3. 3-5 relevant topic tags for organization

Article: {title}
{f"Author: {author}" if author else ""}

CONTENT:
{content}

Respond in JSON format:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "tags": ["tag1", "tag2", ...]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text.strip())
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            result = {
                "summary": response_text[:500],
                "key_points": [],
                "tags": [],
            }

        return result

    async def summarize_thread(
        self,
        tweets: list[str],
        author: str,
    ) -> dict:
        """Generate summary for an X/Twitter thread.

        Returns dict with:
            - summary: str
            - tags: list[str]
        """
        thread_text = "\n\n".join(f"{i+1}. {tweet}" for i, tweet in enumerate(tweets))

        prompt = f"""Analyze this Twitter/X thread and provide:

1. A concise summary (1-2 paragraphs) of the main argument/narrative
2. 3-5 relevant topic tags

Thread by @{author}:

{thread_text}

Respond in JSON format:
{{
    "summary": "...",
    "tags": ["tag1", "tag2", ...]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text.strip())
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            result = {
                "summary": response_text[:500],
                "tags": [],
            }

        return result

    async def generate_connections(
        self,
        new_content_summary: str,
        similar_items: list[dict],
    ) -> list[str]:
        """Generate natural language connections between new content and existing items.

        Args:
            new_content_summary: Summary of the new content
            similar_items: List of dicts with 'title', 'summary', 'vault_path'

        Returns:
            List of connection descriptions
        """
        if not similar_items:
            return []

        similar_text = "\n\n".join(
            f"**{item['title']}**: {item['summary'][:300]}..."
            for item in similar_items
        )

        prompt = f"""Given this new content and similar past content, describe the meaningful connections between them.

NEW CONTENT:
{new_content_summary}

SIMILAR PAST CONTENT:
{similar_text}

Provide 2-3 specific connections that show how these ideas relate, build on each other, or contrast.
Focus on intellectual connections, shared themes, or complementary perspectives.

Respond with a JSON array of connection strings:
["Connection 1 description", "Connection 2 description", ...]"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]

            connections = json.loads(response_text.strip())
        except (json.JSONDecodeError, ValueError):
            connections = []

        return connections

    async def generate_daily_digest(
        self,
        content_items: list[dict],
        date_str: str,
    ) -> dict:
        """Generate a daily digest summarizing the day's content.

        Returns dict with:
            - summary: str
            - themes: list[str]
            - connections: list[str]
        """
        if not content_items:
            return {
                "summary": "No content was processed today.",
                "themes": [],
                "connections": [],
            }

        items_text = "\n\n".join(
            f"**{item['type'].upper()}: {item['title']}**\n{item['summary']}"
            for item in content_items
        )

        prompt = f"""Generate a daily digest for {date_str} based on the content consumed:

{items_text}

Provide:
1. A cohesive summary of what was learned today (2-3 paragraphs)
2. Key themes that emerged across the content
3. Notable connections or patterns between different pieces

Respond in JSON format:
{{
    "summary": "...",
    "themes": ["theme 1", "theme 2", ...],
    "connections": ["connection 1", "connection 2", ...]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.index("```") + 3
                json_end = response_text.index("```", json_start)
                response_text = response_text[json_start:json_end]

            result = json.loads(response_text.strip())
        except (json.JSONDecodeError, ValueError):
            result = {
                "summary": response_text[:1000],
                "themes": [],
                "connections": [],
            }

        return result

    async def generate_podcast_email(
        self,
        transcript: str,
        metadata,
        user_details: list[str],
        user_insights: list[str],
        feedback: Optional[str] = None,
        previous_draft: Optional[str] = None,
    ) -> str:
        """Generate a professional email-style summary for a podcast.

        Args:
            transcript: Full podcast transcript
            metadata: PodcastMetadata object
            user_details: User-provided key details (from interactive mode)
            user_insights: User-provided insights (from interactive mode)
            feedback: Optional feedback on previous draft
            previous_draft: Previous draft to improve upon

        Returns:
            Formatted email-style summary string
        """
        # Truncate transcript for token limits
        max_chars = 80000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[Transcript truncated...]"

        # Build user input section
        user_input_section = ""
        if user_details or user_insights:
            user_input_section = "\n\nUSER-PROVIDED CONTENT (incorporate and expand on these):\n"
            if user_details:
                user_input_section += "\nKey Details from User:\n"
                for i, detail in enumerate(user_details, 1):
                    user_input_section += f"  {i}. {detail}\n"
            if user_insights:
                user_input_section += "\nKey Insights from User:\n"
                for i, insight in enumerate(user_insights, 1):
                    user_input_section += f"  {i}. {insight}\n"
            user_input_section += "\nIMPORTANT: The user's details and insights should be the PRIMARY focus. Use the transcript to expand on and contextualize them, not to replace them.\n"

        # Build feedback section for revisions
        revision_section = ""
        if feedback and previous_draft:
            revision_section = f"""

REVISION REQUEST:
The user has provided feedback on the previous draft. Please revise accordingly.

Previous Draft:
{previous_draft}

User Feedback:
{feedback}

Apply the feedback while maintaining the email format structure."""

        show_info = f" from {metadata.show_name}" if metadata.show_name else ""
        duration_info = f"{metadata.duration // 60} minutes" if metadata.duration else "Unknown duration"

        prompt = f"""Generate a professional email summary for sharing key learnings from this podcast.

PODCAST INFO:
- Title: {metadata.title}
- Show: {metadata.show_name or "Unknown Show"}
- Duration: {duration_info}

TRANSCRIPT:
{transcript}
{user_input_section}
{revision_section}

Write a clear, cogent, concise email in this EXACT format:

---

Hi Team,

Today I listened to the **{metadata.title}** podcast{show_info}. Here are the key details and insights.

**KEY DETAILS**

**[Detail Topic 1]**
[2-3 sentences explaining this detail with specific examples or data from the podcast]

**[Detail Topic 2]**
[2-3 sentences explaining this detail]

[Continue for 5-10 key details total]

**KEY INSIGHTS**

**[Insight Topic 1]**
[2-3 sentences explaining this insight and why it matters]

**[Insight Topic 2]**
[2-3 sentences explaining this insight]

[Continue for 3-5 key insights total]

---

GUIDELINES:
- Each detail/insight should have a BOLDED subheader followed by 2-3 lines of explanation
- Be specific - include numbers, names, examples from the podcast
- KEY DETAILS = factual information, data points, frameworks mentioned
- KEY INSIGHTS = takeaways, implications, actionable ideas
- Keep it professional but accessible
- Total length: 400-800 words
{f"- PRIORITIZE the user's provided details and insights" if user_details or user_insights else ""}

Return ONLY the email content (no markdown code blocks, no extra commentary)."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        email_content = response.content[0].text.strip()

        # Clean up any markdown code blocks if present
        if email_content.startswith("```"):
            lines = email_content.split("\n")
            email_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        return email_content
