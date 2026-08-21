"""
CyberSafe Toolkit v2.0
Main Application Entry Point
Professional Dark Theme - Responsive Design
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import sys
import sqlite3
import threading
import hashlib
import secrets
import string
import socket
import json
import shutil
import subprocess
import platform
import re
import ipaddress
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#0d1117",
    "bg_medium": "#161b22",
    "bg_light": "#1c2128",
    "border": "#21262d",
    "text_white": "#ffffff",
    "text_light": "#c9d1d9",
    "text_muted": "#8b949e",
    "accent_cyan": "#00d4ff",
    "accent_green": "#00ff88",
    "accent_gold": "#ffd700",
    "accent_red": "#ff4757",
    "accent_blue": "#54a0ff",
    "accent_purple": "#5f27cd",
    "accent_orange": "#ffa502",
    "hover_cyan": "#0099cc",
    "hover_green": "#00cc66",
    "hover_gold": "#cc9900",
    "hover_red": "#cc3333",
    "hover_blue": "#3a7bd5",
    "hover_purple": "#4a1a9e",
    "hover_orange": "#cc8400",
}

def get_app_data_dir():
    if platform.system() == "Windows":
        base_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "CyberSafeToolkit")
    else:
        base_dir = os.path.join(os.path.expanduser("~"), ".cybersafe_toolkit")
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "database"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "quarantine"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "reports"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    return base_dir

APP_DATA_DIR = get_app_data_dir()
DB_PATH = os.path.join(APP_DATA_DIR, "database", "cybersafe.db")
QUARANTINE_DIR = os.path.join(APP_DATA_DIR, "quarantine")
REPORTS_DIR = os.path.join(APP_DATA_DIR, "reports")
LOGS_DIR = os.path.join(APP_DATA_DIR, "logs")

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS security_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                target TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            );
            CREATE TABLE IF NOT EXISTS hash_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                file_name TEXT,
                sha256_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                scan_type TEXT,
                open_ports TEXT,
                services TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS quarantine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT,
                quarantined_path TEXT,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
    
    def add_record(self, operation, target, result, status="SUCCESS"):
        self.cursor.execute("INSERT INTO security_records (operation, target, result, status) VALUES (?, ?, ?, ?)", (operation, target, result, status))
        self.conn.commit()
    
    def save_hash(self, file_path, file_name, sha256_hash):
        self.cursor.execute("INSERT INTO hash_records (file_path, file_name, sha256_hash) VALUES (?, ?, ?)", (file_path, file_name, sha256_hash))
        self.conn.commit()
    
    def save_scan(self, target, scan_type, open_ports, services):
        self.cursor.execute("INSERT INTO scan_history (target, scan_type, open_ports, services) VALUES (?, ?, ?, ?)", (target, scan_type, json.dumps(open_ports), json.dumps(services)))
        self.conn.commit()
    
    def save_quarantine(self, original_path, quarantined_path, reason):
        self.cursor.execute("INSERT INTO quarantine (original_path, quarantined_path, reason) VALUES (?, ?, ?)", (original_path, quarantined_path, reason))
        self.conn.commit()
    
    def get_all_records(self):
        self.cursor.execute("SELECT * FROM security_records ORDER BY timestamp DESC")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

class LogoHandler:
    def __init__(self):
        self.logo_image = None
        self.logo_photo = None
        self.logo_header_photo = None
        self.logo_icon = None
        self.logo_path = None
        self.icon_path = None
        self.load_logo()
    
    def load_logo(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "assets/logo.png")
            icon_path = os.path.join(script_dir, "assets/icon.ico")
            
            if os.path.exists(logo_path):
                self.logo_path = logo_path
                self.logo_image = Image.open(logo_path).convert("RGBA")
                
                self.logo_small = self.logo_image.copy()
                self.logo_small.thumbnail((60, 60), Image.Resampling.LANCZOS)
                self.logo_photo = ctk.CTkImage(light_image=self.logo_small, dark_image=self.logo_small, size=(60, 60))
                
                self.logo_header = self.logo_image.copy()
                self.logo_header.thumbnail((90, 90), Image.Resampling.LANCZOS)
                self.logo_header_photo = ctk.CTkImage(light_image=self.logo_header, dark_image=self.logo_header, size=(90, 90))
                
                self.logo_icon = self.logo_image.copy()
                self.logo_icon.thumbnail((32, 32), Image.Resampling.LANCZOS)
            else:
                self.create_default_logo()
            
            if os.path.exists(icon_path):
                self.icon_path = icon_path
            else:
                self.icon_path = None
                
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.create_default_logo()
    
    def create_default_logo(self):
        try:
            img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.polygon([(100, 15), (175, 45), (175, 110), (100, 175), (25, 110), (25, 45)], fill='#161b22', outline='#00d4ff', width=4)
            draw.polygon([(100, 30), (160, 55), (160, 105), (100, 160), (40, 105), (40, 55)], fill='#0d1117', outline='#00ff88', width=2)
            draw.text((65, 80), "CS", fill='#00ff88')
            draw.rectangle([85, 95, 115, 130], fill='#ffd700', outline='#ffd700')
            draw.arc([90, 75, 110, 95], start=180, end=360, fill='#ffd700', width=3)
            
            self.logo_image = img
            self.logo_small = img.copy()
            self.logo_small.thumbnail((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ctk.CTkImage(light_image=self.logo_small, dark_image=self.logo_small, size=(60, 60))
            self.logo_header = img.copy()
            self.logo_header.thumbnail((40, 40), Image.Resampling.LANCZOS)
            self.logo_header_photo = ctk.CTkImage(light_image=self.logo_header, dark_image=self.logo_header, size=(40, 40))
            self.logo_icon = img.copy()
            self.logo_icon.thumbnail((32, 32), Image.Resampling.LANCZOS)
            self.icon_path = None
        except Exception as e:
            print(f"Error creating default logo: {e}")

def show_custom_messagebox(title, message, msg_type="info"):
    try:
        popup = ctk.CTkToplevel()
        popup.title(title)
        popup.geometry("420x280")
        popup.resizable(False, False)
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (420 // 2)
        y = (popup.winfo_screenheight() // 2) - (280 // 2)
        popup.geometry(f"420x280+{x}+{y}")
        popup.configure(fg_color=COLORS["bg_medium"])
        try:
            logo_handler = LogoHandler()
            if logo_handler.icon_path:
                popup.iconbitmap(logo_handler.icon_path)
            elif logo_handler.logo_icon:
                icon = ImageTk.PhotoImage(logo_handler.logo_icon)
                popup.iconphoto(False, icon)
                popup._icon = icon
        except Exception:
            pass
        content_frame = ctk.CTkFrame(popup, corner_radius=12, fg_color=COLORS["bg_light"])
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        accent_color = COLORS["accent_green"] if msg_type == "info" else COLORS["accent_red"]
        accent = ctk.CTkFrame(content_frame, height=3, fg_color=accent_color, corner_radius=0)
        accent.pack(fill="x", side="top")
        try:
            logo_handler = LogoHandler()
            if logo_handler.logo_photo:
                ctk.CTkLabel(content_frame, image=logo_handler.logo_photo, text="").pack(pady=15)
        except Exception:
            pass
        msg_label = ctk.CTkLabel(content_frame, text=message, font=ctk.CTkFont(size=14), text_color=COLORS["text_light"], wraplength=350, justify="center")
        msg_label.pack(pady=10, padx=20)
        def close_popup():
            popup.destroy()
        btn_color = COLORS["accent_green"] if msg_type == "info" else COLORS["accent_red"]
        hover_color = COLORS["hover_green"] if msg_type == "info" else COLORS["hover_red"]
        ctk.CTkButton(content_frame, text="OK", command=close_popup, height=35, width=100, fg_color=btn_color, hover_color=hover_color, font=ctk.CTkFont(size=13, weight="bold")).pack(pady=15)
        popup.grab_set()
        popup.after(100, popup.lift)
        popup.focus_force()
        return popup
    except Exception:
        if msg_type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
        return None

class CyberSafeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CyberSafe Toolkit v2.0")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        min_width = int(screen_width * 0.5)
        min_height = int(screen_height * 0.5)
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(min_width, min_height)
        self.update_idletasks()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.set_window_icon()
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.configure(fg_color=COLORS["bg_dark"])
        self.bind("<Configure>", self.on_window_resize)
        self.db = Database()
        self.logo_handler = LogoHandler()
        self.current_hash = ""
        self.current_open_ports = []
        self.current_symmetric_file = None
        self.current_hash_file = None
        self.current_rsa_file = None
        self.current_quarantine_file = None
        self.rsa_public_key = None
        self.rsa_private_key = None
        self.stop_scan_flag = False
        self.build_sidebar()
        self.build_main_area()
        self.build_status_bar()
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.show_dashboard()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_window_resize(self, event):
        if event.widget == self:
            width = event.width
            if width < 1100:
                new_sidebar_width = 200
            elif width < 1400:
                new_sidebar_width = 220
            else:
                new_sidebar_width = 240
            if hasattr(self, 'sidebar'):
                self.sidebar.configure(width=new_sidebar_width)
    
    def set_window_icon(self):
        try:
            self.logo_handler = LogoHandler()
            if self.logo_handler.icon_path and os.path.exists(self.logo_handler.icon_path):
                try:
                    self.iconbitmap(self.logo_handler.icon_path)
                except Exception:
                    pass
            if self.logo_handler.logo_icon:
                icon = ImageTk.PhotoImage(self.logo_handler.logo_icon)
                self.iconphoto(True, icon)
                self._icon = icon
        except Exception:
            pass
    
    def on_closing(self):
        self.db.close()
        self.destroy()
    
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["bg_dark"])
        self.sidebar.grid_propagate(False)
        accent_frame = ctk.CTkFrame(self.sidebar, height=3, fg_color=COLORS["accent_cyan"], corner_radius=0)
        accent_frame.pack(fill="x", side="top")
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=20, padx=15, fill="x")
        if self.logo_handler.logo_photo:
            logo_label = ctk.CTkLabel(logo_frame, image=self.logo_handler.logo_photo, text="")
            logo_label.pack(side="left", padx=(0, 10))
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_frame, text="CyberSafe", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Toolkit v2.0", font=ctk.CTkFont(size=12), text_color=COLORS["accent_cyan"]).pack(anchor="w")
        separator = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"])
        separator.pack(fill="x", padx=15, pady=10)
        
        nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0, scrollbar_button_color=COLORS["accent_cyan"], scrollbar_button_hover_color=COLORS["hover_cyan"])
        nav_scroll.pack(fill="both", expand=True, pady=5)
        
        nav_items = [
            ("📊", "Dashboard", self.show_dashboard),
            ("🔐", "Symmetric Encryption", self.show_symmetric_encryption),
            ("🔑", "Asymmetric Encryption", self.show_asymmetric_encryption),
            ("🔒", "Hash & Integrity", self.show_hashing),
            ("📝", "Password Generator", self.show_password_gen),
            ("💪", "Strength Analyzer", self.show_strength),
            ("🌐", "Port Scanner", self.show_port_scanner),
            ("🔍", "Network Discovery", self.show_network_discovery),
            ("🚫", "Quarantine", self.show_quarantine),
            ("📄", "Security Report", self.show_report),
            ("📊", "History", self.show_history),
        ]
        
        for emoji, text, command in nav_items:
            btn_frame = ctk.CTkFrame(nav_scroll, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(btn_frame, text=emoji, font=ctk.CTkFont(size=18), width=30).pack(side="left", padx=(5, 0))
            btn = ctk.CTkButton(btn_frame, text=text, command=command, height=38, corner_radius=8, anchor="w", fg_color="transparent", hover_color=COLORS["bg_light"], text_color=COLORS["text_light"], font=ctk.CTkFont(size=13))
            btn.pack(side="left", fill="x", expand=True)
        
        team_separator = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"])
        team_separator.pack(fill="x", padx=15, pady=5)
        team_btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        team_btn_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(team_btn_frame, text="👨‍💻", font=ctk.CTkFont(size=18), width=30).pack(side="left", padx=(5, 0))
        team_btn = ctk.CTkButton(team_btn_frame, text="CyberSafe Team", command=self.show_team, height=38, corner_radius=8, anchor="w", fg_color="transparent", hover_color=COLORS["hover_blue"], text_color=COLORS["text_light"], font=ctk.CTkFont(size=13))
        team_btn.pack(side="left", fill="x", expand=True)
        
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        ctk.CTkLabel(bottom_frame, text="Version 2.0.0", font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 10))
        exit_btn = ctk.CTkButton(bottom_frame, text="🚪  Exit Application", command=self.on_closing, height=40, corner_radius=8, fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"], text_color=COLORS["text_white"], font=ctk.CTkFont(size=13, weight="bold"))
        exit_btn.pack(fill="x")
    
    def build_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_medium"])
    
    def build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color=COLORS["bg_dark"])
        status_left = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_left.pack(side="left", padx=15)
        self.status_dot = ctk.CTkLabel(status_left, text="●", font=ctk.CTkFont(size=12), text_color=COLORS["accent_green"])
        self.status_dot.pack(side="left", padx=(0, 5))
        self.status_label = ctk.CTkLabel(status_left, text="Ready", font=ctk.CTkFont(size=12), text_color=COLORS["text_light"])
        self.status_label.pack(side="left")
        time_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        time_frame.pack(side="right", padx=15)
        ctk.CTkLabel(time_frame, text="🕐", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
        self.time_label = ctk.CTkLabel(time_frame, text="", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.time_label.pack(side="left")
        self.update_time()
    
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.after(1000, self.update_time)
    
    def set_status(self, text):
        self.status_label.configure(text=text)
    
    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def add_header(self, title_text, subtitle=None):
        header_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        header_frame.pack(fill="x", padx=25, pady=25)
        accent = ctk.CTkFrame(header_frame, width=4, fg_color=COLORS["accent_cyan"], corner_radius=0)
        accent.pack(side="left", fill="y", padx=(0, 15))
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        if hasattr(self.logo_handler, 'logo_header_photo'):
            ctk.CTkLabel(content_frame, image=self.logo_handler.logo_header_photo, text="").pack(side="left", padx=(0, 15))
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left")
        ctk.CTkLabel(text_frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(text_frame, text=subtitle, font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"]).pack(anchor="w")
        return header_frame
    
    def show_team(self):
        self.clear_main()
        self.set_status("CyberSafe Team")
        self.add_header("👨‍💻 CyberSafe Team", "Meet the developers behind this project")
        
        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", corner_radius=0, scrollbar_button_color=COLORS["accent_blue"], scrollbar_button_hover_color=COLORS["hover_blue"])
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        team_members = [
            {
                "emoji": "👨‍💻",
                "name": "Diaa Maher",
                "role": "Lead Developer",
                "description": "Responsible for overall architecture and core functionality",
                "skills": ["Python", "Cybersecurity", "Cryptography", "Networking"],
                "color": COLORS["accent_cyan"],
            },
            {
                "emoji": "👨‍💻",
                "name": "Eslam Mahmoud",
                "role": "Security Analyst",
                "description": "Specializes in vulnerability assessment and security testing",
                "skills": ["Penetration Testing", "Risk Assessment", "Security Auditing"],
                "color": COLORS["accent_green"],
            },
            {
                "emoji": "👩‍💻",
                "name": "Doaa Ahmed",
                "role": "UI/UX Designer",
                "description": "Focuses on user experience and interface design",
                "skills": ["UI Design", "UX Research", "Prototyping", "CSS"],
                "color": COLORS["accent_gold"],
            },
            {
                "emoji": "🧑‍💻",
                "name": "Saeed Tarek",
                "role": "Malware Analyst",
                "description": "Specializes in malware analysis and reverse engineering",
                "skills": ["Reverse Engineering", "Malware Analysis", "Assembly", "IDA Pro", "OllyDbg"],
                "color": COLORS["accent_purple"],
            },
        ]
        
        for member in team_members:
            member_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
            member_frame.pack(fill="x", pady=10)
            accent = ctk.CTkFrame(member_frame, width=4, fg_color=member["color"], corner_radius=0)
            accent.pack(side="left", fill="y", padx=(0, 15))
            content_frame = ctk.CTkFrame(member_frame, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(header_frame, text=member["emoji"], font=ctk.CTkFont(size=40)).pack(side="left", padx=(0, 15))
            name_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            name_frame.pack(side="left")
            ctk.CTkLabel(name_frame, text=member["name"], font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w")
            ctk.CTkLabel(name_frame, text=member["role"], font=ctk.CTkFont(size=14), text_color=member["color"]).pack(anchor="w")
            ctk.CTkLabel(content_frame, text=member["description"], font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"], wraplength=600, justify="left").pack(anchor="w", pady=(10, 5))
            ctk.CTkLabel(content_frame, text="Skills:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_light"]).pack(anchor="w", pady=(5, 5))
            skills_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            skills_frame.pack(fill="x", pady=5)
            for skill in member["skills"]:
                skill_btn = ctk.CTkButton(skills_frame, text=skill, height=30, corner_radius=15, fg_color=COLORS["bg_medium"], hover_color=member["color"], text_color=COLORS["text_light"], font=ctk.CTkFont(size=11), border_width=1, border_color=member["color"], state="disabled")
                skill_btn.pack(side="left", padx=3, pady=2)
        
        info_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        info_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(info_frame, text="📋 Project Information", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 10))
        info_items = [
            ("📌", "Project Name", "CyberSafe Toolkit v2.0"),
            ("🎯", "Purpose", "Cybersecurity Education & Practical Tools"),
            ("🏫", "Academic Field", "Cybersecurity / CyberOps"),
            ("📅", "Version", "2.0.0"),
        ]
        for emoji, label, value in info_items:
            info_row = ctk.CTkFrame(info_frame, fg_color="transparent")
            info_row.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(info_row, text=emoji, font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(info_row, text=f"{label}:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_muted"], width=150).pack(side="left")
            ctk.CTkLabel(info_row, text=value, font=ctk.CTkFont(size=13), text_color=COLORS["text_light"]).pack(side="left")
    
    # ------------------------------ Dashboard ------------------------------ #
    def show_dashboard(self):
        self.clear_main()
        self.set_status("Dashboard")
        self.add_header("Welcome to CyberSafe Toolkit", "Your comprehensive cybersecurity companion")
        
        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", corner_radius=0, scrollbar_button_color=COLORS["accent_cyan"], scrollbar_button_hover_color=COLORS["hover_cyan"])
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        stats_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        self.db.cursor.execute("SELECT COUNT(*) FROM security_records")
        total_operations = self.db.cursor.fetchone()[0]
        self.db.cursor.execute("SELECT COUNT(*) FROM quarantine")
        quarantine_count = self.db.cursor.fetchone()[0]
        stats = [
            ("📊", "Total Operations", str(total_operations), COLORS["accent_cyan"]),
            ("🚫", "Quarantined Files", str(quarantine_count), COLORS["accent_red"]),
            ("🌐", "Open Ports Found", str(len(self.current_open_ports)), COLORS["accent_green"]),
        ]
        for emoji, label, value, color in stats:
            stat_frame = ctk.CTkFrame(stats_frame, corner_radius=12, fg_color=COLORS["bg_light"])
            stat_frame.pack(side="left", padx=5, pady=5, expand=True, fill="both")
            ctk.CTkLabel(stat_frame, text=emoji, font=ctk.CTkFont(size=30)).pack(pady=(15, 5))
            ctk.CTkLabel(stat_frame, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack(pady=5)
            ctk.CTkLabel(stat_frame, text=label, font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"]).pack(pady=(0, 15))
        
        actions_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        actions_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(actions_frame, text="⚡ Quick Actions", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 10))
        quick_scroll = ctk.CTkScrollableFrame(actions_frame, fg_color="transparent", height=65, orientation="horizontal", scrollbar_button_color=COLORS["accent_orange"], scrollbar_button_hover_color=COLORS["hover_orange"])
        quick_scroll.pack(fill="x", padx=10, pady=(0, 15))
        quick_actions = [
            ("🔒", "Encrypt File", self.show_symmetric_encryption, COLORS["accent_green"], COLORS["hover_green"]),
            ("📝", "Generate Password", self.show_password_gen, COLORS["accent_cyan"], COLORS["hover_cyan"]),
            ("🌐", "Scan Network", self.show_port_scanner, COLORS["accent_blue"], COLORS["hover_blue"]),
            ("📄", "Generate Report", self.show_report, COLORS["accent_orange"], COLORS["hover_orange"]),
            ("🔑", "RSA Keys", self.show_asymmetric_encryption, COLORS["accent_gold"], COLORS["hover_gold"]),
            ("🔒", "Hash File", self.show_hashing, COLORS["accent_purple"], COLORS["hover_purple"]),
        ]
        for emoji, text, command, color, hover_color in quick_actions:
            btn = ctk.CTkButton(quick_scroll, text=f"{emoji}  {text}", command=command, height=40, width=180, corner_radius=10, fg_color=COLORS["bg_medium"], hover_color=hover_color, text_color=COLORS["text_light"], font=ctk.CTkFont(size=13), border_width=1, border_color=COLORS["border"])
            btn.pack(side="left", padx=5, pady=5)
        
        tips_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        tips_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(tips_frame, text="🔒 Security Tips", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 10))
        tips = [
            "• Always use strong passwords with at least 12 characters",
            "• Enable two-factor authentication when available",
            "• Keep your encryption keys in a safe place",
            "• Only scan networks you own or have permission to test",
            "• Regularly verify file integrity with SHA-256 hashes",
        ]
        for tip in tips:
            ctk.CTkLabel(tips_frame, text=tip, font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"], anchor="w").pack(anchor="w", padx=20, pady=3)
    
    # ------------------------------ Symmetric Encryption ------------------------------ #
    def show_symmetric_encryption(self):
        self.clear_main()
        self.set_status("Symmetric Encryption")
        self.add_header("Symmetric Encryption", "Encrypt and decrypt files using AES-GCM or Fernet")
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        method_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        method_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(method_frame, text="Encryption Method:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        method_options = ctk.CTkFrame(method_frame, fg_color="transparent")
        method_options.pack(fill="x", padx=15, pady=(0, 15))
        self.encryption_method = ctk.StringVar(value="AES-GCM")
        for method in ["AES-GCM", "Fernet"]:
            ctk.CTkRadioButton(method_options, text=method, variable=self.encryption_method, value=method, text_color=COLORS["text_light"]).pack(side="left", padx=10, pady=5)
        
        key_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        key_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(key_frame, text="Encryption Key:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.symmetric_key_entry = ctk.CTkEntry(key_frame, height=40, placeholder_text="Enter or generate a key", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.symmetric_key_entry.pack(fill="x", padx=15, pady=5)
        key_buttons = ctk.CTkFrame(key_frame, fg_color="transparent")
        key_buttons.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(key_buttons, text="Generate Key", command=self.generate_symmetric_key, width=150, fg_color=COLORS["accent_cyan"], hover_color=COLORS["hover_cyan"]).pack(side="left", padx=5)
        ctk.CTkButton(key_buttons, text="Save Key", command=lambda: self.save_encryption_key("symmetric"), width=150, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"]).pack(side="left", padx=5)
        ctk.CTkButton(key_buttons, text="Load Key", command=lambda: self.load_encryption_key("symmetric"), width=150, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"]).pack(side="left", padx=5)
        
        file_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        file_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(file_frame, text="Selected File:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.symmetric_file_label = ctk.CTkLabel(file_frame, text="No file selected", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.symmetric_file_label.pack(anchor="w", padx=15, pady=5)
        ctk.CTkButton(file_frame, text="Select File", command=self.select_symmetric_file, width=150, fg_color=COLORS["accent_purple"], hover_color=COLORS["hover_purple"]).pack(anchor="w", padx=15, pady=(5, 15))
        
        action_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        action_frame.pack(fill="x", pady=5)
        ctk.CTkButton(action_frame, text="🔒 Encrypt File", command=self.encrypt_file_symmetric, height=45, width=200, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"], font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)
        ctk.CTkButton(action_frame, text="🔓 Decrypt File", command=self.decrypt_file_symmetric, height=45, width=200, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"], font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)
        self.symmetric_status = ctk.CTkLabel(main_container, text="", font=ctk.CTkFont(size=13), text_color=COLORS["accent_green"])
        self.symmetric_status.pack(pady=10)
    
    def generate_symmetric_key(self):
        method = self.encryption_method.get()
        if method == "Fernet":
            key = Fernet.generate_key().decode()
        else:
            key = secrets.token_hex(32)
        self.symmetric_key_entry.delete(0, "end")
        self.symmetric_key_entry.insert(0, key)
        show_custom_messagebox("Key Generated", "Keep this key safe. You will need it for decryption.")
        self.set_status("Encryption key generated")
    
    def save_encryption_key(self, key_type):
        key = self.symmetric_key_entry.get().strip()
        if not key:
            show_custom_messagebox("Error", "No key to save.", "error")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".key", filetypes=[("Key files", "*.key"), ("All files", "*.*")], initialfile=f"{key_type}_key.key")
        if not filepath:
            return
        try:
            with open(filepath, "w") as f:
                f.write(key)
            self.db.add_record("Save Key", filepath, "Key saved")
            show_custom_messagebox("Success", f"Key saved to:\n{filepath}")
            self.set_status("Key saved")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def load_encryption_key(self, key_type):
        filepath = filedialog.askopenfilename(title="Select key file", filetypes=[("Key files", "*.key"), ("All files", "*.*")])
        if not filepath:
            return
        try:
            with open(filepath, "r") as f:
                key = f.read().strip()
            self.symmetric_key_entry.delete(0, "end")
            self.symmetric_key_entry.insert(0, key)
            self.db.add_record("Load Key", filepath, "Key loaded")
            self.set_status("Key loaded")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def select_symmetric_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.current_symmetric_file = filepath
            self.symmetric_file_label.configure(text=os.path.basename(filepath))
            self.set_status(f"Selected: {os.path.basename(filepath)}")
    
    def encrypt_file_symmetric(self):
        if not self.current_symmetric_file:
            show_custom_messagebox("Error", "Please select a file to encrypt.", "error")
            return
        key = self.symmetric_key_entry.get().strip()
        if not key:
            show_custom_messagebox("Error", "Please enter or generate an encryption key.", "error")
            return
        method = self.encryption_method.get()
        filepath = self.current_symmetric_file
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            if method == "Fernet":
                fernet = Fernet(key.encode())
                encrypted = fernet.encrypt(data)
            else:
                nonce = secrets.token_bytes(12)
                key_bytes = key.encode()[:32] if len(key) >= 32 else key.encode().ljust(32, b'\0')
                cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(nonce), backend=default_backend())
                encryptor = cipher.encryptor()
                encrypted = encryptor.update(data) + encryptor.finalize()
                encrypted = nonce + encryptor.tag + encrypted
            out_path = filepath + ".encrypted"
            with open(out_path, "wb") as f:
                f.write(encrypted)
            self.db.add_record("Symmetric Encryption", filepath, f"Encrypted using {method}")
            self.symmetric_status.configure(text=f"✅ File encrypted successfully!\nSaved as: {out_path}", text_color=COLORS["accent_green"])
            self.set_status("File encrypted")
            show_custom_messagebox("Success", f"File encrypted!\n\nMethod: {method}\nOutput: {out_path}")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
            self.set_status("Encryption failed")
    
    def decrypt_file_symmetric(self):
        filepath = filedialog.askopenfilename(title="Select encrypted file", filetypes=[("Encrypted files", "*.encrypted"), ("All files", "*.*")])
        if not filepath:
            return
        key = self.symmetric_key_entry.get().strip()
        if not key:
            show_custom_messagebox("Error", "Please enter the encryption key.", "error")
            return
        method = self.encryption_method.get()
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            if method == "Fernet":
                fernet = Fernet(key.encode())
                decrypted = fernet.decrypt(data)
            else:
                nonce = data[:12]
                tag = data[12:28]
                ciphertext = data[28:]
                key_bytes = key.encode()[:32] if len(key) >= 32 else key.encode().ljust(32, b'\0')
                cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(nonce, tag), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            out_path = filepath
            if out_path.endswith(".encrypted"):
                out_path = out_path[:-10]
            else:
                out_path = filepath + ".decrypted"
            if os.path.exists(out_path):
                base, ext = os.path.splitext(out_path)
                out_path = f"{base}_restored{ext}"
            with open(out_path, "wb") as f:
                f.write(decrypted)
            self.db.add_record("Symmetric Decryption", filepath, f"Decrypted using {method}")
            self.symmetric_status.configure(text=f"✅ File decrypted successfully!\nSaved as: {out_path}", text_color=COLORS["accent_green"])
            self.set_status("File decrypted")
            show_custom_messagebox("Success", f"File decrypted!\n\nMethod: {method}\nOutput: {out_path}")
        except Exception:
            show_custom_messagebox("Error", "Unable to decrypt file. The key may be invalid.", "error")
            self.set_status("Decryption failed")
    
    # ------------------------------ Asymmetric Encryption ------------------------------ #
    def show_asymmetric_encryption(self):
        self.clear_main()
        self.set_status("Asymmetric Encryption")
        self.add_header("Asymmetric Encryption (RSA)", "Encrypt and decrypt using RSA public/private keys")
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        gen_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        gen_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(gen_frame, text="RSA Key Pair", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkButton(gen_frame, text="Generate Key Pair", command=self.generate_rsa_keypair, height=35, width=200, fg_color=COLORS["accent_gold"], hover_color=COLORS["hover_gold"], text_color="#000000", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(5, 15))
        
        keys_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        keys_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(keys_frame, text="Public Key:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=5)
        self.public_key_text = ctk.CTkTextbox(keys_frame, height=80, wrap="word", state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.public_key_text.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(keys_frame, text="Private Key:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=5)
        self.private_key_text = ctk.CTkTextbox(keys_frame, height=80, wrap="word", state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.private_key_text.pack(fill="x", padx=15, pady=5)
        key_ops = ctk.CTkFrame(keys_frame, fg_color="transparent")
        key_ops.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(key_ops, text="Save Keys", command=self.save_rsa_keys, width=150, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"]).pack(side="left", padx=5)
        ctk.CTkButton(key_ops, text="Load Keys", command=self.load_rsa_keys, width=150, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"]).pack(side="left", padx=5)
        
        file_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        file_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(file_frame, text="File Operations", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.rsa_file_label = ctk.CTkLabel(file_frame, text="No file selected", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.rsa_file_label.pack(anchor="w", padx=15, pady=5)
        file_buttons = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_buttons.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(file_buttons, text="Select File", command=self.select_rsa_file, width=150, fg_color=COLORS["accent_purple"], hover_color=COLORS["hover_purple"]).pack(side="left", padx=5)
        ctk.CTkButton(file_buttons, text="Encrypt with Public Key", command=lambda: self.rsa_encrypt_file("public"), width=200, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"]).pack(side="left", padx=5)
        ctk.CTkButton(file_buttons, text="Decrypt with Private Key", command=lambda: self.rsa_decrypt_file("private"), width=200, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"]).pack(side="left", padx=5)
        self.rsa_status = ctk.CTkLabel(main_container, text="", font=ctk.CTkFont(size=13), text_color=COLORS["accent_green"])
        self.rsa_status.pack(pady=10)
    
    def generate_rsa_keypair(self):
        try:
            self.rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            self.rsa_public_key = self.rsa_private_key.public_key()
            private_pem = self.rsa_private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode()
            public_pem = self.rsa_public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()
            self.public_key_text.configure(state="normal")
            self.public_key_text.delete("1.0", "end")
            self.public_key_text.insert("1.0", public_pem)
            self.public_key_text.configure(state="disabled")
            self.private_key_text.configure(state="normal")
            self.private_key_text.delete("1.0", "end")
            self.private_key_text.insert("1.0", private_pem)
            self.private_key_text.configure(state="disabled")
            self.db.add_record("RSA Key Generation", "RSA-2048", "Key pair generated")
            self.set_status("RSA key pair generated")
            show_custom_messagebox("Success", "RSA key pair generated successfully!")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def save_rsa_keys(self):
        if not self.rsa_private_key or not self.rsa_public_key:
            show_custom_messagebox("Error", "Generate key pair first.", "error")
            return
        private_path = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files", "*.pem"), ("All files", "*.*")], initialfile="private_key.pem")
        if private_path:
            try:
                private_pem = self.rsa_private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())
                with open(private_path, "wb") as f:
                    f.write(private_pem)
                self.db.add_record("Save RSA Key", private_path, "Private key saved")
            except Exception as e:
                show_custom_messagebox("Error", f"Failed to save private key: {e}", "error")
        public_path = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files", "*.pem"), ("All files", "*.*")], initialfile="public_key.pem")
        if public_path:
            try:
                public_pem = self.rsa_public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
                with open(public_path, "wb") as f:
                    f.write(public_pem)
                self.db.add_record("Save RSA Key", public_path, "Public key saved")
                show_custom_messagebox("Success", "Keys saved successfully!")
            except Exception as e:
                show_custom_messagebox("Error", f"Failed to save public key: {e}", "error")
    
    def load_rsa_keys(self):
        private_path = filedialog.askopenfilename(title="Select private key", filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if private_path:
            try:
                with open(private_path, "rb") as f:
                    self.rsa_private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
                self.rsa_public_key = self.rsa_private_key.public_key()
                private_pem = self.rsa_private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode()
                self.private_key_text.configure(state="normal")
                self.private_key_text.delete("1.0", "end")
                self.private_key_text.insert("1.0", private_pem)
                self.private_key_text.configure(state="disabled")
                self.db.add_record("Load RSA Key", private_path, "Private key loaded")
            except Exception as e:
                show_custom_messagebox("Error", f"Failed to load private key: {e}", "error")
    
    def select_rsa_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.current_rsa_file = filepath
            self.rsa_file_label.configure(text=os.path.basename(filepath))
    
    def rsa_encrypt_file(self, key_type):
        if not self.current_rsa_file:
            show_custom_messagebox("Error", "Please select a file.", "error")
            return
        if not self.rsa_public_key:
            show_custom_messagebox("Error", "Generate or load RSA key pair first.", "error")
            return
        try:
            with open(self.current_rsa_file, "rb") as f:
                data = f.read()
            aes_key = secrets.token_bytes(32)
            nonce = secrets.token_bytes(12)
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            encrypted_key = self.rsa_public_key.encrypt(aes_key, asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
            encrypted = len(encrypted_key).to_bytes(4, 'big') + encrypted_key + nonce + encryptor.tag + encrypted_data
            out_path = self.current_rsa_file + ".rsa_encrypted"
            with open(out_path, "wb") as f:
                f.write(encrypted)
            self.db.add_record("RSA Encryption", self.current_rsa_file, f"Encrypted -> {out_path}")
            self.rsa_status.configure(text=f"✅ File encrypted with RSA!\nSaved as: {out_path}", text_color=COLORS["accent_green"])
            self.set_status("RSA encryption complete")
            show_custom_messagebox("Success", f"File encrypted!\nOutput: {out_path}")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def rsa_decrypt_file(self, key_type):
        filepath = filedialog.askopenfilename(title="Select RSA encrypted file", filetypes=[("RSA encrypted files", "*.rsa_encrypted"), ("All files", "*.*")])
        if not filepath:
            return
        if not self.rsa_private_key:
            show_custom_messagebox("Error", "Generate or load RSA key pair first.", "error")
            return
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            key_length = int.from_bytes(data[:4], 'big')
            encrypted_key = data[4:4+key_length]
            nonce = data[4+key_length:4+key_length+12]
            tag = data[4+key_length+12:4+key_length+28]
            encrypted_data = data[4+key_length+28:]
            aes_key = self.rsa_private_key.decrypt(encrypted_key, asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            out_path = filepath
            if out_path.endswith(".rsa_encrypted"):
                out_path = out_path[:-14]
            else:
                out_path = filepath + ".decrypted"
            if os.path.exists(out_path):
                base, ext = os.path.splitext(out_path)
                out_path = f"{base}_restored{ext}"
            with open(out_path, "wb") as f:
                f.write(decrypted)
            self.db.add_record("RSA Decryption", filepath, f"Decrypted -> {out_path}")
            self.rsa_status.configure(text=f"✅ File decrypted with RSA!\nSaved as: {out_path}", text_color=COLORS["accent_green"])
            self.set_status("RSA decryption complete")
            show_custom_messagebox("Success", f"File decrypted!\nOutput: {out_path}")
        except Exception:
            show_custom_messagebox("Error", "Unable to decrypt file. Check your private key.", "error")
            self.set_status("RSA decryption failed")
    
    # ------------------------------ Hashing & Integrity ------------------------------ #
    def show_hashing(self):
        self.clear_main()
        self.set_status("Hash & Integrity")
        self.add_header("File Hash & Integrity Checker", "Calculate and verify SHA-256 hashes")
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        algo_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        algo_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(algo_frame, text="Hash Algorithm:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        algo_options = ctk.CTkFrame(algo_frame, fg_color="transparent")
        algo_options.pack(fill="x", padx=15, pady=(0, 15))
        self.hash_algo = ctk.StringVar(value="SHA-256")
        for algo in ["SHA-256", "SHA-512", "MD5", "SHA-1"]:
            ctk.CTkRadioButton(algo_options, text=algo, variable=self.hash_algo, value=algo, text_color=COLORS["text_light"]).pack(side="left", padx=10, pady=5)
        
        file_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        file_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(file_frame, text="Selected File:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.hash_file_label = ctk.CTkLabel(file_frame, text="No file selected", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.hash_file_label.pack(anchor="w", padx=15, pady=5)
        ctk.CTkButton(file_frame, text="Select File", command=self.select_hash_file, width=150, fg_color=COLORS["accent_purple"], hover_color=COLORS["hover_purple"]).pack(anchor="w", padx=15, pady=(5, 15))
        
        calc_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        calc_frame.pack(fill="x", pady=5)
        ctk.CTkButton(calc_frame, text="Calculate Hash", command=self.calculate_hash, height=35, width=200, fg_color=COLORS["accent_cyan"], hover_color=COLORS["hover_cyan"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.hash_output = ctk.CTkEntry(calc_frame, height=40, placeholder_text="Hash will appear here", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.hash_output.pack(fill="x", padx=15, pady=(5, 15))
        
        integrity_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        integrity_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(integrity_frame, text="Integrity Verification", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 10))
        ctk.CTkLabel(integrity_frame, text="Expected Hash:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=5)
        self.expected_hash_entry = ctk.CTkEntry(integrity_frame, height=40, placeholder_text="Paste original hash here", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.expected_hash_entry.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(integrity_frame, text="Check Integrity", command=self.check_integrity, height=35, width=200, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"]).pack(anchor="w", padx=15, pady=(10, 15))
        self.integrity_status = ctk.CTkLabel(main_container, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.integrity_status.pack(pady=10)
    
    def select_hash_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.current_hash_file = filepath
            self.hash_file_label.configure(text=os.path.basename(filepath))
            self.set_status(f"Selected: {os.path.basename(filepath)}")
    
    def calculate_hash(self):
        if not self.current_hash_file:
            show_custom_messagebox("Error", "Please select a file.", "error")
            return
        algo = self.hash_algo.get()
        hash_func = getattr(hashlib, algo.lower().replace("-", ""), None)
        if not hash_func:
            show_custom_messagebox("Error", f"Unsupported algorithm: {algo}", "error")
            return
        h = hash_func()
        try:
            with open(self.current_hash_file, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            digest = h.hexdigest()
            self.current_hash = digest
            self.hash_output.delete(0, "end")
            self.hash_output.insert(0, digest)
            self.db.save_hash(self.current_hash_file, os.path.basename(self.current_hash_file), digest)
            self.db.add_record(f"{algo} Hash", self.current_hash_file, digest)
            self.set_status(f"{algo} calculated")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def check_integrity(self):
        if not self.current_hash:
            show_custom_messagebox("Error", "Please calculate a hash first.", "error")
            return
        expected = self.expected_hash_entry.get().strip()
        if not expected:
            show_custom_messagebox("Error", "Please enter an expected hash.", "error")
            return
        if expected.lower() == self.current_hash.lower():
            self.integrity_status.configure(text="✅ File UNCHANGED - Integrity verified", text_color=COLORS["accent_green"])
            status = "UNCHANGED"
        else:
            self.integrity_status.configure(text="⚠️ File MODIFIED - Integrity check failed", text_color=COLORS["accent_red"])
            status = "MODIFIED"
        self.db.add_record("Integrity Check", self.current_hash_file, status)
        self.set_status(f"Integrity: {status}")
    
    # ------------------------------ Password Generator ------------------------------ #
    def show_password_gen(self):
        self.clear_main()
        self.set_status("Password Generator")
        self.add_header("Secure Password Generator", "Generate cryptographically secure passwords")
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        settings_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        settings_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(settings_frame, text="Password Length:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.password_length = ctk.CTkEntry(settings_frame, height=35, width=100, fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.password_length.insert(0, "16")
        self.password_length.pack(anchor="w", padx=15, pady=5)
        options_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=15, pady=(5, 15))
        self.pw_upper = ctk.BooleanVar(value=True)
        self.pw_lower = ctk.BooleanVar(value=True)
        self.pw_digits = ctk.BooleanVar(value=True)
        self.pw_symbols = ctk.BooleanVar(value=True)
        self.pw_exclude_ambiguous = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="Uppercase (A-Z)", variable=self.pw_upper, text_color=COLORS["text_light"]).pack(anchor="w", padx=5, pady=2)
        ctk.CTkCheckBox(options_frame, text="Lowercase (a-z)", variable=self.pw_lower, text_color=COLORS["text_light"]).pack(anchor="w", padx=5, pady=2)
        ctk.CTkCheckBox(options_frame, text="Numbers (0-9)", variable=self.pw_digits, text_color=COLORS["text_light"]).pack(anchor="w", padx=5, pady=2)
        ctk.CTkCheckBox(options_frame, text="Special characters (!@#$...)", variable=self.pw_symbols, text_color=COLORS["text_light"]).pack(anchor="w", padx=5, pady=2)
        ctk.CTkCheckBox(options_frame, text="Exclude ambiguous characters", variable=self.pw_exclude_ambiguous, text_color=COLORS["text_light"]).pack(anchor="w", padx=5, pady=2)
        
        ctk.CTkButton(main_container, text="Generate Password", command=self.generate_password, height=40, width=200, fg_color=COLORS["accent_cyan"], hover_color=COLORS["hover_cyan"], font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        self.generated_password = ctk.CTkEntry(main_container, height=50, placeholder_text="Generated password", font=ctk.CTkFont(size=16), fg_color=COLORS["bg_light"], border_color=COLORS["border"], text_color=COLORS["text_white"])
        self.generated_password.pack(fill="x", pady=10)
        ctk.CTkButton(main_container, text="Copy to Clipboard", command=self.copy_password, height=35, width=180, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"]).pack(pady=10)
    
    def generate_password(self):
        try:
            length = int(self.password_length.get())
            if length < 4 or length > 128:
                show_custom_messagebox("Error", "Length must be between 4 and 128.", "error")
                return
        except ValueError:
            show_custom_messagebox("Error", "Invalid length.", "error")
            return
        charset = ""
        if self.pw_upper.get():
            charset += string.ascii_uppercase
        if self.pw_lower.get():
            charset += string.ascii_lowercase
        if self.pw_digits.get():
            charset += string.digits
        if self.pw_symbols.get():
            charset += string.punctuation
        if self.pw_exclude_ambiguous.get():
            ambiguous = "l1O0I"
            charset = ''.join(c for c in charset if c not in ambiguous)
        if not charset:
            show_custom_messagebox("Error", "Select at least one character type.", "error")
            return
        password = []
        if self.pw_upper.get():
            password.append(secrets.choice(string.ascii_uppercase))
        if self.pw_lower.get():
            password.append(secrets.choice(string.ascii_lowercase))
        if self.pw_digits.get():
            password.append(secrets.choice(string.digits))
        if self.pw_symbols.get():
            password.append(secrets.choice(string.punctuation))
        if self.pw_exclude_ambiguous.get():
            ambiguous = "l1O0I"
            password = [c for c in password if c not in ambiguous]
        remaining = length - len(password)
        if remaining > 0:
            password.extend(secrets.choice(charset) for _ in range(remaining))
        secrets.SystemRandom().shuffle(password)
        final_password = ''.join(password)
        self.generated_password.delete(0, "end")
        self.generated_password.insert(0, final_password)
        self.db.add_record("Password Generation", "Random Password", "Generated")
        self.set_status("Password generated")
    
    def copy_password(self):
        password = self.generated_password.get()
        if password:
            self.clipboard_clear()
            self.clipboard_append(password)
            self.set_status("Password copied to clipboard")
            show_custom_messagebox("Copied", "Password copied to clipboard!")
    
    # ------------------------------ Strength Analyzer ------------------------------ #
    def show_strength(self):
        self.clear_main()
        self.set_status("Password Strength Analyzer")
        self.add_header("Password Strength Analyzer", "Analyze password strength and get recommendations")
        main_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=10)
        
        ctk.CTkLabel(main_container, text="Enter password to analyze:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", pady=10)
        self.strength_entry = ctk.CTkEntry(main_container, height=40, placeholder_text="Type or paste password here", font=ctk.CTkFont(size=14), fg_color=COLORS["bg_light"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.strength_entry.pack(fill="x", pady=5)
        ctk.CTkButton(main_container, text="Analyze Strength", command=self.analyze_strength, height=40, width=200, fg_color=COLORS["accent_cyan"], hover_color=COLORS["hover_cyan"], font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
        
        results_frame = ctk.CTkFrame(main_container, corner_radius=12, fg_color=COLORS["bg_light"])
        results_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(results_frame, text="Strength Score:", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.strength_progress = ctk.CTkProgressBar(results_frame, width=600)
        self.strength_progress.set(0)
        self.strength_progress.pack(fill="x", padx=15, pady=10)
        self.strength_label = ctk.CTkLabel(results_frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.strength_label.pack(pady=5)
        self.strength_details = ctk.CTkTextbox(results_frame, height=200, wrap="word", font=ctk.CTkFont(size=12), state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.strength_details.pack(fill="x", padx=15, pady=(5, 15))
    
    def analyze_strength(self):
        password = self.strength_entry.get()
        if not password:
            show_custom_messagebox("Error", "Please enter a password.", "error")
            return
        score = 0
        details = []
        suggestions = []
        if len(password) >= 16:
            score += 30
            details.append("✅ Excellent length (16+ characters)")
        elif len(password) >= 12:
            score += 25
            details.append("✅ Good length (12-15 characters)")
        elif len(password) >= 8:
            score += 15
            details.append("⚠️ Acceptable length (8-11 characters)")
            suggestions.append("Consider using a longer password (12+ characters)")
        else:
            score += 5
            details.append("❌ Too short (less than 8 characters)")
            suggestions.append("Password is too short. Use at least 8 characters")
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        variety_count = sum([has_lower, has_upper, has_digit, has_symbol])
        score += variety_count * 15
        details.append(f"Character types: {variety_count}/4")
        if variety_count < 3:
            suggestions.append("Use a mix of uppercase, lowercase, numbers, and symbols")
        weak_patterns = ["password", "123456", "qwerty", "letmein", "admin", "iloveyou", "welcome", "monkey", "dragon", "football"]
        lowered = password.lower()
        for pattern in weak_patterns:
            if pattern in lowered:
                score = min(score, 20)
                details.append(f"❌ Contains common weak pattern: '{pattern}'")
                suggestions.append("Avoid common words and patterns")
                break
        score = max(0, min(score, 100))
        self.strength_progress.set(score / 100)
        if score >= 80:
            label = "STRONG"
            color = COLORS["accent_green"]
        elif score >= 60:
            label = "GOOD"
            color = "#00cc00"
        elif score >= 40:
            label = "MODERATE"
            color = COLORS["accent_orange"]
        elif score >= 20:
            label = "WEAK"
            color = COLORS["accent_red"]
        else:
            label = "VERY WEAK"
            color = "#ff0000"
        self.strength_label.configure(text=f"{label} ({score}/100)", text_color=color)
        details_text = "\n".join(details)
        if suggestions:
            details_text += "\n\n💡 Suggestions:\n" + "\n".join(f"• {s}" for s in suggestions)
        self.strength_details.configure(state="normal")
        self.strength_details.delete("1.0", "end")
        self.strength_details.insert("1.0", details_text)
        self.strength_details.configure(state="disabled")
        self.db.add_record("Password Analysis", "Password", f"Score: {score}/100 ({label})")
        self.set_status(f"Password strength: {label}")
    
    # ------------------------------ Port Scanner ------------------------------ #
    def show_port_scanner(self):
        self.clear_main()
        self.set_status("Port Scanner")
        self.add_header("TCP Port Scanner", "Scan for open TCP ports on authorized systems")
        ctk.CTkLabel(self.main_frame, text="⚠️ Use only on systems you own or have explicit permission to test!", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["accent_red"]).pack(pady=10)
        main_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", corner_radius=0, scrollbar_button_color=COLORS["accent_cyan"], scrollbar_button_hover_color=COLORS["hover_cyan"])
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        input_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        input_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(input_frame, text="Target IP/Hostname:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_white"]).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.scan_target_entry = ctk.CTkEntry(input_frame, height=35, width=250, placeholder_text="e.g. 192.168.1.1", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.scan_target_entry.grid(row=0, column=1, padx=15, pady=10)
        ctk.CTkLabel(input_frame, text="Port Range:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_white"]).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        port_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        port_frame.grid(row=1, column=1, padx=15, pady=10, sticky="w")
        self.scan_start_port = ctk.CTkEntry(port_frame, height=35, width=80, fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.scan_start_port.insert(0, "1")
        self.scan_start_port.pack(side="left", padx=2)
        ctk.CTkLabel(port_frame, text="to", text_color=COLORS["text_light"]).pack(side="left", padx=5)
        self.scan_end_port = ctk.CTkEntry(port_frame, height=35, width=80, fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.scan_end_port.insert(0, "1024")
        self.scan_end_port.pack(side="left", padx=2)
        
        options_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        options_frame.pack(fill="x", pady=5)
        self.scan_service_detection = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="Enable service detection", variable=self.scan_service_detection, text_color=COLORS["text_light"]).pack(side="left", padx=15, pady=15)
        
        self.scan_button = ctk.CTkButton(main_scroll, text="Start Scan", command=self.start_scan, height=40, width=200, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"], font=ctk.CTkFont(size=14, weight="bold"))
        self.scan_button.pack(pady=15)
        self.scan_progress = ctk.CTkProgressBar(main_scroll, width=600)
        self.scan_progress.set(0)
        self.scan_progress.pack(pady=10)
        
        results_frame = ctk.CTkFrame(main_scroll, corner_radius=12, fg_color=COLORS["bg_light"])
        results_frame.pack(fill="both", expand=True, pady=5)
        ctk.CTkLabel(results_frame, text="Scan Results:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.scan_results = ctk.CTkTextbox(results_frame, wrap="word", font=ctk.CTkFont(size=13), state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.scan_results.pack(fill="both", expand=True, padx=15, pady=(5, 15))
    
    def start_scan(self):
        target = self.scan_target_entry.get().strip()
        start_port = self.scan_start_port.get().strip()
        end_port = self.scan_end_port.get().strip()
        if not target:
            show_custom_messagebox("Error", "Please enter a target.", "error")
            return
        try:
            start = int(start_port)
            end = int(end_port)
            if start < 1 or end > 65535 or start > end:
                raise ValueError
        except ValueError:
            show_custom_messagebox("Error", "Invalid port range.", "error")
            return
        self.scan_results.configure(state="normal")
        self.scan_results.delete("1.0", "end")
        self.scan_results.configure(state="disabled")
        self.scan_progress.set(0)
        ports_to_scan = list(range(start, end + 1))
        self.scan_results.configure(state="normal")
        self.scan_results.insert("end", f"Scanning {target}...\n")
        self.scan_results.configure(state="disabled")
        self.scan_button.configure(state="disabled")
        self.stop_scan_flag = False
        thread = threading.Thread(target=self.scan_ports, args=(target, ports_to_scan), daemon=True)
        thread.start()
    
    def scan_ports(self, target, ports):
        open_ports = []
        services = {}
        total_ports = len(ports)
        service_map = {21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 135: "MS RPC", 139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy"}
        for i, port in enumerate(ports):
            if self.stop_scan_flag:
                break
            progress = (i + 1) / total_ports
            self.after(0, self.scan_progress.set, progress)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((target, port))
                if result == 0:
                    open_ports.append(port)
                    service = service_map.get(port, "unknown") if self.scan_service_detection.get() else "unknown"
                    services[port] = service
                    self.after(0, self.append_scan_result, port, service)
                sock.close()
            except Exception:
                pass
        self.after(0, self.scan_complete, target, open_ports, services)
    
    def append_scan_result(self, port, service):
        self.scan_results.configure(state="normal")
        self.scan_results.insert("end", f"  Port {port}: OPEN ({service})\n")
        self.scan_results.see("end")
        self.scan_results.configure(state="disabled")
    
    def scan_complete(self, target, open_ports, services):
        self.scan_button.configure(state="normal")
        self.scan_progress.set(1)
        self.scan_results.configure(state="normal")
        if open_ports:
            self.scan_results.insert("end", f"\n✅ Scan complete. {len(open_ports)} open ports found.\n")
        else:
            self.scan_results.insert("end", "\n✅ Scan complete. No open ports found.\n")
        self.scan_results.configure(state="disabled")
        self.current_open_ports = open_ports
        self.current_services = services
        self.current_scan_target = target
        self.db.save_scan(target, "TCP", open_ports, services)
        self.db.add_record("Port Scan", target, f"Open ports: {open_ports}")
        self.set_status(f"Scan complete: {len(open_ports)} open ports")
    
    # ------------------------------ Network Discovery ------------------------------ #
    def show_network_discovery(self):
        self.clear_main()
        self.set_status("Network Discovery")
        self.add_header("Network Device Discovery", "Discover devices on your local network")
        ctk.CTkLabel(self.main_frame, text="Discover active devices using Ping Sweep + ARP", font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"]).pack(pady=10)
        
        range_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        range_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(range_frame, text="Network Range:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(side="left", padx=15, pady=15)
        self.network_range_entry = ctk.CTkEntry(range_frame, height=35, width=250, fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.network_range_entry.insert(0, "192.168.1.0/24")
        self.network_range_entry.pack(side="left", padx=15, pady=15)
        ctk.CTkButton(self.main_frame, text="Start Discovery", command=self.start_discovery, height=40, width=200, fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"], font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.discovery_progress = ctk.CTkProgressBar(self.main_frame, width=600)
        self.discovery_progress.set(0)
        self.discovery_progress.pack(pady=10)
        self.discovery_status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.discovery_status_label.pack(pady=5)
        self.discovery_results = ctk.CTkTextbox(self.main_frame, wrap="word", font=ctk.CTkFont(size=12), state="disabled", fg_color=COLORS["bg_light"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.discovery_results.pack(fill="both", expand=True, padx=25, pady=10)
    
    def start_discovery(self):
        network_range = self.network_range_entry.get().strip()
        if not network_range:
            show_custom_messagebox("Error", "Please enter a network range.", "error")
            return
        self.discovery_results.configure(state="normal")
        self.discovery_results.delete("1.0", "end")
        self.discovery_results.insert("end", "Starting network discovery...\n\n")
        self.discovery_results.configure(state="disabled")
        self.discovery_progress.set(0)
        self.discovery_status_label.configure(text="Initializing...")
        self.set_status("Discovering devices...")
        thread = threading.Thread(target=self._discovery_worker, args=(network_range,), daemon=True)
        thread.start()
    
    def _discovery_worker(self, network_range):
        try:
            network = ipaddress.ip_network(network_range, strict=False)
            devices = []
            active_hosts = []
            hosts = list(network.hosts())
            total_hosts = len(hosts)
            for i, ip in enumerate(hosts):
                ip_str = str(ip)
                progress = (i + 1) / total_hosts if total_hosts > 0 else 0
                self.after(0, self._update_discovery_ui, progress, ip_str, len(active_hosts))
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creationflags = subprocess.CREATE_NO_WINDOW
                    ping_cmd = ["ping", "-n", "1", "-w", "300", ip_str]
                else:
                    startupinfo = None
                    creationflags = 0
                    ping_cmd = ["ping", "-c", "1", "-W", "1", ip_str]
                try:
                    if startupinfo:
                        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=1, startupinfo=startupinfo, creationflags=creationflags)
                    else:
                        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if result.returncode == 0:
                        active_hosts.append(ip_str)
                        self.after(0, self._update_discovery_found, ip_str)
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
            if active_hosts:
                try:
                    if platform.system() == "Windows":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        arp_result = subprocess.run(["arp", "-a"], capture_output=True, text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        arp_result = subprocess.run(["arp", "-a"], capture_output=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    arp_dict = {}
                    for line in arp_result.stdout.split('\n'):
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        mac_match = re.search(r'([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})', line)
                        if ip_match and mac_match:
                            arp_dict[ip_match.group(1)] = mac_match.group(1)
                    for ip in active_hosts:
                        mac = arp_dict.get(ip, "Unknown")
                        devices.append((ip, mac))
                except Exception:
                    for ip in active_hosts:
                        devices.append((ip, "Unknown"))
            self.after(0, self._discovery_complete, network_range, devices)
        except ValueError as e:
            self.after(0, self._discovery_error, f"Invalid network range: {e}")
        except Exception as e:
            self.after(0, self._discovery_error, str(e))
    
    def _update_discovery_ui(self, progress, current_ip, found_count):
        try:
            self.discovery_progress.set(progress)
            self.discovery_status_label.configure(text=f"Scanning: {current_ip} | Found: {found_count} devices")
            self.set_status(f"Scanning: {current_ip} ({int(progress * 100)}%)")
        except Exception:
            pass
    
    def _update_discovery_found(self, ip):
        try:
            self.discovery_results.configure(state="normal")
            self.discovery_results.insert("end", f"  ✅ {ip}\n")
            self.discovery_results.see("end")
            self.discovery_results.configure(state="disabled")
        except Exception:
            pass
    
    def _discovery_complete(self, network_range, devices):
        try:
            self.discovery_progress.set(1)
            self.discovery_status_label.configure(text=f"Complete: {len(devices)} devices found")
            self.discovery_results.configure(state="normal")
            self.discovery_results.delete("1.0", "end")
            if devices:
                self.discovery_results.insert("end", f"✅ Discovery Complete!\n\n")
                self.discovery_results.insert("end", f"Found {len(devices)} active devices:\n\n")
                self.discovery_results.insert("end", "=" * 60 + "\n")
                self.discovery_results.insert("end", f"{'IP Address':<20} {'MAC Address':<20}\n")
                self.discovery_results.insert("end", "=" * 60 + "\n")
                for ip, mac in devices:
                    self.discovery_results.insert("end", f"{ip:<20} {mac:<20}\n")
                self.db.add_record("Network Discovery", network_range, f"Found {len(devices)} devices")
                self.set_status(f"✅ Found {len(devices)} devices")
            else:
                self.discovery_results.insert("end", "❌ No active devices found on this network.")
                self.set_status("No devices found")
            self.discovery_results.configure(state="disabled")
        except Exception:
            pass
    
    def _discovery_error(self, error_msg):
        try:
            self.discovery_progress.set(0)
            self.discovery_status_label.configure(text="Error occurred")
            self.discovery_results.configure(state="normal")
            self.discovery_results.delete("1.0", "end")
            self.discovery_results.insert("end", f"❌ Discovery failed:\n{error_msg}")
            self.discovery_results.configure(state="disabled")
            self.set_status("Discovery failed")
        except Exception:
            pass
    
    # ------------------------------ Quarantine ------------------------------ #
    def show_quarantine(self):
        self.clear_main()
        self.set_status("File Quarantine")
        self.add_header("File Quarantine", "Isolate suspicious files for safekeeping")
        
        action_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        action_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(action_frame, text="Quarantine a suspicious file:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.quarantine_file_label = ctk.CTkLabel(action_frame, text="No file selected", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.quarantine_file_label.pack(anchor="w", padx=15, pady=5)
        ctk.CTkButton(action_frame, text="Select File", command=self.select_quarantine_file, width=150, fg_color=COLORS["accent_purple"], hover_color=COLORS["hover_purple"]).pack(anchor="w", padx=15, pady=5)
        ctk.CTkLabel(action_frame, text="Reason for quarantine:", font=ctk.CTkFont(size=13), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(10, 5))
        self.quarantine_reason = ctk.CTkEntry(action_frame, height=35, placeholder_text="e.g. Suspicious file detected", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.quarantine_reason.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(action_frame, text="Quarantine File", command=self.quarantine_file, height=35, width=180, fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"], font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(10, 15))
        
        list_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        list_frame.pack(fill="both", expand=True, padx=25, pady=10)
        ctk.CTkLabel(list_frame, text="Quarantined Files:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(anchor="w", padx=15, pady=(15, 5))
        self.quarantine_list = ctk.CTkTextbox(list_frame, wrap="word", font=ctk.CTkFont(size=12), state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.quarantine_list.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.refresh_quarantine_list()
    
    def select_quarantine_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.current_quarantine_file = filepath
            self.quarantine_file_label.configure(text=os.path.basename(filepath))
    
    def quarantine_file(self):
        if not self.current_quarantine_file:
            show_custom_messagebox("Error", "Please select a file to quarantine.", "error")
            return
        reason = self.quarantine_reason.get().strip()
        if not reason:
            reason = "Manual quarantine"
        quarantine_dir = QUARANTINE_DIR
        os.makedirs(quarantine_dir, exist_ok=True)
        original_name = os.path.basename(self.current_quarantine_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_name = f"{timestamp}_{original_name}"
        quarantine_path = os.path.join(quarantine_dir, quarantine_name)
        try:
            shutil.copy2(self.current_quarantine_file, quarantine_path)
            self.db.save_quarantine(self.current_quarantine_file, quarantine_path, reason)
            self.db.add_record("File Quarantine", self.current_quarantine_file, reason, "QUARANTINED")
            self.refresh_quarantine_list()
            self.set_status("File quarantined")
            show_custom_messagebox("Success", f"File quarantined to:\n{quarantine_path}")
        except Exception as e:
            show_custom_messagebox("Error", f"Failed to quarantine file: {str(e)}", "error")
    
    def refresh_quarantine_list(self):
        self.db.cursor.execute("SELECT * FROM quarantine ORDER BY timestamp DESC")
        records = self.db.cursor.fetchall()
        self.quarantine_list.configure(state="normal")
        self.quarantine_list.delete("1.0", "end")
        if not records:
            self.quarantine_list.insert("end", "No quarantined files.")
        else:
            self.quarantine_list.insert("end", f"{'File':<30} {'Reason':<30} {'Date':<20}\n")
            self.quarantine_list.insert("end", "=" * 80 + "\n")
            for record in records:
                file_name = os.path.basename(record[1])[:25]
                reason = record[3][:25] if record[3] else "N/A"
                date = record[4][:19] if len(record) > 4 else "N/A"
                self.quarantine_list.insert("end", f"{file_name:<30} {reason:<30} {date:<20}\n")
        self.quarantine_list.configure(state="disabled")
    
    # ------------------------------ Report Module ------------------------------ #
    def show_report(self):
        self.clear_main()
        self.set_status("Security Report")
        self.add_header("Security Report Generator", "Generate comprehensive security reports")
        
        options_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        options_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(options_frame, text="Report Type:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_white"]).pack(side="left", padx=15, pady=15)
        self.report_type = ctk.StringVar(value="TXT")
        for rtype in ["TXT", "PDF", "CSV"]:
            ctk.CTkRadioButton(options_frame, text=rtype, variable=self.report_type, value=rtype, text_color=COLORS["text_light"]).pack(side="left", padx=10, pady=15)
        
        content_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        content_frame.pack(fill="both", expand=True, padx=25, pady=10)
        self.report_preview = ctk.CTkTextbox(content_frame, wrap="word", font=ctk.CTkFont(size=12), state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.report_preview.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_report_preview()
        ctk.CTkButton(self.main_frame, text="Export Report", command=self.export_report, height=40, width=200, fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"], font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
    
    def refresh_report_preview(self):
        records = self.db.get_all_records()
        self.report_preview.configure(state="normal")
        self.report_preview.delete("1.0", "end")
        if not records:
            self.report_preview.insert("end", "No security operations recorded.")
        else:
            self.report_preview.insert("end", "=" * 70 + "\n")
            self.report_preview.insert("end", "CYBERSAFE TOOLKIT - SECURITY REPORT\n")
            self.report_preview.insert("end", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.report_preview.insert("end", "=" * 70 + "\n\n")
            for record in records:
                id, operation, target, result, timestamp, status = record
                self.report_preview.insert("end", f"[{timestamp}] {operation}\n")
                self.report_preview.insert("end", f"    Target: {target}\n")
                self.report_preview.insert("end", f"    Result: {result}\n")
                self.report_preview.insert("end", f"    Status: {status}\n")
                self.report_preview.insert("end", "-" * 70 + "\n")
        self.report_preview.configure(state="disabled")
    
    def export_report(self):
        report_type = self.report_type.get()
        records = self.db.get_all_records()
        if not records:
            show_custom_messagebox("Report", "No records to export.")
            return
        if report_type == "TXT":
            self.export_txt_report(records)
        elif report_type == "PDF":
            self.export_pdf_report(records)
        elif report_type == "CSV":
            self.export_csv_report(records)
    
    def export_txt_report(self, records):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], initialfile="cybersafe_report.txt")
        if not filepath:
            return
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write("CYBERSAFE TOOLKIT - SECURITY REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                for record in records:
                    id, operation, target, result, timestamp, status = record
                    f.write(f"[{timestamp}] {operation}\n")
                    f.write(f"    Target: {target}\n")
                    f.write(f"    Result: {result}\n")
                    f.write(f"    Status: {status}\n")
                    f.write("-" * 70 + "\n")
            self.db.add_record("Export Report", filepath, f"Exported {len(records)} records")
            show_custom_messagebox("Success", f"Report exported to:\n{filepath}")
            self.set_status("Report exported")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    def export_pdf_report(self, records):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")], initialfile="cybersafe_report.pdf")
        if not filepath:
            return
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, textColor=colors.HexColor('#0d1117'), spaceAfter=30)
            elements.append(Paragraph("CyberSafe Toolkit - Security Report", title_style))
            elements.append(Spacer(1, 0.2 * inch))
            date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=12, textColor=colors.grey)
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
            elements.append(Spacer(1, 0.3 * inch))
            table_data = [["Timestamp", "Operation", "Target", "Result", "Status"]]
            for record in records:
                id, operation, target, result, timestamp, status = record
                table_data.append([timestamp, operation, str(target)[:30], str(result)[:50], status])
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1117')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(table)
            doc.build(elements)
            self.db.add_record("Export Report", filepath, f"Exported {len(records)} records to PDF")
            show_custom_messagebox("Success", f"PDF report exported to:\n{filepath}")
            self.set_status("PDF report exported")
        except Exception as e:
            show_custom_messagebox("Error", f"Failed to export PDF: {str(e)}", "error")
    
    def export_csv_report(self, records):
        import csv
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile="cybersafe_report.csv")
        if not filepath:
            return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Operation", "Target", "Result", "Status"])
                for record in records:
                    id, operation, target, result, timestamp, status = record
                    writer.writerow([timestamp, operation, target, result, status])
            self.db.add_record("Export Report", filepath, f"Exported {len(records)} records to CSV")
            show_custom_messagebox("Success", f"CSV report exported to:\n{filepath}")
            self.set_status("CSV report exported")
        except Exception as e:
            show_custom_messagebox("Error", str(e), "error")
    
    # ------------------------------ History ------------------------------ #
    def show_history(self):
        self.clear_main()
        self.set_status("Operation History")
        self.add_header("Operation History", "View all security operations performed")
        
        filter_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        filter_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(filter_frame, text="Filter by:", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_white"]).pack(side="left", padx=15, pady=15)
        self.history_filter = ctk.CTkEntry(filter_frame, height=35, width=200, placeholder_text="e.g. Encryption, Scan...", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.history_filter.pack(side="left", padx=15, pady=15)
        ctk.CTkButton(filter_frame, text="Apply Filter", command=self.refresh_history, width=120, fg_color=COLORS["accent_cyan"], hover_color=COLORS["hover_cyan"]).pack(side="left", padx=5, pady=15)
        ctk.CTkButton(filter_frame, text="Clear Filter", command=self.clear_history_filter, width=120, fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"]).pack(side="left", padx=5, pady=15)
        
        history_frame = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=COLORS["bg_light"])
        history_frame.pack(fill="both", expand=True, padx=25, pady=10)
        self.history_text = ctk.CTkTextbox(history_frame, wrap="word", font=ctk.CTkFont(size=12), state="disabled", fg_color=COLORS["bg_medium"], border_color=COLORS["border"], text_color=COLORS["text_light"])
        self.history_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_history()
    
    def refresh_history(self):
        filter_text = self.history_filter.get().strip()
        if filter_text:
            self.db.cursor.execute("SELECT * FROM security_records WHERE operation LIKE ? OR target LIKE ? OR result LIKE ? ORDER BY timestamp DESC", (f"%{filter_text}%", f"%{filter_text}%", f"%{filter_text}%"))
        else:
            self.db.cursor.execute("SELECT * FROM security_records ORDER BY timestamp DESC")
        records = self.db.cursor.fetchall()
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        if not records:
            self.history_text.insert("end", "No records found.")
        else:
            self.history_text.insert("end", f"{'ID':<5} {'Timestamp':<20} {'Operation':<25} {'Target':<25} {'Status':<12}\n")
            self.history_text.insert("end", "=" * 100 + "\n")
            for record in records:
                id, operation, target, result, timestamp, status = record
                target_display = str(target)[:25] if target else "N/A"
                self.history_text.insert("end", f"{id:<5} {timestamp:<20} {operation:<25} {target_display:<25} {status:<12}\n")
        self.history_text.configure(state="disabled")
    
    def clear_history_filter(self):
        self.history_filter.delete(0, "end")
        self.refresh_history()

# ------------------------------ Main Entry Point ------------------------------ #
if __name__ == "__main__":
    app = CyberSafeApp()
    app.mainloop()