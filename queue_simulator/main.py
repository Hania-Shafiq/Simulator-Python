"""
Main launcher for Sapphire Shopping Outlet Queue Simulator.
"""
import tkinter as tk
from simulator_gui import QueueSimulatorGUI

def main():
    """Launch the queue simulator application."""
    root = tk.Tk()
    
    # Set application icon and title
    root.title("Sapphire Shopping Outlet - Queue Simulator")
    
    # Create and run the application
    app = QueueSimulatorGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()