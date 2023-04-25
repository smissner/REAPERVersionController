gfx.init("My GUI", 200, 100)
local hwnd = reaper.JS_Window_Create("My GUI", 0, 0, 0, 0,0)
reaper.JS_Window_SetPosition(hwnd, 100, 100,0,0)
reaper.JS_Window_SetSize(hwnd, 200, 100)
local button1 = {x = 50, y = 50, w = 80, h = 30, caption = "Button 1"}
local button2 = {x = 120, y = 50, w = 80, h = 30, caption = "Button 2"}

function drawButtons()
  gfx.setfont(1, "Arial", 20)
  gfx.setfont(2, "Arial", 16)
  gfx.setfont(3, "Arial", 18, "b")
  gfx.r = 0.5
  gfx.g = 0.5
  gfx.b = 0.5
  gfx.rect(button1.x, button1.y, button1.w, button1.h, true)
  gfx.rect(button2.x, button2.y, button2.w, button2.h, true)
  gfx.r = 1
  gfx.g = 1
  gfx.b = 1
  gfx.x = button1.x + button1.w/2 - gfx.measurestr(button1.caption)/2
  gfx.y = button1.y + button1.h/2 - gfx.texth/2
  gfx.drawstr(button1.caption)
  gfx.x = button2.x + button2.w/2 - gfx.measurestr(button2.caption)/2
  gfx.y = button2.y + button2.h/2 - gfx.texth/2
  gfx.drawstr(button2.caption)
end

function checkButtons(x, y)
  if x > button1.x and x < button1.x + button1.w and y > button1.y and y < button1.y + button1.h then
    reaper.ShowConsoleMsg("Button 1 clicked\n")
  elseif x > button2.x and x < button2.x + button2.w and y > button2.y and y < button2.y + button2.h then
    reaper.ShowConsoleMsg("Button 2 clicked\n")
  end
end

function main()
  drawButtons()
  if gfx.getchar() >= 0 then
    local x, y = gfx.mouse_x, gfx.mouse_y
    if gfx.mouse_cap == 1 then
      checkButtons(x, y)
    end
    gfx.update()
    reaper.defer(main)
  end
end

main()
