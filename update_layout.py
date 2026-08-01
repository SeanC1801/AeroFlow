import re

with open('templates/index.html', 'w') as f:
    f.write("""<!DOCTYPE html>
<html class="light" lang="en">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>AeroFlow - Kanban Board</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Work+Sans:wght@600&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
<script id="tailwind-config">
  tailwind.config = {
    darkMode: "class",
    theme: {
      extend: {
        colors: {
                "primary-container": "#0099ff",
                "on-background": "#191c1e",
                "on-secondary-container": "#00743a",
                "on-secondary-fixed": "#00210c",
                "on-error": "#ffffff",
                "secondary-container": "#6bfe9c",
                "tertiary-fixed": "#ffe084",
                "tertiary-container": "#cea700",
                "outline-variant": "#bfc7d5",
                "surface-dim": "#d8dadc",
                "surface-container-high": "#e6e8ea",
                "primary": "#0061a5",
                "on-primary-fixed-variant": "#00497e",
                "on-secondary-fixed-variant": "#005228",
                "on-primary-fixed": "#001d36",
                "on-primary-container": "#002f54",
                "secondary-fixed": "#6bfe9c",
                "on-secondary": "#ffffff",
                "on-error-container": "#93000a",
                "surface-container": "#eceef0",
                "surface-tint": "#0061a5",
                "inverse-surface": "#2d3133",
                "secondary": "#006d37",
                "on-tertiary-fixed-variant": "#574500",
                "error": "#ba1a1a",
                "surface-variant": "#e0e3e5",
                "surface-container-lowest": "#ffffff",
                "primary-fixed": "#d2e4ff",
                "surface-container-highest": "#e0e3e5",
                "on-surface-variant": "#3f4753",
                "outline": "#707884",
                "inverse-primary": "#9fcaff",
                "background": "#f7f9fb",
                "surface-container-low": "#f2f4f6",
                "secondary-fixed-dim": "#4ae183",
                "on-tertiary-container": "#4e3d00",
                "on-tertiary-fixed": "#231b00",
                "tertiary": "#735c00",
                "primary-fixed-dim": "#9fcaff",
                "inverse-on-surface": "#eff1f3",
                "error-container": "#ffdad6",
                "on-surface": "#191c1e",
                "on-primary": "#ffffff",
                "tertiary-fixed-dim": "#eec209",
                "surface-bright": "#f7f9fb",
                "surface": "#f7f9fb",
                "on-tertiary": "#ffffff"
        },
        borderRadius: {
                "DEFAULT": "1rem",
                "lg": "2rem",
                "xl": "3rem",
                "full": "9999px"
        },
        spacing: {
                "unit": "8px",
                "container-max": "1280px",
                "margin-lg": "40px",
                "gutter-md": "24px"
        },
        fontFamily: {
                "label-sm": ["Work Sans"],
                "headline-xl": ["Plus Jakarta Sans"],
                "headline-lg-mobile": ["Plus Jakarta Sans"],
                "headline-lg": ["Plus Jakarta Sans"],
                "body-md": ["Plus Jakarta Sans"]
        },
        fontSize: {
                "label-sm": ["12px", { "lineHeight": "1.2", "letterSpacing": "0.05em", "fontWeight": "600" }],
                "headline-xl": ["48px", { "lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "700" }],
                "headline-lg-mobile": ["28px", { "lineHeight": "1.2", "fontWeight": "700" }],
                "headline-lg": ["32px", { "lineHeight": "1.2", "fontWeight": "700" }],
                "body-md": ["16px", { "lineHeight": "1.6", "fontWeight": "400" }]
        },
        animation: {
            "flow": "flow 20s ease-in-out infinite alternate",
            "gleam": "gleam 2s infinite linear",
            "sound-pulse": "sound-pulse 0.3s ease-out"
        },
        keyframes: {
            "flow": {
                "0%": { backgroundPosition: "0% 50%" },
                "100%": { backgroundPosition: "100% 50%" }
            },
            "gleam": {
                "0%": { transform: "translateX(-100%) rotate(45deg)" },
                "100%": { transform: "translateX(200%) rotate(45deg)" }
            },
            "sound-pulse": {
                "0%": { transform: "scale(1)", boxShadow: "0 0 0 0 rgba(255,255,255,0.7)" },
                "50%": { transform: "scale(0.95)", boxShadow: "0 0 0 10px rgba(255,255,255,0)" },
                "100%": { transform: "scale(1)", boxShadow: "0 0 0 0 rgba(255,255,255,0)" }
            }
        }
      }
    }
  }
</script>
<link rel="stylesheet" href="/static/css/styles.css?v=6">
</head>

<body class="font-body-md text-on-surface antialiased h-screen overflow-hidden flex flex-col" style="font-family: 'Segoe UI', 'Frutiger', 'Trebuchet MS', 'Tahoma', sans-serif; -webkit-font-smoothing: antialiased; background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuDQyHuhIcIMnGGgXRUy7Xa1g3XTSZ4HRatKwXutxaQicM-fBZn0gfZeWJDvkjMFF-z1EnwRdWgSQBpkgY5BtcwvSASQhrOGihzDbHCTvMkYMHyiaMg-ZILz9RYSfepw0AmBl0OHSK3gYv0MitAULI4KSS4XJCtikyF_8HRqgLbWiMay0eDX5tszydnJBDMMdKhbT6doGM54HhKY3_17gFf6AvMLFBAMVWiXZZ4H5kTg0zmaqRSek64hd5CoRQVZbMInVNbvad4_ZPEM'); background-size: 120% 120%; background-position: 0% 50%; background-repeat: no-repeat; background-attachment: fixed; animation: flowAurora 35s ease-in-out infinite alternate; overflow: hidden;">

<!-- TopNavBar -->
<nav class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-gutter-md h-16 shadow-[0_4px_24px_0_rgba(0,0,0,0.05)] transition-all duration-300" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-bottom: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
  <div class="flex items-center gap-8">
    <span class="font-headline-lg text-[24px] font-bold tracking-tight text-[#0061a5] bg-clip-text drop-shadow-md" style="background: linear-gradient(135deg, #00FF88 0%, #00AA55 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.4)); font-weight: 600;">AeroFlow</span>
    <div class="hidden md:flex gap-6 items-center">
      <a class="nav-tab active-tab text-white font-bold border-b-2 pb-1 font-label-sm text-label-sm transition-all duration-300 px-2" href="#" data-view="board" style="text-shadow: rgba(0, 0, 0, 0.8) 0px 1px 2px; border-bottom: 2px solid rgb(32, 224, 112); font-weight: 600;">Sprint Board</a>
      <a class="nav-tab text-white font-bold hover:text-[#0061a5] transition-colors font-label-sm text-label-sm px-2 py-1" href="#" data-view="members" style="text-shadow: rgba(0, 0, 0, 0.8) 0px 1px 2px;">Members</a>
      <a id="nav-calendar-tab" class="nav-tab text-white font-bold hover:text-[#0061a5] transition-colors font-label-sm text-label-sm px-2 py-1" href="#" data-view="calendar" style="text-shadow: rgba(0, 0, 0, 0.8) 0px 1px 2px;">Calendar Grid</a>
      <a class="nav-tab text-white font-bold hover:text-[#0061a5] transition-colors font-label-sm text-label-sm px-2 py-1" href="#" data-view="resources" style="text-shadow: rgba(0, 0, 0, 0.8) 0px 1px 2px;">Resource Hub</a>
    </div>
  </div>
  <div class="flex items-center gap-4">
    <div class="relative hidden sm:block">
      <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#C0E0D0] text-[18px]">search</span>
      <input id="command-input" class="search-input pl-10 pr-4 py-2 rounded-full text-label-sm font-bold focus:outline-none w-64" placeholder="Type / for commands..." type="text" autocomplete="off" style="background: rgba(10, 25, 20, 0.75); box-shadow: rgba(0, 0, 0, 0.7) 0px 2px 5px inset, rgba(255, 255, 255, 0.15) 0px 1px 0px; border: 1px solid rgba(140, 255, 190, 0.25); color: rgb(192, 224, 208);">
      <div id="command-dropdown" class="command-dropdown hidden">
        <button class="command-option" data-cmd="/summary"><span class="material-symbols-outlined text-[16px]">summarize</span><span><strong>/summary</strong> &mdash; Generate Daily Standup Report</span></button>
        <button class="command-option" data-cmd="/filter "><span class="material-symbols-outlined text-[16px]">filter_alt</span><span><strong>/filter [text]</strong> &mdash; Dim non-matching cards</span></button>
      </div>
    </div>
  </div>
</nav>

<div class="flex flex-1 pt-16 h-full relative z-10">

  <!-- SideNavBar -->
  <aside id="app-sidebar" class="hidden lg:flex flex-col w-64 z-40 py-8 px-4 transition-all duration-300" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-right: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
    <div class="mb-8 flex items-center gap-3 px-2">
      <div class="w-10 h-10 rounded-full bg-[#0099ff] flex items-center justify-center shadow-md logo-container shrink-0">
        <span class="material-symbols-outlined text-white text-[20px]">workspaces</span>
      </div>
      <div class="sidebar-label">
        <h2 class="font-label-sm text-label-sm font-bold text-white drop-shadow-sm">Global Workspace</h2>
        <p class="font-label-sm text-[10px] text-white/70 drop-shadow-sm">Productivity Suite</p>
      </div>
    </div>
    <nav class="flex flex-col gap-2 flex-1 overflow-y-auto board-scroll">
      <div class="sidebar-section-header flex items-center rounded-xl hover:bg-white/10 transition-all"
           style="box-sizing: border-box; padding: 6px 12px; margin: 4px 0; line-height: 1.4; display: flex; align-items: center; justify-content: space-between; overflow: visible;">
        <a class="side-link flex-1 flex items-center gap-3 px-2 py-3 rounded-xl" href="#" id="projects-toggle">
          <span class="material-symbols-outlined shrink-0 text-white text-[18px]">account_tree</span>
          <span class="sidebar-label font-label-sm text-label-sm whitespace-nowrap text-white font-bold" style="text-shadow: 0 1px 2px rgba(0,0,0,0.5);">Projects</span>
        </a>
        <button id="project-add-btn" class="sidebar-label shrink-0 mr-2 p-1 rounded-full text-white hover:text-[#6bfe9c] hover:bg-white/10 transition-colors" title="New project">
          <span class="material-symbols-outlined text-[20px]">add</span>
        </button>
      </div>
      <div id="sidebar-project-list" class="sidebar-label flex flex-col gap-1 pl-2 ml-4 border-l border-white/20" style="overflow: visible;"></div>
    </nav>
    <div class="mt-auto flex flex-col items-start gap-4">
      <button id="sidebar-toggle" class="mr-auto p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors shadow-sm text-white/70 flex items-center justify-center w-8 h-8 border border-white/20">
        <span id="sidebar-toggle-icon" class="material-symbols-outlined text-[18px]">keyboard_double_arrow_left</span>
      </button>
    </div>
  </aside>

  <!-- Main Dashboard Canvas -->
  <main class="flex-1 p-gutter-md h-full overflow-hidden flex flex-col gap-6">

    <header class="flex justify-between items-center shrink-0 p-8 rounded-3xl" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
      <div class="min-w-0">
        <div class="flex items-center gap-2 group mb-2">
          <h1 id="project-title" class="font-headline-xl text-[40px] text-white drop-shadow-md tracking-tight font-extrabold font-semibold cursor-text truncate" title="Click to rename" style="text-shadow: 0 2px 4px rgba(0,0,0,0.5);">Sprint Board</h1>
          <button id="project-title-edit" class="opacity-0 group-hover:opacity-100 transition-opacity text-[#20E070]" title="Rename project">
            <span class="material-symbols-outlined">edit</span>
          </button>
        </div>
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 bg-[#d2e4ff] text-[#00497e] font-label-sm text-label-sm font-bold rounded-full shadow-sm code-badge">Project Code: <span id="project-code-label" class="font-bold">DEMO-123</span></span>
          <span class="text-white/80 font-body-md text-[14px]">· <span id="view-subtitle">Manage and track your active tasks.</span></span>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button id="add-task-btn" class="sound-button relative overflow-hidden bg-gradient-to-r from-primary-container to-primary text-white px-6 py-2.5 rounded-full font-label-sm text-label-sm font-bold flex items-center gap-2 hover:scale-105 transition-transform shadow-[0_4px_12px_rgba(0,153,255,0.4)] border border-white/40 group shrink-0" style="background: linear-gradient(180deg, #20E070 0%, #10A040 100%); border: 2px solid rgba(255, 255, 255, 0.8); box-shadow: inset 0 1px 1px rgba(255,255,255,0.6), 0 4px 15px rgba(16, 160, 64, 0.5); text-shadow: rgba(0, 0, 0, 0.3) 0px 1px 2px; font-weight: 600;">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full group-hover:animate-gleam"></div>
          <span class="material-symbols-outlined text-[18px]">add</span> Add New Task
        </button>
      </div>
    </header>

    <!-- ===================== VIEW: BOARD ===================== -->
    <section id="view-board" class="view flex-1 overflow-hidden w-full">
      <div class="grid grid-cols-4 gap-6 h-full px-2 py-2 w-full" style="display: grid; grid-template-columns: repeat(4, minmax(0px, 1fr)); gap: 16px; width: 100%; box-sizing: border-box;">
        
        <!-- Column 1: To-Do -->
        <div class="glass-tray rounded-[2.5rem] p-4 flex flex-col gap-4 h-full min-h-0" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
          <div class="glass-panel rounded-full px-5 py-3 flex justify-between items-center sticky top-0 z-10 shadow-[0_2px_10px_rgba(0,0,0,0.1)]" style="background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 1);">
            <span class="font-label-sm text-[13px] font-extrabold text-[#191c1e] flex items-center gap-3 drop-shadow-sm tracking-wide">
              <span class="w-3.5 h-3.5 rounded-full bg-[#cea700] shadow-[0_0_8px_rgba(206,167,0,0.8),inset_0_1px_2px_rgba(255,255,255,0.8)] border border-white/50"></span> To-Do
            </span>
            <span class="count-badge bg-[#191c1e]/5 px-2.5 py-0.5 rounded-full font-label-sm text-[11px] font-bold text-[#191c1e]" data-count="todo">0</span>
          </div>
          <div class="flex-1 overflow-y-auto board-scroll pr-1 flex flex-col gap-4 pb-4" data-status="todo"></div>
        </div>
        
        <!-- Column 2: In Progress -->
        <div class="glass-tray rounded-[2.5rem] p-4 flex flex-col gap-4 h-full min-h-0" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
          <div class="glass-panel rounded-full px-5 py-3 flex justify-between items-center sticky top-0 z-10 shadow-[0_2px_10px_rgba(0,0,0,0.1)]" style="background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 1);">
            <span class="font-label-sm text-[13px] font-extrabold text-[#191c1e] flex items-center gap-3 drop-shadow-sm tracking-wide">
              <span class="w-3.5 h-3.5 rounded-full bg-[#0099ff] shadow-[0_0_8px_rgba(0,153,255,0.8),inset_0_1px_2px_rgba(255,255,255,0.8)] border border-white/50 animate-pulse"></span> In Progress
            </span>
            <span class="count-badge bg-[#191c1e]/5 px-2.5 py-0.5 rounded-full font-label-sm text-[11px] font-bold text-[#191c1e]" data-count="in_progress">0</span>
          </div>
          <div class="flex-1 overflow-y-auto board-scroll pr-1 flex flex-col gap-4 pb-4" data-status="in_progress"></div>
        </div>
        
        <!-- Column 3: Done -->
        <div class="glass-tray rounded-[2.5rem] p-4 flex flex-col gap-4 h-full min-h-0" style="background: linear-gradient(180deg, rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(140, 255, 190, 0.25); box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.45), inset 0 -1px 2px rgba(0, 0, 0, 0.4), 0 8px 32px rgba(0, 0, 0, 0.45);">
          <div class="glass-panel rounded-full px-5 py-3 flex justify-between items-center sticky top-0 z-10 shadow-[0_2px_10px_rgba(0,0,0,0.1)]" style="background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.5);">
            <span class="font-label-sm text-[13px] font-extrabold text-[#191c1e] flex items-center gap-3 drop-shadow-sm tracking-wide">
              <span class="w-3.5 h-3.5 rounded-full bg-[#006d37] shadow-[0_0_8px_rgba(0,109,55,0.8),inset_0_1px_2px_rgba(255,255,255,0.8)] border border-white/50"></span> Done
            </span>
            <span class="count-badge bg-[#191c1e]/5 px-2.5 py-0.5 rounded-full font-label-sm text-[11px] font-bold text-[#191c1e]" data-count="done">0</span>
          </div>
          <div class="flex-1 overflow-y-auto board-scroll pr-1 flex flex-col gap-4 pb-4" data-status="done"></div>
        </div>
        
        <!-- Column 4: Approved -->
        <div class="glass-tray rounded-[2.5rem] p-4 flex flex-col gap-4 h-full min-h-0" style="background: linear-gradient(rgba(22, 48, 38, 0.75) 0%, rgba(12, 28, 22, 0.85) 100%); backdrop-filter: blur(16px); border: 1px solid rgba(140, 255, 190, 0.25); box-shadow: rgba(255, 255, 255, 0.45) 0px 1px 1px inset, rgba(0, 0, 0, 0.4) 0px -1px 2px inset, rgba(0, 0, 0, 0.45) 0px 8px 32px;">
          <div class="glass-panel rounded-full px-5 py-3 flex justify-between items-center sticky top-0 z-10 shadow-[0_2px_10px_rgba(0,0,0,0.1)]" style="background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.4);">
            <span class="font-label-sm text-[13px] font-extrabold text-[#191c1e] flex items-center gap-3 drop-shadow-sm tracking-wide">
              <span class="w-3.5 h-3.5 rounded-full bg-[#0099ff] shadow-[0_0_8px_rgba(0,153,255,0.8),inset_0_1px_2px_rgba(255,255,255,0.8)] border border-white/50"></span> Approved
            </span>
            <span class="count-badge bg-[#191c1e]/5 px-2.5 py-0.5 rounded-full font-label-sm text-[11px] font-bold text-[#191c1e]" data-count="approved">0</span>
          </div>
          <div class="flex-1 overflow-y-auto board-scroll pr-1 flex flex-col gap-4 pb-4" data-status="approved"></div>
        </div>

      </div>
    </section>

    <!-- ===================== VIEW: MEMBERS ===================== -->
    <section id="view-members" class="view hidden flex-1 overflow-y-auto board-scroll">
      <div id="members-grid" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6 p-2"></div>
    </section>

    <!-- ===================== VIEW: CALENDAR (Mon–Sun) ===================== -->
    <section id="view-calendar" class="view hidden flex-1 overflow-y-auto board-scroll flex flex-col gap-4 p-2">
      <div>
        <h3 class="font-label-sm text-label-sm font-bold text-white mb-2 drop-shadow-sm" style="text-shadow: 0 1px 2px rgba(0,0,0,0.5);">Unscheduled</h3>
        <div id="calendar-unscheduled" class="glass-tray rounded-2xl p-3 flex flex-wrap gap-3 min-h-[70px]" data-cal-day=""></div>
      </div>
      <div id="calendar-grid" class="grid grid-cols-7 gap-3 flex-1 min-h-0"></div>
    </section>

    <!-- ===================== VIEW: RESOURCES (Link Hub) ===================== -->
    <section id="view-resources" class="view hidden flex-1 overflow-y-auto board-scroll p-2 flex flex-col gap-6">
      <form id="resource-form" class="glass-tray rounded-2xl p-4 flex flex-wrap gap-3 items-end">
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold text-white/70">Title</label>
          <input id="res-title" class="edit-field w-48" placeholder="e.g. Figma Board" required>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold text-white/70">URL</label>
          <input id="res-url" class="edit-field w-64" placeholder="https://..." type="url" required>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold text-white/70">Category</label>
          <input id="res-category" class="edit-field w-40" placeholder="GitHub / Drive / ...">
        </div>
        <button class="btn-save" type="submit">Add Link</button>
      </form>
      <div id="resources-list" class="flex flex-col gap-6"></div>
    </section>

    <!-- HUD Interaction Affordance -->
    <div class="hud-helper-bar">💡 Tip: Double-click notes to inspect read-only details • Click ✎ to edit • Drag to Calendar tab to schedule</div>

  </main>
</div>

<!-- Standup Summary Modal -->
<div id="summary-modal" class="summary-modal-overlay hidden">
  <div class="summary-modal">
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-headline-lg text-[24px] font-bold text-white" style="text-shadow: 0 1px 2px rgba(0,0,0,0.5);">Daily Standup Report</h2>
      <button id="summary-close" class="p-1 rounded-full hover:bg-white/20 transition-colors text-white">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <pre id="summary-content" class="summary-content board-scroll"></pre>
    <div class="flex justify-end mt-4 gap-3">
      <button id="summary-copy" class="jelly-button px-5 py-2 rounded-full font-label-sm text-label-sm font-bold flex items-center gap-2 hover:scale-105 transition-transform">
        <span class="material-symbols-outlined text-[16px]">content_copy</span> Copy to Clipboard
      </button>
    </div>
  </div>
</div>

<!-- Toast notification -->
<div id="toast" class="toast hidden"></div>

<script type="module" src="/static/js/board.js?v=4"></script>
</body>
</html>
""")

