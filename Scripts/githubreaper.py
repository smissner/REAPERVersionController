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

# This script allows remote collaboration for Reaper projects via GitHub

# Things you need:
# 1. Update your system to latest software (usually good to do)
# 2. Update Python (this script uses 3.11.3)
# 3. Update Reaper (currently using v6.78 macOS-arm64)
# 4. Update pip (Python package manager) using 'pip3 install --upgrade pip' (currently using 23.0.1)
# 5. Install required modules below using 'pip3 install <required module>'
  # - 'pip3 install GitPython'
  # - 'pip3 install python-reapy'
# 6. Install ReaPack: https://reapack.com/ (currently using v1.2.4.3 macOS arm64)
# 7. Install ReaImGui through ReaPack: https://github.com/cfillion/reaimgui (currently using 0.8.5)
# 8. You'll need to configure your own SSH key to write to your repo
  # See: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
  # See: https://docs.github.com/en/get-started/getting-started-with-git/managing-remote-repositories#switching-remote-urls-from-https-to-ssh
# 9. Add this Python script to Reaper using the 'Actions' menu
# 10. Replace project and repo details below with your repo and project
# 11. Run the script (inside reaper 'Actions' menu with the project open--don't use terminal)

import sys
import os
sys.path.append(RPR_GetResourcePath() + '/Scripts/ReaTeam Extensions/API')

import imgui_python
import reapy
import git

# Find the Reaper project inside this repo
# Replace this with the reaper project name you wish to use
project_name = 'githubreaper'
project = reapy.Project(project_name)
# Find the Git repo inside the working directory (same as project path)
repo = git.Repo(project.path)
# Get the SSH key info (setup on your system)
git_ssh_identity_file = os.path.expanduser('~/.ssh/id_ed25519')
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
# Get the origin
origin = repo.remotes.origin
# Switch to url of the repo you wish to use (has to be in SSH format like this--no https)
repo_url = 'git@github.com:emurray2/reapergithub.git'
origin.set_url(repo_url)

# Keep track of branches
local_branch_names = []
remote_branch_names = []

def init():
  updateBranchList()

  global ctx
  global current_local_branch
  global current_remote_branch
  global commit_message
  global new_branch_name
  ctx = imgui_python.ImGui_CreateContext('GitHub Reaper')

  current_local_branch = [repo.active_branch]
  current_remote_branch = [remote_branch_names[0]]

  commit_message = ['']
  new_branch_name = ['']

  loop()

# Render cycle for drop-down menu
def renderDropdown(name: str, binding, branches):
  if imgui_python.ImGui_BeginCombo(ctx, name, binding[0]):
    for branch in branches:
      is_selected = (binding[0] == branch)
      (begin_select, is_selected) = imgui_python.ImGui_Selectable(ctx, branch, is_selected)
      if begin_select:
        # Set the menu binding
        binding[0] = branch
        # Checkout the selected branch
        checkout(branch)
        # Open the project for the selected branch
        reapy.open_project(project.path + '/'+project_name+'.rpp')
      if is_selected:
        imgui_python.ImGui_SetItemDefaultFocus(ctx)
    imgui_python.ImGui_EndCombo(ctx)

# Render cycle for text input
def renderTextInput(name: str, binding):
  (show_textinput, message) = imgui_python.ImGui_InputText(ctx, name, binding[0])
  if show_textinput:
    binding[0] = message

def loop():
  imgui_python.ImGui_SetNextWindowSize(ctx, 700, 500, imgui_python.ImGui_Cond_FirstUseEver())
  visible, open = imgui_python.ImGui_Begin(ctx, 'GitHub Reaper', True)

  if visible:
    if imgui_python.ImGui_Button(ctx, 'Fetch Origin'):
      updateBranchList()
      reapy.show_message_box('Successfully fetched origin.','Fetch Success')

    renderDropdown('Local Branches', current_local_branch, local_branch_names)
    renderDropdown('Remote Branches', current_remote_branch, remote_branch_names)

    if imgui_python.ImGui_Button(ctx, 'Delete Selected Local Branch'):
      deleteSelectedBranch('local')
    if imgui_python.ImGui_Button(ctx, 'Delete Selected Remote Branch'):
      deleteSelectedBranch('remote')

    renderTextInput('Commit message',commit_message)
    renderTextInput('New branch name',new_branch_name)

    if imgui_python.ImGui_Button(ctx, 'Create Branch'):
      createBranch()

    if imgui_python.ImGui_Button(ctx, 'Push Changes'):
      pushChanges()

    imgui_python.ImGui_End(ctx)

  if open:
    RPR_defer('loop()')

