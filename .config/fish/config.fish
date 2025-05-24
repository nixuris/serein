if status is-interactive
    ~/.config/hypr/scripts/sttt scanline --scanline-reverse true -d 0.5
    fastfetch
    export EDITOR="nvim"
    export VISUAL="nvim"
    fish_add_path .local/bin
    fish_add_path .cargo/bin

    alias xs="sudo pacman -S"
    alias xr="sudo pacman -Rns"
    alias xu="sudo pacman -Syu"


    alias e="nvim"
    alias se="sudo -E -s nvim"
end