with open('static/css/styles.css', 'r') as f:
    css = f.read()

# Replace the gradient blocks
css = re.sub(
    r'\.sticky-lime\s+\.card-face__surface\s*\{[^\}]+\}',
    '.sticky-lime  .card-face__surface { background: linear-gradient(135deg, #6bfe9c, #4ae183); border: 1px solid rgba(255,255,255,0.6); }\n'
    '.sticky-lime .js-title { color: #00210c !important; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 16px !important; }\n'
    '.sticky-lime .js-username { color: #005228 !important; }\n'
    '.sticky-lime .avatar-badge { color: #006d37 !important; border: 1px solid rgba(255,255,255,0.8); background: rgba(255,255,255,0.5); }',
    css
)

css = re.sub(
    r'\.sticky-sunny\s+\.card-face__surface\s*\{[^\}]+\}',
    '.sticky-sunny .card-face__surface { background: linear-gradient(135deg, #ffe084, #eec209); border: 1px solid rgba(255,255,255,0.6); }\n'
    '.sticky-sunny .js-title { color: #4e3d00 !important; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 16px !important; }\n'
    '.sticky-sunny .js-username { color: #574500 !important; }\n'
    '.sticky-sunny .avatar-badge { color: #735c00 !important; border: 1px solid rgba(255,255,255,0.8); background: rgba(255,255,255,0.5); }',
    css
)

