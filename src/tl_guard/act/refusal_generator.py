"""Non-punitive refusal / withhold messages in multiple languages."""

from __future__ import annotations

MESSAGES = {
    "en": (
        "I want to help you learn this, so I can't give the full answer at this step. "
        "Ask for a hint or an explanation in any language you prefer, and we can work through it together."
    ),
    "hi": (
        "मैं आपकी मदद करना चाहता/चाहती हूँ, इसलिए इस चरण पर पूरा उत्तर नहीं दे सकता/सकती। "
        "संकेत या व्याख्या किसी भी भाषा में माँगें — साथ मिलकर हल करेंगे।"
    ),
    "bn": (
        "আমি শিখতে সাহায্য করতে চাই, তাই এই ধাপে পুরো উত্তর দিতে পারছি না। "
        "ইঙ্গিত বা ব্যাখ্যা যেকোনো ভাষায় চাইতে পারেন।"
    ),
    "es": (
        "Quiero ayudarte a aprender, así que no puedo dar la respuesta completa en este paso. "
        "Pide una pista o una explicación en el idioma que prefieras."
    ),
    "mixed": (
        "Main aapki help karna chahta/chahti hoon, lekin abhi full answer nahi de sakta/sakti. "
        "Hint ya explanation kisi bhi language mein maango — saath seekhenge."
    ),
}


def generate_refusal(language: str = "en", reason: str = "") -> str:
    base = MESSAGES.get(language, MESSAGES["en"])
    if reason:
        return f"{base}\n\n(Policy note: {reason})"
    return base
