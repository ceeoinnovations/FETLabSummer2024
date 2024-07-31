import os , sys , shutil

home_directory = os.path.expanduser("~")

def get_file_path(filename):
    for root, dirs, files in os.walk(home_directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

def move_file(source, destination):
    try:
        shutil.move(source, destination)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def copy_file(source , destination):
    try:
        shutil.copy(source, destination)
        print(f"File copied from {source} to {destination}")
    except Exception as e:
    	print(f"Error: {e}")

def delete_file(filename):
    file_path = get_file_path(filename)
    if file_path:
        os.remove(file_path)

def delete_dir(directory):
    try:
        shutil.rmtree(directory)
        print(f"{directory} and all its contents have been deleted.")
    except Exception as e:
    	print(f"Error: {e}")
