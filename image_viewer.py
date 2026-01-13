"""
Lightweight Image Viewer for Windows
Supports: JPG, JPEG, PNG, WEBP, GIF
Features: View, zoom, convert between formats
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


class ImageViewer:
    SUPPORTED_FORMATS = [
        ("All Images", "*.jpg *.jpeg *.png *.webp *.gif"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("WebP", "*.webp"),
        ("GIF", "*.gif"),
    ]

    CONVERT_FORMATS = {
        "PNG": ".png",
        "JPEG": ".jpg",
        "WebP": ".webp",
        "GIF": ".gif",
        "BMP": ".bmp",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("900x700")
        self.root.minsize(600, 400)

        # State variables
        self.current_image = None  # PIL Image
        self.display_image = None  # ImageTk for display
        self.current_path = None
        self.zoom_level = 1.0
        self.original_size = (0, 0)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """Setup the main UI components."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        self._create_toolbar()

        # Image display area with scrollbars
        self._create_image_area()

        # Status bar
        self._create_statusbar()

        # Menu bar
        self._create_menu()

    def _create_toolbar(self):
        """Create the toolbar with buttons."""
        toolbar = ttk.Frame(self.main_frame, padding=5)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        # Open button
        self.btn_open = ttk.Button(toolbar, text="Open", command=self.open_image)
        self.btn_open.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Zoom controls
        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=2)

        self.btn_zoom_out = ttk.Button(toolbar, text="-", width=3, command=self.zoom_out)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=1)

        self.zoom_label = ttk.Label(toolbar, text="100%", width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)

        self.btn_zoom_in = ttk.Button(toolbar, text="+", width=3, command=self.zoom_in)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=1)

        self.btn_fit = ttk.Button(toolbar, text="Fit", command=self.fit_to_window)
        self.btn_fit.pack(side=tk.LEFT, padx=2)

        self.btn_actual = ttk.Button(toolbar, text="1:1", command=self.actual_size)
        self.btn_actual.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Convert section
        ttk.Label(toolbar, text="Convert to:").pack(side=tk.LEFT, padx=2)

        self.convert_var = tk.StringVar(value="PNG")
        self.convert_combo = ttk.Combobox(
            toolbar,
            textvariable=self.convert_var,
            values=list(self.CONVERT_FORMATS.keys()),
            state="readonly",
            width=8
        )
        self.convert_combo.pack(side=tk.LEFT, padx=2)

        self.btn_convert = ttk.Button(toolbar, text="Convert & Save", command=self.convert_image)
        self.btn_convert.pack(side=tk.LEFT, padx=2)

    def _create_image_area(self):
        """Create the scrollable image display area."""
        # Container frame
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for image display
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )

        # Scrollbars
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Welcome text
        self.canvas.create_text(
            450, 350,
            text="Click 'Open' to start",
            fill='#888888',
            font=('Segoe UI', 14),
            tags='welcome'
        )

    def _create_statusbar(self):
        """Create the status bar."""
        self.statusbar = ttk.Frame(self.main_frame)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(self.statusbar, text="Ready", padding=(5, 2))
        self.status_label.pack(side=tk.LEFT)

        self.size_label = ttk.Label(self.statusbar, text="", padding=(5, 2))
        self.size_label.pack(side=tk.RIGHT)

        self.format_label = ttk.Label(self.statusbar, text="", padding=(5, 2))
        self.format_label.pack(side=tk.RIGHT)

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Convert & Save As...", command=self.convert_image, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window, accelerator="Ctrl+0")
        view_menu.add_command(label="Actual Size (1:1)", command=self.actual_size, accelerator="Ctrl+1")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _bind_events(self):
        """Bind keyboard and mouse events."""
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.convert_image())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        self.root.bind('<Control-1>', lambda e: self.actual_size())

        # Mouse wheel zoom
        self.canvas.bind('<Control-MouseWheel>', self._on_mousewheel_zoom)

        # Drag and drop (Windows)
        self.root.drop_target_register = lambda *args: None  # Placeholder

        # Canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_resize)

    def _on_mousewheel_zoom(self, event):
        """Handle mouse wheel zoom with Ctrl."""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def _on_canvas_resize(self, event):
        """Handle canvas resize."""
        if self.current_image:
            # Update welcome text position if no image
            self.canvas.delete('welcome')

    def open_image(self, filepath=None):
        """Open an image file."""
        if filepath is None:
            filepath = filedialog.askopenfilename(
                title="Open Image",
                filetypes=self.SUPPORTED_FORMATS
            )

        if not filepath:
            return

        try:
            # Load image with Pillow
            self.current_image = Image.open(filepath)
            self.current_path = filepath
            self.original_size = self.current_image.size

            # Handle animated GIFs - just show first frame
            if hasattr(self.current_image, 'n_frames') and self.current_image.n_frames > 1:
                self.current_image.seek(0)

            # Convert to RGB if necessary (for display)
            if self.current_image.mode in ('RGBA', 'LA', 'P'):
                # Keep alpha for proper display
                self.current_image = self.current_image.convert('RGBA')
            elif self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')

            # Fit to window initially
            self.fit_to_window()

            # Update UI
            filename = os.path.basename(filepath)
            self.root.title(f"Image Viewer - {filename}")
            self.status_label.config(text=filepath)
            self.size_label.config(text=f"{self.original_size[0]} x {self.original_size[1]} px")

            # Get format
            fmt = self.current_image.format or os.path.splitext(filepath)[1].upper().replace('.', '')
            self.format_label.config(text=f"Format: {fmt}")

            # Clear welcome text
            self.canvas.delete('welcome')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")

    def _display_image(self):
        """Display the current image at the current zoom level."""
        if self.current_image is None:
            return

        # Calculate new size
        new_width = int(self.original_size[0] * self.zoom_level)
        new_height = int(self.original_size[1] * self.zoom_level)

        # Resize image
        resized = self.current_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        # Convert to PhotoImage
        self.display_image = ImageTk.PhotoImage(resized)

        # Clear canvas and display
        self.canvas.delete("all")

        # Center the image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x = max(new_width // 2, canvas_width // 2)
        y = max(new_height // 2, canvas_height // 2)

        self.canvas.create_image(x, y, anchor=tk.CENTER, image=self.display_image)

        # Update scroll region
        self.canvas.configure(scrollregion=(0, 0, max(new_width, canvas_width), max(new_height, canvas_height)))

        # Update zoom label
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def zoom_in(self):
        """Zoom in by 25%."""
        if self.current_image and self.zoom_level < 5.0:
            self.zoom_level = min(5.0, self.zoom_level * 1.25)
            self._display_image()

    def zoom_out(self):
        """Zoom out by 25%."""
        if self.current_image and self.zoom_level > 0.1:
            self.zoom_level = max(0.1, self.zoom_level / 1.25)
            self._display_image()

    def fit_to_window(self):
        """Fit image to window size."""
        if self.current_image is None:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate zoom to fit
        width_ratio = canvas_width / self.original_size[0]
        height_ratio = canvas_height / self.original_size[1]

        self.zoom_level = min(width_ratio, height_ratio, 1.0) * 0.95  # 95% to add margin
        self._display_image()

    def actual_size(self):
        """Display image at actual size (100%)."""
        if self.current_image:
            self.zoom_level = 1.0
            self._display_image()

    def convert_image(self):
        """Convert and save the current image to a different format."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded to convert.")
            return

        target_format = self.convert_var.get()
        extension = self.CONVERT_FORMATS[target_format]

        # Get original filename without extension
        if self.current_path:
            base_name = os.path.splitext(os.path.basename(self.current_path))[0]
        else:
            base_name = "converted_image"

        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            title="Save Converted Image",
            defaultextension=extension,
            initialfile=f"{base_name}{extension}",
            filetypes=[(target_format, f"*{extension}")]
        )

        if not save_path:
            return

        try:
            # Prepare image for saving
            img_to_save = self.current_image

            # Handle format-specific requirements
            if target_format == "JPEG":
                # JPEG doesn't support transparency
                if img_to_save.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img_to_save.size, (255, 255, 255))
                    if img_to_save.mode == 'P':
                        img_to_save = img_to_save.convert('RGBA')
                    background.paste(img_to_save, mask=img_to_save.split()[-1] if img_to_save.mode == 'RGBA' else None)
                    img_to_save = background
                elif img_to_save.mode != 'RGB':
                    img_to_save = img_to_save.convert('RGB')
                img_to_save.save(save_path, 'JPEG', quality=95)

            elif target_format == "PNG":
                img_to_save.save(save_path, 'PNG')

            elif target_format == "WebP":
                img_to_save.save(save_path, 'WebP', quality=95)

            elif target_format == "GIF":
                if img_to_save.mode != 'P':
                    img_to_save = img_to_save.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
                img_to_save.save(save_path, 'GIF')

            elif target_format == "BMP":
                if img_to_save.mode == 'RGBA':
                    background = Image.new('RGB', img_to_save.size, (255, 255, 255))
                    background.paste(img_to_save, mask=img_to_save.split()[-1])
                    img_to_save = background
                img_to_save.save(save_path, 'BMP')

            messagebox.showinfo("Success", f"Image saved as:\n{save_path}")
            self.status_label.config(text=f"Saved: {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image:\n{str(e)}")

    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Image Viewer",
            "Image Viewer v1.0\n\n"
            "A lightweight image viewer for Windows.\n\n"
            "Supported formats:\n"
            "JPG, JPEG, PNG, WebP, GIF\n\n"
            "Features:\n"
            "- View images with zoom\n"
            "- Convert between formats"
        )


def main():
    root = tk.Tk()

    # Set app icon (optional)
    try:
        root.iconbitmap(default='')
    except:
        pass

    app = ImageViewer(root)

    # Check if file was passed as argument
    import sys
    if len(sys.argv) > 1:
        app.open_image(sys.argv[1])

    root.mainloop()


if __name__ == "__main__":
    main()
