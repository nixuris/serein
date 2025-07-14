_G.OpenGitRepoPickerWithTelescope = function()
  local actions = require "telescope.actions"
  local action_state = require "telescope.actions.state"

  -- Ensure this is a table
  local repos = {}

  -- Use io.popen to find git directories

  local handle = io.popen [[
  find $HOME -type d -name ".git" -prune \
  ! -path "$HOME/.*" \
  ! -path "$HOME/.*/**" \
  2>/dev/null
]]

  if handle then
    local result = handle:read "*a"
    handle:close()

    -- Split lines properly
    for line in string.gmatch(result, "[^\r\n]+") do
      local repo_path = line:gsub("/%.git$", "")
      table.insert(repos, repo_path)
    end
  end

  if #repos == 0 then
    vim.notify("No Git repositories found.", vim.log.levels.WARN)
    return
  end

  -- Telescope picker
  require("telescope.pickers")
    .new({}, {
      prompt_title = "Git Repositories",
      finder = require("telescope.finders").new_table {
        results = repos,
      },
      sorter = require("telescope.config").values.generic_sorter {},
      attach_mappings = function(prompt_bufnr)
        actions.select_default:replace(function()
          local selection = action_state.get_selected_entry()
          actions.close(prompt_bufnr)

          vim.cmd("cd " .. vim.fn.fnameescape(selection[1]))
          vim.cmd "terminal gitui"
          vim.schedule(function()
            vim.cmd "startinsert"
          end)

          vim.api.nvim_create_autocmd("TermClose", {
            once = true,
            callback = function()
              vim.cmd "Alpha"
            end,
          })

          -- Or just open terminal if you want
        end)
        return true
      end,
    })
    :find()
end

-- Register Vim command
vim.cmd [[ command! OpenGitRepos lua OpenGitRepoPickerWithTelescope() ]]
