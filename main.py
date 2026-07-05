import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import threading
import queue


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Set the application directory for consistent behavior
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)


class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer Pro")
        self.root.geometry("800x650")

        # Variables
        self.image_files = []
        self.preview_images = []
        self.current_preview_index = 0
        self.resize_queue = queue.Queue()

        # Create menu bar
        self.create_menu_bar()

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(self.main_frame, text="Image Resizer Pro",
                                font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Drag and drop area
        self.drop_frame = ttk.LabelFrame(self.main_frame, text="Drop Zone", padding="10")
        self.drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        self.drop_frame.columnconfigure(0, weight=1)

        self.drop_label = tk.Label(self.drop_frame, text="Drop image files here\nor click to browse",
                                   bg='lightgray', relief='ridge', height=6,
                                   font=('Arial', 12))
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.drop_label.bind("<Button-1>", self.browse_files)

        # Enable drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

        # Settings frame
        settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        settings_frame.columnconfigure(1, weight=1)

        # Width
        ttk.Label(settings_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(settings_frame, textvariable=self.width_var, width=15)
        self.width_entry.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Height
        ttk.Label(settings_frame, text="Height:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(settings_frame, textvariable=self.height_var, width=15)
        self.height_entry.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Presets
        ttk.Label(settings_frame, text="Presets:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(settings_frame, textvariable=self.preset_var,
                                         values=["Custom", "1920x1080", "1280x720", "800x600", "640x480", "320x240"],
                                         state="readonly", width=15)
        self.preset_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.preset_combo.bind('<<ComboboxSelected>>', self.on_preset_selected)
        self.preset_combo.set("Custom")

        # Maintain aspect ratio
        self.maintain_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Maintain aspect ratio",
                        variable=self.maintain_aspect).grid(row=1, column=2, columnspan=1,
                                                            sticky=tk.W, padx=5, pady=5)

        # Add size to filename
        self.add_size_to_filename = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Add size to filename",
                        variable=self.add_size_to_filename).grid(row=1, column=3,
                                                                 sticky=tk.W, padx=5, pady=5)

        # Output settings
        ttk.Label(settings_frame, text="Output Format:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.format_var = tk.StringVar(value="JPEG")
        self.format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var,
                                         values=["JPEG", "PNG", "WEBP", "BMP"],
                                         state="readonly", width=15)
        self.format_combo.grid(row=2, column=1, sticky=tk.W, padx=5)

        # Output directory
        ttk.Label(settings_frame, text="Output Folder:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.output_dir_var = tk.StringVar(value="resized_images")
        self.output_dir_entry = ttk.Entry(settings_frame, textvariable=self.output_dir_var, width=30)
        self.output_dir_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(settings_frame, text="Browse", command=self.browse_output_dir).grid(row=3, column=3, padx=5)

        # Control buttons
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.resize_btn = ttk.Button(control_frame, text="Resize All",
                                     command=self.start_resize, width=20)
        self.resize_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = ttk.Button(control_frame, text="Clear List",
                                    command=self.clear_files, width=20)
        self.clear_btn.grid(row=0, column=1, padx=5)

        # File list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Files", padding="10")
        list_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # File listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical",
                                  command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # File count label
        self.file_count_label = ttk.Label(self.main_frame, text="Total files: 0")
        self.file_count_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # Configure grid weights for resizing
        self.main_frame.rowconfigure(4, weight=1)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=0)

        # Bind resize events
        self.width_entry.bind('<KeyRelease>', self.on_size_change)
        self.height_entry.bind('<KeyRelease>', self.on_size_change)

        # Configure the root for proper resizing
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Start the queue processor
        self.process_queue()

    def create_menu_bar(self):
        """Create the menu bar with About menu only"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_command(label="About", command=self.show_about)

    def show_about(self):
        """Show About dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Image Resizer Pro")
        about_window.geometry("420x380")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.focus_set()

        frame = ttk.Frame(about_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(frame, text="📷 Image Resizer Pro",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))

        version_label = ttk.Label(frame, text="Version 1.0.0")
        version_label.pack(pady=(0, 15))

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=(0, 15))

        license_label = ttk.Label(frame, text="License: Freeware")
        license_label.pack(anchor=tk.W, pady=2)

        copyright_label = ttk.Label(frame, text="Copyright © 2026")
        copyright_label.pack(anchor=tk.W, pady=2)

        author_label = ttk.Label(frame, text="Author: Pavlenko Evgeniy")
        author_label.pack(anchor=tk.W, pady=2)

        email_label = ttk.Label(frame, text="Email: pavlenkoevgeniy85@gmail.com")
        email_label.pack(anchor=tk.W, pady=2)

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=(15, 15))

        desc_text = "A simple and powerful tool for batch resizing images.\n"
        desc_text += "Supports drag & drop, multiple formats, and aspect ratio preservation."
        desc_label = tk.Label(frame, text=desc_text,
                              font=('Arial', 9),
                              wraplength=360,
                              justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))

        close_btn = ttk.Button(frame, text="Close", command=about_window.destroy)
        close_btn.pack()

    def on_drop(self, event):
        """Handle drag and drop events"""
        files = self.root.tk.splitlist(event.data)
        added_count = 0
        for file in files:
            if file and os.path.isfile(file):
                if file not in self.image_files:
                    self.image_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
                    added_count += 1
        self.file_count_label.config(text=f"Total files: {len(self.image_files)}")
        if added_count > 0:
            self.status_var.set(f"Added {added_count} files")

    def browse_files(self, event=None):
        """Browse for image files"""
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
        )
        added_count = 0
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
                added_count += 1
        self.file_count_label.config(text=f"Total files: {len(self.image_files)}")
        if added_count > 0:
            self.status_var.set(f"Added {added_count} files")

    def clear_files(self):
        """Clear all files from the list"""
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="Total files: 0")
        self.status_var.set("Cleared all files")

    def on_preset_selected(self, event):
        """Handle preset selection"""
        preset = self.preset_var.get()
        if preset != "Custom":
            width, height = preset.split('x')
            self.width_var.set(width)
            self.height_var.set(height)

    def on_size_change(self, event):
        """Handle size input changes"""
        pass

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def start_resize(self):
        """Start the resizing process"""
        if not self.image_files:
            messagebox.showwarning("No Files", "Please add some image files first!")
            return

        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid positive numbers for width and height")
            return

        output_dir = self.output_dir_var.get()
        if not output_dir:
            output_dir = "resized_images"

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        self.resize_btn.config(state='disabled')
        self.status_var.set("Resizing images...")

        thread = threading.Thread(target=self.resize_images,
                                  args=(width, height, output_dir))
        thread.daemon = True
        thread.start()

    def resize_images(self, width, height, output_dir):
        """Resize images (runs in separate thread)"""
        format_map = {
            "JPEG": "JPEG",
            "PNG": "PNG",
            "WEBP": "WEBP",
            "BMP": "BMP"
        }

        image_format = format_map.get(self.format_var.get(), "JPEG")
        maintain_aspect = self.maintain_aspect.get()
        add_size_to_filename = self.add_size_to_filename.get()

        success_count = 0
        total_files = len(self.image_files)
        errors = []

        for i, file_path in enumerate(self.image_files):
            try:
                self.resize_queue.put(("status", f"Processing {i + 1}/{total_files}: {os.path.basename(file_path)}"))

                with Image.open(file_path) as img:
                    if maintain_aspect:
                        original_width, original_height = img.size
                        ratio = min(width / original_width, height / original_height)
                        new_width = int(original_width * ratio)
                        new_height = int(original_height * ratio)
                    else:
                        new_width = width
                        new_height = height

                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    filename = Path(file_path).stem
                    extension = Path(file_path).suffix[1:].lower()

                    if add_size_to_filename:
                        filename = f"{filename}_{new_width}x{new_height}"

                    if image_format == "JPEG" and extension in ['png', 'bmp', 'gif']:
                        if resized_img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', resized_img.size, (255, 255, 255))
                            if resized_img.mode == 'P':
                                resized_img = resized_img.convert('RGBA')
                            background.paste(resized_img,
                                             mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                            resized_img = background
                        output_path = Path(output_dir) / f"{filename}.jpg"
                    else:
                        output_path = Path(output_dir) / f"{filename}.{image_format.lower()}"

                    save_kwargs = {}
                    if image_format == "JPEG":
                        save_kwargs['quality'] = 95
                        save_kwargs['optimize'] = True

                    resized_img.save(output_path, format=image_format, **save_kwargs)
                    success_count += 1

            except Exception as e:
                error_msg = f"Error processing {os.path.basename(file_path)}: {str(e)}"
                errors.append(error_msg)
                self.resize_queue.put(("error", error_msg))

        if success_count == total_files:
            self.resize_queue.put(("status", f"Successfully resized all {success_count} images!"))
        else:
            status_msg = f"Resized {success_count} out of {total_files} images"
            if errors:
                status_msg += " (check for errors)"
            self.resize_queue.put(("status", status_msg))

        self.resize_queue.put(("complete", success_count == total_files, errors))

    def process_queue(self):
        """Process the queue for status updates"""
        try:
            while not self.resize_queue.empty():
                message = self.resize_queue.get_nowait()
                if message[0] == "status":
                    self.status_var.set(message[1])
                elif message[0] == "error":
                    messagebox.showerror("Error", message[1])
                elif message[0] == "complete":
                    self.resize_btn.config(state='normal')
                    if message[1]:
                        messagebox.showinfo("Complete", "Image resizing completed successfully!")
                    else:
                        if message[2]:
                            error_summary = "\n".join(message[2][:3])
                            if len(message[2]) > 3:
                                error_summary += f"\n... and {len(message[2]) - 3} more errors"
                            messagebox.showwarning("Completed with Errors",
                                                   f"Image resizing completed with errors:\n\n{error_summary}")
                        else:
                            messagebox.showwarning("Completed", "Image resizing completed with some issues.")
        except:
            pass

        self.root.after(100, self.process_queue)


def main():
    # Change to the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        os.chdir(os.path.dirname(sys.executable))

    root = TkinterDnD.Tk()
    app = ImageResizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
