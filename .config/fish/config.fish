if status is-interactive
    ~/.config/hypr/scripts/sttt scanline --scanline-reverse true -d 0.5
    fastfetch
    export EDITOR="nvim"
    export VISUAL="nvim"
    fish_add_path .local/bin
    fish_add_path .cargo/bin

    alias xs="paru -S"
    alias xr="paru -Rns"
    alias xu="paru"

    alias gpu="__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia"
    alias e="nvim"
    alias vim="nvim"
    alias vi="nvim"
    alias se="sudo -E -s nvim"
end
