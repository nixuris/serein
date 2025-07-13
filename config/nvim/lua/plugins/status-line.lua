return {

  -- Statusline
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup {
        options = {
          theme = "auto", -- Use 'tokyonight', 'gruvbox', etc., or 'auto'
          icons_enabled = true,
          section_separators = "",
          component_separators = "|",
          globalstatus = true, -- whole width
        },
        sections = {
          lualine_a = { "mode" },
          lualine_b = { "branch", "diff" },
          lualine_c = { "filename", "filetype" },
          lualine_x = { "diagnostics", "encoding" },
          lualine_y = { "progress" },
          lualine_z = { "location" },
        },
      }
    end,
  },
}
