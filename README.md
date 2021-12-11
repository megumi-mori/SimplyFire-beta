# PyMini

update log
- Dec 10 2021:
  - decay function takes into account the previous mini
  - still need to plot correctly on the param guide
  - None option added for decay (for faster analysis?)
- Dec 9 2021: vb0.1.6
  - filtering the mini results option
  - decay:rise ratio criterion added 
- Dec 8 2021: vb0.1.5
  - converted mini parameters to ms (instead of number of data points)
  - fixed bug with mini details not being focused when selected via the traceviewer
  - fixed bug with disappearing mini details during evoked/mini analysis switch or overlay/continuous mode switch
  - cleaned code for data_display column show/hide
  - opening mini-file adds undo queue with the mini data prior to file opening
- Dec 2 2021: vb.1.3-4
    - fixed error with next_peak_idx variable (undefined if compound option is not checked)
    - forward search for previously found minis
  - extrapolate 'true amplitude' from previous mini using decay function for compound minis
- Nov 29 2021: vb0.1.2
    - added a way to look forward when searching for minis
    - might need to update so that the future mini is analyzed for amplitude (reject if too low)
  
# things to look out for
- 21930008 at 33.5s - noisy decay, halfwidth requires short lag
  - try fixing this by going further than 'end' if not compound? 

