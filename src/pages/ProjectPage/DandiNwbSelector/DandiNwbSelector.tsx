import { Search } from "@mui/icons-material"
import { FunctionComponent, useCallback, useEffect, useState } from "react"
import SmallIconButton from "../../../components/SmallIconButton"
import SearchResults from "./SearchResults"
import { AssetResponse, AssetsResponseItem, DandisetSearchResultItem, DandisetsResponse } from "./types"

type Props = {
    width: number
    height: number
    onNwbFilesSelected: (files: {nwbUrl: string, dandisetId: string, dandisetVersion: string, assetId: string, assetPath: string, useStaging: boolean}[]) => Promise<void>
}

const topBarHeight = 30
const searchBarHeight = 50
const DandiNwbSelector: FunctionComponent<Props> = ({width, height, onNwbFilesSelected}) => {
    const [searchText, setSearchText] = useState<string>('')
    const [searchResult, setSearchResults] = useState<DandisetSearchResultItem[]>([])
    const [useStaging, setUseStaging] = useState<boolean>(false)
    const toggleUseStaging = useCallback(() => {setUseStaging(v => (!v))}, [])
    const stagingStr = useStaging ? '-staging' : ''
    useEffect(() => {
        let canceled = false
        setSearchResults([])
        ; (async () => {
            const response = await fetch(`https://api${stagingStr}.dandiarchive.org/api/dandisets/?page=1&page_size=50&ordering=-modified&search=${searchText}&draft=true&empty=false&embargoed=false`)
            if (canceled) return
            if (response.status === 200) {
                const json = await response.json()
                const dandisetResponse = json as DandisetsResponse
                setSearchResults(dandisetResponse.results)
            }
        })()
        return () => {canceled = true}
    }, [searchText, stagingStr])

    const handleImportItems = useCallback(async (items: {dandisetId: string, dandisetVersion: string, assetItem: AssetsResponseItem}[]) => {
        const files: {nwbUrl: string, dandisetId: string, dandisetVersion: string, assetId: string, assetPath: string, useStaging: boolean}[] = []
        for (const item of items) {
            const response = await fetch(`https://api${stagingStr}.dandiarchive.org/api/dandisets/${item.dandisetId}/versions/${item.dandisetVersion}/assets/${item.assetItem.asset_id}/`)
            if (response.status === 200) {
                const json = await response.json()
                const assetResponse: AssetResponse = json
                let nwbUrl = assetResponse.contentUrl.find(url => url.includes('amazonaws.com'))
                if (!nwbUrl) nwbUrl = assetResponse.contentUrl[0]
                if (!nwbUrl) return
                files.push({nwbUrl, dandisetId: item.dandisetId, dandisetVersion: item.dandisetVersion, assetId: item.assetItem.asset_id, assetPath: item.assetItem.path, useStaging})
            }
        }
        await onNwbFilesSelected(files)
    }, [onNwbFilesSelected, stagingStr, useStaging])

    return (
        <div style={{position: 'absolute', width, height, background: 'white'}}>
            <div style={{position: 'absolute', width, height: topBarHeight, top: 0, overflow: 'hidden', background: 'white', display: 'flex', justifyContent: 'right'}}>
                <Checkbox checked={useStaging} onClick={toggleUseStaging} label="use staging site" />
                <div style={{width: 50}} />
            </div>
            <div style={{position: 'absolute', width, height: searchBarHeight, top: topBarHeight, overflow: 'hidden', background: 'white'}}>
                <SearchBar
                    width={width}
                    height={searchBarHeight}
                    onSearch={setSearchText}
                />
            </div>
            <div style={{position: 'absolute', width, height: height - searchBarHeight - topBarHeight, top: searchBarHeight + topBarHeight, overflow: 'hidden'}}>
                <SearchResults
                    width={width}
                    height={height - searchBarHeight}
                    searchResults={searchResult}
                    onImportItems={handleImportItems}
                    useStaging={useStaging}
                />
            </div>
        </div>
    )
}

type SearchBarProps = {
    width: number
    height: number
    onSearch: (searchText: string) => void
}

const SearchBar: FunctionComponent<SearchBarProps> = ({width, height, onSearch}) => {
    const [searchText, setSearchText] = useState<string>('')
    const searchButtonWidth = height
    
    return (
        <div style={{paddingLeft: 15}}>
            <div style={{position: 'absolute', left: 0, top: 0, width: searchButtonWidth, height}}>
                <SearchButton width={searchButtonWidth} height={height} onClick={() => onSearch(searchText)} />
            </div>

            <div style={{position: 'absolute', left: searchButtonWidth, top: 0, width: width - searchButtonWidth, height}}>
                <input
                    style={{width: width - 40 - searchButtonWidth, height: 30, fontSize: 20, padding: 5}}
                    type="text" placeholder="Search DANDI"
                    onChange={e => setSearchText(e.target.value)}
                    // when enter is pressed
                    onKeyDown={e => {
                        if (e.key === 'Enter') {
                            onSearch(searchText)
                        }
                    }}
                    // do not spell check
                    spellCheck={false}
                />
            </div>
        </div>
    )
}

const Checkbox: FunctionComponent<{checked: boolean, onClick: () => void, label: string}> = ({checked, onClick, label}) => {
    return (
        <div style={{display: 'flex', alignItems: 'center', cursor: 'pointer'}} onClick={onClick}>
            <div style={{width: 20, height: 20, borderRadius: 3, border: '1px solid black', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                {checked && <div style={{width: 10, height: 10, borderRadius: 2, background: 'black'}} />}
            </div>
            <div style={{marginLeft: 5}}>{label}</div>
        </div>
    )
}

type SearchButtonProps = {
    onClick: () => void
    width: number
    height: number
}

const SearchButton: FunctionComponent<SearchButtonProps> = ({onClick, width, height}) => {
    return (
        <SmallIconButton
            icon={<Search />}
            label=""
            fontSize={height - 5}
        />
    )
}

export default DandiNwbSelector