class: CommandLineTool
cwlVersion: v1.0

baseCommand: sort

inputs:
  reverse:
    type: boolean?
    inputBinding:
      position: 1
      prefix: "--reverse"
  outname:
    type: string
    inputBinding:
      position: 2
      prefix: "--output"
  sort_in:
    type: File
    inputBinding:
      position: 3
outputs:
  sort_out:
    type: File
    outputBinding:
      glob: "*sorted"
