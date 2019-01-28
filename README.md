# Lane-Detector
Basic lane marker detection and traking using Semantic segmentaion and basic Image processing
## TO DO:
- [x] Start the readme
- [ ] mention about Prerequisites
- [ ] Mention about the parameters in readme.md

## How To use :
1. Get segmented images in appropriate folders.
2. Then Run Object detectors
```
python object_detector.py
python pole_detector.py
python car_detector.py
```
This will create cluster images
3. Then run Cluster_tracking.py to cluster and track lanes and poles, generate optical flow and save the result(tracklets) in npy format
```
python cluster_tracking.py
```
4. clustering.py will track the previous objects based and form nice tracklets and will other pre proicessing such as creating refence point ofr each object in each frame
5. Finally graph.py will take all these tracklets( cars , poles , lanes ) Create an graph and ask for annotaions and create a graph in am format whoich can be used by the muli relational GCN
