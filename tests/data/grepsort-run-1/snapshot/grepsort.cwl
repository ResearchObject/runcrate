class: Workflow
cwlVersion: v1.0

inputs:
  grepsort_in:
    type: File
    secondaryFiles:
      - "^.aux"
  reverse_sort:
    type: boolean
    default: false
outputs:
  grepsort_out:
    type: File
    outputSource: sorted/sort_out

steps:
  grep:
    in:
      grep_in: grepsort_in
    out: [grep_out]
    run: greptool.cwl
  sorted:
    in:
      sort_in: grep/grep_out
      reverse: reverse_sort
    out: [sort_out]
    run: sorttool.cwl
