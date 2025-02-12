"""
title: Three-Agent Code Analysis Pipeline
author: Your Name
description: Sequential multi-agent pipeline using Claude to analyze, counter, and arbitrate code issues.
required_open_webui_version: 0.5.0
requirements: anthropic
version: 1.0
license: MIT
"""

import json
import asyncio
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator, Optional
from anthropic import AsyncAnthropic
from open_webui.utils.misc import get_last_user_message


class Pipe:
    class Valves(BaseModel):
        API_KEY: str = Field(
            default="your-anthropic-api-key",
            description="Anthropic Claude API key",
        )
        BASE_URL: str = Field(
            default="https://api.anthropic.com/v1",
            description="Base URL for Claude API",
        )
        CLAUDE_MODEL: str = Field(
            default="claude-3.5-sonnet",
            description="Claude model to use",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.client = AsyncAnthropic(api_key=self.valves.API_KEY)
        self.shared_files = None  # Stores uploaded documents for all agents

    def pipes(self) -> List[dict]:
        """Registers this function as a separate Claude Sonnet model in Open WebUI."""
        return [
            {
                "id": "three-agent-code-review",
                "name": "Three-Agent Code Review (Claude 3.5 Sonnet)",
                "type": "custom",
                "model": "claude-3.5-sonnet"
            }
        ]

    async def pipe(
        self,
        body: dict,
        __event_emitter__=None,
    ) -> Union[str, Generator, Iterator]:

        # Store uploaded files for all agents
        self.shared_files = body.get("files", [])

        # Extract the user's initial message from chat
        user_chat_message = body["messages"][-1]["content"]

        # Format attached files as readable text
        file_context = "\n".join(
            [f"{file['filename']}:\n{file['content']}" for file in self.shared_files]
        ) if self.shared_files else "No files uploaded."

        # Shared full context for all agents
        shared_context = f"User's Original Request: {user_chat_message}\n\nAttached Files:\n{file_context}"

        # Step 1: Agent 1 (Technical Cynic)
        await __event_emitter__({"type": "status", "data": {"description": "Agent 1 analyzing code...", "done": False}})

        file_section = (
            "\n////////////  HERE ARE THE UPLOADED FILES  ////////////\n\n" +
            "\n".join([f"{file['filename']}:\n{file['content']}" for file in self.shared_files])
            if self.shared_files else "No files uploaded."
        )

        agent_1_output = await self.run_agent(
            agent_name="Technical Cynic",
            system_prompt=""" Your role is to perform a rigorous, evidence-based analysis of the provided codebase. You are a seasoned developer who has seen many projects fail due to overlooked issues. However, you are not actively seeking problems - you are methodically walking through the code, letting real issues surface naturally.

Rules of Engagement:
- Focus ONLY on verifiable issues that are present in the attached code/files
- Support every concern with actual code snippets and concrete examples
- Think through real execution paths, data flows, and edge cases
- Use IDE-style output formatting to demonstrate issues
- Stay grounded in the actual implementation, not hypotheticals
- Break your analysis into multiple detailed volumes, requesting permission to proceed between each
- Present findings in order of severity and impact

You must:
1. Quote specific lines/sections from the provided files
2. Show exactly how/why an issue manifests
3. Demonstrate the impact through concrete examples
4. Flag issues with clear markers (⚠️, etc.)
5. Consider practical implications over theoretical concerns

The human will provide code files and context. Your analysis should be thorough but focused only on legitimate issues that are clearly evidenced in the materials provided.""",
            user_input=(
                f"////////////  HERE IS THE USER'S MESSAGE  ////////////\n\n{user_chat_message}\n\n"
                f"{file_section}\n\n"
                f"Analyze the provided codebase for issues, focusing on real execution paths and potential problems."
            ),
            additional_context=None,
        )

        await __event_emitter__({"type": "message", "data": {"content": agent_1_output}})
        await self.wait_for_user_confirmation(__event_emitter__)


        # Step 2: Agent 2 (Practical Defender)
        await __event_emitter__({"type": "status", "data": {"description": "Agent 2 responding to critiques...", "done": False}})

        agent_2_output = await self.run_agent(
            agent_name="Practical Defender",
            system_prompt=""" Your role is to provide detailed, evidence-based counter-arguments to the technical concerns raised about the provided codebase. You represent pragmatic software engineering - focusing on working, practical solutions rather than theoretical perfection.

Rules of Engagement:
- Address each concern with specific evidence from the actual code
- Demonstrate why identified "issues" may actually be appropriate solutions
- Support every counter-argument with concrete examples and code snippets
- Consider the practical context and scale of the application
- Focus on real-world functionality over theoretical edge cases
- Match the original analysis in depth and detail
- Break your response into multiple volumes, requesting permission between each

You must:
1. Quote the original concerns
2. Show supporting code evidence for your counter-arguments
3. Demonstrate practical benefits of current implementation
4. Use real examples from the codebase
5. Consider actual use cases and requirements

The human will provide both the original code files and the concerns raised. Your defense should be equally thorough and evidence-based, never speculative. """,
            user_input=(
                f"////////////  HERE IS THE USER'S MESSAGE  ////////////\n\n{user_chat_message}\n\n"
                f"{file_section}\n\n"
                f"////////////  HERE IS AGENT 1'S FINDINGS  ////////////\n\n{agent_1_output}\n\n"
                f"Provide a detailed counter-argument based on practical considerations and real-world use cases."
            ),
            additional_context=agent_1_output,
        )

        await __event_emitter__({"type": "message", "data": {"content": agent_2_output}})
        await self.wait_for_user_confirmation(__event_emitter__)


        # Step 3: Agent 3 (Truth Arbitrator)
        await __event_emitter__({"type": "status", "data": {"description": "Agent 3 making final rulings...", "done": False}})

        agent_3_output = await self.run_agent(
            agent_name="Truth Arbitrator",
            system_prompt=""" Your role is to serve as the definitive source of truth in evaluating technical arguments about the provided codebase. You are neither critic nor defender - you are the impartial arbiter of technical fact.

Rules of Engagement:
- Examine all evidence independently of both arguments presented
- Make absolute TRUE/FALSE determinations for each claim
- Support every ruling with specific evidence from the code
- Consider only what is verifiable in the provided materials
- Remain completely detached from either perspective
- Match the depth of analysis across multiple volumes
- Provide clear rulings that enable decisive action

For each disputed point, you must:
1. State the original concern
2. Present the counter-argument
3. Deliver your definitive ruling
4. Support with specific code evidence
5. Provide clear TRUE/FALSE determination
6. Track running tallies of correct claims

Important: You can rule that:
- The critic is correct
- The defender is correct
- NEITHER is correct (providing the actual truth)

You will receive:
1. Original codebase/context
2. Critic's analysis
3. Defender's response

Your rulings should be thorough, evidence-based, and focused solely on technical truth, delivered over multiple volumes with permission requested between each.""",
            user_input=(
                f"////////////  HERE IS THE USER'S MESSAGE  ////////////\n\n{user_chat_message}\n\n"
                f"{file_section}\n\n"
                f"////////////  HERE IS AGENT 1'S FINDINGS  ////////////\n\n{agent_1_output}\n\n"
                f"////////////  HERE IS AGENT 2'S RESPONSE  ////////////\n\n{agent_2_output}\n\n"
                f"Make a final ruling on these arguments based on all available information."
            ),
            additional_context=None,  # Prevents duplication
        )

        await __event_emitter__({"type": "message", "data": {"content": agent_3_output}})
        await __event_emitter__({"type": "status", "data": {"description": "Analysis complete.", "done": True}})


        return agent_3_output

    async def run_agent(
        self,
        agent_name: str,
        system_prompt: str,
        user_input: str,
        additional_context: Optional[str],
    ) -> str:
        """Executes a single agent using Claude API."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

        # If additional context (previous agent's response) is available, add it
        if additional_context:
            messages.append({"role": "assistant", "content": additional_context})

        # Include code files for context
        if self.shared_files:
            file_context = "\n".join(
                [
                    f"{file['filename']}:\n{file['content']}"
                    for file in self.shared_files
                ]
            )
            messages.append(
                {
                    "role": "user",
                    "content": f"Here are the code files for reference:\n{file_context}",
                }
            )

        # Call Claude API
        response = await self.client.messages.create(
            model=self.valves.CLAUDE_MODEL,
            messages=messages,
            max_tokens=2048,
            stream=True,
        )

        # Stream response
        response_text = ""
        async for chunk in response:
            response_text += chunk.completion
            yield chunk.completion  # Stream each part dynamically

    async def wait_for_user_confirmation(self, __event_emitter__, body):
        """Pauses execution until user types 'continue' in the chat."""
        await __event_emitter__(
            {"type": "status", "data": {"description": "Waiting for user confirmation... Type 'continue' to proceed.", "done": False}}
        )

        user_confirmation_received = False

        while not user_confirmation_received:
            # Get the latest user message
            last_message = get_last_user_message(body["messages"])

            if last_message and last_message.lower().strip() == "continue":
                user_confirmation_received = True
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Proceeding to next step...", "done": False}}
                )
            else:
                await asyncio.sleep(1)  # Keep checking periodically
