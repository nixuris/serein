#!/bin/bash
# Hyprland Install Script

# 1. Update the system
echo "Updating system with paru -Syu..."
paru -Syu --noconfirm

# 2. Prompt for username (since we're running as root)
read -p "Enter the username for config installation: " USERNAME

# 3. Remove directories from the user's ~/.config
#    (Only do this if they exist—just to avoid error messages)
echo "Removing any existing configs in /home/$USERNAME/.config..."
rm -rf "/home/$USERNAME/.config/fish" "/home/$USERNAME/.config/ranger" "/home/$USERNAME/.config/alacritty" "/home/$USERNAME/.config/cava" "/home/$USERNAME/.config/swaync" "/home/$USERNAME/.config/fastfetch" "/home/$USERNAME/.config/hypr" "/home/$USERNAME/.config/nvim" "/home/$USERNAME/.config/rofi" "/home/$USERNAME/.config/waybar" "/home/$USERNAME/.config/swaylock" "/home/$USERNAME/.config/swappy" 
# 4. Copy all contents from 'home/.config' (inside this repo) to the user's ~/.config
#    Assuming we're already in the Hyprdots-arch directory that contains 'home/.config'
echo "Copying new .config files to /home/$USERNAME/.config..."
mkdir -p "/home/$USERNAME/.config"
cp -r .config/* "/home/$USERNAME/.config"

# 5. Fix ownership of the copied configs so they're owned by the user
chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.config"

# 6. Install the required Hyprland packages
echo "Installing Hyprland and related packages..."
paru -S --noconfirm --needed \
  swww swaylock grim slurp swappy wl-clipboard cliphist ueberzugpp libnotify yad playerctl swaync alacritty \
  waybar hyprland rofi-wayland imagemagick xdg-desktop-portal-hyprland xdg-desktop-portal-gtk jq bc cava \
  papirus-icon-theme catppuccin-gtk-theme-frappe nwg-look bibata-cursor-theme \
  ttf-jetbrains-mono-nerd noto-fonts noto-fonts-emoji noto-fonts-cjk \

echo "Your Hyprland environment should be good to go."

