'''
Copyright (c) 2023 Evan Murray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# This script contains a GUI for interacting with merge conflicts
import sys
import os

sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')
import imgui_python
import reapy
import git

def init():
    global ctx
    # A dictionary containing the conflict states for each row
    global conflict_states
    # List of conflicts
    global conflict_list
    # Reference to last button (id) clicked
    global last_button
    # Reference to last row (conflict) clicked
    global last_conflict
    global continueLoop

    ctx = imgui_python.ImGui_CreateContext('Conflict Resolver')
    continueLoop = True
    conflict_states = {}
    conflict_list = ['help']*32
    last_button = ['']
    last_conflict = ['']
    continueLoop = True
    loop()

def loop():
    imgui_python.ImGui_SetNextWindowSize(ctx, 700, 500, imgui_python.ImGui_Cond_FirstUseEver())
    visible, open = imgui_python.ImGui_Begin(ctx, 'Conflict Resolver', True)
    global continueLoop
    if visible:
        createConflictTable(conflict_list)
        createResolveButton()
        imgui_python.ImGui_End(ctx)
    if open and continueLoop:
        RPR_defer('loop()')

def createResolveButton():
    if imgui_python.ImGui_Button(ctx, 'Finish Resolve'):
        finishResolve()

def finishResolve():
    global continueLoop
    continueLoop = False
    # Show a message with the conflict names and chosen sides for resolution
    resolution = ", ".join(key for key, value in conflict_states.items() if value == True)
    reapy.show_message_box(resolution, 'Conflict Resolution:')

def createConflictTable(conflicts):
    num_columns = 3

    imgui_python.ImGui_BeginTable(ctx, 'Conflict Table', num_columns)

    # Create the table header
    imgui_python.ImGui_TableSetupColumn(ctx, '')
    imgui_python.ImGui_TableSetupColumn(ctx, 'Side #1')
    imgui_python.ImGui_TableSetupColumn(ctx, 'Side #2')
    imgui_python.ImGui_TableHeadersRow(ctx)

    # Create rows with each conflict name and the corresponding buttons for each side
    addConflicts(conflicts, num_columns-1)

    imgui_python.ImGui_EndTable(ctx)

def addConflicts(conflicts, num_buttons: int):
    # Render (loop through) each row
    for row in range(0, len(conflicts)):
        conflict_name = conflicts[row]
        imgui_python.ImGui_TableNextColumn(ctx)
        imgui_python.ImGui_Text(ctx, conflict_name)
        addConflictButtons(conflict_name, row, num_buttons)

def addConflictButtons(conflict_name: str, row_number: int, num_buttons: int):
    # Loop through the buttons in this row
    for i in range(0, num_buttons):
        imgui_python.ImGui_TableNextColumn(ctx)

        button_id = str(conflict_name) + ' ' + 'Side #' + str(i+1)

        # Create a dictionary for the row state if it doesn't exist
        if button_id not in conflict_states:
            # Set all 'Side #1' buttons on by default
            conflict_states[button_id] = True if i == 0 else False

        # If this button is clicked, do the following:
        if imgui_python.ImGui_RadioButton(ctx, '##radio_table_' + str(button_id), conflict_states[button_id]):
            # Set its state to True (on)
            conflict_states[button_id] = True
            # Store this state for later usage
            last_button[0] = button_id
            last_conflict[0] = conflict_name
        # Deactivate the other buttons in this row
        if last_conflict[0] == conflict_name and button_id != last_button[0]:
            conflict_states[button_id] = False

RPR_defer('init()')
