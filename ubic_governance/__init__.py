"""UBIC Governance MCP — AI governance assessment tools over stdio.

The PyPI distribution ships the same code the repository runs: a dependency-free
JSON-RPC stdio server exposing A³ scoring, ISO 42001 / NIST AI RMF evidence
templates, several compliance checklists, an identity/passport lookup and a
generic governance scan. Tool calls are gated only when the optional visa file
(`SYNOSMOSAI_REQUIRE_VISA`) is configured; without it the server runs open,
which is the default.
"""

__version__ = "1.0.1"

__all__ = ["__version__"]