def fetchOrigin():
  with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    origin.update()
    origin.fetch()

def checkout(branch: str):
  try:
    # This might fail if the branch is remote
    repo.heads[branch].checkout()
  except:
    # Branch is remote, add it to local
    ref = origin.refs[str.split(branch,'/')[1]]
    if ref.remote_head not in repo.heads:
      new_head = repo.create_head(ref.remote_head, ref)
      new_head.set_tracking_branch(ref)
      local_branch_names.append(new_head.name)
    repo.heads[ref.remote_head].checkout()
    current_local_branch[0] = str.split(branch,'/')[1]

def createBranch():
  if new_branch_name[0] == '':
    reapy.show_message_box('Please enter a name for the new branch.', 'Branch Name Empty')
  else:
    branch_name = new_branch_name[0]
    remote_name = "origin"
    # Get origin remote
    origin = repo.remote(remote_name)
    # Create new branch
    repo.head.reference = repo.create_head(branch_name)
    # Create new remote ref and set it to track.
    rem_ref = git.RemoteReference(repo, f"refs/remotes/{remote_name}/{branch_name}")
    repo.head.reference.set_tracking_branch(rem_ref)
    local_branch_names.append(new_branch_name[0])
    reapy.show_message_box('Branch created: '+new_branch_name[0],'Branch Created')

def deleteSelectedBranch(type: str):
  # Checkout default branch to avoid errors
  repo.heads.main.checkout()
  if type == 'local':
    # Store menu binding for deletion
    deleting_head = current_local_branch[0]
    repo.delete_head(deleting_head)
    local_branch_names.remove(deleting_head)
    reapy.show_message_box('Local branch deleted: '+deleting_head,'Branch Deleted')
  if type == 'remote':
    # Store menu binding for deletion
    deleting_branch = str.split(current_remote_branch[0],'/')[1]
    # Set menu binding to default branch
    current_remote_branch[0] = origin.refs.main.name

    # Delete local branches if existent before remote (to avoid warnings)
    if deleting_branch in repo.heads:
      repo.delete_head(deleting_branch)
      local_branch_names.remove(deleting_branch)
    with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
      origin.push(refspec=(":%s" % deleting_branch))
      reapy.show_message_box('Remote branch deleted: '+deleting_branch,'Branch Deleted')
  # Store name for success message
  name = current_local_branch[0]
  # Set menu binding to default branch
  current_local_branch[0] = repo.active_branch
  # Open the project for default branch
  reapy.open_project(project.path + '/'+project_name+'.rpp')
  updateBranchList()

def pushChanges():
  # Find changed files
  files = repo.git.diff(None, name_only=True)
  with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    # Check if commit message is empty and branch name is empty (otherwise user is creating a branch and not a commit)
    if commit_message[0] == '' and new_branch_name[0] == '':
      reapy.show_message_box('Please enter text for commit message', 'Commit Failed')
    # Branch is being created, check if user filled in the name and create it
    elif new_branch_name[0] != '' and new_branch_name[0] in local_branch_names:
      origin.push(new_branch_name[0])
      reapy.show_message_box('Branch added to upstream: '+new_branch_name[0],'Branch Upstream')
      new_branch_name[0] = ''
      updateBranchList()
    # If no files were changed, we can't do anything
    elif len(files) == 0:
      reapy.show_message_box('No files have changed.', 'Commit Failed')
    # Some files were changed as in a typical git commit, let's add those changes to remote
    elif new_branch_name[0] == '' and commit_message != '':
      for f in files.split('\n'):
        repo.git.add(f)
      repo.index.commit(commit_message[0])
      origin.push()
      reapy.show_message_box('Commit successful: '+commit_message[0],'Commit Success')
      updateBranchList()

def updateBranchList():
  fetchOrigin()

  # Reset branch list
  local_branch_names.clear()
  remote_branch_names.clear()

  # Get local branch list
  for head in repo.heads:
    if head.name != 'HEAD':
      local_branch_names.append(head.name)

  # Get remote branch list
  for ref in origin.refs:
    if ref.name != origin.name+'/'+'HEAD':
      remote_branch_names.append(ref.name)

RPR_defer('init()')
