import reapy
import git
project = reapy.Project()
try:
  repo = git.Repo(project.path)
  reapy.print("Git repository already instantiated")
except:
  repo = git.Repo.init(project.path)
  repo.git.add(project.name)
  for track in project.tracks:
    for item in track.items:
      for take in item.takes:
        repo.git.add(take.source.filename)
  repo.git.commit("-m","Initial commit")
  reapy.print("Repository created")
