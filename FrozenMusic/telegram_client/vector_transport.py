import os
import glob
import tempfile
import asyncio
import psutil
import subprocess
import yt_dlp


# --- Hardcoded Cookies ---
COOKIE_CONTENT = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	FALSE	1793522371	HSID	AdzGzDS-sv2Dxh6gj
.youtube.com	TRUE	/	TRUE	1793522371	SSID	ANodiydGwjRxMjhLQ
.youtube.com	TRUE	/	FALSE	1793522371	APISID	cifAe6-LMoB3BUto/AwbmzxwAD66JAoIw_
.youtube.com	TRUE	/	TRUE	1793522371	SAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-1PAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-3PAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1786086169	LOGIN_INFO	AFmmF2swRAIgVCS48KA4Vsnvw4XEZHhCKzYYUHF9HCarHDCTVlVDzpgCIG2Fb0rOZvZg8Z6Wjmg79suIPf015V-gBINGgHE_eE4Y:QUQ3MjNmeVZqdE5NT1B5SGc2ekNWZUZ3andwSUo1VlFnWkpmUkVNaWc1TWZnUXNIcFZ2T1NzOUxnY3lwSkY0aC1FMWJSa1pmbHlFa1p6RFNMaDVOM3F2ZWlzamctV1lFbThiNjdsZ0thNmJkQXcxSExHcDdoR0ZlRzZrWnAtYk5Eem1NMHFCM3c4S3RaSlVzVjBUNHZlZGt1TmJCUnJwdWRR
.youtube.com	TRUE	/	TRUE	1795763712	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	FALSE	1793522371	SID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9tpJbiuphkKVcJqink3W-QwACgYKAVwSARISFQHGX2MixPCvckbV-IEmDQI2oM85cRoVAUF8yKp21BhW70vfMqy99ubctT2C0076
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-1PSID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9b97q6fAc4xfnKyicZPFiwgACgYKAT0SARISFQHGX2Mi23MYY1P8KTnGhLRKm7c5pRoVAUF8yKo2tWPkWhgMkASEMPx9hRKo0076
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-3PSID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9yBo6TzXkeGNEOpnLReKTBgACgYKAYwSARISFQHGX2MibJqjQzngW5KClf4JUqtDERoVAUF8yKr_OxIHjmMvMDZn-feF5Zxc0076
.youtube.com	TRUE	/	TRUE	1792739711	__Secure-1PSIDTS	sidts-CjEBmkD5S6MvitZbQVpbCidr88gjdJfNLkm_Pvk9vJVlpPWWJBUbmoKhMdCJ2abNfuOOEAA
.youtube.com	TRUE	/	TRUE	1792739711	__Secure-3PSIDTS	sidts-CjEBmkD5S6MvitZbQVpbCidr88gjdJfNLkm_Pvk9vJVlpPWWJBUbmoKhMdCJ2abNfuOOEAA
.youtube.com	TRUE	/	FALSE	1761203726	ST-hcbf8d	session_logininfo=AFmmF2swRAIgVCS48KA4Vsnvw4XEZHhCKzYYUHF9HCarHDCTVlVDzpgCIG2Fb0rOZvZg8Z6Wjmg79suIPf015V-gBINGgHE_eE4Y%3AQUQ3MjNmeVZqdE5NT1B5SGc2ekNWZUZ3andwSUo1VlFnWkpmUkVNaWc1TWZnUXNIcFZ2T1NzOUxnY3lwSkY0aC1FMWJSa1pmbHlFa1p6RFNMaDVOM3F2ZWlzamctV1lFbThiNjdsZ0thNmJkQXcxSExHcDdoR0ZlRzZrWnAtYk5Eem1NMHFCM3c4S3RaSlVzVjBUNHZlZGt1TmJCUnJwdWRR
.youtube.com	TRUE	/	FALSE	1792739720	SIDCC	AKEyXzVg4vtTr0WhzNJiPkYJchLrlkN_N2eZzEupvA62EJwtoew4I04hvWShFl8o4yoDOnNY
.youtube.com	TRUE	/	TRUE	1792739720	__Secure-1PSIDCC	AKEyXzXd6cfWsqtmB1l53p-9p5P1ItifHM9N-QRyXYEYVMc7sSrE7WJhu812yTMw7HwoQ76IUg
.youtube.com	TRUE	/	TRUE	1792739720	__Secure-3PSIDCC	AKEyXzWb6Mo6gMPvkLdx7kSHhQQbC8PaKmeLyUOAhizj_TrfqyfUSiqSoaem5COacK1wlxvE9A
.youtube.com	TRUE	/	TRUE	1761204321	CONSISTENCY	AKreu9ttuvDS0pWGd1CdvoKpD6-OLmpVhiPDF2Jy1wIgizglmRvhl6qEJbcShTrZYNVbGCW31FTtC8xk7S0fg86bQ4Jj54ZczJ-96W2-V2X-1z0daktAec0rl3wvB8tXQs4saHEpYgsAoz49VujwYMJ6
.youtube.com	TRUE	/	TRUE	1776755715	VISITOR_INFO1_LIVE	gD_fnWox6Ow
.youtube.com	TRUE	/	TRUE	1776755715	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgNg%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	cV5enldHPGo
.youtube.com	TRUE	/	TRUE	1776755707	__Secure-ROLLOUT_TOKEN	CLG-o5yt_cPRCBC6xeODuKCOAxjfxJSX47mQAw%3D%3D
"""

_SPOTIFY_COOKIES_CONTENT = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.spotify.com	TRUE	/	TRUE	1793251371	sp_t	88712f8d129fa1dfada204b68e315739
.spotify.com	TRUE	/	TRUE	1761759954	sp_landing	https%3A%2F%2Fopen.spotify.com%2F%3Fsp_cid%3D88712f8d129fa1dfada204b68e315739%26device%3Ddesktop
.spotify.com	TRUE	/	FALSE	1761801785	_gid	GA1.2.716778631.1761673557
.spotify.com	TRUE	/	TRUE	1795792973	_hp5_event_props.4043975597	%7B%7D
.spotify.com	TRUE	/	TRUE	1793251374	sp_adid	545d7a5c-0fd0-45ff-8026-aa311a0cd14d
.spotify.com	TRUE	/	TRUE	1761717033	_cs_mk_ga	0.5449057216368858_1761715233496
open.spotify.com	FALSE	/	FALSE	0	sss	1
.spotify.com	TRUE	/	TRUE	1795792973	_hp5_meta.4043975597	%7B%22userId%22%3A%222574089323671771%22%2C%22sessionId%22%3A%222821914299042856%22%2C%22sessionProperties%22%3A%7B%22time%22%3A1761715234093%2C%22id%22%3A%222821914299042856%22%2C%22utm%22%3A%7B%22source%22%3A%22%22%2C%22medium%22%3A%22%22%2C%22term%22%3A%22%22%2C%22content%22%3A%22%22%2C%22campaign%22%3A%22%22%7D%2C%22initial_pageview_info%22%3A%7B%22time%22%3A1761715234093%2C%22id%22%3A%225889420349800657%22%2C%22title%22%3A%22Spotify%20-%20Web%20Player%3A%20Music%20for%20everyone%22%2C%22url%22%3A%7B%22domain%22%3A%22open.spotify.com%22%2C%22path%22%3A%22%2F%22%2C%22query%22%3A%22%22%2C%22hash%22%3A%22%22%7D%7D%2C%22search_keyword%22%3A%22%22%2C%22referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%7D%7D
.spotify.com	TRUE	/	TRUE	1796275319	sp_m	in-en
.spotify.com	TRUE	/	TRUE	1762924970	sp_dc	AQD1ekjbJSNAdzPG3AdpYI81tsWFPMZLJheg5838SI3pcX6X2AWdn6V0O8ITrHtgTcLDbDFW73pL74vNBXIe0X5B52WWWGYI6aQ4CNjOi3c1SylKDX-F__HTPIml2ui-CsQf1iiye4XZdHnb6ou8JKgy9rMamJGCfXtbkbY7xG9_UtnZ9_0Sol5EniNMifj-bLUtvH85PugAIvLa7VE
.spotify.com	TRUE	/	FALSE	1761715433	_gat_UA-5784146-31	1
.spotify.com	TRUE	/	FALSE	1796275385	_ga	GA1.2.1925864589.1761673557
.spotify.com	TRUE	/	FALSE	1796275385	_ga_BMC5VGR8YS	GS2.2.s1761715234$o2$g1$t1761715385$j48$l0$h0
.spotify.com	TRUE	/	FALSE	1793251385	OptanonAlertBoxClosed	2025-10-29T05:23:05.078Z
.spotify.com	TRUE	/	FALSE	1793251385	OptanonConsent	isGpcEnabled=0&datestamp=Wed+Oct+29+2025+10%3A53%3A05+GMT%2B0530+(India+Standard+Time)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=s00%3A1%2Cf00%3A1%2Cm00%3A1%2Ct00%3A1%2Ci00%3A1%2Cf11%3A1%2Cm03%3A1&AwaitingReconsent=false
.spotify.com	TRUE	/	FALSE	1796275385	_ga_ZWG1NSHWD8	GS2.1.s1761715234$o3$g1$t1761715385$j48$l0$h0
.spotify.com	TRUE	/	TRUE	1795792985	_hp5_let.4043975597	1761715385054
"""

