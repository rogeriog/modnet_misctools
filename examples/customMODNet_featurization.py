from modnet.preprocessing import MODData
import modnet.featurizers
import contextlib
class CustomFeaturizer(modnet.featurizers.MODFeaturizer):

    def __init__(self, fast_oxid=False):
        super().__init__()

        with contextlib.redirect_stdout(None):
            """
            from matminer.featurizers.composition import (
                AtomicOrbitals,
                OxidationStates,
            )
            ## just included these to have oxidation states for fingerprints
            self.composition_featurizers = (
                AtomicOrbitals(),
            )
            self.oxid_composition_featurizers = (
                OxidationStates(),
            )
            """
            from matminer.featurizers.structure import (
                    BondFractions,
                    CoulombMatrix,
                    SineCoulombMatrix)
                    
            from matminer.featurizers.site import (        
                    VoronoiFingerprint, 
                    CrystalNNFingerprint, 
                    OPSiteFingerprint)
            ## missing featurizers in perovskites set
            self.site_featurizers = (
                        #    AGNIFingerprints(),
                            CrystalNNFingerprint.from_preset("ops"),
                            OPSiteFingerprint(),
                            VoronoiFingerprint(),
                        )

            self.structure_featurizers = (
                            CoulombMatrix(),
                            SineCoulombMatrix(),
                            BondFractions(),
                         )

            self.fast_oxid = fast_oxid
from modnet.preprocessing import MODData
from modnet.models import MODNetModel


loadeddata=MODData.load('DATAFILES/matbench_perovskites_moddata.pkl.gz')
df_structure=loadeddata.df_structure
Featurizer=CustomFeaturizer()
from matminer.featurizers.structure import SiteStatsFingerprint
import pandas as pd
#resultsdf=[]
resultdf=Featurizer.featurize_site(df_structure)
tmpdf=Featurizer.featurize_structure(df_structure)
resultdf=pd.concat([resultdf,tmpdf],axis=1)
print(resultdf)
import pickle
pickle.dump(resultdf, open("AddedFeats_MB_Perovskite.pkl","wb"))



"""
for fingerprint in Featurizer.site_featurizers:
    site_stats_fingerprint = SiteStatsFingerprint(
                            fingerprint, stats=('mean','std_dev')
                                        )
    df = df_structure.copy()
    df = site_stats_fingerprint.featurize_dataframe( df, 
            "structure", multiindex=False, ignore_errors=True
                                        )
    resultsdf.append(df)

    #result=featurizer.featurize_dataframe(df_structure, "structure", ignore_errors=True, return_errors=True)
#
dfs_final=pd.concat(resultsdf, axis=1)
print(dfs_final)
"""
"""
# Creating MODData
data = MODData(materials = loadeddata.structures,
               # targets = loadeddata.targets,               
               featurizer = CustomFeaturizer(),
                                     )
#data.featurize()
#previous_dffeat=data.df_featurized
#data.df_featurized=None
#data.featurizer=CustomFeaturizer()
data.featurize(n_jobs=24)
data.save('./AddedFeats_MB_Perovskite.pkl.gz')
"""
"""
df_structure=data.df_structure


for featurizer in site_featurizers:
    result=featurizer.featurize_dataframe(df_structure, "structure", ignore_errors=True, return_errors=True)
    print(result)
"""
