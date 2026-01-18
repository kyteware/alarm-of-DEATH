def get_file_content(file_path):
    """
    Reads a text file and returns its content as a string.
    """
    try:
        # 'with' ensures the file is closed automatically even if errors occur
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
            
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# --- Usage ---

# 1. Define the file path
path_to_file = '/history.txt'

# 2. Call the function and assign to an UPPERCASE variable (The Constant)
HISTORY_CONTENT = get_file_content(path_to_file)

# 3. Verify
if HISTORY_CONTENT:
    print("Content loaded into constant successfully:")
    print(HISTORY_CONTENT)