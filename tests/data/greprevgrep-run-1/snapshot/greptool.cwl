class: CommandLineTool
cwlVersion: v1.0

baseCommand: grep

inputs:
  pattern_file:
    type: File
    inputBinding:
      prefix: -f
  grep_in:
    type: File
    inputBinding:
      position: 2
outputs:
  grep_out:
    type: stdout
stdout: grep_out.txt
