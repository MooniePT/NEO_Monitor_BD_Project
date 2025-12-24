import sys
import os
import traceback
import tkinter as tk

# Add the current directory to sys.path to ensure imports work as expected
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print(f"DEBUG: sys.path: {sys.path}")
print("DEBUG: Attempting to import gui_main...")

try:
    import gui_main
    print("DEBUG: Import successful. Initializing App...")
    
    # We need to ensure we don't start a second root if gui_main does something weird, 
    # but gui_main's main block shouldn't run on import.
    
    app = gui_main.App()
    print("DEBUG: App initialized. Starting mainloop...")
    app.mainloop()
    print("DEBUG: Mainloop finished.")

except Exception:
    print("DEBUG: Exception caught during execution:")
    traceback.print_exc()
except SystemExit as e:
    print(f"DEBUG: SystemExit caught: {e}")
