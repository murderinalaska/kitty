#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
#  kitty.py — v4.7.0
#  · same-folder Module.dll · old-version injection · multi-version launcher
#  · auto-offset sync · executor feature config · fully defensive frontend
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations
import base64, ctypes, ctypes.wintypes, json, mimetypes, os, platform, re, shutil, socket, struct, subprocess, sys, threading, time, urllib.parse, urllib.request, webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import webview; HAS_PYWEBVIEW = True
except ImportError:
    webview = None; HAS_PYWEBVIEW = False
try:
    from PIL import Image, ImageDraw; HAS_PIL = True
except ImportError:
    Image = ImageDraw = None; HAS_PIL = False
try:
    import pystray; HAS_PYSTRAY = True
except ImportError:
    pystray = None; HAS_PYSTRAY = False
try:
    import psutil; HAS_PSUTIL = True
except ImportError:
    psutil = None; HAS_PSUTIL = False

APP_NAME = "Kitty"
APP_VERSION = "4.7.0"
APP_BUILD = "2026.10.15-r3"

APP_DIR = Path.home() / ".kitty_ide"
CONFIG_DIR = APP_DIR / "config"
THEMES_DIR = APP_DIR / "themes"
SCRIPTS_DIR = APP_DIR / "scripts"
AUTOEXEC_DIR = APP_DIR / "autoexec"
CACHE_DIR = APP_DIR / "cache"
PROFILE_DIR = APP_DIR / "profile"
AVATAR_FILE = PROFILE_DIR / "avatar.png"
RECOVERY_FILE = CACHE_DIR / "unsaved_recovery.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

for _f in (APP_DIR, CONFIG_DIR, THEMES_DIR, SCRIPTS_DIR, AUTOEXEC_DIR, CACHE_DIR, PROFILE_DIR):
    try: _f.mkdir(parents=True, exist_ok=True)
    except Exception: pass

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_SCRIPT_EXTS = {".lua", ".luau", ".txt"}
DLL_NAME = "Module.dll"
EXEC_HOST = "127.0.0.1"
EXEC_PORT = 6969

def _runtime_dir() -> Path:
    try:
        if getattr(sys, "frozen", False): return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent
    except Exception: return Path.cwd()
APP_RUNTIME_DIR = _runtime_dir()

DLL_SEARCH_PATHS: List[Path] = [
    APP_RUNTIME_DIR / DLL_NAME,
    APP_RUNTIME_DIR / "bin" / DLL_NAME,
    APP_RUNTIME_DIR / "module" / DLL_NAME,
    APP_RUNTIME_DIR / "modules" / DLL_NAME,
    APP_RUNTIME_DIR.parent / DLL_NAME,
    Path.cwd() / DLL_NAME,
    APP_DIR / "module" / DLL_NAME,
]
def _resolve_dll() -> Optional[Path]:
    for p in DLL_SEARCH_PATHS:
        try:
            if p.is_file(): return p
        except Exception: continue
    return None
def _module_dir() -> Path:
    f = _resolve_dll()
    if f: return f.parent
    d = APP_DIR / "module"; d.mkdir(parents=True, exist_ok=True); return d

BUILTIN_THEMES: Dict[str, Dict[str, str]] = {
    "kitty": {"id":"kitty","name":"Kitty","desc":"Paper & ink","bg":"#f4ede1","panel":"#eae2d2","surface":"#ddd3bf","elevated":"#cfc4ad","hover":"#c3b69b","border":"#d6cbb6","borderStrong":"#b3a586","text":"#141419","text2":"#41414d","text3":"#7a7a88","accent":"#1e3a5f","accent2":"#2f5f92","glow":"rgba(30,58,95,0.20)","selection":"rgba(30,58,95,0.22)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-ink": {"id":"kitty-ink","name":"Kitty Ink","desc":"Cream + black","bg":"#efe9df","panel":"#e5ded1","surface":"#d6cebf","elevated":"#c5bcab","hover":"#b5ab98","border":"#cec4b2","borderStrong":"#9e9180","text":"#0d0d10","text2":"#36363c","text3":"#6e6e75","accent":"#0d0d10","accent2":"#2a2a30","glow":"rgba(13,13,16,0.18)","selection":"rgba(13,13,16,0.20)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-navy": {"id":"kitty-navy","name":"Kitty Navy","desc":"Ink-navy cat","bg":"#f1eadc","panel":"#e6decb","surface":"#d6cdb6","elevated":"#c4b99e","hover":"#b2a688","border":"#cfc4ab","borderStrong":"#8a7d63","text":"#131824","text2":"#3a4256","text3":"#767c8d","accent":"#1e3a5f","accent2":"#3a6ea5","glow":"rgba(30,58,95,0.22)","selection":"rgba(30,58,95,0.24)","success":"#2d8659","warn":"#b87333","danger":"#a83232"},
    "kitty-pink": {"id":"kitty-pink","name":"Kitty Pink","desc":"Grumpy cat","bg":"#f3ebde","panel":"#e8dfce","surface":"#d9cdb6","elevated":"#c8b89c","hover":"#b8a583","border":"#d2c6af","borderStrong":"#8f7f60","text":"#16161a","text2":"#423d42","text3":"#7c7178","accent":"#d97f9a","accent2":"#e898b0","glow":"rgba(217,127,154,0.26)","selection":"rgba(217,127,154,0.28)","success":"#2d8659","warn":"#b87333","danger":"#c4425e"},
    "photo-neon": {"id":"photo-neon","name":"Neon Vibe","desc":"Purple + cyan","bg":"#0a0814","panel":"#120d24","surface":"#1a1235","elevated":"#251a4a","hover":"#32235f","border":"#2b1f52","borderStrong":"#43307a","text":"#ece5ff","text2":"#a08fd6","text3":"#685b98","accent":"#b388ff","accent2":"#22d3ee","glow":"rgba(179,136,255,0.42)","selection":"rgba(179,136,255,0.34)","success":"#22d3ee","warn":"#fb923c","danger":"#f43f5e"},
    "photo-amber": {"id":"photo-amber","name":"Amber Exit","desc":"Christmas night","bg":"#0f0612","panel":"#1a0c1f","surface":"#25132c","elevated":"#301a38","hover":"#3e234a","border":"#3a2044","borderStrong":"#5a3268","text":"#f4e5ec","text2":"#b894a3","text3":"#7c5f6e","accent":"#e63e3e","accent2":"#fb923c","glow":"rgba(230,62,62,0.38)","selection":"rgba(230,62,62,0.30)","success":"#4ade80","warn":"#fbbf24","danger":"#e63e3e"},
    "photo-fire": {"id":"photo-fire","name":"Purple Fire","desc":"Avatar fire","bg":"#06060c","panel":"#0e0c1a","surface":"#15122a","elevated":"#1e1a3c","hover":"#2a2452","border":"#241e48","borderStrong":"#3c3272","text":"#e8e6ff","text2":"#9188c8","text3":"#5a5388","accent":"#7c3aed","accent2":"#a78bfa","glow":"rgba(124,58,237,0.50)","selection":"rgba(124,58,237,0.38)","success":"#34d399","warn":"#fbbf24","danger":"#ef4444"},
    "reaper": {"id":"reaper","name":"Reaper","desc":"Void + acid green","bg":"#05060a","panel":"#0a0d14","surface":"#101520","elevated":"#161d2c","hover":"#1e2638","border":"#1a2233","borderStrong":"#2a3650","text":"#d8e0f0","text2":"#7c8aa8","text3":"#4a5468","accent":"#6ee7b7","accent2":"#34d399","glow":"rgba(110,231,183,0.42)","selection":"rgba(110,231,183,0.28)","success":"#6ee7b7","warn":"#fcd34d","danger":"#f87171"},
    "void-green": {"id":"void-green","name":"Void Green","desc":"Spectral green","bg":"#050806","panel":"#0a100d","surface":"#101a13","elevated":"#16231a","hover":"#1d3022","border":"#1d3826","borderStrong":"#2d5b3b","text":"#e4f8e9","text2":"#a2c5ac","text3":"#65826d","accent":"#52ff8a","accent2":"#18c964","glow":"rgba(82,255,138,0.32)","selection":"rgba(82,255,138,0.24)","success":"#52ff8a","warn":"#f6d365","danger":"#ff647c"},
    "void-mono": {"id":"void-mono","name":"Void Mono","desc":"Black glass","bg":"#050505","panel":"#0c0c0c","surface":"#141414","elevated":"#1b1b1b","hover":"#252525","border":"#292929","borderStrong":"#454545","text":"#f5f5f5","text2":"#c2c2c2","text3":"#777777","accent":"#f5f5f5","accent2":"#bdbdbd","glow":"rgba(245,245,245,0.22)","selection":"rgba(245,245,245,0.20)","success":"#b4f4c0","warn":"#ffd479","danger":"#ff7474"},
    "crimson": {"id":"crimson","name":"Crimson","desc":"Real Executor","bg":"#0b0a0d","panel":"#111015","surface":"#17151b","elevated":"#1d1a21","hover":"#252028","border":"#2a2630","borderStrong":"#3a3440","text":"#f0eaf0","text2":"#a094a0","text3":"#6a5f6c","accent":"#c9303d","accent2":"#e8455a","glow":"rgba(201,48,61,0.22)","selection":"rgba(201,48,61,0.24)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
    "graphite": {"id":"graphite","name":"Graphite","desc":"Neutral","bg":"#0b0d12","panel":"#11141b","surface":"#171b24","elevated":"#1c2230","hover":"#242c3a","border":"#292f3c","borderStrong":"#3a4254","text":"#f0f3f8","text2":"#a0a9b8","text3":"#737e90","accent":"#8b7cff","accent2":"#60a5fa","glow":"rgba(139,124,255,0.22)","selection":"rgba(139,124,255,0.24)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
    "mono": {"id":"mono","name":"Mono","desc":"Grayscale","bg":"#0f0f0f","panel":"#141414","surface":"#1a1a1a","elevated":"#212121","hover":"#282828","border":"#262626","borderStrong":"#363636","text":"#ededed","text2":"#9a9a9a","text3":"#636363","accent":"#d4d4d4","accent2":"#8f8f8f","glow":"rgba(212,212,212,0.14)","selection":"rgba(212,212,212,0.20)","success":"#34d399","warn":"#f59e0b","danger":"#ef4444"},
}

SECTION_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "appearance": {
        "theme":"kitty","activeLogo":"paw","customAccentHex":"",
        "uiDensity":"compact","cornerRadius":"subtle","sidebarIconSize":14,"sidebarLabels":True,
        "topoHeaderPattern":True,"glowIntensity":25,
        "borderEnabled":True,"borderMode":"rainbow","borderColor":"#b388ff","borderWidth":2,
        "useBackgroundImage":False,"bgImageOpacity":40,"bgImageBlur":4,"bgImageSaturation":100,
        "bgScope":"whole","panelOpacity":82,"imageAutoTheme":True,"themeBeforeImage":"kitty",
        "customColors":{"bg":"#0b0d12","panel":"#11141b","surface":"#171b24","border":"#292f3c","text":"#f0f3f8","text2":"#a0a9b8","accent":"#8b7cff","accent2":"#60a5fa"},
        "fxType":"orbs","fxIntensity":"med","fxColorMode":"theme","fxColor1":"#1e3a5f","fxColor2":"#2f5f92","fxOpacity":"normal",
        "customTheme":{"name":"Custom Image","imageFilename":"","imageDataUrl":"","palette":dict(BUILTIN_THEMES["kitty"])},
    },
    "roblox": {
        "autoAttach":False,"autoLaunch":False,"autoInject":False,
        "skipVersionCheck":True,"forceOldVersionBypass":True,"preferSuspendedInject":True,
        "patchClientVersion":True,"useManualMapper":False,
        "launchMode":"latest","selectedVersion":"","injectTimeoutSec":60,
        "raknet":False,"internalUI":False,"bypassAFK":True,
        "execHost":"127.0.0.1","execPort":6969,
    },
    "effects": {
        "masterAnimations":True,"animationSpeed":"normal","hoverEffects":True,"magneticIcons":True,
        "cursorSpotlight":False,"glowEffects":True,"buttonPressAnim":True,"smoothTabTransitions":True,
        "toastAnimations":True,"reduceMotion":False,"ripplesEnabled":True,"staggerEnabled":True,
        "clickParticles":False,"particleColor":"","particleCount":16,
        "cursorTrail":False,"trailIntervalMs":42,
        "waterCursor":True,"waterIntensity":5,"waterSize":76,
        "fogGlow":True,"smoothScrolling":True,
    },
    "editor": {"fontFamily":"Cascadia Code","fontSize":13,"lineHeight":1.55,"lineNumbers":True,"highlightCurrentLine":True,"indentationGuides":True,"wordWrap":False,"autoIndent":True,"autoCloseBrackets":True,"tabSize":4,"minimap":False,"syntaxTheme":"crimson","confirmCloseUnsaved":True,"showWhitespace":False},
    "console": {"showConsole":True,"consolePosition":"bottom","consoleHeight":160,"autoScroll":True,"timestamps":True,"filter":"all","maxLines":2000,"confirmClearOutput":False,"rightSidebarVisible":True,"leftExplorerVisible":True,"activityRailVisible":True,"lastActivity":"explorer"},
    "shortcuts": {"save":"Ctrl+S","newTab":"Ctrl+N","closeTab":"Ctrl+W","reopenClosedTab":"Ctrl+Shift+T","find":"Ctrl+F","replace":"Ctrl+H","commandPalette":"Ctrl+K","toggleConsole":"Ctrl+J"},
    "general": {"launchMaximized":False,"minimizeToTray":False,"streamproof":False,"disguiseMode":False,"performanceMode":"medium","globalToggleKey":"Insert","userName":"lostinthoughts","planName":"Free","licenseStatus":"Active","licenseExpires":"Never","defaultNewTabBehavior":"luau_template"},
    "secret": {"unlocked":False,"reaperMode":False},
}
def get_flat_defaults(): return json.loads(json.dumps(SECTION_DEFAULTS))

DEFAULT_SCRIPTS = [
    {"id":"s_save","title":"saveinstance.luau","folder":"Scripts","content":"saveinstance()\n"},
    {"id":"s_actor","title":"Actor Comm Channel.luau","folder":"Scripts","content":"local id, ch = create_comm_channel()\n"},
    {"id":"s_autoexec","title":"FrameCap.luau","folder":"AutoExec","content":"setfpscap(144)\n"},
]

_main_window: Any = None
_tray_icon: Any = None
_main_hidden: bool = False
_hk_thread: Optional[threading.Thread] = None
_hk_stop = threading.Event()
VK_MAP = {"Insert":0x2D,"Delete":0x2E,"Home":0x24,"End":0x23,"PageUp":0x21,"PageDown":0x22,"F1":0x70,"F2":0x71,"F3":0x72,"F4":0x73,"F5":0x74,"F6":0x75,"F7":0x76,"F8":0x77,"F9":0x78,"F10":0x79,"F11":0x7A,"F12":0x7B}
WM_HOTKEY=0x0312; WM_QUIT=0x0012; MOD_NOREPEAT=0x4000; _HK_ID=0x4B54
PROCESS_ALL_ACCESS=0x1F0FFF; PROCESS_QUERY_LIMITED_INFORMATION=0x1000
MEM_COMMIT=0x1000; MEM_RESERVE=0x2000; MEM_RELEASE=0x8000
PAGE_READWRITE=0x04; CREATE_SUSPENDED=0x00000004

def atomic_write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path); return True
    except Exception: return False

def _get_pid_version(pid: int) -> Optional[str]:
    try:
        k32 = ctypes.windll.kernel32
        k32.OpenProcess.restype = ctypes.wintypes.HANDLE
        k32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
        k32.QueryFullProcessImageNameW.restype = ctypes.wintypes.BOOL
        k32.QueryFullProcessImageNameW.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.LPWSTR, ctypes.POINTER(ctypes.wintypes.DWORD)]
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h: return None
        try:
            sz = ctypes.wintypes.DWORD(32768); buf = ctypes.create_unicode_buffer(sz.value)
            if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(sz)):
                v = os.path.basename(os.path.dirname(buf.value))
                if v.lower().startswith("version-"): return v
        finally: k32.CloseHandle(h)
    except Exception: pass
    return None

def apply_streamproof_win32(enable: bool) -> bool:
    if os.name != "nt" or _main_window is None: return False
    try:
        u32 = ctypes.windll.user32
        flag = 0x00000011 if enable else 0x00000000
        hwnd = getattr(_main_window, "native_handle", None)
        if hwnd: return bool(u32.SetWindowDisplayAffinity(ctypes.wintypes.HWND(hwnd), flag))
    except Exception: pass
    return False

def apply_process_priority_win32(mode: str) -> bool:
    if os.name != "nt": return False
    try:
        k32 = ctypes.windll.kernel32; h = k32.GetCurrentProcess()
        if mode == "low": k32.SetPriorityClass(h, 0x00000020)
        elif mode == "high": k32.SetPriorityClass(h, 0x00000080)
        else: k32.SetPriorityClass(h, 0x00008000)
        return True
    except Exception: return False

def toggle_window_visibility() -> None:
    global _main_hidden
    if _main_window is None: return
    try:
        if not _main_hidden:
            _main_window.hide(); _main_hidden = True
            if _tray_icon: _tray_icon.visible = True
        else:
            _main_window.show(); _main_hidden = False
            if _tray_icon: _tray_icon.visible = False
    except Exception: pass

def start_global_hotkey(key_name: str) -> bool:
    global _hk_thread
    stop_global_hotkey()
    if os.name != "nt" or not key_name: return False
    vk = VK_MAP.get(key_name)
    if vk is None and len(key_name) == 1 and key_name.isalnum(): vk = ord(key_name.upper())
    if vk is None: return False
    def _loop():
        try:
            u32 = ctypes.windll.user32
            if not u32.RegisterHotKey(None, _HK_ID, MOD_NOREPEAT, vk): return
            msg = ctypes.wintypes.MSG()
            try:
                while not _hk_stop.is_set():
                    r = u32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                    if r in (0, -1): break
                    if msg.message == WM_HOTKEY and msg.wParam == _HK_ID: toggle_window_visibility()
                    u32.TranslateMessage(ctypes.byref(msg)); u32.DispatchMessageW(ctypes.byref(msg))
            finally: u32.UnregisterHotKey(None, _HK_ID)
        except Exception: pass
    _hk_stop.clear(); _hk_thread = threading.Thread(target=_loop, daemon=True); _hk_thread.start(); return True

def stop_global_hotkey() -> None:
    global _hk_thread
    if _hk_thread and _hk_thread.is_alive():
        _hk_stop.set()
        if os.name == "nt":
            try: ctypes.windll.user32.PostThreadMessageW(_hk_thread.ident, WM_QUIT, 0, 0)
            except Exception: pass
        _hk_thread.join(timeout=1.0)
    _hk_thread = None; _hk_stop.clear()

def init_system_tray() -> None:
    global _tray_icon
    if not (HAS_PYSTRAY and HAS_PIL) or _tray_icon is not None: return
    try:
        img = Image.new("RGB", (64, 64), color="#f4ede1"); draw = ImageDraw.Draw(img)
        draw.ellipse([24,40,40,54], fill="#1e3a5f"); draw.ellipse([14,26,24,38], fill="#1e3a5f")
        draw.ellipse([24,22,34,34], fill="#1e3a5f"); draw.ellipse([34,22,44,34], fill="#1e3a5f"); draw.ellipse([44,26,54,38], fill="#1e3a5f")
        def on_show(i, it):
            global _main_hidden
            if _main_window: _main_window.show()
            _main_hidden = False
        def on_exit(i, it):
            try: i.stop()
            except Exception: pass
            stop_global_hotkey()
            if _main_window:
                try: _main_window.destroy()
                except Exception: pass
        menu = pystray.Menu(pystray.MenuItem("Restore Kitty", on_show, default=True), pystray.MenuItem("Exit", on_exit))
        _tray_icon = pystray.Icon("kitty_ide", img, APP_NAME, menu)
        threading.Thread(target=_tray_icon.run, daemon=True).start()
    except Exception: _tray_icon = None

def list_installed_versions() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    lad = os.environ.get("LOCALAPPDATA")
    if not lad: return out
    root = Path(lad) / "Roblox" / "Versions"
    if not root.is_dir(): return out
    try:
        for d in sorted(root.iterdir()):
            if not d.is_dir(): continue
            exe = d / "RobloxPlayerBeta.exe"
            if not exe.is_file(): continue
            try: mt = exe.stat().st_mtime
            except Exception: mt = 0
            out.append({"name": d.name, "path": str(d), "exe": str(exe), "modified": mt})
    except Exception: pass
    out.sort(key=lambda r: -r["modified"]); return out

# ── Injection ────────────────────────────────────────────────────────────────
def _prep_k32():
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = ctypes.wintypes.HANDLE
    k32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    k32.VirtualAllocEx.restype = ctypes.c_void_p
    k32.VirtualAllocEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
    k32.WriteProcessMemory.restype = ctypes.wintypes.BOOL
    k32.WriteProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.ReadProcessMemory.restype = ctypes.wintypes.BOOL
    k32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    k32.GetModuleHandleW.restype = ctypes.wintypes.HMODULE
    k32.GetModuleHandleW.argtypes = [ctypes.wintypes.LPCWSTR]
    k32.GetProcAddress.restype = ctypes.c_void_p
    k32.GetProcAddress.argtypes = [ctypes.wintypes.HMODULE, ctypes.wintypes.LPCSTR]
    k32.CreateRemoteThread.restype = ctypes.wintypes.HANDLE
    k32.CreateRemoteThread.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD)]
    k32.WaitForSingleObject.restype = ctypes.wintypes.DWORD
    k32.WaitForSingleObject.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD]
    k32.VirtualFreeEx.restype = ctypes.wintypes.BOOL
    k32.VirtualFreeEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, ctypes.wintypes.DWORD]
    k32.CloseHandle.restype = ctypes.wintypes.BOOL
    k32.CloseHandle.argtypes = [ctypes.wintypes.HANDLE]
    k32.GetLastError.restype = ctypes.wintypes.DWORD
    k32.GetLastError.argtypes = []
    return k32

def _wpm(k32, h, addr, data: bytes) -> bool:
    try:
        buf = ctypes.create_string_buffer(data, len(data)); n = ctypes.c_size_t(0)
        return bool(k32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, len(data), ctypes.byref(n)))
    except Exception: return False

def _rpm(k32, h, addr, size):
    try:
        buf = ctypes.create_string_buffer(size); n = ctypes.c_size_t(0)
        if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n)):
            return buf.raw[:n.value]
    except Exception: pass
    return None

def inject_loadlibrary(pid: int, dll: str) -> Dict[str, Any]:
    k32 = _prep_k32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        err = k32.GetLastError(); return {"ok": False, "error": f"OpenProcess failed (err {err})"}
    try:
        pb = dll.encode("mbcs") + b"\x00"
        addr = k32.VirtualAllocEx(h, None, len(pb), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr: return {"ok": False, "error": "VirtualAllocEx failed"}
        if not _wpm(k32, h, addr, pb): return {"ok": False, "error": "WriteProcessMemory failed"}
        kk = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kk, b"LoadLibraryA")
        if not ll: return {"ok": False, "error": "GetProcAddress failed"}
        tid = ctypes.wintypes.DWORD()
        th = k32.CreateRemoteThread(h, None, 0, ll, addr, 0, ctypes.byref(tid))
        if not th: return {"ok": False, "error": "CreateRemoteThread failed"}
        k32.WaitForSingleObject(th, 15000); k32.CloseHandle(th); k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
        return {"ok": True, "method": "loadlibrary"}
    finally: k32.CloseHandle(h)

