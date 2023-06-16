class: Workflow
cwlVersion: v1.0

inputs:
  revsort_in:
    type: File
  reverse_sort:
    type: boolean
    default: false
outputs:
  revsort_out:
    type: File
    outputSource: sorted/sort_out

steps:

  rev:
    in:
      rev_in: revsort_in
    out: [rev_out]
    run:
      class: CommandLineTool
      baseCommand: rev
      inputs:
        rev_in:
          type: File
          inputBinding: {}
      outputs:
        rev_out:
          type: File
          outputBinding:
            glob: rev_out.txt
      stdout: rev_out.txt

  sorted:
    in:
      sort_in: rev/rev_out
      reverse: reverse_sort
    out: [sort_out]
    run:
      class: CommandLineTool
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
