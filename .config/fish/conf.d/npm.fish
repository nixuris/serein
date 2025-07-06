# ~/.config/fish/conf.d/npm.fish

# NPM User-Wide Global Package Configuration
# This ensures global npm packages installed to ~/.local/bin are found.

set -gx NPM_GLOBAL_BIN "$HOME/.local/bin"

if not string match -q -- $NPM_GLOBAL_BIN $PATH
  set -gx PATH "$NPM_GLOBAL_BIN" $PATH
end