def inject_ntcreatethread(pid: int, dll: str) -> Dict[str, Any]:
    try: ntdll = ctypes.WinDLL("ntdll")
    except Exception as e: return {"ok": False, "error": f"ntdll: {e}"}
    k32 = _prep_k32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h: return {"ok": False, "error": "OpenProcess failed"}
    try:
        pb = dll.encode("utf-16-le") + b"\x00\x00"
        addr = k32.VirtualAllocEx(h, None, len(pb), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr: return {"ok": False, "error": "VirtualAllocEx failed"}
        if not _wpm(k32, h, addr, pb): return {"ok": False, "error": "WriteProcessMemory failed"}
        kk = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kk, b"LoadLibraryW")
        if not ll: return {"ok": False, "error": "GetProcAddress failed"}
        NCT = ntdll.NtCreateThreadEx
        NCT.restype = ctypes.c_long
        NCT.argtypes = [ctypes.POINTER(ctypes.wintypes.HANDLE), ctypes.wintypes.DWORD, ctypes.c_void_p, ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_void_p]
        th = ctypes.wintypes.HANDLE()
        status = NCT(ctypes.byref(th), 0x1FFFFF, None, h, ctypes.c_void_p(ll), ctypes.c_void_p(addr), 0, 0, 0, 0, None)
        if status != 0 or not th: return {"ok": False, "error": f"NtCreateThreadEx failed (0x{status & 0xFFFFFFFF:X})"}
        k32.WaitForSingleObject(th, 15000); k32.CloseHandle(th); k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
        return {"ok": True, "method": "ntcreatethread"}
    finally: k32.CloseHandle(h)

def inject_early_bird(pid: int, dll: str) -> Dict[str, Any]:
    k32 = _prep_k32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h: return {"ok": False, "error": "OpenProcess failed"}
    try:
        pb = dll.encode("mbcs") + b"\x00"
        addr = k32.VirtualAllocEx(h, None, len(pb), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        if not addr: return {"ok": False, "error": "VirtualAllocEx failed"}
        if not _wpm(k32, h, addr, pb): return {"ok": False, "error": "WriteProcessMemory failed"}
        kk = k32.GetModuleHandleW("kernel32.dll")
        ll = k32.GetProcAddress(kk, b"LoadLibraryA")
        if not ll: return {"ok": False, "error": "GetProcAddress failed"}
        tid = ctypes.wintypes.DWORD()
        th = k32.CreateRemoteThread(h, None, 0, ll, addr, 0, ctypes.byref(tid))
        if not th: return {"ok": False, "error": "CreateRemoteThread failed"}
        k32.WaitForSingleObject(th, 15000); k32.CloseHandle(th)
        def _later():
            time.sleep(3.0)
            try: k32.VirtualFreeEx(h, addr, 0, MEM_RELEASE)
            except Exception: pass
            try: k32.CloseHandle(h)
            except Exception: pass
        threading.Thread(target=_later, daemon=True).start()
        return {"ok": True, "method": "early-bird"}
    except Exception as e:
        try: k32.CloseHandle(h)
        except Exception: pass
        return {"ok": False, "error": str(e)}

def _launch_suspended(exe: str) -> Dict[str, Any]:
    try:
        class _SI(ctypes.Structure):
            _fields_ = [("cb", ctypes.wintypes.DWORD), ("lpReserved", ctypes.wintypes.LPWSTR), ("lpDesktop", ctypes.wintypes.LPWSTR), ("lpTitle", ctypes.wintypes.LPWSTR), ("dwX", ctypes.wintypes.DWORD), ("dwY", ctypes.wintypes.DWORD), ("dwXSize", ctypes.wintypes.DWORD), ("dwYSize", ctypes.wintypes.DWORD), ("dwXCountChars", ctypes.wintypes.DWORD), ("dwYCountChars", ctypes.wintypes.DWORD), ("dwFillAttribute", ctypes.wintypes.DWORD), ("dwFlags", ctypes.wintypes.DWORD), ("wShowWindow", ctypes.wintypes.WORD), ("cbReserved2", ctypes.wintypes.WORD), ("lpReserved2", ctypes.c_void_p), ("hStdInput", ctypes.wintypes.HANDLE), ("hStdOutput", ctypes.wintypes.HANDLE), ("hStdError", ctypes.wintypes.HANDLE)]
        class _PI(ctypes.Structure):
            _fields_ = [("hProcess", ctypes.wintypes.HANDLE), ("hThread", ctypes.wintypes.HANDLE), ("dwProcessId", ctypes.wintypes.DWORD), ("dwThreadId", ctypes.wintypes.DWORD)]
        k32 = ctypes.windll.kernel32
        si = _SI(); si.cb = ctypes.sizeof(si)
        pi = _PI()
        cmd = f'"{exe}"'
        ok = k32.CreateProcessW(None, ctypes.c_wchar_p(cmd), None, None, False, CREATE_SUSPENDED, None, ctypes.c_wchar_p(str(Path(exe).parent)), ctypes.byref(si), ctypes.byref(pi))
        if not ok:
            err = ctypes.GetLastError(); return {"ok": False, "error": f"CreateProcessW failed (err {err})"}
        return {"ok": True, "pid": int(pi.dwProcessId), "process_handle": int(pi.hProcess or 0), "thread_handle": int(pi.hThread or 0)}
    except Exception as e: return {"ok": False, "error": str(e)}

def _resume(thread_handle: int) -> bool:
    try: return ctypes.windll.kernel32.ResumeThread(ctypes.wintypes.HANDLE(thread_handle)) != 0xFFFFFFFF
    except Exception: return False

def _close(h: int) -> None:
    try: ctypes.windll.kernel32.CloseHandle(ctypes.wintypes.HANDLE(h))
    except Exception: pass

def _launch_normal(exe: str) -> Dict[str, Any]:
    try:
        p = subprocess.Popen([exe], close_fds=True)
        return {"ok": True, "pid": p.pid}
    except Exception as e: return {"ok": False, "error": str(e)}

def patch_client_version_string(pid: int, latest: str) -> Dict[str, Any]:
    if not latest or not latest.startswith("version-"): return {"ok": False, "error": "no latest version"}
    k32 = _prep_k32()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h: return {"ok": False, "error": "OpenProcess failed"}
    try:
        vers = list_installed_versions()
        own = next((v["name"] for v in vers if v["name"] != latest), None)
        if not own: return {"ok": False, "error": "no old version string"}
        needle = own.encode("ascii"); repl = latest.encode("ascii")
        if len(needle) != len(repl): return {"ok": False, "error": "version string length mismatch"}
        class _MBI(ctypes.Structure):
            _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p), ("AllocationProtect", ctypes.wintypes.DWORD), ("RegionSize", ctypes.c_size_t), ("State", ctypes.wintypes.DWORD), ("Protect", ctypes.wintypes.DWORD), ("Type", ctypes.wintypes.DWORD)]
        VQE = k32.VirtualQueryEx; VQE.restype = ctypes.c_size_t
        VQE.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(_MBI), ctypes.c_size_t]
        addr = 0; hits = 0; scanned = 0
        while scanned < (2 << 30):
            mbi = _MBI()
            if not VQE(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)): break
            base = int(mbi.BaseAddress or 0); size = int(mbi.RegionSize or 0)
            if size == 0: break
            if mbi.State == 0x1000 and mbi.Protect in (0x02, 0x04, 0x20, 0x40, 0x80) and base > 0 and size < (128 << 20):
                CH = 1 << 20; off = 0
                while off < size:
                    r = min(CH, size - off); buf = _rpm(k32, h, base + off, r)
                    if buf:
                        i = 0
                        while True:
                            i = buf.find(needle, i)
                            if i == -1: break
                            if _wpm(k32, h, base + off + i, repl): hits += 1
                            i += len(needle)
                    off += r
            scanned += size; addr = base + size
            if addr <= 0: break
        return {"ok": hits > 0, "hits": hits}
    finally: k32.CloseHandle(h)

