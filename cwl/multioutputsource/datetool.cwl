cwlVersion: v1.2
class: CommandLineTool
baseCommand: [date, "-r"]

inputs:
  somefile:
    type: File
    inputBinding:
      position: 1
outputs:
  date_out:
    type: File
    outputBinding:
      glob: date_out.txt
stdout: date_out.txt
