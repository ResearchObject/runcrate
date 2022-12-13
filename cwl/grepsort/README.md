# grepsort

Example of workflow that uses `secondaryFiles` (see [File](https://www.commonwl.org/v1.0/CommandLineTool.html#File)). It runs a grep on the input `.txt` file, taking the patterns to search for from a file with the same name except for the extension, which has to be `.aux`. For instance, if the input file is `lines.txt`, the pattern file must be called `lines.aux`.
