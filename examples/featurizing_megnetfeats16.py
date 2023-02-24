from modnet.preprocessing import MODData
data=MODData.load('./DATAFILES/matbench_perovskites_moddata.pkl.gz')
import pickle

from ProcessFeatureDatasets import sliced_featurization, get_MEGNetFeaturesDF 

structures=data.df_structure['structure']
sliced_featurization(structures, get_MEGNetFeaturesDF, prefix_df='MEGNetFeats16', 
                     slice_size=1000, savedir='./DATAFILES/MEGNetFeats16/',layer_type='penult',
                     continue_from_index=14)
