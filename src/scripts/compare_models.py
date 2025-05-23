"""
Script to run all models and compare their performance.
"""

import os
import sys
import subprocess
import logging
import argparse
import pandas as pd
import csv
import time
import signal

# Add src directory to path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from utils.results_tracker import print_model_comparison, save_report_to_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_script(script_name, args=None, timeout=1800):  # Default timeout of 30 minutes
    """Run a Python script and capture its output."""
    logger.info(f"Running {script_name}...")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    cmd = [sys.executable, script_path]
    
    # Add any additional arguments
    if args:
        cmd.extend(args)
    
    try:
        # Run with timeout
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout  # Add timeout to prevent hanging
        )
        execution_time = time.time() - start_time
        logger.info(f"Script execution time: {execution_time:.2f} seconds")
        
        if result.returncode != 0:
            logger.error(f"Error running {script_name}:")
            logger.error(result.stderr)
            return False
        
        logger.info(f"Successfully ran {script_name}")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout after {timeout} seconds while running {script_name}")
        return False
    except Exception as e:
        logger.error(f"Error running {script_name}: {str(e)}")
        return False

def load_and_display_results():
    """Load results from CSV and display them as a dataframe."""
    results_file = os.path.join(src_dir, 'model_results.csv')
    
    if not os.path.exists(results_file):
        logger.error("No results file found.")
        return
    
    try:
        # Load results into pandas DataFrame
        df = pd.read_csv(results_file)
        
        # Display the DataFrame
        logger.info("\nModel Results (sorted by accuracy):")
        logger.info(f"\n{df.to_string()}")
        
        # Also display the best model summary
        summary_file = os.path.join(src_dir, 'best_model_summary.txt')
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                logger.info(f"\nBest Model Summary:\n\n{f.read()}")
    
    except Exception as e:
        logger.error(f"Error loading results: {str(e)}")

def main():
    """Run all models and compare their performance."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Compare different sentiment analysis models")
        
        parser.add_argument(
            "--include_roberta", 
            action="store_true",
            help="Include RoBERTa model in comparison (slower but potentially more accurate)"
        )
        
        parser.add_argument(
            "--include_all", 
            action="store_true",
            help="Include all models in comparison"
        )
        
        parser.add_argument(
            "--sample_size", 
            type=int, 
            default=20000,  # Increased from 5000 to match run_pipeline.py default
            help="Sample size for models (smaller values are faster but less accurate)"
        )
        
        parser.add_argument(
            "--timeout", 
            type=int, 
            default=1800,  # 30 minutes default
            help="Timeout in seconds for each model script"
        )
        
        parser.add_argument(
            "--skip_training", 
            action="store_true",
            help="Skip model training and just generate comparison from existing results"
        )
        
        parser.add_argument(
            "--verbose", 
            type=int, 
            default=1,
            choices=[0, 1, 2],
            help="Verbosity level (0=quiet, 1=normal, 2=verbose)"
        )
        
        args = parser.parse_args()
        
        # Script mapping
        script_mapping = {
            "mlp_basic": "mlp_basic_main.py",
            "mlp_enhanced": "mlp_enhanced_main.py",
            "roberta": "roberta_main.py",
            "kernel": "kernel_approximation_main.py",
            "pca": "randomized_pca_main.py",
            "lstm": "lstm_main.py",
            "lstm_roberta": "lstm_roberta_main.py"
        }
        
        # Check if we should skip training
        if not args.skip_training:
            # List of scripts to run
            scripts = [
                {"name": script_mapping["mlp_basic"], "args": [f"--sample_size={args.sample_size}"]},
                {"name": script_mapping["mlp_enhanced"], "args": [f"--sample_size={args.sample_size}"]},
                {"name": script_mapping["kernel"], "args": [f"--sample_size={args.sample_size}"]},
                {"name": script_mapping["pca"], "args": [f"--sample_size={args.sample_size}"]}
            ]
            
            # Add RoBERTa if requested
            if args.include_roberta or args.include_all:
                # Use a smaller sample size for transformer models if the requested size is very large
                transformer_sample_size = min(args.sample_size, 20000) if args.sample_size > 20000 else args.sample_size
                
                # RoBERTa args
                roberta_args = [
                    f"--sample_size={transformer_sample_size}"
                ]
                scripts.append({"name": script_mapping["roberta"], "args": roberta_args})
                
                # Add LSTM and LSTM-RoBERTa if include_all is set
                if args.include_all:
                    scripts.append({"name": script_mapping["lstm"], "args": [
                        f"--sample_size={transformer_sample_size}",
                        "--mode=train"
                    ]})
                    
                    scripts.append({"name": script_mapping["lstm_roberta"], "args": [
                        f"--sample_size={transformer_sample_size}",
                        "--mode=train"
                    ]})
            
            # Run all scripts
            for script_info in scripts:
                script_timeout = args.timeout
                # Transformer models need more time
                if script_info["name"] in [script_mapping["roberta"], script_mapping["lstm_roberta"]]:
                    script_timeout = max(script_timeout, 3600)  # At least 60 minutes
                    
                success = run_script(script_info["name"], script_info["args"], timeout=script_timeout)
                if not success:
                    logger.warning(f"Skipping {script_info['name']} due to errors")
        else:
            logger.info("Skipping model training as requested")
        
        # Generate the CSV report
        save_report_to_file()
        
        # Load and display the results
        load_and_display_results()
        
        logger.info("Model comparison complete!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 