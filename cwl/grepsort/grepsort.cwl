class: Workflow
cwlVersion: v1.2

label: grepsort workflow
doc: a workflow that performs grep followed by sort
intent: ["http://example.org/intents/grep", "http://example.org/intents/sort"]

inputs:
  grepsort_in:
    label: grepsort input
    doc: input to the grepsort workflow
    type: File
    secondaryFiles:
      - "^.aux"
  reverse_sort:
    label: reverse_sort input
    type: boolean
    default: false
outputs:
  grepsort_out:
    type: File
    outputSource: sorted/sort_out

steps:
  grep:
    label: grep step
    doc: performs grep on the input
    in:
      grep_in: grepsort_in
    out: [grep_out]
    run: greptool.cwl
  sorted:
    doc: performs sort on the output of grep
    in:
      sort_in: grep/grep_out
      reverse: reverse_sort
    out: [sort_out]
    run: sorttool.cwl
