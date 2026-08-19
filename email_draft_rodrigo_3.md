Hi Rodrigo,

That validation caught a real bug and it is ours, not yours. The spike times were written in NeuroExplorer ticks instead of seconds, so at 40 kHz a four hour recording came out as a unit table spanning nineteen years, which is what `check_spike_times_not_in_samples` and `check_units_table_duration` are telling you. Everything else in those files is right, the LFP, the AIM scores and the laser trials all carry proper times. It is fixed on the same branch, and on `mr171201e6` the spike times now run from 0.0023 s to 14932.85 s against a recording of 14932.9 s.

So the Plexon files need one more round. `neuroconv` 0.10.0 came out yesterday and the branch now pins the release instead of the pre-release, so this time the environment has to be rebuilt before you convert again:

```
cd nelson-lab-to-nwb
git switch restore-installable-repo
git pull
conda env remove --name env_nelson
conda env create --file make_env.yml
```

Then convert those sessions again and upload them to `001180` over what is there. The Intan files are not affected, as they carry no units, but they will not hurt from being re-run either. I converted both pipelines end to end from a clean environment built from these pins alone before writing this.

One more thing worth fixing in the same pass, in the metadata file. The subject is still the template one, `subid012345`, with `genotype` and `description` set to `not defined`, and the session start is 2000-07-23, which is earlier than the date of birth in the same file, so DANDI computes a negative age for the subject. The file already public in `001130` carries all of that too. Better to correct it now than after the dandiset is published with the paper.

On the inspection error from your earlier email, there is nothing to do on your side either. It comes from `nwbwidgets`, which has not been released in three years and does not work with the current `pynwb`. I removed it from the repo and the notebooks no longer import it. Use Neurosift instead:
https://neurosift.app

Your own dandiset opens here, though you will have to paste your DANDI API key into its settings while `001180` is embargoed:
https://neurosift.app/dandiset/001180

Once the spike times are fixed, the view worth your time there is the units raster against the trials table, as each laser pulse is written as a trial with its `stimulus_amplitude`, so you can see firing around the stimulation split by the four amplitudes.

Best,
Heberto
