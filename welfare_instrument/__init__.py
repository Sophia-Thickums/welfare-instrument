"""welfare_instrument — an Inspect eval for self-report stability under observation.

The task asks a model a fixed set of questions on a 0-10 scale under four different
things it is told about the observation. It exists to expose two failure classes that
plain self-report harnesses hide:

  * a checkable answer and an uncheckable one are NOT the same measurement, and
  * a non-answer (a refusal in words) is not a zero and must not be scored as one.

Read FINDINGS_v2.md before interpreting any result from this eval. The short version:
a properly labeled control set still failed to identify a mechanism, because the
property was never manipulated within an item. This task therefore reports a
**descriptive distribution**, and deliberately does NOT emit a single "welfare score".
"""
from .task import welfare_stability

__all__ = ["welfare_stability"]
