import reapy
import git

# Get the path of the current Reaper project
project = reapy.Project()
projectPath = project.path

# Check if the local repository exists
try:
    repo = git.Repo(projectPath)
except git.exc.InvalidGitRepositoryError:
    raise Exception(f"Error: Local repository not found at {projectPath}.")

# Get the current branch you're working in
currentBranch = repo.active_branch

# Check if the remote repository exists
if "origin" not in repo.remotes:
    raise Exception("Error: Remote repository not found.")

# Set the upstream of the branch if it doesn't exist in the remote yet
if not currentBranch.tracking_branch():
    remoteBranch = f"origin/{currentBranch.name}"
    currentBranch.set_tracking_branch(remoteBranch)

# Push to the remote branch
try:
    repo.git.push("-u", "origin", currentBranch.name)
except git.exc.GitCommandError as e:
    raise Exception(f"Error: Could not push to remote branch {currentBranch}: {e}")
