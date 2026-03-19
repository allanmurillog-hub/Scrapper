import os
import shutil

folder = "C:\\Users\\Allan\\OneDrive\\Desktop\\Disorganized files"


folders_to_create = ["PDFs", "Text Files", "Images",
                     "Installers and Spreadsheets", "Compressed Files", "Other Files"]

for f in folders_to_create:
    os.makedirs(os.path.join(folder, f), exist_ok=True)

for file in os.listdir(folder):
    file_path = os.path.join(folder, file)
    if not os.path.isfile(file_path):
        continue

    filelower = file.lower()

    if filelower.endswith(".pdf"):
        shutil.move(os.path.join(folder, file),
                    os.path.join(folder, "PDFs", file))
    elif filelower.endswith(".txt"):
        shutil.move(os.path.join(folder, file),
                    os.path.join(folder, "Text Files", file))
    elif filelower.endswith(".jpg") or filelower.endswith(".png"):
        shutil.move(os.path.join(folder, file),
                    os.path.join(folder, "Images", file))
    elif filelower.endswith(".msi"):
        shutil.move(os.path.join(folder, file), os.path.join(
            folder, "Installers and Spreadsheets", file))
    elif filelower.endswith(".rar") or filelower.endswith(".zip"):
        shutil.move(os.path.join(folder, file), os.path.join(
            folder, "Compressed Files", file))
    else:
        destination = "Other Files"

        if destination:
            try:
                shutil.move(os.path.join(folder, file),
                            os.path.join(folder, destination, file))
            except Exception as e:
                print(f"Error moving file {file}: {e}")
