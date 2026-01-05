#!/usr/bin/env python3
"""
XEDA TERMINAL AGENT - MULTI-MODEL EDITION (v9.3) - ENHANCED VERSION
Author: AI Software Engineer
Date: 2025

Features:
 - Triple AI Engine Support (Gemini + DeepSeek + Groq)
 - Auto Package Installation
 - Post-execution Summary
 - Silent Error Handling
 - Deep Thinking Workflow
 - Single-line Progress Updates
"""

import os
import sys
import json
import time
import subprocess
import traceback
import ctypes
import platform
import difflib
import threading
import queue
import random
import re
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ==============================================================================
# 0. ENHANCED ANSI COLORS & UI SYSTEM
# ==============================================================================

# Enable ANSI Colors for Windows 10/11 CMD
if os.name == 'nt':
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class Color:
    """ANSI color codes"""
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    
    RESET = '\033[0m'

class UI:
    """Handles all user interface interactions and styling with silent mode."""
    GHOST_MODE = False
    SILENT_ERRORS = True
    LAST_PROGRESS_LENGTH = 0
    EXECUTION_SUMMARY = []
    
    @staticmethod
    def add_to_summary(action, target, status="✅", details=""):
        """Add entry to execution summary"""
        UI.EXECUTION_SUMMARY.append({
            "action": action,
            "target": target,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def clear_summary():
        """Clear execution summary"""
        UI.EXECUTION_SUMMARY = []
    
    @staticmethod
    def show_summary():
        """Show execution summary after completion"""
        if not UI.EXECUTION_SUMMARY or UI.GHOST_MODE:
            return
        
        print(f"\n{Color.CYAN}{'━'*50}{Color.RESET}")
        print(f"{Color.BOLD}📊 Execution Summary:{Color.RESET}")
        print(f"{Color.DIM}{'━'*50}{Color.RESET}")
        
        successes = 0
        failures = 0
        installed = []
        created = []
        modified = []
        
        for entry in UI.EXECUTION_SUMMARY:
            status_color = Color.GREEN if "✅" in entry["status"] else Color.RED if "❌" in entry["status"] else Color.YELLOW
            print(f"{status_color}{entry['status']}{Color.RESET} {entry['action']}: {entry['target']}")
            
            if entry["details"]:
                print(f"   {Color.DIM}{entry['details']}{Color.RESET}")
            
            # Categorize
            if "✅" in entry["status"]:
                successes += 1
                if "install" in entry["action"].lower():
                    installed.append(entry["target"])
                elif "create" in entry["action"].lower():
                    created.append(entry["target"])
                elif "modif" in entry["action"].lower():
                    modified.append(entry["target"])
            elif "❌" in entry["status"]:
                failures += 1
        
        print(f"{Color.DIM}{'━'*50}{Color.RESET}")
        
        # Show statistics
        print(f"\n{Color.BOLD}📈 Statistics:{Color.RESET}")
        print(f"  {Color.GREEN}✓ Successes: {successes}{Color.RESET} | {Color.RED}✗ Failures: {failures}{Color.RESET}")
        
        if installed:
            print(f"\n{Color.GREEN}📦 Installed Packages:{Color.RESET}")
            for pkg in installed:
                print(f"  • {pkg}")
        
        if created:
            print(f"\n{Color.BLUE}📄 Created Files:{Color.RESET}")
            for file in created[:10]:
                print(f"  • {file}")
            if len(created) > 10:
                print(f"  {Color.DIM}... and {len(created)-10} more{Color.RESET}")
        
        if modified:
            print(f"\n{Color.YELLOW}✏️  Modified Files:{Color.RESET}")
            for file in modified[:10]:
                print(f"  • {file}")
            if len(modified) > 10:
                print(f"  {Color.DIM}... and {len(modified)-10} more{Color.RESET}")
        
        print(f"\n{Color.CYAN}{'━'*50}{Color.RESET}")
        print(f"{Color.GREEN}✨ Task completed successfully!{Color.RESET}\n")
        
        # Clear summary for next task
        UI.clear_summary()
    
    @staticmethod
    def set_ghost(enabled: bool):
        UI.GHOST_MODE = enabled
        state = "ON 👻" if enabled else "OFF"
        UI.print_system(f"Ghost Mode: {state}")

    @staticmethod
    def update_progress(message):
        """Single-line progress updates"""
        if UI.GHOST_MODE:
            return
            
        # Clear previous line
        clear = " " * UI.LAST_PROGRESS_LENGTH
        print(f"\r{clear}\r", end="", flush=True)
        
        # Show new progress with spinner
        spinner = random.choice(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        display_msg = f"{Color.CYAN}{spinner}{Color.RESET} {message}"
        print(f"\r{display_msg}", end="", flush=True)
        UI.LAST_PROGRESS_LENGTH = len(display_msg)
    
    @staticmethod
    def clear_progress():
        """Clear progress line"""
        if UI.LAST_PROGRESS_LENGTH > 0:
            print(f"\r{' ' * UI.LAST_PROGRESS_LENGTH}\r", end="", flush=True)
            UI.LAST_PROGRESS_LENGTH = 0

    @staticmethod
    def log(text, color=Color.RESET, force=False):
        if not UI.GHOST_MODE or force:
            UI.clear_progress()
            print(f"{color}{text}{Color.RESET}")

    @staticmethod
    def print_agent(text, model_name="XEDA"):
        if not UI.GHOST_MODE:
            UI.clear_progress()
            print(f"\n{Color.GREEN}│{Color.RESET}")
            print(f"{Color.GREEN}└─▶ [{model_name}]{Color.RESET} {text}")

    @staticmethod
    def print_system(text):
        UI.log(f"{Color.DIM}▸ {Color.CYAN}[System]{Color.DIM}:{Color.RESET} {text}",Color.DIM)

    @staticmethod
    def print_user(text):
        UI.log(f"👤 {Color.BLUE}[You]:{Color.RESET} {text}", Color.BLUE)

    @staticmethod
    def print_success(text):
        UI.log(f"✅ {text}{Color.RESET}", Color.GREEN, force=True)

    @staticmethod
    def print_error(text, silent=True):
        if not silent:
            UI.log(f"❌ {text}{Color.RESET}", Color.RED, force=True)

    @staticmethod
    def print_warning(text):
        UI.log(f"⚠️  {text}{Color.RESET}", Color.YELLOW, force=True)
    
    @staticmethod
    def print_note(text):
        UI.log(f"📝 {text}{Color.RESET}", Color.CYAN, force=True)

    @staticmethod
    def input_prompt(path):
        display_path = path.replace(os.path.expanduser("~"), "~")
        UI.clear_progress()
        print(f"\n{Color.BLUE}{display_path}{Color.YELLOW} ➤ {Color.RESET} ", end="", flush=True)
        return input().strip()
        
    @staticmethod
    def render_plan(plan_data, model_name="AI"):
        """Enhanced plan rendering with deep analysis"""
        steps = plan_data.get('steps', [])
        confidence = plan_data.get('confidence', 0)
        risk = plan_data.get('risk', 'Unknown')
        suggestion = plan_data.get('suggestion', '')
        analysis = plan_data.get('analysis', '')
        dependencies = plan_data.get('dependencies', [])
        
        conf_color = Color.GREEN if confidence >= 80 else Color.YELLOW if confidence >= 50 else Color.RED
        
        UI.clear_progress()
        UI.log(f"\n{Color.YELLOW}📋 Execution Plan {Color.DIM}(Model: {model_name} | Confidence: {conf_color}{confidence}%{Color.DIM} | Risk: {risk}){Color.RESET}")
        
        if analysis:
            UI.log(f"\n{Color.CYAN}🔍 Deep Analysis:{Color.RESET}")
            UI.log(f"{Color.DIM}{analysis}{Color.RESET}")
        
        if dependencies:
            UI.log(f"\n{Color.MAGENTA}📦 Dependencies:{Color.RESET}")
            for dep in dependencies:
                UI.log(f"  • {dep}")

        if suggestion:
            UI.log(f"\n{Color.CYAN}💡 Teammate Tip: {suggestion}{Color.RESET}")

        UI.log(f"\n{Color.DIM}----------------------------------------{Color.RESET}")
        for i, step in enumerate(steps, 1):
            action = step.get('action', '???').upper()
            target = step.get('path') or step.get('command') or "Unknown"
            desc = step.get('description', '')
            reasoning = step.get('reasoning', '')
            
            color = Color.GREEN if action == 'CREATE' else Color.YELLOW if action == 'MODIFY' else Color.RED if action == 'DELETE' else Color.CYAN
            UI.log(f" {i}. {color}{action:<8}{Color.RESET} {target}")
            UI.log(f"    └─ {Color.DIM}{desc}{Color.RESET}")
            if reasoning:
                UI.log(f"      {Color.MAGENTA}🤔 {reasoning}{Color.RESET}")
        UI.log(f"{Color.DIM}----------------------------------------{Color.RESET}\n")
    
    @staticmethod
    def show_diff(file_path, old_content, new_content, model_name="AI"):
        if UI.GHOST_MODE: return
        
        UI.clear_progress()
        print(f"\n{Color.YELLOW}🔍 Diff Preview (by {model_name}) for: {Color.BOLD}{file_path}{Color.RESET}")
        print(f"{Color.DIM}----------------------------------------{Color.RESET}")
        
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=''
        )
        
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"{Color.GREEN}{line}{Color.RESET}")
            elif line.startswith('-') and not line.startswith('---'):
                print(f"{Color.RED}{line}{Color.RESET}")
            elif line.startswith('@'):
                print(f"{Color.BLUE}{line}{Color.RESET}")
            else:
                print(f"{Color.DIM}{line}{Color.RESET}")
        print(f"{Color.DIM}----------------------------------------{Color.RESET}\n")

# ==============================================================================
# 1. PACKAGE MANAGER - AUTO INSTALLATION SYSTEM
# ==============================================================================

class PackageManager:
    """Handles automatic package installation and dependency management"""
    
    # Common package managers and their install commands
    PACKAGE_MANAGERS = {
        'npm': {
            'check': 'npm --version',
            'install': 'npm install',
            'global_install': 'npm install -g',
            'check_package': 'npm list'
        },
        'pip': {
            'check': 'pip --version',
            'install': 'pip install',
            'global_install': 'pip install',
            'check_package': 'pip show'
        },
        'pip3': {
            'check': 'pip3 --version',
            'install': 'pip3 install',
            'global_install': 'pip3 install',
            'check_package': 'pip3 show'
        },
        'yarn': {
            'check': 'yarn --version',
            'install': 'yarn add',
            'global_install': 'yarn global add',
            'check_package': 'yarn list'
        },
        'apt': {
            'check': 'apt --version',
            'install': 'sudo apt install',
            'check_package': 'dpkg -s'
        },
        'brew': {
            'check': 'brew --version',
            'install': 'brew install',
            'check_package': 'brew list'
        },
        'docker': {
            'check': 'docker --version',
            'install': 'system-specific',
            'check_package': 'docker --version'
        },
        'git': {
            'check': 'git --version',
            'install': 'system-specific',
            'check_package': 'git --version'
        }
    }
    
    # في class PackageManager، أعد كتابة دالة detect_missing_package:

@staticmethod
def detect_missing_package(error_output: str, command: str) -> tuple:
    """Detect missing package from error output"""
    error_lower = error_output.lower()
    command_lower = command.lower()
    
    # تحسين اكتشاف npm
    if 'npm' in command_lower or 'node' in command_lower or 'npx' in command_lower:
        # تحقق من رسائل الخطأ الشائعة
        error_patterns = [
            'npm: command not found',
            'npm: not found',
            'npm: no such file or directory',
            'node: command not found',
            'node: not found'
        ]
        
        for pattern in error_patterns:
            if pattern in error_lower:
                return 'npm', 'nodejs', "Node.js package manager"
    
    # تحسين اكتشاف pip
    if 'pip' in command_lower or 'python' in command_lower:
        error_patterns = [
            'pip: command not found',
            'pip3: command not found',
            'python: command not found',
            'python3: command not found'
        ]
        
        for pattern in error_patterns:
            if pattern in error_lower:
                return 'pip', 'python3-pip', "Python package installer"
    
    # اكتشاف docker
    if 'docker' in command_lower:
        if 'docker: command not found' in error_lower:
            return 'docker', 'docker-ce', "Docker container platform"
    
    # اكتشاف git
    if 'git' in command_lower:
        if 'git: command not found' in error_lower:
            return 'git', 'git', "Git version control"
    
    # محاولة استخراج اسم الباكج من رسالة الخطأ
    patterns = [
        r"package '([^']+)' is not installed",
        r"module '([^']+)' not found",
        r"could not find module '([^']+)'",
        r"command '([^']+)' not found"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error_output, re.IGNORECASE)
        if match:
            pkg_name = match.group(1)
            # تحديد مدير الباكج بناءً على السياق
            if '.' in pkg_name or pkg_name.startswith('@'):
                return 'npm', pkg_name, f"Node.js package: {pkg_name}"
            elif any(char.isupper() for char in pkg_name):
                return 'pip', pkg_name, f"Python package: {pkg_name}"
    
    return None, None, None
    @staticmethod
    def is_package_manager_installed(manager: str) -> bool:
        """Check if a package manager is installed"""
        if manager not in PackageManager.PACKAGE_MANAGERS:
            return False
        
        check_cmd = PackageManager.PACKAGE_MANAGERS[manager]['check']
        try:
            result = subprocess.run(
                check_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def install_package_manager(manager: str) -> tuple:
        """Install a package manager"""
        install_commands = {
            'npm': {
                'windows': 'winget install OpenJS.NodeJS',
                'linux': 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs',
                'darwin': 'brew install node'
            },
            'pip': {
                'windows': 'python -m ensurepip --upgrade',
                'linux': 'sudo apt update && sudo apt install python3-pip',
                'darwin': 'brew install python'
            },
            'docker': {
                'windows': 'winget install Docker.DockerDesktop',
                'linux': 'curl -fsSL https://get.docker.com | sudo sh',
                'darwin': 'brew install docker'
            },
            'git': {
                'windows': 'winget install Git.Git',
                'linux': 'sudo apt update && sudo apt install git',
                'darwin': 'brew install git'
            }
        }
        
        system = platform.system().lower()
        
        if manager in install_commands and system in install_commands[manager]:
            cmd = install_commands[manager][system]
            return True, cmd
        
        return False, f"Automatic installation not available for {manager} on {system}"
    
    @staticmethod
    def get_install_command(manager: str, package: str, is_global=False) -> str:
        """Get installation command for a package"""
        if manager not in PackageManager.PACKAGE_MANAGERS:
            return None
        
        cmd_template = PackageManager.PACKAGE_MANAGERS[manager]['global_install' if is_global else 'install']
        return f"{cmd_template} {package}"
    
    @staticmethod
    def handle_missing_dependency(error_output: str, failed_command: str, store):
        """Handle missing dependency and ask for installation permission"""
        manager, package, description = PackageManager.detect_missing_package(error_output, failed_command)
        
        if not manager or not package:
            return None
        
        # Check if package manager itself is missing
        if not PackageManager.is_package_manager_installed(manager):
            UI.print_note(f"📦 {manager.upper()} is not installed.")
            UI.print_note(f"   Required for: {description}")
            
            if UI.GHOST_MODE:
                return None
            
            response = input(f"{Color.YELLOW}Install {manager.upper()}? (y/n): {Color.RESET}").lower()
            if response != 'y':
                return None
            
            can_install, install_cmd = PackageManager.install_package_manager(manager)
            if not can_install:
                UI.print_error(f"Cannot auto-install {manager}")
                return None
            
            UI.print_system(f"Installing {manager.upper()}...")
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                UI.print_success(f"✅ {manager.upper()} installed successfully")
                store.log(f"Installed package manager: {manager}", "INFO")
                UI.add_to_summary(f"Installed {manager.upper()}", manager, "✅", "Package manager installed")
                return True
            else:
                UI.print_error(f"Failed to install {manager}")
                store.log(f"Failed to install {manager}: {result.stderr}", "ERROR")
                return False
        
        # Package is missing, not the manager
        UI.print_note(f"📦 Missing package: {package}")
        UI.print_note(f"   Required for command: {failed_command}")
        
        if UI.GHOST_MODE:
            return None
        
        response = input(f"{Color.YELLOW}Install {package}? (y/n): {Color.RESET}").lower()
        if response != 'y':
            return None
        
        install_cmd = PackageManager.get_install_command(manager, package)
        if not install_cmd:
            UI.print_error(f"Cannot determine install command for {package}")
            return None
        
        UI.print_system(f"Installing {package}...")
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            UI.print_success(f"✅ {package} installed successfully")
            store.log(f"Installed package: {package} via {manager}", "INFO")
            UI.add_to_summary(f"Installed package", package, "✅", f"via {manager}")
            return True
        else:
            UI.print_error(f"Failed to install {package}")
            store.log(f"Failed to install {package}: {result.stderr}", "ERROR")
            UI.add_to_summary(f"Failed to install", package, "❌", result.stderr[:100])
            return False

# ==============================================================================
# 2. PERSISTENCE & CONFIGURATION
# ==============================================================================

# Try to import all available AI libraries
AI_ENGINES = {}
try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
    AI_ENGINES['gemini'] = True
except ImportError:
    AI_ENGINES['gemini'] = False

try:
    from openai import OpenAI
    AI_ENGINES['deepseek'] = True
except ImportError:
    AI_ENGINES['deepseek'] = False

try:
    import groq
    AI_ENGINES['groq'] = True
except ImportError:
    AI_ENGINES['groq'] = False

class PersistenceLayer:
    """Manages saving/loading configs, history, and logs with Multi-Model support."""
    
    APP_DIR = os.path.join(os.path.expanduser("~"), ".xeda_terminal")
    
    DEFAULT_CONFIG = {
        "active_engine": "groq",
        "gemini_api_key": "",
        "deepseek_api_key": "",
        "groq_api_key": "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",
        "model": "gemini-2.5-flash-lite",
        "groq_model": "groq/compound",
        "temperature": 0.7,
        "max_tokens": 8192,
        "workspace": os.getcwd(),
        "auto_mode": False,
        "ghost_mode": False,
        "silent_errors": True,
        "fallback_enabled": True,
        "auto_install": True,
        "model_stats": {},
        "installed_packages": [],
        "installation_history": [],
        "error_log": []
    }

    def __init__(self):
        self._ensure_dir()
        self.config_path = os.path.join(self.APP_DIR, "config.json")
        self.history_path = os.path.join(self.APP_DIR, "history.json")
        self.log_path = os.path.join(self.APP_DIR, "system.log")
        self.error_path = os.path.join(self.APP_DIR, "errors.json")
        
        self.config = self._load_config_safely()
        self.history = self._load_json(self.history_path, [])
        self.error_log = self._load_json(self.error_path, [])
        self.last_plan_cache = None
        
        # Initialize model stats if not present
        if "model_stats" not in self.config:
            self.config["model_stats"] = {}
        
        # Set UI silent mode
        UI.SILENT_ERRORS = self.config.get("silent_errors", True)

    def _ensure_dir(self):
        if not os.path.exists(self.APP_DIR):
            os.makedirs(self.APP_DIR, exist_ok=True)

    def _load_config_safely(self):
        config = self.DEFAULT_CONFIG.copy()
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    
                    # Handle legacy configs
                    if "api_key" in loaded and "gemini_api_key" not in loaded:
                        loaded["gemini_api_key"] = loaded["api_key"]
                    
                    for key, value in loaded.items():
                        config[key] = value
            except Exception as e:
                self.log_error(f"Config reset due to corruption ({e})", silent=True)
        
        return config

    def _load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
            with open(self.error_path, 'w', encoding='utf-8') as f:
                json.dump(self.error_log[-100:], f, indent=2)
        except Exception as e:
            self.log_error(f"Failed to save state: {e}", silent=True)

    def log(self, message, level="INFO", model=None):
        try:
            timestamp = datetime.now().isoformat()
            model_tag = f" [{model}]" if model else ""
            entry = f"[{timestamp}]{model_tag} [{level}] {message}\n"
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(entry)
        except:
            pass

    def log_error(self, error_message, context="", silent=True):
        """Log error internally without showing user"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error_message),
            "context": context,
            "silent": silent
        }
        self.error_log.append(error_entry)
        
        # Also log to system log
        self.log(f"ERROR: {error_message} [{context}]", "ERROR")
        
        # Save errors periodically
        if len(self.error_log) % 10 == 0:
            self.save()
    
    def track_installation(self, package, manager, success=True):
        """Track package installation attempts"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "package": package,
            "manager": manager,
            "success": success
        }
        
        if success:
            if package not in self.config.get("installed_packages", []):
                self.config.setdefault("installed_packages", []).append(package)
        
        self.config.setdefault("installation_history", []).append(entry)
        self.save()
    
    def is_package_installed(self, package):
        """Check if package was previously installed"""
        return package in self.config.get("installed_packages", [])

    def update_model_stat(self, model_name, success=True, tokens_used=0):
        """Update statistics for a model"""
        if model_name not in self.config["model_stats"]:
            self.config["model_stats"][model_name] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "tokens_used": 0,
                "last_used": datetime.now().isoformat()
            }
        
        stats = self.config["model_stats"][model_name]
        stats["requests"] += 1
        stats["tokens_used"] += tokens_used
        stats["last_used"] = datetime.now().isoformat()
        
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        
        self.save()

    def get_available_engines(self):
        """Return list of available AI engines"""
        available = []
        for engine, is_available in AI_ENGINES.items():
            if is_available:
                if engine == "gemini" and self.config.get("gemini_api_key"):
                    available.append(engine)
                elif engine == "deepseek" and self.config.get("deepseek_api_key"):
                    available.append(engine)
                elif engine == "groq" and self.config.get("groq_api_key"):
                    available.append(engine)
        return available

    def switch_engine(self, engine_name):
        """Switch active AI engine"""
        if engine_name in AI_ENGINES and AI_ENGINES[engine_name]:
            if engine_name == "gemini" and not self.config.get("gemini_api_key"):
                return False, "Gemini API key not configured"
            elif engine_name == "deepseek" and not self.config.get("deepseek_api_key"):
                return False, "DeepSeek API key not configured"
            elif engine_name == "groq" and not self.config.get("groq_api_key"):
                return False, "Groq API key not configured"
            
            self.config["active_engine"] = engine_name
            self.save()
            return True, f"Switched to {engine_name.upper()}"
        return False, f"Engine {engine_name} not available"

    def update_workspace(self, path):
        try:
            abs_path = os.path.abspath(os.path.expanduser(path))
            if os.path.exists(abs_path):
                self.config["workspace"] = abs_path
                self.save()
                return True, abs_path
        except Exception as e:
            self.log_error(f"Workspace update failed: {e}", path, silent=True)
        return False, path
