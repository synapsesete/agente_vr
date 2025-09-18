from __future__ import annotations

import json
import logging
import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException

logger = logging.getLogger(__name__)


class CustomAgentOutputParser(AgentOutputParser):

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:

        logger.debug("Text received:|%s|", text)

        if text and text[-1] != "\n":
            text += "\n"

        final_answer_prefix = "Final Answer:"
        final_answer_block = self._parse_block(final_answer_prefix, text)
        if final_answer_block:
            final_answer = final_answer_block[len(final_answer_prefix) :]
            return AgentFinish({"output": final_answer}, text)
        else:
            action_prefix = "Action: "
            action_block = self._parse_block(action_prefix, text)
            if not action_block:
                msg = f"Could not parse LLM Output: {text}"
                raise OutputParserException(msg)

            logger.debug("Action_block: |%s|", action_block)
            action = action_block[len(action_prefix) :]
            logger.debug("Action: |%s|", action)
            if action is None:
                msg = f"Could not parse action directive: {action}"
                raise OutputParserException(msg)

            # Parse out the action and the directive.
            action_input_prefix = "Action Input: "
            action_input_block = self._parse_block(action_input_prefix, text)
            logger.debug("action_input_block: |%s|", action_input_block)
            action_input = action_input_block[len(action_input_prefix) :]
            action_input = json.loads(action_input.replace("'", '"'))
            logger.debug("Action Input: |%s|", action_input)

            return AgentAction(action, action_input, text)

    def _parse_block(self, prefix: str, text: str) -> str:
        return self._get_text_between_delimiters(text, prefix, "\n")

    def _get_text_between_delimiters(self, text, start_delim, end_delim):
        # Regex pattern to match the text between the delimiters
        pattern = re.escape(start_delim) + "(.*?)" + re.escape(end_delim)
        # Find all matches
        matches = re.search(pattern, text)
        if matches:
            return matches.group().strip()
        else:
            return None

    @property
    def _type(self) -> str:
        return "react"
