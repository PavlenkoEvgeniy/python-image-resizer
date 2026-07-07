"""Main application window UI."""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from typing import Callable, Optional

from image_resizer.config import AppConfig
from image_resizer.dialogs import AboutDialog, ErrorDialog
from image_resizer.image_processor import ImageProcessor, OutputFormat


class ImageResizerWindow:
    """Main application window for Image Resizer."""

    def __init__(self, root: TkinterDnD.Tk, config: Optional[AppConfig] = None):
        """Initialize the main window.

        Args:
            root: Tkinter root window.
            config: Application configuration.
        """
        self.root = root
        self.config = config or AppConfig()
        self.processor = ImageProcessor()

        # State
        self.image_files: list[str] = []
        self.resize_queue: queue.Queue = queue.Queue()
        self._processing = False

        self._setup_window()
        self._create_widgets()
        self._center_window()
        self._start_queue_processor()

    def _center_window(self) -> None:
        """Center window on screen after all widgets are created."""
        self.root.update()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 650
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("Image Resizer Pro")
        self.root.geometry("800x650")
        
        # Withdraw window, center it, then show - ensures correct position
        self.root.withdraw()
        self.root.update()

        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 650
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.deiconify()

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure main frame grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(4, weight=1)

        # Title
        title = ttk.Label(
            self.main_frame,
            text="Image Resizer Pro",
            font=("Arial", 20, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Drop zone
        self._create_drop_zone()

        # Settings
        self._create_settings()

        # Control buttons
        self._create_controls()

        # File list
        self._create_file_list()

        # Status bar
        self._create_status_bar()

    def _create_drop_zone(self) -> None:
        """Create the drag and drop zone."""
        drop_frame = ttk.LabelFrame(self.main_frame, text="Drop Zone", padding="10")
        drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        drop_frame.columnconfigure(0, weight=1)

        self.drop_label = tk.Label(
            drop_frame,
            text="Drop image files here\nor click to browse",
            bg="lightgray",
            relief="ridge",
            height=6,
            font=("Arial", 12),
        )
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.drop_label.bind("<Button-1>", self._on_browse_clicked)

        # Enable drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

    def _create_settings(self) -> None:
        """Create settings panel."""
        settings = ttk.LabelFrame(self.main_frame, text="Settings", padding="10")
        settings.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        settings.columnconfigure(1, weight=1)
        settings.columnconfigure(3, weight=1)

        # Width
        ttk.Label(settings, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.width_var = tk.StringVar(value=str(self.config.default_width))
        self.width_entry = ttk.Entry(settings, textvariable=self.width_var, width=15)
        self.width_entry.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Height
        ttk.Label(settings, text="Height:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.height_var = tk.StringVar(value=str(self.config.default_height))
        self.height_entry = ttk.Entry(settings, textvariable=self.height_var, width=15)
        self.height_entry.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Presets
        preset_names = [p[0] for p in self.config.presets]
        ttk.Label(settings, text="Presets:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.preset_var = tk.StringVar(value="Custom")
        self.preset_combo = ttk.Combobox(
            settings,
            textvariable=self.preset_var,
            values=preset_names,
            state="readonly",
            width=15,
        )
        self.preset_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.preset_combo.set("Custom")

        # Maintain aspect ratio
        self.maintain_aspect = tk.BooleanVar(value=self.config.maintain_aspect_ratio)
        ttk.Checkbutton(
            settings,
            text="Maintain aspect ratio",
            variable=self.maintain_aspect,
        ).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        # Add size to filename
        self.add_size_to_filename = tk.BooleanVar(value=self.config.add_dimensions_to_filename)
        ttk.Checkbutton(
            settings,
            text="Add size to filename",
            variable=self.add_size_to_filename,
        ).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        # Output format
        ttk.Label(settings, text="Output Format:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.format_var = tk.StringVar(value=self.config.default_output_format)
        self.format_combo = ttk.Combobox(
            settings,
            textvariable=self.format_var,
            values=[f.value for f in OutputFormat],
            state="readonly",
            width=15,
        )
        self.format_combo.grid(row=2, column=1, sticky=tk.W, padx=5)

        # Output directory
        ttk.Label(settings, text="Output Folder:").grid(row=3, column=0, sticky=tk.W, padx=5)
        self.output_dir_var = tk.StringVar(value=self.config.default_output_dir)
        self.output_dir_entry = ttk.Entry(settings, textvariable=self.output_dir_var, width=30)
        self.output_dir_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(settings, text="Browse", command=self._browse_output_dir).grid(
            row=3, column=3, padx=5
        )

        # Bind size change events
        self.width_entry.bind("<KeyRelease>", self._on_size_changed)
        self.height_entry.bind("<KeyRelease>", self._on_size_changed)

    def _create_controls(self) -> None:
        """Create control buttons."""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.resize_btn = ttk.Button(
            control_frame,
            text="Resize All",
            command=self._start_resize,
            width=20,
        )
        self.resize_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = ttk.Button(
            control_frame,
            text="Clear List",
            command=self._clear_files,
            width=20,
        )
        self.clear_btn.grid(row=0, column=1, padx=5)

    def _create_file_list(self) -> None:
        """Create the file list widget."""
        list_frame = ttk.LabelFrame(self.main_frame, text="Files", padding="10")
        list_frame.grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # File count
        self.file_count_label = ttk.Label(self.main_frame, text="Total files: 0")
        self.file_count_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

    def _create_status_bar(self) -> None:
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def _start_queue_processor(self) -> None:
        """Start the queue processor for async updates."""
        self.root.after(100, self._process_queue)

    # Event handlers

    def _on_drop(self, event) -> None:
        """Handle drag and drop events."""
        files = self.root.tk.splitlist(event.data)
        self._add_files(files)

    def _on_browse_clicked(self, event=None) -> None:
        """Open file browser."""
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")],
        )
        self._add_files(files)

    def _add_files(self, files: tuple[str, ...]) -> None:
        """Add files to the list.

        Args:
            files: Tuple of file paths.
        """
        added = 0
        for file in files:
            if file and os.path.isfile(file):
                if file not in self.image_files:
                    self.image_files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
                    added += 1

        self._update_file_count()
        if added > 0:
            self.status_var.set(f"Added {added} files")

    def _clear_files(self) -> None:
        """Clear all files from the list."""
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
        self._update_file_count()
        self.status_var.set("Cleared all files")

    def _update_file_count(self) -> None:
        """Update the file count label."""
        self.file_count_label.config(text=f"Total files: {len(self.image_files)}")

    def _on_preset_selected(self, event=None) -> None:
        """Handle preset selection."""
        preset = self.preset_var.get()
        if preset != "Custom":
            w, h = self.config.get_preset_dimensions(preset)
            if w > 0 and h > 0:
                self.width_var.set(str(w))
                self.height_var.set(str(h))

    def _on_size_changed(self, event=None) -> None:
        """Handle size input changes."""
        self.preset_var.set("Custom")

    def _browse_output_dir(self) -> None:
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def _get_dimensions(self) -> tuple[int, int]:
        """Get target dimensions from UI.

        Returns:
            Tuple of (width, height).

        Raises:
            ValueError: If dimensions are invalid.
        """
        width = int(self.width_var.get())
        height = int(self.height_var.get())
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")
        return width, height

    def _start_resize(self) -> None:
        """Start the resize process."""
        if not self.image_files:
            ErrorDialog.show_warning("No Files", "Please add some image files first!")
            return

        try:
            width, height = self._get_dimensions()
        except ValueError:
            ErrorDialog.show_error(
                "Invalid Input",
                "Please enter valid positive numbers for width and height",
            )
            return

        output_dir = self.output_dir_var.get() or self.config.default_output_dir

        # Disable button during processing
        self.resize_btn.config(state="disabled")
        self.status_var.set("Resizing images...")

        # Create processor with current settings
        format_str = self.format_var.get()
        output_format = OutputFormat(format_str)
        processor = ImageProcessor(output_format=output_format, quality=self.config.jpeg_quality)

        # Start processing thread
        thread = threading.Thread(
            target=self._resize_worker,
            args=(
                processor,
                width,
                height,
                output_dir,
                self.maintain_aspect.get(),
                self.add_size_to_filename.get(),
            ),
            daemon=True,
        )
        thread.start()

    def _resize_worker(
        self,
        processor: ImageProcessor,
        width: int,
        height: int,
        output_dir: str,
        maintain_aspect: bool,
        add_dimensions: bool,
    ) -> None:
        """Worker thread for resizing images.

        Args:
            processor: ImageProcessor instance.
            width: Target width.
            height: Target height.
            output_dir: Output directory.
            maintain_aspect: Whether to maintain aspect ratio.
            add_dimensions: Whether to add dimensions to filename.
        """
        total = len(self.image_files)
        success = 0
        errors = []

        for i, file_path in enumerate(self.image_files):
            self.resize_queue.put(
                ("status", f"Processing {i + 1}/{total}: {os.path.basename(file_path)}")
            )

            result = processor.resize(
                file_path,
                output_dir,
                width,
                height,
                maintain_aspect,
                add_dimensions,
            )

            if result.success:
                success += 1
            else:
                errors.append(result.error)
                self.resize_queue.put(("error", result.error))

        # Final status
        if success == total:
            self.resize_queue.put(("status", f"Successfully resized all {success} images!"))
        else:
            msg = f"Resized {success} out of {total} images"
            if errors:
                msg += " (check for errors)"
            self.resize_queue.put(("status", msg))

        self.resize_queue.put(("complete", success == total, errors))

    def _process_queue(self) -> None:
        """Process the resize queue for status updates."""
        try:
            while not self.resize_queue.empty():
                message = self.resize_queue.get_nowait()
                msg_type = message[0]

                if msg_type == "status":
                    self.status_var.set(message[1])
                elif msg_type == "error":
                    ErrorDialog.show_error("Error", message[1])
                elif msg_type == "complete":
                    self.resize_btn.config(state="normal")
                    if message[1]:
                        ErrorDialog.show_info("Complete", "Image resizing completed successfully!")
                    else:
                        if message[2]:
                            error_summary = "\n".join(message[2][:3])
                            if len(message[2]) > 3:
                                error_summary += f"\n... and {len(message[2]) - 3} more errors"
                            ErrorDialog.show_warning(
                                "Completed with Errors",
                                f"Image resizing completed with errors:\n\n{error_summary}",
                            )
                        else:
                            ErrorDialog.show_warning(
                                "Completed", "Image resizing completed with some issues."
                            )
        except queue.Empty:
            pass

        self.root.after(100, self._process_queue)

    def show_about(self) -> None:
        """Show the about dialog."""
        AboutDialog(self.root)