import pandas as pd
import numpy as np

def reduce_cat_to_max_num_realizations(cmip6_cat):
    '''Reduce grid labels in pangeo cmip6 catalogue by 
    keeping grid_label and 'ipf' identifier combination with most datasets (=most realizations if using require_all_on)'''
    df = cmip6_cat.df
    cols = df.columns.tolist()
    
    df['ipf'] = [s[s.find('i'):] for s in df.member_id] #extract 'ipf' from 'ripf'

    #generate list of tuples of (source_id,ipf,grid_label) that provide most realizations (note this will omit realizations not available at this grid but possibly at others)
    max_num_ds_tuples = df.groupby(['source_id','ipf'])['grid_label'].value_counts().groupby(level=0).head(1).index.to_list() #head(1) gives (first) max. value since value_counts sorts max to min
    df_filter = pd.DataFrame(max_num_ds_tuples,columns=['source_id','ipf','grid_label']) #generate df to merge catalogue df on
    
    df = df_filter.merge(right=df, on = ['source_id','ipf','grid_label'], how='left') #do the subsetting
    df = df.drop(columns=['ipf']) #clean up
    df= df[cols]

    cmip6_cat.esmcat._df = df #(columns now ordered differently, probably not an issue?)
    return cmip6_cat

def drop_vars_from_cat(cmip6_cat,vars_to_drop):
    '''drops entries with unwanted variables from search catalogue dataframe'''
    cmip6_cat.esmcat._df = cmip6_cat.df.drop(cmip6_cat.df[cmip6_cat.df.variable_id.isin(vars_to_drop)].index).reset_index(drop=True)
    return cmip6_cat

def drop_older_versions(cat):
    for i in np.arange(len(cat.df)):
        if isinstance(cat.df.loc[i,'version'],int)==False:
            cat.df.loc[i,'version'] = int(cat.df.loc[i,'version'].replace('v',''))
    #sorting by zstore first to make sure that the newest leap catalogue is used if duplicate datasets with the same version!
    cat.esmcat._df = cat.df.sort_values(by='zstore', ascending=False).drop_duplicates(subset=['activity_id','institution_id','source_id','experiment_id','member_id','table_id','variable_id','grid_label','version']).sort_index()
    cat.esmcat._df = cat.df.sort_values(by='version', ascending=False).drop_duplicates(subset=['activity_id','institution_id','source_id','experiment_id','member_id','table_id','variable_id','grid_label']).sort_index()
    
    return cat