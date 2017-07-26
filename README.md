# WDL Cell Ranger
Cell Ranger is the 10x single-cell software package. It runs pipelines using a tool called "martian". Martian
is closed source and the pipelines it runs are relatively hard to modify, so it's currently not a great
candidate for use in the HCA DCP.

However, most of the actual 10x analysis code outside of martian is python scripts and open source tools. So,
it would be helpful to make use of that without having to accept the current constraints of martian. Ideally,
the 10x pipelines run by the HCA DCP could easily incorporate modules from Cell Ranger and modules from
third parties, depending on what the community decides works best.

This is a _very_ rough draft of some ideas around how to do that. It replaces the martian parsing functionality
with a little python code that can read martian pipeline and stage definitions. It exposes martian stages via
a simple command-line interface, so you can do things like

```
martian stage run <stage_name> <stage_parameters>
```

instead of the higher-level `cellranger` commands. These commands can be run with something like WDL+Cromwell,
which replaces the martian orchestration functionality.

It's possible to run the first few stages of `cellranger mkfastq` with what's here:

1. Create the docker image that Cromwell with use
  * Download the cellranger-2.0.0.tar.gz tarball from 10x and bcl2fastq from Illumina, and put them
     adjacent to the Dockerfile.
  * Run `docker build -t 10x_hca_wdl <path_to_local_repo>` 
2. Get the input data.
  * Download the "tiny" bcl and samplesheet from 10x. 
  * Update the wdls/tiny\_make\_fastq.json file so the paths point to your local run path and samplesheet.
3. Run cromwell: `java -jar cromwell.jar run wdls/make_fastq.wdl -i wdls/tiny_make_fastqs_inputs.json`

This will run the first couple of environment checks that `cellranger mkfastq` does along with samplesheet
preparation.
