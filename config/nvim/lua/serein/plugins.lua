return {

-- Telescope with hidden files
  {
    'nvim-telescope/telescope.nvim',
    dependencies = {
      { 'nvim-telescope/telescope-fzf-native.nvim', build = 'make' },
    },
    config = function()
    local telescope = require 'telescope'
     telescope.setup({
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
          fuzzy = true,                    -- enable fuzzy matching
          override_generic_sorter = true,  -- replace the generic sorter
          override_file_sorter = true,     -- replace file sorter
          case_mode = "smart_case",        -- or "ignore_case", "respect_case"
        },
      },
    })
    telescope.load_extension('fzf')
      local builtin = require 'telescope.builtin'
      vim.keymap.set('n', '<leader>ff', builtin.find_files, { desc = '[F]ind [F]iles' })
      vim.keymap.set('n', '<leader>fg', builtin.live_grep, { desc = '[F]ind by [G]rep' })
      vim.keymap.set('n', '<leader>fb', builtin.buffers, { desc = '[F]ind [B]uffers' })
      vim.keymap.set('n', '<leader>fh', builtin.help_tags, { desc = '[F]ind [H]elp' })
    end,
  },

-- Neo-tree
  {
    'nvim-neo-tree/neo-tree.nvim',
    dependencies = {
      'nvim-lua/plenary.nvim',
      'nvim-tree/nvim-web-devicons',
      'MunifTanjim/nui.nvim',
      's1n7ax/nvim-window-picker',
    },
    config = function()
      vim.keymap.set('n', '<leader>e', '<cmd>Neotree toggle<CR>', { desc = '[E]xplorer Neo-tree' })
    require("neo-tree").setup({
      filesystem = {
        window = {
          mappings = {
            ["<cr>"] = "open_with_window_picker",  -- Use enter to trigger window picker
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
    })
    end,
  },
   
-- Theme
  {
    'nvim-lualine/lualine.nvim',
    dependencies = { 'nvim-tree/nvim-web-devicons' },
    config = function()
      require('lualine').setup {
	options = {
	  theme = 'auto',      -- Use 'tokyonight', 'gruvbox', etc., or 'auto'
	  icons_enabled = true,
	  section_separators = '',
	  component_separators = '|',
	  globalstatus = true, -- whole width
	},
	sections = {
	  lualine_a = { 'mode' },
          lualine_b = { 'branch', 'diff' },
          lualine_c = { 'filename', 'filetype' },
          lualine_x = { 'diagnostics', 'encoding', 'fileformat' },
          lualine_y = { 'progress' },
          lualine_z = { 'location' },
	},
      }
    end,
    },

    {
  'hrsh7th/nvim-cmp',
  dependencies = {
    'hrsh7th/cmp-buffer',       -- words from current buffer
    'hrsh7th/cmp-nvim-lsp',     -- LSP suggestions
    'L3MON4D3/LuaSnip',         -- optional: snippet engine
    'saadparwaiz1/cmp_luasnip', -- optional: LuaSnip integration
  },
  config = function()
    local cmp = require'cmp'

    cmp.setup({
      snippet = {
        expand = function(args)
          require('luasnip').lsp_expand(args.body)
        end,
      },
      mapping = cmp.mapping.preset.insert({
        ['<Tab>'] = cmp.mapping.confirm({ select = true }), -- press Tab to confirm
        ['<CR>']  = cmp.mapping.confirm({ select = true }), -- or Enter
        ['<C-Space>'] = cmp.mapping.complete(),             -- manual trigger if needed
      }),
      sources = cmp.config.sources({
        { name = 'nvim_lsp' },
        { name = 'buffer' },
      }),
    })
  end
}

}
