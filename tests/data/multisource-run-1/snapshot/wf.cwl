cwlVersion: v1.2
class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}

inputs:
  in_file: File

outputs:
  out_file:
    type: File
    outputSource:
      cat/cat_out

steps:
  date:
    in:
      somefile: in_file
    out: [date_out]
    run: datetool.cwl
  isodate:
    in:
      somefile: in_file
    out: [date_out]
    run: isodatetool.cwl
  cat:
    in:
      files:
        source: [date/date_out, isodate/date_out]
        linkMerge: merge_flattened
    out:
      [cat_out]
    run: cattool.cwl
