function fish_prompt
	printf '%s' (set_color -o 4a4b52) "
" (set_color normal) (set_color -o 8ab4f8) (set_color -b 4a4b52) "  " (set_color normal) (set_color -o 8ab4f8) (set_color -b 4a4b52) (prompt_pwd) (set_color normal) (set_color -o 4a4b52) "" (set_color normal) (set_color -o 8ab4f8) " ❯ "
end
