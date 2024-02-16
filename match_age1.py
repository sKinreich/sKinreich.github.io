def match_age1(group1,group2):
    # The two groups include ID and session,
    # and age (it can have more features of course)
    # the return are the indices from both goups that are
    # matched
    group2_ind = []
    group1_ind=[]
    tt=[0,1,-1,2,-2,3,-3]
    for kk in tt:
        for countm, im in enumerate(group2.age):
            done = False
            if math.isnan(im): # continue if age is missing
                continue
            for counth, ih in enumerate(group1.age):
                if math.isnan(ih):# continue if age is missing
                    continue
                if counth in group1_ind:# continue if age is missing
                    continue
                if round(im) == round(ih) + kk:
                        group1_ind.append(counth)
                        group2_ind.append(countm)
                        done = True
                        break
                else:
                        if counth == len(group1):
                            break
                if done:
                    break
        filename='group2_ind_aud.txt'
        np.savetxt(filename, group2_ind)
        filename='group1_ind_cntl.txt'
        np.savetxt(filename, group1_ind)
        return group1_ind, group2_ind