# ── Backend ──────────────────────────────────────────────────────────────────
class KittyBackend:
    def __init__(self):
        self._lock = threading.RLock()
        self.runtime_mode = "pywebview" if HAS_PYWEBVIEW else "browser"
        self.is_maximized = False
        self.attached = False
        self._attached_pid: Optional[int] = None
        self._attached_version = ""
        self._attached_method = ""
        self.settings = self._load_settings()
        self.scripts = self._load_scripts()
        threading.Thread(target=self._offset_watcher, daemon=True).start()

    def _offsets_paths(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return {"offsets": CACHE_DIR / "offsets.json", "version": CACHE_DIR / "offsets_version.txt", "meta": CACHE_DIR / "offsets_meta.json"}

    def _fetch(self, url: str, timeout: int = 25) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}-Offsets/{APP_VERSION}"})
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()

    def sync_offsets(self, force: bool = False):
        with self._lock:
            p = self._offsets_paths()
            cached = ""
            if p["version"].is_file():
                try: cached = p["version"].read_text(encoding="utf-8").strip()
                except Exception: pass
            live = cached
            try:
                live = self._fetch("https://offsets.imtheo.lol/roblox/version", 10).decode("utf-8", "ignore").strip()
            except Exception as e:
                if p["offsets"].is_file(): return {"ok": True, "cached": True, "version": cached, "note": f"probe failed: {e}"}
                return {"ok": False, "error": f"probe failed: {e}"}
            need = force or not p["offsets"].is_file() or (live and live != cached)
            if not need: return {"ok": True, "cached": True, "version": cached}
            try:
                raw = self._fetch("https://offsets.imtheo.lol/offsets.json", 30)
                if not raw or len(raw) < 64: return {"ok": False, "error": "payload too small"}
                p["offsets"].write_bytes(raw)
                if live: p["version"].write_text(live, encoding="utf-8")
                atomic_write_json(p["meta"], {"version": live or cached or "unknown", "fetched": datetime.now().isoformat(), "bytes": len(raw)})
                return {"ok": True, "fetched": True, "version": live or cached, "bytes": len(raw), "changed": live != cached}
            except Exception as e: return {"ok": False, "error": str(e)}

    def offsets_status(self):
        p = self._offsets_paths()
        cached = ""
        if p["version"].is_file():
            try: cached = p["version"].read_text(encoding="utf-8").strip()
            except Exception: pass
        dll = _resolve_dll()
        return {"ok": True, "cached_version": cached, "offsets_cached": p["offsets"].is_file(),
                "module_dir": str(_module_dir()), "runtime_dir": str(APP_RUNTIME_DIR),
                "dll_path": str(dll) if dll else "", "dll_found": bool(dll)}

    def _offset_watcher(self):
        time.sleep(2.0)
        while True:
            try: self.sync_offsets()
            except Exception: pass
            time.sleep(30 * 60)

    def _write_module_config(self, pid=None, version=""):
        md = _module_dir()
        try: md.mkdir(parents=True, exist_ok=True)
        except Exception: return
        s = self.settings; rb = s.get("roblox", {}); gen = s.get("general", {}); p = self._offsets_paths()
        cfg = {
            "schema": 3, "app": APP_NAME, "appVersion": APP_VERSION,
            "writtenAt": datetime.now().isoformat(),
            "targetPid": pid, "clientVersion": version,
            "raknet": bool(rb.get("raknet", False)),
            "internalUI": bool(rb.get("internalUI", False)),
            "bypassAFK": bool(rb.get("bypassAFK", True)),
            "skipVersionCheck": bool(rb.get("skipVersionCheck", True)),
            "forceOldVersionBypass": bool(rb.get("forceOldVersionBypass", True)),
            "autoExec": bool(rb.get("autoAttach", False)),
            "injectTimeoutSec": int(rb.get("injectTimeoutSec", 60)),
            "offsetsFile": str(p["offsets"]),
            "offsetsVersion": p["version"].read_text(encoding="utf-8").strip() if p["version"].is_file() else "",
            "autoexecDir": str(AUTOEXEC_DIR), "scriptsDir": str(SCRIPTS_DIR),
            "cacheDir": str(CACHE_DIR), "dataDir": str(APP_DIR), "moduleDir": str(md),
            "execHost": str(rb.get("execHost", EXEC_HOST)),
            "execPort": int(rb.get("execPort", EXEC_PORT)),
            "userName": str(gen.get("userName", "")),
            "planName": str(gen.get("planName", "")),
        }
        atomic_write_json(md / "kitty_module_config.json", cfg)
        try:
            env = [f"KITTY_{k.upper()}={v}" for k, v in cfg.items() if isinstance(v, (str, int, bool))]
            (md / "kitty_module.env").write_text("\n".join(env) + "\n", encoding="utf-8")
        except Exception: pass

    def _pre_inject(self, pid=None, ver=""):
        try: self.sync_offsets()
        except Exception: pass
        try: self._write_module_config(pid, ver)
        except Exception: pass

    def _deep_merge(self, default, loaded):
        out = {}
        for k, dv in default.items():
            if k not in loaded: out[k] = json.loads(json.dumps(dv)); continue
            lv = loaded[k]
            if isinstance(dv, dict) and isinstance(lv, dict): out[k] = self._deep_merge(dv, lv)
            elif isinstance(dv, bool): out[k] = bool(lv)
            elif isinstance(dv, int) and not isinstance(dv, bool):
                try: out[k] = int(lv)
                except Exception: out[k] = dv
            elif isinstance(dv, float):
                try: out[k] = float(lv)
                except Exception: out[k] = dv
            elif isinstance(dv, str): out[k] = str(lv) if lv is not None else dv
            elif isinstance(dv, list): out[k] = lv if isinstance(lv, list) else list(dv)
            else: out[k] = lv
        return out

    def _load_settings(self):
        with self._lock:
            defaults = get_flat_defaults()
            if not SETTINGS_FILE.is_file():
                atomic_write_json(SETTINGS_FILE, defaults); return defaults
            try:
                raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                if not isinstance(raw, dict): raise ValueError("root")
                merged = self._deep_merge(defaults, raw)
            except Exception:
                merged = defaults; atomic_write_json(SETTINGS_FILE, merged)
            ct = merged.get("appearance", {}).get("customTheme", {})
            img = ct.get("imageFilename", "")
            if img:
                ip = THEMES_DIR / Path(img).name
                if ip.is_file():
                    try:
                        m = mimetypes.guess_type(ip.name)[0] or "image/png"
                        ct["imageDataUrl"] = f"data:{m};base64,{base64.b64encode(ip.read_bytes()).decode('ascii')}"
                    except Exception: ct["imageDataUrl"] = ""
                else: ct["imageFilename"] = ""; ct["imageDataUrl"] = ""
            return merged

    def _save_settings(self):
        with self._lock:
            c = json.loads(json.dumps(self.settings))
            ct = c.get("appearance", {}).get("customTheme", {})
            if ct.get("imageFilename"): ct["imageDataUrl"] = ""
            return atomic_write_json(SETTINGS_FILE, c)

    def _load_scripts(self):
        items = [dict(x) for x in DEFAULT_SCRIPTS]
        for fname, fpath in (("Scripts", SCRIPTS_DIR), ("AutoExec", AUTOEXEC_DIR)):
            try:
                for p in sorted(fpath.glob("*")):
                    disabled = fname == "AutoExec" and p.name.lower().endswith((".lua.disabled", ".luau.disabled", ".txt.disabled"))
                    if p.is_file() and (p.suffix.lower() in ALLOWED_SCRIPT_EXTS or disabled):
                        try:
                            items.append({"id": f"disk_{fname}_{p.stem}_{abs(hash(p.name))%9999}", "title": p.name, "folder": fname, "content": p.read_text(encoding="utf-8", errors="replace"), "disabled": disabled})
                        except Exception: pass
            except Exception: pass
        return items

    def get_initial_state(self):
        with self._lock:
            return {"ok": True,
                "app": {"name": APP_NAME, "version": APP_VERSION, "build": APP_BUILD, "runtimeMode": self.runtime_mode,
                        "platform": f"{platform.system()} {platform.release()}", "pythonVersion": platform.python_version(),
                        "settingsPath": str(SETTINGS_FILE), "runtimeDir": str(APP_RUNTIME_DIR),
                        "themesDir": str(THEMES_DIR), "scriptsDir": str(SCRIPTS_DIR),
                        "hasPil": HAS_PIL, "hasPystray": HAS_PYSTRAY, "hasPsutil": HAS_PSUTIL},
                "settings": self.settings, "sectionDefaults": SECTION_DEFAULTS, "builtinThemes": BUILTIN_THEMES,
                "scripts": self.scripts, "attached": self.attached, "profilePicture": self._profile_pic(),
                "offsets": self.offsets_status(), "installedVersions": list_installed_versions()}

    def update_settings(self, payload):
        with self._lock:
            if not isinstance(payload, dict): return {"ok": False}
            self.settings = self._deep_merge(self.settings, payload)
            saved = self._save_settings()
            gen = self.settings.get("general", {})
            apply_streamproof_win32(bool(gen.get("streamproof", False)))
            apply_process_priority_win32(str(gen.get("performanceMode", "medium")))
            if _main_window is not None:
                try: _main_window.set_title("Spotify" if gen.get("disguiseMode") else APP_NAME)
                except Exception: pass
            try: self._write_module_config(self._attached_pid, self._attached_version)
            except Exception: pass
            return {"ok": saved, "settings": self.settings}

    def reset_all_settings(self):
        with self._lock:
            self.settings = get_flat_defaults(); self._save_settings()
            return {"ok": True, "settings": self.settings}

    def _profile_pic(self):
        if not AVATAR_FILE.is_file(): return None
        try:
            m = mimetypes.guess_type(AVATAR_FILE.name)[0] or "image/png"
            return f"data:{m};base64,{base64.b64encode(AVATAR_FILE.read_bytes()).decode('ascii')}"
        except Exception: return None

    def pick_theme_image(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            r = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=("Images (*.png;*.jpg;*.jpeg;*.webp)", "All (*.*)"))
            if not r: return {"ok": False, "cancelled": True}
            p = Path(r[0] if isinstance(r, (list, tuple)) else r)
            if p.suffix.lower() not in ALLOWED_IMAGE_EXTS: return {"ok": False, "error": "Unsupported image"}
            raw = p.read_bytes()
            m = mimetypes.guess_type(p.name)[0] or "image/png"
            return {"ok": True, "filename": p.name, "dataUrl": f"data:{m};base64,{base64.b64encode(raw).decode('ascii')}"}
        except Exception as e: return {"ok": False, "error": str(e)}

    def pick_profile_image(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            r = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=("Images (*.png;*.jpg;*.jpeg;*.webp)", "All (*.*)"))
            if not r: return {"ok": False, "cancelled": True}
            p = Path(r[0] if isinstance(r, (list, tuple)) else r)
            raw = p.read_bytes(); PROFILE_DIR.mkdir(parents=True, exist_ok=True); AVATAR_FILE.write_bytes(raw)
            m = mimetypes.guess_type(p.name)[0] or "image/png"
            return {"ok": True, "dataUrl": f"data:{m};base64,{base64.b64encode(raw).decode('ascii')}"}
        except Exception as e: return {"ok": False, "error": str(e)}

    def save_profile_image(self, payload):
        try:
            u = str(payload.get("dataUrl") or "")
            if not u.startswith("data:image/"): return {"ok": False, "error": "Invalid"}
            _, b64 = u.split(",", 1); raw = base64.b64decode(b64)
            if len(raw) < 32: return {"ok": False, "error": "Corrupted"}
            PROFILE_DIR.mkdir(parents=True, exist_ok=True); AVATAR_FILE.write_bytes(raw)
            return {"ok": True}
        except Exception as e: return {"ok": False, "error": str(e)}

    def remove_profile_image(self):
        try:
            if AVATAR_FILE.is_file(): AVATAR_FILE.unlink()
            return {"ok": True}
        except Exception as e: return {"ok": False, "error": str(e)}

    def save_custom_theme_image(self, payload):
        with self._lock:
            try:
                fn = str(payload.get("filename") or "wallpaper.png")
                u = str(payload.get("dataUrl") or "")
                if not u.startswith("data:image/"): return {"ok": False, "error": "Invalid"}
                hdr, b64 = u.split(",", 1); raw = base64.b64decode(b64)
                if len(raw) < 32: return {"ok": False, "error": "Corrupted"}
                ext = Path(fn).suffix.lower()
                if ext not in ALLOWED_IMAGE_EXTS: ext = ".png"
                stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", Path(fn).stem)[:32]
                name = f"theme_{stem}_{int(time.time())}{ext}"
                (THEMES_DIR / name).write_bytes(raw)
                ct = self.settings["appearance"]["customTheme"]
                ct["name"] = Path(fn).stem[:28] or "Custom Image"
                ct["imageFilename"] = name; ct["imageDataUrl"] = u
                self._save_settings()
                return {"ok": True, "settings": self.settings}
            except Exception as e: return {"ok": False, "error": str(e)}

    def remove_custom_theme_image(self):
        with self._lock:
            ct = self.settings["appearance"]["customTheme"]
            old = ct.get("imageFilename", "")
            if old:
                p = THEMES_DIR / Path(old).name
                if p.is_file():
                    try: p.unlink()
                    except Exception: pass
            ct["imageFilename"] = ""; ct["imageDataUrl"] = ""
            ct["palette"] = dict(BUILTIN_THEMES["kitty"])
            self.settings["appearance"]["useBackgroundImage"] = False
            self._save_settings()
            return {"ok": True, "settings": self.settings}

    def open_script_file(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False, "fallback": True}
        try:
            r = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=("Luau & Lua (*.luau;*.lua;*.txt)", "All (*.*)"))
            if not r: return {"ok": False, "cancelled": True}
            p = Path(r[0] if isinstance(r, (list, tuple)) else r)
            return {"ok": True, "filename": p.name, "content": p.read_text(encoding="utf-8", errors="replace"), "path": str(p)}
        except Exception as e: return {"ok": False, "error": str(e)}

    def save_script_file(self, payload):
        raw = str(payload.get("filename") or "Untitled.luau")
        auto = raw.replace("\\", "/").lower().startswith("autoexec/")
        direct = bool(payload.get("direct", False))
        fn = Path(raw).name
        if not Path(fn).suffix: fn += ".luau"
        content = str(payload.get("content") or "")
        if auto:
            try:
                AUTOEXEC_DIR.mkdir(parents=True, exist_ok=True)
                (AUTOEXEC_DIR / fn).write_text(content, encoding="utf-8")
                return {"ok": True, "filename": fn, "folder": "AutoExec"}
            except Exception as e: return {"ok": False, "error": str(e)}
        if direct:
            try:
                SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
                (SCRIPTS_DIR / fn).write_text(content, encoding="utf-8")
                return {"ok": True, "filename": fn, "direct": True}
            except Exception as e: return {"ok": False, "error": str(e)}
        if HAS_PYWEBVIEW and _main_window is not None:
            try:
                r = _main_window.create_file_dialog(webview.SAVE_DIALOG, save_filename=fn, file_types=("Luau (*.luau)", "Lua (*.lua)", "Text (*.txt)"))
                if not r: return {"ok": False, "cancelled": True}
                p = Path(r if isinstance(r, str) else r[0])
                p.write_text(content, encoding="utf-8")
                return {"ok": True, "filename": p.name, "path": str(p)}
            except Exception as e: return {"ok": False, "error": str(e)}
        (SCRIPTS_DIR / fn).write_text(content, encoding="utf-8")
        return {"ok": True, "filename": fn, "browserDownload": True}

    def manage_script_file(self, payload):
        try:
            f = str(payload.get("folder") or ""); a = str(payload.get("action") or "")
            fn = Path(str(payload.get("filename") or "")).name
            if not fn or fn in {".", ".."} or Path(fn).name != fn: return {"ok": False, "error": "Invalid filename"}
            base = SCRIPTS_DIR if f == "Scripts" else (AUTOEXEC_DIR if f == "AutoExec" else None)
            if not base: return {"ok": False, "error": "Unsupported folder"}
            base.mkdir(parents=True, exist_ok=True); t = base / fn
            if not t.is_file(): return {"ok": False, "error": "Not found"}
            if a == "delete": t.unlink(); return {"ok": True, "filename": fn}
            if f == "AutoExec" and a == "disable":
                if fn.lower().endswith(".disabled"): return {"ok": False, "error": "Already disabled"}
                dest = t.with_name(t.name + ".disabled")
                if dest.exists(): return {"ok": False, "error": "Exists"}
                t.rename(dest); return {"ok": True, "filename": dest.name, "disabled": True}
            if f == "Scripts" and a == "rename":
                nn = Path(str(payload.get("newFilename") or "")).name
                if not nn or Path(nn).suffix.lower() not in ALLOWED_SCRIPT_EXTS: return {"ok": False, "error": "Extension"}
                dest = base / nn
                if dest.exists() and dest != t: return {"ok": False, "error": "In use"}
                t.rename(dest); return {"ok": True, "filename": dest.name}
            return {"ok": False, "error": "Unsupported action"}
        except Exception as e: return {"ok": False, "error": str(e)}

    def export_settings_json(self):
        with self._lock:
            c = json.loads(json.dumps(self.settings))
            c.get("appearance", {}).get("customTheme", {})["imageDataUrl"] = ""
            raw = json.dumps(c, indent=2)
            if HAS_PYWEBVIEW and _main_window is not None:
                try:
                    r = _main_window.create_file_dialog(webview.SAVE_DIALOG, save_filename="kitty_settings.json", file_types=("JSON (*.json)", "All (*.*)"))
                    if not r: return {"ok": False, "cancelled": True}
                    Path(r if isinstance(r, str) else r[0]).write_text(raw, encoding="utf-8")
                    return {"ok": True}
                except Exception as e: return {"ok": False, "error": str(e)}
            return {"ok": True, "json": raw, "browserDownload": True}

    def import_settings_json(self, payload):
        with self._lock:
            t = str(payload.get("json") or "")
            if not t and HAS_PYWEBVIEW and _main_window is not None:
                try:
                    r = _main_window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=("JSON (*.json)", "All (*.*)"))
                    if not r: return {"ok": False, "cancelled": True}
                    t = Path(r[0] if isinstance(r, (list, tuple)) else r).read_text(encoding="utf-8")
                except Exception as e: return {"ok": False, "error": str(e)}
            try:
                p = json.loads(t)
                if not isinstance(p, dict): raise ValueError("root")
                self.settings = self._deep_merge(get_flat_defaults(), p); self._save_settings()
                return {"ok": True, "settings": self.settings}
            except Exception as e: return {"ok": False, "error": str(e)}

    def open_data_folder(self):
        try:
            if os.name == "nt": os.startfile(str(APP_DIR))
            elif sys.platform == "darwin": os.system(f'open "{APP_DIR}"')
            else: os.system(f'xdg-open "{APP_DIR}"')
            return {"ok": True}
        except Exception as e: return {"ok": False, "error": str(e)}

    def _roblox_pids(self):
        if HAS_PSUTIL:
            pids = []
            for p in psutil.process_iter(["pid", "name"]):
                try: n = (p.info.get("name") or "").lower()
                except Exception: continue
                if "robloxplayerbeta" in n: pids.append(p.info["pid"])
            return pids
        if os.name == "nt":
            try:
                o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq RobloxPlayerBeta.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=8)
                pids = []
                for line in (o.stdout or "").splitlines():
                    if "robloxplayerbeta" in line.lower():
                        m = re.search(r"\",\"(\d+)\"", line)
                        if m: pids.append(int(m.group(1)))
                return pids
            except Exception: return []
        return []

    def kill_roblox(self):
        killed = 0
        for pid in self._roblox_pids():
            try:
                if HAS_PSUTIL: psutil.Process(pid).kill(); killed += 1
                else: subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=8); killed += 1
            except Exception: pass
        self.attached = False; self._attached_pid = None; self._attached_version = ""
        return {"ok": True, "killed": killed}

    def get_status(self):
        try:
            c = socket.create_connection((EXEC_HOST, EXEC_PORT), 1); c.close(); att = True
        except OSError: att = False
        pids = self._roblox_pids()
        return {"attached": att, "pids": pids, "roblox_running": bool(pids),
                "attached_pid": self._attached_pid, "attached_version": self._attached_version,
                "attached_method": self._attached_method}

    def _do_inject(self, pid: int, method: str):
        dll = _resolve_dll()
        if not dll: return {"ok": False, "error": f"{DLL_NAME} not found"}
        ds = str(dll)
        if method == "early-bird": r = inject_early_bird(pid, ds)
        elif method == "ntcreatethread": r = inject_ntcreatethread(pid, ds)
        else: r = inject_loadlibrary(pid, ds)
        if r.get("ok"):
            self.attached = True; self._attached_pid = pid
            self._attached_version = _get_pid_version(pid) or ""
            self._attached_method = r.get("method", method)
        return r

    def simulate_attach(self, target_pid=None):
        with self._lock:
            pids = self._roblox_pids()
            if not pids: return {"ok": False, "error": "Roblox not running"}
            pid = int(target_pid) if target_pid else pids[0]
            if pid not in pids: return {"ok": False, "error": f"PID {pid} not active"}
            ver = _get_pid_version(pid) or ""
            self._pre_inject(pid, ver)
            if not _resolve_dll(): return {"ok": False, "error": f"{DLL_NAME} not found"}
            rb = self.settings.get("roblox", {})
            order = ["ntcreatethread", "loadlibrary"] if rb.get("useManualMapper") else ["loadlibrary", "ntcreatethread"]
            last = None
            for m in order:
                r = self._do_inject(pid, m)
                if r.get("ok"):
                    return {"ok": True, "attached": True, "pid": pid, "message": f"Injected {DLL_NAME} into PID {pid}", "clientVersion": self._attached_version, "method": r.get("method", m)}
                last = r.get("error")
            return {"ok": False, "error": last or "all methods failed"}

    def launch_and_inject(self, version: str = ""):
        with self._lock:
            dll = _resolve_dll()
            if not dll: return {"ok": False, "error": f"{DLL_NAME} not found next to kitty.py"}
            running = self._roblox_pids()
            if running: return {"ok": False, "error": f"Roblox already running (PID {running[0]})", "already_running": True}
            installed = list_installed_versions()
            if not installed: return {"ok": False, "error": "No Roblox versions found"}
            target = next((v for v in installed if v["name"] == version), None) or installed[0]
            rb = self.settings.get("roblox", {})
            prefer_susp = rb.get("preferSuspendedInject", True)
            force_old = rb.get("forceOldVersionBypass", True)
            use_patch = rb.get("patchClientVersion", True)
            self._pre_inject(None, target["name"])
            result = {"ok": False}
            if prefer_susp:
                l = _launch_suspended(target["exe"])
                if l.get("ok"):
                    pid = l["pid"]
                    self._pre_inject(pid, target["name"])
                    inj = self._do_inject(pid, "early-bird")
                    _resume(l["thread_handle"])
                    time.sleep(1.0)
                    _close(l["process_handle"]); _close(l["thread_handle"])
                    if inj.get("ok"):
                        return {"ok": True, "attached": True, "pid": pid, "message": f"Suspended launch + early-bird into {target['name']}", "method": "early-bird", "version": target["name"]}
                    time.sleep(2.0)
                    if _get_pid_version(pid):
                        retry = self._do_inject(pid, "loadlibrary")
                        if retry.get("ok"):
                            return {"ok": True, "attached": True, "pid": pid, "message": f"Fallback into {target['name']}", "method": "loadlibrary", "version": target["name"]}
                        result = {"ok": False, "error": f"early-bird: {inj.get('error')}; fallback: {retry.get('error')}"}
                    else: result = {"ok": False, "error": inj.get("error") or "early-bird failed"}
            if not result.get("ok") and force_old:
                l = _launch_normal(target["exe"])
                if not l.get("ok"): return l
                pid = l["pid"]
                self._pre_inject(pid, target["name"])
                deadline = time.time() + int(rb.get("injectTimeoutSec", 60))
                while time.time() < deadline:
                    if pid in self._roblox_pids(): break
                    time.sleep(0.5)
                time.sleep(1.5)
                if use_patch and target["name"] != installed[0]["name"]:
                    try: patch_client_version_string(pid, installed[0]["name"])
                    except Exception: pass
                r = self._do_inject(pid, "loadlibrary")
                if r.get("ok"):
                    return {"ok": True, "attached": True, "pid": pid, "message": f"Launched + injected into {target['name']}", "method": "loadlibrary", "version": target["name"]}
                result = {"ok": False, "error": r.get("error") or "inject failed"}
            return result

    def simulate_execute(self, payload):
        code = str(payload.get("code") or "").strip()
        if not code: return {"ok": False, "error": "Empty"}
        try:
            c = socket.create_connection((EXEC_HOST, EXEC_PORT), timeout=5)
            c.sendall(struct.pack("!I", len(code.encode("utf-8"))) + code.encode("utf-8")); c.close()
            return {"ok": True, "title": str(payload.get("title") or "Untitled"), "lines": len(code.splitlines()), "bytes": len(code)}
        except OSError as e: return {"ok": False, "error": f"Module not attached ({e})"}

    def window_minimize(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            try: _main_window.minimize()
            except Exception: pass
        return {"ok": True}
    def window_maximize(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            try:
                if self.is_maximized: _main_window.restore(); self.is_maximized = False
                else: _main_window.maximize(); self.is_maximized = True
            except Exception: pass
        else: self.is_maximized = not self.is_maximized
        return {"ok": True, "maximized": self.is_maximized}
    def window_resize(self, payload):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False}
        try:
            w = int(payload.get("width") or 0); h = int(payload.get("height") or 0)
            if w < 400 or h < 300: return {"ok": False}
            try: _main_window.resize(w, h)
            except AttributeError: pass
            return {"ok": True}
        except Exception as e: return {"ok": False, "error": str(e)}
    def window_get_rect(self):
        if not HAS_PYWEBVIEW or _main_window is None: return {"ok": False}
        try: return {"ok": True, "width": int(_main_window.width or 0), "height": int(_main_window.height or 0)}
        except Exception: return {"ok": False}
    def window_close(self):
        if HAS_PYWEBVIEW and _main_window is not None:
            if self.settings.get("general", {}).get("minimizeToTray") and _tray_icon is not None:
                toggle_window_visibility(); return {"ok": True, "hidToTray": True}
            try: _main_window.destroy()
            except Exception: pass
        return {"ok": True}


# ═══════════════════════════════════════════════════════════════════════════════
#  FRONTEND — defensive, null-safe
# ═══════════════════════════════════════════════════════════════════════════════

KITTY_HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>Kitty</title>
<style>
:root{--bg:#f4ede1;--panel:#eae2d2;--surface:#ddd3bf;--elevated:#cfc4ad;--hover:#c3b69b;--border:#d6cbb6;--border-strong:#b3a586;--divider:#e0d6c2;--text:#141419;--text2:#41414d;--text3:#7a7a88;--accent:#1e3a5f;--accent-hover:#2f5f92;--accent-soft:rgba(30,58,95,0.16);--glow:rgba(30,58,95,0.20);--selection:rgba(30,58,95,0.22);--success:#2d8659;--warn:#b87333;--danger:#a83232;--panel-opacity:0.82;--bg-img-opacity:0;--border-color:transparent;--border-width:2px;--fx-opacity:0.55;--font-ui:'Inter','Segoe UI',system-ui,sans-serif;--font-mono:'Cascadia Code',Consolas,monospace;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--text);font-family:var(--font-ui);font-size:12px;user-select:none;-webkit-font-smoothing:antialiased;}
button{font:inherit;color:inherit;background:none;border:none;cursor:pointer;position:relative;overflow:hidden;}
input,select{font:inherit;color:inherit;outline:none;}
svg{display:block;}
::-webkit-scrollbar{width:10px;height:10px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:5px;border:2px solid transparent;background-clip:padding-box;}
::-webkit-scrollbar-thumb:hover{background:var(--border-strong);background-clip:padding-box;border:2px solid transparent;}
#wallpaper{position:fixed;inset:0;z-index:1;pointer-events:none;background-size:cover;background-position:center;background-repeat:no-repeat;opacity:var(--bg-img-opacity);}
#bg-fx{position:fixed;inset:0;z-index:2;pointer-events:none;overflow:hidden;opacity:var(--fx-opacity);}
.fx-orb{position:absolute;border-radius:50%;filter:blur(70px);background:radial-gradient(circle,var(--accent),transparent 70%);animation:orbDrift 14s ease-in-out infinite;}
@keyframes orbDrift{0%,100%{transform:translate(0,0) scale(1);opacity:.5;}50%{transform:translate(40px,-50px) scale(1.15);opacity:.85;}}
.fx-spark{position:absolute;bottom:-10px;width:2.5px;height:2.5px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent);animation:sparkRise 12s linear infinite;opacity:0;}
@keyframes sparkRise{0%{transform:translateY(0) scale(0);opacity:0;}15%,85%{opacity:1;}100%{transform:translateY(-100vh) scale(1);opacity:0;}}
#spotlight{position:fixed;inset:0;z-index:3;pointer-events:none;opacity:0;background:radial-gradient(360px circle at var(--cx,-500px) var(--cy,-500px),var(--glow),transparent 70%);}
#water-canvas{position:fixed;inset:0;width:100%;height:100%;z-index:4;pointer-events:none;opacity:.78;mix-blend-mode:screen;}
#border-layer{position:fixed;inset:0;z-index:9999;pointer-events:none;display:none;}
body.border-on #border-layer{display:block;}
body.border-rainbow #border-layer{background:linear-gradient(120deg,#ff0066,#ffcc00,#00e676,#00b0ff,#b388ff,#ec4899,#ff0066);background-size:400% 400%;animation:borderShift 8s linear infinite;opacity:.85;}
body.border-solid #border-layer{background:var(--border-color);opacity:.9;}
body.border-on #border-layer{-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);mask-composite:exclude;padding:var(--border-width);}
@keyframes borderShift{0%{background-position:0% 50%;}100%{background-position:400% 50%;}}
#app{position:relative;z-index:5;width:100vw;height:100vh;display:flex;flex-direction:column;background:transparent;}
#titlebar{height:34px;min-height:34px;display:flex;align-items:center;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-bottom:1px solid var(--divider);padding:0 8px 0 12px;-webkit-app-region:drag;position:relative;}
.tb-left{display:flex;align-items:center;gap:8px;}
.brand-logo{min-width:22px;height:22px;color:var(--accent);display:inline-flex;align-items:center;justify-content:center;}
.brand-logo svg{width:20px;height:20px;}
.brand-name{font-family:'Brush Script MT',cursive;font-size:18px;font-style:italic;color:var(--text);}
.brand-ver{font-size:10px;color:var(--text3);padding:1px 5px;border:1px solid var(--border);border-radius:4px;font-family:var(--font-mono);}
.tb-center{position:absolute;left:50%;transform:translateX(-50%);display:flex;gap:2px;padding:2px;border-radius:6px;background:color-mix(in srgb,var(--surface) 80%,transparent);border:1px solid var(--divider);}
.nav-icon{width:30px;height:22px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);transition:all .15s;}
.nav-icon svg{width:14px;height:14px;stroke:currentColor;stroke-width:1.75;fill:none;}
.nav-icon:hover{color:var(--text2);background:var(--surface);}
.nav-icon.active{color:var(--text);background:var(--surface);}
.nav-icon.active::after{content:"";position:absolute;left:6px;right:6px;bottom:-3px;height:2px;background:var(--accent);border-radius:2px;}
.tb-right{margin-left:auto;display:flex;gap:2px;}
.wbtn{width:34px;height:26px;display:inline-flex;align-items:center;justify-content:center;color:var(--text2);border-radius:4px;}
.wbtn svg{width:11px;height:11px;stroke:currentColor;stroke-width:1.4;fill:none;}
.wbtn:hover{background:var(--surface);color:var(--text);}
.wbtn.close:hover{background:#c42b1c;color:#fff;}
#body{flex:1;min-height:0;display:flex;}
#activity{width:44px;min-width:44px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-right:1px solid var(--divider);display:flex;flex-direction:column;align-items:center;padding:8px 0;gap:2px;}
#activity.hidden{display:none;}
.act-btn{width:30px;height:30px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);position:relative;}
.act-btn svg{width:15px;height:15px;stroke:currentColor;stroke-width:1.7;fill:none;}
.act-btn:hover{color:var(--text2);background:var(--surface);}
.act-btn.active{color:var(--text);background:var(--surface);}
.act-btn.active::before{content:"";position:absolute;left:-8px;top:6px;bottom:6px;width:2px;background:var(--accent);border-radius:2px;}
.act-sep{flex:1;}
#explorer{width:240px;min-width:0;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-right:1px solid var(--divider);display:flex;flex-direction:column;overflow:hidden;transition:width .24s,opacity .15s;}
#explorer.hidden{width:0;min-width:0;opacity:0;pointer-events:none;border-right-color:transparent;}
.explorer-head{height:32px;padding:0 8px 0 10px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);}
.explorer-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);}
.explorer-collapse{width:22px;height:22px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);}
.explorer-collapse:hover{background:var(--surface);color:var(--text);}
.explorer-collapse svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2;}
.explorer-body{flex:1;overflow-y:auto;padding:6px 4px;}
.panel-section{padding:8px;}
.field{display:flex;align-items:center;gap:6px;height:26px;background:var(--bg);border:1px solid var(--divider);border-radius:4px;padding:0 8px;}
.field:focus-within{border-color:var(--accent);}
.field svg{width:12px;height:12px;color:var(--text3);stroke:currentColor;fill:none;stroke-width:1.8;flex-shrink:0;}
.field input{flex:1;background:transparent;border:none;font-size:11px;color:var(--text);min-width:0;}
.tree-group{margin-bottom:8px;padding:0 4px;}
.tree-group-head{display:flex;align-items:center;gap:4px;padding:4px 6px;color:var(--text3);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;cursor:pointer;border-radius:4px;}
.tree-group-head:hover{color:var(--text2);}
.tree-group-head svg{width:9px;height:9px;stroke:currentColor;fill:none;stroke-width:2;transition:transform .15s;}
.tree-group[data-open="false"] .tree-group-head svg{transform:rotate(-90deg);}
.tree-group[data-open="false"] .tree-items{max-height:0;opacity:0;padding:0;}
.tree-group-count{margin-left:auto;color:var(--text3);font-size:9px;background:var(--bg);padding:1px 5px;border-radius:8px;}
.tree-items{display:flex;flex-direction:column;gap:1px;padding-left:10px;overflow:hidden;max-height:900px;transition:max-height .24s,opacity .15s;}
.tree-item{display:flex;align-items:center;gap:7px;min-height:22px;padding:0 7px;border-radius:4px;color:var(--text2);font-size:11px;cursor:pointer;white-space:nowrap;overflow:hidden;position:relative;}
.tree-item:hover{background:var(--surface);color:var(--text);}
.tree-item.active{background:var(--surface);color:var(--text);}
.tree-item>svg{width:14px;height:14px;min-width:14px;flex:0 0 14px;color:var(--text3);}
.tree-item>span{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;}
.tree-item-state{margin-left:auto;font-size:8px;color:var(--warn);border:1px solid color-mix(in srgb,var(--warn) 35%,transparent);padding:1px 4px;border-radius:4px;}
#workspace{flex:1;min-width:0;display:flex;flex-direction:column;background:transparent;}
#view-home{flex:1;overflow-y:auto;padding:24px;display:none;flex-direction:column;gap:16px;}
#view-home.active{display:flex;}
.home-head{display:flex;align-items:center;gap:12px;margin-bottom:4px;}
.home-head-icon{min-width:52px;height:52px;padding:6px 10px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;background:var(--surface);border:1px solid var(--border);color:var(--accent);}
.home-head-icon svg{width:26px;height:26px;}
.home-head-title{font-family:'Brush Script MT',cursive;font-size:26px;font-style:italic;color:var(--text);}
.home-head-sub{font-size:12px;color:var(--text2);margin-top:2px;}
.home-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;}
.home-card{background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border:1px solid var(--border);border-radius:6px;padding:12px 14px;}
.home-card-head{display:flex;align-items:center;gap:8px;margin-bottom:10px;}
.home-card-icon{width:20px;height:20px;color:var(--accent);display:inline-flex;align-items:center;justify-content:center;}
.home-card-icon svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;}
.home-card-title{font-size:12px;font-weight:600;color:var(--text);}
.home-card-row{display:flex;justify-content:space-between;padding:6px 0;font-size:11px;border-bottom:1px solid var(--divider);}
.home-card-row:last-child{border-bottom:none;}
.home-card-row .l{color:var(--text3);}
.home-card-row .v{color:var(--text);font-family:var(--font-mono);font-size:10px;}
.home-card-row .v.ok{color:var(--success);}
.home-actions{display:flex;gap:8px;flex-wrap:wrap;}
.home-action{display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:11px;cursor:pointer;}
.home-action:hover{border-color:var(--accent);background:var(--elevated);}
.home-action svg{width:14px;height:14px;color:var(--accent);stroke:currentColor;fill:none;stroke-width:1.8;}
#view-editor{flex:1;min-height:0;display:none;flex-direction:column;}
#view-editor.active{display:flex;}
#tabstrip{height:32px;display:flex;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-bottom:1px solid var(--divider);overflow:hidden;}
#tabs{display:flex;flex:1;overflow-x:auto;}
.tab{display:inline-flex;align-items:center;gap:8px;padding:0 10px 0 12px;height:100%;max-width:190px;color:var(--text3);font-size:11px;border-right:1px solid var(--divider);cursor:pointer;flex-shrink:0;position:relative;}
.tab:hover{color:var(--text2);background:var(--surface);}
.tab.active{color:var(--text);background:var(--bg);}
.tab.active::before{content:"";position:absolute;left:0;right:0;bottom:0;height:1.5px;background:var(--accent);}
.tab-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tab-dirty{width:5px;height:5px;border-radius:50%;background:var(--accent);display:none;flex-shrink:0;}
.tab.dirty .tab-dirty{display:block;}
.tab-close{width:14px;height:14px;border-radius:3px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);flex-shrink:0;opacity:0;}
.tab:hover .tab-close,.tab.active .tab-close{opacity:1;}
.tab-close:hover{background:var(--surface);color:var(--text);}
.tab-close svg{width:8px;height:8px;stroke:currentColor;fill:none;stroke-width:1.6;}
#tab-new{width:32px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);flex-shrink:0;}
#tab-new:hover{background:var(--surface);color:var(--text);}
#tab-new svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:2;}
#tab-toolbar{display:flex;gap:2px;padding:0 8px;border-left:1px solid var(--divider);align-items:center;}
#tab-toolbar button{color:var(--text3);width:26px;height:22px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;}
#tab-toolbar button svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.7;}
#tab-toolbar button:hover{background:var(--surface);color:var(--text);}
#editor-body{flex:1;min-height:0;display:flex;position:relative;}
#gutter{width:46px;min-width:46px;padding:10px 8px 10px 4px;color:var(--text3);font-family:var(--font-mono);font-size:13px;line-height:1.55;text-align:right;overflow:hidden;white-space:pre;}
#gutter.hidden{display:none;}
.gln{padding-right:2px;}
.gln.active{color:var(--text2);}
#editor-stage{flex:1;min-width:0;position:relative;overflow:hidden;}
#syntax,#editor-input{position:absolute;inset:0;width:100%;height:100%;padding:10px 14px;font-family:var(--font-mono);font-size:13px;line-height:1.55;tab-size:4;white-space:pre;}
#syntax{z-index:2;pointer-events:none;color:var(--text);overflow:hidden;}
#editor-input{z-index:3;resize:none;background:transparent;color:transparent;caret-color:var(--text);border:none;}
#editor-input.word-wrap,#syntax.word-wrap{white-space:pre-wrap;}
.tk-kw{color:#c9303d;font-weight:600;}.tk-fn{color:#2f5f92;}.tk-str{color:#2d8659;}.tk-num{color:#b87333;}.tk-com{color:var(--text3);font-style:italic;}
#find-bar{position:absolute;top:8px;right:24px;z-index:30;background:var(--surface);border:1px solid var(--border-strong);border-radius:6px;padding:8px 10px;display:none;flex-direction:column;gap:6px;}
#find-bar.open{display:flex;}
.find-row{display:flex;gap:6px;align-items:center;}
.find-row input{width:180px;height:24px;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:0 8px;color:var(--text);font-size:11px;}
.mini-btn{height:24px;padding:0 8px;background:var(--elevated);border:1px solid var(--border);border-radius:4px;color:var(--text2);font-size:10px;}
#bottom-panel{height:160px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-top:1px solid var(--divider);display:flex;flex-direction:column;}
#bottom-panel.hidden{display:none;}
#bottom-resizer{height:4px;cursor:ns-resize;background:transparent;display:flex;align-items:center;justify-content:center;}
#bottom-resizer:hover{background:var(--surface);}
#bottom-resizer::before{content:"";width:30px;height:2px;background:var(--border-strong);}
#bottom-resizer.hidden{display:none;}
#bottom-tabs{height:28px;padding:0 10px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);}
.bottom-tabs-left{display:flex;gap:10px;height:100%;}
.btab{height:100%;display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--text3);border-bottom:1.5px solid transparent;padding:0 2px;cursor:pointer;}
.btab:hover{color:var(--text2);}
.btab.active{color:var(--text);border-bottom-color:var(--accent);}
.btab svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:1.8;}
.bottom-tabs-right{display:flex;gap:4px;}
.bottom-tabs-right button{padding:3px 8px;border-radius:4px;color:var(--text3);font-size:10px;}
.bottom-tabs-right button:hover{background:var(--surface);color:var(--text);}
#bottom-body{flex:1;min-height:0;overflow-y:auto;padding:8px 10px;font-family:var(--font-mono);font-size:10px;line-height:1.55;user-select:text;}
.log-line{display:flex;gap:8px;padding:1px 0;}
.log-time{color:var(--text3);flex-shrink:0;}
.log-msg{color:var(--text2);word-break:break-word;}
.log-line.info .log-msg{color:var(--text);}.log-line.ok .log-msg{color:var(--success);}.log-line.warn .log-msg{color:var(--warn);}.log-line.err .log-msg{color:var(--danger);}
#bottom-body:empty::before{content:"Terminal ready.";color:var(--text3);font-style:italic;}
#rail{width:40px;min-width:40px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-left:1px solid var(--divider);display:flex;flex-direction:column;align-items:center;padding:8px 0;gap:6px;}
#rail.hidden{display:none;}
.rail-btn{width:30px;height:30px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text3);position:relative;}
.rail-btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:1.7;}
.rail-btn:hover{color:var(--text);background:var(--surface);}
.rail-btn.primary{background:var(--accent);color:#fff;}
.rail-btn.primary:hover{background:var(--accent-hover);}
.rail-sep{width:22px;height:1px;background:var(--divider);}
.rail-spacer{flex:1;}
#statusbar{height:22px;min-height:22px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-top:1px solid var(--divider);display:flex;align-items:center;padding:0 10px;font-size:10px;color:var(--text3);gap:10px;position:relative;}
.sb-group{display:flex;align-items:center;gap:10px;}
.sb-spacer{flex:1;}
.sb-item{display:inline-flex;align-items:center;gap:5px;}
.sb-item svg{width:11px;height:11px;stroke:currentColor;fill:none;stroke-width:1.8;}
.sb-path{font-family:var(--font-mono);max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.sb-dot{width:6px;height:6px;border-radius:50%;background:var(--text3);}
.sb-dot.on{background:var(--success);box-shadow:0 0 6px var(--success);}
.sb-btn{padding:2px 6px;border-radius:4px;color:var(--text3);font-size:10px;display:inline-flex;align-items:center;gap:4px;cursor:pointer;}
.sb-btn:hover{background:var(--surface);color:var(--text);}
#inject-menu{position:absolute;bottom:calc(22px + 4px);right:8px;min-width:200px;background:var(--surface);border:1px solid var(--border-strong);border-radius:6px;padding:4px;display:none;z-index:200;}
#inject-menu.open{display:block;}
.menu-row{display:flex;align-items:center;gap:8px;padding:6px 10px;border-radius:4px;color:var(--text2);font-size:11px;cursor:pointer;}
.menu-row svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.8;}
.menu-row:hover{background:var(--hover);color:var(--text);}
.menu-row.danger:hover{color:var(--danger);}
#view-settings{flex:1;min-height:0;display:none;}
#view-settings.active{display:flex;}
#settings{flex:1;display:flex;}
#settings-nav{width:220px;min-width:220px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border-right:1px solid var(--divider);padding:12px 10px;display:flex;flex-direction:column;gap:10px;overflow-y:auto;}
.s-head{display:flex;align-items:center;gap:8px;padding:0 6px 8px;}
.s-head button{width:22px;height:22px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text2);}
.s-head button:hover{background:var(--surface);color:var(--text);}
.s-head svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:2;}
.s-title{font-size:13px;font-weight:600;color:var(--text);}
.s-search{display:flex;align-items:center;gap:6px;height:26px;background:var(--bg);border:1px solid var(--divider);border-radius:4px;padding:0 8px;}
.s-search:focus-within{border-color:var(--accent);}
.s-search svg{width:12px;height:12px;color:var(--text3);stroke:currentColor;fill:none;stroke-width:1.8;}
.s-search input{flex:1;background:transparent;border:none;font-size:11px;color:var(--text);min-width:0;}
#settings-cats{display:flex;flex-direction:column;gap:1px;}
.s-cat{display:flex;align-items:center;gap:10px;padding:6px 8px;border-radius:4px;color:var(--text2);font-size:11px;cursor:pointer;position:relative;text-align:left;width:100%;}
.s-cat svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:1.7;flex-shrink:0;}
.s-cat:hover{background:var(--surface);color:var(--text);}
.s-cat.active{background:var(--surface);color:var(--text);}
.s-cat.active::before{content:"";position:absolute;left:-2px;top:6px;bottom:6px;width:2px;background:var(--accent);border-radius:2px;}
.s-cat-name{flex:1;min-width:0;}
#settings-body{flex:1;min-width:0;overflow-y:auto;padding:24px 32px;scroll-behavior:smooth;}
.s-section-head{display:flex;flex-direction:column;gap:3px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--divider);position:relative;}
.s-section-head::after{content:"";position:absolute;bottom:-1px;left:0;width:60px;height:2px;background:var(--accent);}
.s-section-title{font-size:15px;font-weight:600;color:var(--text);}
.s-section-sub{font-size:11px;color:var(--text3);}
.s-subhead{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);margin:20px 0 10px;display:flex;align-items:center;gap:10px;}
.s-subhead::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 40%,var(--divider)),transparent);}
.s-subhead:first-child{margin-top:0;}
.s-row{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 12px;background:color-mix(in srgb,var(--panel) calc(var(--panel-opacity)*100%),transparent);border:1px solid var(--border);border-radius:6px;margin-bottom:6px;}
.s-row.vertical{flex-direction:column;align-items:stretch;}
.s-row:hover{border-color:var(--border-strong);}
.s-row-info{display:flex;flex-direction:column;gap:3px;min-width:0;flex:1;}
.s-row-title{font-size:12px;color:var(--text);font-weight:500;}
.s-row-desc{font-size:11px;color:var(--text3);line-height:1.5;}
.s-row-control{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.s-row.vertical .s-row-control{justify-content:flex-start;}
.sw{width:34px;height:18px;border-radius:9px;position:relative;background:var(--surface);border:1px solid var(--border-strong);cursor:pointer;flex-shrink:0;transition:background .15s,border-color .15s;}
.sw::after{content:"";position:absolute;top:1px;left:1px;width:14px;height:14px;border-radius:50%;background:var(--text3);transition:transform .2s,background .15s;}
.sw.on{background:var(--accent);border-color:var(--accent);}
.sw.on::after{transform:translateX(16px);background:#fff;}
.slider-wrap{display:flex;align-items:center;gap:8px;min-width:220px;}
input[type=range].slider{-webkit-appearance:none;appearance:none;width:140px;height:3px;border-radius:2px;background:var(--border-strong);cursor:pointer;}
input[type=range].slider::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;border-radius:50%;background:var(--accent);border:2px solid var(--bg);}
.slider-val{min-width:46px;text-align:right;font-family:var(--font-mono);font-size:10px;color:var(--text2);}
.ui-select,.ui-text{height:26px;padding:0 10px;background:var(--bg);border:1px solid var(--border-strong);border-radius:4px;color:var(--text);min-width:130px;font-size:11px;}
.ui-select:focus,.ui-text:focus{border-color:var(--accent);}
.ui-text.mono{font-family:var(--font-mono);}
input[type=color].mini-color{width:28px;height:26px;border:none;background:transparent;cursor:pointer;padding:0;}
.btn{height:26px;padding:0 12px;background:var(--elevated);border:1px solid var(--border-strong);border-radius:4px;color:var(--text2);font-size:11px;display:inline-flex;align-items:center;gap:6px;cursor:pointer;}
.btn svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:1.8;}
.btn:hover{background:var(--hover);color:var(--text);}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff;}
.btn.primary:hover{background:var(--accent-hover);}
.btn.danger{color:var(--danger);}
.btn.danger:hover{background:color-mix(in srgb,var(--danger) 12%,transparent);border-color:var(--danger);}
.segmented{display:inline-flex;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:3px;gap:2px;}
.segmented button{background:transparent;border:none;color:var(--text3);padding:4px 10px;border-radius:4px;font-size:10px;font-weight:600;cursor:pointer;}
.segmented button.active{background:var(--accent);color:#fff;}
.segmented button:not(.active):hover{color:var(--text);background:var(--surface);}
.theme-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-top:8px;}
.theme-card{padding:10px 12px;border-radius:6px;border:1px solid var(--border);background:var(--bg);cursor:pointer;display:flex;flex-direction:column;gap:6px;position:relative;}
.theme-card:hover{border-color:var(--border-strong);}
.theme-card.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.theme-card-head{display:flex;align-items:center;justify-content:space-between;}
.theme-card-name{font-size:12px;color:var(--text);font-weight:600;}
.theme-check{font-size:8px;font-weight:800;color:var(--text3);}
.theme-card.active .theme-check{color:var(--accent);}
.theme-dots{display:flex;gap:3px;}
.theme-dot{width:10px;height:10px;border-radius:3px;border:1px solid rgba(0,0,0,0.14);}
.theme-card-desc{font-size:10px;color:var(--text3);}
.bg-thumbs{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;}
.bg-thumb{width:74px;height:48px;border-radius:4px;background:var(--bg);border:1px solid var(--border);cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--text3);overflow:hidden;}
.bg-thumb.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.bg-thumb img{width:100%;height:100%;object-fit:cover;}
.version-list{display:flex;flex-direction:column;gap:6px;width:100%;margin-top:8px;}
.version-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:6px;}
.version-row.active{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent);}
.version-row .vinfo{display:flex;flex-direction:column;gap:2px;min-width:0;flex:1;}
.version-row .vname{font-family:var(--font-mono);font-size:11px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.version-row .vmeta{font-size:9px;color:var(--text3);}
#cmd-back,#app-modal-back{position:fixed;inset:0;z-index:500;background:rgba(0,0,0,0.5);display:none;align-items:flex-start;justify-content:center;padding-top:90px;}
#cmd-back.open{display:flex;}
#app-modal-back.open{display:flex;align-items:center;padding-top:0;}
#cmd-modal{width:460px;background:var(--panel);border:1px solid var(--border-strong);border-radius:8px;overflow:hidden;}
#cmd-input{width:100%;height:42px;padding:0 12px;background:var(--bg);border:none;border-bottom:1px solid var(--divider);color:var(--text);font-size:12px;}
#cmd-list{max-height:340px;overflow-y:auto;padding:4px;}
.cmd-row{padding:6px 10px;border-radius:4px;display:flex;align-items:center;justify-content:space-between;color:var(--text2);font-size:12px;cursor:pointer;}
.cmd-row:hover,.cmd-row.selected{background:var(--surface);color:var(--text);}
.cmd-kb{font-family:var(--font-mono);font-size:10px;color:var(--text3);}
#app-modal{width:min(430px,calc(100vw - 34px));background:var(--panel);border:1px solid var(--border-strong);border-radius:10px;overflow:hidden;}
#app-modal-head{padding:18px 20px 12px;display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--divider);}
#app-modal-title{font-size:14px;font-weight:700;color:var(--text);}
#app-modal-message{padding:16px 20px 8px;color:var(--text2);font-size:12px;line-height:1.65;white-space:pre-wrap;}
#app-modal-input{display:block;width:calc(100% - 40px);margin:10px 20px 16px;padding:10px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--bg);color:var(--text);}
#app-modal-actions{display:flex;justify-content:flex-end;gap:8px;padding:8px 20px 18px;}
#tab-ctx,#file-ctx{position:fixed;z-index:620;min-width:170px;background:var(--panel);border:1px solid var(--border-strong);border-radius:6px;padding:4px;display:none;}
#tab-ctx.open,#file-ctx.open{display:block;}
.ctx-row{padding:6px 10px;border-radius:4px;color:var(--text2);font-size:11px;cursor:pointer;}
.ctx-row:hover{background:var(--hover);color:var(--text);}
.ctx-row.danger:hover{color:var(--danger);}
.ctx-sep{height:1px;background:var(--divider);margin:4px 0;}
#clients-backdrop{position:fixed;inset:0;z-index:640;background:rgba(0,0,0,0.55);opacity:0;pointer-events:none;transition:opacity .24s;}
#clients-backdrop.open{opacity:1;pointer-events:auto;}
#clients{position:fixed;top:0;right:0;bottom:0;width:380px;max-width:90vw;background:var(--panel);border-left:1px solid var(--border-strong);z-index:650;display:flex;flex-direction:column;transform:translateX(100%);transition:transform .3s;}
#clients.open{transform:translateX(0);}
#clients .head{padding:12px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--divider);}
#clients .title{font-size:13px;font-weight:600;color:var(--text);display:flex;align-items:center;gap:8px;}
#clients .title svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.8;color:var(--accent);}
#clients .close{width:26px;height:26px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:var(--text2);}
#clients .close:hover{background:var(--surface);color:var(--text);}
#clients-list{flex:1;overflow-y:auto;padding:10px;}
.clients-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;gap:10px;padding:20px;color:var(--text3);}
.clients-empty h3{font-size:13px;color:var(--text2);font-weight:600;}
.client-row{display:flex;align-items:center;justify-content:space-between;padding:10px;background:var(--surface);border:1px solid var(--border);border-radius:6px;margin-bottom:6px;}
.client-info{display:flex;flex-direction:column;gap:2px;}
.client-pid{font-family:var(--font-mono);font-size:12px;color:var(--text);}
.client-state{font-size:10px;color:var(--text3);}
.client-state.attached{color:var(--success);}
.client-attach{padding:5px 12px;background:var(--accent);color:#fff;border-radius:4px;font-size:11px;cursor:pointer;}
.client-attach:hover{background:var(--accent-hover);}
.client-attach:disabled{background:var(--border-strong);cursor:default;}
#attach-overlay{position:fixed;inset:0;z-index:700;background:rgba(0,0,0,0.55);display:none;align-items:center;justify-content:center;}
#attach-overlay.open{display:flex;}
.attach-box{background:var(--panel);border:1px solid var(--border-strong);border-radius:8px;padding:24px;min-width:320px;text-align:center;}
.spinner{width:40px;height:40px;margin:0 auto 12px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .9s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.attach-step{font-family:var(--font-mono);font-size:11px;color:var(--text2);min-height:20px;}
#toasts{position:fixed;right:12px;bottom:34px;z-index:800;display:flex;flex-direction:column;gap:6px;pointer-events:none;}
.toast{pointer-events:auto;min-width:220px;max-width:320px;padding:8px 12px;background:var(--surface);border:1px solid var(--border-strong);border-radius:6px;display:flex;align-items:center;gap:8px;font-size:11px;color:var(--text);transition:opacity .3s;}
.toast-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0;}
.toast.ok .toast-dot{background:var(--success);}.toast.warn .toast-dot{background:var(--warn);}.toast.err .toast-dot{background:var(--danger);}
#loading{position:fixed;inset:0;z-index:99999;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;transition:opacity .3s;}
#loading.hidden{opacity:0;pointer-events:none;}
.load-logo{width:56px;height:56px;border-radius:50%;background:var(--surface);border:1px solid var(--border-strong);display:flex;align-items:center;justify-content:center;color:var(--accent);}
.load-logo svg{width:30px;height:30px;}
.load-title{font-family:'Brush Script MT',cursive;font-size:28px;font-style:italic;color:var(--text);}
.load-bar{width:180px;height:2px;background:var(--surface);border-radius:1px;overflow:hidden;}
.load-bar-fill{height:100%;width:0;background:var(--accent);transition:width .3s;}
#resize-grip{position:fixed;bottom:0;right:0;width:18px;height:18px;z-index:900;cursor:nwse-resize;display:flex;align-items:flex-end;justify-content:flex-end;padding:3px;color:var(--text3);opacity:.6;}
#resize-grip:hover{opacity:1;color:var(--accent);}
#resize-grip svg{width:12px;height:12px;stroke:currentColor;fill:none;stroke-width:2;}
</style></head>
<body data-theme="kitty">

<div id="wallpaper"></div>
<div id="bg-fx"></div>
<div id="spotlight"></div>
<canvas id="water-canvas"></canvas>
<div id="border-layer"></div>

<div id="loading">
  <div class="load-logo"><svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="16.6" rx="3.9" ry="2.9"/><ellipse cx="5.4" cy="10.1" rx="1.95" ry="2.4"/><ellipse cx="9.7" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="14.3" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="18.6" cy="10.1" rx="1.95" ry="2.4"/></svg></div>
  <div class="load-title">Kitty</div>
  <div class="load-bar"><div class="load-bar-fill" id="load-fill"></div></div>
</div>

<input type="file" id="pick-script" accept=".lua,.luau,.txt" style="display:none"/>
<input type="file" id="pick-image" accept="image/*" style="display:none"/>
<input type="file" id="pick-avatar" accept="image/*" style="display:none"/>
<input type="file" id="pick-json" accept=".json" style="display:none"/>

<div id="app">
  <header id="titlebar" class="pywebview-drag-region">
    <div class="tb-left">
      <span class="brand-logo" id="brand-logo"></span>
      <span class="brand-name" id="brand-name">Kitty</span>
      <span class="brand-ver" id="brand-ver">v4.7.0</span>
    </div>
    <nav class="tb-center">
      <button class="nav-icon" data-view="home" title="Home"><svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></button>
      <button class="nav-icon active" data-view="editor" title="Editor"><svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></button>
      <button class="nav-icon" id="nav-cmd" title="Command Palette (Ctrl+K)"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
      <button class="nav-icon" id="nav-clients" title="Clients"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg></button>
      <button class="nav-icon" data-view="settings" title="Settings"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 10v6M4.22 4.22l4.24 4.24m7.08 7.08l4.24 4.24M1 12h6m10 0h6"/></svg></button>
    </nav>
    <div class="tb-right">
      <button class="wbtn" id="win-min" title="Minimize"><svg viewBox="0 0 12 12"><line x1="2" y1="6" x2="10" y2="6"/></svg></button>
      <button class="wbtn" id="win-max" title="Maximize"><svg viewBox="0 0 12 12"><rect x="2" y="2" width="8" height="8"/></svg></button>
      <button class="wbtn close" id="win-close" title="Close"><svg viewBox="0 0 12 12"><line x1="2" y1="2" x2="10" y2="10"/><line x1="10" y1="2" x2="2" y2="10"/></svg></button>
    </div>
  </header>

  <div id="body">
    <aside id="activity">
      <button class="act-btn active" data-act="explorer" title="Explorer"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3z"/><line x1="9" y1="3" x2="9" y2="21"/></svg></button>
      <button class="act-btn" data-act="search" title="Search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
      <button class="act-btn" data-act="scripts" title="Scripts"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></button>
      <button class="act-btn" data-act="autoexec" title="AutoExec"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></button>
      <span class="act-sep"></span>
      <button class="act-btn" data-act="account" title="Account"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></button>
    </aside>

    <aside id="explorer">
      <div class="explorer-head">
        <span class="explorer-title" id="explorer-title">Explorer</span>
        <button class="explorer-collapse" id="explorer-collapse" title="Collapse (Ctrl+B)"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button>
      </div>
      <div class="explorer-body" id="explorer-body"></div>
    </aside>

    <main id="workspace">
      <section id="view-home">
        <div class="home-head">
          <div class="home-head-icon" id="home-logo"></div>
          <div>
            <div class="home-head-title" id="home-title">Kitty</div>
            <div class="home-head-sub" id="home-sub">Premium Roblox workspace</div>
          </div>
        </div>
        <div class="home-grid">
          <div class="home-card">
            <div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></span><span class="home-card-title">Account</span></div>
            <div class="home-card-row"><span class="l">User</span><span class="v" id="h-user">—</span></div>
            <div class="home-card-row"><span class="l">Plan</span><span class="v" id="h-plan">—</span></div>
          </div>
          <div class="home-card">
            <div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/></svg></span><span class="home-card-title">License</span></div>
            <div class="home-card-row"><span class="l">Status</span><span class="v ok" id="h-lic">Active</span></div>
            <div class="home-card-row"><span class="l">Expires</span><span class="v" id="h-exp">Never</span></div>
          </div>
          <div class="home-card">
            <div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></span><span class="home-card-title">Runtime</span></div>
            <div class="home-card-row"><span class="l">DLL</span><span class="v" id="h-dll">—</span></div>
            <div class="home-card-row"><span class="l">Offsets</span><span class="v" id="h-off">—</span></div>
            <div class="home-card-row"><span class="l">Attached</span><span class="v" id="h-att">Not injected</span></div>
          </div>
          <div class="home-card">
            <div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span><span class="home-card-title">Roblox</span></div>
            <div class="home-card-row"><span class="l">Versions</span><span class="v" id="h-vers">—</span></div>
            <div class="home-card-row"><span class="l">Newest</span><span class="v" id="h-new">—</span></div>
          </div>
        </div>
        <div class="home-card">
          <div class="home-card-head"><span class="home-card-icon"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span><span class="home-card-title">Quick Actions</span></div>
          <div class="home-actions">
            <button class="home-action" id="qa-new"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><span>New Script</span></button>
            <button class="home-action" id="qa-attach"><svg viewBox="0 0 24 24"><path d="M18.36 6.64a9 9 0 1 1-12.72 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg><span>Attach</span></button>
            <button class="home-action" id="qa-launch"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Launch &amp; Inject</span></button>
            <button class="home-action" id="qa-settings"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/></svg><span>Settings</span></button>
          </div>
        </div>
      </section>

      <section id="view-editor" class="active">
        <div id="tabstrip">
          <div id="tabs"></div>
          <button id="tab-new" title="New Tab (Ctrl+N)"><svg viewBox="0 0 24 24" fill="none"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></button>
          <div id="tab-toolbar">
            <button id="tb-open" title="Open"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></button>
            <button id="tb-save" title="Save"><svg viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/></svg></button>
            <button id="tb-find" title="Find"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>
            <button id="tb-copy" title="Copy All"><svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
          </div>
        </div>
        <div id="editor-body">
          <div id="gutter"></div>
          <div id="editor-stage">
            <pre id="syntax" aria-hidden="true"></pre>
            <textarea id="editor-input" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea>
          </div>
          <div id="find-bar">
            <div class="find-row"><input type="text" id="find-input" placeholder="Find..."/><button class="mini-btn" id="find-next">Next</button><button class="mini-btn" id="find-close">✕</button></div>
            <div class="find-row" id="replace-row" style="display:none"><input type="text" id="replace-input" placeholder="Replace..."/><button class="mini-btn" id="replace-one">Replace</button><button class="mini-btn" id="replace-all">All</button></div>
          </div>
        </div>
        <div id="bottom-panel">
          <div id="bottom-resizer"></div>
          <div id="bottom-tabs">
            <div class="bottom-tabs-left">
              <button class="btab active" data-btab="terminal">Terminal</button>
              <button class="btab" data-btab="roblox">Roblox</button>
            </div>
            <div class="bottom-tabs-right"><button id="term-copy">Copy</button><button id="term-clear">Clear</button></div>
          </div>
          <div id="bottom-body"></div>
        </div>
      </section>

      <section id="view-settings">
        <div id="settings">
          <aside id="settings-nav">
            <div class="s-head"><button id="settings-back" title="Back"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></button><span class="s-title">Settings</span></div>
            <div class="s-search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/></svg><input type="text" id="settings-search" placeholder="Search..."/></div>
            <div id="settings-cats"></div>
          </aside>
          <div id="settings-body"></div>
        </div>
      </section>
    </main>

    <aside id="rail">
      <button class="rail-btn primary" id="rail-execute" title="Execute"><svg viewBox="0 0 24 24" fill="none"><polygon points="6 4 20 12 6 20 6 4"/></svg></button>
      <span class="rail-sep"></span>
      <button class="rail-btn" id="rail-clear" title="Clear"><svg viewBox="0 0 24 24"><path d="M20 20H7L3 16C2 15 2 13 3 12L13 2L22 11L20 20Z"/></svg></button>
      <button class="rail-btn" id="rail-save" title="Save"><svg viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/></svg></button>
      <button class="rail-btn" id="rail-open" title="Open"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg></button>
      <span class="rail-spacer"></span>
      <button class="rail-btn" id="rail-launch" title="Launch &amp; Inject"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg></button>
      <button class="rail-btn" id="rail-inject" title="Attach to running"><svg viewBox="0 0 24 24"><path d="M4 20l4-4"/><path d="M12 2l10 10-8 8-10-10z"/></svg></button>
    </aside>
  </div>

  <footer id="statusbar">
    <div class="sb-group"><span class="sb-item"><svg viewBox="0 0 24 24"><path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h18"/></svg><span class="sb-path" id="sb-path">No file</span></span></div>
    <span class="sb-spacer"></span>
    <div class="sb-group">
      <span class="sb-item" id="sb-cursor">Ln 1, Col 1</span>
      <span class="sb-item" id="sb-spaces">Spaces: 4</span>
      <span class="sb-item">UTF-8</span>
      <span class="sb-item" id="sb-version">—</span>
      <button class="sb-btn" id="inject-trigger"><span class="sb-dot" id="sb-dot"></span><span id="sb-inject-label">Not injected</span></button>
    </div>
  </footer>

  <div id="inject-menu">
    <div class="menu-row" id="menu-inject"><svg viewBox="0 0 24 24"><path d="M4 20l4-4"/><path d="M12 2l10 10-8 8-10-10z"/></svg><span>Attach to running</span></div>
    <div class="menu-row" id="menu-launch"><svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Launch &amp; Inject</span></div>
    <div class="menu-row" id="menu-clients"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg><span>Manage Clients</span></div>
    <div class="menu-row danger" id="menu-kill"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg><span>Kill Roblox</span></div>
  </div>
</div>

<div id="cmd-back"><div id="cmd-modal"><input type="text" id="cmd-input" placeholder="Type a command..."/><div id="cmd-list"></div></div></div>

<div id="app-modal-back">
  <div id="app-modal">
    <div id="app-modal-head"><span id="app-modal-title">Kitty</span></div>
    <div id="app-modal-message"></div>
    <input id="app-modal-input" type="text" autocomplete="off"/>
    <div id="app-modal-actions"><button class="btn" id="app-modal-cancel">Cancel</button><button class="btn primary" id="app-modal-ok">OK</button></div>
  </div>
</div>

<div id="tab-ctx">
  <div class="ctx-row" id="ctx-rename">Rename</div>
  <div class="ctx-row" id="ctx-dup">Duplicate</div>
  <div class="ctx-row" id="ctx-autoexec">Add to AutoExec</div>
  <div class="ctx-sep"></div>
  <div class="ctx-row" id="ctx-close-others">Close Others</div>
  <div class="ctx-row danger" id="ctx-close">Close</div>
</div>

<div id="file-ctx">
  <div class="ctx-row" id="file-ctx-open">Open</div>
  <div class="ctx-row" id="file-ctx-rename">Rename</div>
  <div class="ctx-sep"></div>
  <div class="ctx-row" id="file-ctx-disable">Disable Auto-Execute</div>
  <div class="ctx-row danger" id="file-ctx-remove">Remove File</div>
</div>

<div id="clients-backdrop"></div>
<div id="clients">
  <div class="head">
    <span class="title"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg> Roblox Clients</span>
    <button class="close" id="clients-close"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
  </div>
  <div id="clients-list"></div>
</div>

<div id="attach-overlay"><div class="attach-box"><div class="spinner"></div><div class="attach-step" id="attach-step">Working...</div></div></div>
<div id="toasts"></div>
<div id="resize-grip"><svg viewBox="0 0 24 24"><polyline points="21 15 21 21 15 21"/><polyline points="9 21 3 21 3 15"/></svg></div>

<script>
"use strict";
(() => {
// ─── State ────────────────────────────────────────────────────────────────────
const S = {
  booted: false, settings: null, themes: {}, app: {},
  scripts: [], tabs: [], closed: [], activeTab: null, ctxTab: null,
  attached: false, logs: { terminal: [], roblox: [] }, activeTab2: "terminal",
  explorerVisible: true, lastActivity: "explorer", currentView: "editor",
  settingsSection: "roblox", profilePic: null, ctxFileId: null,
  offsets: {}, versions: [], selectedVersion: "",
};

// ─── Safe helpers ─────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id) || null;
const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));
const esc = (s) => String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const on = (id, ev, fn) => { const el = $(id); if (el && typeof fn === "function") el.addEventListener(ev, fn); return el; };
const setTxt = (id, v) => { const el = $(id); if (el) el.textContent = v; };
const setCls = (id, cls, on) => { const el = $(id); if (el) el.classList.toggle(cls, !!on); };

async function api(method, payload) {
  if (window.pywebview && window.pywebview.api && typeof window.pywebview.api[method] === "function") {
    try { return await window.pywebview.api[method](payload || {}); }
    catch (e) { console.error("[api]", method, e); return { ok: false, error: String(e) }; }
  }
  try {
    const r = await fetch("/api/" + method, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload || {}) });
    return await r.json();
  } catch (e) { return { ok: false, error: String(e) }; }
}

