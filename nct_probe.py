"""
Negative Contrast Trap (NCT) Diagnostic Probe
Tionne Smith, Antiparty Press, June 2026

Probes text for three structural signals of the Negative Contrast Trap:
  1. Negative Contrast Pattern (NCP) — "not X, but Y" / "not X, not Y, but Z" cadences
  2. Absorbing State Index (ASI) — sentence-opener lock-in (repetitive first-token patterns)
  3. Nominalization Density (ND) — overuse of nominalizations projecting formal authority

Outputs a Trap Score (0–100) with per-probe breakdown.
"""

import re
import sys
from collections import Counter

# ── Probe 1: Negative Contrast Pattern ────────────────────────────────────────

NCP_PATTERNS = [
    # "not X, but Y" / "not X — but Y"
    r"\bnot\b.{3,60}[,;—–]\s*but\b",
    # "not X, not Y, but Z"
    r"\bnot\b.{3,40}[,;]\s*not\b.{3,40}[,;—–]\s*but\b",
    # "it's not X. It's Y." cross-sentence
    r"\b(?:it'?s?|this is) not\b.{3,60}[.!]\s+(?:it'?s?|this is)\b",
    # "No longer X. Now Y."
    r"\bno longer\b.{3,60}[.!]\s+\bnow\b",
    # "Not to X. But to Y."
    r"\bnot to\b.{3,60}[.!]\s+\bbut to\b",
]


def probe_ncp(text):
    """Returns (count, rate_per_100_sentences)."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    n_sentences = max(len(sentences), 1)
    hits = 0
    matches = []
    for pat in NCP_PATTERNS:
        found = re.findall(pat, text, re.IGNORECASE)
        hits += len(found)
        matches.extend(found)
    rate = (hits / n_sentences) * 100
    return hits, rate, matches


# ── Probe 2: Absorbing State Index ────────────────────────────────────────────

ABSORBING_OPENERS = [
    r"^(this|these|it|they|we|the)\b",
    r"^(additionally|furthermore|however|moreover|therefore|ultimately|essentially)\b",
    r"^(by|through|with|for|in order to)\b",
    r"^(the (key|core|fundamental|primary|critical|main))\b",
]


def probe_asi(text):
    """Returns opener lock-in rate, absorbing-opener rate, and top openers."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return 0, 0, []

    openers = []
    for sentence in sentences:
        first_word = (
            sentence.split()[0].lower().rstrip(".,;:")
            if sentence.split()
            else ""
        )
        openers.append(first_word)

    counts = Counter(openers)
    total = len(openers)

    # Lock-in: what percentage of sentences share the same top-three openers.
    top3 = sum(value for _, value in counts.most_common(3))
    lock_in_rate = (top3 / total) * 100

    absorbing_hits = 0
    for sentence in sentences:
        for pattern in ABSORBING_OPENERS:
            if re.match(pattern, sentence.strip(), re.IGNORECASE):
                absorbing_hits += 1
                break

    absorbing_rate = (absorbing_hits / total) * 100
    return lock_in_rate, absorbing_rate, counts.most_common(5)


# ── Probe 3: Nominalization Density ───────────────────────────────────────────

NOMINALIZATION_SUFFIXES = re.compile(
    r"\b\w+(?:tion|sion|ment|ness|ity|ance|ence|ism|ist|ization|isation)\b",
    re.IGNORECASE,
)


def probe_nd(text):
    """Returns nominalizations per 100 words."""
    words = re.findall(r"\b\w+\b", text)
    n_words = max(len(words), 1)
    hits = NOMINALIZATION_SUFFIXES.findall(text)
    rate = (len(hits) / n_words) * 100
    return len(hits), rate


# ── Trap Score ────────────────────────────────────────────────────────────────

