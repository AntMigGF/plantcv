from plantcv.parallel import metadata_parser
from plantcv.parallel import job_builder
from plantcv.parallel import multiprocess
from plantcv.parallel import process_results
import tempfile


def run_workflow(config, workflow):
    """Wrapper function that runs all steps needed to run a PlantCV workflow.

    Inputs:
    config   = plantcv.parallel.WorkflowConfig class instance
    workflow = PlantCV workflow

    :param config: plantcv.parallel.WorkflowConfig
    :param workflow: str
    """
    jobcount, meta = metadata_parser(input_dir=config.input_dir, meta_fields=config.metadata_structure,
                                     valid_meta=config.metadata_terms, meta_filters=config.metadata_filters,
                                     date_format=config.timestampformat, start_date=config.start_date,
                                     end_date=config.end_date, delimiter=config.delimiter, file_type=config.imgformat,
                                     group_by=config.group_by, merge_group=config.merge_group)
    jobs = job_builder(meta, valid_meta=config.metadata_terms, workflow=workflow, job_dir=config.tmp_dir,
                       out_dir=config.output_dir, coprocess=config.coprocess, other_args=config.other_args,
                       writeimg=config.writeimg)

    multiprocess(jobs=jobs, cpus=config.processes)
    process_results(job_dir=config.tmp_dir, json_file=config.json)