function toast(msg, level) {
  const t = $("toasts"); if (!t) return;
  const el = document.createElement("div");
  el.className = "toast " + (level || "info");
  el.innerHTML = '<span class="toast-dot"></span><span>' + esc(msg) + '</span>';
  t.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 3200);
}

// Modal dialog
function dialog(opts) {
  opts = opts || {};
  return new Promise(resolve => {
    const back = $("app-modal-back"), title = $("app-modal-title"), msg = $("app-modal-message"),
          inp = $("app-modal-input"), ok = $("app-modal-ok"), ca = $("app-modal-cancel");
    if (!back || !ok || !ca) { resolve(opts.input ? null : false); return; }
    if (title) title.textContent = opts.title || "Kitty";
    if (msg) msg.textContent = opts.message || "";
    if (inp) { inp.style.display = opts.input ? "block" : "none"; inp.value = opts.value || ""; }
    ok.textContent = opts.confirmText || "OK";
    ca.textContent = opts.cancelText || "Cancel";
    ok.classList.toggle("danger", !!opts.danger);
    back.classList.add("open");
    let done = false;
    const cleanup = (r) => { if (done) return; done = true; back.classList.remove("open");
      ok.removeEventListener("click", onOk); ca.removeEventListener("click", onCa); resolve(r); };
    const onOk = () => cleanup(opts.input ? (inp ? inp.value.trim() : "") : true);
    const onCa = () => cleanup(opts.input ? null : false);
    ok.addEventListener("click", onOk); ca.addEventListener("click", onCa);
    setTimeout(() => { try { (opts.input ? inp : ok).focus(); } catch(_) {} }, 30);
  });
}
const prompt2 = (msg, val, title) => dialog({ title: title || "Rename", message: msg, value: val || "", input: true, confirmText: "Save" });
const confirm2 = (msg, title, ctext, danger) => dialog({ title: title || "Confirm", message: msg, input: false, confirmText: ctext || "Continue", danger: !!danger });

