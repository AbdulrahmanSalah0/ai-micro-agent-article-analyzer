import os

structure = {
    "agent": ["fetcher.py", "processor.py", "extractor.py"],
    "utils": ["json_handler.py", "webhook.py"],
    "": ["main.py", ".env", "requirements.txt", "README.md"]
}

def create_structure(base_path="."):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)

        if folder and not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)

            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(f"# {file}\n")

    print("✅ Project structure created successfully!")

if __name__ == "__main__":
    create_structure()