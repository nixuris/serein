return {

  -- Telescope with hidden files
  {
    "nvim-telescope/telescope.nvim",
    dependencies = {
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    },
    config = function()
      local telescope = require "telescope"
      telescope.setup {
        defaults = {
          file_ignore_patterns = {
            "__pycache__/",
            "%.mkv",
            "%.png",
            "%.pdf",
            "%.xlxs",
            "Games/",
            "Pictures/",
            "Wallpapers/",
            "Documents/",
            "Downloads/",
            "Music/",
            "Videos/",
          },
        },
        pickers = {
          find_files = {
            -- hidden = true, -- include dotfiles
          },
        },
        extensions = {
          fzf = {
            fuzzy = true, -- enable fuzzy matching
            override_generic_sorter = true, -- replace the generic sorter
            override_file_sorter = true, -- replace file sorter
            case_mode = "smart_case", -- or "ignore_case", "respect_case"
          },
        },
      }
      telescope.load_extension "fzf"
    end,
  },

  -- Neo-tree
  {
    "nvim-neo-tree/neo-tree.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons",
      "MunifTanjim/nui.nvim",
      "s1n7ax/nvim-window-picker",
    },
    config = function()
      require("neo-tree").setup {
        filesystem = {
          window = {
            mappings = {
              ["<cr>"] = "open_with_window_picker", -- Use enter to trigger window picker
            },
          },
          hijack_netrw_behavior = "open_default",
        },
        buffers = {
          window = {
            mappings = {
              ["<cr>"] = "open_with_window_picker",
            },
          },
        },
        window_picker = {
          enabled = true,
          picker = "default", -- also accepts "fzf" if you got telescope or fzf
          exclude = {
            filetype = { "neo-tree", "neo-tree-popup", "notify" },
            buftype = { "terminal", "quickfix", "nofile" },
          },
        },
      }
    end,
  },
}
