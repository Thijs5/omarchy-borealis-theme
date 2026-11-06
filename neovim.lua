return {
  {
    "omacom/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg = "#140F1F",
        dark_bg = "#0D0A16",
        darker_bg = "#08060F",
        lighter_bg = "#2A2340",

        fg = "#DFEDE5",
        dark_fg = "#9DBCB1",
        light_fg = "#ECF5EF",
        bright_fg = "#FBFFFC",
        muted = "#9C96B2",

        red = "#E56D87",
        yellow = "#C5D98A",
        orange = "#C4906B",
        green = "#59C98D",
        cyan = "#3FA894",
        blue = "#8194C8",
        magenta = "#BE80D0",
        brown = "#B7947B",

        bright_red = "#F08098",
        bright_yellow = "#DDEDA6",
        bright_green = "#8FE7AB",
        bright_cyan = "#6FD9C4",
        bright_blue = "#A2B4E3",
        bright_magenta = "#D08FE0",

        accent = "#6FD9C4",
        cursor = "#FBFFFC",
        foreground = "#DFEDE5",
        background = "#140F1F",
        selection = "#29483F",
        selection_foreground = "#FBFFFC",
        selection_background = "#29483F",
      },
      on_highlights = function(h, c)
        -- Aether uses muted as both text and a filled badge/menu background.
        -- Separate selected fills and resolve low-contrast explicit text pairs.
        h.Visual = { fg = c.bright_fg, bg = c.selection }
        h.VisualNOS = { fg = c.bright_fg, bg = c.selection }
        h.PmenuSel = { fg = c.bright_fg, bg = c.selection }
        h.PmenuMatchSel = { fg = c.bright_cyan, bg = c.selection }
        h.BlinkCmpMenuSelection = { fg = c.bright_fg, bg = c.selection }
        h["@tag.delimiter.tsx"] = { fg = c.blue }
        local function lum(hex)
          if type(hex) ~= "string" or not hex:match("^#%x%x%x%x%x%x$") then return nil end
          local channels = {}
          for i = 2, 6, 2 do
            local v = tonumber(hex:sub(i, i + 1), 16) / 255
            channels[#channels + 1] = v <= 0.04045 and v / 12.92 or ((v + 0.055) / 1.055) ^ 2.4
          end
          return channels[1] * 0.2126 + channels[2] * 0.7152 + channels[3] * 0.0722
        end
        local function ratio(a, b)
          local x, y = lum(a), lum(b)
          if not x or not y then return nil end
          return (math.max(x, y) + 0.05) / (math.min(x, y) + 0.05)
        end
        for _, style in pairs(h) do
          if type(style) == "table" and style.fg and style.bg then
            local current = ratio(style.fg, style.bg)
            if current and current < 4.5 then
              for _, candidate in ipairs({ c.fg, c.bg, c.bright_fg, "#000000" }) do
                if ratio(candidate, style.bg) >= 4.5 then style.fg = candidate; break end
              end
            end
          end
        end
      end,
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
