return {
  { -- Nord colorscheme
    "arcticicestudio/nord-vim",
    priority = 1000, -- Make sure to load this before all the other start plugins.
    config = function()
      vim.cmd.colorscheme "nord"
      -- lua/serein/config/transparent.lua (or put in options.lua)
      vim.api.nvim_set_hl(0, "Normal", { fg = "#c0caf5", bg = "NONE" })
      -- vim.api.nvim_set_hl(0, "Normal", { bg = "none" })
      vim.api.nvim_set_hl(0, "NormalNC", { bg = "none" })
      vim.api.nvim_set_hl(0, "NormalFloat", { bg = "none" })
      vim.api.nvim_set_hl(0, "FloatBorder", { bg = "none" })
      vim.api.nvim_set_hl(0, "TelescopeNormal", { bg = "none" })
      vim.api.nvim_set_hl(0, "TelescopeBorder", { bg = "none" })
      vim.api.nvim_set_hl(0, "VertSplit", { bg = "none" })
      vim.api.nvim_set_hl(0, "StatusLine", { bg = "none" })
    end,
  },

  -- {
  --   "folke/tokyonight.nvim",
  --   priority = 1000,
  --   config = function()
  --     vim.cmd.colorscheme "tokyonight-night" -- or "storm", "moon", etc.
  --     vim.api.nvim_set_hl(0, "Normal", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "NormalNC", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "NormalFloat", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "FloatBorder", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "TelescopeNormal", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "TelescopeBorder", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "VertSplit", { bg = "none" })
  --     vim.api.nvim_set_hl(0, "StatusLine", { bg = "none" })
  --   end,
  -- },
}
