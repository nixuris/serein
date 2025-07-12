## Neovim Setup

The Neovim configuration is a custom setup managed with `lazy.nvim`, providing a highly personalized and efficient development environment. It is *not* based on NvChad.

### Key Features:

*   **Plugin Management:** Utilizes `lazy.nvim` for efficient and declarative plugin management.
*   **Dashboard:** A custom dashboard powered by `alpha.nvim` provides a welcoming interface with quick access to common actions (new file, find file, recent files, grep) and displays plugin load statistics.
*   **Language Server Protocol (LSP):** Configured with `nvim-lspconfig` and `mason.nvim` for automatic installation and setup of language servers. It includes out-of-the-box support for:
    *   **Python:** `pyright`
    *   **C/C++:** `clangd`
    Common LSP features like hover information, renaming, code actions, and go-to definition are readily available. `neodev.nvim` is used to enhance Lua development within Neovim itself.
*   **Fuzzy Finding:** Integrated with `telescope.nvim` and `telescope-fzf-native.nvim` for fast and powerful fuzzy finding of files, live grepping, buffer navigation, and help tag searching. It includes custom ignore patterns for various non-code files and directories.
*   **File Explorer:** `neo-tree.nvim` provides a robust file explorer with seamless integration for opening files in specific windows.
*   **Status Line:** `lualine.nvim` displays a clean and informative status line with a "nord" theme, showing essential information like current mode, Git branch, file status, diagnostics, and more.
*   **Completion:** `nvim-cmp` offers intelligent code completion, leveraging LSP suggestions and buffer content. It's also integrated with `LuaSnip` for snippet expansion.
*   **Custom Keymaps & Options:** A comprehensive set of custom keybindings and Neovim options are configured for enhanced navigation, window management, and overall user experience. This includes leader key mappings, clipboard integration, and visual settings.