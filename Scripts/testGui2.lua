-- NoIndex: true

--[[
    Lokasenna_GUI example

    - General demonstration
  - Tabs and layer sets
    - Subwindows
  - Accessing elements' parameters

]]--

-- The Core library must be loaded prior to anything else

local lib_path = reaper.GetExtState("Lokasenna_GUI", "lib_path_v2")
if not lib_path or lib_path == "" then
    reaper.MB("Couldn't load the Lokasenna_GUI library. Please run 'Script: Set Lokasenna_GUI v2 library path.lua' in your Action List.", "Whoops!", 0)
    return
end
loadfile(lib_path .. "Core.lua")()

GUI.req("Classes/Class - Label.lua")()
GUI.req("Classes/Class - Knob.lua")()
GUI.req("Classes/Class - Tabs.lua")()
GUI.req("Classes/Class - Slider.lua")()
GUI.req("Classes/Class - Button.lua")()
GUI.req("Classes/Class - Menubox.lua")()
GUI.req("Classes/Class - Textbox.lua")()
GUI.req("Classes/Class - Frame.lua")()
GUI.req("Classes/Class - Options.lua")()
GUI.req("Classes/Class - Window.lua")()

-- If any of the requested libraries weren't found, abort the script.
if missing_lib then return 0 end




------------------------------------
-------- Functions -----------------
------------------------------------


local function fade_lbl()

   -- Fade out the label
    if GUI.elms.my_lbl.z == 3 then
        GUI.elms.my_lbl:fade(1, 3, 6)

    -- Bring it back
    else
        GUI.elms.my_lbl:fade(1, 3, 6, -3)
    end

end


local function btn_click()

    -- Open the Window element
  GUI.elms.wnd_test:open()

end


local function wnd_OK()

    -- Close the Window element
    GUI.elms.wnd_test:close()

end


