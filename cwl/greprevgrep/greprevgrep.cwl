class: Workflow
cwlVersion: v1.0

inputs:
  wf_in:
    type: File
  wf_pattern_file:
    type: File
outputs:
  wf_out:
    type: File
    outputSource: grep2/grep_out

steps:
  grep1:
    in:
      grep_in: wf_in
      pattern_file: wf_pattern_file
    out: [grep_out]
    run: greptool.cwl
  reverse:
    in:
      rev_in: grep1/grep_out
    out: [rev_out]
    run: revtool.cwl
  grep2:
    in:
      grep_in: reverse/rev_out
      pattern_file: wf_pattern_file
    out: [grep_out]
    run: greptool.cwl
