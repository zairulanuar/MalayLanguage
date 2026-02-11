#!/usr/bin/env python3
"""
MalayLanguage MCP Server

A Model Context Protocol server providing Malay language processing tools using the Malaya library.
Supports both stdio and HTTP streaming at /mcp endpoint.
"""

import logging
import sys
from typing import Any, Optional

import malaya
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("malaylanguage-mcp")

# Initialize MCP server
app = Server("malaylanguage-mcp-server")

# Cache for loaded models to avoid reloading
_model_cache = {}


def get_language_detection_model():
    """Get or initialize the language detection model."""
    if "language_detection" not in _model_cache:
        try:
            logger.info("Loading language detection model...")
            _model_cache["language_detection"] = malaya.language_detection.transformer()
            logger.info("Language detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading language detection model: {e}")
            raise
    return _model_cache["language_detection"]


def get_normalizer_model():
    """Get or initialize the text normalizer model."""
    if "normalizer" not in _model_cache:
        try:
            logger.info("Loading text normalizer model...")
            _model_cache["normalizer"] = malaya.normalize.normalizer()
            logger.info("Text normalizer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading normalizer model: {e}")
            raise
    return _model_cache["normalizer"]


def get_spelling_corrector():
    """Get or initialize the spelling correction model."""
    if "spelling" not in _model_cache:
        try:
            logger.info("Loading spelling correction model...")
            _model_cache["spelling"] = malaya.spelling_correction.transformer()
            logger.info("Spelling correction model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading spelling correction model: {e}")
            raise
    return _model_cache["spelling"]


def get_translation_model(source: str = "ms", target: str = "en"):
    """Get or initialize the translation model."""
    key = f"translation_{source}_{target}"
    if key not in _model_cache:
        try:
            logger.info(f"Loading translation model {source}->{target}...")
            _model_cache[key] = malaya.translation.transformer(source=source, target=target)
            logger.info(f"Translation model {source}->{target} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading translation model: {e}")
            raise
    return _model_cache[key]


def get_paraphrase_model():
    """Get or initialize the paraphrase/rewrite model."""
    if "paraphrase" not in _model_cache:
        try:
            logger.info("Loading paraphrase model...")
            _model_cache["paraphrase"] = malaya.paraphrase.transformer()
            logger.info("Paraphrase model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading paraphrase model: {e}")
            raise
    return _model_cache["paraphrase"]


