import os

def search(inputPath, excludedPath):

    excludeFlag = True
    numOfFilesScanned = 0

    if not excludedPath:
        #If there is not included exclusion, the flag will be set to false to skip comparisons
        excludeFlag = False

    if not os.path.exists(inputPath):
        #invalid returns -1
        return -1

    inputPath = os.path.abspath(inputPath)
    if os.path.isfile(inputPath):
        if not excludedPath:
            #single file with no exclusion
            return 1
        elif inputPath not in excludedPath:
            #single file accounting for exclusion
            return 1
        else:
            return 0

    if excludeFlag:
        #ensures that the excluded paths input is a set
        if isinstance(excludedPath, str):
            excludedPath = {excludedPath}
        else:
            excludedPath = set(excludedPath)


        excludedSet = set()
        for ePath in excludedPath:
            ePath = os.path.abspath(ePath)
            excludedSet.add(ePath)

            #if exculsion includes a dir, it will add all files within the dir to exculsion
            if os.path.isdir(ePath):
                for root, dirs, files in os.walk(ePath):
                    for file in files:
                        excludedSet.add(os.path.join(root, file))
        
        excludedPath = excludedSet

    for root, dirs, files in os.walk(inputPath, topdown=True):

        for file in files:
            filePath = os.path.join(root, file)
            print(filePath)
            if excludeFlag:
                if filePath not in excludedPath:
                    #This is where specifics of files can be extracted.
                    numOfFilesScanned += 1
            else:
                #Given no exclusion this is where details about scanned files can be extracted.
                numOfFilesScanned += 1

    return numOfFilesScanned