// ─── Luau highlighter ─────────────────────────────────────────────────────────
const KW = /\b(local|function|return|if|then|elseif|else|end|for|in|do|while|repeat|until|and|or|not|true|false|nil|continue|break|export|type|typeof|self)\b/g;
const FN = /\b(print|warn|error|assert|pcall|require|pairs|ipairs|tostring|tonumber|loadstring|saveinstance|game|workspace|script|task|math|string|table|os|coroutine)\b/g;
const NUM = /\b(0x[0-9a-fA-F]+|\d+(?:\.\d+)?)\b/g;
function highlight(code) {
  return code.split("\n").map(line => {
    let comment = "";
    const ci = line.indexOf("--");
    if (ci !== -1) { comment = '<span class="tk-com">' + esc(line.slice(ci)) + '</span>'; line = line.slice(0, ci); }
    const strings = [];
    line = line.replace(/(["'])(?:\\.|(?!\1).)*\1/g, (m) => { strings.push('<span class="tk-str">' + esc(m) + '</span>'); return "\x00S" + (strings.length - 1) + "\x00"; });
    let safe = esc(line);
    safe = safe.replace(KW, '<span class="tk-kw">$1</span>');
    safe = safe.replace(FN, '<span class="tk-fn">$1</span>');
    safe = safe.replace(NUM, '<span class="tk-num">$1</span>');
    safe = safe.replace(/\x00S(\d+)\x00/g, (_, i) => strings[+i]);
    return safe + comment;
  }).join("\n") + "\n";
}

// ─── Theme application ────────────────────────────────────────────────────────
const hexRgba = (hex, a) => { const h = (hex || "#000").replace("#","");
  return "rgba(" + (parseInt(h.slice(0,2),16)||0) + "," + (parseInt(h.slice(2,4),16)||0) + "," + (parseInt(h.slice(4,6),16)||0) + "," + a + ")"; };
const shade = (hex, f) => { const h = (hex || "#000000").replace("#","");
  const r = Math.min(255, Math.round((parseInt(h.slice(0,2),16)||0)*f)),
        g = Math.min(255, Math.round((parseInt(h.slice(2,4),16)||0)*f)),
        b = Math.min(255, Math.round((parseInt(h.slice(4,6),16)||0)*f));
  return "#" + r.toString(16).padStart(2,"0") + g.toString(16).padStart(2,"0") + b.toString(16).padStart(2,"0"); };

function applyTheme() {
  if (!S.settings || !S.settings.appearance) return;
  const a = S.settings.appearance;
  const reaper = !!(S.settings.secret && S.settings.secret.reaperMode);
  let tid = a.theme || "kitty";
  if (reaper && tid.indexOf("reaper") !== 0) tid = "reaper";
  let pal = S.themes[tid] || S.themes.kitty;
  if (a.theme === "custom-colors" && !reaper) pal = Object.assign({}, S.themes.graphite || {}, a.customColors || {});
  if (a.theme === "custom" && !reaper && a.imageAutoTheme !== false && a.customTheme && a.customTheme.palette) pal = a.customTheme.palette;
  if (!pal) pal = S.themes.kitty;
  document.body.setAttribute("data-theme", tid);
  const r = document.documentElement.style;
  const map = { bg:"--bg", panel:"--panel", surface:"--surface", elevated:"--elevated", hover:"--hover", border:"--border", borderStrong:"--border-strong", text:"--text", text2:"--text2", text3:"--text3" };
  for (const k in map) if (pal[k]) r.setProperty(map[k], pal[k]);
  if (pal.border) r.setProperty("--divider", pal.border);
  const acc = (!reaper && /^#[0-9a-fA-F]{6}$/.test(a.customAccentHex || "")) ? a.customAccentHex : (pal.accent || "#1e3a5f");
  r.setProperty("--accent", acc);
  r.setProperty("--accent-hover", shade(acc, 1.15));
  r.setProperty("--accent-soft", hexRgba(acc, 0.16));
  if (pal.glow) r.setProperty("--glow", pal.glow);
  if (pal.selection) r.setProperty("--selection", pal.selection);
  if (pal.success) r.setProperty("--success", pal.success);
  if (pal.warn) r.setProperty("--warn", pal.warn);
  if (pal.danger) r.setProperty("--danger", pal.danger);
  renderBrand();
}

function renderBrand() {
  if (!S.settings || !S.settings.appearance) return;
  const reaper = !!(S.settings.secret && S.settings.secret.reaperMode);
  const logoHtml = reaper
    ? '<span style="font-size:20px;line-height:1">☠</span>'
    : '<svg viewBox="0 0 24 24" fill="currentColor"><ellipse cx="12" cy="16.6" rx="3.9" ry="2.9"/><ellipse cx="5.4" cy="10.1" rx="1.95" ry="2.4"/><ellipse cx="9.7" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="14.3" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="18.6" cy="10.1" rx="1.95" ry="2.4"/></svg>';
  ["brand-logo","home-logo"].forEach(id => { const el = $(id); if (el) el.innerHTML = logoHtml; });
  setTxt("brand-name", reaper ? "REAPER" : (S.settings.general && S.settings.general.disguiseMode ? "Spotify" : "Kitty"));
  setTxt("home-title", reaper ? "REAPER" : "Kitty");
}

function applySettings() {
  if (!S.settings) return;
  const a = S.settings.appearance || {};
  const e = S.settings.effects || {};
  const ed = S.settings.editor || {};
  const c = S.settings.console || {};
  const g = S.settings.general || {};
  const sec = S.settings.secret || {};
  const r = document.documentElement.style;

  document.body.classList.toggle("no-glow", !e.glowEffects);
  document.body.classList.toggle("border-on", a.borderEnabled !== false && a.borderMode !== "off");
  document.body.classList.toggle("border-rainbow", a.borderEnabled !== false && a.borderMode === "rainbow");
  document.body.classList.toggle("border-solid", a.borderEnabled !== false && a.borderMode === "solid");
  if (a.borderColor) r.setProperty("--border-color", a.borderColor);
  if (a.borderWidth) r.setProperty("--border-width", a.borderWidth + "px");

  // Wallpaper
  const wp = $("wallpaper");
  const url = (a.customTheme && a.customTheme.imageDataUrl) || "";
  if (a.useBackgroundImage && url && wp) {
    wp.style.backgroundImage = 'url("' + url + '")';
    r.setProperty("--bg-img-opacity", (Number(a.bgImageOpacity || 40) / 100).toFixed(2));
  } else if (wp) {
    wp.style.backgroundImage = "";
    r.setProperty("--bg-img-opacity", "0");
  }
  r.setProperty("--panel-opacity", (Number(a.panelOpacity || 82) / 100).toFixed(2));
  r.setProperty("--fx-opacity", { dim: "0.28", normal: "0.55", bold: "0.85" }[a.fxOpacity] || "0.55");

  // Editor typography
  r.setProperty("--font-mono", "'" + (ed.fontFamily || "Cascadia Code") + "', Consolas, monospace");
  const inp = $("editor-input"), syn = $("syntax");
  const in2 = $("editor-input");
  if (in2) in2.style.fontSize = (Number(ed.fontSize || 13)) + "px";
  if (syn) syn.style.fontSize = (Number(ed.fontSize || 13)) + "px";
  setCls("gutter", "hidden", !ed.lineNumbers);

  setCls("bottom-panel", "hidden", !c.showConsole);
  setCls("bottom-resizer", "hidden", !c.showConsole);
  setCls("rail", "hidden", !c.rightSidebarVisible);
  setCls("activity", "hidden", !c.activityRailVisible);

  S.explorerVisible = c.leftExplorerVisible !== false;
  S.lastActivity = c.lastActivity || "explorer";
  syncExplorer();
  syncActivityActive();
  renderExplorer();

  // Background FX
  const fx = $("bg-fx");
  if (fx) {
    fx.innerHTML = "";
    const type = a.fxType || "orbs";
    if (type !== "off") {
      const n = { low: 4, med: 8, high: 14 }[a.fxIntensity || "med"] || 8;
      for (let i = 0; i < n; i++) {
        const o = document.createElement("div");
        o.className = "fx-orb";
        const sz = 140 + Math.random() * 260;
        o.style.width = sz + "px"; o.style.height = sz + "px";
        o.style.left = (Math.random() * 100) + "%"; o.style.top = (Math.random() * 100) + "%";
        o.style.animationDuration = (10 + Math.random() * 12) + "s";
        o.style.animationDelay = (-Math.random() * 12) + "s";
        fx.appendChild(o);
      }
    }
  }

  applyTheme();
  setTxt("brand-ver", "v" + (S.app.version || "4.7.0"));
  refreshEditor(true);
  renderLogs();
}

async function patch(p) {
  const r = await api("update_settings", p);
  if (r && r.ok) { S.settings = r.settings; applySettings(); return true; }
  toast((r && r.error) || "Save failed", "err");
  return false;
}

// ─── Explorer ─────────────────────────────────────────────────────────────────
function syncExplorer() {
  const el = $("explorer");
  if (el) el.classList.toggle("hidden", !S.explorerVisible);
}
function syncActivityActive() {
  $$(".act-btn").forEach(b => b.classList.toggle("active", b.getAttribute("data-act") === S.lastActivity));
}
function activityClick(name) {
  if (name === S.lastActivity && S.explorerVisible) S.explorerVisible = false;
  else { S.explorerVisible = true; S.lastActivity = name; }
  syncExplorer(); syncActivityActive(); renderExplorer();
  patch({ console: { leftExplorerVisible: S.explorerVisible, lastActivity: name } });
}

function renderExplorer() {
  const body = $("explorer-body"); if (!body) return;
  setTxt("explorer-title", ({ explorer: "Explorer", search: "Search", scripts: "Scripts", autoexec: "Auto-Execute", account: "Account" })[S.lastActivity] || "Explorer");
  body.innerHTML = "";
  if (S.lastActivity === "account") {
    const pfp = S.profilePic;
    const av = pfp ? '<img src="' + pfp + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%">' : '<svg viewBox="0 0 24 24" fill="currentColor" style="width:36px;height:36px"><ellipse cx="12" cy="16.6" rx="3.9" ry="2.9"/><ellipse cx="5.4" cy="10.1" rx="1.95" ry="2.4"/><ellipse cx="9.7" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="14.3" cy="7.4" rx="1.95" ry="2.4"/><ellipse cx="18.6" cy="10.1" rx="1.95" ry="2.4"/></svg>';
    const user = (S.settings && S.settings.general && S.settings.general.userName) || "—";
    const plan = (S.settings && S.settings.general && S.settings.general.planName) || "Free";
    body.innerHTML = '<div class="panel-section"><div style="text-align:center;padding:14px"><div style="width:76px;height:76px;border-radius:50%;margin:0 auto 14px;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer" id="acct-avatar">' + av + '</div><div style="font-size:13px;font-weight:600">' + esc(user) + '</div><div style="font-size:11px;color:var(--text3);margin-top:2px">' + esc(plan) + '</div></div><div style="display:flex;gap:6px;justify-content:center;margin-top:8px"><button class="btn" id="acct-up">Upload</button><button class="btn danger" id="acct-rm">Remove</button></div></div>';
    on("acct-avatar", "click", () => { const p = $("pick-avatar"); if (p) p.click(); });
    on("acct-up", "click", () => { const p = $("pick-avatar"); if (p) p.click(); });
    on("acct-rm", "click", async () => { await api("remove_profile_image"); S.profilePic = null; renderExplorer(); });
    return;
  }
  if (S.lastActivity === "search") {
    body.innerHTML = '<div class="panel-section"><div class="field"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/></svg><input type="text" id="side-search" placeholder="Search scripts..."/></div><div id="side-results" style="margin-top:10px"></div></div>';
    const inp = $("side-search"); const out = $("side-results");
    if (inp && out) {
      const render = () => {
        const q = inp.value.trim().toLowerCase();
        out.innerHTML = "";
        if (!q) return;
        const m = S.scripts.filter(x => x.title.toLowerCase().includes(q) || (x.content || "").toLowerCase().includes(q));
        m.slice(0, 40).forEach(x => {
          const d = document.createElement("div"); d.className = "tree-item";
          d.innerHTML = '<span>' + esc(x.title) + '</span>';
          d.addEventListener("click", () => openScript(x));
          out.appendChild(d);
        });
      };
      inp.addEventListener("input", render);
    }
    return;
  }
  // Files panel
  const only = S.lastActivity === "scripts" ? "Scripts" : (S.lastActivity === "autoexec" ? "AutoExec" : "");
  const groups = {};
  S.scripts.forEach(x => { const f = x.folder || "Scripts"; (groups[f] = groups[f] || []).push(x); });
  ["Scripts","AutoExec"].forEach(f => { if (!groups[f]) groups[f] = []; });
  let html = '<div class="panel-section"><div class="field"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/></svg><input type="text" id="explorer-filter" placeholder="Filter files..."/></div></div>';
  let any = false;
  Object.keys(groups).forEach((name, idx) => {
    if (only && name !== only) return;
    const items = groups[name];
    if (!only && items.length === 0) return;
    any = true;
    html += '<div class="tree-group" data-open="true" data-folder="' + esc(name) + '">'
      + '<div class="tree-group-head"><svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg><span>' + esc(name) + '</span><span class="tree-group-count">' + items.length + '</span></div>'
      + '<div class="tree-items">';
    items.forEach(x => {
      html += '<div class="tree-item" data-id="' + esc(x.id) + '" data-title="' + esc(x.title.toLowerCase()) + '">'
        + '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6H6z"/></svg>'
        + '<span>' + esc(x.title) + '</span>'
        + (x.disabled ? '<span class="tree-item-state">DISABLED</span>' : "")
        + '</div>';
    });
    html += '</div></div>';
  });
  if (!any) html += '<div class="panel-section"><div style="text-align:center;padding:20px;color:var(--text3);font-size:11px">No files</div></div>';
  body.innerHTML = html;

  // Wire
  $$(".tree-group-head", body).forEach(h => h.addEventListener("click", () => {
    const g = h.parentElement;
    g.dataset.open = g.dataset.open === "false" ? "true" : "false";
  }));
  $$(".tree-item", body).forEach(el => {
    el.addEventListener("click", () => {
      const s = S.scripts.find(x => x.id === el.dataset.id);
      if (s) openScript(s);
    });
    el.addEventListener("contextmenu", (ev) => {
      ev.preventDefault(); ev.stopPropagation();
      const s = S.scripts.find(x => x.id === el.dataset.id);
      if (!s) return;
      S.ctxFileId = s.id;
      const auto = (s.folder || "").toLowerCase().startsWith("autoexec");
      const rn = $("file-ctx-rename"); if (rn) rn.style.display = auto ? "none" : "";
      const dis = $("file-ctx-disable"); if (dis) dis.style.display = (auto && !s.disabled) ? "" : "none";
      const m = $("file-ctx"); if (m) { m.classList.add("open"); m.style.left = Math.min(ev.clientX, window.innerWidth - 205) + "px"; m.style.top = Math.min(ev.clientY, window.innerHeight - 140) + "px"; }
    });
  });
  const filt = $("explorer-filter");
  if (filt) filt.addEventListener("input", () => {
    const q = filt.value.trim().toLowerCase();
    $$(".tree-item", body).forEach(el => { el.style.display = (!q || (el.dataset.title || "").includes(q)) ? "" : "none"; });
  });
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
function openScript(s) {
  const ex = S.tabs.find(t => (t.scriptId && t.scriptId === s.id) || (!t.scriptId && t.title === s.title));
  if (ex) return selectTab(ex.id);
  createTab(s.title, s.content, s.id);
}
function createTab(title, content, scriptId) {
  const rt = title || "Untitled";
  const ex = S.tabs.find(t => (scriptId && t.scriptId === scriptId) || (!scriptId && t.title === rt && !t.scriptId));
  if (ex) return selectTab(ex.id);
  const id = "tab_" + Date.now() + "_" + Math.random().toString(36).slice(2, 6);
  const empty = S.settings && S.settings.general && S.settings.general.defaultNewTabBehavior === "empty";
  const body = content !== undefined ? content : (empty ? "" : "-- Untitled Script\n");
  S.tabs.push({ id, title: rt, content: body, saved: body, scriptId: scriptId || null, dirty: false });
  selectTab(id);
}
function selectTab(id) {
  const t = S.tabs.find(x => x.id === id); if (!t) return;
  S.activeTab = id;
  const inp = $("editor-input"); if (inp) inp.value = t.content;
  setTxt("sb-path", t.title);
  renderTabs(); refreshEditor(true);
}
function renderTabs() {
  const bar = $("tabs"); if (!bar) return;
  bar.innerHTML = "";
  S.tabs.forEach(t => {
    const el = document.createElement("div");
    el.className = "tab" + (t.id === S.activeTab ? " active" : "") + (t.dirty ? " dirty" : "");
    el.innerHTML = '<span class="tab-name">' + esc(t.title) + '</span><span class="tab-dirty"></span><button class="tab-close"><svg viewBox="0 0 12 12"><line x1="2.5" y1="2.5" x2="9.5" y2="9.5"/><line x1="9.5" y1="2.5" x2="2.5" y2="9.5"/></svg></button>';
    el.addEventListener("click", () => selectTab(t.id));
    el.querySelector(".tab-close").addEventListener("click", (ev) => { ev.stopPropagation(); closeTab(t.id); });
    el.addEventListener("contextmenu", (ev) => {
      ev.preventDefault(); S.ctxTab = t.id;
      const m = $("tab-ctx"); if (m) { m.classList.add("open"); m.style.left = Math.min(ev.clientX, window.innerWidth - 180) + "px"; m.style.top = Math.min(ev.clientY, window.innerHeight - 180) + "px"; }
    });
    bar.appendChild(el);
  });
}
async function closeTab(id) {
  const idx = S.tabs.findIndex(x => x.id === id); if (idx === -1) return;
  const t = S.tabs[idx];
  const confirm = S.settings && S.settings.editor && S.settings.editor.confirmCloseUnsaved;
  if (t.dirty && confirm) { if (!await confirm2('Close "' + t.title + '" with unsaved changes?', "Close Tab", "Close", true)) return; }
  if (S.tabs.length === 1) { t.title = "Untitled"; t.content = ""; t.saved = ""; t.dirty = false; t.scriptId = null; const inp = $("editor-input"); if (inp) inp.value = ""; selectTab(t.id); return; }
  S.tabs.splice(idx, 1);
  if (S.activeTab === id) selectTab(S.tabs[Math.max(0, idx - 1)].id);
  else renderTabs();
}

// ─── Editor ───────────────────────────────────────────────────────────────────
function refreshEditor(force) {
  const inp = $("editor-input"), syn = $("syntax"), gut = $("gutter");
  if (!inp || !syn || !gut) return;
  const val = inp.value, sel = inp.selectionStart || 0;
  let lines = 1, cur = 1, lastNl = -1;
  for (let i = 0; i < val.length; i++) if (val.charCodeAt(i) === 10) { lines++; if (i < sel) { cur++; lastNl = i; } }
  syn.innerHTML = highlight(val);
  syn.scrollTop = inp.scrollTop; syn.scrollLeft = inp.scrollLeft;
  gut.innerHTML = "";
  for (let i = 1; i <= lines; i++) {
    const d = document.createElement("div");
    d.className = "gln" + (i === cur ? " active" : ""); d.textContent = i;
    gut.appendChild(d);
  }
  gut.scrollTop = inp.scrollTop;
  setTxt("sb-cursor", "Ln " + cur + ", Col " + (sel - lastNl));
}

// ─── Logs ─────────────────────────────────────────────────────────────────────
function log(tab, text, level) {
  const ts = new Date().toTimeString().slice(0, 8);
  const b = S.logs[tab] || (S.logs[tab] = []);
  b.push({ ts, text, level: level || "info" });
  const max = Number(S.settings && S.settings.console && S.settings.console.maxLines || 2000);
  if (b.length > max) b.shift();
  if (S.activeTab2 === tab) renderLogs();
}
function renderLogs() {
  const box = $("bottom-body"); if (!box) return;
  const list = S.logs[S.activeTab2] || [];
  box.innerHTML = "";
  list.forEach(it => {
    const d = document.createElement("div");
    d.className = "log-line " + it.level;
    d.innerHTML = '<span class="log-time">[' + it.ts + ']</span><span class="log-msg">' + esc(it.text) + '</span>';
    box.appendChild(d);
  });
  if (S.settings && S.settings.console && S.settings.console.autoScroll !== false) box.scrollTop = box.scrollHeight;
}
function setBottomTab(t) {
  S.activeTab2 = t;
  $$(".btab").forEach(b => b.classList.toggle("active", b.getAttribute("data-btab") === t));
  renderLogs();
}

// ─── Attach state UI ─────────────────────────────────────────────────────────
function setAttached(att, pid, ver) {
  S.attached = !!att;
  setCls("sb-dot", "on", att);
  setTxt("sb-inject-label", att ? (pid ? "Attached · " + pid : "Attached") : "Not injected");
  setTxt("h-att", att ? "Injected" : "Not injected");
  setTxt("sb-version", ver ? ver.replace("version-", "v") : "—");
}

async function doAttach(pid) {
  const ov = $("attach-overlay"), st = $("attach-step");
  const steps = ["Checking DLL...", "Syncing offsets...", "Opening process...", "Injecting...", "Verifying..."];
  let i = 0;
  if (ov) ov.classList.add("open"); if (st) st.textContent = steps[0];
  const iv = setInterval(() => { i = Math.min(i + 1, steps.length - 1); if (st) st.textContent = steps[i]; }, 350);
  try {
    const r = await api("simulate_attach", pid ? { pid } : {});
    clearInterval(iv); if (ov) ov.classList.remove("open");
    if (r && r.ok) {
      setAttached(true, r.pid, r.clientVersion);
      log("terminal", r.message, "ok"); toast(r.message, "ok");
    } else {
      log("terminal", (r && r.error) || "Attach failed", "err");
      toast((r && r.error) || "Attach failed", "err");
    }
  } catch (e) { clearInterval(iv); if (ov) ov.classList.remove("open"); toast("Attach error: " + e, "err"); }
}

async function doLaunch(version) {
  const ov = $("attach-overlay"), st = $("attach-step");
  const steps = ["Syncing offsets...", "Writing module config...", "Launching suspended...", "Early-bird inject...", "Resuming client..."];
  let i = 0;
  if (ov) ov.classList.add("open"); if (st) st.textContent = steps[0];
  const iv = setInterval(() => { i = Math.min(i + 1, steps.length - 1); if (st) st.textContent = steps[i]; }, 500);
  try {
    const r = await api("launch_and_inject", { version: version || "" });
    clearInterval(iv); if (ov) ov.classList.remove("open");
    if (r && r.ok) {
      setAttached(true, r.pid, r.version);
      log("terminal", r.message, "ok"); toast(r.message, "ok");
    } else {
      log("terminal", (r && r.error) || "Launch failed", "err");
      toast((r && r.error) || "Launch failed", "err");
    }
  } catch (e) { clearInterval(iv); if (ov) ov.classList.remove("open"); toast("Launch error: " + e, "err"); }
}

// ─── Views ────────────────────────────────────────────────────────────────────
function switchView(name) {
  S.currentView = name;
  $$(".nav-icon[data-view]").forEach(b => b.classList.toggle("active", b.getAttribute("data-view") === name));
  ["home","editor","settings"].forEach(v => { const el = $("view-" + v); if (el) el.classList.toggle("active", v === name); });
  if (name === "settings") renderSettingsNav();
}

// ─── Settings ─────────────────────────────────────────────────────────────────
const SECTIONS = [
  { id:"roblox", name:"Roblox" },
  { id:"versions", name:"Versions" },
  { id:"appearance", name:"Appearance" },
  { id:"effects", name:"Effects" },
  { id:"editor", name:"Editor" },
  { id:"terminal", name:"Terminal" },
  { id:"window", name:"Window" },
  { id:"behavior", name:"Behavior" },
  { id:"connections", name:"Connections" },
  { id:"secret", name:"???" },
];

function renderSettingsNav() {
  const nav = $("settings-cats"); if (!nav) return;
  nav.innerHTML = "";
  SECTIONS.forEach(s => {
    const b = document.createElement("button");
    b.className = "s-cat" + (S.settingsSection === s.id ? " active" : "");
    b.innerHTML = '<span class="s-cat-name">' + esc(s.name) + '</span>';
    b.addEventListener("click", () => { S.settingsSection = s.id; renderSettingsNav(); });
    nav.appendChild(b);
  });
  renderSettingsBody();
}

function swHtml(bind, on) { return '<div class="sw' + (on ? " on" : "") + '" data-bind="' + bind + '"></div>'; }
function rowHtml(t, d, c) { return '<div class="s-row"><div class="s-row-info"><div class="s-row-title">' + esc(t) + '</div><div class="s-row-desc">' + esc(d) + '</div></div><div class="s-row-control">' + c + '</div></div>'; }
function sliderHtml(id, mn, mx, v, sfx, step) {
  return '<div class="slider-wrap"><input type="range" class="slider" id="' + id + '" min="' + mn + '" max="' + mx + '" step="' + (step||1) + '" value="' + v + '"/><span class="slider-val" id="' + id + '-lbl">' + v + (sfx||"") + '</span></div>';
}
function selectHtml(bind, opts, v) {
  return '<select class="ui-select" data-select="' + bind + '">' + opts.map(o => '<option value="' + o.v + '"' + (String(v)===String(o.v)?" selected":"") + '>' + o.l + '</option>').join("") + '</select>';
}
function segHtml(id, opts, v) {
  return '<div class="segmented" id="' + id + '">' + opts.map(o => '<button data-v="' + o.v + '"' + (String(v)===String(o.v)?' class="active"':"") + '>' + o.l + '</button>').join("") + '</div>';
}

function buildSection(id) {
  const s = S.settings; if (!s) return "";
  const a = s.appearance || {}, e = s.effects || {}, ed = s.editor || {},
        c = s.console || {}, g = s.general || {}, rb = s.roblox || {}, sec = s.secret || {};
  let h = "";
  if (id === "roblox") {
    h += '<div class="s-section-head"><div class="s-section-title">Roblox</div><div class="s-section-sub">Injection, offsets, executor features.</div></div>';
    h += rowHtml("Module.dll", "Auto-detected next to kitty.py or ./bin/.", '<span style="font-family:var(--font-mono);font-size:10px;word-break:break-all">' + esc(S.offsets.dll_path || "NOT FOUND") + '</span>');
    h += rowHtml("Offsets", "Auto-synced from offsets.imtheo.lol.", '<span style="font-family:var(--font-mono);font-size:10px">' + esc(S.offsets.cached_version || "not cached") + '</span>');
    h += rowHtml("Sync offsets", "Force-refresh the table now.", '<button class="btn primary" id="cfg-sync">Sync</button>');
    h += '<div class="s-subhead">Injection methods</div>';
    h += rowHtml("Prefer suspended injection", "Launch Roblox frozen, inject before its checks, then resume.", swHtml("roblox.preferSuspendedInject", rb.preferSuspendedInject !== false));
    h += rowHtml("Force old-version bypass", "Try extra strategies for older clients.", swHtml("roblox.forceOldVersionBypass", rb.forceOldVersionBypass !== false));
    h += rowHtml("Patch ClientVersion in memory", "Rewrite old version string in the client.", swHtml("roblox.patchClientVersion", rb.patchClientVersion !== false));
    h += rowHtml("Skip version check", "Tell the module to skip its own version check.", swHtml("roblox.skipVersionCheck", rb.skipVersionCheck !== false));
    h += rowHtml("Prefer NtCreateThreadEx", "Use NTCT instead of CreateRemoteThread.", swHtml("roblox.useManualMapper", !!rb.useManualMapper));
    h += rowHtml("Inject timeout", "Seconds before giving up.", sliderHtml("s-inject-to", 5, 180, rb.injectTimeoutSec || 60, "s"));
    h += '<div class="s-subhead">Executor features</div>';
    h += rowHtml("RakNet", "Enable RakNet library.", swHtml("roblox.raknet", rb.raknet));
    h += rowHtml("Internal UI", "Enable module's internal UI.", swHtml("roblox.internalUI", rb.internalUI));
    h += rowHtml("Bypass AFK", "Keep client from idling out.", swHtml("roblox.bypassAFK", rb.bypassAFK !== false));
    h += rowHtml("AutoExec", "Run AutoExec scripts after injection.", swHtml("roblox.autoAttach", rb.autoAttach));
    h += '<div class="s-subhead">Socket</div>';
    h += rowHtml("Host", "Exec socket host.", '<input type="text" class="ui-text mono" data-text="roblox.execHost" value="' + esc(rb.execHost) + '"/>');
    h += rowHtml("Port", "Exec socket port.", '<input type="text" class="ui-text mono" data-text="roblox.execPort" value="' + esc(rb.execPort) + '"/>');
    h += rowHtml("Actions", "Status + kill.", '<button class="btn" id="cfg-status">Check</button> <button class="btn danger" id="cfg-kill">Kill Roblox</button>');
  } else if (id === "versions") {
    h += '<div class="s-section-head"><div class="s-section-title">Versions</div><div class="s-section-sub">Launch a specific Roblox client and inject into it. Old versions supported via suspended injection.</div></div>';
    h += '<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Installed Roblox Versions</div><div class="s-row-desc">Found in %LOCALAPPDATA%\\Roblox\\Versions.</div></div><div class="version-list" id="version-list">';
    if (S.versions.length) {
      S.versions.forEach((v, i) => {
        h += '<div class="version-row' + (S.selectedVersion === v.name ? " active" : "") + '" data-ver="' + esc(v.name) + '"><div class="vinfo"><div class="vname">' + esc(v.name) + '</div><div class="vmeta">' + new Date((v.modified||0)*1000).toLocaleString() + (i===0?" · NEWEST":"") + '</div></div><button class="btn primary" data-launch-ver="' + esc(v.name) + '">Launch &amp; Inject</button></div>';
      });
    } else {
      h += '<div style="text-align:center;padding:16px;color:var(--text3);font-size:11px">No versions detected</div>';
    }
    h += '</div></div>';
    h += rowHtml("Refresh list", "Rescan installed versions.", '<button class="btn" id="cfg-refresh">Refresh</button>');
  } else if (id === "appearance") {
    h += '<div class="s-section-head"><div class="s-section-title">Appearance</div></div>';
    h += '<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Theme</div></div><div class="theme-grid" id="theme-grid"></div></div>';
    h += '<div class="s-subhead">Border</div>';
    h += rowHtml("Enable border", "Colored border around window.", swHtml("appearance.borderEnabled", a.borderEnabled !== false));
    h += rowHtml("Border mode", "Rainbow or solid.", segHtml("seg-border", [{v:"rainbow",l:"Rainbow"},{v:"solid",l:"Solid"},{v:"off",l:"Off"}], a.borderMode));
    if (a.borderMode === "solid") h += rowHtml("Border color", "Solid color.", '<input type="color" class="mini-color" id="border-c" value="' + (a.borderColor||"#b388ff") + '"/>');
    h += rowHtml("Border width", "Thickness.", sliderHtml("s-border-w", 1, 8, a.borderWidth || 2, "px"));
    h += '<div class="s-subhead">Wallpaper</div>';
    h += '<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Background Image</div></div><div class="bg-thumbs" id="bg-thumbs"></div><div style="display:flex;gap:6px;margin-top:10px"><button class="btn primary" id="cfg-upload">Upload &amp; Apply</button><button class="btn danger" id="cfg-remove-bg">Remove</button></div></div>';
    h += rowHtml("Opacity", "Wallpaper visibility.", sliderHtml("s-bg-op", 0, 100, a.bgImageOpacity || 40, "%"));
    h += rowHtml("Panel opacity", "Panel transparency over wallpaper.", sliderHtml("s-panel-op", 30, 100, a.panelOpacity || 82, "%"));
    h += rowHtml("Image-derived colors", "Recolor UI from wallpaper.", swHtml("appearance.imageAutoTheme", a.imageAutoTheme !== false));
    h += '<div class="s-subhead">Ambient FX</div>';
    h += rowHtml("Effect", "Background particles.", segHtml("seg-fx", [{v:"off",l:"Off"},{v:"orbs",l:"Orbs"}], a.fxType));
    h += rowHtml("Intensity", "Density.", segHtml("seg-fx-int", [{v:"low",l:"Low"},{v:"med",l:"Med"},{v:"high",l:"High"}], a.fxIntensity));
    h += '<div class="s-subhead">Surface</div>';
    h += rowHtml("Accent override", "Custom accent color.", '<input type="color" class="mini-color" id="acc-c" value="' + (a.customAccentHex||"#1e3a5f") + '"/><input type="text" class="ui-text mono" data-text="appearance.customAccentHex" value="' + esc(a.customAccentHex||"") + '" style="width:100px"/>');
    h += rowHtml("Density", "Compact / comfortable / spacious.", selectHtml("appearance.uiDensity", [{v:"compact",l:"Compact"},{v:"comfortable",l:"Comfortable"},{v:"spacious",l:"Spacious"}], a.uiDensity));
    h += rowHtml("Radius", "Corner geometry.", selectHtml("appearance.cornerRadius", [{v:"sharp",l:"Sharp"},{v:"subtle",l:"Subtle"},{v:"rounded",l:"Rounded"}], a.cornerRadius));
    h += rowHtml("Sidebar labels", "Show filenames.", swHtml("appearance.sidebarLabels", a.sidebarLabels !== false));
  } else if (id === "effects") {
    h += '<div class="s-section-head"><div class="s-section-title">Effects</div><div class="s-section-sub">Particles, cursor, motion.</div></div>';
    h += rowHtml("Click particles", "Burst on click.", swHtml("effects.clickParticles", e.clickParticles));
    h += rowHtml("Particle count", "Particles per burst.", sliderHtml("s-part-n", 4, 36, e.particleCount || 16, ""));
    h += rowHtml("Cursor trail", "Trail dots follow pointer.", swHtml("effects.cursorTrail", e.cursorTrail));
    h += rowHtml("Water cursor", "Glassy rings follow cursor.", swHtml("effects.waterCursor", e.waterCursor !== false));
    h += rowHtml("Ripples", "Button click ripples.", swHtml("effects.ripplesEnabled", e.ripplesEnabled));
    h += rowHtml("Master animations", "Enable transitions.", swHtml("effects.masterAnimations", e.masterAnimations));
    h += rowHtml("Animation speed", "Duration preset.", selectHtml("effects.animationSpeed", [{v:"slow",l:"Slow"},{v:"normal",l:"Normal"},{v:"fast",l:"Fast"}], e.animationSpeed));
    h += rowHtml("Cursor spotlight", "Radial glow follows pointer.", swHtml("effects.cursorSpotlight", e.cursorSpotlight));
    h += rowHtml("Reduced motion", "Disable nonessential motion.", swHtml("effects.reduceMotion", e.reduceMotion));
    h += rowHtml("Fog glow", "Hover breathing glow.", swHtml("effects.fogGlow", e.fogGlow !== false));
  } else if (id === "editor") {
    h += '<div class="s-section-head"><div class="s-section-title">Editor</div></div>';
    h += rowHtml("Font family", "Monospace stack.", selectHtml("editor.fontFamily", [{v:"Cascadia Code",l:"Cascadia Code"},{v:"JetBrains Mono",l:"JetBrains Mono"},{v:"Consolas",l:"Consolas"}], ed.fontFamily));
    h += rowHtml("Font size", "Pixels.", sliderHtml("s-font", 11, 20, ed.fontSize || 13, "px"));
    h += rowHtml("Line height", "Vertical rhythm.", sliderHtml("s-lh", 1.2, 2.0, ed.lineHeight || 1.55, "", 0.05));
    h += rowHtml("Line numbers", "Show gutter.", swHtml("editor.lineNumbers", ed.lineNumbers));
    h += rowHtml("Highlight current line", "Highlight cursor line.", swHtml("editor.highlightCurrentLine", ed.highlightCurrentLine));
    h += rowHtml("Word wrap", "Wrap long lines.", swHtml("editor.wordWrap", ed.wordWrap));
    h += rowHtml("Tab size", "Indentation width.", selectHtml("editor.tabSize", [{v:2,l:"2"},{v:4,l:"4"},{v:8,l:"8"}], ed.tabSize));
    h += rowHtml("Auto indent", "Indent on Enter.", swHtml("editor.autoIndent", ed.autoIndent));
    h += rowHtml("Auto-close brackets", "Pair brackets & quotes.", swHtml("editor.autoCloseBrackets", ed.autoCloseBrackets));
  } else if (id === "terminal") {
    h += '<div class="s-section-head"><div class="s-section-title">Terminal</div></div>';
    h += rowHtml("Show terminal", "Display bottom panel.", swHtml("console.showConsole", c.showConsole));
    h += rowHtml("Height", "Panel height.", sliderHtml("s-term-h", 100, 400, c.consoleHeight || 160, "px"));
    h += rowHtml("Auto scroll", "Scroll to newest.", swHtml("console.autoScroll", c.autoScroll));
    h += rowHtml("Timestamps", "Prefix each line.", swHtml("console.timestamps", c.timestamps));
    h += rowHtml("Max lines", "Retained lines.", selectHtml("console.maxLines", [{v:500,l:"500"},{v:2000,l:"2,000"},{v:5000,l:"5,000"}], c.maxLines));
    h += rowHtml("Confirm clear", "Prompt before clearing.", swHtml("console.confirmClearOutput", c.confirmClearOutput));
  } else if (id === "window") {
    h += '<div class="s-section-head"><div class="s-section-title">Window</div></div>';
    h += rowHtml("Launch maximized", "Open maximized.", swHtml("general.launchMaximized", g.launchMaximized));
    h += rowHtml("Minimize to tray", "Hide to tray on close.", swHtml("general.minimizeToTray", g.minimizeToTray));
    h += rowHtml("Streamproof (WDA)", "Exclude from OBS.", swHtml("general.streamproof", g.streamproof));
    h += rowHtml("Disguise title", 'Rename window to "Spotify".', swHtml("general.disguiseMode", g.disguiseMode));
    h += rowHtml("Global hotkey", "Hide / restore key.", selectHtml("general.globalToggleKey", [{v:"Insert",l:"Insert"},{v:"F8",l:"F8"},{v:"F9",l:"F9"},{v:"F10",l:"F10"},{v:"Home",l:"Home"}], g.globalToggleKey));
  } else if (id === "behavior") {
    h += '<div class="s-section-head"><div class="s-section-title">Behavior</div></div>';
    h += rowHtml("Performance mode", "OS scheduling priority.", selectHtml("general.performanceMode", [{v:"low",l:"Low"},{v:"medium",l:"Medium"},{v:"high",l:"High"}], g.performanceMode));
    h += rowHtml("Hover effects", "Border + lift on hover.", swHtml("effects.hoverEffects", e.hoverEffects));
    h += rowHtml("Magnetic icons", "Nav icons follow cursor.", swHtml("effects.magneticIcons", e.magneticIcons));
    h += rowHtml("Button press", "Scale feedback on click.", swHtml("effects.buttonPressAnim", e.buttonPressAnim));
    h += rowHtml("Glow effects", "Colored glow shadows.", swHtml("effects.glowEffects", e.glowEffects));
  } else if (id === "connections") {
    h += '<div class="s-section-head"><div class="s-section-title">Connections</div></div>';
    h += rowHtml("Runtime dir", "Where kitty.py lives.", '<span style="font-family:var(--font-mono);font-size:10px;word-break:break-all">' + esc(S.app.runtimeDir || "") + '</span>');
    h += rowHtml("Settings file", "Persisted config.", '<span style="font-family:var(--font-mono);font-size:10px;word-break:break-all">' + esc(S.app.settingsPath || "") + '</span>');
    h += rowHtml("Export settings", "Save to JSON.", '<button class="btn" id="cfg-exp">Export</button>');
    h += rowHtml("Import settings", "Load from JSON.", '<button class="btn" id="cfg-imp">Import</button>');
    h += rowHtml("Open data folder", "Open Kitty data dir.", '<button class="btn" id="cfg-folder">Open</button>');
    h += rowHtml("Reset all", "Restore defaults.", '<button class="btn danger" id="cfg-reset">Reset</button>');
  } else if (id === "secret") {
    const un = sec.unlocked;
    h += '<div class="s-section-head"><div class="s-section-title">' + (un ? "The Void" : "???") + '</div><div class="s-section-sub">' + (un ? "Unlocked." : "Something is hidden here.") + '</div></div>';
    if (!un) {
      h += '<div class="s-row vertical"><div class="s-row-info"><div class="s-row-title">Seal of the Void</div><div class="s-row-desc">Click colors in ROYGBP order.</div></div><div style="display:flex;gap:14px;justify-content:center;padding:20px;background:var(--bg);border:1px dashed var(--border-strong);border-radius:6px;margin-top:8px" id="seal-wrap">'
        + ["#e74c3c","#f39c12","#f1c40f","#2ecc71","#3498db","#9b59b6"].map(c => '<div class="seal-dot" data-color="' + c + '" style="width:44px;height:44px;border-radius:50%;background:' + c + ';cursor:pointer"></div>').join("")
        + '</div></div>';
    } else {
      h += rowHtml("Reaper mode", "Grim reaper brand.", swHtml("secret.reaperMode", sec.reaperMode));
      h += rowHtml("Re-lock", "Reset the seal.", '<button class="btn" id="reaper-relock">Re-lock</button>');
    }
  }
  return h;
}

function renderSettingsBody() {
  const body = $("settings-body"); if (!body || !S.settings) return;
  body.innerHTML = buildSection(S.settingsSection);
  wireControls();
  if (S.settingsSection === "appearance") renderThemes();
  if (S.settingsSection === "secret") wireSeal();
}

function wireControls() {
  $$(".sw[data-bind]").forEach(el => el.addEventListener("click", () => {
    const parts = el.dataset.bind.split(".");
    const cur = S.settings[parts[0]] && S.settings[parts[0]][parts[1]];
    const patchObj = {}; patchObj[parts[0]] = {}; patchObj[parts[0]][parts[1]] = !cur;
    patch(patchObj);
  }));
  $$(".ui-select[data-select]").forEach(el => el.addEventListener("change", () => {
    const parts = el.dataset.select.split(".");
    let v = el.value; if (/^\d+$/.test(v)) v = Number(v);
    const obj = {}; obj[parts[0]] = {}; obj[parts[0]][parts[1]] = v;
    patch(obj);
  }));
  $$(".ui-text[data-text]").forEach(el => el.addEventListener("change", () => {
    const parts = el.dataset.text.split(".");
    let v = el.value.trim(); if (/^-?\d+$/.test(v)) v = Number(v);
    const obj = {}; obj[parts[0]] = {}; obj[parts[0]][parts[1]] = v;
    patch(obj);
  }));
  $$(".segmented").forEach(seg => {
    const map = { "seg-border": "appearance.borderMode", "seg-fx": "appearance.fxType", "seg-fx-int": "appearance.fxIntensity" };
    const bind = map[seg.id]; if (!bind) return;
    seg.addEventListener("click", (ev) => {
      const b = ev.target.closest("button"); if (!b) return;
      const parts = bind.split(".");
      const obj = {}; obj[parts[0]] = {}; obj[parts[0]][parts[1]] = b.dataset.v;
      patch(obj).then(() => renderSettingsBody());
    });
  });
  const sliders = [
    ["s-inject-to", v => ({ roblox: { injectTimeoutSec: v } }), "s"],
    ["s-panel-op", v => ({ appearance: { panelOpacity: v } }), "%"],
    ["s-bg-op", v => ({ appearance: { bgImageOpacity: v } }), "%"],
    ["s-font", v => ({ editor: { fontSize: v } }), "px"],
    ["s-lh", v => ({ editor: { lineHeight: v } }), ""],
    ["s-term-h", v => ({ console: { consoleHeight: v } }), "px"],
    ["s-part-n", v => ({ effects: { particleCount: v } }), ""],
    ["s-border-w", v => ({ appearance: { borderWidth: v } }), "px"],
  ];
  sliders.forEach(([id, map, sfx]) => {
    const el = $(id); const lbl = $(id + "-lbl"); if (!el) return;
    el.addEventListener("input", () => {
      const v = Number(el.value); if (lbl) lbl.textContent = v + (sfx || "");
      patch(map(v));
    });
  });
  on("cfg-sync", "click", async (ev) => {
    const b = ev.currentTarget; b.disabled = true; b.textContent = "...";
    const r = await api("sync_offsets", { force: true });
    if (r && r.ok) { toast("Offsets synced: " + (r.version || "?"), "ok"); log("terminal", "Offsets synced: " + (r.version || "?"), "ok"); }
    else toast((r && r.error) || "Sync failed", "err");
    S.offsets = await api("offsets_status");
    renderSettingsBody();
  });
  on("cfg-status", "click", async () => {
    const r = await api("get_status");
    if (r) { setAttached(r.attached, r.attached_pid, r.attached_version); log("roblox", r.attached ? "Attached (PID " + r.attached_pid + ")" : "Not attached", r.attached ? "ok" : "warn"); }
  });
  on("cfg-kill", "click", async () => {
    if (!await confirm2("Terminate all Roblox processes?", "Kill Roblox", "Kill", true)) return;
    const r = await api("kill_roblox");
    if (r && r.ok) { log("terminal", "Killed " + r.killed, "warn"); setAttached(false); }
  });
  on("cfg-refresh", "click", async () => {
    const init = await api("get_initial_state");
    if (init && init.ok) { S.versions = init.installedVersions || []; renderSettingsBody(); }
  });
  $$("[data-launch-ver]").forEach(b => b.addEventListener("click", () => {
    const v = b.getAttribute("data-launch-ver");
    S.selectedVersion = v;
    doLaunch(v);
  }));
  on("cfg-upload", "click", async () => {
    const r = await api("pick_theme_image");
    if (r && r.ok && r.dataUrl) {
      const saved = await api("save_custom_theme_image", { filename: r.filename, dataUrl: r.dataUrl });
      if (saved && saved.ok) {
        S.settings = saved.settings;
        await patch({ appearance: { useBackgroundImage: true } });
        renderSettingsBody(); toast("Background applied", "ok");
      }
    } else if (r && r.fallback) { const p = $("pick-image"); if (p) p.click(); }
    else if (r && r.error) toast(r.error, "err");
  });
  on("cfg-remove-bg", "click", async () => {
    const r = await api("remove_custom_theme_image");
    if (r && r.ok) { S.settings = r.settings; applySettings(); renderSettingsBody(); toast("Removed", "info"); }
  });
  on("acc-c", "change", (e) => patch({ appearance: { customAccentHex: e.target.value } }));
  on("border-c", "change", (e) => patch({ appearance: { borderColor: e.target.value } }));
  on("cfg-exp", "click", async () => {
    const r = await api("export_settings_json");
    if (r && r.browserDownload && r.json) {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([r.json], { type: "application/json" }));
      a.download = "kitty_settings.json"; a.click();
    }
    toast("Exported", "ok");
  });
  on("cfg-imp", "click", async () => {
    if (window.pywebview) {
      const r = await api("import_settings_json", {});
      if (r && r.ok) { S.settings = r.settings; applySettings(); renderSettingsBody(); toast("Imported", "ok"); }
    } else { const p = $("pick-json"); if (p) p.click(); }
  });
  on("cfg-folder", "click", () => api("open_data_folder"));
  on("cfg-reset", "click", async () => {
    if (!await confirm2("Reset all settings?", "Reset", "Reset", true)) return;
    const r = await api("reset_all_settings");
    if (r && r.ok) { S.settings = r.settings; applySettings(); renderSettingsBody(); toast("Reset", "ok"); }
  });
  on("reaper-relock", "click", () => patch({ secret: { unlocked: false, reaperMode: false } }).then(() => renderSettingsBody()));
}

function wireSeal() {
  if (S.settings && S.settings.secret && S.settings.secret.unlocked) return;
  const order = ["#e74c3c","#f39c12","#f1c40f","#2ecc71","#3498db","#9b59b6"];
  let progress = [];
  $$("#seal-wrap .seal-dot").forEach(d => d.addEventListener("click", () => {
    const c = d.dataset.color;
    if (c === order[progress.length]) {
      progress.push(c); d.style.boxShadow = "0 0 20px 4px #fff";
      if (progress.length === order.length) {
        setTimeout(() => patch({ secret: { unlocked: true } }).then(() => renderSettingsBody()), 300);
        toast("The seal is broken.", "warn");
      }
    } else {
      progress = [];
      $$("#seal-wrap .seal-dot").forEach(x => x.style.boxShadow = "none");
    }
  }));
}

function renderThemes() {
  const g = $("theme-grid"); if (!g || !S.settings) return;
  const a = S.settings.appearance || {};
  const hidden = new Set(["reaper","void-green","void-mono"]);
  g.innerHTML = "";
  Object.values(S.themes).forEach(t => {
    if (hidden.has(t.id) && !(S.settings.secret && S.settings.secret.unlocked)) return;
    if (t.id === "reaper") return;
    const active = a.theme === t.id;
    const c = document.createElement("div");
    c.className = "theme-card" + (active ? " active" : "");
    c.innerHTML = '<div class="theme-card-head"><span class="theme-card-name">' + esc(t.name) + '</span><span class="theme-check">' + (active ? "✓" : "") + '</span></div><div class="theme-dots"><span class="theme-dot" style="background:' + t.bg + '"></span><span class="theme-dot" style="background:' + t.panel + '"></span><span class="theme-dot" style="background:' + t.accent + '"></span></div><div class="theme-card-desc">' + esc(t.desc) + '</div>';
    c.addEventListener("click", () => patch({ appearance: { theme: t.id, customAccentHex: "" } }).then(() => renderSettingsBody()));
    g.appendChild(c);
  });
  // Background thumbs
  const box = $("bg-thumbs");
  if (box) {
    box.innerHTML = "";
    const url = a.customTheme && a.customTheme.imageDataUrl;
    if (url) {
      const d = document.createElement("div");
      d.className = "bg-thumb" + (a.useBackgroundImage ? " active" : "");
      d.innerHTML = '<img src="' + url + '"/>';
      d.addEventListener("click", () => patch({ appearance: { useBackgroundImage: true } }));
      box.appendChild(d);
    } else {
      const d = document.createElement("div");
      d.className = "bg-thumb";
      d.innerHTML = '<span style="font-size:10px;color:var(--text3)">None</span>';
      box.appendChild(d);
    }
  }
}

// ─── Clients drawer ───────────────────────────────────────────────────────────
async function showClients() {
  const d = $("clients"), b = $("clients-backdrop"), l = $("clients-list");
  if (!d || !b || !l) return;
  b.classList.add("open"); d.classList.add("open");
  l.innerHTML = '<div class="clients-empty"><h3>Scanning...</h3></div>';
  const r = await api("get_status");
  if (r && r.pids && r.pids.length) {
    l.innerHTML = "";
    r.pids.forEach(pid => {
      const row = document.createElement("div"); row.className = "client-row";
      const isAtt = r.attached_pid === pid;
      row.innerHTML = '<div class="client-info"><span class="client-pid">PID ' + pid + '</span><span class="client-state' + (isAtt ? " attached" : "") + '">' + (isAtt ? "Attached (" + (r.attached_version || "?") + ")" : "Not attached") + '</span></div><button class="client-attach"' + (isAtt ? " disabled" : "") + '>' + (isAtt ? "Attached" : "Attach") + '</button>';
      if (!isAtt) row.querySelector(".client-attach").addEventListener("click", async () => { await doAttach(pid); showClients(); });
      l.appendChild(row);
    });
  } else {
    l.innerHTML = '<div class="clients-empty"><h3>No Roblox running</h3><p>Launch Roblox or use Launch &amp; Inject.</p></div>';
  }
}

// ─── Command palette ─────────────────────────────────────────────────────────
const CMDS = [
  { label: "Execute script", kb: "Ctrl+Enter", run: () => $("rail-execute") && $("rail-execute").click() },
  { label: "Attach to running Roblox", run: () => doAttach() },
  { label: "Launch & Inject (newest)", run: () => doLaunch("") },
  { label: "New tab", kb: "Ctrl+N", run: () => createTab() },
  { label: "Save active script", kb: "Ctrl+S", run: () => $("tb-save") && $("tb-save").click() },
  { label: "Open file", run: () => $("tb-open") && $("tb-open").click() },
  { label: "Toggle terminal", kb: "Ctrl+J", run: () => patch({ console: { showConsole: !(S.settings.console && S.settings.console.showConsole) } }) },
  { label: "Toggle sidebar", kb: "Ctrl+B", run: () => activityClick(S.lastActivity) },
  { label: "Settings", run: () => switchView("settings") },
  { label: "Home", run: () => switchView("home") },
];
function openCmd() {
  const b = $("cmd-back"), i = $("cmd-input");
  if (b) b.classList.add("open"); if (i) { i.value = ""; i.focus(); }
  renderCmd("");
}
function renderCmd(q) {
  const l = $("cmd-list"); if (!l) return;
  l.innerHTML = "";
  const c = (q || "").trim().toLowerCase();
  CMDS.filter(x => !c || x.label.toLowerCase().includes(c)).forEach(cmd => {
    const r = document.createElement("div"); r.className = "cmd-row";
    r.innerHTML = '<span>' + esc(cmd.label) + '</span><span class="cmd-kb">' + esc(cmd.kb || "") + '</span>';
    r.addEventListener("click", () => { const b = $("cmd-back"); if (b) b.classList.remove("open"); cmd.run(); });
    l.appendChild(r);
  });
}

// ─── FX layers ────────────────────────────────────────────────────────────────
function attachFx() {
  document.addEventListener("pointerdown", (e) => {
    const ef = S.settings && S.settings.effects; if (!ef) return;
    const anim = (S.settings.effects && S.settings.effects.masterAnimations !== false && S.settings.effects.reduceMotion !== true);
    if (!anim) return;
    if (ef.ripplesEnabled) {
      const t = e.target.closest("button, .act-btn, .nav-icon, .rail-btn, .s-cat, .tab, .home-action, .theme-card, .tree-item");
      if (t) {
        const r = t.getBoundingClientRect(); const sz = Math.max(r.width, r.height);
        const rp = document.createElement("span");
        rp.style.cssText = "position:absolute;border-radius:50%;pointer-events:none;width:" + sz + "px;height:" + sz + "px;left:" + (e.clientX - r.left - sz/2) + "px;top:" + (e.clientY - r.top - sz/2) + "px;background:color-mix(in srgb,var(--accent) 38%,transparent);transform:scale(0);animation:sparkRise 600ms var(--ease-out) forwards;";
        try { t.appendChild(rp); setTimeout(() => rp.remove(), 620); } catch(_) {}
      }
    }
    if (ef.clickParticles) {
      const N = Math.max(4, Math.min(36, Number(ef.particleCount) || 16));
      const color = ef.particleColor || getComputedStyle(document.documentElement).getPropertyValue("--accent").trim();
      for (let i = 0; i < N; i++) {
        const p = document.createElement("div");
        const angle = (Math.PI * 2 * i) / N + Math.random() * 0.5;
        const dist = 24 + Math.random() * 70;
        p.style.cssText = "position:fixed;width:6px;height:6px;border-radius:50%;pointer-events:none;z-index:99999;left:" + e.clientX + "px;top:" + e.clientY + "px;background:" + color + ";box-shadow:0 0 8px " + color + ";transform:translate(-50%,-50%) scale(1);opacity:1;transition:transform .7s ease-out,opacity .7s ease-out;";
        document.body.appendChild(p);
        requestAnimationFrame(() => { p.style.transform = "translate(calc(-50% + " + (Math.cos(angle)*dist) + "px), calc(-50% + " + (Math.sin(angle)*dist) + "px)) scale(0)"; p.style.opacity = "0"; });
        setTimeout(() => p.remove(), 720);
      }
    }
  });
  // Water cursor
  const canvas = $("water-canvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    if (ctx) {
      let ripples = [], raf = 0, lastMove = 0, lx = null, ly = null;
      const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
      const draw = (now) => {
        raf = 0;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const ef = S.settings && S.settings.effects;
        if (!ef || ef.waterCursor === false || ef.masterAnimations === false || ef.reduceMotion) { ripples = []; return; }
        const hex = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim().replace("#","");
        const cl = /^[0-9a-f]{6}$/i.test(hex) ? hex : "1e3a5f";
        const rr = parseInt(cl.slice(0,2),16), gg = parseInt(cl.slice(2,4),16), bb = parseInt(cl.slice(4,6),16);
        const sz = Math.max(24, Math.min(150, Number(ef.waterSize) || 76));
        const inten = Math.max(1, Math.min(10, Number(ef.waterIntensity) || 5)) / 5;
        const keep = [];
        for (const w of ripples) {
          const p = (now - w.t) / (780 + sz * 2.5);
          if (p >= 1) continue;
          keep.push(w);
          const fade = Math.pow(1 - p, 1.75) * Math.min(1.8, inten);
          const rad = 7 + p * sz;
          ctx.beginPath();
          ctx.lineWidth = 1.2;
          ctx.strokeStyle = "rgba(" + rr + "," + gg + "," + bb + "," + (fade * .28) + ")";
          ctx.ellipse(w.x, w.y, rad, rad * .58, 0, 0, Math.PI * 2);
          ctx.stroke();
        }
        ripples = keep;
        if (ripples.length) raf = requestAnimationFrame(draw);
      };
      const drop = (x, y) => {
        const ef = S.settings && S.settings.effects;
        if (!ef || ef.waterCursor === false) return;
        ripples.push({ x, y, t: performance.now() });
        if (ripples.length > 24) ripples.splice(0, ripples.length - 24);
        if (!raf) raf = requestAnimationFrame(draw);
      };
      resize(); window.addEventListener("resize", resize);
      window.addEventListener("pointermove", (e) => {
        const ef = S.settings && S.settings.effects;
        if (!ef || ef.waterCursor === false || !ef.masterAnimations || ef.reduceMotion) { lx = e.clientX; ly = e.clientY; return; }
        const now = performance.now();
        const dx = lx == null ? 0 : e.clientX - lx;
        const dy = ly == null ? 0 : e.clientY - ly;
        if (now - lastMove > 40 && (lx == null || dx*dx + dy*dy > 150)) { drop(e.clientX, e.clientY); lastMove = now; }
        lx = e.clientX; ly = e.clientY;
      });
      window.addEventListener("pointerdown", e => drop(e.clientX, e.clientY));
    }
  }
}

// ─── Wire all ─────────────────────────────────────────────────────────────────
function wireAll() {
  on("win-min", "click", () => api("window_minimize"));
  on("win-max", "click", () => api("window_maximize"));
  on("win-close", "click", () => api("window_close"));

  $$(".nav-icon[data-view]").forEach(b => b.addEventListener("click", () => switchView(b.getAttribute("data-view"))));
  on("nav-cmd", "click", openCmd);
  on("nav-clients", "click", showClients);
  $$(".act-btn").forEach(b => b.addEventListener("click", () => activityClick(b.getAttribute("data-act"))));
  on("explorer-collapse", "click", () => { S.explorerVisible = false; syncExplorer(); patch({ console: { leftExplorerVisible: false } }); });

  on("tab-new", "click", () => createTab());
  on("tb-open", "click", async () => {
    const r = await api("open_script_file");
    if (r && r.ok) createTab(r.filename, r.content);
    else if (r && r.fallback) { const p = $("pick-script"); if (p) p.click(); }
  });
  on("tb-save", "click", saveActive);
  on("tb-find", "click", () => { const fb = $("find-bar"); if (fb) fb.classList.add("open"); });
  on("tb-copy", "click", async () => { try { const i = $("editor-input"); await navigator.clipboard.writeText(i ? i.value : ""); toast("Copied", "ok"); } catch(_) {} });
  on("rail-save", "click", saveActive);
  on("rail-open", "click", () => { const b = $("tb-open"); if (b) b.click(); });
  on("rail-execute", "click", executeActive);
  on("rail-clear", "click", () => { const i = $("editor-input"); if (i) { i.value = ""; i.dispatchEvent(new Event("input")); } });
  on("rail-launch", "click", () => doLaunch(""));
  on("rail-inject", "click", () => doAttach());

  async function saveActive() {
    const t = S.tabs.find(x => x.id === S.activeTab); if (!t) return;
    const i = $("editor-input"); if (!i) return;
    const r = await api("save_script_file", { filename: t.title, content: i.value, direct: true });
    if (r && r.ok) { t.saved = i.value; t.dirty = false; renderTabs(); log("terminal", 'Saved "' + t.title + '"', "ok"); toast("Saved " + t.title, "ok"); }
    else toast((r && r.error) || "Save failed", "err");
  }
  async function executeActive() {
    const t = S.tabs.find(x => x.id === S.activeTab);
    const i = $("editor-input");
    const r = await api("simulate_execute", { title: t ? t.title : "Untitled", code: i ? i.value : "" });
    if (!r || !r.ok) { log("terminal", (r && r.error) || "Execute failed", "err"); toast((r && r.error) || "Execute failed", "err"); return; }
    log("terminal", 'Executed "' + r.title + '" (' + r.lines + " lines)", "ok");
    toast("Executed " + r.title, "ok");
  }

  const inp = $("editor-input");
  if (inp) {
    inp.addEventListener("input", () => {
      const t = S.tabs.find(x => x.id === S.activeTab);
      if (t) {
        t.content = inp.value;
        const d = t.content !== t.saved;
        if (d !== t.dirty) { t.dirty = d; renderTabs(); }
      }
      refreshEditor(false);
    });
    inp.addEventListener("scroll", () => refreshEditor(false));
    inp.addEventListener("keyup", () => refreshEditor(false));
    inp.addEventListener("keydown", (ev) => {
      const ed = (S.settings && S.settings.editor) || {};
      if (ev.key === "Tab") {
        ev.preventDefault();
        const tabSz = Number(ed.tabSize || 4);
        inp.setRangeText(" ".repeat(tabSz), inp.selectionStart, inp.selectionEnd, "end");
        inp.dispatchEvent(new Event("input"));
      } else if (ev.key === "Enter" && ed.autoIndent !== false) {
        const start = inp.selectionStart;
        const before = inp.value.slice(0, start);
        const cur = before.split("\n").pop() || "";
        const ind = (cur.match(/^\s*/) || [""])[0];
        ev.preventDefault();
        inp.setRangeText("\n" + ind, start, inp.selectionEnd, "end");
        inp.dispatchEvent(new Event("input"));
      } else if (ed.autoCloseBrackets !== false && inp.selectionStart === inp.selectionEnd) {
        const pairs = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'" };
        if (pairs[ev.key]) {
          ev.preventDefault();
          const p = inp.selectionStart;
          inp.setRangeText(ev.key + pairs[ev.key], p, p, "end");
          inp.selectionStart = inp.selectionEnd = p + 1;
          inp.dispatchEvent(new Event("input"));
        }
      }
    });
  }

  $$(".btab").forEach(b => b.addEventListener("click", () => setBottomTab(b.getAttribute("data-btab"))));
  on("term-copy", "click", async () => {
    const txt = (S.logs[S.activeTab2] || []).map(l => "[" + l.ts + "] " + l.text).join("\n");
    try { await navigator.clipboard.writeText(txt); toast("Copied", "ok"); } catch(_) {}
  });
  on("term-clear", "click", () => { S.logs[S.activeTab2] = []; renderLogs(); });

  const rs = $("bottom-resizer");
  if (rs) rs.addEventListener("pointerdown", (ev) => {
    ev.preventDefault();
    const startY = ev.clientY;
    const panel = $("bottom-panel"); if (!panel) return;
    const startH = panel.getBoundingClientRect().height;
    const move = (m) => { panel.style.height = Math.max(80, Math.min(500, startH - (m.clientY - startY))) + "px"; };
    const up = () => { window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); };
    window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
  });

  on("inject-trigger", "click", () => { const m = $("inject-menu"); if (m) m.classList.toggle("open"); });
  document.addEventListener("click", (ev) => {
    if (!ev.target.closest("#inject-menu") && !ev.target.closest("#inject-trigger")) { const m = $("inject-menu"); if (m) m.classList.remove("open"); }
    if (!ev.target.closest("#tab-ctx")) { const m = $("tab-ctx"); if (m) m.classList.remove("open"); }
    if (!ev.target.closest("#file-ctx") && !ev.target.closest(".tree-item")) { const m = $("file-ctx"); if (m) m.classList.remove("open"); }
  });
  on("menu-inject", "click", () => { const m = $("inject-menu"); if (m) m.classList.remove("open"); doAttach(); });
  on("menu-launch", "click", () => { const m = $("inject-menu"); if (m) m.classList.remove("open"); doLaunch(""); });
  on("menu-clients", "click", () => { const m = $("inject-menu"); if (m) m.classList.remove("open"); showClients(); });
  on("menu-kill", "click", async () => {
    const m = $("inject-menu"); if (m) m.classList.remove("open");
    if (!await confirm2("Terminate all Roblox?", "Kill", "Kill", true)) return;
    const r = await api("kill_roblox");
    if (r && r.ok) { log("terminal", "Killed " + r.killed, "warn"); setAttached(false); }
  });

  on("find-close", "click", () => { const fb = $("find-bar"); if (fb) fb.classList.remove("open"); });
  on("find-next", "click", () => {
    const inp = $("editor-input"), fi = $("find-input");
    if (!inp || !fi) return;
    const n = fi.value; if (!n) return;
    const start = inp.selectionEnd;
    let idx = inp.value.indexOf(n, start); if (idx === -1) idx = inp.value.indexOf(n, 0);
    if (idx !== -1) { inp.focus(); inp.setSelectionRange(idx, idx + n.length); }
  });

  on("ctx-rename", "click", async () => {
    const t = S.tabs.find(x => x.id === S.ctxTab); if (!t) return;
    const n = await prompt2("New name:", t.title);
    if (n && n.trim()) { t.title = n.trim(); renderTabs(); }
  });
  on("ctx-dup", "click", () => { const t = S.tabs.find(x => x.id === S.ctxTab); if (t) createTab(t.title + " (copy)", t.content, t.scriptId); });
  on("ctx-autoexec", "click", async () => {
    const t = S.tabs.find(x => x.id === S.ctxTab); if (!t) return;
    const f = /\.(luau|lua|txt)$/i.test(t.title) ? t.title : t.title + ".luau";
    const r = await api("save_script_file", { filename: "autoexec/" + f, content: t.content });
    if (r && r.ok) { S.scripts.push({ id: "disk_" + Date.now(), title: f, folder: "AutoExec", content: t.content }); renderExplorer(); toast("Added to AutoExec", "ok"); }
  });
  on("ctx-close-others", "click", () => { const k = S.tabs.find(x => x.id === S.ctxTab); if (k) { S.tabs = [k]; selectTab(k.id); } });
  on("ctx-close", "click", () => { if (S.ctxTab) closeTab(S.ctxTab); });

  on("file-ctx-open", "click", () => { const s = S.scripts.find(x => x.id === S.ctxFileId); const m = $("file-ctx"); if (m) m.classList.remove("open"); if (s) openScript(s); });
  on("file-ctx-rename", "click", async () => {
    const s = S.scripts.find(x => x.id === S.ctxFileId); const m = $("file-ctx"); if (m) m.classList.remove("open"); if (!s) return;
    const n = await prompt2("New filename:", s.title);
    if (!n) return;
    const safe = /\.(lua|luau|txt)$/i.test(n) ? n : n + ".luau";
    if (String(s.id).startsWith("disk_")) { const r = await api("manage_script_file", { folder: "Scripts", action: "rename", filename: s.title, newFilename: safe }); if (r && r.ok) s.title = r.filename; }
    else s.title = safe;
    renderExplorer();
  });
  on("file-ctx-remove", "click", async () => {
    const s = S.scripts.find(x => x.id === S.ctxFileId); const m = $("file-ctx"); if (m) m.classList.remove("open"); if (!s) return;
    if (String(s.id).startsWith("disk_")) {
      const f = (s.folder || "").toLowerCase().startsWith("autoexec") ? "AutoExec" : "Scripts";
      await api("manage_script_file", { folder: f, action: "delete", filename: s.title });
    }
    S.scripts = S.scripts.filter(x => x.id !== s.id); renderExplorer();
  });
  on("file-ctx-disable", "click", async () => {
    const s = S.scripts.find(x => x.id === S.ctxFileId); const m = $("file-ctx"); if (m) m.classList.remove("open"); if (!s) return;
    if (String(s.id).startsWith("disk_")) {
      const r = await api("manage_script_file", { folder: "AutoExec", action: "disable", filename: s.title });
      if (r && r.ok) { s.title = r.filename; s.disabled = true; renderExplorer(); }
    }
  });

  const closeCl = () => { const d = $("clients"), b = $("clients-backdrop"); if (d) d.classList.remove("open"); if (b) b.classList.remove("open"); };
  on("clients-close", "click", closeCl);
  on("clients-backdrop", "click", closeCl);

  on("cmd-back", "click", (ev) => { if (ev.target.id === "cmd-back") { const b = $("cmd-back"); if (b) b.classList.remove("open"); } });
  on("cmd-input", "input", (e) => renderCmd(e.target.value));
  on("cmd-input", "keydown", (e) => {
    if (e.key === "Escape") { const b = $("cmd-back"); if (b) b.classList.remove("open"); }
    if (e.key === "Enter") { const f = document.querySelector("#cmd-list .cmd-row"); if (f) f.click(); }
  });

  on("settings-search", "input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    $$("#settings-body .s-row").forEach(r => { r.style.display = (!q || r.innerText.toLowerCase().includes(q)) ? "" : "none"; });
  });
  on("settings-back", "click", () => switchView("editor"));

  on("qa-new", "click", () => { switchView("editor"); createTab(); });
  on("qa-attach", "click", () => doAttach());
  on("qa-launch", "click", () => doLaunch(""));
  on("qa-settings", "click", () => switchView("settings"));

  on("pick-script", "change", (e) => { const f = e.target.files && e.target.files[0]; if (!f) return; const r = new FileReader(); r.onload = () => createTab(f.name, String(r.result || "")); r.readAsText(f); });
  on("pick-image", "change", async (e) => {
    const f = e.target.files && e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const url = String(r.result || "");
      const saved = await api("save_custom_theme_image", { filename: f.name, dataUrl: url });
      if (saved && saved.ok) { S.settings = saved.settings; await patch({ appearance: { useBackgroundImage: true } }); renderSettingsBody(); toast("Background applied", "ok"); }
    };
    r.readAsDataURL(f);
  });
  on("pick-avatar", "change", async (e) => {
    const f = e.target.files && e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const url = String(r.result || "");
      const res = await api("save_profile_image", { dataUrl: url });
      if (res && res.ok) { S.profilePic = url; renderExplorer(); toast("Avatar updated", "ok"); }
    };
    r.readAsDataURL(f);
  });
  on("pick-json", "change", async (e) => {
    const f = e.target.files && e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = async () => {
      const res = await api("import_settings_json", { json: String(r.result || "") });
      if (res && res.ok) { S.settings = res.settings; applySettings(); renderSettingsBody(); toast("Imported", "ok"); }
    };
    r.readAsText(f);
  });

  const grip = $("resize-grip");
  if (grip) grip.addEventListener("pointerdown", async (ev) => {
    ev.preventDefault();
    const rect = await api("window_get_rect");
    const sx = ev.screenX, sy = ev.screenY;
    const sw = (rect && rect.width) || 1180, sh = (rect && rect.height) || 720;
    let pending = false;
    const move = async (m) => {
      if (pending) return; pending = true;
      requestAnimationFrame(async () => {
        const nw = Math.max(880, sw + (m.screenX - sx));
        const nh = Math.max(520, sh + (m.screenY - sy));
        await api("window_resize", { width: nw, height: nh });
        pending = false;
      });
    };
    const up = () => { window.removeEventListener("pointermove", move); window.removeEventListener("pointerup", up); };
    window.addEventListener("pointermove", move); window.addEventListener("pointerup", up);
  });

  window.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") { e.preventDefault(); const b = $("rail-execute"); if (b) b.click(); }
    else if (e.ctrlKey && (e.key === "b" || e.key === "B")) { e.preventDefault(); activityClick(S.lastActivity); }
    else if (e.ctrlKey && e.key === "k") { e.preventDefault(); openCmd(); }
    else if (e.ctrlKey && e.key === "s") { e.preventDefault(); const b = $("tb-save"); if (b) b.click(); }
    else if (e.ctrlKey && e.key === "n") { e.preventDefault(); createTab(); }
    else if (e.ctrlKey && e.key === "w") { e.preventDefault(); if (S.activeTab) closeTab(S.activeTab); }
    else if (e.ctrlKey && e.key === "j") { e.preventDefault(); patch({ console: { showConsole: !(S.settings && S.settings.console && S.settings.console.showConsole) } }); }
  });
}

