import sys, os
from modnet.preprocessing import MODData
import numpy as np
import pandas as pd
import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
# setting path
#sys.path.append('../')
#from MEGNetCustomTraining import MEGNetCustomTraining
import glob


def getCumulative_PCA(X,datasetname="Dataset",savedir='./'):
    ''' Generates PCA analysis of the dataset returning the PCA cumulative variance to determine the number of components.
    '''
    try:
        os.mkdir(savedir)
    except:
        print(f"Folder {savedir} already created")
    # Standardizing the features
    standard_scaler_PCA=StandardScaler()
    X = standard_scaler_PCA.fit_transform(X)
    
    pca = PCA().fit(X)
    cumulative_pca_components=np.cumsum(pca.explained_variance_ratio_)
    plt.plot(cumulative_pca_components)
    plt.xlabel('number of components')
    plt.ylabel('cumulative explained variance');
    saveprefix=savedir+f'{datasetname}_CumulativePCA'
    plt.savefig(saveprefix+'.png')
    np.savetxt(saveprefix+'.txt',list(enumerate(cumulative_pca_components)))
    print(pca.explained_variance_ratio_)

def get_PCAdataset(X,n_components,datasetname="Dataset",savedir='./', featname="ReducedFeats"):
    ''' Returns the PCA transformed dataset with the given number of components. '''
    try:
        os.mkdir(savedir)
    except:
        print(f"Folder {savedir} already created")
    standard_scaler_PCA=StandardScaler()
    ## get X columns
    Xcolumns=X.columns
    X = standard_scaler_PCA.fit_transform(X)
    pickle.dump(standard_scaler_PCA,open(savedir+f"{datasetname}_PCAScaler.pkl","wb"))
    ## PCA fit transform
    pca = PCA(n_components=n_components)
    principalComponents = pca.fit_transform(X)
    OFM_PC_df = pd.DataFrame(data = principalComponents
                 , columns = [f'OFM|PC_{idx+1}' for idx in range(n_components) ])
    pickle.dump(OFM_PC_df,open(savedir+f"{datasetname}_PCAtransformed.pkl","wb"))
    print("Transformed Dataset through PCA")
    print(OFM_PC_df)
    OFM_PCAcomponents = pd.DataFrame(pca.components_[:n_components], 
                                     columns=Xcolumns,
                                     index=[f'{featname}|PC_{idx+1}' for idx in range(n_components)])
    print("PCA components correspondents")
    pickle.dump(OFM_PCAcomponents,open(savedir+f"{datasetname}_PCAcomponents.pkl","wb"))
    print(OFM_PCAcomponents)

from megnet.utils.models import load_model, AVAILABLE_MODELS
from keras.models import Model
import warnings
warnings.filterwarnings("ignore")
# print(AVAILABLE_MODELS)
def get_MEGNetFeaturesDF(structures,layer_type='antepenult'):
    MEGNetFeats_structs=[]
    if layer_type=='antepenult':
        layeridx=-3
        sizelayer=32
    elif layer_type=='penult':
        layeridx=-2
        sizelayer=16

    for model_name in ['Eform_MP_2019','Efermi_MP_2019','Bandgap_MP_2018','logK_MP_2019','logG_MP_2019']:
        model=load_model(model_name) 
        intermediate_layer_model = Model(inputs=model.input,
                             outputs=model.layers[layeridx].output)   
        MEGNetModel_structs=[]
        for s in structures:
            try:
                graph = model.graph_converter.convert(s)
                inp = model.graph_converter.graph_to_input(graph)
                pred = intermediate_layer_model.predict(inp, verbose=False)
                model_struct=pd.DataFrame([pred[0][0]], 
                                          columns=[f"MEGNet_{model_name}_{idx+1}" for idx in 
                                                   range(len(pred[0][0]))])
                MEGNetModel_structs.append(model_struct)
            except Exception as e:
                print(e)
                print("Probably an invalid structure was passed to the model, continuing..")
                model_struct=pd.DataFrame([np.nan]*sizelayer, 
                                          columns=[f"MEGNet{sizelayer}l_{model_name}_{idx+1}" for idx in 
                                                   range(len(pred[0][0]))])
                continue
        ## now append the columns with the layer of each model
        MEGNetModel_structs=pd.concat(MEGNetModel_structs,axis=0)
        MEGNetFeats_structs.append(MEGNetModel_structs)
        print(f"Features calculated for model {model_name}.")
    ## now every structure calculated with each model is combined in a final dataframe
    MEGNetFeats_structs=pd.concat(MEGNetFeats_structs,axis=1)
    return MEGNetFeats_structs

def sliced_featurization(structures, featurizer, prefix_df='featurized', slice_size=1000, savedir='./',**kwargs):
    try:
        os.mkdir(savedir)
    except:
        print(f"Folder {savedir} already created.")
    slices=list(range(0,len(structures),slice_size))+[None]
    for idx in range(len(slices)-1):
        if kwargs.get('continue_from_index',False) and idx < kwargs.get('continue_from_index',0):
           continue
        kwargs.pop('continue_from_index',0)
        print(f"Processing slice {idx+1} out of {len(slices)}")
        feat_df=featurizer(structures[slices[idx]:slices[idx+1]],**kwargs)
        pickle.dump(feat_df,open(savedir+prefix_df+f"_slice{idx}.pkl", "wb"))
        del feat_df ## free memory

