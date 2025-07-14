# Neovim Configuration: A Deep Dive

This document provides a comprehensive overview of the Serein Neovim setup, a custom-built development environment managed with `lazy.nvim`. This configuration is *not* based on NvChad and has been tailored for a unique and efficient workflow, blending aesthetics with powerful functionality.

## Core Philosophy

The configuration is built on a modular and organized structure, located in `lua/`.

- **`init.lua`**: The main entry point that loads core settings and the plugin manager.
- **`lua/serein/`**: This directory contains the core, non-plugin configuration for Neovim itself.
  - `options.lua`: Sets global Neovim options for behavior, text rendering, and user interface.
  - `keymaps.lua`: Defines all custom keybindings for navigation, commands, and plugin integrations.
  - `pkgman.lua`: Handles the bootstrapping and setup of the `lazy.nvim` plugin manager.
- **`lua/plugins/`**: Each file in this directory configures a specific plugin or a group of related plugins, keeping the setup clean and easy to manage.

## Key Features & Plugins

### 1. Startup & Dashboard (`alpha-nvim`)

The first thing you see is a custom dashboard powered by `alpha-nvim`, providing a dynamic and functional entry point.

- **Main Dashboard**: Offers quick access to common tasks like finding files, browsing Git repositories, or opening the file manager. It also features a prominent Serein-branded header.
- **Serein CLI Hub**: A unique, secondary dashboard dedicated to managing the Serein environment itself. From here, you can directly run `serein update`, `serein rollback`, and other essential commands from within Neovim.
- **Seamless Integration**: The dashboard automatically reappears after you close terminal-based tools like `ranger` or `serein`, ensuring a consistent workflow.

### 2. Development Environment

The configuration is a capable IDE for multiple languages, with a strong focus on LSP integration and code assistance.

- **LSP & Tooling (`mason.nvim`, `nvim-lspconfig`)**: Language servers for Python (`pyright`), C/C++ (`clangd`), and Lua (`lua_ls`) are installed automatically. The setup provides standard LSP features like diagnostics, code actions, and hover information.
- **Treesitter (`nvim-treesitter`)**: Provides robust and accurate syntax highlighting, indentation, and code navigation for a wide range of languages.
- **Auto-Completion (`nvim-cmp`)**: Offers intelligent, context-aware code completion sourced from the LSP and the current buffer.
- **Auto-Formatting (`conform.nvim`)**: Automatically formats code on save for supported filetypes (like Lua with `stylua`), with the ability to manually format using `<leader>f`.
- **Git Integration (`gitsigns.nvim`)**: Provides Git status indicators directly in the sign column, showing added, changed, or deleted lines.

### 3. File & Project Navigation

- **Fuzzy Finding (`telescope.nvim`)**: Telescope is the primary tool for navigating files and projects. It's configured to:
  - Find files (`<leader>ff`), live grep for text (`<leader>fg`), and browse open buffers (`<leader>fb`).
  - Ignore common nuisance directories and files (e.g., `__pycache__`, media files) for cleaner results.
  - Use `fzf-native` for a significant performance boost.
- **File Explorer (`neo-tree.nvim`)**: A modern file explorer that can be toggled with `<leader>e`. It features a unique "window picker" integration, allowing you to choose exactly which split to open a file in.
- **Git Repository Picker**: A custom Telescope picker, available via the `:OpenGitRepos` command, scans your home directory for Git repositories and opens the selected one in a `gitui` terminal session.

### 4. User Interface & Experience

- **Theme (`nord-vim`)**: The Nord colorscheme provides a clean, dark, and consistent look. The configuration is set up for a **transparent background**, allowing it to blend seamlessly with your terminal's appearance.
- **Status Line (`lualine.nvim`)**: A sleek and informative status line that displays the current mode, Git branch, file information, and diagnostics.
- **Keybinding Hints (`which-key.nvim`)**: An indispensable plugin that displays available keybindings after you press `<leader>`, making the custom keymaps easy to discover and learn.
- **Colorizer (`nvim-colorizer.lua`)**: Automatically highlights color codes (e.g., `#RRGGBB`) with their actual color, which is incredibly useful for CSS, web development, and configuration files.

### 5. Custom Keymaps & Options

The configuration is highly ergonomic, with a focus on the `<leader>` key (mapped to `Space`).

- **Window Navigation**: Uses `Ctrl + H/J/K/L` for fast and intuitive split navigation.
- **Telescope**: All Telescope pickers are conveniently mapped under `<leader>f`.
- **File Management**: `<leader>e` toggles the file explorer, and `<leader>ws` provides a quick way to save a new file.
- **Typing**: Aside from regular keybindings, `<leader>wr` conveniently conveniently replaces multiple instances of words at once.
- **Clipboard**: System clipboard integration is enabled, so standard yank/put operations work as expected.
- **Quality of Life**: Settings like `smartcase` for searching, `undofile` for persistent undo, and custom list characters enhance the editing experience.
