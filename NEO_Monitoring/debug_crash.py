"""
Script de debug para capturar o crash após conexão à BD
"""
import sys
import traceback

# Redirect stderr to file
sys.stderr = open('crash_log.txt', 'w')
sys.stdout = open('crash_log.txt', 'a')

print("=== DEBUG CRASH SCRIPT STARTED ===")

try:
    # Import everything
    print("Importing gui_main...")
    from src import gui_main
    
    print("Creating App instance...")
    app = gui_main.App()
    
    print("Starting mainloop...")
    app.mainloop()
    
except Exception as e:
    print(f"\n=== EXCEPTION CAUGHT ===")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {e}")
    print(f"\n=== FULL TRACEBACK ===")
    traceback.print_exc()
    
finally:
    print("\n=== DEBUG SCRIPT ENDED ===")
    sys.stderr.close()
    sys.stdout.close()
