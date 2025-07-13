vim.diagnostic.config {
  virtual_text = {
    prefix = "●", -- Could be '', '●', '◆'
    spacing = 2,
  },
  underline = true,
  update_in_insert = false,
  severity_sort = true,
  signs = {
    text = {
      [vim.diagnostic.severity.ERROR] = " ",
      [vim.diagnostic.severity.WARN] = " ",
      [vim.diagnostic.severity.HINT] = "󰌵 ",
      [vim.diagnostic.severity.INFO] = " ",
    },
  },
}
return {

  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason.nvim", -- LSP installer
      "williamboman/mason-lspconfig.nvim", -- bridge between Mason & lspconfig
      "hrsh7th/cmp-nvim-lsp", -- LSP completion source for nvim-cmp
      "folke/neodev.nvim", -- Lua dev for Neovim config itself
    },
    config = function()
      require("neodev").setup() -- Setup Neovim's Lua LSP

      local lspconfig = require "lspconfig"
      local mason = require "mason"
      local mason_lspconfig = require "mason-lspconfig"

      mason.setup()
      mason_lspconfig.setup {
        ensure_installed = { "pyright", "clangd", "lua_ls" },
      }

      local capabilities = require("cmp_nvim_lsp").default_capabilities()

      -- Define a global on_attach function
      local on_attach = function(_, bufnr)
        local opts = { buffer = bufnr, silent = true }
      end

      -- Python
      lspconfig.pyright.setup {
        capabilities = capabilities,
        on_attach = on_attach,
      }

      -- C++
      lspconfig.clangd.setup {
        capabilities = capabilities,
        on_attach = on_attach,
      }
    end,
  },

  {
    "folke/todo-comments.nvim",
    event = "VimEnter",
    dependencies = { "nvim-lua/plenary.nvim" },
    opts = { signs = false },
  },

  { -- Highlight, edit, and navigate code
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    main = "nvim-treesitter.configs", -- Sets main module to use for opts
    opts = {
      ensure_installed = {
        "bash",
        "c",
        "diff",
        "html",
        "lua",
        "luadoc",
        "markdown",
        "markdown_inline",
        "query",
        "vim",
        "vimdoc",
      },
      auto_install = true,
      highlight = {
        enable = true,
      },
      indent = {
        enable = true,
      },
    },
  },

  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-buffer", -- words from current buffer
      "hrsh7th/cmp-nvim-lsp", -- LSP suggestions
      "L3MON4D3/LuaSnip", -- optional: snippet engine
      "saadparwaiz1/cmp_luasnip", -- optional: LuaSnip integration
    },
    config = function()
      local cmp = require "cmp"

      cmp.setup {
        snippet = {
          expand = function(args)
            require("luasnip").lsp_expand(args.body)
          end,
        },
        mapping = cmp.mapping.preset.insert {
          ["<Tab>"] = cmp.mapping.confirm { select = true }, -- press Tab to confirm
          ["<CR>"] = cmp.mapping.confirm { select = true }, -- or Enter
          ["<C-Space>"] = cmp.mapping.complete(), -- manual trigger if needed
        },
        sources = cmp.config.sources {
          { name = "nvim_lsp" },
          { name = "buffer" },
        },
      }
    end,
  },

  { -- Autoformat
    "stevearc/conform.nvim",
    event = { "BufWritePre" },
    cmd = { "ConformInfo" },
    keys = {
      {
        "<leader>f",
        function()
          require("conform").format { async = true, lsp_format = "fallback" }
        end,
        mode = "",
        desc = "[F]ormat buffer",
      },
    },
    opts = {
      notify_on_error = false,
      format_on_save = function(bufnr)
        local disable_filetypes = { c = true, cpp = true }
        if disable_filetypes[vim.bo[bufnr].filetype] then
          return nil
        else
          return {
            timeout_ms = 500,
            lsp_format = "fallback",
          }
        end
      end,
      formatters_by_ft = {
        lua = { "stylua" },
      },
    },
  },

  "NMAC427/guess-indent.nvim",

  { -- Adds git related signs to the gutter, as well as utilities for managing changes
    "lewis6991/gitsigns.nvim",
    opts = {
      signs = {
        add = { text = "+" },
        change = { text = "~" },
        delete = { text = "_" },
        topdelete = { text = "‾" },
        changedelete = { text = "~" },
      },
    },
  },

  {
    "NvChad/nvim-colorizer.lua",
    event = "BufReadPre",
    config = function()
      require("colorizer").setup {
        filetypes = { "*" }, -- or limit to { "css", "html", "js", etc. }
        user_default_options = {
          mode = "virtualtext", -- ⬅️ the key setting you missed
          virtualtext = "󱓻",
          names = false,
          css = true,
          tailwind = true,
          rgb_fn = true,
          hsl_fn = true,
        },
      }
    end,
  },
}
