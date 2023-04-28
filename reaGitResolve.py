import sys
import os
sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')
import imgui_python
import json
import git
import reapy
#Gui Functions
def init(conflicts):
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
    global skipProj

    ctx = imgui_python.ImGui_CreateContext('Conflict Resolver')
    continueLoop = True
    conflict_states = {}
    if("REAPER_PROJECT" in conflicts[0]):
      conflicts.pop(0)
      skipProj = "1"
    conflict_list = conflicts
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
    global skipProj
    continueLoop = False
    # Show a message with the conflict names and chosen sides for resolution
    resolution = [key for key, value in conflict_states.items() if value == True]
    resolutionAnswers = []
    if(skipProj is not None):
      resolutionAnswers.append("1")
    for r in resolution:
      if('#1' in r):
        resolutionAnswers.append('0')
      else:
        resolutionAnswers.append('1')
    resolve(resolutionAnswers)
    

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

##############
conflictedFile = RPR_GetExtState("MergeConflict","FileName")
conflicts = RPR_GetExtState("MergeConflict","Conflicts")
conflicts = json.loads(conflicts)
path = RPR_GetExtState("MergeConflict","Path")
changelog = RPR_GetExtState("MergeConflict","Changelog")
changelog = changelog.splitlines()
def process_input_text(input_text: str,conflictSides) -> str:
    lines = input_text.split('\n')
    conflicts = []
    in_conflict = False
    half_conflict = False
    i = -1
    mnb = 0
    line = None
    while(i<len(lines)):
        line = lines[i]
        if "<<<<<<" in line:
            in_conflict = True
            conflicts.append(["", "", ""]) 
        elif ">>>>>>" in line:
            in_conflict = False
            for conflict in conflicts:
                conflict_text = conflict[0] + conflict[2]
                lines[i] = conflict[0 if conflictSides[mnb] == "0" else 2][:-2]
                mnb += 1
                l = i
                for j in range(len(conflict_text.split('\n')) + 1):
                    lines.pop(l - 1 - j)
                    i += -1
            conflicts = []
            half_conflict = False
           

        elif in_conflict:
            if "======" in line:
                conflicts[-1][1] = line
                half_conflict = True
            else:
                if(half_conflict):
                    conflicts[-1][2] += line + "\n"
                else:
                    conflicts[-1][0] += line + "\n"
        i += 1
    return "\n".join(lines)
def resolve(resolutionChoices):
  with open(conflictedFile, 'r') as input_file:
      input_text = input_file.read()
  with open(conflictedFile, 'w') as output_file:
      output_file.write(process_input_text(input_text,resolutionChoices))
  repo = git.Repo(path)
  repo.git.add(conflictedFile)
  message = reapy.get_user_inputs("Write a message for your merge resolution commit",["-m"])
  repo.git.commit("-m",message["-m"])
  reapy.open_project(conflictedFile)
  reapy.show_message_box('Conficts resolved')
  repo.git.clean('-xf')
conflictChoices = []
for i in range(len(conflicts)):
    cnflct = ""
    tag = conflicts[i][0][0:conflicts[i][0].index("\n")]
    tag = tag.replace(" ","")
    getKey = ""
    for l in changelog:
      if('key_=' in l and 'chunk' in l):
        keyloc = l.index('key_=')
        finder = l[keyloc + 6:]
        finder = finder.index('\'')
        key = l[keyloc + 6:keyloc+6+finder]
        if(key in tag):
          chunk = l.index('chunk')
          chunk = l[chunk:chunk + 7]
          if(not chunk[-1].isnumeric()):
            chunk.pop()
          cnflct = "At " + chunk + ":" + tag
          break
    cnflct = cnflct + tag
    conflictChoices.append(cnflct)
RPR_defer('init(conflictChoices)')
