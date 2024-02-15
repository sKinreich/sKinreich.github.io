def process_meta_file(hbnlnov_file):
    hbnlnov = pd.read_csv(hbnlnov_file, low_memory=False)
    hbnlnov = hbnlnov.loc[hbnlnov['date_diff_session'] < 365, :].reset_index(drop=True)
    hbnlnov = hbnlnov.loc[hbnlnov['date_diff_session'] > -365, :].reset_index(drop=True)
    hbnlnov['session_ID'] = hbnlnov['session'] + '1_' + hbnlnov['ID'].astype('str')
    hbnlnov = hbnlnov.loc[hbnlnov['questname'].str.contains('dx_'), :].reset_index(drop=True)
    hbnlnov = hbnlnov[~hbnlnov['questname'].str.contains('pssaga')].reset_index(drop=True)
    return hbnlnov


def add_meta():
    # life span
    # a file is extracted with a list of session
    #(ID+session) and for each sex, age and dx is added
    #Colection of the data is divided into two becouse the information
    # becouse the data and lifespan data exist in different files

    freq1='Gamma' # in my files the information is divided according to freqs
    # adding meta data to the files sex age.
    # lifespan
    meta_data_life= pd.read_excel(
        'C:/Users/SKinreic/OneDrive - Downstate Medical '
        'Center/private/Alcohol/lifespan/masterFile_asOf_01-02-2024_lifespan.xlsx')
    # for lifespan calculate the age
    meta_data_life["TESTDATE"]=meta_data_life["TESTDATE"].map(pd.to_datetime)
    meta_data_life["DOB"]=meta_data_life["DOB"].map(pd.to_datetime)
    meta_data_life['age'] = meta_data_life['TESTDATE'].dt.year  - meta_data_life['DOB'].dt.year
    # lifespan diagnosis file
    dx_data_life= pd.read_sas(
        'C:/Users/SKinreic/OneDrive - Downstate Medical Center/private/Alcohol/lifespan/ssaga5_dx/dx_ssaga5.sas7bdat')

    # process_the_meta_file
    #The big meta file from Weipeng was
    hbnlnov0=process_meta_file('E:/Data/COGA/HBNL2023Jan.ssaga 1.csv')

    meta_data_core= pd.read_excel(
        'E:/Data/COGA/core_pheno_20201120.xlsx')
    meta_data_core['sex'] = meta_data_core['sex'].replace({1: 'm'})
    meta_data_core['sex'] = meta_data_core['sex'].replace({2: 'f'})

    meta_data_core_info = pd.read_csv(
        'E:/Data/COGA/HBNL2023Novb.sessions.csv')
    meta_data_core_info['session'] = meta_data_core_info['session'].replace({'L1': 'L'})
    meta_data_core_info['ID_session']=meta_data_core_info['session'] +"1_"+meta_data_core_info['ID']
    # runs separatly for each freq
    # going over all the files in the freq file and add
    # more info about the subject
    freq_file= pd.read_csv(
        'E:/Data/COGA/eec/source_coh_'+freq1+'.csv')

    # core diagnosis

    no_age=[]
    sex_all = []
    age_all = []
    id_all = []
    aldx_all=[]
    race_all=[]
    m=0
    n=0

    for count, i in enumerate(freq_file['subject_ID']):
        if 'p0' in i:
            no_age.append(i)
            d=1
            continue
        print(i)
        i_life = int(i.split('_')[1])
        if 'l1' in i: # if the file is part of the latelife
            if i_life in meta_data_life['ID'].values:
                sex_info = meta_data_life.loc[meta_data_life['ID'] == i_life]['GENDER'].reset_index(drop=True)[0]
                age_info = meta_data_life.loc[meta_data_life['ID'] == i_life]['age'].reset_index(drop=True)[0]
                sex_all.append(sex_info)
                age_all.append(age_info)
                id_all.append(i)
                continue
            else:
                print(m)
                no_age.append(i)
        elif i in meta_data_core_info['ID_session'].values:# the id and session
            i_life = int(i.split('_')[1])
            age_info = meta_data_core_info.loc[meta_data_core_info['ID_session'] == i]['age'].reset_index(drop=True)[0]
            # not all the subjects in the core file
            if i_life in meta_data_core['ID'].values:
                sex_info = meta_data_core.loc[meta_data_core['ID'] == i_life]['sex'].reset_index(drop=True)[0]
                race_info = meta_data_core.loc[meta_data_core['ID'] == i_life]['race'].reset_index(drop=True)[0]
                sex_all.append(sex_info)
                age_all.append(age_info)
                race_all.append(race_info)
                id_all.append(i)
                continue
            else:# if not in core phenotype file then lets take sex from the file
                file1=freq_file.loc[count, 'file']
                file1=file1.replace('_'+freq1+'.csv','.cnt')
                file2=glob('*/'+file1)
                if not file2:
                    no_age.append(i)
                    continue
                else:
                    print(file2[0])
                    raw = mne.io.read_raw_cnt(file2[0], preload=True)
                    aa=raw.info['subject_info']['sex']
                    sex_info=int(aa)
                    race_info = ''
                    sex_all.append(sex_info)
                    age_all.append(age_info)
                    race_all.append(race_info)
                    id_all.append(i)
                    continue
                d = 1
        else:
            print(m)
            no_age.append(i)
            d=1

    freq_file = freq_file[~freq_file['subject_ID'].isin(no_age)]
    freq_file.reset_index(inplace=True)
    freq_file['age'] = age_all
    freq_file['sex'] = sex_all
    freq_file['id_all'] = id_all
    #freq_file['race'] = race_all

    # diagnosis
    no_age=[] # holds subject that we dont find information about them
    n=0
    for count, i in enumerate(freq_file['subject_ID']):
        n=n+1
        i_life = int(i.split('_')[1])
        if 'l1' in i:
            m=m+1
            if i_life in dx_data_life['IND_ID'].values:
                aldx_info = dx_data_life.loc[dx_data_life['IND_ID'] == i_life]['ald5dx'].reset_index(drop=True)[0]
                aldx_all.append(aldx_info)
                continue
            else:
                print(m)
                no_age.append(i)
                d=1
                continue
        else:
            if i in hbnlnov0['session_ID'].values: # prospective
                a1_file = hbnlnov0.loc[hbnlnov0['session_ID'] == i, :]
                aldx_info = a1_file['ALD4DPDX'].reset_index(drop=True)[0]
                aldx_all.append(aldx_info)
                continue
            else:
                print(m)
                no_age.append(i)
                d = 1
                continue
        print(m)
        no_age.append(i)
        d = 1
        continue

    freq_file = freq_file[~freq_file['subject_ID'].isin(no_age)]
    freq_file.reset_index(inplace=True)
    freq_file['aldx_all'] = aldx_all
    # file with age and sex variables
    freq_file.to_csv('source_coh_'+freq1+'_with_age.csv')

    np.savetxt('no_age.csv',
               no_age,
               delimiter=",",
               fmt='% s')
