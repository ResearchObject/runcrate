class: CommandLineTool
cwlVersion: v1.2

label: grep tool
doc: a tool wrapper for the grep command
intent: ["http://example.org/intents/grep"]

hints:
  - class: ResourceRequirement
    ramMin: 64

baseCommand: ["bash", "-c"]

inputs:
  grep_in:
    label: grep input
    doc: input file for the grep tool
    type: File
    secondaryFiles:
      - "^.aux"
outputs:
  grep_out:
    label: grep output
    type: File
    outputBinding:
      glob: grep_out.txt

arguments:
  - position: 0
    valueFrom: |
      grep -f $(inputs.grep_in.dirname)/$(inputs.grep_in.nameroot).aux $(inputs.grep_in.path) >grep_out.txt