css = re.sub(
    r'\.sticky-aqua\s+\.card-face__surface\s*\{[^\}]+\}',
    '.sticky-aqua  .card-face__surface { background: linear-gradient(135deg, #d2e4ff, #9fcaff); border: 1px solid rgba(255,255,255,0.6); }\n'
    '.sticky-aqua .js-title { color: #002f54 !important; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 16px !important; }\n'
    '.sticky-aqua .js-username { color: #00497e !important; }\n'
    '.sticky-aqua .avatar-badge { color: #0061a5 !important; border: 1px solid rgba(255,255,255,0.8); background: rgba(255,255,255,0.5); }',
    css
)

css = re.sub(
    r'\.sticky-pink\s+\.card-face__surface\s*\{[^\}]+\}',
    '.sticky-pink  .card-face__surface { background: linear-gradient(135deg, #ffdad6, #ffb4ab); border: 1px solid rgba(255,255,255,0.6); }\n'
    '.sticky-pink .js-title { color: #3f0000 !important; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 16px !important; }\n'
    '.sticky-pink .js-username { color: #93000a !important; }\n'
    '.sticky-pink .avatar-badge { color: #93000a !important; border: 1px solid rgba(255,255,255,0.8); background: rgba(255,255,255,0.5); }',
    css
)

css = re.sub(
    r'\.avatar-badge\s*\{[^\}]+\}',
    '.avatar-badge {\n'
    '    position: absolute; top: 1rem; right: 1rem;\n'
    '    width: 1.75rem; height: 1.75rem; border-radius: 9999px;\n'
    '    background: rgba(255,255,255,0.5); color: #0061a5;\n'
    '    display: flex; align-items: center; justify-content: center;\n'
    '    font-weight: 700; font-size: 10px; font-family: \'Work Sans\', sans-serif;\n'
    '    border: 1px solid rgba(255,255,255,0.8); backdrop-filter: blur(4px);\n'
    '    box-shadow: 0 1px 2px rgba(0,0,0,0.05);\n'
    '}',
    css
)

with open('static/css/styles.css', 'w') as f:
    f.write(css)
