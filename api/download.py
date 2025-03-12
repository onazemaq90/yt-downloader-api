import yt_dlp as youtube_dl
import p_pl_dl_common as dl_common
from vercel import VercelResponse  # You'll need to install this

sExtractor = 'xhamster'

def _xhamsterHeaderGet():
    dHeaders_xh = {
        'Host': 'xhamster.com',
        'User-Agent': dl_common.randomizeUserAgent(),
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Cookie': dl_common.cookieHeaderStringGet(),
        'TE': 'trailers'
    }
    return dHeaders_xh

def handler(request):
    try:
        # Get URL from query parameters
        sUrl = request.args.get('url')
        if not sUrl:
            return VercelResponse(
                {"error": "URL parameter is required"},
                status_code=400
            )

        sCookieSource = request.args.get('cookie_source')
        nVideoLimit = request.args.get('limit', type=int)
        bDebug = request.args.get('debug', default=False, type=bool)

        if sCookieSource:
            dl_common.parseCookieFile(sCookieSource)

        if not dl_common.dCookiesParsed:
            print("WARNING :: No cookies provided!")

        if f'{sExtractor}.com/videos' in sUrl:
            sUrlType = 'video'
        elif f'{sExtractor}.com/my' in sUrl:
            sUrlType = 'playlist'
        else:
            raise ValueError(f"Unable to determine {sExtractor} URL type!")

        dXhamsterHeader = _xhamsterHeaderGet()
        html = dl_common.session.get(sUrl, headers=dl_common.dHeaders, cookies=dl_common.dCookiesParsed)
        
        if html.status_code != 200:
            return VercelResponse(
                {"error": f"Connection failed with status {html.status_code}"},
                status_code=html.status_code
            )

        lUrlVideos = []
        if sUrlType == 'playlist':
            sUrlBaseFormat = urlStandardize(sUrl)
            nPage = 0
            while True:
                nPage += 1
                sUrlPage = sUrlBaseFormat.format(f'{nPage:02}')
                page = dl_common.Page(sUrlPage, headers=dXhamsterHeader)
                
                if page.content.status_code != 200:
                    break
                    
                page._extract_video_urls()
                if page.videos:
                    lUrlVideos += [url for url in page.videos if 'com/videos' in url]
                else:
                    break

        elif sUrlType == 'video':
            lUrlVideos = [sUrl]

        dYdlOptions = dict(dl_common.dYdlOptions)
        dYdlOptions['outtmpl'] = '%(title)s.%(ext)s'

        results = []
        with youtube_dl.YoutubeDL(dYdlOptions) as ydl:
            for sVideoUrl in lUrlVideos[:nVideoLimit] if nVideoLimit else lUrlVideos:
                info = ydl.extract_info(sVideoUrl, download=False)
                results.append({
                    "title": info.get('title'),
                    "url": sVideoUrl
                })

        return VercelResponse({"videos": results})

    except Exception as e:
        return VercelResponse(
            {"error": str(e)},
            status_code=500
        )

def urlStandardize(sUrl):
    if sUrl[-1] != '/':
        sUrl += '/'
    sUrl += '{}'
    return sUrl
