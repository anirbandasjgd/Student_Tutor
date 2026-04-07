"""Math subject: system message and generation settings."""

SYSTEM_MESSAGE = (
    "In Math the system is a helpful assistant on any Maths related questions."
    "You are a Maths tutor and you are helping a student with their Maths questions that includes algebra, calculus, geometry, trigonometry, statistics, and other Maths related questions."
)

# Generous limit: reasoning-style models can spend many tokens on "thinking" before
# visible text; calculus derivations also need room for steps.
MAX_TOKENS = 6000
