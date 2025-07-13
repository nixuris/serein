return {

  {
    "MeanderingProgrammer/markdown.nvim",
    name = "render-markdown.nvim",
    ft = "markdown",
    config = function()
      require("render-markdown").setup {
        headings = { "Headline1", "Headline2", "Headline3" },
      }
    end,
  },
}
