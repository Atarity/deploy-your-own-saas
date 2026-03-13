import json
from datetime import datetime, timezone

def format_relative_time(pushed_at_str):
    if not pushed_at_str:
        return None, None

    try:
        # GitHub uses UTC 'Z' or offset
        pushed_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
        # Current time context from user
        now = datetime(2026, 3, 13, 16, 30, 29, tzinfo=timezone.utc)

        diff = now - pushed_at
        seconds = diff.total_seconds()

        if seconds < 0:
            return "just now", "🟢"

        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        months = days / 30.44
        years = days / 365.25

        # Determine status color
        if days < 30:
            status = "🟢"
        elif days < 365:
            status = "🟠"
        else:
            status = "🔴"

        # Determine relative text
        if hours < 1:
            text = f"{int(minutes)}m"
        elif days < 1:
            text = f"{int(hours)}h"
        elif months < 1:
            text = f"{int(days)}d"
        elif years < 1:
            text = f"{int(months)}mo"
        else:
            text = f"{int(years)}y"

        return text, status
    except Exception:
        return None, None

def main():
    db_path = "dyos-db.json"
    output_path = "README.md"

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        print(f"Error: {db_path} not found.")
        return
    # Header
    lines = []
    lines.append("**[[Submit product or tutorial](https://github.com/Atarity/deploy-your-own-saas/issues/new?assignees=&labels=&template=submit-new-product.md)]** or make it thru PR.")
    lines.append("")
    lines.append("![Scryer](/scryer.jpg)")
    lines.append("")

    for group in db.get("groups", []):
        group_name = group.get("name", "Unknown")
        icon = group.get("icon", "")
        lines.append(f"### {icon} Deploy your own `{group_name}`")

        # Sort projects by stars count descending
        projects = group.get("projects", [])
        projects.sort(key=lambda x: x.get("stars", 0), reverse=True)

        for project in projects:
            name = project.get("name", "Unnamed")
            description = project.get("description", "")
            github = project.get("github", "")
            site = project.get("site", "")
            stars = project.get("stars", 0)
            pushed_at = project.get("pushed_at", "")

            # Primary Link: GitHub priority, then Site
            primary_link = github if github else site

            # Format enrichment stats: [⭐️ stars, status time]
            stats_content = []
            if stars > 0:
                stats_content.append(f"⭐️ {stars}") # No comma delimiters

            rel_time, status = format_relative_time(pushed_at)
            if rel_time:
                stats_content.append(f"{status} {rel_time}")

            stats_str = f" [{', '.join(stats_content)}]" if stats_content else ""

            # Final line format: - [Name](Link) [Stats] — Description
            line = f"- [{name}]({primary_link}){stats_str} — {description}"
            lines.append(line)

        lines.append("")
    #   Footer
    lines.append("----")
    lines.append("")
    lines.append("Worth to check:")
    lines.append("- https://www.reddit.com/r/selfhosted/")
    lines.append("- https://geek-cookbook.funkypenguin.co.nz/")
    lines.append("- https://github.com/sovereign/sovereign")
    lines.append("- https://roll.urown.net/about.html")
    lines.append("")
    lines.append("Cover mashup based on [KADA★BURA](https://www.kadaburadraws.com/pixel-art#/text-rpg/) art.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Successfully generated {output_path} .")

if __name__ == "__main__":
    main()