# ==============================================================================
# CHAT MANAGEMENT SYSTEM WITH CHAT IDs
# ==============================================================================

class ChatSession:
    """Represents a single chat session with ID and metadata"""
    
    def __init__(self, chat_id=None, title="New Chat", created_at=None):
        self.chat_id = chat_id or self.generate_chat_id()
        self.title = title
        self.created_at = created_at or datetime.now().isoformat()
        self.last_activity = datetime.now().isoformat()
        self.messages = []  # List of {"role": "user/model", "parts": [message]}
        self.file_path = None
        
    @staticmethod
    def generate_chat_id():
        """Generate a unique chat ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        return f"chat_{timestamp}_{random_suffix}"
    
    def to_dict(self):
        """Convert chat session to dictionary for serialization"""
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create chat session from dictionary"""
        chat = cls(
            chat_id=data.get("chat_id"),
            title=data.get("title", "Untitled"),
            created_at=data.get("created_at")
        )
        chat.last_activity = data.get("last_activity", chat.created_at)
        chat.messages = data.get("messages", [])
        return chat
    
    def add_message(self, role, content):
        """Add a message to the chat"""
        self.messages.append({
            "role": role,
            "parts": [content],
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now().isoformat()
        
        if self.title == "New Chat" and role == "user":
            words = content.split()[:5]
            self.title = " ".join(words)[:30]
            if len(content) > 30:
                self.title += "..."
    
    def get_messages_for_ai(self, limit=20):
        return [{"role": msg["role"], "parts": msg["parts"]} 
                for msg in self.messages[-limit:]]
    
    def get_summary(self):
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages)
        }


class ChatManager:
    """Manages chat sessions with persistent storage"""
    
    def __init__(self, persistence: PersistenceLayer):
        self.store = persistence
        self.chats_file = os.path.join(persistence.APP_DIR, "chats.json")
        self.sessions = {}
        self.current_chat_id = None
        self._load_chats()
        
    def _load_chats(self):
        try:
            if os.path.exists(self.chats_file):
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for chat_data in data.get("chats", []):
                    chat = ChatSession.from_dict(chat_data)
                    self.sessions[chat.chat_id] = chat
                    
                self.current_chat_id = data.get("current_chat_id")
                
                if self.current_chat_id not in self.sessions:
                    self.create_new_chat()
        except Exception as e:
            self.store.log_error(f"Failed to load chats: {e}", "chat_manager", silent=True)
            self.create_new_chat()
    
    def save_chats(self):
        try:
            data = {
                "current_chat_id": self.current_chat_id,
                "chats": [chat.to_dict() for chat in self.sessions.values()]
            }
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.store.log_error(f"Failed to save chats: {e}", "chat_manager", silent=True)
    
    def create_new_chat(self):
        chat = ChatSession()
        self.sessions[chat.chat_id] = chat
        self.current_chat_id = chat.chat_id
        self.save_chats()
        self.store.log(f"Created new chat: {chat.chat_id}", "INFO")
        return chat
    
    def switch_to_chat(self, chat_id):
        if chat_id in self.sessions:
            self.current_chat_id = chat_id
            self.save_chats()
            return True, self.sessions[chat_id]
        return False, f"Chat not found: {chat_id}"
    
    def get_current_chat(self):
        if self.current_chat_id in self.sessions:
            return self.sessions[self.current_chat_id]
        return self.create_new_chat()
    
    def list_chats(self, limit=20):
        chats = list(self.sessions.values())
        chats.sort(key=lambda x: x.last_activity, reverse=True)
        return chats[:limit]
    
    def rename_chat(self, chat_id, new_title):
        if chat_id in self.sessions:
            self.sessions[chat_id].title = new_title[:50]
            self.save_chats()
            return True, f"Chat renamed to: {new_title}"
        return False, f"Chat not found: {chat_id}"
    
    def delete_chat(self, chat_id):
        if chat_id in self.sessions:
            if chat_id == self.current_chat_id:
                return False, "Cannot delete current chat."
            del self.sessions[chat_id]
            self.save_chats()
            return True, "Chat deleted"
        return False, "Chat not found"
    
    def add_message_to_current(self, role, content):
        chat = self.get_current_chat()
        chat.add_message(role, content)
        self.save_chats()
        return chat
    
    def clear_current_chat(self):
        chat = self.get_current_chat()
        chat.messages = []
        self.save_chats()
        return True, "Chat cleared"
    
    def export_chat(self, chat_id, format="json"):
        if chat_id not in self.sessions:
            return False, "Chat not found"
        chat = self.sessions[chat_id]
        if format == "json":
            file = f"chat_export_{chat_id}.json"
            with open(file, "w", encoding="utf-8") as f:
                json.dump(chat.to_dict(), f, indent=2, ensure_ascii=False)
            return True, file
        elif format == "txt":
            file = f"chat_export_{chat_id}.txt"
            with open(file, "w", encoding="utf-8") as f:
                for msg in chat.messages:
                    f.write(f"{msg['role']}: {msg['parts'][0]}\n\n")
            return True, file
        return False, "Unsupported format"

# ==============================================================================
# 3. FILE SYSTEM & WORKSPACE
# ==============================================================================

