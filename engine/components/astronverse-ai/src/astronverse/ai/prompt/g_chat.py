"""Grouped chat prompt wrappers for role play and question generation."""

from astronverse.ai.prompt.chat import (
    PROMPT_GENERATE_QUESTION,
    PROMPT_ROLE_PLAY,
)

prompt_role_play_generator = [{"role": "system", "content": PROMPT_ROLE_PLAY}]

prompt_generate_question = [{"role": "user", "content": PROMPT_GENERATE_QUESTION}]
