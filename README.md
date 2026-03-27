# UFS benchmark results

This repository hosts the scripts to plot the UFS benchmark results.

### How to use

* Download and untar the CSVs into a folder named `results`: `tar -xzvf csv.tar.gz -C ./results`
* Create a python virtual environment and download the dependencies from the `requirements.txt` file.
* Modify the configurations inside `graph_cgroups_bargraph_clients.py` as needed:
    - You'll notice one "configuration" per plot. You can only generate one plot at a time, so only one configuration should be uncommented at a time. Uncomment them as needed to plot the different benchmarks.
    - If you scroll down some more, you'll notice a `benchmark` variable, indicating the name of the benchmark. You'll need to change this depending on whether you're generating a YCSB or a TPC-C plot.
* Once you've changed the configurations to your liking, you can generate the plot by simply running the script without arguments:

```
python3 graph_cgroups_bargraph_clients.py
```

* The end result is a PDF generated in the `sched_ext/barplot` folder. Feel free to contact me if you have questions!