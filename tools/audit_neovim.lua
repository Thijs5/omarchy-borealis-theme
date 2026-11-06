local root=assert(vim.env.BOREALIS_THEME_DIR)
vim.opt.rtp:append(assert(vim.env.BOREALIS_AETHER_DIR))
local opts=dofile(root..'/neovim.lua')[1].opts
opts.plugins={all=true,auto=false}
require('aether').setup(opts)
local _,groups=require('aether.theme').setup()
local normal=vim.api.nvim_get_hl(0,{name='Normal',link=false})
local output={}
for name,_ in pairs(groups) do
  local h=vim.api.nvim_get_hl(0,{name=name,link=false})
  if h.fg then
    table.insert(output,{name=name,fg=string.format('#%06X',h.fg),bg=string.format('#%06X',h.bg or normal.bg),explicit_bg=h.bg~=nil})
  end
end
vim.fn.writefile({vim.json.encode(output)},assert(vim.env.BOREALIS_AUDIT_OUT))
vim.cmd('qa!')
