from Themis import Themis
def main():
  # Debug
  themis = Themis("s5230837","Bobit0Drog@231")
  year = themis.getYear(2023, 2024)
  
  # pf = year.getCourse("Programming Fundamentals (for CS)")
  # pf = pf.getExerciseGroups()
  # print(pf[1].exercises[1].submit("main.c")) # <- this should throw error
  
  # no_folders = year.getCourse("Computer Architecture")
  # ca_ass = no_folders.getExerciseGroups()
  ai = year.getCourse("Imperative Programming (for AI)")
  ai = ai.getExerciseGroups()
  print(ai[7].exercises[1].submit("suitcase.py", silent=False))
  
  ads = year.getCourse("Algorithms and Data Structures for CS")
  ads = ads.getExerciseGroups()
  # print(ads[0].folders)
  print(ads[0].folders[5].folders[0].exercises[0].submit(["texteditor.c", "texteditor.h"], silent=False))
  # for ass in ca_ass:
  #   print(ass.exercises)

if __name__ == "__main__":
  main()