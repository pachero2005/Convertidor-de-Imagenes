import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import customtkinter as ctk

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# Configuración inicial
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ConvER Pro")
root.geometry("700x580")
root.resizable(False, False)

files = []
fmt = ctk.StringVar(value="JPG")
q = ctk.StringVar(value="95")
w = ctk.StringVar(value="900")
h = ctk.StringVar(value="630")

# --- INTERFAZ ---

# Frame superior
frame_top = ctk.CTkFrame(root)
frame_top.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

label_list_title = ctk.CTkLabel(frame_top, text="Archivos Seleccionados:", font=ctk.CTkFont(size=13, weight="bold"))
label_list_title.pack(anchor="w", padx=10, pady=(10, 5))

scroll_frame = ctk.CTkScrollableFrame(frame_top, width=640, height=180)
scroll_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

pb = ctk.CTkProgressBar(root, orientation="determinate", width=640)
pb.pack(pady=5)
pb.set(0)

# Frame de controles
frame_bot = ctk.CTkFrame(root, corner_radius=10)
frame_bot.pack(fill=tk.X, padx=15, pady=15)

# Botones de selección y conversión en la misma fila
btn_files = ctk.CTkButton(frame_bot, text="Seleccionar Archivos", command=lambda: load(False))
btn_files.grid(row=0, column=0, padx=10, pady=15)

btn_folder = ctk.CTkButton(frame_bot, text="Seleccionar Carpeta", command=lambda: load(True))
btn_folder.grid(row=0, column=1, padx=10, pady=15)

btn_convert = ctk.CTkButton(frame_bot, text="CONVERTIR", command=lambda: convert(), 
                            fg_color="green", hover_color="darkgreen", 
                            font=ctk.CTkFont(size=12, weight="bold"))
btn_convert.grid(row=0, column=2, padx=10, pady=15)

# Fila de configuración de formato
label_fmt = ctk.CTkLabel(frame_bot, text="Formato:")
label_fmt.grid(row=1, column=0, sticky="e", padx=10, pady=5)

combo_fmt = ctk.CTkComboBox(frame_bot, variable=fmt, values=["JPG", "PNG", "WEBP", "BMP", "TIFF"], state="readonly", width=140)
combo_fmt.grid(row=1, column=1, sticky="w", padx=10, pady=5)

# Fila de dimensiones predeterminadas
label_w = ctk.CTkLabel(frame_bot, text="Ancho (px):")
label_w.grid(row=2, column=0, sticky="e", padx=10, pady=5)
entry_w = ctk.CTkEntry(frame_bot, textvariable=w, width=140)
entry_w.grid(row=2, column=1, sticky="w", padx=10, pady=5)

label_h = ctk.CTkLabel(frame_bot, text="Alto (px):")
label_h.grid(row=2, column=2, sticky="e", padx=5, pady=5)
entry_h = ctk.CTkEntry(frame_bot, textvariable=h, width=140)
entry_h.grid(row=2, column=3, sticky="w", padx=10, pady=5)


# --- FUNCIONES ---
def update_file_list():
    for widget in scroll_frame.winfo_children():
        widget.destroy()
    
    if not files:
        lbl = ctk.CTkLabel(scroll_frame, text="No hay archivos seleccionados", text_color="gray")
        lbl.pack(pady=10)
    else:
        for f in files:
            lbl = ctk.CTkLabel(scroll_frame, text=f, anchor="w", font=ctk.CTkFont(size=11))
            lbl.pack(fill=tk.X, padx=5, pady=2)

def load(is_folder):
    global files
    if is_folder:
        d = filedialog.askdirectory()
        if not d: return
        ex = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp", ".heic"}
        files = [os.path.join(d, f) for f in os.listdir(d) if os.path.splitext(f)[1].lower() in ex]
    else:
        fs = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.gif *.webp *.heic")])
        files = list(fs)
    update_file_list()

def convert():
    out = filedialog.askdirectory()
    if not out: return
    
    target_w = int(w.get()) if w.get().isdigit() else None
    target_h = int(h.get()) if h.get().isdigit() else None
    
    total_files = len(files)
    if total_files == 0:
        messagebox.showwarning("Advertencia", "Selecciona al menos un archivo primero.")
        return

    pb.set(0)
    for i, f in enumerate(files):
        try:
            im = Image.open(f)
            if target_w or target_h:
                if target_w and target_h:
                    new_w, new_h = target_w, target_h
                elif target_w:
                    new_w = target_w
                    new_h = int(im.height * (target_w / im.width))
                else:
                    new_h = target_h
                    new_w = int(im.width * (target_h / im.height))
                im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            e = fmt.get().upper()
            dst = os.path.join(out, os.path.splitext(os.path.basename(f))[0] + "." + e.lower())
            
            if e in ("JPG", "JPEG"): 
                im.convert("RGB").save(dst, "JPEG", quality=int(q.get()))
            else: 
                im.save(dst, e)
        except Exception as x: 
            print(x)
            
        pb.set((i + 1) / total_files)
        root.update_idletasks()
        
    messagebox.showinfo("Listo", "Proceso terminado")
    pb.set(0)

root.mainloop()