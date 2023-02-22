import os
import shutil
from modnet.preprocessing import MODData
import pickle
import pandas as pd


# Get the current folder
current_folder = os.path.abspath(os.path.dirname(__file__))


def replace_line(file_name, line_num, text):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    lines[line_num] = text
    with open(file_name, 'w') as f:
        f.writelines(lines)


def initialize_data(fullpath_moddata, calculation_name, dirnames, sampling=[None], target_name=None):
    for idx, dirname in enumerate(dirnames):
        # the full set calculations files
        if sampling[idx] is None:
            shutil.copyfile(fullpath_moddata, os.path.join(dirname, calculation_name, 'precomputed', os.path.basename(fullpath_moddata)))
        else:
            n_samples = sampling[idx]
            data = MODData.load(fullpath_moddata)
            print(data.df_featurized)
            datatmp = data.df_featurized
            if target_name is None:
                target_name = data.df_targets.columns[0]
            datatmp[target_name] = data.df_targets
            datatmp['structure'] = data.df_structure
            datatmp = datatmp.sample(n_samples, random_state=1)
            print(datatmp)
            # substitute in MODData and save
            data.df_featurized = datatmp.drop([target_name, 'structure'], axis=1)
            data.df_targets = datatmp[[target_name]]
            data.df_structure = datatmp[['structure']]
            data.save(os.path.join(dirname, calculation_name, 'precomputed', os.path.basename(fullpath_moddata).split('.')[0] + f'_{n_samples}.pkl.gz'))


def initialize_dirs(calculation_name, main_dirs, subfolders=['./']):
    matbench_folders = ["final_model", "folds", "plots", "precomputed", "results"]
    run_folders = []
    for folder in main_dirs:
        try:
            os.mkdir(folder)
        except FileExistsError:
            print("Folder already created.")
            continue
        for subfolder in subfolders:
            try:
                if subfolder != './':
                    os.mkdir(os.path.join(folder, subfolder))
            except FileExistsError:
                print("Folder already created.")
                continue
            run_folders.append(os.path.join(folder, subfolder))
            shutil.copyfile(os.path.join(current_folder, "_run_benchmark.py"), os.path.join(folder, subfolder, "run_benchmark.py"))
            shutil.copyfile(os.path.join(current_folder, "_submit.sh"), os.path.join(folder, subfolder, "submit.sh"))
            shutil.copyfile(os.path.join(current_folder, "_gitignore"), os.path.join(folder, subfolder, ".gitignore"))
            if subfolder == './':
                replace_line(os.path.join(folder, subfolder, "submit.sh"), 1, f'#SBATCH --job-name={folder}\n')
            else:
                replace_line(os.path.join(folder, subfolder, "submit.sh"), 1, f'#SBATCH --job-name={folder}{subfolder}\n')
            replace_line(os.path.join(folder, subfolder, "submit.sh"), 15, f'python3 run_benchmark.py --task {calculation_name} --n_jobs $nproc >> log.txt\n')
            try:
                os.mkdir(os.path.join(folder, subfolder, calculation_name))
            except FileExistsError:
                print("Folder already created.")
            for matbench_folder in matbench_folders:
                try:
                    os.mkdir(os.path.join(folder, subfolder, calculation_name, matbench_folder))
                except FileExistsError:
                    print("Folder already created.")
                    continue

def AppendToMODData(data_to_concatenate, reference_filename, saved_filename, mode='concat',addidprefix=True):
#    datatoconcatenate="result_OFMclustering_perovskites.pkl"
#    referencefilename="/path/to/featurized/matbench_perovskites/precomputed/matbench_perovskites_moddata.pkl.gz"
    dataToConcat=pickle.load(open(data_to_concatenate,"rb"))
    if addidprefix:
        dataToConcat.index="id"+dataToConcat.index.astype(str)
    print(dataToConcat)
    dataReference = MODData.load(reference_filename) # precomputed_moddata)
    print(dataReference.df_featurized)
    if mode == 'concat': 
        concatDF=pd.concat([dataReference.df_featurized,dataToConcat],axis=1)
        dataReference.df_featurized=concatDF
    if mode == 'substitute':
        dataReference.df_featurized=dataToConcat
    dataReference.save(saved_filename)
    print(dataReference.df_featurized)

'''
import os, shutil 
from modnet.preprocessing import MODData 
import os

# Get the current folder
current_folder = os.path.abspath(os.path.dirname(__file__))

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def initialize_data(fullpath_moddata,calculation_name,dirnames,sampling=[None],target_name=None):
    for idx, dirname in enumerate(dirnames):
    ### the full set calculations files
        if sampling[idx] is None:
            shutil.copyfile(path_full_data, './'+dirname+'/'+calculation_name+'/precomputed/'+path_full_data.split('/')[-1])
        else:
            n_samples=sampling[idx]
            data=MODData.load(path_full_data)
            print(data.df_featurized)
            datatmp=data.df_featurized
            if target_name is None:
                target_name=data.df_targets.columns[0]
            datatmp[target_name]=data.df_targets
            datatmp['structure']=data.df_structure
            datatmp=datatmp.sample(n_samples,random_state=1)
            print(datatmp)
            ## substitute in MODData and save
            data.df_featurized=datatmp.drop([target_name,'structure'],axis=1)
            data.df_targets=datatmp[[target_name]]
            data.df_structure=datatmp[['structure']]
            data.save(dirname+calculation_name+'/precomputed/'+path_full_data.split('/')[-1].split('.')[0]+f'_{n_samples}.pkl.gz')

def initialize_dirs(calculation_name,main_dirs,subfolders=['./']):
    # types=["MODNetCompressed"]
    matbench_folders=["final_model","folds","plots","precomputed","results"]
    run_folders=[]
    for folder in main_dirs:
        try:
            os.mkdir(folder)
        except OSError:
            print("Folder already created.")
            continue
        for subfolder in subfolders:
            try:
                if subfolder != './':
                    os.mkdir(folder+'/'+subfolder)
            except OSError:
                print("Folder already created.")
                continue
            run_folders.append(folder+'/'+subfolder)
            
            shutil.copyfile(current_folder+"/_run_benchmark.py", folder+'/'+subfolder+"/run_benchmark.py")
            shutil.copyfile(current_folder+"/_submit.sh", folder+'/'+subfolder+"/submit.sh")
            shutil.copyfile(current_folder+"/_gitignore", folder+'/'+subfolder+"/.gitignore")
            if subfolder == './':
                replace_line(folder+'/'+subfolder+"/submit.sh",1,f'#SBATCH --job-name={folder}\n')
            else:
                replace_line(folder+'/'+subfolder+"/submit.sh",1,f'#SBATCH --job-name={folder}{subfolder}\n')
            replace_line(folder+'/'+subfolder+"/submit.sh",15,f'python3 run_benchmark.py --task {calculation_name} --n_jobs $nproc >> log.txt\n')
            try:
                os.mkdir(folder+'/'+subfolder+'/'+calculation_name+'/')
            except OSError:
                print("Folder already created.")
            for matbench_folder in matbench_folders:
                try:
                    os.mkdir(folder+'/'+subfolder+'/'+calculation_name+'/'+matbench_folder) 
                except OSError:
                    print("Folder already created.")
                    continue
    return run_folders
'''