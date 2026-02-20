import json
import logging
import re
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FactCandidate:
    fact_id: str
    chunk_id: str
    statement: str
    fact_type: str
    importance: float


class FactItem(BaseModel):
    statement: str = Field(min_length=8, max_length=400)
    fact_type: str = Field(pattern=r"^(definition|claim|method|result|limitation|formula)$")
    importance: float = Field(ge=0.0, le=1.0)


class FactResponse(BaseModel):
    facts: list[FactItem]


# --- Outline models ---

class OutlineSubsection(BaseModel):
    heading: str = Field(min_length=2, max_length=200)
    fact_indices: list[int]


class OutlineSection(BaseModel):
    heading: str = Field(min_length=2, max_length=200)
    summary_note: str = Field(max_length=500, default="")
    subsections: list[OutlineSubsection] = Field(min_length=1, max_length=5)


class OutlineResponse(BaseModel):
    sections: list[OutlineSection] = Field(min_length=1, max_length=15)


# --- Annotation models ---

class AnnotationItem(BaseModel):
    subsection_index: int
    annotation: str = Field(max_length=600, default="")


class AnnotationsResponse(BaseModel):
    annotations: list[AnnotationItem]


def _fallback_extract(chunk_id: str, text: str) -> list[FactCandidate]:
    lines = [ln.strip() for ln in text.split(".") if ln.strip()]
    out: list[FactCandidate] = []
    for idx, line in enumerate(lines[:5], start=1):
        out.append(
            FactCandidate(
                fact_id=f"f_{chunk_id}_{idx}",
                chunk_id=chunk_id,
                statement=line[:240],
                fact_type="claim",
                importance=0.55,
            )
        )
    if not out:
        out.append(
            FactCandidate(
                fact_id=f"f_{chunk_id}_1",
                chunk_id=chunk_id,
                statement=text[:220],
                fact_type="definition",
                importance=0.5,
            )
        )
    return out


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self._http_client: httpx.Client | None = None

    @property
    def http_client(self) -> httpx.Client:
        """Lazily-created, reusable httpx client with connection pooling."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.Client(
                timeout=settings.llm_timeout_seconds,
                trust_env=False,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._http_client

    def close(self):
        if self._http_client and not self._http_client.is_closed:
            self._http_client.close()

    # ---- low-level helpers ----

    def _extract_json_string(self, raw: str) -> str:
        """Strip markdown code fences and extract JSON object for parsing."""
        s = raw.strip()
        for pattern in (r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", r"^```\s*\n?(.*?)\n?```\s*$"):
            m = re.search(pattern, s, re.DOTALL)
            if m:
                s = m.group(1).strip()
        start = s.find("{")
        if start == -1:
            return s
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
        return s

    def _call_llm_raw(self, system: str, user: str) -> str:
        """Call the LLM and return raw content string (OpenAI-compatible or Anthropic)."""
        if self.provider == "anthropic":
            return self._call_anthropic_raw(system, user)
        return self._call_openai_raw(system, user)

    def _call_openai_raw(self, system: str, user: str) -> str:
        if not settings.llm_api_key:
            raise ValueError("LLM_OUTPUT_INVALID: missing llm api key")

        payload = {
            "model": settings.llm_model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}

        resp = self.http_client.post(url, headers=headers, json=payload)
        if not resp.is_success:
            detail = resp.text[:500]
            raise ValueError(f"LLM_API_ERROR ({resp.status_code}): {detail}")
        data = resp.json()

        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _call_anthropic_raw(self, system: str, user: str) -> str:
        token = settings.anthropic_auth_token or settings.llm_api_key
        if not token:
            raise ValueError("LLM_OUTPUT_INVALID: missing anthropic auth token")

        payload = {
            "model": settings.llm_model,
            "max_tokens": 1200,
            "temperature": 0.1,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }

        url = f"{settings.anthropic_base_url.rstrip('/')}/v1/messages"
        headers = {
            "x-api-key": token,
            "anthropic-version": settings.anthropic_version,
            "content-type": "application/json",
        }

        resp = self.http_client.post(url, headers=headers, json=payload)
        if not resp.is_success:
            detail = resp.text[:500]
            raise ValueError(f"LLM_API_ERROR ({resp.status_code}): {detail}")
        data = resp.json()

        blocks = data.get("content", [])
        text_parts = [b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join([p for p in text_parts if p]).strip()

    # ---- JSON parsing ----

    def _normalize_facts_payload(self, parsed: dict) -> dict:
        """Normalize model output to match FactResponse schema."""
        allowed_types = ("definition", "claim", "method", "result", "limitation", "formula")
        facts = parsed.get("facts") or []
        out = []
        for item in facts:
            if not isinstance(item, dict):
                continue
            st = str(item.get("statement") or "").strip() or "No statement."
            if len(st) < 8:
                st = (st + " (detail)").strip()[:400]
            st = st[:400]
            ft = str(item.get("fact_type") or item.get("type") or "claim").lower()
            if ft not in allowed_types:
                ft = "claim"
            imp = item.get("importance", 0.5)
            try:
                imp = float(imp)
            except (TypeError, ValueError):
                imp = 0.5
            imp = max(0.0, min(1.0, imp))
            out.append({"statement": st, "fact_type": ft, "importance": imp})
        return {"facts": out}

    def _parse_json_content(self, content: str) -> FactResponse:
        if not content:
            raise ValueError("LLM_OUTPUT_INVALID: empty model output")
        last_error: Exception | None = None
        for candidate in (content.strip(), self._extract_json_string(content)):
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                parsed = self._normalize_facts_payload(parsed)
                return FactResponse.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
        msg = "LLM_OUTPUT_INVALID: invalid json schema"
        if last_error:
            msg += f" (e.g. {last_error!s})"
        snippet = content.strip()[:200]
        if len(content.strip()) > 200:
            snippet += "..."
        msg += f". Raw snippet: {snippet!r}"
        raise ValueError(msg) from last_error

    def _parse_json_generic(self, content: str) -> dict:
        """Parse raw LLM output into a dict, stripping code fences."""
        if not content:
            raise ValueError("LLM_OUTPUT_INVALID: empty model output")
        last_error: Exception | None = None
        for candidate in (content.strip(), self._extract_json_string(content)):
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError as exc:
                last_error = exc
        snippet = content.strip()[:200]
        msg = f"LLM_OUTPUT_INVALID: cannot parse JSON. Raw snippet: {snippet!r}"
        raise ValueError(msg) from last_error

    # ---- fact extraction ----

    def _fact_prompt_parts(self, text: str) -> tuple[str, str]:
        system = (
            "You extract key learning points from academic text for presentation slides. "
            "Each statement must be a self-contained bullet point — concise enough to fit "
            "on one line of a slide (max ~20 words). Avoid academic jargon; prefer plain, "
            "direct language a student can grasp at a glance. "
            "Return strict JSON only with key 'facts'."
        )
        user = (
            "Extract up to 8 key points suitable as slide bullet points.\n"
            "Rules:\n"
            "- Each statement: max ~20 words, one core idea per bullet\n"
            "- Start with the key noun or verb, not filler words\n"
            "- Use active voice where possible\n"
            "- Classify each as: definition, claim, method, result, limitation, or formula\n\n"
            "Return JSON object: {\"facts\":[{\"statement\":string,\"fact_type\":string,\"importance\":number}]}"
            " and nothing else.\n\n"
            f"Text:\n{text}"
        )
        return system, user

    def extract_facts(self, chunk_id: str, text: str) -> list[FactCandidate]:
        if self.provider == "mock":
            return _fallback_extract(chunk_id, text)

        last_error: Exception | None = None
        for _ in range(settings.llm_max_retries + 1):
            try:
                system, user = self._fact_prompt_parts(text)
                raw = self._call_llm_raw(system, user)
                result = self._parse_json_content(raw)
                facts = []
                for idx, item in enumerate(result.facts[:8], start=1):
                    facts.append(
                        FactCandidate(
                            fact_id=f"f_{chunk_id}_{idx}",
                            chunk_id=chunk_id,
                            statement=item.statement.strip(),
                            fact_type=item.fact_type,
                            importance=float(item.importance),
                        )
                    )
                if not facts:
                    raise ValueError("LLM_OUTPUT_INVALID: no facts returned")
                return facts
            except Exception as exc:  # noqa: BLE001
                last_error = exc

        if last_error:
            raise last_error
        raise ValueError("LLM_OUTPUT_INVALID: unknown llm failure")

    # ---- outline building ----

    def build_outline(self, facts: list[FactCandidate], language: str) -> OutlineResponse:
        """Ask LLM to organize facts into a teaching-oriented outline."""
        if self.provider == "mock":
            return self._mock_outline(facts)

        fact_list_str = "\n".join(
            f"[{i}] ({f.fact_type}, importance={f.importance:.2f}) {f.statement}"
            for i, f in enumerate(facts)
        )

        system = (
            "You are an expert instructional designer creating teaching slide decks. "
            "Each subsection becomes ONE slide. Design for visual clarity and learning flow. "
            f"Respond in {language}. Return strict JSON only."
        )
        user = (
            f"Organize the following {len(facts)} facts into a presentation slide deck outline.\n\n"
            "Slide design constraints:\n"
            "- Each subsection = 1 slide. Max 6 bullets per slide (subsection).\n"
            "- Ideal: 3-5 bullets per slide for readability.\n"
            "- 3-8 sections total, each with 1-5 subsections (slides).\n"
            "- Balance section sizes — avoid putting 80% of content in one section.\n\n"
            "Learning flow:\n"
            "- Order sections from foundational concepts → advanced/applied topics.\n"
            "- Within each section, progress from overview → details → implications.\n"
            "- Group related facts on the same slide; don't scatter related ideas.\n"
            "- Section headings: short, topic-focused (2-5 words ideal).\n"
            "- Subsection headings: describe the slide's key message.\n\n"
            "Each subsection references facts by their [index] numbers.\n"
            "Every fact index must appear in exactly one subsection.\n\n"
            "Return JSON:\n"
            '{"sections":[{"heading":string,"summary_note":string,'
            '"subsections":[{"heading":string,"fact_indices":[int,...]}]}]}\n\n'
            f"Facts:\n{fact_list_str}"
        )

        last_error: Exception | None = None
        for _ in range(settings.llm_max_retries + 1):
            try:
                raw = self._call_llm_raw(system, user)
                parsed = self._parse_json_generic(raw)
                outline = OutlineResponse.model_validate(parsed)
                # Validate all fact_indices are in range
                valid_range = set(range(len(facts)))
                used = set()
                for sec in outline.sections:
                    for sub in sec.subsections:
                        for idx in sub.fact_indices:
                            if idx not in valid_range:
                                raise ValueError(f"fact_index {idx} out of range [0, {len(facts)})")
                            used.add(idx)
                # If some facts are unused, append them to the last subsection
                unused = valid_range - used
                if unused and outline.sections:
                    last_sub = outline.sections[-1].subsections[-1]
                    last_sub.fact_indices.extend(sorted(unused))
                return outline
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("build_outline attempt failed: %s", exc)

        if last_error:
            raise last_error
        raise ValueError("LLM_OUTPUT_INVALID: outline generation failed")

    def _mock_outline(self, facts: list[FactCandidate]) -> OutlineResponse:
        """Generate a simple outline for mock/testing mode."""
        sections = []
        group_size = 4
        for s_idx in range(0, len(facts), group_size * 2):
            chunk = facts[s_idx : s_idx + group_size * 2]
            subsections = []
            for ss_idx in range(0, len(chunk), group_size):
                sub_chunk = chunk[ss_idx : ss_idx + group_size]
                indices = [s_idx + ss_idx + j for j in range(len(sub_chunk))]
                subsections.append(OutlineSubsection(
                    heading=f"Topic {s_idx // (group_size * 2) + 1}.{ss_idx // group_size + 1}",
                    fact_indices=indices,
                ))
            sections.append(OutlineSection(
                heading=f"Section {s_idx // (group_size * 2) + 1}",
                summary_note=f"Covers facts {s_idx}-{min(s_idx + group_size * 2, len(facts)) - 1}",
                subsections=subsections,
            ))
        if not sections:
            sections.append(OutlineSection(
                heading="Overview",
                summary_note="All extracted content",
                subsections=[OutlineSubsection(heading="Key Points", fact_indices=list(range(len(facts))))],
            ))
        return OutlineResponse(sections=sections)

    # ---- annotation writing ----

    def write_annotations(self, sections_data: list[dict], language: str) -> list[str]:
        """Ask LLM to write teaching annotations for each subsection."""
        if self.provider == "mock":
            total = sum(len(s.get("subsections", [])) for s in sections_data)
            return ["Key concepts and their implications." for _ in range(total)]

        # Build a summary of sections for the prompt
        desc_parts = []
        total_subs = 0
        for s in sections_data:
            for ss in s.get("subsections", []):
                desc_parts.append(
                    f"[{total_subs}] Section: {s['heading']} / Subsection: {ss['heading']} — "
                    f"Bullets: {'; '.join(ss.get('bullet_texts', [])[:3])}"
                )
                total_subs += 1

        system = (
            "You are a presentation coach writing speaker notes for teaching slides. "
            "Your notes help the presenter explain each slide clearly and engage the audience. "
            f"Respond in {language}. Return strict JSON only."
        )
        user = (
            f"Write a speaker note for each of the following {total_subs} slides (subsections).\n\n"
            "Speaker note guidelines:\n"
            "- 1-3 sentences that the presenter reads or paraphrases while showing the slide.\n"
            "- Start with the key takeaway or 'why this matters'.\n"
            "- Include a concrete example, analogy, or question to engage the audience when possible.\n"
            "- Use conversational tone — as if speaking to students, not writing a paper.\n"
            "- If the slide has a formula, briefly explain what each variable means.\n\n"
            "Return JSON:\n"
            '{"annotations":[{"subsection_index":int,"annotation":string}]}\n\n'
            f"Slides:\n" + "\n".join(desc_parts)
        )

        try:
            raw = self._call_llm_raw(system, user)
            parsed = self._parse_json_generic(raw)
            resp = AnnotationsResponse.model_validate(parsed)
            # Build list indexed by subsection order
            result = [""] * total_subs
            for item in resp.annotations:
                if 0 <= item.subsection_index < total_subs:
                    result[item.subsection_index] = item.annotation
            return result
        except Exception as exc:  # noqa: BLE001
            logger.warning("write_annotations failed, falling back to empty: %s", exc)
            return ["" for _ in range(total_subs)]
