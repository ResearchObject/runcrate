cwlVersion: v1.2
class: CommandLineTool
baseCommand: [date, "-I", "-r"]

inputs:
  somefile:
    type: File
    inputBinding:
      position: 1
outputs:
  date_out:
    type: File
    outputBinding:
      glob: isodate_out.txt
stdout: isodate_out.txt