// ─── Boot ─────────────────────────────────────────────────────────────────────
async function boot() {
  if (S.booted) return; S.booted = true;
  try {
    const init = await api("get_initial_state");
    if (init && init.ok) {
      S.settings = init.settings || {};
      S.themes = init.builtinThemes || {};
      S.scripts = init.scripts || [];
      S.app = init.app || {};
      S.profilePic = init.profilePicture || null;
      S.offsets = init.offsets || {};
      S.versions = init.installedVersions || [];
      if (S.settings.console) S.explorerVisible = S.settings.console.leftExplorerVisible !== false;
      if (S.settings.console) S.lastActivity = S.settings.console.lastActivity || "explorer";
      setAttached(!!init.attached);
    } else {
      S.settings = { appearance: {}, effects: {}, editor: {}, console: {}, general: {}, secret: {} };
      S.themes = {};
      toast((init && init.error) || "Using default settings", "warn");
    }
    const g = S.settings.general || {};
    setTxt("h-user", g.userName || "—");
    setTxt("h-plan", g.planName || "—");
    setTxt("h-lic", g.licenseStatus || "Active");
    setTxt("h-exp", g.licenseExpires || "Never");
    setTxt("h-dll", S.offsets.dll_found ? "found" : "missing");
    setTxt("h-off", S.offsets.cached_version || "not cached");
    setTxt("h-vers", (S.versions.length || 0) + " installed");
    setTxt("h-new", (S.versions[0] && S.versions[0].name) || "—");

    applyTheme();
    renderTabs();
    wireAll();
    attachFx();
    applySettings();

    if (S.scripts.length) createTab(S.scripts[0].title, S.scripts[0].content, S.scripts[0].id);
    else createTab("Untitled", "-- Untitled Script\n");

    log("terminal", "Kitty v" + (S.app.version || "4.7.0") + " ready", "ok");
    if (S.offsets.dll_found) log("terminal", "Module.dll: " + S.offsets.dll_path, "info");
    else log("terminal", "Module.dll not found — put it next to kitty.py", "warn");
    log("terminal", "Offsets: " + (S.offsets.cached_version || "not cached"), "info");
    log("terminal", "Installed versions: " + S.versions.length, "info");
  } catch (err) {
    console.error("[boot]", err);
    toast("Startup error — see console", "err");
    if (!S.settings) S.settings = { appearance: {}, effects: {}, editor: {}, console: {}, general: {}, secret: {} };
    try { applySettings(); } catch (_) {}
  } finally {
    const f = $("load-fill"); if (f) f.style.width = "100%";
    setTimeout(() => {
      const l = $("loading");
      if (l) { l.classList.add("hidden"); setTimeout(() => { l.style.display = "none"; }, 400); }
    }, 350);
  }
  setInterval(async () => {
    try {
      const r = await api("get_status");
      if (r && !!r.attached !== S.attached) setAttached(!!r.attached, r.attached_pid, r.attached_version);
    } catch (_) {}
  }, 4000);
}

