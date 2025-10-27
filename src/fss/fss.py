import os

def search(inputPath, excludedPath):

    excludeFlag = True
    numOfFilesScanned = 0

    if not excludedPath:
        excludeFlag = False

    if not os.path.exists(inputPath):
        return -1

    inputPath = os.path.abspath(inputPath)
    if os.path.isfile(inputPath):
        if not excludedPath:
            return 1
        elif inputPath not in excludedPath:
            return 1
        else:
            return 0

    if excludeFlag:
        if isinstance(excludedPath, str):
            excludedPath = [excludedPath]

        excludedSet = set()
        for ePath in excludedPath:
            ePath = os.path.abspath(ePath)
            excludedSet.add(ePath)

            if os.path.isdir(ePath):
                for root, dirs, files in os.walk(ePath):
                    for file in files:
                        excludedSet.add(os.path.join(root, file))
        
        excludedPath = excludedSet

    for root, dirs, files in os.walk(inputPath, topdown=True):

        if excludeFlag:
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in excludedPath] #This will exclude any directories included in the excludedPath set to prevent unneeded scans

        for file in files:
            filePath = os.path.join(root, file)
            print(filePath)
            if excludeFlag:
                if filePath not in excludedPath:
                    #This is where specifics of files can be extracted.
                    numOfFilesScanned += 1
            else:
                #Given no restrictions this is where details about scanned files can be extracted.
                numOfFilesScanned += 1

    return numOfFilesScanned
