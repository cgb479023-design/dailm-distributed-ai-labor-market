import os
import json
from datetime import datetime

def generate_offline_bundle(project_name="HAINAN_UNIVERSITY_DEMO"):
    """
    100% closed-loop logic: Fuses data and UI into a single offline HTML
    """
    print(f"[PROCESS] Generating offline demo bundle for [{project_name}]...")

    # 1. Define paths
    template_path = "prebid_workbench.html"
    expansion_data_path = "EXPANSION_RESULT.txt"
    output_dir = "dist_offline"
    output_file = f"{output_dir}/PreBid_Offline_{project_name}.html"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Read AI generated content
    try:
        with open(expansion_data_path, "r", encoding="utf-8") as f:
            expansion_content = f.read()
        print("[SUCCESS] Read AI expansion results (EXPANSION_RESULT)")
    except FileNotFoundError:
        expansion_content = "No AI data found. Please run the main flow first."
        print("[WARNING] EXPANSION_RESULT.txt not found")

    # 3. Read HTML template and inject data
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Template file {template_path} not found")
        return

    # Logic: Inject data into localStorage initialization
    sanitized_content = expansion_content.replace('`', '\\`').replace('${', '\\${')
    
    data_injection = f"""
    <!-- PreBid Master AI: Offline Data Injection -->
    <script>
        (function() {{
            const OFFLINE_DATA = {{
                project: "{project_name}",
                generatedAt: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ai_core: `{sanitized_content}`
            }};
            localStorage.setItem("prebid_offline_data_v1", JSON.stringify(OFFLINE_DATA));
            console.log("PreBid Master: Offline data injection complete");
        }})();
    </script>
    """

    # Insert injection script before </head>
    if "</head>" in html_content:
        final_html = html_content.replace("</head>", f"{data_injection}\n</head>")
    else:
        final_html = html_content + data_injection

    # 4. Save final file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"[COMPLETE] Offline demo generated: {os.path.abspath(output_file)}")
    print("TIP: You can copy this single file to a USB drive or email it to the customer.")

if __name__ == "__main__":
    generate_offline_bundle()