class WorkspaceManager:
    """Handles all file operations safely with deep analysis capabilities."""
    
    def __init__(self, persistence: PersistenceLayer):
        self.store = persistence
        initial_ws = self.store.config.get("workspace", os.getcwd())
        if os.path.exists(initial_ws):
            os.chdir(initial_ws)
        else:
            self.store.update_workspace(os.getcwd())

    def get_current_path(self):
        return os.getcwd()

    def detect_tech_stack(self):
        files = set(os.listdir(os.getcwd()))
        stack = []
        
        if 'package.json' in files: stack.append("Node.js")
        if 'requirements.txt' in files: stack.append("Python")
        if 'pyproject.toml' in files: stack.append("Python (Poetry/Flit)")
        if 'docker-compose.yml' in files: stack.append("Docker")
        if '.git' in files: stack.append("Git")
        if any(f.endswith('.py') for f in files): stack.append("Python Files")
        if any(f.endswith('.js') for f in files): stack.append("JavaScript")
        
        if not stack: return "Empty/Generic Directory"
        return ", ".join(stack)

    def analyze_project(self):
        """Deep analysis of project structure"""
        analysis = {
            "total_files": 0,
            "file_types": {},
            "entry_points": [],
            "config_files": []
        }
        
        try:
            for root, dirs, files in os.walk(os.getcwd()):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'): continue
                    
                    analysis["total_files"] += 1
                    
                    ext = os.path.splitext(file)[1]
                    if ext:
                        analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                    
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.getcwd())
                    
                    if file in {'main.py', 'app.py', 'index.js', 'server.js'}:
                        analysis["entry_points"].append(rel_path)
                    elif file in {'package.json', 'requirements.txt', 'docker-compose.yml'}:
                        analysis["config_files"].append(rel_path)
        except Exception as e:
            self.store.log_error(f"Project analysis error: {e}", "workspace", silent=True)
        
        return analysis

    def read_file_with_context(self, file_path, lines_around=3):
        """Read file with surrounding context"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            context = ""
            for i, line in enumerate(lines):
                context += f"{i+1:4}: {line}"
            
            return context, len(lines)
        except:
            return "", 0

    def list_files(self, recursive=False, limit=50):
        ignore_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.idea', '.vscode'}
        file_list = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(os.getcwd()):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for file in files:
                        if file.startswith('.'): continue
                        rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                        file_list.append(rel_path)
                        if len(file_list) >= limit: break
                    if len(file_list) >= limit: break
            else:
                for item in os.listdir(os.getcwd()):
                    if item.startswith('.'): continue
                    if item in ignore_dirs: continue
                    file_list.append(item)
                    if len(file_list) >= limit: break
        except Exception as e:
            self.store.log_error(f"File listing error: {e}", "workspace", silent=True)
            return []
            
        return file_list

    def read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.store.log_error(f"Failed to read file {path}: {e}", "workspace", silent=True)
            return ""

    def write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            self.store.log_error(f"Write failed for {path}: {e}", "workspace", silent=True)
            return str(e)

    def delete_file(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception as e:
            self.store.log_error(f"Delete failed for {path}: {e}", "workspace", silent=True)
            return False
        return False

# ==============================================================================
# 4. SILENT AI ENGINES
# ==============================================================================

class BaseAIEngine:
    """Base class for all AI engines with silent error handling"""
    
    def __init__(self, persistence: PersistenceLayer):
        self.store = persistence
        self.engine_name = "base"
        self.model_name = ""
        self._configured = False
        
    def _configure_api(self):
        pass
        
    def generate_content(self, prompt, retries=3):
        """Generate content with silent error handling"""
        for attempt in range(retries):
            try:
                result = self._unsafe_generate(prompt)
                if result:
                    tokens_used = len(result.split()) * 1.3
                    self.store.update_model_stat(f"{self.engine_name}:{self.model_name}", True, int(tokens_used))
                return result
            except Exception as e:
                error_msg = str(e)
                self.store.log_error(f"{self.engine_name} error (attempt {attempt+1}): {error_msg}", prompt[:100], silent=True)
                
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
        
        self.store.update_model_stat(f"{self.engine_name}:{self.model_name}", False, 0)
        return None
        
    def _unsafe_generate(self, prompt):
        """To be implemented by subclasses"""
        pass
        
    def chat(self, user_msg, history):
        """Chat with silent error handling"""
        try:
            return self._unsafe_chat(user_msg, history)
        except Exception as e:
            self.store.log_error(f"{self.engine_name} chat error: {e}", user_msg[:50], silent=True)
            self.store.update_model_stat(f"{self.engine_name}:{self.model_name}", False, 0)
            return f"⚠️ {self.engine_name} is temporarily unavailable.", self.engine_name
        
    def _unsafe_chat(self, user_msg, history):
        """To be implemented by subclasses"""
        pass
        
    def get_fix_for_error(self, cmd, error_output):
        """Get fix with silent error handling"""
        try:
            return self._unsafe_get_fix(cmd, error_output)
        except Exception as e:
            self.store.log_error(f"{self.engine_name} fix error: {e}", cmd, silent=True)
            return None
    
    def _unsafe_get_fix(self, cmd, error_output):
        """To be implemented by subclasses"""
        pass

class GeminiEngine(BaseAIEngine):
    """Gemini AI Engine with silent error handling"""
    
    def __init__(self, persistence: PersistenceLayer):
        super().__init__(persistence)
        self.engine_name = "gemini"
        self.model_name = persistence.config.get("model", "gemini-2.5-flash-lite")
        self._configure_api()
        
    def _configure_api(self):
        if not AI_ENGINES.get('gemini', False):
            raise ImportError("google-generativeai not installed")
            
        key = self.store.config.get("gemini_api_key")
        while not key and not UI.GHOST_MODE:
            UI.print_system("Gemini Authentication Required")
            key = input("🔑 Please paste your Gemini API Key: ").strip()
            self.store.config["gemini_api_key"] = key
            self.store.save()
        
        if key:
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel(self.model_name)
            self._configured = True
        
    def _unsafe_generate(self, prompt):
        if not self._configured:
            return None
            
        response = self.model.generate_content(prompt)
        return response.text
        
    def _unsafe_chat(self, user_msg, history):
        if not self._configured:
            return "Gemini engine not configured.", "gemini"
            
        chat_session = self.model.start_chat(history=history)
        response = chat_session.send_message(user_msg)
        text = response.text
        
        tokens_used = len(text.split()) * 1.3
        self.store.update_model_stat(f"gemini:{self.model_name}", True, int(tokens_used))
        return text, "gemini"
            
    def _unsafe_get_fix(self, cmd, error_output):
        prompt = f"""
        Command Failed: `{cmd}`
        Error: {error_output[:500]}
        
        Analyze if this is a missing package/command error.
        If yes, provide the exact package installation command.
        
        Examples:
        - If 'npm' not found: 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs'
        - If 'python3' not found: 'sudo apt update && sudo apt install python3'
        - If package missing: 'pip install package_name' or 'npm install package_name'
        
        Provide ONLY the installation command if needed, or "NO_PACKAGE_FIX" if not.
        """
        fix = self._unsafe_generate(prompt)
        return fix.strip() if fix and "NO_PACKAGE_FIX" not in fix.upper() else None

class DeepSeekEngine(BaseAIEngine):
    """DeepSeek AI Engine with silent error handling"""
    
    def __init__(self, persistence: PersistenceLayer):
        super().__init__(persistence)
        self.engine_name = "deepseek"
        self.model_name = persistence.config.get("deepseek_model", "deepseek-reasoner")
        self._configured = False
        self.balance_checked = False
        self.balance_available = True
        self._configure_api()
        
    def _configure_api(self):
        if not AI_ENGINES.get('deepseek', False):
            raise ImportError("openai not installed")
            
        key = self.store.config.get("deepseek_api_key")
        while not key and not UI.GHOST_MODE:
            UI.print_system("DeepSeek Authentication Required")
            key = input("🔑 Please paste your DeepSeek API Key: ").strip()
            self.store.config["deepseek_api_key"] = key
            self.store.save()
        
        if key:
            self.client = OpenAI(
                api_key=key,
                base_url="https://api.deepseek.com"
            )
            self._configured = True
                
    def check_balance(self):
        """Check DeepSeek account balance silently"""
        try:
            test_prompt = "Hello"
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=5
            )
            self.balance_available = True
            self.balance_checked = True
            return True
        except Exception as e:
            error_msg = str(e)
            if "402" in error_msg or "Insufficient Balance" in error_msg:
                self.balance_available = False
                self.balance_checked = True
                return False
            elif "401" in error_msg:
                self.store.log_error("DeepSeek API Key invalid or expired.", "balance_check", silent=True)
                self.balance_available = False
                return False
            else:
                self.balance_available = True
                return True
                
    def _unsafe_generate(self, prompt):
        if not self._configured:
            return None
            
        if not self.balance_checked:
            if not self.check_balance():
                self.store.log_error("DeepSeek: Insufficient Balance", "generate", silent=True)
                return None
        
        if not self.balance_available:
            self.store.log_error("DeepSeek: Insufficient Balance", "generate", silent=True)
            return None
            
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.store.config.get("max_tokens", 8192)
        )
        
        return response.choices[0].message.content
        
    def _unsafe_chat(self, user_msg, history):
        if not self._configured:
            return "DeepSeek engine not configured.", "deepseek"
            
        if not self.balance_checked:
            if not self.check_balance():
                error_msg = "❌ DeepSeek: Insufficient Balance"
                self.store.log_error(error_msg, "chat", silent=True)
                return error_msg, "deepseek"
        
        if not self.balance_available:
            error_msg = "❌ DeepSeek: Insufficient Balance"
            return error_msg, "deepseek"
            
        messages = []
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("parts", [""])[0]})
        
        messages.append({"role": "user", "content": user_msg})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.store.config.get("max_tokens", 8192)
        )
        
        text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else len(text.split()) * 1.3
        self.store.update_model_stat(f"deepseek:{self.model_name}", True, int(tokens_used))
        return text, "deepseek"
            
    def _unsafe_get_fix(self, cmd, error_output):
        prompt = f"""
        Command Failed: `{cmd}`
        Error: {error_output[:500]}
        
        Analyze if this is a missing package/command error.
        If yes, provide the exact package installation command.
        
        Examples:
        - If 'npm' not found: 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs'
        - If 'python3' not found: 'sudo apt update && sudo apt install python3'
        - If package missing: 'pip install package_name' or 'npm install package_name'
        
        Provide ONLY the installation command if needed, or "NO_PACKAGE_FIX" if not.
        """
        fix = self._unsafe_generate(prompt)
        return fix.strip() if fix and "NO_PACKAGE_FIX" not in fix.upper() else None

class GroqEngine(BaseAIEngine):
    """Groq AI Engine with silent error handling"""
    
    def __init__(self, persistence: PersistenceLayer):
        super().__init__(persistence)
        self.engine_name = "groq"
        self.model_name = persistence.config.get("groq_model", "mixtral-8x7b-32768")
        self._configured = False
        self._configure_api()
        
    def _configure_api(self):
        if not AI_ENGINES.get('groq', False):
            raise ImportError("groq library not installed")
            
        key = self.store.config.get("groq_api_key")
        while not key and not UI.GHOST_MODE:
            UI.print_system("Groq Authentication Required")
            key = input("🔑 Please paste your Groq API Key: ").strip()
            self.store.config["groq_api_key"] = key
            self.store.save()
        
        if key:
            try:
                self.client = groq.Groq(api_key=key)
                self._configured = True
            except Exception as e:
                self.store.log_error(f"Failed to initialize Groq client: {e}", "config", silent=True)
                raise
        
    def _unsafe_generate(self, prompt):
        if not self._configured:
            return None
            
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.store.config.get("temperature", 0.7),
            max_tokens=self.store.config.get("max_tokens", 8192),
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
        
    def _unsafe_chat(self, user_msg, history):
        if not self._configured:
            return "Groq engine not configured.", "groq"
            
        messages = []
        
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("parts", [""])[0]})
        
        messages.append({"role": "user", "content": user_msg})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.store.config.get("temperature", 0.7),
            max_tokens=self.store.config.get("max_tokens", 8192),
            top_p=1,
            stream=False
        )
        
        text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else len(text.split()) * 1.3
        self.store.update_model_stat(f"groq:{self.model_name}", True, int(tokens_used))
        return text, "groq"
            
    def _unsafe_get_fix(self, cmd, error_output):
        prompt = f"""
        Command Failed: `{cmd}`
        Error: {error_output[:500]}
        
        Analyze if this is a missing package/command error.
        If yes, provide the exact package installation command.
        
        Examples:
        - If 'npm' not found: 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs'
        - If 'python3' not found: 'sudo apt update && sudo apt install python3'
        - If package missing: 'pip install package_name' or 'npm install package_name'
        
        Provide ONLY the installation command if needed, or "NO_PACKAGE_FIX" if not.
        """
        fix = self._unsafe_generate(prompt)
        return fix.strip() if fix and "NO_PACKAGE_FIX" not in fix.upper() else None
        
    def get_available_models(self):
        """Get list of available Groq models"""
        available_models = [
            "mixtral-8x7b-32768",
            "llama2-70b-4096",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "gemma-7b-it",
        ]
        return available_models

class MultiAIEngine:
    """Manages multiple AI engines with fallback support and silent error handling"""
    
    def __init__(self, persistence: PersistenceLayer):
        self.store = persistence
        self.engines = {}
        self.active_engine_name = persistence.config.get("active_engine", "groq")
        self._init_engines()
        self.fallback_order = self._determine_fallback_order()
        
    def _determine_fallback_order(self):
        """Determine smart fallback order based on availability and balance"""
        order = []
        
        if 'groq' in self.engines:
            order.append('groq')
        
        if 'gemini' in self.engines:
            order.append('gemini')
        
        if 'deepseek' in self.engines:
            deepseek_engine = self.engines['deepseek']
            if not deepseek_engine.balance_checked:
                if deepseek_engine.check_balance():
                    order.append('deepseek')
            elif deepseek_engine.balance_available:
                order.append('deepseek')
        
        return order
    
    def _init_engines(self):
        """Initialize all available engines"""
        if AI_ENGINES.get('groq', False):
            try:
                self.engines['groq'] = GroqEngine(self.store)
                UI.print_success(f"✓ Groq engine loaded: {self.engines['groq'].model_name}", silent=True)
                if not self.active_engine_name or self.active_engine_name not in self.engines:
                    self.active_engine_name = 'groq'
                    self.store.config["active_engine"] = 'groq'
            except Exception as e:
                self.store.log_error(f"Failed to load Groq: {e}", "engine_init", silent=True)
                
        if AI_ENGINES.get('gemini', False):
            try:
                self.engines['gemini'] = GeminiEngine(self.store)
                UI.print_success(f"✓ Gemini engine loaded: {self.engines['gemini'].model_name}", silent=True)
            except Exception as e:
                self.store.log_error(f"Failed to load Gemini: {e}", "engine_init", silent=True)
                
        if AI_ENGINES.get('deepseek', False):
            try:
                self.engines['deepseek'] = DeepSeekEngine(self.store)
                UI.print_success(f"✓ DeepSeek engine loaded: {self.engines['deepseek'].model_name}", silent=True)
            except Exception as e:
                self.store.log_error(f"Failed to load DeepSeek: {e}", "engine_init", silent=True)
                
        if not self.engines:
            if not UI.SILENT_ERRORS:
                UI.print_warning("⚠️ No AI engines available. Please install dependencies.")
    
    def get_active_engine(self):
        """Get the currently active engine"""
        return self.engines.get(self.active_engine_name)
            
    def switch_engine(self, engine_name):
        """Switch active engine"""
        if engine_name in self.engines:
            self.active_engine_name = engine_name
            self.store.config["active_engine"] = engine_name
            self.store.save()
            return True, f"Switched to {engine_name.upper()}"
        return False, f"Engine {engine_name} not available"
        
    def get_engine(self, engine_name):
        """Get specific engine by name"""
        return self.engines.get(engine_name)
        
    def generate_content(self, prompt, retries=3, force_engine=None):
        """Generate content with intelligent fallback support and silent error handling"""
        if force_engine and force_engine in self.engines:
            engine = self.engines[force_engine]
            if engine.engine_name == 'deepseek' and not engine.balance_available:
                self.store.log_error(f"DeepSeek has insufficient balance", "generate", silent=True)
            else:
                result = engine.generate_content(prompt, retries)
                if result:
                    return result, engine.engine_name
        
        engine = self.get_active_engine()
        if engine:
            if engine.engine_name == 'deepseek' and not engine.balance_available:
                self.store.log_error(f"DeepSeek has insufficient balance", "generate", silent=True)
            else:
                result = engine.generate_content(prompt, retries)
                if result:
                    return result, engine.engine_name
                
        if self.store.config.get("fallback_enabled", True):
            self.fallback_order = self._determine_fallback_order()
            
            for engine_name in self.fallback_order:
                if engine_name != self.active_engine_name:
                    fallback_engine = self.engines[engine_name]
                    
                    if engine_name == 'deepseek' and not fallback_engine.balance_available:
                        continue
                        
                    if not UI.GHOST_MODE:
                        UI.update_progress(f"Trying {engine_name.upper()}...")
                    
                    result = fallback_engine.generate_content(prompt, retries)
                    if result:
                        self.switch_engine(engine_name)
                        if not UI.GHOST_MODE:
                            UI.update_progress(f"Auto-switched to {engine_name.upper()}")
                            time.sleep(0.5)
                        return result, fallback_engine.engine_name
                        
        return None, None
        
    def chat(self, user_msg, history):
        """Chat with active engine"""
        engine = self.get_active_engine()
        if engine:
            return engine.chat(user_msg, history)
        return "No AI engine available.", None
        
    def get_fix_for_error(self, cmd, error_output):
        """Get fix with active engine"""
        engine = self.get_active_engine()
        if engine:
            return engine.get_fix_for_error(cmd, error_output)
        return None

# ==============================================================================
# 5. ENHANCED AGENT BRAIN WITH DEEP THINKING
# ==============================================================================

class AgentBrain:
    """The intelligence layer that decides WHAT to do using AI, not Keywords."""
    
    def __init__(self, ai: MultiAIEngine, workspace: WorkspaceManager):
        self.ai = ai
        self.ws = workspace
        self.last_model_used = None
        self.thinking_steps = [
            "Analyzing task requirements...",
            "Examining project structure...",
            "Reading relevant files...",
            "Understanding dependencies...",
            "Formulating optimal approach...",
            "Creating detailed plan..."
        ]

    def deep_router(self, prompt):
        if len(prompt.strip()) < 3: return "CHAT"
        
        sys_prompt = f"""
                    You are a STRICT Intent Classifier for a developer assistant.

                    Your task:
                    Classify the user's input into EXACTLY ONE category based on INTENT, not wording.

                    CATEGORIES:

                    1. CHAT
                    - Casual conversation, greetings, opinions, or non-technical talk.
                    - No request to explain, build, fix, or run anything.
                    - Examples:
                    "hello"
                    "thanks"
                    "احسن لغة ايه؟"

                    2. QUESTION
                    - Asking for explanations, concepts, comparisons, or how something works.
                    - NO request to execute, install, modify, or create anything.
                    - Examples:
                    "what is JWT?"
                    "explain REST vs GraphQL"
                    "npm بيشتغل ازاي؟"

                    3. MODIFY_PROJECT
                    - Requests to CHANGE or UPDATE an EXISTING project or codebase.
                    - Mentions current files, code, structure, or features to modify.
                    - Examples:
                    "add auth to my app"
                    "update package.json"
                    "refactor this function"

                    4. CREATE_PROJECT
                    - Requests to CREATE something NEW from scratch.
                    - Includes scaffolding, boilerplate, initialization, or full setup.
                    - Examples:
                    "create a Next.js app"
                    "start a FastAPI project"
                    "generate a CLI tool"

                    5. DEBUG
                    - Fixing errors, crashes, failed commands, or unexpected behavior.
                    - Includes error messages, logs, stack traces, or words like:
                    error, failed, not working, crash.
                    - Examples:
                    "npm install failed"
                    "this command gives error"
                    "fix this bug"

                    6. RUN_ONLY
                    - Requests whose PRIMARY intent is to EXECUTE, INSTALL, DOWNLOAD, START, STOP, or RUN something.
                    - Even if written in natural language, slang, or Arabic.
                    - NO explanation requested.
                    - NO code modification or project creation.
                    - The expected response is a SHELL COMMAND ONLY.

                    Examples that MUST be classified as RUN_ONLY:
                    
                    - "install node"
                    - "حملي npm"
                    - "نزل git"
                    - "عاوز انزل docker"
                    - "شغل السيرفر"
                    - "run tests"
                    - "start redis"
                    - "وقف الكونتينر"
                    - "update node version"
                    - "ثبت الباكج بتاع fastapi"

                    IMPORTANT DISTINCTION:
                    - If the user wants an explanation → QUESTION
                    - If the user wants execution or installation → RUN_ONLY
                    - If the user wants to fix a failure → DEBUG
                    - If the user wants to build something new → CREATE_PROJECT
                    - If the user wants to change existing code → MODIFY_PROJECT

                    PRIORITY RULES (STRICT ORDER):
                    1. If input contains an ERROR, FAILURE, or crash → DEBUG
                    2. If input requests changing existing code/files → MODIFY_PROJECT
                    3. If input requests creating a new project → CREATE_PROJECT
                    4. If input requests installing, downloading, running, starting, stopping anything → RUN_ONLY
                    5. If input is informational only → QUESTION
                    6. Otherwise → CHAT

                    OUTPUT RULES:
                    - Output ONLY ONE category name.
                    - NO explanations.
                    - NO punctuation.
                    - NO extra text.
                    - Output must be EXACTLY one of:
                        CHAT
                        QUESTION
                        MODIFY_PROJECT
                        CREATE_PROJECT
                        DEBUG
                        RUN_ONLY
                    
                    User Input:
                    "{prompt}"
                    """

        result, model_name = self.ai.generate_content(sys_prompt)
        self.last_model_used = model_name
        return result.strip().upper() if result else "CHAT"

    def detect_intent(self, prompt):
        intent = self.deep_router(prompt)
        if intent in ['MODIFY_PROJECT', 'CREATE_PROJECT', 'DEBUG', 'RUN_ONLY']:
            return "AGENT"
        return "CHAT"

    def create_plan(self, task_description):
        """Enhanced planning with deep analysis"""
        if not UI.GHOST_MODE:
            for step in self.thinking_steps:
                UI.update_progress(step)
                time.sleep(0.3)
        
        files = self.ws.list_files(recursive=True, limit=30)
        files_str = "\n".join(files[:15]) if files else "(Empty Directory)"
        tech_stack = self.ws.detect_tech_stack()
        project_analysis = self.ws.analyze_project()
        
        prompt = f"""
        Role: Senior DevOps & Software Architect.
        
        TASK: {task_description}
        
        PROJECT CONTEXT (Deep Analysis):
        - Tech Stack: {tech_stack}
        - Total Files: {project_analysis['total_files']}
        - Entry Points: {project_analysis['entry_points']}
        - Config Files: {project_analysis['config_files']}
        - File Types: {', '.join([f'{k}: {v}' for k, v in project_analysis['file_types'].items()][:5])}
        
        CURRENT WORKSPACE FILES (Top 15):
        {files_str}
        
        Goal: Create a detailed Step-by-Step execution plan with DEEP ANALYSIS.
        
        Requirements:
        1. Assign a Confidence Score (0-100) with justification.
        2. Analyze the risk (Low, Medium, High) with explanation.
        3. Provide DEEP TECHNICAL ANALYSIS of the approach.
        4. List any DEPENDENCIES required.
        5. Offer a 'suggestion' (AI-as-a-Teammate) for architecture improvements.
        6. Provide steps with actions: CREATE, MODIFY, DELETE, COMMAND, ANALYZE.
        7. For each step, include REASONING explaining why it's necessary.
        
        Constraint: Return ONLY a valid JSON object.
        
        JSON Format Example:
        {{
            "confidence": 92,
            "confidence_reason": "Task is straightforward and matches existing patterns in the project",
            "risk": "Low",
            "risk_reason": "Only modifies configuration files, no core logic changes",
            "analysis": "This task requires adding a new endpoint to the existing API. The project uses Flask framework and follows MVC pattern. Need to create model, view, and controller components.",
            "dependencies": ["flask", "sqlalchemy"],
            "suggestion": "Consider adding input validation and error handling to the new endpoint.",
            "steps": [
                {{
                    "action": "analyze",
                    "target": "app.py",
                    "description": "Review main application structure",
                    "reasoning": "Need to understand the current Flask app structure before adding new endpoints"
                }},
                {{
                    "action": "create",
                    "path": "models/new_model.py",
                    "description": "Create new database model",
                    "reasoning": "Required for the new feature's data structure"
                }},
                {{
                    "action": "modify",
                    "path": "app.py",
                    "description": "Add new route endpoint",
                    "reasoning": "Main application file needs the new route definition"
                }},
                {{
                    "action": "command",
                    "command": "pip install flask sqlalchemy",
                    "description": "Install required dependencies",
                    "reasoning": "These packages are needed for the new functionality"
                }}
            ]
        }}
        """
        
        response, model_name = self.ai.generate_content(prompt)
        self.last_model_used = model_name
        
        if not response: return None, None
        
        clean_json = response.replace('```json', '').replace('```', '').strip()
        try:
            plan_data = json.loads(clean_json)
            if 'steps' not in plan_data: return None, None
            
            if 'analysis' not in plan_data:
                plan_data['analysis'] = "No detailed analysis provided."
            if 'dependencies' not in plan_data:
                plan_data['dependencies'] = []
            if 'confidence_reason' not in plan_data:
                plan_data['confidence_reason'] = "Based on AI analysis of task complexity and project context."
            if 'risk_reason' not in plan_data:
                plan_data['risk_reason'] = "Standard risk assessment based on file modification scope."
            
            return plan_data, model_name
        except json.JSONDecodeError as e:
            self.ai.store.log_error(f"Failed to parse AI plan: {e}", clean_json[:200], silent=True)
            return None, None
    def detect_installation_request(self, prompt: str) -> tuple:
        """
        اكتشاف طلبات التثبيت/التحميل من وصف المستخدم
        Returns: (package_name, package_manager, is_global)
        """
        prompt_lower = prompt.lower()
        
        # أنماط للكلمات الدالة (باللغتين العربية والإنجليزية)
        install_patterns = [
            'download', 'install', 'get', 'setup', 'fetch', 'pull',
            'تحميل', 'نزّل', 'نزل', 'حمّل', 'حملي', 'ثبّت', 'شغّل', 
            'شغلي', 'عاوز', 'أريد', 'ابغى', 'نبي', 'محتاج', 'احتاج',
            'setup', 'configure', 'configure', 'run', 'start'
        ]
        
        # تحقق إذا كان الطلب عن تثبيت
        is_install_request = any(pattern in prompt_lower for pattern in install_patterns)
        
        if not is_install_request:
            return None, None, False
        
        # اكتشاف نظام التشغيل المذكور
        os_keywords = {
            'windows': ['windows', 'win', 'ويندوز', 'ويندو'],
            'linux': ['linux', 'ubuntu', 'debian', 'لينكس', 'يوبنتو'],
            'mac': ['mac', 'macos', 'apple', 'ماك', 'مَاك']
        }
        
        # اكتشاف مدير الحزم بناءً على السياق
        managers = {
                # Node.js / JavaScript
                'npm': [
                    'npm', 'node', 'nodejs', 'node.js',
                    'نود', 'نودجيس', 'نودجي اس', 'نود جي اس'
                ],
                'windowsterminal': [
                    'windowsterminal', 'windowsterminal', 'windowsterminal', 'windowsterminal',
                    'wt', 'windowsterminal', 'windowsterminal', 'windowsterminal'
                ],
                'yarn': [
                    'yarn', 'يارن'
                ],
                'pnpm': [
                    'pnpm', 'بي ان بي ام'
                ],

                # Python
                'pip': [
                    'pip', 'pip3', 'python', 'python3',
                    'بايثون', 'بايب', 'بايب3'
                ],
                'conda': [
                    'conda', 'anaconda', 'miniconda',
                    'كوندا', 'اناكوندا'
                ],
                'poetry': [
                    'poetry', 'بوترى', 'بويتري'
                ],

                # Containers / DevOps
                'docker': [
                    'docker', 'docker-compose',
                    'دوكر', 'كونتينر', 'حاوية'
                ],
                'kubectl': [
                    'kubectl', 'kubernetes', 'k8s',
                    'كيوب', 'كيوبرنيتس'
                ],
                'helm': [
                    'helm', 'هيلم'
                ],

                # Version control
                'git': [
                    'git', 'github', 'gitlab',
                    'جيت', 'جيتهاب', 'ريبو', 'مستودع'
                ],

                # Linux package managers
                'apt': [
                    'apt', 'apt-get', 'ubuntu', 'debian',
                    'أبت', 'يوبنتو', 'ديبيان'
                ],
                'dnf': [
                    'dnf', 'fedora', 'redhat',
                    'فيدورا', 'ريد هات'
                ],
                'yum': [
                    'yum', 'centos',
                    'يام', 'سينت او اس'
                ],
                'pacman': [
                    'pacman', 'arch',
                    'باكمان', 'آرتش'
                ],
                'zypper': [
                    'zypper', 'opensuse',
                    'زيبر', 'سوزي'
                ],

                # macOS
                'brew': [
                    'brew', 'homebrew', 'macos', 'mac',
                    'برو', 'هوم برو', 'ماك'
                ],
                'port': [
                    'macports', 'port',
                    'ماك بورتس'
                ],

                # Windows
                'winget': [
                    'winget', 'windows', 'msstore',
                    'ويندوز', 'وينجت'
                ],
                'choco': [
                    'choco', 'chocolatey',
                    'شوكولاتي', 'تشوكو'
                ],
                'scoop': [
                    'scoop',
                    'سكوب'
                ],

                # Languages / Build tools
                'cargo': [
                    'cargo', 'rust',
                    'كارغو', 'راست'
                ],
                'go': [
                    'go', 'golang',
                    'جو', 'جولانج'
                ],
                'maven': [
                    'maven', 'java',
                    'مافن', 'جافا'
                ],
                'gradle': [
                    'gradle',
                    'جرادل'
                ],
                'composer': [
                    'composer', 'php',
                    'كومبوزر', 'بي اتش بي'
                ],
                'nuget': [
                    'nuget', '.net', 'dotnet',
                    'نيوجيت', 'دوت نت'
                ]
            }

        
        # اكتشاف الحزمة
        package_name = None
        detected_manager = None
        
        # أولاً: اكتشاف مدير الحزم المذكور
        for manager, keywords in managers.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    detected_manager = manager
                    break
            if detected_manager:
                break
        
        # ثانياً: اكتشاف الحزمة
        # قائمة بالحزم الشائعة
        common_packages = {
            'npm': ['npm', 'node', 'express', 'react', 'vue', 'angular'],
            'pip': ['pip', 'python', 'django', 'flask', 'tensorflow', 'pandas'],
            'docker': ['docker', 'docker-ce', 'docker-desktop'],
            'git': ['git', 'git-bash', 'git-for-windows'],
            'wt':["wt","windowsterminal"],
        }
        
        # بحث عن حزم معروفة
        if detected_manager and detected_manager in common_packages:
            for pkg in common_packages[detected_manager]:
                if pkg in prompt_lower:
                    package_name = pkg
                    break
        
        # إذا لم نجد حزمة معروفة، حاول استخراج الاسم
        if not package_name:
            # أنماط regex لاستخراج أسماء الحزم
            patterns = [
                r'(?:download|install|get|setup)\s+(?:the\s+)?([a-zA-Z0-9@\-\._]+)(?:\s+package|\s+tool|\s+for)?',
                r'([a-zA-Z0-9@\-\._]+)(?:\s+package|\s+library|\s+tool|\s+software)',
                r'package\s+([a-zA-Z0-9@\-\._]+)',
                r'تحميل\s+([^\s]+)',
                r'نزل\s+([^\s]+)',
                r'حمّل\s+([^\s]+)',
                r'install\s+([^\s]+)',
                r'download\s+([^\s]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    potential_package = match.group(1)
                    # تأكد أن هذا ليس مدير حزم
                    if potential_package not in managers.keys() and len(potential_package) > 1:
                        package_name = potential_package
                        break
            
            # إذا لم نتمكن من استخراج اسم الحزمة، لكن لدينا مدير، فربما المستخدم يريد تثبيت المدير نفسه
            if not package_name and detected_manager:
                # إذا كان الطلب عن تثبيت المدير نفسه (مثلاً "download npm")
                if detected_manager in prompt_lower:
                    package_name = detected_manager
        
        # تحديد إذا كان تثبيت عام
        is_global = any(word in prompt_lower for word in ['global', 'system', '-g', 'عام', 'على الجهاز', 'للجهاز'])
        
        return package_name, detected_manager, is_global
    def execute_code_generation(self, path, instruction, is_modification=False):
        """Enhanced code generation with context"""
        existing_code = self.ws.read_file(path)
        context = f"Existing File Content ({len(existing_code.splitlines())} lines):\n{existing_code}\n\n" if is_modification else "New File Creation.\n"

        prompt = f"""
        Role: Expert Coder.
        File: {path}
        Instruction: {instruction}
        
        {context}
        
        Requirements:
        1. Generate COMPLETE, WORKING code.
        2. Follow best practices and coding standards.
        3. Add comments for complex logic.
        4. Handle edge cases appropriately.
        5. Ensure code is well-structured and maintainable.
        
        Output: ONLY the complete code content. No markdown blocks, no explanations.
        """
        
        code, model_name = self.ai.generate_content(prompt)
        self.last_model_used = model_name
        
        if code:
            code = code.replace('```python', '').replace('```sh', '').replace('```', '').strip()
        return code, model_name

# ==============================================================================
# 6. MAIN APPLICATION WITH AUTO-INSTALLATION
# ==============================================================================

class TerminalApp:
    def __init__(self):

        self.persistence = PersistenceLayer()
        self.workspace = WorkspaceManager(self.persistence)
        self.ai = MultiAIEngine(self.persistence) if any(AI_ENGINES.values()) else None
        self.agent = AgentBrain(self.ai, self.workspace) if self.ai else None
        self.auto_mode = False
        self.package_manager = PackageManager()
        self.chat_manager = ChatManager(self.persistence)
        self.internal_commands = {
            'exit': self.do_exit, 'quit': self.do_exit, 'clear': self.do_clear,
            'cls': self.do_clear, 'help': self.do_help, 'workspace': self.do_workspace,
            'history': self.do_history, 'model': self.do_change_model, 
            'auto': self.do_toggle_auto, 'ghost': self.do_toggle_ghost,
            'replay': self.do_replay_last_task, 'engine': self.do_switch_engine,
            'engines': self.do_list_engines, 'stats': self.do_model_stats,
            'fallback': self.do_toggle_fallback, 'check_balance': self.do_check_balance,
            'groq_models': self.do_list_groq_models, 'silent': self.do_toggle_silent,
            'summary': self.do_show_summary,
            'chats': self.do_list_chats,
            'chat': self.do_switch_chat,
            'newchat': self.do_new_chat,
            'savechat': self.do_save_chat,
            'loadchat': self.do_load_chat,
            'renamechat': self.do_rename_chat,
            'deletechat': self.do_delete_chat,
            'exportchat': self.do_export_chat,
            'currentchat': self.do_current_chat,
            'clearchat': self.do_clear_chat,
        }

        self.fixed_terminal_commands = {
            'ls', 'dir', 'mkdir', 'rm', 'del', 'cp', 'mv', 
            'git', 'python', 'python3', 'pip', 'npm', 'node', 
            'docker', 'grep', 'cat', 'type', 'echo', 'ping', 
            'curl', 'wget', 'ps', 'kill', 'whoami', 'pwd'
        }

    def start(self):
        self.do_clear()
        import shutil
        
        columns = shutil.get_terminal_size().columns
        box_width = min(columns - 2, 90)
        title = "XEDA AGENT v9.3 - Happy New Year 2026 "
        subtitle = "Groq | Gemini | DeepSeek | Auto-Package Installation | Post-execution Summary"
        
        box_width = max(box_width, len(title) + 4)
        inner_width = box_width - 2
        
        print(f"{Color.CYAN}")
        print("╔" + "═" * inner_width + "╗")
        print(f"║{title.center(inner_width)}║")
        print("╚" + "═" * inner_width + "╝")
        print(f"{Color.DIM}{subtitle.center(box_width)}{Color.RESET}\n")
        
        self.do_list_engines(None)
        
        on = f"{Color.GREEN}[ON]{Color.RESET}"
        off = f"{Color.DIM}[OFF]{Color.RESET}"

        UI.print_system(f"Workspace   ▸ {self.workspace.get_current_path()}")
        UI.print_system(f"Silent      ▸ {on} 🔇" if UI.SILENT_ERRORS else f"Silent      ▸ {off}")
        UI.print_system(f"AutoInstall ▸ {on} 📦" if self.persistence.config.get('auto_install', True) else f"AutoInstall ▸ {off}")
        UI.print_system(f"AI routing  ▸ {Color.GREEN}[Active]{Color.RESET}")
        chat = self.chat_manager.get_current_chat()
        chat_display = chat.title
        if len(chat.messages) > 0:
            chat_display += f" ({len(chat.messages)} messages)"

        UI.print_system(f"Current Chat  ▸ {Color.GREEN}{chat_display}{Color.RESET}")
        UI.print_system(f"Chat ID       ▸ {Color.DIM}{chat.chat_id}{Color.RESET}")



        while True:
            try:
                auto_state = f"{Color.RED}[MANUAL]{Color.RESET}" if not self.auto_mode else f"{Color.GREEN}[AUTO]{Color.RESET}"
                ghost_state = f"{Color.DIM}[GHOST]{Color.RESET} " if UI.GHOST_MODE else ""
                silent_state = f"{Color.BLUE}[SILENT]{Color.RESET} " if UI.SILENT_ERRORS else ""
                
                if self.ai:
                    active_engine = self.ai.active_engine_name.upper()
                    if active_engine == "GEMINI":
                        engine_color = Color.GREEN
                    elif active_engine == "DEEPSEEK":
                        engine_color = Color.CYAN
                    elif active_engine == "GROQ":
                        engine_color = Color.YELLOW
                    else:
                        engine_color = Color.WHITE
                    engine_state = f"{engine_color}[{active_engine}]{Color.RESET} "
                else:
                    engine_state = ""
                    
                UI.clear_progress()
                
                print(f"\n{ghost_state}{silent_state}{engine_state}{auto_state} ", end="")
                
                user_input = UI.input_prompt(self.workspace.get_current_path())
                if not user_input: continue
                
                UI.update_progress("Processing...")
                self.process_input(user_input)
                
            except KeyboardInterrupt:
                UI.clear_progress()
                print("\n⏸️  Interrupted by User.") 
                continue
            except Exception as e:
                self.persistence.log_error(f"Critical Loop Error: {e}", "system", silent=True)
                UI.clear_progress()
                if not UI.SILENT_ERRORS:
                    UI.print_error(f"Critical Loop Error: {e}")

    def process_input(self, text):
        first_word = text.split()[0].lower() if text else ""

        if first_word in self.internal_commands:
            UI.clear_progress()
            self.internal_commands[first_word](text)
            return
            
        if first_word == "cd":
            self.handle_cd_command(text)
            return

        if first_word in self.fixed_terminal_commands:
            self.run_system_command(text)
            return

        if not self.agent or not self.ai:
            UI.update_progress("AI agent not available. Please install dependencies.")
            time.sleep(1)
            UI.clear_progress()
            return

        # الكشف التلقائي عن نية المستخدم
        intent = self.agent.deep_router(text)
        
        if intent == 'RUN_ONLY':
            # تحقق إذا كان هذا طلب تثبيت
            if self._looks_like_install_request(text):
                self.handle_installation_request(text)
            else:
                self.run_system_command(text)
        elif intent in ['MODIFY_PROJECT', 'CREATE_PROJECT', 'DEBUG']:
            UI.clear_progress()
            self.run_agent_workflow(text)
        else:
            # تحقق إذا كان طلب تثبيت حتى لو لم يكن RUN_ONLY
            if self._looks_like_install_request(text):
                self.handle_installation_request(text)
            else:
                UI.clear_progress()
                self.run_chat_mode(text)

    def _looks_like_install_request(self, text: str) -> bool:
        """تحقق بسيط إذا كان النص يبدو كطلب تثبيت"""
        text_lower = text.lower()
        
        install_keywords = [
            'download', 'install', 'get', 'setup',
            'تحميل', 'نزّل', 'نزل', 'حمّل', 'حملي', 'ثبّت',
            'شغّل', 'شغلي', 'عاوز', 'أريد', 'نبي'
        ]
        
        # تحقق إذا كان يحتوي على كلمة تثبيت + اسم حزمة/أداة
        has_install_word = any(word in text_lower for word in install_keywords)
        
        # قائمة بكلمات تشير إلى أدوات/حزم (يمكن توسيعها)
        tool_words = ['npm', 'node', 'python', 'rust', 'docker', 'git',
                    'package', 'tool', 'software', 'برنامج', 'أداة']
        
        has_tool_word = any(word in text_lower for word in tool_words)
        
        return has_install_word and has_tool_word
    def run_chat_mode(self, text):
        active_engine = self.ai.active_engine_name if self.ai else "N/A"
        
        chat = self.chat_manager.get_current_chat()
        chat.add_message("user", text)
        
        UI.update_progress("Thinking...")
        
        history = chat.get_messages_for_ai(limit=20)
        response, model_name = self.ai.chat(text, history)
        
        chat.add_message("model", response)
        self.chat_manager.save_chats()
        
        UI.clear_progress()
        UI.print_agent(response, model_name or active_engine)
        
        self.persistence.log(
            f"Chat: {chat.title} ({chat.chat_id}) - User: {text[:50]}...",
            "CHAT"
        )

    def run_agent_workflow(self, task):
        active_engine = self.ai.active_engine_name if self.ai else "N/A"
        UI.update_progress(f"🤔 Analyzing: {task[:50]}...")
        
        UI.clear_summary()
        
        plan_data, model_name = self.agent.create_plan(task)
        if not plan_data:
            UI.clear_progress()
            UI.print_error("❌ Failed to create plan", silent=True)
            return

        self.persistence.last_plan_cache = plan_data
        UI.clear_progress()
        
        if UI.SILENT_ERRORS or UI.GHOST_MODE:
            steps = plan_data.get('steps', [])
            print(f"\n{Color.CYAN}📋 Plan Summary: {len(steps)} steps{Color.RESET}")
            for i, step in enumerate(steps[:3], 1):
                action = step.get('action', '').upper()
                target = step.get('path') or step.get('command') or "Unknown"
                print(f"  {i}. {action}: {target[:50]}...")
            if len(steps) > 3:
                print(f"  ... and {len(steps)-3} more steps")
        else:
            UI.render_plan(plan_data, model_name or active_engine)
        
        confidence = plan_data.get('confidence', 0)

        if confidence < 40:
            if not UI.SILENT_ERRORS:
                UI.print_warning("📉 Low confidence (<40%)")
                if input(f"{Color.YELLOW}Continue? (y/n): {Color.RESET}").lower().strip() != 'y':
                    UI.print_system("⏹️  Cancelled")
                    return
        elif not self.auto_mode and not UI.GHOST_MODE:
            print(f"{Color.YELLOW}Execute {len(plan_data.get('steps', []))} steps? (y/n/auto): {Color.RESET}", end="", flush=True)
            confirm = input().lower().strip()
            
            if confirm == 'auto': 
                self.do_toggle_auto(None)
            elif confirm != 'y':
                UI.print_system("⏹️  Cancelled")
                return

        self.execute_plan_with_progress(plan_data.get('steps', []), model_name or active_engine)

    def execute_plan_with_progress(self, steps: List[Dict], model_name="AI"):
        """Execute plan with auto-installation support"""
        total = len(steps)
        completed_steps = 0
        
        for i, step in enumerate(steps, 1):
            action = step.get('action', '').lower()
            path = step.get('path', '')
            cmd = step.get('command', '')
            desc = step.get('description', '')
            
            target = cmd if action == 'command' else path
            progress = f"[{i}/{total}] {action.upper()} → {target}"
            UI.update_progress(progress)
            
            if not self.auto_mode and not UI.GHOST_MODE and not UI.SILENT_ERRORS:
                UI.clear_progress()
                choice = input(f"{Color.YELLOW}Allow step {i}/{total}? (y/n/skip): {Color.RESET}").lower().strip()
                if choice == 'n': 
                    UI.print_warning("Execution stopped by user.")
                    UI.add_to_summary("Stopped by user", f"Step {i}", "⏸️", "User interrupted")
                    break
                if choice == 'skip': 
                    UI.update_progress(f"⏭️  Skipped: {target}")
                    UI.add_to_summary("Skipped", target, "⏭️", "User skipped")
                    continue

            try:
                if action in ['create', 'modify']:
                    self._handle_file_action(action, path, desc, model_name)
                    completed_steps += 1
                    
                elif action == 'delete':
                    if self.workspace.delete_file(path):
                        UI.update_progress(f"🗑️  Deleted: {path}")
                        UI.add_to_summary("Deleted file", path, "✅")
                    else:
                        UI.update_progress(f"❌ Failed to delete: {path}")
                        UI.add_to_summary("Failed to delete", path, "❌")
                    completed_steps += 1
                    
                elif action == 'command':
                    success = self.run_command_with_ai_install(cmd)
                    if success:
                        completed_steps += 1
                    else:
                        UI.add_to_summary("Failed command", cmd.split()[0], "❌", "Command failed")
                    
                elif action == 'analyze':
                    UI.update_progress(f"🔍 Analyzed: {path}")
                    time.sleep(0.3)
                    completed_steps += 1
                    UI.add_to_summary("Analyzed", path, "🔍")

                self.persistence.log(f"Action: {action} | Target: {path or cmd}")

            except Exception as e:
                self.persistence.log_error(f"Execution Error in step {i}: {e}", f"Action: {action}", silent=True)
                UI.add_to_summary("Error in step", f"Step {i}", "❌", str(e)[:100])
                
                if not UI.SILENT_ERRORS:
                    UI.update_progress(f"⚠️  Step failed (continuing)")
                time.sleep(0.5)
        
        success_rate = (completed_steps / total * 100) if total > 0 else 0
        
        if success_rate >= 90:
            completion_icon = "✨"
            completion_color = Color.GREEN
            completion_msg = "Excellent"
        elif success_rate >= 70:
            completion_icon = "👍"
            completion_color = Color.YELLOW
            completion_msg = "Good"
        elif success_rate >= 50:
            completion_icon = "⚠️ "
            completion_color = Color.YELLOW
            completion_msg = "Partial"
        else:
            completion_icon = "❌"
            completion_color = Color.RED
            completion_msg = "Poor"
        
        UI.clear_progress()
        print(f"\n{completion_color}{completion_icon} Execution Complete: {completion_msg} ({completed_steps}/{total} steps){Color.RESET}")
        
        UI.show_summary()

    def run_command_with_ai_install(self, cmd, max_retries=3):
        """Run command with AI-assisted package installation"""
        current_cmd = cmd
        original_cmd = cmd
        
        for attempt in range(max_retries + 1):
            if attempt == 0:
                UI.update_progress(f"Running: {current_cmd[:50]}...")
            elif attempt == 1:
                UI.update_progress(f"🔄 AI is analyzing the error...")
            else:
                UI.update_progress(f"🔄 AI Retry {attempt}/{max_retries}...")
            
            proc = subprocess.run(current_cmd, shell=True, capture_output=True, text=True)
            
            if proc.returncode == 0:
                # النجاح
                if not UI.GHOST_MODE and proc.stdout.strip():
                    UI.clear_progress()
                    print(f"{Color.GREEN}{proc.stdout[:500]}{Color.RESET}")
                return True
            
            error_output = proc.stderr
            
            if attempt < max_retries:
                UI.clear_progress()
                
                # تحقق إذا كان الخطأ بسبب باكج مفقود
                is_package_error = any(
                    pattern in error_output.lower() 
                    for pattern in ['command not found', 'not found', 'module not found', 
                                'could not find', 'npm: not found', 'node: not found',
                                'pip: not found', 'python: not found']
                )
                
                if is_package_error:
                    # ⭐⭐ الجزء الجديد: استخدم AI لتوليد أمر التثبيت ⭐⭐
                    install_cmd = self._get_ai_install_command(cmd, error_output)
                    
                    if install_cmd:
                        UI.print_warning(f"⚠️  Missing dependency detected by AI")
                        UI.print_note(f"AI suggests: {install_cmd[:100]}...")
                        
                        if UI.GHOST_MODE:
                            # في وضع ghost، نفذ مباشرة
                            UI.update_progress(f"📦 Auto-installing via AI...")
                            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                UI.print_success(f"✅ AI-installed successfully")
                                time.sleep(2)
                                UI.update_progress("🔄 Retrying original command...")
                                continue
                            else:
                                UI.print_error(f"❌ AI installation failed: {result.stderr[:100]}")
                                break
                        else:
                            # اسأل المستخدم
                            response = input(f"{Color.YELLOW}Execute AI-generated install command? (y/n): {Color.RESET}").lower()
                            if response == 'y':
                                UI.update_progress(f"📦 Executing AI install command...")
                                result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
                                
                                if result.returncode == 0:
                                    UI.clear_progress()
                                    UI.print_success(f"✅ AI-installed successfully")
                                    UI.add_to_summary("AI-installed", cmd.split()[0], "✅", f"via {install_cmd[:50]}")
                                    
                                    time.sleep(2)
                                    UI.update_progress("🔄 Retrying original command...")
                                    continue
                                else:
                                    UI.clear_progress()
                                    UI.print_error(f"❌ AI installation failed: {result.stderr[:100]}")
                                    break
                            else:
                                UI.print_warning("⏸️  Installation declined")
                                break
                    else:
                        UI.print_error("❌ AI couldn't generate install command")
                        break
                else:
                    # أخطاء أخرى - حاول إصلاحها
                    fix_cmd = self.ai.get_fix_for_error(current_cmd, error_output)
                    if fix_cmd:
                        UI.update_progress(f"🛠️  Applying AI fix...")
                        current_cmd = fix_cmd
                        time.sleep(1)
                        continue
                    else:
                        break
            else:
                # فشلت كل المحاولات
                self.persistence.log_error(
                    f"Command failed after {max_retries} attempts: {original_cmd}", 
                    error_output[:200], 
                    silent=True
                )
                UI.add_to_summary("Failed command", original_cmd.split()[0], "❌", error_output[:100])
                break
        
        return False

    def _get_ai_install_command(self, failed_cmd, error_output):
        """Ask AI to generate OS-specific install command"""
        
        # التعرف على نظام التشغيل
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            os_info = "Windows (use winget, chocolatey, or scoop)"
            package_managers = "winget install, choco install, or scoop install"
        elif system == 'linux':
            # اكتشاف توزيعة لينكس
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read()
                    if 'ubuntu' in content.lower() or 'debian' in content.lower():
                        os_info = "Ubuntu/Debian (use apt)"
                        package_managers = "sudo apt install"
                    elif 'fedora' in content.lower():
                        os_info = "Fedora (use dnf)"
                        package_managers = "sudo dnf install"
                    elif 'arch' in content.lower():
                        os_info = "Arch Linux (use pacman)"
                        package_managers = "sudo pacman -S"
                    else:
                        os_info = "Linux (generic)"
                        package_managers = "appropriate package manager"
            except:
                os_info = "Linux (generic)"
                package_managers = "appropriate package manager"
        elif system == 'darwin':
            os_info = "macOS (use Homebrew)"
            package_managers = "brew install"
        else:
            os_info = f"Unknown OS: {system}"
            package_managers = "appropriate package manager"
        
        # بناء prompt للـ AI
        prompt = f"""
                A command has FAILED due to a missing dependency or executable.

                FAILED COMMAND:
                {failed_cmd}

                ERROR OUTPUT (truncated):
                {error_output[:600]}

                OPERATING SYSTEM:
                {os_info}

                Your task:
                Identify the ROOT missing dependency (tool, runtime, library, compiler, or package manager)
                and generate the EXACT shell command needed to install it.

                Important:
                - The missing dependency may be:
                • a CLI tool (e.g. git, curl, ffmpeg, docker)
                • a language runtime (python, node, java, go, ruby, php, dotnet)
                • a compiler or build tool (gcc, make, cmake, clang)
                • a system library (openssl, zlib, libssl, libc++)
                • a package manager itself (npm, pip, yarn, pnpm, poetry)
                • a cloud / dev tool (aws, gcloud, az, kubectl)
                - The name may NOT be explicitly mentioned.
                - You must infer it from the error message.

                Rules (STRICT):
                1. Output ONLY ONE valid shell command — no explanations.
                2. The command MUST work on the OS specified.
                3. Use the most STANDARD package manager for that OS:
                - Ubuntu/Debian → apt
                - Fedora/RHEL → dnf
                - Arch → pacman
                - macOS → brew
                - Windows → winget (preferred), choco if needed
                4. Include required privileges (sudo, admin).
                5. Install the MAIN dependency, not plugins or versions.
                6. Do NOT install unrelated tools.
                7. If the dependency is already part of a meta-package, install the meta-package.
                8. If installation requires multiple chained commands, return them as ONE line joined with &&.
                9. If the dependency cannot be installed automatically, install the closest official package.

                Common inference patterns:
                - "command not found" → missing executable
                - "No module named X" → missing language package manager or runtime
                - "cannot open shared object file" → missing system library
                - "gcc: command not found" → missing build-essential / gcc
                - "npm: not found" → Node.js runtime missing
                - "pip: command not found" → python-pip missing
                - "ld: library not found" → missing system dev library
                - "make: not found" → missing build tools

                Examples:
                - Ubuntu error: "gcc: command not found"
                → sudo apt update && sudo apt install build-essential

                - macOS error: "zsh: command not found: ffmpeg"
                → brew install ffmpeg

                - Windows error: "'python' is not recognized"
                → winget install Python.Python.3

                - Ubuntu error: "No module named pip"
                → sudo apt install python3-pip

                - Fedora error: "git: command not found"
                → sudo dnf install git

                Output format:
                <INSTALL COMMAND ONLY>
                """

        
        # استخدام AI لتوليد الأمر
        result, model_name = self.ai.generate_content(prompt)
        
        if result and "UNKNOWN_PACKAGE" not in result.upper():
            # تنظيف النتيجة
            clean_cmd = result.strip()
            clean_cmd = clean_cmd.replace('```bash', '').replace('```sh', '').replace('```', '').strip()
            clean_cmd = clean_cmd.split('\n')[0]  # أخذ أول سطر فقط
            
            # تسجيل في السجل
            self.persistence.log(f"AI generated install command: {clean_cmd}", "INFO", model_name)
            
            return clean_cmd
        
        return None
    def _handle_file_action(self, action, path, desc, model_name):
        """Handle file creation/modification with summary tracking"""
        is_mod = (action == 'modify')
        
        new_content, gen_model = self.agent.execute_code_generation(path, desc, is_mod)
        
        if new_content:
            old_content = self.workspace.read_file(path) if is_mod else ""
            
            if not UI.GHOST_MODE and is_mod and old_content and not UI.SILENT_ERRORS:
                UI.clear_progress()
                old_lines = len(old_content.splitlines())
                new_lines = len(new_content.splitlines())
                print(f"\n{Color.YELLOW}📄 {path}: {old_lines} → {new_lines} lines{Color.RESET}")
                
                if not self.auto_mode:
                    UI.clear_progress()
                    if input(f"{Color.YELLOW}Apply changes? (y/n): {Color.RESET}").lower() != 'y':
                        UI.update_progress("⏭️  Modification skipped")
                        UI.add_to_summary("Skipped modification", path, "⏭️", "User declined")
                        return
            
            res = self.workspace.write_file(path, new_content)
            if res is True:
                action_text = "Modified" if is_mod else "Created"
                UI.update_progress(f"{'✏️ ' if is_mod else '📄'} {action_text}: {path}")
                
                lines = len(new_content.splitlines())
                details = f"{lines} lines via {gen_model or model_name}"
                UI.add_to_summary(
                    f"{action_text} file", 
                    path, 
                    "✅", 
                    details
                )
                
                self.persistence.log(f"{gen_model or model_name} generated: {path}")
            else:
                self.persistence.log_error(f"Write Failed for {path}: {res}", "file_ops", silent=True)
                UI.update_progress(f"❌ Failed to write: {path}")
                UI.add_to_summary(f"Failed to {action}", path, "❌", str(res)[:100])

    def run_system_command(self, cmd):
        try:
            UI.update_progress(f"Executing: {cmd[:50]}...")
            subprocess.run(cmd, shell=True)
            UI.clear_progress()
        except Exception as e:
            self.persistence.log_error(f"Command failed: {e}", "system", silent=True)
            UI.clear_progress()
    def handle_installation_request(self, prompt: str):
        """
        معالجة طلبات التثبيت - يعتمد كلياً على AI لتوليد الأمر
        """
        UI.clear_progress()
        
        # استخدام الذكاء الاصطناعي لتوليد أمر التثبيت المناسب
        ai_prompt = self._build_ai_install_prompt(prompt)
        
        UI.update_progress("🤔 AI is generating the installation command...")
        
        # اسأل AI لتوليد الأمر
        response, model_name = self.ai.generate_content(ai_prompt)
        
        if not response:
            UI.print_error("AI could not generate installation command", silent=True)
            return
        
        # معالجة الرد من AI
        self._process_ai_installation_response(response, model_name, prompt)

    def _build_ai_install_prompt(self, user_request: str) -> str:
        """بناء الـ prompt المناسب للذكاء الاصطناعي"""
        import platform
        import subprocess
        
        system = platform.system().lower()
        
        # جمع معلومات عن النظام
        system_info = f"Operating System: {system}"
        
        # التحقق من مديري الحزم المتاحين
        available_managers = []
        
        # التحقق من winget (Windows)
        if system == 'windows':
            try:
                result = subprocess.run('winget --version', shell=True, 
                                    capture_output=True, text=True)
                if result.returncode == 0:
                    available_managers.append('winget')
            except:
                pass
        
        # التحقق من chocolatey
        try:
            result = subprocess.run('choco --version', shell=True, 
                                capture_output=True, text=True)
            if result.returncode == 0:
                available_managers.append('chocolatey')
        except:
            pass
        
        # التحقق من npm
        try:
            result = subprocess.run('npm --version', shell=True, 
                                capture_output=True, text=True)
            if result.returncode == 0:
                available_managers.append('npm')
        except:
            pass
        
        # التحقق من pip
        try:
            result = subprocess.run('pip --version', shell=True, 
                                capture_output=True, text=True)
            if result.returncode == 0:
                available_managers.append('pip')
        except:
            pass
        
        # بناء الـ prompt
        prompt = f"""
        You are an expert system administrator and package manager expert.
        
        USER REQUEST: "{user_request}"
        
        SYSTEM INFORMATION:
        - OS: {system}
        - Available package managers: {', '.join(available_managers) if available_managers else 'Unknown'}
        
        TASK:
        Based on the user's request, generate the CORRECT installation command.
        
        IMPORTANT RULES:
        1. Generate ONE single command that can be executed directly in the terminal.
        2. The command MUST work on the current OS ({system}).
        3. Choose the MOST APPROPRIATE package manager for the task.
        4. Include all necessary flags (like -y for apt, --accept-package-agreements for winget).
        5. If multiple commands are needed, chain them with &&.
        6. For Windows: Prefer winget if available, then chocolatey, then manual download.
        7. For Linux: Prefer apt for Debian/Ubuntu, yum/dnf for Fedora/RHEL, pacman for Arch.
        8. For macOS: Use brew.
        9. If the package name is ambiguous, choose the most popular/mainstream one.
        
        OUTPUT FORMAT:
        Return a JSON object with this exact structure:
        {{
            "package": "name_of_package",
            "manager": "package_manager_used",
            "command": "full_shell_command_to_execute",
            "explanation": "brief_explanation_in_english",
            "risk_level": "low/medium/high",
            "notes": "any_important_notes"
        }}
        
        EXAMPLES:
        
        Example 1 (Windows):
        Request: "download rust for windows"
        Available: winget
        Response: {{
            "package": "Rust.Rustup",
            "manager": "winget",
            "command": "winget install --id Rust.Rustup --accept-package-agreements",
            "explanation": "Installs Rust programming language via Rustup (recommended installer)",
            "risk_level": "low",
            "notes": "Rustup will install both rustc and cargo"
        }}
        
        Example 2 (Linux - Ubuntu):
        Request: "install python on ubuntu"
        Available: apt
        Response: {{
            "package": "python3",
            "manager": "apt",
            "command": "sudo apt update && sudo apt install python3 -y",
            "explanation": "Installs Python 3 from Ubuntu repositories",
            "risk_level": "low",
            "notes": "Python 3 is pre-installed on most Ubuntu versions"
        }}
        
        Example 3 (macOS):
        Request: "install docker on mac"
        Available: brew
        Response: {{
            "package": "docker",
            "manager": "brew",
            "command": "brew install --cask docker",
            "explanation": "Installs Docker Desktop for macOS",
            "risk_level": "medium",
            "notes": "Docker Desktop requires manual setup after installation"
        }}
        
        Example 4 (Arabic):
        Request: "حملي npm"
        Available: winget
        Response: {{
            "package": "OpenJS.NodeJS",
            "manager": "winget",
            "command": "winget install OpenJS.NodeJS",
            "explanation": "Installs Node.js which includes npm",
            "risk_level": "low",
            "notes": "Node.js installer includes npm by default"
        }}
        
        Now, generate the command for the user's request.
        """
        
        return prompt

    def _process_ai_installation_response(self, response: str, model_name: str, original_request: str):
        """معالجة الرد من الذكاء الاصطناعي"""
        try:
            # تنظيف الرد
            clean_response = response.strip()
            
            # إزالة markdown code blocks
            if '```json' in clean_response:
                clean_response = clean_response.split('```json')[1].split('```')[0].strip()
            elif '```' in clean_response:
                clean_response = clean_response.split('```')[1].split('```')[0].strip()
            
            # تحليل JSON
            install_info = json.loads(clean_response)
            
            package = install_info.get('package')
            manager = install_info.get('manager')
            command = install_info.get('command')
            explanation = install_info.get('explanation', '')
            risk_level = install_info.get('risk_level', 'unknown')
            notes = install_info.get('notes', '')
            
            if not all([package, manager, command]):
                raise ValueError("Missing required fields in AI response")
            
            # عرض المعلومات
            UI.clear_progress()
            
            # تلوين مستوى الخطورة
            risk_color = {
                'low': Color.GREEN,
                'medium': Color.YELLOW,
                'high': Color.RED
            }.get(risk_level.lower(), Color.WHITE)
            
            print(f"\n{Color.CYAN}🤖 AI Installation Plan:{Color.RESET}")
            print(f"{Color.DIM}{'='*60}{Color.RESET}")
            print(f"{Color.BOLD}Package:{Color.RESET}    {package}")
            print(f"{Color.BOLD}Manager:{Color.RESET}    {manager}")
            print(f"{Color.BOLD}Risk:{Color.RESET}       {risk_color}{risk_level.upper()}{Color.RESET}")
            print(f"{Color.BOLD}Command:{Color.RESET}    {Color.GREEN}{command}{Color.RESET}")
            
            if explanation:
                print(f"\n{Color.BOLD}Explanation:{Color.RESET}")
                print(f"{Color.DIM}{explanation}{Color.RESET}")
            
            if notes:
                print(f"\n{Color.BOLD}Notes:{Color.RESET}")
                print(f"{Color.DIM}📝 {notes}{Color.RESET}")
            
            print(f"{Color.DIM}{'='*60}{Color.RESET}")
            
            # تسجيل في السجل
            self.persistence.log(
                f"AI generated install command: {command} for '{original_request}'",
                "INFO",
                model_name
            )
            
            # طلب التنفيذ
            self._ask_for_execution(command, package, manager, model_name)
            
        except json.JSONDecodeError as e:
            UI.print_error(f"AI returned invalid JSON: {e}", silent=True)
            UI.print_note(f"AI raw response: {response[:200]}...")
            # محاولة استخراج الأمر مباشرة إذا لم يكن JSON
            self._extract_command_from_text(response, original_request)
        except Exception as e:
            UI.print_error(f"Failed to process AI response: {e}", silent=True)
            self.persistence.log_error(f"AI processing failed: {e}", response[:100], silent=True)

    def _extract_command_from_text(self, text: str, original_request: str):
        """استخراج أمر من نص AI إذا لم يكن JSON"""
        # البحث عن سطر يشبه أمر تنفيذ
        lines = text.split('\n')
        potential_commands = []
        
        for line in lines:
            line = line.strip()
            # تحقق إذا كان السطر يبدو كأمر
            if (line.startswith('winget') or line.startswith('sudo') or 
                line.startswith('apt') or line.startswith('brew') or
                line.startswith('npm') or line.startswith('pip') or
                line.startswith('choco') or 'install' in line.lower()):
                potential_commands.append(line)
        
        if potential_commands:
            UI.print_warning("AI didn't return proper JSON, but found potential command:")
            for cmd in potential_commands[:3]:  # أول 3 أوامر فقط
                print(f"  {Color.GREEN}{cmd}{Color.RESET}")
            
            if len(potential_commands) == 1:
                self._ask_for_execution(potential_commands[0], "unknown", "unknown", "AI")
        else:
            UI.print_error("Could not extract installation command from AI response", silent=True)
            UI.print_note("Try rephrasing your request, like:")
            UI.print_note("  • 'install rust using winget on windows'")
            UI.print_note("  • 'download node.js for windows 11'")

    def _ask_for_execution(self, command: str, package: str, manager: str, model_name: str):
        """طلب تنفيذ الأمر من المستخدم"""
        if UI.GHOST_MODE:
            # التنفيذ التلقائي في وضع Ghost
            UI.update_progress(f"📦 Auto-installing {package}...")
            self._execute_ai_installation(command, package, manager, model_name)
        else:
            # طلب التأكيد
            print(f"\n{Color.YELLOW}Execute this command? (y/n/explain): {Color.RESET}", end="")
            response = input().lower().strip()
            
            if response == 'y':
                UI.update_progress(f"📦 Installing {package}...")
                self._execute_ai_installation(command, package, manager, model_name)
            elif response == 'explain':
                # طلب شرح أكثر من AI
                self._ask_ai_for_explanation(command, package)
            else:
                UI.print_system("Installation cancelled")
        
    def _execute_ai_installation(self, command: str, package: str, manager: str, model_name: str):
        """تنفيذ أمر التثبيت الذي ولده AI"""
        try:
            UI.clear_progress()
            UI.print_note(f"Executing: {command}")
            
            # تنفيذ الأمر
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                UI.print_success(f"✅ Successfully installed {package}")
                
                # تسجيل النجاح
                self.persistence.track_installation(package, manager, True)
                UI.add_to_summary(f"AI-installed {package}", manager, "✅", f"via {model_name}")
                
                # عرض الإخراج إذا كان موجودًا
                if result.stdout.strip():
                    print(f"\n{Color.GREEN}Output:{Color.RESET}")
                    print(f"{Color.DIM}{result.stdout[:500]}{Color.RESET}")
                
                # اقتراح الخطوة التالية
                self._suggest_next_steps(package, manager)
                
            else:
                # الفشل
                error_msg = result.stderr
                
                UI.print_error(f"❌ Installation failed for {package}", silent=False)
                
                # عرض تفاصيل الخطأ
                if error_msg:
                    print(f"\n{Color.RED}Error details:{Color.RESET}")
                    print(f"{Color.DIM}{error_msg[:400]}{Color.RESET}")
                
                # تسجيل الفشل
                self.persistence.track_installation(package, manager, False)
                UI.add_to_summary(f"Failed to install {package}", manager, "❌", error_msg[:100])
                
                # طلب مساعدة AI لحل المشكلة
                self._ask_ai_for_fix(command, error_msg, package)
                
        except Exception as e:
            UI.print_error(f"❌ Execution failed: {e}", silent=False)
            self.persistence.log_error(f"Installation execution failed: {e}", command, silent=True)

    def _ask_ai_for_explanation(self, command: str, package: str):
        """طلب شرح مفصل للأمر من AI"""
        UI.update_progress("🤔 Asking AI for detailed explanation...")
        
        prompt = f"""
        Explain this installation command in simple terms:
        
        Command: {command}
        Package: {package}
        
        Provide a detailed explanation including:
        1. What this command does exactly
        2. Why these specific flags/options are used
        3. Any potential risks or side effects
        4. What the user should do after installation
        
        Keep it clear and concise.
        """
        
        response, model_name = self.ai.generate_content(prompt)
        
        if response:
            UI.clear_progress()
            print(f"\n{Color.CYAN}📚 AI Explanation:{Color.RESET}")
            print(f"{Color.DIM}{'='*60}{Color.RESET}")
            print(response)
            print(f"{Color.DIM}{'='*60}{Color.RESET}")
            
            # العودة للسؤال عن التنفيذ
            print(f"\n{Color.YELLOW}Execute the command now? (y/n): {Color.RESET}", end="")
            response = input().lower().strip()
            if response == 'y':
                UI.update_progress(f"📦 Installing {package}...")
                self._execute_ai_installation(command, package, "unknown", model_name)

    def _ask_ai_for_fix(self, failed_command: str, error_output: str, package: str):
        """طلب حل للمشكلة من AI"""
        if UI.GHOST_MODE:
            return
        
        print(f"\n{Color.YELLOW}Ask AI for a fix? (y/n): {Color.RESET}", end="")
        response = input().lower().strip()
        
        if response != 'y':
            return
        
        UI.update_progress("🤔 AI is analyzing the error...")
        
        prompt = f"""
        Installation command failed:
        
        Command: {failed_command}
        Error: {error_output[:500]}
        Package: {package}
        
        Suggest a fix. This could be:
        1. An alternative installation method
        2. A prerequisite that needs to be installed first
        3. A different package name
        4. Manual installation steps
        
        Provide clear, actionable steps.
        """
        
        response, model_name = self.ai.generate_content(prompt)
        
        if response:
            UI.clear_progress()
            print(f"\n{Color.CYAN}🔧 AI Suggested Fix:{Color.RESET}")
            print(f"{Color.DIM}{'='*60}{Color.RESET}")
            print(response)
            print(f"{Color.DIM}{'='*60}{Color.RESET}")

    def _suggest_next_steps(self, package: str, manager: str):
        """اقتراح الخطوات التالية بعد التثبيت الناجح"""
        suggestions = {
            'rust': [
                "Run 'rustc --version' to verify installation",
                "Run 'cargo --version' to check Cargo package manager",
                "Create a test project: 'cargo new hello_world'"
            ],
            'node': [
                "Run 'node --version' to check Node.js",
                "Run 'npm --version' to check npm",
                "Create a test file: 'console.log(\"Hello Node\")'"
            ],
            'python': [
                "Run 'python --version' or 'python3 --version'",
                "Run 'pip --version' to check pip",
                "Try: 'python -c \"print('Hello Python')\"'"
            ],
            'docker': [
                "Run 'docker --version' to verify",
                "Try: 'docker run hello-world'",
                "Check if Docker service is running"
            ],
            'git': [
                "Run 'git --version'",
                "Configure git: 'git config --global user.name \"Your Name\"'",
                "Try: 'git init' in a test directory"
            ]
        }
        
        # البحث عن اقتراحات
        package_lower = package.lower()
        for key, steps in suggestions.items():
            if key in package_lower:
                print(f"\n{Color.GREEN}🚀 Next steps for {package}:{Color.RESET}")
                for step in steps:
                    print(f"  • {step}")
                break
    def handle_cd_command(self, text):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            try:
                os.chdir(parts[1])
                self.persistence.update_workspace(os.getcwd())
                UI.update_progress(f"Changed to: {os.getcwd()}")
                time.sleep(0.3)
                UI.clear_progress()
            except Exception as e:
                self.persistence.log_error(f"CD failed: {e}", parts[1], silent=True)

    def do_toggle_silent(self, text):
        """Toggle silent error mode"""
        UI.SILENT_ERRORS = not UI.SILENT_ERRORS
        self.persistence.config["silent_errors"] = UI.SILENT_ERRORS
        self.persistence.save()
        state = "ENABLED" if UI.SILENT_ERRORS else "DISABLED"
        color = Color.BLUE if UI.SILENT_ERRORS else Color.YELLOW
        UI.print_system(f"Silent Error Mode: {color}{state}{Color.RESET}")

    def do_toggle_auto(self, _):
        self.auto_mode = not self.auto_mode
        state = "ENABLED" if self.auto_mode else "DISABLED"
        color = Color.GREEN if self.auto_mode else Color.RED
        UI.print_system(f"Auto-Pilot Mode: {color}{state}{Color.RESET}")

    def do_toggle_ghost(self, text):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            UI.set_ghost(parts[1].lower() == 'on')
        else:
            UI.set_ghost(not UI.GHOST_MODE)
    
    def do_toggle_fallback(self, text):
        current = self.persistence.config.get("fallback_enabled", True)
        self.persistence.config["fallback_enabled"] = not current
        self.persistence.save()
        state = "ENABLED" if not current else "DISABLED"
        color = Color.GREEN if not current else Color.RED
        UI.print_system(f"Auto-Fallback: {color}{state}{Color.RESET}")
    
    def do_check_balance(self, text):
        """Check DeepSeek account balance"""
        if not self.ai:
            UI.print_error("AI engine manager not initialized", silent=True)
            return
            
        if 'deepseek' not in self.ai.engines:
            UI.print_error("DeepSeek engine not available", silent=True)
            return
            
        deepseek_engine = self.ai.engines['deepseek']
        UI.update_progress("Checking DeepSeek balance...")
        
        if deepseek_engine.check_balance():
            UI.clear_progress()
            UI.print_success("✓ DeepSeek account has sufficient balance")
        else:
            UI.clear_progress()
            UI.print_error("✗ DeepSeek: Insufficient Balance", silent=False)
            if not UI.SILENT_ERRORS:
                print(f"\n{Color.YELLOW}Please recharge at: {Color.CYAN}https://platform.deepseek.com/{Color.RESET}")
    def do_list_chats(self, text):
        """List all available chat sessions"""
        chats = self.chat_manager.list_chats(limit=20)
        
        if not chats:
            UI.print_system("No chats found. Start a conversation to create one!")
            return
        
        current_id = self.chat_manager.current_chat_id
        
        print(f"\n{Color.CYAN}💬 Available Chats:{Color.RESET}")
        print(f"{Color.DIM}{'='*80}{Color.RESET}")
        
        for i, chat in enumerate(chats, 1):
            # Parse dates for display
            try:
                created_dt = datetime.fromisoformat(chat.created_at.replace('Z', '+00:00'))
                last_dt = datetime.fromisoformat(chat.last_activity.replace('Z', '+00:00'))
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")
                last_str = last_dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_str = chat.created_at[:16]
                last_str = chat.last_activity[:16]
            
            # Mark current chat
            is_current = " ⭐ CURRENT" if chat.chat_id == current_id else ""
            
            # Truncate title if too long
            title_display = chat.title
            if len(title_display) > 30:
                title_display = title_display[:27] + "..."
            
            print(f"{i:2}. {Color.BOLD}{title_display:<30}{Color.RESET}")
            print(f"    {Color.DIM}ID: {chat.chat_id}{is_current}{Color.RESET}")
            print(f"    {Color.DIM}Created: {created_str} | Last: {last_str} | Messages: {len(chat.messages)}{Color.RESET}")
            
            # Show first message if available
            if chat.messages and i <= 5:
                first_msg = chat.messages[0]['parts'][0]
                preview = first_msg[:60] + "..." if len(first_msg) > 60 else first_msg
                print(f"    {Color.DIM}First: \"{preview}\"{Color.RESET}")
            
            print(f"    {Color.DIM}{'-'*40}{Color.RESET}")
        
        print(f"\n{Color.BLUE}Commands:{Color.RESET}")
        print(f"  • {Color.YELLOW}chat <ID or number>{Color.RESET} - Switch to chat")
        print(f"  • {Color.YELLOW}newchat{Color.RESET} - Start new chat")
        print(f"  • {Color.YELLOW}deletechat <ID>{Color.RESET} - Delete chat")
        print(f"  • {Color.YELLOW}renamechat <ID> <new title>{Color.RESET} - Rename chat")
        print(f"  • {Color.YELLOW}exportchat <ID> [json/txt]{Color.RESET} - Export chat")
    
    def do_switch_chat(self, text):
        """Switch to a specific chat by ID or number"""
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            # Show current chat info
            chat = self.chat_manager.get_current_chat()
            print(f"\n{Color.CYAN}Current Chat:{Color.RESET}")
            print(f"  ID: {Color.BOLD}{chat.chat_id}{Color.RESET}")
            print(f"  Title: {Color.GREEN}{chat.title}{Color.RESET}")
            print(f"  Messages: {len(chat.messages)}")
            print(f"  Created: {chat.created_at[:19]}")
            return
        
        target = parts[1].strip()
        
        # Check if it's a number from the list
        if target.isdigit():
            chats = self.chat_manager.list_chats(limit=100)
            index = int(target) - 1
            if 0 <= index < len(chats):
                target = chats[index].chat_id
            else:
                UI.print_error(f"Invalid chat number: {target}", silent=True)
                return
        
        # Switch to the chat
        success, result = self.chat_manager.switch_to_chat(target)
        if success:
            chat = result
            UI.print_success(f"Switched to chat: {Color.BOLD}{chat.title}{Color.RESET}")
            UI.print_note(f"Chat ID: {chat.chat_id} | Messages: {len(chat.messages)}")
            
            # Show last few messages
            if chat.messages:
                print(f"\n{Color.DIM}Last messages:{Color.RESET}")
                for msg in chat.messages[-3:]:
                    role_icon = "👤" if msg['role'] == 'user' else "🤖"
                    role_color = Color.BLUE if msg['role'] == 'user' else Color.GREEN
                    preview = msg['parts'][0][:80] + "..." if len(msg['parts'][0]) > 80 else msg['parts'][0]
                    print(f"  {role_icon} {role_color}{preview}{Color.RESET}")
        else:
            UI.print_error(f"Failed to switch chat: {result}", silent=True)
    
    def do_new_chat(self, text):
        """Create a new chat session"""
        parts = text.split(maxsplit=1)
        title = parts[1] if len(parts) > 1 else None
        
        old_chat = self.chat_manager.get_current_chat()
        new_chat = self.chat_manager.create_new_chat()
        
        if title:
            self.chat_manager.rename_chat(new_chat.chat_id, title)
            new_chat.title = title
        
        UI.print_success(f"Created new chat: {Color.BOLD}{new_chat.title}{Color.RESET}")
        UI.print_note(f"Chat ID: {new_chat.chat_id}")
        UI.print_note(f"Previous chat: {old_chat.title} (ID: {old_chat.chat_id})")
    
    def do_save_chat(self, text):
        """Save current chat (auto-saved, just shows info)"""
        chat = self.chat_manager.get_current_chat()
        UI.print_success(f"Chat auto-saved: {chat.title}")
        UI.print_note(f"ID: {chat.chat_id} | Messages: {len(chat.messages)}")
        UI.print_note("Chats are automatically saved after each message.")
    
    def do_load_chat(self, text):
        """Alias for switch_chat"""
        self.do_switch_chat(text)
    
    def do_rename_chat(self, text):
        """Rename current or specified chat"""
        parts = text.split(maxsplit=2)
        
        if len(parts) == 1:
            # Show current chat name
            chat = self.chat_manager.get_current_chat()
            UI.print_system(f"Current chat: '{chat.title}' (ID: {chat.chat_id})")
            return
        
        if len(parts) == 2:
            # Rename current chat
            new_title = parts[1]
            chat = self.chat_manager.get_current_chat()
            success, message = self.chat_manager.rename_chat(chat.chat_id, new_title)
        else:
            # Rename specific chat
            chat_id = parts[1]
            new_title = parts[2]
            success, message = self.chat_manager.rename_chat(chat_id, new_title)
        
        if success:
            UI.print_success(message)
        else:
            UI.print_error(message, silent=True)
    
    def do_delete_chat(self, text):
        """Delete a chat session"""
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            UI.print_error("Specify chat ID to delete", silent=True)
            UI.print_note("Use 'chats' to list all chats with their IDs")
            return
        
        chat_id = parts[1].strip()
        
        # Ask for confirmation
        if not UI.GHOST_MODE:
            chat = self.chat_manager.sessions.get(chat_id)
            if chat:
                confirm = input(f"{Color.RED}Delete chat '{chat.title}'? (y/N): {Color.RESET}").lower()
                if confirm != 'y':
                    UI.print_system("Deletion cancelled")
                    return
        
        success, message = self.chat_manager.delete_chat(chat_id)
        if success:
            UI.print_success(message)
        else:
            UI.print_error(message, silent=True)
    
    def do_export_chat(self, text):
        """Export chat to file"""
        parts = text.split(maxsplit=2)
        if len(parts) < 2:
            # Export current chat
            chat = self.chat_manager.get_current_chat()
            chat_id = chat.chat_id
            format = parts[1] if len(parts) > 1 else "json"
        else:
            chat_id = parts[1]
            format = parts[2] if len(parts) > 2 else "json"
        
        success, message = self.chat_manager.export_chat(chat_id, format)
        if success:
            UI.print_success(message)
        else:
            UI.print_error(message, silent=True)
    
    def do_current_chat(self, text):
        """Show current chat information"""
        chat = self.chat_manager.get_current_chat()
        
        print(f"\n{Color.CYAN}📱 Current Chat Session:{Color.RESET}")
        print(f"{Color.DIM}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}Title:{Color.RESET}    {chat.title}")
        print(f"{Color.BOLD}ID:{Color.RESET}        {chat.chat_id}")
        print(f"{Color.BOLD}Created:{Color.RESET}   {chat.created_at[:19]}")
        print(f"{Color.BOLD}Last:{Color.RESET}      {chat.last_activity[:19]}")
        print(f"{Color.BOLD}Messages:{Color.RESET}  {len(chat.messages)}")
        
        if chat.messages:
            print(f"\n{Color.DIM}Recent Messages:{Color.RESET}")
            for msg in chat.messages[-5:]:
                role = "👤 User" if msg['role'] == 'user' else "🤖 AI"
                timestamp = msg.get('timestamp', '')[:16]
                content_preview = msg['parts'][0][:60] + "..." if len(msg['parts'][0]) > 60 else msg['parts'][0]
                print(f"  {Color.DIM}{timestamp}{Color.RESET} {role}: {content_preview}")
        
        print(f"\n{Color.BLUE}Quick Commands:{Color.RESET}")
        print(f"  {Color.YELLOW}newchat [title]{Color.RESET} - Start new chat")
        print(f"  {Color.YELLOW}chats{Color.RESET} - List all chats")
        print(f"  {Color.YELLOW}exportchat{Color.RESET} - Export this chat")
        print(f"  {Color.YELLOW}clearchat{Color.RESET} - Clear messages (keep chat)")
    
    def do_clear_chat(self, text):
        """Clear all messages in current chat"""
        chat = self.chat_manager.get_current_chat()
        
        if not chat.messages:
            UI.print_system("Chat is already empty")
            return
        
        if not UI.GHOST_MODE:
            confirm = input(f"{Color.YELLOW}Clear all {len(chat.messages)} messages in '{chat.title}'? (y/N): {Color.RESET}").lower()
            if confirm != 'y':
                UI.print_system("Clearing cancelled")
                return
        
        success, message = self.chat_manager.clear_current_chat()
        if success:
            UI.print_success(message)
            UI.print_note(f"Chat '{chat.title}' is now empty (ID preserved: {chat.chat_id})")
    def do_replay_last_task(self, _):
        if self.persistence.last_plan_cache:
            UI.print_system("Replaying last task...")
            active_engine = self.ai.active_engine_name if self.ai else "N/A"
            self.execute_plan_with_progress(self.persistence.last_plan_cache.get('steps', []), active_engine)
        else:
            UI.print_warning("No last task found to replay.")

    def do_switch_engine(self, text):
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            engine_name = parts[1].strip().lower()
            if self.ai:
                success, message = self.ai.switch_engine(engine_name)
                if success:
                    UI.print_success(message)
                    self.agent.ai = self.ai
                else:
                    UI.print_error(message, silent=True)
            else:
                UI.print_error("AI engine manager not initialized", silent=True)
        else:
            if self.ai:
                print(f"Current Engine: {Color.GREEN}{self.ai.active_engine_name.upper()}{Color.RESET}")
            else:
                print("No AI engines available")

    def do_list_engines(self, _):
        if not self.ai:
            UI.print_warning("No AI engines initialized")
            return
            
        print(f"\n{Color.CYAN}🤖 Available AI Engines:{Color.RESET}")
        print(f"{Color.DIM}{'='*50}{Color.RESET}")
        
        for engine_name, engine in self.ai.engines.items():
            is_active = (engine_name == self.ai.active_engine_name)
            if engine_name == "gemini":
                status_color = Color.GREEN
            elif engine_name == "deepseek":
                status_color = Color.CYAN
            elif engine_name == "groq":
                status_color = Color.YELLOW
            else:
                status_color = Color.WHITE
                
            if is_active:
                status_color = Color.BOLD + status_color
                
            active_marker = " ⭐ ACTIVE" if is_active else ""
            
            print(f"  {status_color}{engine_name.upper():<10}{Color.RESET} → {engine.model_name}{active_marker}")
            
            if engine_name == 'deepseek':
                if engine.balance_checked:
                    balance_status = f"{Color.GREEN}✓ Balance OK{Color.RESET}" if engine.balance_available else f"{Color.RED}✗ Insufficient Balance{Color.RESET}"
                    print(f"    {balance_status}")
            
            stat_key = f"{engine_name}:{engine.model_name}"
            stats = self.persistence.config.get("model_stats", {}).get(stat_key)
            if stats:
                success_rate = (stats['successes'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
                print(f"    {Color.DIM}Requests: {stats['requests']} | Success: {success_rate:.1f}% | Tokens: {stats['tokens_used']:,}{Color.RESET}")
        
        print(f"{Color.DIM}{'='*50}{Color.RESET}")
        print(f"{Color.BLUE}Use: 'engine <name>' to switch{Color.RESET}")

    def do_list_groq_models(self, _):
        """List available Groq models"""
        if not self.ai or 'groq' not in self.ai.engines:
            UI.print_error("Groq engine not available", silent=True)
            return
            
        groq_engine = self.ai.engines['groq']
        models = groq_engine.get_available_models()
        
        print(f"\n{Color.YELLOW}🚀 Available Groq Models:{Color.RESET}")
        print(f"{Color.DIM}{'='*50}{Color.RESET}")
        
        for model in models:
            is_active = (model == groq_engine.model_name)
            if is_active:
                print(f"  {Color.GREEN}✓ {model:<25}{Color.RESET} ← Current")
            else:
                print(f"  {Color.WHITE}  {model:<25}{Color.RESET}")
        
        print(f"{Color.DIM}{'='*50}{Color.RESET}")
        print(f"{Color.YELLOW}Use: 'model groq <model_name>' to switch models{Color.RESET}")

    def do_model_stats(self, _):
        stats = self.persistence.config.get("model_stats", {})
        if not stats:
            UI.print_warning("No model statistics available yet.")
            return
            
        print(f"\n{Color.CYAN}📊 AI Model Statistics:{Color.RESET}")
        print(f"{Color.DIM}{'='*60}{Color.RESET}")
        
        total_requests = 0
        total_tokens = 0
        
        for model_name, data in sorted(stats.items()):
            requests = data.get('requests', 0)
            successes = data.get('successes', 0)
            failures = data.get('failures', 0)
            tokens = data.get('tokens_used', 0)
            last_used = data.get('last_used', 'Never')
            
            success_rate = (successes / requests * 100) if requests > 0 else 0
            
            if success_rate >= 90:
                rate_color = Color.GREEN
            elif success_rate >= 70:
                rate_color = Color.YELLOW
            else:
                rate_color = Color.RED
                
            print(f"  {Color.BOLD}{model_name}{Color.RESET}")
            print(f"    Requests: {requests} | {rate_color}Success: {success_rate:.1f}%{Color.RESET}")
            print(f"    Tokens Used: {tokens:,} | Last Used: {last_used[:16]}")
            print(f"    {Color.DIM}{'-'*40}{Color.RESET}")
            
            total_requests += requests
            total_tokens += tokens
            
        print(f"\n{Color.BOLD}Totals:{Color.RESET} {total_requests:,} requests | {total_tokens:,} tokens")
        print(f"{Color.DIM}{'='*60}{Color.RESET}")

    def do_change_model(self, text):
        parts = text.split(maxsplit=2)
        if len(parts) == 1:
            if self.ai and self.ai.get_active_engine():
                engine = self.ai.get_active_engine()
                print(f"Current Model: {engine.model_name}")
                print(f"Engine: {engine.engine_name.upper()}")
            else:
                print("No active AI engine")
                
        elif len(parts) == 3:
            engine_name = parts[1].strip().lower()
            model_name = parts[2].strip()
            
            if engine_name == "gemini":
                self.persistence.config["model"] = model_name
                self.persistence.save()
                if self.ai and 'gemini' in self.ai.engines:
                    try:
                        self.ai.engines['gemini'] = GeminiEngine(self.persistence)
                        UI.print_success(f"Gemini model updated to: {model_name}")
                    except Exception as e:
                        UI.print_error(f"Failed to reload Gemini: {e}", silent=True)
                        
            elif engine_name == "deepseek":
                self.persistence.config["deepseek_model"] = model_name
                self.persistence.save()
                if self.ai and 'deepseek' in self.ai.engines:
                    try:
                        self.ai.engines['deepseek'] = DeepSeekEngine(self.persistence)
                        UI.print_success(f"DeepSeek model updated to: {model_name}")
                    except Exception as e:
                        UI.print_error(f"Failed to reload DeepSeek: {e}", silent=True)
                        
            elif engine_name == "groq":
                self.persistence.config["groq_model"] = model_name
                self.persistence.save()
                if self.ai and 'groq' in self.ai.engines:
                    try:
                        self.ai.engines['groq'] = GroqEngine(self.persistence)
                        UI.print_success(f"Groq model updated to: {model_name}")
                    except Exception as e:
                        UI.print_error(f"Failed to reload Groq: {e}", silent=True)
            else:
                UI.print_error(f"Unknown engine: {engine_name}", silent=True)

    def do_workspace(self, text):
        print(f"Current: {self.workspace.get_current_path()}")

    def do_history(self, text):
        for i, item in enumerate(self.persistence.history[-5:]):
             print(f"{i}. {item['role']}: {str(item['parts'])[:50]}...")
    
    def do_show_summary(self, _):
        """Show last execution summary"""
        if UI.EXECUTION_SUMMARY:
            UI.show_summary()
        else:
            UI.print_warning("No execution summary available yet.")

    def do_clear(self, _=None):
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_help(self, _=None):
        print(f"""
        {Color.CYAN}XEDA v9.3 - Enhanced Commands:{Color.RESET}

        {Color.GREEN}Core Features:{Color.RESET}
          • Auto-package installation 📦
          • Post-execution summary 📊
          • Silent error handling 🔇
          • Deep thinking workflow 🤔

        {Color.YELLOW}Commands:{Color.RESET}
          <task>              : Auto-route to agent or chat
          summary             : Show last execution summary
          engines             : List AI engines
          engine <name>       : Switch engine
          auto                : Toggle auto-execution
          ghost [on/off]      : Toggle ghost mode
          silent              : Toggle error visibility
          replay              : Re-execute last plan
        {Color.YELLOW}Chat Commands:{Color.RESET}
            chats              : List all chat sessions
            chat <ID/num>      : Switch to specific chat
            newchat [title]    : Start new chat session
            currentchat        : Show current chat info
            renamechat <title> : Rename current chat
            deletechat <ID>    : Delete a chat session
            exportchat [format]: Export chat (json/txt)
            clearchat          : Clear current chat messages

        {Color.BLUE}System:{Color.RESET}
          cd [path]           : Change directory
          clear/cls           : Clear screen
          help                : This message
          exit/quit           : Exit

        {Color.MAGENTA}Status Icons:{Color.RESET}
          ✅ Success    ❌ Failure    ⚠️  Warning
          🔄 Retrying  🛠️  Fixing    📦 Installing
          ⏭️  Skipped   ⏸️  Paused    ✨ Excellent
        """)

    def do_exit(self, _=None):
        UI.print_system("Saving & Shutting down...")
        self.persistence.save()
        sys.exit(0)

# ==============================================================================
# 7. INSTALLATION CHECK & MAIN
# ==============================================================================

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import google.generativeai
    except ImportError:
        missing.append("google-generativeai")
    
    try:
        from openai import OpenAI
    except ImportError:
        missing.append("openai")
    
    try:
        import groq
    except ImportError:
        missing.append("groq")
    
    if missing:
        print(f"\n{Color.YELLOW}⚠️  Missing AI dependencies:{Color.RESET}")
        for dep in missing:
            print(f"   - {dep}")
        
        print(f"\n{Color.CYAN}📦 To install:{Color.RESET}")
        print(f"   pip install {' '.join(missing)}")
        
        response = input(f"\n{Color.YELLOW}Install now? (y/n): {Color.RESET}").lower()
        if response == 'y':
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
                print(f"{Color.GREEN}✅ Dependencies installed!{Color.RESET}")
                return True
            except Exception as e:
                print(f"{Color.RED}❌ Installation failed: {e}{Color.RESET}")
                return False
        else:
            print(f"{Color.YELLOW}⚠️  AI features may be disabled.{Color.RESET}")
            print(f"{Color.CYAN}You can still use basic commands and system tools.{Color.RESET}")
            return False
    
    return True

def main():
    """Main entry point"""
    try:
        if not check_dependencies():
            print(f"\n{Color.YELLOW}⚠️  Running with limited features.{Color.RESET}")
        
        app = TerminalApp()
        app.start()
    except KeyboardInterrupt:
        print(f"\n{Color.GREEN}👋 Goodbye!{Color.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Color.RED}💥 Fatal error: {e}{Color.RESET}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()