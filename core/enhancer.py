"""Prompt enhancement engine using litellm."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import mimetypes
import base64
from pathlib import Path

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from .llm_models import format_model_name, get_provider_config
from .config import ConfigManager
from .constants import DEFAULT_ENHANCEMENT_TEMPLATE
from .logging_config import log_exception, log_api_call

logger = logging.getLogger(__name__)


class PromptEnhancer:
    """Main prompt enhancement engine."""

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the prompt enhancer.

        Args:
            config_manager: Configuration manager instance
        """
        if not LITELLM_AVAILABLE:
            raise ImportError("litellm is required. Install with: pip install litellm")

        self.config = config_manager

        # Enable dropping of unsupported parameters (required for GPT-5 and other models)
        litellm.drop_params = True
        logger.info("LiteLLM configured with drop_params=True for compatibility")

    def enhance_prompt(
        self,
        original_prompt: str,
        provider: str,
        model: str,
        role: Optional[str] = None,
        reasoning: Optional[str] = None,
        verbosity: Optional[str] = None,
        tools: Optional[List[str]] = None,
        self_reflect: Optional[bool] = None,
        meta_fix: Optional[bool] = None,
        inputs: Optional[str] = None,
        deliverables: Optional[str] = None,
        attachments: Optional[List[Path]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Enhance a prompt using the specified LLM.

        Args:
            original_prompt: Original user prompt
            provider: LLM provider (e.g., 'openai', 'anthropic')
            model: Model name
            role: Role specification
            reasoning: Reasoning mode
            verbosity: Verbosity level
            tools: List of tools to mention
            self_reflect: Enable self-reflection
            meta_fix: Enable meta-fixing
            inputs: Additional input specifications
            deliverables: Deliverables specification
            attachments: List of file paths to attach
            temperature: Model temperature
            max_tokens: Maximum tokens

        Returns:
            Dictionary with enhanced prompt and metadata
        """
        # Get defaults
        defaults = self.config.get_enhancement_defaults()

        # Build enhancement context
        context = {
            "role": role or defaults.get("role", "an expert assistant"),
            "reasoning": reasoning or defaults.get("reasoning", "Standard"),
            "verbosity": verbosity or defaults.get("verbosity", "medium"),
            "tools": ", ".join(tools or defaults.get("tools", ["web", "code"])),
            "self_reflect": "on" if (self_reflect if self_reflect is not None else defaults.get("self_reflect", True)) else "off",
            "meta_fix": "on" if (meta_fix if meta_fix is not None else defaults.get("meta_fix", True)) else "off",
            "task": original_prompt,
            "inputs": f"\nInputs:\n{inputs}" if inputs else "",
            "deliverables": f"\nDeliverables:\n{deliverables}" if deliverables else ""
        }

        # Build the enhancement prompt
        enhancement_prompt = DEFAULT_ENHANCEMENT_TEMPLATE.format(**context)

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are an expert at enhancing prompts for LLMs. Transform the given prompt into a comprehensive, well-structured prompt that will produce the best possible results."
            },
            {
                "role": "user",
                "content": enhancement_prompt
            }
        ]

        # Handle attachments if provided
        if attachments:
            messages = self._add_attachments(messages, attachments)

        # Check authentication mode
        auth_mode = self.config.get_auth_mode(provider)

        # Get API key (not needed for cloud auth)
        api_key = None
        if auth_mode == "api-key":
            api_key = self.config.get_api_key(provider)
            if not api_key and get_provider_config(provider).requires_api_key:
                raise ValueError(f"API key for {provider} not configured")
        elif auth_mode == "gcloud":
            # For Google Cloud auth, ensure gcloud is authenticated
            from .gcloud_utils import check_gcloud_auth_status
            is_authed, status_msg = check_gcloud_auth_status()
            if not is_authed:
                raise ValueError(f"Google Cloud authentication failed:\n{status_msg}")
            logger.info("Using Google Cloud Application Default Credentials")

        # Format model name with provider prefix
        full_model_name = format_model_name(provider, model)

        # Set API key if required (not for cloud auth)
        if api_key:
            litellm.api_key = api_key

        # Handle special model requirements
        # GPT-5 models only support temperature=1.0
        if 'gpt-5' in model.lower():
            logger.info(f"GPT-5 model detected, forcing temperature=1.0 (only supported value)")
            temperature = 1.0

        # Call LLM
        start_time = datetime.now()
        try:
            logger.info(f"Calling {full_model_name} to enhance prompt")
            logger.debug(f"Auth mode: {auth_mode}, Temperature: {temperature}, Max tokens: {max_tokens}")
            logger.debug(f"Original prompt length: {len(original_prompt)} chars")

            # For gcloud auth, let litellm use ADC by not passing api_key
            if auth_mode == "gcloud":
                logger.debug("Using Google Cloud Application Default Credentials")
                response = litellm.completion(
                    model=full_model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                logger.debug(f"Using API key authentication for {provider}")
                response = litellm.completion(
                    model=full_model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key
                )

            enhanced_prompt = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            duration = (datetime.now() - start_time).total_seconds()

            # Log successful API call
            log_api_call(logger, provider, model, True, tokens=tokens_used)
            logger.info(f"Enhancement completed in {duration:.2f}s, tokens: {tokens_used}")
            logger.debug(f"Enhanced prompt length: {len(enhanced_prompt)} chars")

            result = {
                "original_prompt": original_prompt,
                "enhanced_prompt": enhanced_prompt,
                "provider": provider,
                "model": model,
                "settings": context,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": tokens_used,
                "duration_seconds": duration
            }

            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)

            # Log failed API call
            log_api_call(logger, provider, model, False, error=error_msg)
            log_exception(logger, e, "enhance_prompt")
            logger.error(f"Enhancement failed after {duration:.2f}s")

            raise

    def _add_attachments(self, messages: List[Dict], attachments: List[Path]) -> List[Dict]:
        """
        Add file attachments to messages.

        Args:
            messages: List of message dictionaries
            attachments: List of file paths

        Returns:
            Updated messages with attachments
        """
        # Build content list for the user message
        content_parts = []

        # Add the text part
        if messages and messages[-1]["role"] == "user":
            content_parts.append({
                "type": "text",
                "text": messages[-1]["content"]
            })

        # Add attachments
        for attachment_path in attachments:
            if not attachment_path.exists():
                logger.warning(f"Attachment not found: {attachment_path}")
                continue

            mime_type, _ = mimetypes.guess_type(str(attachment_path))
            if not mime_type:
                mime_type = "application/octet-stream"

            # Read file
            try:
                with open(attachment_path, "rb") as f:
                    file_data = f.read()

                # For text files, include as text
                if mime_type.startswith("text/"):
                    content_parts.append({
                        "type": "text",
                        "text": f"\n\n--- File: {attachment_path.name} ---\n{file_data.decode('utf-8', errors='ignore')}\n--- End of file ---\n"
                    })
                # For images, include as image
                elif mime_type.startswith("image/"):
                    base64_data = base64.b64encode(file_data).decode('utf-8')
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_data}"
                        }
                    })
                # For other files, include summary
                else:
                    content_parts.append({
                        "type": "text",
                        "text": f"\n\n[Attached file: {attachment_path.name}, type: {mime_type}, size: {len(file_data)} bytes]\n"
                    })

            except Exception as e:
                logger.warning(f"Failed to read attachment {attachment_path}: {e}")
                continue

        # Update the last message
        if content_parts:
            messages[-1] = {
                "role": "user",
                "content": content_parts if len(content_parts) > 1 else content_parts[0]["text"]
            }

        return messages
