class: CommandLineTool
cwlVersion: v1.2

requirements:
  - class: ResourceRequirement
    ramMin: 16

baseCommand: sort

inputs:
  reverse:
    type: boolean
    inputBinding:
      position: 1
      prefix: "--reverse"
  sort_in:
    type: File
    inputBinding:
      position: 2
outputs:
  sort_out:
    type: File
    outputBinding:
      glob: sort_out.txt
stdout: sort_out.txt