if (window.pywebview && window.pywebview.api) boot();
else {
  window.addEventListener("pywebviewready", boot, { once: true });
  window.addEventListener("DOMContentLoaded", () => setTimeout(boot, 200), { once: true });
  // In case pywebview is slow, still dismiss loader after 8s
  setTimeout(() => { const l = $("loading"); if (l && !l.classList.contains("hidden")) { l.classList.add("hidden"); } }, 8000);
}
})();
</script>
</body></html>
"""

# ═══════════════════════════════════════════════════════════════════════════════
#  API BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════

class ApiBridge:
    def __init__(self, backend): self._b = backend
    def get_initial_state(self, _p=None): return self._b.get_initial_state()
    def update_settings(self, p=None): return self._b.update_settings(p if isinstance(p, dict) else {})
    def reset_all_settings(self, _p=None): return self._b.reset_all_settings()
    def sync_offsets(self, p=None):
        force = bool((p or {}).get("force", True)) if isinstance(p, dict) else True
        return self._b.sync_offsets(force=force)
    def offsets_status(self, _p=None): return self._b.offsets_status()
    def pick_theme_image(self, _p=None): return self._b.pick_theme_image()
    def pick_profile_image(self, _p=None): return self._b.pick_profile_image()
    def save_profile_image(self, p=None): return self._b.save_profile_image(p if isinstance(p, dict) else {})
    def remove_profile_image(self, _p=None): return self._b.remove_profile_image()
    def save_custom_theme_image(self, p=None): return self._b.save_custom_theme_image(p if isinstance(p, dict) else {})
    def remove_custom_theme_image(self, _p=None): return self._b.remove_custom_theme_image()
    def open_script_file(self, _p=None): return self._b.open_script_file()
    def save_script_file(self, p=None): return self._b.save_script_file(p if isinstance(p, dict) else {})
    def manage_script_file(self, p=None): return self._b.manage_script_file(p if isinstance(p, dict) else {})
    def export_settings_json(self, _p=None): return self._b.export_settings_json()
    def import_settings_json(self, p=None): return self._b.import_settings_json(p if isinstance(p, dict) else {})
    def open_data_folder(self, _p=None): return self._b.open_data_folder()
    def simulate_attach(self, p=None):
        pid = None
        if isinstance(p, dict): pid = p.get("pid")
        return self._b.simulate_attach(pid)
    def launch_and_inject(self, p=None):
        v = str((p or {}).get("version", "")) if isinstance(p, dict) else ""
        return self._b.launch_and_inject(v)
    def simulate_execute(self, p=None): return self._b.simulate_execute(p if isinstance(p, dict) else {})
    def kill_roblox(self, _p=None): return self._b.kill_roblox()
    def get_status(self, _p=None): return self._b.get_status()
    def window_minimize(self, _p=None): return self._b.window_minimize()
    def window_maximize(self, _p=None): return self._b.window_maximize()
    def window_resize(self, p=None): return self._b.window_resize(p if isinstance(p, dict) else {})
    def window_get_rect(self, _p=None): return self._b.window_get_rect()
    def window_close(self, _p=None): return self._b.window_close()


def run_http_fallback(backend):
    backend.runtime_mode = "browser"; bridge = ApiBridge(backend)
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): return
        def _j(self, code, d):
            raw = json.dumps(d, ensure_ascii=False).encode("utf-8")
            self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            if urllib.parse.urlparse(self.path).path in ("/", "/index.html"):
                raw = KITTY_HTML.encode("utf-8")
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw); return
            self._j(404, {"ok": False})
        def do_POST(self):
            path = urllib.parse.urlparse(self.path).path
            if not path.startswith("/api/"): self._j(404, {"ok": False}); return
            m = path[len("/api/"):].strip("/")
            sz = int(self.headers.get("Content-Length", "0") or "0")
            b = self.rfile.read(sz) if sz > 0 else b"{}"
            try: pl = json.loads(b.decode("utf-8")) if b else {}
            except Exception: pl = {}
            fn = getattr(bridge, m, None)
            if not callable(fn): self._j(404, {"ok": False, "error": f"Unknown {m}"}); return
            self._j(200, fn(pl))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    url = f"http://127.0.0.1:{port}/"
    print(f"[{APP_NAME}] Fallback at {url}")
    threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()


def _enable_ansi():
    if os.name != "nt": return
    try:
        k32 = ctypes.windll.kernel32
        h = k32.GetStdHandle(-11); mode = ctypes.wintypes.DWORD()
        if k32.GetConsoleMode(h, ctypes.byref(mode)): k32.SetConsoleMode(h, mode.value | 0x0004)
    except Exception: pass


# Your new KITTY ASCII art (from the reference)
KITTY_ART = (
    "\033[0;93m██\033[0;37m   \033[0;93m██\033[0;37m \033[0;93;42m█▓\033[0;37m \033[0;93;42m█\033[0;93m█\033[0;93;42m█▓█\033[0;93m█\033[0;37m \033[0;93;42m█\033[0;93m█\033[0;93;42m█▓█\033[0;93m█\033[0;37m \033[0;93m▄\033[0;93;42m▓\033[0;37m   \033[0;93;42m█\033[0;93m▄\033[0m\n"
    "\033[0;93;42m▓▒\033[0;37m   \033[0;93;42m▒▓\033[0;37m \033[0;93;42m▓▒\033[0;37m   \033[0;93;42m▓▒\033[0;37m     \033[0;93;42m▓▒\033[0;37m   \033[0;93;42m▓▒\033[0;37m   \033[0;93;42m▒▓\033[0m\n"
    "\033[0;93;42m▒░\033[0;37m   \033[0;93;42m░▒\033[0;37m \033[0;93;42m▒░\033[0;37m   \033[0;93;42m▒░\033[0;37m     \033[0;93;42m▒░\033[0;37m   \033[0;93;42m▒░\033[0;37m   \033[0;93;42m░▒\033[0m\n"
    "\033[0;93;42m░ \033[0;37m  \033[0;32m▄\033[0;93;42m \033[0;32m▀\033[0;37m \033[0;93;42m░ \033[0;37m   \033[0;93;42m░ \033[0;37m     \033[0;93;42m░ \033[0;37m   \033[0;93;42m░ \033[0;37m   \033[0;93;42m ░\033[0m\n"
    "\033[0;34;42m ░   \033[0;32m▄\033[0;37m  \033[0;34;42m ░\033[0;37m   \033[0;34;42m ░\033[0;37m     \033[0;34;42m ░\033[0;37m   \033[0;32m▀\033[0;34;42m░ \033[0;32m▄\033[0;32;42m \033[0;34;42m░ \033[0m\n"
    "\033[0;34;42m░▒\033[0;37m  \033[0;32m▀\033[0;34;42m▒░\033[0;37m \033[0;34;42m░▒\033[0;37m   \033[0;34;42m░▒\033[0;37m     \033[0;34;42m░▒\033[0;37m     \033[0;32m▀▀\033[0;37m \033[0;34;42m▒░\033[0m\n"
    "\033[0;34;42m▒▓\033[0;37m   \033[0;34;42m▓▒\033[0;37m \033[0;34;42m▒▓\033[0;37m   \033[0;34;42m▒▓\033[0;37m     \033[0;34;42m▒▓\033[0;37m   \033[0;34;42m▒▓\033[0;37m   \033[0;34;42m▓▒\033[0m\n"
    "\033[0;34;42m▓\033[0;34m█\033[0;37m   \033[0;34;42m█▓\033[0;37m \033[0;34;42m▓\033[0;34m█\033[0;37m   \033[0;34;42m▓\033[0;34m█\033[0;37m     \033[0;34;42m▓\033[0;34m█\033[0;37m   \033[0;34;42m▓█\033[0;34m▄\033[0;37m  \033[0;34;42m█▓\033[0m\n"
    "\033[0;34m██\033[0;37m   \033[0;34m██\033[0;37m \033[0;34m██\033[0;37m   \033[0;34m██\033[0;37m     \033[0;34m██\033[0;37m    \033[0;34m▀███▀\033[0;37m \033[0m"
)


def print_banner():
    _enable_ansi()
    D = "\033[38;5;240m"; N = "\033[38;5;110m"; OK = "\033[38;5;114m"; BAD = "\033[38;5;210m"; R = "\033[0m"
    print()
    print(KITTY_ART)
    print()
    print(f"  {D}Kitty{R} {N}v{APP_VERSION}{R}  {D}·{R}  {D}premium Roblox workspace{R}")
    print(f"  {D}{'─' * 56}{R}")
    print(f"  {D}runtime{R}    {APP_RUNTIME_DIR}")
    dll = _resolve_dll()
    print(f"  {D}module{R}     {dll if dll else 'NOT FOUND — put ' + DLL_NAME + ' next to kitty.py'}")
    print(f"  {D}platform{R}   {platform.system()} {platform.release()}")
    print(f"  {D}python{R}     {platform.python_version()}")
    print(f"  {D}pywebview{R}  {OK+'yes'+R if HAS_PYWEBVIEW else BAD+'no'+R}")
    print(f"  {D}pillow{R}     {OK+'yes'+R if HAS_PIL else BAD+'no'+R}")
    print(f"  {D}pystray{R}    {OK+'yes'+R if HAS_PYSTRAY else BAD+'no'+R}")
    print(f"  {D}psutil{R}     {OK+'yes'+R if HAS_PSUTIL else BAD+'no'+R}")
    installed = list_installed_versions()
    print(f"  {D}versions{R}   {len(installed)} installed" + (f" (newest: {installed[0]['name']})" if installed else ""))
    print(f"  {D}{'─' * 56}{R}")
    print()


def _print_help():
    print("=" * 72)
    print(f"[{APP_NAME}] pywebview failed to start.")
    print("")
    print("  Install WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703")
    print("  Then: pip install pywebview")
    print("")
    print("  Or:   python kitty.py --browser")
    print("=" * 72)


def main():
    global _main_window
    print_banner()
    argv = sys.argv[1:]
    if "--browser" in argv:
        run_http_fallback(KittyBackend()); return
    if not HAS_PYWEBVIEW:
        print("pywebview not installed. pip install pywebview  OR  python kitty.py --browser")
        sys.exit(1)
    backend = KittyBackend()
    init_system_tray()
    gen = backend.settings.get("general", {})
    start_global_hotkey(str(gen.get("globalToggleKey", "Insert")))
    apply_process_priority_win32(str(gen.get("performanceMode", "medium")))
    try:
        bridge = ApiBridge(backend)
        _main_window = webview.create_window(
            title="Spotify" if gen.get("disguiseMode") else APP_NAME,
            html=KITTY_HTML, js_api=bridge,
            width=1180, height=720, min_size=(880, 520),
            frameless=True, easy_drag=False, background_color="#f4ede1")
        if gen.get("streamproof"):
            threading.Timer(1.2, lambda: apply_streamproof_win32(True)).start()
        webview.start(debug=False)
        stop_global_hotkey(); return
    except Exception as e:
        print(f"[{APP_NAME}] pywebview raised: {e}")
        if "--force" in argv: run_http_fallback(backend); return
        _print_help(); sys.exit(1)


if __name__ == "__main__":
    main()
