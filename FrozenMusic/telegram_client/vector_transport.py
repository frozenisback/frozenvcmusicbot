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
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

open.spotify.com	FALSE	/episode	FALSE	0	sss	1
.spotify.com	TRUE	/	TRUE	1791383497	sp_t	ccc2c8d181eb192906a11c40b50b127b
.spotify.com	TRUE	/	TRUE	1759933824	sp_landing	https%3A%2F%2Fopen.spotify.com%2F%3Fsp_cid%3Dccc2c8d181eb192906a11c40b50b127b%26device%3Ddesktop
.spotify.com	TRUE	/	TRUE	1759849226	_cs_mk_ga	0.7963095260015378_1759847426366
.spotify.com	TRUE	/	FALSE	1759933898	_gid	GA1.2.485530918.1759847426
open.spotify.com	FALSE	/	FALSE	0	sss	1
.spotify.com	TRUE	/	TRUE	1791383499	sp_adid	2ba973b8-f704-4d62-92d6-0b369e5ee9cc
.spotify.com	TRUE	/	TRUE	1794407440	sp_m	in-en
.spotify.com	TRUE	/	TRUE	1761057061	sp_dc	AQBJYlJM1GJO_hI99M6cuxEMWBDMZ28tSOY8-hgHjKWCLn5KM-wGXltLn1HA1m5nv5HJQCmBrg8iVqyFWynYMqf2YIuI1iGgD7ExQt2qiHCZBGjAxUT67T28hlCrJ_8pT-wsWNqEjX0N7EcNRb52e5DQ-dj8qnROzKAmlwF2hUZbSisR3u9wI42P0jq1H4i9qe-mPQ-nDO1Idiq0h40
.spotify.com	TRUE	/	FALSE	1791383471	OptanonAlertBoxClosed	2025-10-07T14:31:11.162Z
.spotify.com	TRUE	/	FALSE	1791383498	OptanonConsent	isGpcEnabled=0&datestamp=Tue+Oct+07+2025+20%3A01%3A38+GMT%2B0530+(India+Standard+Time)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=s00%3A1%2Cf00%3A1%2Cm00%3A1%2Ct00%3A1%2Ci00%3A1%2Cf11%3A1%2Cm03%3A1&AwaitingReconsent=false&geolocation=IN%3BUP
.spotify.com	TRUE	/	FALSE	1794407499	_ga_ZWG1NSHWD8	GS2.1.s1759847426$o1$g1$t1759847498$j59$l0$h0
.spotify.com	TRUE	/	FALSE	1794407499	_ga	GA1.2.2077846945.1759847426
.spotify.com	TRUE	/	FALSE	1759847558	_gat_UA-5784146-31	1
.spotify.com	TRUE	/	FALSE	1794407499	_ga_BMC5VGR8YS	GS2.2.s1759847427$o1$g1$t1759847498$j60$l0$h0
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