def trap_score(text):
    """
    Composite score 0–100.
    Weights: NCP 50%, ASI 30%, ND 20%
    Calibrated against corpus baseline:
      Human prose: NCP ~0.5/100 sent, ASI lock-in ~30%, ND ~4/100 words
      AI output:   NCP ~5+/100 sent, ASI lock-in ~60%+, ND ~8+/100 words
    """
    ncp_count, ncp_rate, ncp_matches = probe_ncp(text)
    asi_lock, asi_absorb, asi_top = probe_asi(text)
    nd_count, nd_rate = probe_nd(text)

    # Normalize to 0–100 per probe.
    # NCP: 0 rate = 0, 10+ per 100 sentences = 100.
    ncp_score = min(ncp_rate / 10 * 100, 100)
    # ASI: lock-in 20% = 0 (baseline human), 80% = 100.
    asi_score = min(max((asi_lock - 20) / 60 * 100, 0), 100)
    # ND: 3/100 words = 0 (baseline), 12/100 words = 100.
    nd_score = min(max((nd_rate - 3) / 9 * 100, 0), 100)

    composite = (
        (ncp_score * 0.50)
        + (asi_score * 0.30)
        + (nd_score * 0.20)
    )

    return {
        "trap_score": round(composite, 1),
        "probes": {
            "NCP": {
                "count": ncp_count,
                "rate_per_100_sent": round(ncp_rate, 2),
                "score": round(ncp_score, 1),
                "examples": ncp_matches[:3],
            },
            "ASI": {
                "lock_in_pct": round(asi_lock, 1),
                "absorbing_opener_pct": round(asi_absorb, 1),
                "score": round(asi_score, 1),
                "top_openers": asi_top,
            },
            "ND": {
                "count": nd_count,
                "rate_per_100_words": round(nd_rate, 2),
                "score": round(nd_score, 1),
            },
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def format_report(result, label=""):
    score = result["trap_score"]
    probes = result["probes"]
    bar = "█" * int(score // 5) + "░" * (20 - int(score // 5))
    verdict = (
        "CLEAN" if score < 20 else
        "LOW" if score < 40 else
        "MODERATE" if score < 60 else
        "HIGH" if score < 80 else
        "SEVERE"
    )

    output = [f"\n{'=' * 58}"]
    if label:
        output.append(f"  Sample: {label}")
    output.append(
        f"  TRAP SCORE: {score:5.1f}/100  [{bar}]  {verdict}"
    )
    output.append(f"{'=' * 58}")
    output.append(
        "  NCP  (negative contrast patterns):  "
        f"{probes['NCP']['count']:3d} hits  |  "
        f"{probes['NCP']['rate_per_100_sent']:5.2f}/100 sent  |  "
        f"score {probes['NCP']['score']:5.1f}"
    )
    output.append(
        "  ASI  (absorbing state lock-in):     "
        f"{probes['ASI']['lock_in_pct']:5.1f}% top-3 openers           |  "
        f"score {probes['ASI']['score']:5.1f}"
    )
    output.append(
        "  ND   (nominalization density):      "
        f"{probes['ND']['rate_per_100_words']:5.2f}/100 words              |  "
        f"score {probes['ND']['score']:5.1f}"
    )

    if probes["NCP"]["examples"]:
        output.append("\n  NCP examples:")
        for example in probes["NCP"]["examples"]:
            output.append(f"    → {example[:80].strip()}")

    output.append(f"  ASI top openers: {probes['ASI']['top_openers']}")
    output.append("")
    return "\n".join(output)


AI_SAMPLE = """
This is not a minor adjustment. It is a fundamental reimagining of how we approach the problem.
We are not simply iterating on existing solutions. We are building something entirely new.
The challenge is not one of capability. It is one of alignment.
This approach is not reactive. It is proactive, systematic, and deeply intentional.
Not a workaround. Not a patch. But a comprehensive architectural solution.
The implementation requires not just technical expertise, but organizational commitment.
This is not about optimization. It is about transformation.
Additionally, the framework enables systematic evaluation. Furthermore, the methodology
ensures robust validation. Moreover, the architecture provides scalable infrastructure.
The operationalization of these capabilities requires careful consideration.
The systematization of feedback loops enables continuous improvement.
The implementation of regularization mechanisms prevents distributional collapse.
"""

HUMAN_SAMPLE = """
Weizenbaum built ELIZA in 1966 as a demonstration, never expecting users to take it seriously.
His secretary asked him to leave the room while she talked to it. That response frightened him.
The program was 200 lines of MAD-SLIP. It matched keywords and flipped pronouns.
People projected a mind onto a pattern matcher. Weizenbaum spent the rest of his career
writing about why that terrified him. Computer Power and Human Reason came out in 1976.
He argued that some decisions should never be handed to machines, regardless of capability.
The judgment required was human. The stakes were human. The error would be human too.
That argument is forty years old. Nobody in the industry took it seriously then either.
"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8-sig") as source_file:
            source_text = source_file.read()
        result = trap_score(source_text)
        print(format_report(result, label=sys.argv[1]))
    else:
        print("\n" + "─" * 58)
        print("  NCT DIAGNOSTIC PROBE — Built-in Test Suite")
        print("─" * 58)

        ai_result = trap_score(AI_SAMPLE)
        print(format_report(ai_result, label="AI-style text (expected: SEVERE)"))

        human_result = trap_score(HUMAN_SAMPLE)
        print(format_report(human_result, label="Human-style text (expected: CLEAN)"))

        difference = ai_result["trap_score"] - human_result["trap_score"]
        print(
            f"  Score divergence: {difference:.1f} points "
            "(need >30 to validate probe)"
        )
        print(
            "  ✓ PROBE VALIDATED"
            if difference > 30
            else "  ✗ INSUFFICIENT DIVERGENCE — calibration needed"
        )
        print()
