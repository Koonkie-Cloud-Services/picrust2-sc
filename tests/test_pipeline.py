#!/usr/bin/env python

import unittest
from os import path
from picrust2.util import TemporaryDirectory
from picrust2.pipeline import full_pipeline_split

class PipelineTest(unittest.TestCase):
    """Tests for the full_pipeline_split function."""
    def setUp(self):
        test_dir_path = path.dirname(path.abspath(__file__))
        test_data_path = path.join(test_dir_path, "test_data")

        self.test_study_seqs = path.join(
            test_data_path, "place_seqs", "study_seqs_test.fasta"
        )

        self.test_ref_dir = path.join(
            test_data_path, "place_seqs", "img_centroid_16S_aligned_head30"
        )

        self.test_known_marker = path.join(
            test_data_path, "workflow", "workflow_marker_for_split_pipeline.tsv.gz"
        )

        self.test_known_traits = path.join(
            test_data_path, "workflow", "workflow_known_traits.tsv.gz"
        )

        self.test_seq_abun_tsv = path.join(
            test_data_path, "workflow", "workflow_seq_abun.tsv.gz"
        )

        # Path to default pathway map (using a simplified structure for testing)
        self.test_pathway_map = path.join(
            path.dirname(test_dir_path),
            "picrust2",
            "default_files",
            "pathway_mapfiles",
            "metacyc_pathways_structured_filtered_v24.txt",
        )

        for file_path in [
            self.test_study_seqs,
            self.test_ref_dir,
            self.test_known_marker,
            self.test_known_traits,
            self.test_seq_abun_tsv,
            self.test_pathway_map,
        ]:
            self.assertTrue(path.exists(file_path), f"Test file not found: {file_path}")

        return


    def test_full_pipeline_split_stratified(self):
        """Test full_pipeline_split with stratified output enabled."""

        with TemporaryDirectory() as temp_dir:

            out_dir = path.join(temp_dir, "pipeline_out_strat")

            # Run with stratified output
            func_output, pathway_output = full_pipeline_split(
                study_fasta=self.test_study_seqs,
                input_table=self.test_seq_abun_tsv,
                output_folder=out_dir,
                ref_dir1=self.test_ref_dir,
                ref_dir2=self.test_ref_dir,
                in_traits="EC",
                custom_trait_tables_ref1=self.test_known_traits,
                custom_trait_tables_ref2=self.test_known_traits,
                marker_gene_table_ref1=self.test_known_marker,
                marker_gene_table_ref2=self.test_known_marker,
                pathway_map=self.test_pathway_map,
                rxn_func=self.test_known_traits,
                no_pathways=True,  # Skip pathway inference for test simplicity
                stratified=True,
                regroup_map=None,
                no_regroup=True,
                skip_minpath=True,
                no_gap_fill=True,
                verbose=True,
            )

            # Check that pathway_output is None when no_pathways=True
            self.assertIsNone(pathway_output)

            # Check that func_output still exists
            self.assertIsNotNone(func_output)

    def test_full_pipeline_split_no_pathways(self):
        """Test full_pipeline_split with pathways disabled."""

        with TemporaryDirectory() as temp_dir:

            out_dir = path.join(temp_dir, "pipeline_out_no_path")

            # Run with no_pathways=True
            func_output, pathway_output = full_pipeline_split(
                study_fasta=self.test_study_seqs,
                input_table=self.test_seq_abun_tsv,
                output_folder=out_dir,
                ref_dir1=self.test_ref_dir,
                ref_dir2=self.test_ref_dir,
                in_traits="EC",
                custom_trait_tables_ref1=self.test_known_traits,
                custom_trait_tables_ref2=self.test_known_traits,
                marker_gene_table_ref1=self.test_known_marker,
                marker_gene_table_ref2=self.test_known_marker,
                pathway_map=self.test_pathway_map,
                rxn_func=self.test_known_traits,
                no_pathways=True,  # Skip pathway inference for test simplicity
                stratified=False,
                regroup_map=None,
                no_regroup=True,
                skip_minpath=True,
                no_gap_fill=True,
                verbose=True,
            )

            # Check that pathway_output is None when no_pathways=True
            self.assertIsNone(pathway_output)

            # Check that func_output still exists
            self.assertIsNotNone(func_output)

            # Check that expected output files exist
            # The combined marker file should exist
            combined_marker = path.join(
                out_dir, "combined_marker_predicted_and_nsti.tsv.gz"
            )
            self.assertTrue(
                path.exists(combined_marker),
                f"Expected combined marker file not found: {combined_marker}",
            )

            # Check that reference tree files were created
            # Since we're using custom ref_dir (not default), should be ref1.tre and ref2.tre
            ref1_tree = path.join(out_dir, "ref1.tre")
            ref2_tree = path.join(out_dir, "ref2.tre")
            self.assertTrue(
                path.exists(ref1_tree), f"Expected ref1 tree not found: {ref1_tree}"
            )
            self.assertTrue(
                path.exists(ref2_tree), f"Expected ref2 tree not found: {ref2_tree}"
            )

if __name__ == "__main__":
    unittest.main()
