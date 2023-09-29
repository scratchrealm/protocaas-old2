export type DandiUploadTask = {
    sorterName: string
    dandisetId: string
    dandiInstance: string
    fileNames: string[]
    names: string[]
}

const prepareDandiUploadTask = (fileNames: string[]): DandiUploadTask | undefined => {
    if (fileNames.length === 0) {
        return undefined
    }
    let sorterName: string | undefined = undefined
    let dandisetId: string | undefined = undefined
    let staging: boolean | undefined = undefined
    const names: string[] = []
    for (const fileName of fileNames) {
        if (!fileName.endsWith('.nwb')) {
            return undefined
        }
        const a = fileName.split('/')
        if (a.length <3) {
            return undefined
        }
        if ((sorterName) && (sorterName !== a[0])) {
            return undefined
        }
        const dd = a[1].startsWith('staging-') ? a[1].substring('staging-'.length) : a[1]
        if ((dandisetId) && (dandisetId !== dd)) {
            return undefined
        }
        const ss = a[1].startsWith('staging-')
        if ((staging !== undefined) && (staging !== ss)) {
            return undefined
        }
        sorterName = a[0]
        dandisetId = dd
        staging = ss
        names.push(a.slice(2).join('/'))
    }
    if ((!sorterName) || (!dandisetId) || (staging === undefined)) {
        return undefined
    }
    if (!validDandisetId(dandisetId)) {
        return undefined
    }
    return {
        sorterName,
        dandisetId,
        dandiInstance: staging ? 'dandi-staging' : 'dandi',
        fileNames,
        names
    }
}

const validDandisetId = (dandisetId: string): boolean => {
    // must be an integer
    if (!dandisetId.match(/^\d+$/)) {
        return false
    }
    return true
}

export default prepareDandiUploadTask
