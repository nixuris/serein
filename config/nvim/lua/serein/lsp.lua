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
        vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
        vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
        vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
        vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
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
}
