import os

SKILLS_DIR = ".claude/skills"


def parse_skill_file(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content.strip()

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content.strip()

    front_matter_raw = parts[1]
    body = parts[2].strip()

    metadata = {}
    for line in front_matter_raw.strip().splitlines():
        line = line.strip()
        if ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip()] = val.strip().strip("\"'")

    return metadata, body


def load_skills(skills_dir: str = SKILLS_DIR) -> list[dict]:
    if not os.path.exists(skills_dir):
        return []

    skills = []
    for entry in sorted(os.listdir(skills_dir)):
        entry_path = os.path.join(skills_dir, entry)
        if not os.path.isdir(entry_path):
            continue

        skill_file = os.path.join(entry_path, "SKILL.md")
        if not os.path.exists(skill_file):
            skill_file = os.path.join(entry_path, "skill.md")
            if not os.path.exists(skill_file):
                continue

        with open(skill_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        metadata, body = parse_skill_file(raw_text)

        skills.append({
            "name": metadata.get("name", entry),
            "description": metadata.get("description", ""),
            "content": body,
        })

    ans = build_system_prompt(skills)
    return ans


def build_system_prompt(skills: list[dict]) -> str:
    if not skills:
        return ""

    lines = ["Available skills:"]
    for s in skills:
        name = s["name"]
        desc = s["description"]
        body = s["content"]

        skill_desc = f"- {name}: {desc}"
        if body:
            skill_desc += f"\n  Instructions: {body}"
        lines.append(skill_desc)

    return "\n".join(lines)