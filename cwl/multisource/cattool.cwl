cwlVersion: v1.2
class: CommandLineTool
baseCommand: [cat]

inputs:
  files:
    type: File[]
    inputBinding:
      position: 1
outputs:
  cat_out:
    type: File
    outputBinding:
      glob: cat_out.txt
stdout: cat_out.txt
