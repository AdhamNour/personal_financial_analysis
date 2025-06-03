from process_single_bank_account import process_single_bank_account
import os

def find_all_xls_files(root_folder):
    xls_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for file in filenames:
            if file.lower().endswith('.xls') and not file.lower().endswith('.xlsx'):
                xls_files.append(os.path.join(dirpath, file))
    return xls_files

# Example usage
root_dir = r'D:\Personal'  # 🔁 change this to your target folder
xls_files = find_all_xls_files(root_dir)

for file in xls_files:
    process_single_bank_account(file)
