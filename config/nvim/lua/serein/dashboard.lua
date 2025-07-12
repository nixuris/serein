local alpha = require "alpha"
local dashboard = require "alpha.themes.dashboard"

-- 🧠 Header Art
dashboard.section.header.val = {
  "███████╗███████╗██████╗ ███████╗██╗███╗   ██╗",
  "██╔════╝██╔════╝██╔══██╗██╔════╝██║████╗  ██║",
  "███████╗█████╗  ██████╔╝█████╗  ██║██╔██╗ ██║",
  "╚════██║██╔══╝  ██╔══██╗██╔══╝  ██║██║╚██╗██║",
  "███████║███████╗██║  ██║███████╗██║██║ ╚████║",
  "╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝",
  "               Welcome back ",
}

-- 🎛️ Buttons
dashboard.section.buttons.val = {
  dashboard.button("n", "  New file", ":ene <BAR> startinsert <CR>"),
  dashboard.button("f", "󰈞  Find file", ":Telescope find_files<CR>"),
  dashboard.button("r", "  Recent files", ":Telescope oldfiles<CR>"),
  dashboard.button("g", "󰱼  Grep text", ":Telescope live_grep<CR>"),
  dashboard.button("s", "  Restore session", ":lua require('persistence').load()<CR>"),
  dashboard.button("q", "  Quit Neovim", ":qa<CR>"),
}

-- 🐾 Footer Info
dashboard.section.footer.val = function()
  local stats = require("lazy").stats()
  return "󰚩  " .. stats.loaded .. " plugins loaded in " .. (math.floor(stats.startuptime * 100) / 100) .. "ms"
end

dashboard.section.footer.opts.hl = "Comment"
dashboard.section.header.opts.hl = "Function"
dashboard.section.buttons.opts.hl = "Keyword"

-- 🧼 Hide tabline/statusline on dashboard
vim.api.nvim_create_autocmd("User", {
  pattern = "AlphaReady",
  callback = function()
    vim.cmd [[ set laststatus=0 | set showtabline=0 ]]
  end,
})

vim.api.nvim_create_autocmd("BufUnload", {
  buffer = 0,
  callback = function()
    vim.cmd [[ set laststatus=2 | set showtabline=2 ]]
  end,
})
vim.keymap.set("n", "<leader>dd", "<cmd>Alpha<CR>", { desc = "Reopen [D]ash[D]oard" })
alpha.setup(dashboard.config)