COOKIE_FILE_PATH = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
    f.write(COOKIE_CONTENT)

# optional globals: COOKIE_FILE_PATH, SHARD_CACHE_MATRIX
SHARD_CACHE_MATRIX = {}

def make_ydl_opts_audio(output_template: str):
    ffmpeg_path = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")
    opts = {
        'format': 'bestaudio/best',     # let yt-dlp pick whatever works
        'outtmpl': output_template,     # temp name + correct extension
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 60,
        'ffmpeg_location': ffmpeg_path,
        'concurrent_fragment_downloads': 4,

        # first extract audio as-is, then manually convert to .webm
        'postprocessors': [
            {  # extract audio without forcing codec
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '0',
            },
            {  # re-mux result to .webm container
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'webm'
            }
        ],
    }
    if 'COOKIE_FILE_PATH' in globals() and COOKIE_FILE_PATH:
        opts['cookiefile'] = COOKIE_FILE_PATH
    return opts


# Main resolver
async def vector_transport_resolver(url: str) -> str:
    """
    If url is a local file -> return it.
    If url is Spotify -> call votify CLI (with hardcoded cookies) and return downloaded file path.
    Otherwise -> use yt-dlp (letting it pick formats), postprocess to .webm and return file path.
    """
    # shortcut: already a local file
    if os.path.exists(url) and os.path.isfile(url):
        return url

    # cache shortcut
    if url in SHARD_CACHE_MATRIX:
        cached = SHARD_CACHE_MATRIX[url]
        if os.path.exists(cached) and os.path.getsize(cached) > 0:
            return cached
        else:
            # remove invalid cache
            SHARD_CACHE_MATRIX.pop(url, None)

    # try to lower process priority (best-effort)
    try:
        proc = psutil.Process(os.getpid())
        if os.name == "nt":
            proc.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            proc.nice(19)
    except Exception:
        pass

    # Detect Spotify URL (open.spotify.com or spotify: URIs)
    is_spotify = False
    if isinstance(url, str):
        u = url.strip()
        if u.startswith("spotify:") or "open.spotify.com" in u:
            is_spotify = True

    if is_spotify:
        # --- Use Votify CLI ---
        # Requirements: votify must be installed and in PATH (pip install votify)
        # We will write the hardcoded cookies to a temporary cookies file and pass --cookies-path.
        tmp_dir = tempfile.mkdtemp(prefix="votify_out_")
        cookies_path = os.path.join(tmp_dir, "cookies.txt")
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(_SPOTIFY_COOKIES_CONTENT)

        # ffmpeg path for votify
        ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")

        # Build votify command:
        # - --cookies-path <path>
        # - --output-path <tmp_dir>
        # - --temp-path <tmp_dir>
        # - --ffmpeg-path <ffmpeg_path>
        # - url
        cmd = [
            "votify",
            "--cookies-path", cookies_path,
            "--output-path", tmp_dir,
            "--temp-path", tmp_dir,
            "--ffmpeg-path", ffmpeg_path,
            "--no-exceptions",  # try to keep stdout stable; optional
            url
        ]

        # Run votify; capture output in case of error
        try:
            # run votify synchronously in executor to avoid blocking event loop
            loop = asyncio.get_running_loop()
            def run_votify():
                # Ensure environment PATH preserved; capture stdout/stderr for debugging
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return res

            res = await loop.run_in_executor(None, run_votify)

            if res.returncode != 0:
                # include stderr for debugging
                raise Exception(f"Votify failed (rc={res.returncode}): {res.stderr.strip() or res.stdout.strip()}")

            # find any file created in tmp_dir (votify places outputs into output-path)
            # prefer audio-like extensions
            patterns = ["*.webm", "*.mp4", "*.m4a", "*.aac", "*.ogg", "*.opus", "*.mp3", "*.*"]
            found = []
            for pat in patterns:
                found = glob.glob(os.path.join(tmp_dir, pat))
                if found:
                    break

            if not found:
                raise Exception("Votify ran successfully but no output file was found in votify output directory.")

            # pick the largest non-empty file
            found = [f for f in found if os.path.getsize(f) > 0]
            if not found:
                raise Exception("Votify produced files but they are empty.")

            found.sort(key=lambda p: os.path.getsize(p), reverse=True)
            downloaded = found[0]

            # cache and return
            SHARD_CACHE_MATRIX[url] = downloaded
            return downloaded

        except Exception as e:
            # bubble up with context
            raise Exception(f"Error downloading from Spotify with Votify: {e}")

    else:
        # --- Use yt-dlp path (let yt-dlp pick stream, then remux to .webm) ---
        base = tempfile.NamedTemporaryFile(delete=False)
        base_name = base.name
        base.close()

        output_tmpl = base_name + ".%(ext)s"
        loop = asyncio.get_running_loop()
        ydl_opts = make_ydl_opts_audio(output_tmpl)

        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        try:
            await loop.run_in_executor(None, download_audio)
        except Exception as e:
            raise Exception(f"Error downloading audio with yt-dlp: {e}")

        # find any produced .webm file first (postprocessor should remux to .webm)
        matches = glob.glob(base_name + "*.webm")
        if not matches:
            matches = glob.glob(base_name + ".*")

        if not matches:
            # cleanup and error
            try:
                os.unlink(base_name)
            except Exception:
                pass
            raise Exception("yt-dlp did not produce any output file.")

        downloaded = matches[0]
        if os.path.getsize(downloaded) == 0:
            try:
                os.unlink(downloaded)
            except Exception:
                pass
            raise Exception("Downloaded file is empty.")

        SHARD_CACHE_MATRIX[url] = downloaded
        return downloaded