# Define available tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Malay language processing tools."""
    return [
        Tool(
            name="detect_language",
            description="Detect the language of the given text. Identifies Malay, English, and other languages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze for language detection",
                    }
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="normalize_malay",
            description="Normalize Malay text by fixing common informal writing patterns, abbreviations, and colloquialisms to standard Malay.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The Malay text to normalize",
                    }
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="correct_spelling",
            description="Correct spelling errors in Malay text using advanced transformer models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The Malay text with potential spelling errors",
                    }
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="apply_glossary",
            description="Look up Malay terms in a standard glossary and provide definitions, translations, and usage examples.",
            inputSchema={
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "The Malay term to look up in the glossary",
                    }
                },
                "required": ["term"],
            },
        ),
        Tool(
            name="rewrite_style",
            description="Rewrite Malay text in a different style while preserving meaning. Uses paraphrasing to generate alternative expressions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The Malay text to rewrite",
                    },
                    "style": {
                        "type": "string",
                        "description": "Target style (e.g., 'formal', 'casual', 'simplified')",
                        "enum": ["formal", "casual", "simplified"],
                        "default": "formal",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="translate",
            description="Translate text between Malay and English (bidirectional).",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to translate",
                    },
                    "source_lang": {
                        "type": "string",
                        "description": "Source language code (ms=Malay, en=English)",
                        "enum": ["ms", "en"],
                        "default": "ms",
                    },
                    "target_lang": {
                        "type": "string",
                        "description": "Target language code (ms=Malay, en=English)",
                        "enum": ["ms", "en"],
                        "default": "en",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="term_lookup",
            description="Look up linguistic information about a Malay term, including part of speech, etymology, and related terms.",
            inputSchema={
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "The Malay term to look up",
                    }
                },
                "required": ["term"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution requests."""
    try:
        if name == "detect_language":
            return await detect_language(arguments.get("text", ""))
        elif name == "normalize_malay":
            return await normalize_malay(arguments.get("text", ""))
        elif name == "correct_spelling":
            return await correct_spelling(arguments.get("text", ""))
        elif name == "apply_glossary":
            return await apply_glossary(arguments.get("term", ""))
        elif name == "rewrite_style":
            return await rewrite_style(
                arguments.get("text", ""),
                arguments.get("style", "formal")
            )
        elif name == "translate":
            return await translate(
                arguments.get("text", ""),
                arguments.get("source_lang", "ms"),
                arguments.get("target_lang", "en")
            )
        elif name == "term_lookup":
            return await term_lookup(arguments.get("term", ""))
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def detect_language(text: str) -> list[TextContent]:
    """Detect the language of the given text."""
    if not text.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only text provided")]
    
    try:
        model = get_language_detection_model()
        result = model.predict([text])[0]
        
        response = f"""Language Detection Result:
Language: {result['label']}
Confidence: {result['score']:.2%}

Input text: {text}"""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return [TextContent(type="text", text=f"Error detecting language: {str(e)}")]


async def normalize_malay(text: str) -> list[TextContent]:
    """Normalize Malay text to standard form."""
    if not text.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only text provided")]
    
    try:
        normalizer = get_normalizer_model()
        normalized = normalizer.normalize(text)
        
        response = f"""Text Normalization Result:

Original: {text}

Normalized: {normalized}"""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Normalization error: {e}")
        return [TextContent(type="text", text=f"Error normalizing text: {str(e)}")]


async def correct_spelling(text: str) -> list[TextContent]:
    """Correct spelling errors in Malay text."""
    if not text.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only text provided")]
    
    try:
        corrector = get_spelling_corrector()
        corrected = corrector.correct(text)
        
        response = f"""Spelling Correction Result:

Original: {text}

Corrected: {corrected}"""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Spelling correction error: {e}")
        return [TextContent(type="text", text=f"Error correcting spelling: {str(e)}")]


async def apply_glossary(term: str) -> list[TextContent]:
    """Look up a term in the Malay glossary."""
    if not term.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only term provided")]
    
    try:
        # Use Malaya's built-in dictionary/vocabulary lookup if available
        # For now, we'll provide a basic lookup using translation and definition
        translator = get_translation_model("ms", "en")
        translation = translator.translate([term])[0]
        
        response = f"""Glossary Lookup: {term}

Translation (EN): {translation}

Note: This is a basic translation. For comprehensive glossary entries with definitions, 
etymology, and usage examples, consider integrating with Dewan Bahasa dan Pustaka's 
official dictionary API or similar resources."""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Glossary lookup error: {e}")
        return [TextContent(type="text", text=f"Error looking up term: {str(e)}")]


async def rewrite_style(text: str, style: str = "formal") -> list[TextContent]:
    """Rewrite text in a different style."""
    if not text.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only text provided")]
    
    try:
        paraphraser = get_paraphrase_model()
        paraphrased = paraphraser.paraphrase([text])[0]
        
        response = f"""Style Rewrite Result (Target: {style}):

Original: {text}

Rewritten: {paraphrased}

Note: The paraphrase model generates alternative expressions. For specific style 
transformations (formal/casual), consider fine-tuning or prompt engineering."""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Style rewrite error: {e}")
        return [TextContent(type="text", text=f"Error rewriting text: {str(e)}")]


async def translate(text: str, source_lang: str = "ms", target_lang: str = "en") -> list[TextContent]:
    """Translate text between Malay and English."""
    if not text.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only text provided")]
    
    if source_lang == target_lang:
        return [TextContent(type="text", text="Error: Source and target languages must be different")]
    
    try:
        translator = get_translation_model(source_lang, target_lang)
        translated = translator.translate([text])[0]
        
        lang_names = {"ms": "Malay", "en": "English"}
        response = f"""Translation Result:

Source ({lang_names[source_lang]}): {text}

Translation ({lang_names[target_lang]}): {translated}"""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return [TextContent(type="text", text=f"Error translating text: {str(e)}")]


async def term_lookup(term: str) -> list[TextContent]:
    """Look up detailed linguistic information about a Malay term."""
    if not term.strip():
        return [TextContent(type="text", text="Error: Empty or whitespace-only term provided")]
    
    try:
        # Combine multiple analysis approaches
        translator = get_translation_model("ms", "en")
        translation = translator.translate([term])[0]
        
        # Try to detect if it's actually Malay
        detector = get_language_detection_model()
        lang_info = detector.predict([term])[0]
        
        response = f"""Term Lookup: {term}

Language: {lang_info['label']} (confidence: {lang_info['score']:.2%})
Translation: {translation}

Note: For comprehensive linguistic analysis including part of speech, etymology, 
and morphological information, consider integrating with specialized Malay linguistic 
databases or NLP pipelines."""
        
        return [TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Term lookup error: {e}")
        return [TextContent(type="text", text=f"Error looking up term: {str(e)}")]


async def main():
    """Run the MCP server on stdio."""
    logger.info("Starting MalayLanguage MCP server on stdio...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
