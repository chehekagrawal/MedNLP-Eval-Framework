import os
import glob
import subprocess

def main():
    # Find all JSON files in the test_data folder (even inside subfolders)
    json_files = glob.glob("test_data/**/*.json", recursive=True)
    
    if not json_files:
        print("❌ No JSON files found in test_data/")
        return

    print(f"📂 Found {len(json_files)} files. Starting evaluation pipeline...\n")

    for input_path in json_files:
        # Extract just the filename (e.g., chart_01.json)
        file_name = os.path.basename(input_path)
        
        # Create the output path (e.g., output/chart_01.json)
        output_path = os.path.join("output", file_name)
        
        # Run test.py via terminal command
        subprocess.run(["python", "test.py", input_path, output_path])

    print("\n🎉 All files processed successfully! Check the 'output' folder.")

if __name__ == "__main__":
    main()