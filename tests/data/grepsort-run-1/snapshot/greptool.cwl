class: CommandLineTool
cwlVersion: v1.0

baseCommand: ["bash", "-c"]

inputs:
  grep_in:
    type: File
    secondaryFiles:
      - "^.aux"
outputs:
  grep_out:
    type: File
    outputBinding:
      glob: grep_out.txt

arguments:
  - position: 0
    valueFrom: |
      grep -f $(inputs.grep_in.dirname)/$(inputs.grep_in.nameroot).aux $(inputs.grep_in.path) >grep_out.txt
