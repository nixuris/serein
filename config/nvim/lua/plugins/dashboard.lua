return {
  {
    "goolord/alpha-nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    event = "VimEnter",

    config = function()
      local alpha = require "alpha"
      local dashboard = require "alpha.themes.dashboard"

      -- Define Main Dashboard
      function OpenMainDashboard()
        dashboard.section.header.val = {
          "███████╗███████╗██████╗ ███████╗██╗███╗   ██╗",
          "██╔════╝██╔════╝██╔══██╗██╔════╝██║████╗  ██║",
          "███████╗█████╗  ██████╔╝█████╗  ██║██╔██╗ ██║",
          "╚════██║██╔══╝  ██╔══██╗██╔══╝  ██║██║╚██╗██║",
          "███████║███████╗██║  ██║███████╗██║██║ ╚████║",
          "╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝",
          "               Welcome back ",
        }

        dashboard.section.buttons.val = {
          dashboard.button("❖", "󱙖  Serein CLI Hub", ":lua OpenSereinDashboard()<CR>"),
          dashboard.button("❖", "  Git Repositories", ":OpenGitRepos <CR>"),
          dashboard.button("❖", "  Open File Manager (Ranger)", ":terminal ranger<CR>"),
          dashboard.button("❖", "󰈞  Find Files", ":Telescope find_files<CR>"),
          dashboard.button("❖", "  New File", ":ene <BAR> startinsert <CR>"),
          dashboard.button("❖", "󰱼  Grep Text", ":Telescope live_grep<CR>"),
          dashboard.button("❖", "  Recent Files", ":Telescope oldfiles<CR>"),
          dashboard.button("❖", "  Quit Neovim", ":qa<CR>"),
        }

        alpha.setup(dashboard.config)
        vim.cmd "AlphaRedraw"
        vim.schedule(function()
          vim.cmd "stopinsert | redraw!"
        end)
      end

      -- Define Serein Dashboard
      function OpenSereinDashboard()
        dashboard.section.header.val = {
          "Serein CLI Hub",
          "Manage your Hyprland system",
          " ",
        }

        dashboard.section.buttons.val = {
          dashboard.button("❖", "  Serein Package Manager", ":terminal serein pkg<CR>"),
          dashboard.button("❖", "󰚰  Update (Edge)", ":terminal serein update edge<CR>"),
          dashboard.button("❖", "󰚰  Update (Stable)", ":terminal serein update stable<CR>"),
          dashboard.button("❖", "󰑓  Rollback", ":terminal serein rollback<CR>"),
          dashboard.button("❖", "  Config Manager", ":terminal serein config<CR>"),
          dashboard.button("❖", "󰆴  Uninstall Serein", ":terminal serein uninstall<CR>"),
          dashboard.button("❖", "󰁯  Back", ":lua OpenMainDashboard()<CR>"),
        }

        alpha.setup(dashboard.config)
        vim.cmd "AlphaRedraw"
      end

      -- Initialize Main Dashboard
      OpenMainDashboard()

      -- Autocmds
      vim.api.nvim_create_autocmd("User", {
        pattern = "AlphaReady",
        callback = function()
          vim.opt.laststatus = 0
        end,
      })

      vim.api.nvim_create_autocmd("TermOpen", {
        pattern = { "*ranger*", "*serein*" },
        callback = function()
          vim.cmd "startinsert"
        end,
      })

      vim.api.nvim_create_autocmd("BufUnload", {
        callback = function()
          if vim.bo.filetype == "alpha" then
            vim.schedule(function()
              vim.opt.laststatus = 3
            end)
          end
        end,
      })

      vim.api.nvim_create_autocmd("TermClose", {
        pattern = { "*ranger*", "*serein*" },
        callback = function()
          vim.defer_fn(function()
            vim.cmd "Alpha"
          end, 50)
        end,
      })

      vim.keymap.set("n", "<leader>dd", "<cmd>Alpha<CR>", { desc = "Reopen [D]ash[D]oard" })
    end,
  },
}
