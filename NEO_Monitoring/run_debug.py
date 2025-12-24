import sys
import traceback
import os

# Redirect ALL output to file
log_file = open('crash_debug.log', 'w', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

print("=== CRASH DEBUG STARTED ===\n")

try:
    os.chdir(r'c:\Users\Carlos\Documents\GitHub\NEO_Monitor_BD_Project\NEO_Monitoring')
    print("Working directory set\n")
    
    print("Importing tk...")
    import tkinter as tk
    print("OK\n")
    
    print("Importing gui_main...")
    from src import gui_main
    print("OK\n")
    
    print("Creating App instance...")
    app = gui_main.App()
    print("OK\n")
    
    print("Starting mainloop...\n")
    app.mainloop()
    
except Exception as e:
    print(f"\n\n=== EXCEPTION CAUGHT ===")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print(f"\n=== TRACEBACK ===")
    traceback.print_exc()
    
finally:
    print("\n=== DEBUG ENDED ===")
    log_file.close()
    
# Re-open and print to console
with open('crash_debug.log', 'r', encoding='utf-8') as f:
    print(f.read())
