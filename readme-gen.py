import json

def get_source_label(url):
    if not url:
        return None
    url_lower = url.lower()
    if 'github.com' in url_lower:
        return 'GitHub'
    if 'gitlab.com' in url_lower or 'dev.funkwhale.audio' in url_lower:
        return 'GitLab'
    if 'codeberg.org' in url_lower:
        return 'Codeberg'
    if 'bitbucket.org' in url_lower:
        return 'Bitbucket'
    if 'pagure.io' in url_lower:
        return 'Pagure'
    return 'Source'

def main():
    db_path = "dyos-db.json"
    output_path = "README.md"

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        print(f"Error: {db_path} not found.")
        return

    lines = []
    # Header
    lines.append("**[[Submit product or tutorial](https://github.com/Atarity/deploy-your-own-saas/issues/new?assignees=&labels=&template=submit-new-product.md)]** or make it thru PR.")
    lines.append("")
    lines.append("![Scryer](/scryer.jpg)")
    lines.append("")

    # Groups
    for group in db.get("groups", []):
        group_name = group.get("name", "Unknown")
        icon = group.get("icon", "")
        lines.append(f"### {icon} Deploy your own `{group_name}`")

        for project in group.get("projects", []):
            name = project.get("name", "Unnamed")
            description = project.get("description", "")
            site = project.get("site", "")
            github = project.get("github", "")

            # Use site if available, else github
            primary_link = site if site else github
            
            # Format project line
            # Ensure there is a space between name link and description dash
            line = f"- [{name}]({primary_link}) — {description}"

            # Link normalization for comparison
            site_norm = site.rstrip('/') if site else ""
            github_norm = github.rstrip('/') if github else ""

            if github_norm and site_norm != github_norm:
                label = get_source_label(github)
                # Append source link at the end
                line += f" [({label})]({github})"
            
            lines.append(line)
        
        lines.append("") # Spacer between groups

    # Footer
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

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
