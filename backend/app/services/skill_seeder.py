"""Seeds the Skill catalog into the database from the SKILL.md files.

Each subdirectory of app/skills/ has a SKILL.md with YAML frontmatter
(skill_name, version, category, trigger, execution_mode) followed by a
markdown body. On startup we upsert one Skill document per file so the
API and UI reflect the real, persisted skill catalog instead of an
empty collection.
"""
import logging
import os
import re

import yaml

from app.models.skill import Skill, SkillCategory, SkillTrigger, SkillExecutionMode

logger = logging.getLogger(__name__)

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _parse_skill_md(path: str) -> dict:
    """Parse a SKILL.md file into frontmatter fields + body."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {path}")

    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()

    title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    display_name = title_match.group(1).strip() if title_match else frontmatter["skill_name"]

    intent_match = re.search(r"^##\s+Intent\s*\n(.+?)(?=\n##|\Z)", body, re.DOTALL | re.MULTILINE)
    description = intent_match.group(1).strip() if intent_match else display_name

    return {
        "name": frontmatter["skill_name"],
        "version": str(frontmatter.get("version", "1.0.0")),
        "category": frontmatter["category"],
        "trigger": frontmatter.get("trigger", "auto"),
        "execution_mode": frontmatter.get("execution_mode", "async"),
        "display_name": display_name,
        "description": description,
        "system_prompt": body,
    }


def discover_skill_files() -> list:
    """Find every SKILL.md under app/skills/."""
    if not os.path.isdir(SKILLS_DIR):
        return []
    paths = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_md = os.path.join(SKILLS_DIR, entry, "SKILL.md")
        if os.path.isfile(skill_md):
            paths.append(skill_md)
    return paths


async def seed_skills_from_catalog() -> dict:
    """Create any missing Skill documents from the on-disk catalog.

    Existing skills (matched by name) are left untouched so manual edits
    or execution metrics aren't overwritten on every restart.
    """
    created, skipped, failed = 0, 0, 0

    for path in discover_skill_files():
        try:
            data = _parse_skill_md(path)
        except Exception as e:
            logger.warning(f"Could not parse {path}: {e}")
            failed += 1
            continue

        try:
            existing = await Skill.find_one(Skill.name == data["name"])
            if existing:
                skipped += 1
                continue

            skill = Skill(
                name=data["name"],
                display_name=data["display_name"],
                description=data["description"],
                category=SkillCategory(data["category"]),
                version=data["version"],
                trigger=SkillTrigger(data["trigger"]),
                execution_mode=SkillExecutionMode(data["execution_mode"]),
                system_prompt=data["system_prompt"],
                is_core=data["category"] == "fable5",
                enabled=True,
                author="system",
                tags=[data["category"], data["trigger"]],
            )
            await skill.insert()
            created += 1
        except Exception as e:
            logger.warning(f"Could not seed skill '{data.get('name')}': {e}")
            failed += 1

    logger.info(f"Skill catalog seed: {created} created, {skipped} already present, {failed} failed")
    return {"created": created, "skipped": skipped, "failed": failed}