-- Returns a list of every element on the specified z-layer and
-- a second list of each element's values
local function get_values_for_tab(tab_num)

  -- The '+ 2' here is just to translate from a tab number to its'
  -- associated z layer. More complicated scripts would have to
  -- actually access GUI.elms.tabs.z_sets[tab_num] and iterate over
  -- the table's contents (see the call to GUI.elms.tabs:update_sets
  -- below)
    local strs_v, strs_val = {}, {}
  for k, v in pairs(GUI.elms_list[tab_num + 2]) do

        strs_v[#strs_v + 1] = v
    local val = GUI.Val(v)
    if type(val) == "table" then
      local strs = {}
      for k, v in pairs(val) do
                local str = tostring(v)

                -- For conciseness, reduce boolean values to T/F
        if str == "true" then
                    str = "T"
                elseif str == "false" then
                    str = "F"
                end
                strs[#strs + 1] = str
      end
      val = table.concat(strs, ", ")
    end

        -- Limit the length of the returned string so it doesn't
        -- spill out past the edge of the window
    strs_val[#strs_val + 1] = string.len(tostring(val)) <= 35
                                and tostring(val)
                                or  string.sub(val, 1, 32) .. "..."

  end

    return strs_v, strs_val

end




------------------------------------
-------- Window settings -----------
------------------------------------


GUI.name = "New Window"
GUI.x, GUI.y, GUI.w, GUI.h = 0, 0, 1024, 1024
GUI.anchor, GUI.corner = "mouse", "C"


--[[

  Button    z,   x,   y,   w,   h, caption, func[, ...]
  Checklist  z,   x,   y,   w,   h, caption, opts[, dir, pad]
  Frame    z,   x,   y,   w,   h[, shadow, fill, color, round]
  Knob    z,   x,   y,   w,   caption, min, max, default[, inc, vals]
  Label    z,   x,   y,    caption[, shadow, font, color, bg]
  Menubox    z,   x,   y,   w,   h, caption, opts
  Radio    z,   x,   y,   w,   h, caption, opts[, dir, pad]
  Slider    z,   x,   y,   w,   caption, min, max, defaults[, inc, dir]
  Tabs    z,   x,   y,     tab_w, tab_h, opts[, pad]
  Textbox    z,   x,   y,   w,   h[, caption, pad]
    Window      z,  x,  y,  w,  h,  caption, z_set[, center]

]]--


-- Elements can be created in any order you want. I find it easiest to organize them
-- by tab, or by what part of the script they're involved in.




------------------------------------
-------- General elements ----------
------------------------------------


GUI.New("tab_bg",  "Frame",    2, 0, 0, 448, 20, false, true, "elm_bg", 0)
GUI.New("my_btn",   "Button",     1, 168, 28, 96, 20, "Go!", btn_click)
GUI.New("btn_frm",  "Frame",    1, 0, 56, GUI.w, 4, true, true)







GUI.New("my_chk",   "Checklist",   5, 32, 96, 312, 244, "Checklist:", "Alice,Bob,Charlie,Denise,asfgewhgrsef,sdgsffsdf,sdfasdwf,Edward,Francine,as,f,fsfs,ssfs,fsss,fasafs,fsg,gr,eg,reg,fasfg,hh,gfds,bfs", "v", 4)





------------------------------------
-------- Subwindow and -------------
-------- its elements  -------------
------------------------------------


GUI.New("wnd_test", "Window", 10, 0, 0, 1024, 244, "Dialog Box", {9, 10})
GUI.New("lbl_elms", "Label", 9, 16, 16, "", false, 4)
GUI.New("lbl_vals", "Label", 9, 96, 16, "", false, 4, nil, elm_bg)
GUI.New("btn_close", "Button", 9, 0, 184, 48, 24, "OK", wnd_OK)

-- We want these elements out of the way until the window is opened
GUI.elms_hide[9] = true
GUI.elms_hide[10] = true


-- :onopen is a hook provided by the Window class. This function will be run
-- every time the window opens.
function GUI.elms.wnd_test:onopen()

    -- :adjustelm places the element's specified x,y coordinates relative to
    -- the Window. i.e. creating an element at 0,0 and adjusting it will put
    -- the element in the Window's top-left corner.
    self:adjustelm(GUI.elms.btn_close)

    -- Buttons look nice when they're centered.
    GUI.elms.btn_close.x, _ = GUI.center(GUI.elms.btn_close, self)

    self:adjustelm(GUI.elms.lbl_elms)
    self:adjustelm(GUI.elms.lbl_vals)

    -- Set the Window's title
  local tab_num = GUI.Val("tabs")
    self.caption = "Element values for Tab " .. tab_num

    -- This Window provides a readout of the values for every element
    -- on the current tab.
    local strs_v, strs_val = get_values_for_tab(tab_num)

    GUI.Val("lbl_elms", table.concat(strs_v, "\n"))
    GUI.Val("lbl_vals", table.concat(strs_val, "\n"))

end




------------------------------------
-------- Main functions ------------
------------------------------------


-- This will be run on every update loop of the GUI script; anything you would put
-- inside a reaper.defer() loop should go here. (The function name doesn't matter)
local function Main()

  -- Prevent the user from resizing the window
  if GUI.resized then

    -- If the window's size has been changed, reopen it
    -- at the current position with the size we specified
    local __,x,y,w,h = gfx.dock(-1,0,0,0,0)
    gfx.quit()
    gfx.init(GUI.name, GUI.w, GUI.h, 0, x, y)
    GUI.redraw_z[0] = true
  end

end


-- Open the script window and initialize a few things
GUI.Init()

-- Tell the GUI library to run Main on each update loop
-- Individual elements are updated first, then GUI.func is run, then the GUI is redrawn
GUI.func = Main

-- How often (in seconds) to run GUI.func. 0 = every loop.
GUI.freq = 0


-- Start the main loop
GUI.Main()
